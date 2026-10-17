"""Opt-in Runtime and Hosting local chat adapter. History and answers stay in local PG."""
import os
from .course_config import setting
import time
from datetime import datetime, timezone
from urllib.parse import urlsplit
import httpx

def enabled():
    return bool(setting('HOSTED_AGENT_URL'))

def validate():
    if not enabled(): return
    if setting('HOSTING_LAB') != 'true':
        raise ValueError('Remote agent execution requires the explicit Runtime and Hosting lab')
    for name in ('DATABASE_URL', 'READ_DATABASE_URL'):
        if urlsplit(os.getenv(name, '')).path != '/ch12_hosting_lab':
            raise ValueError('Runtime and Hosting requires matching disposable lab databases')
    url = urlsplit(setting('HOSTED_AGENT_URL'))
    if (url.scheme not in ('https', 'http') or not url.hostname or url.username
            or url.password or url.query or url.fragment
            or (url.scheme == 'http' and url.hostname not in ('localhost', '127.0.0.1'))):
        raise ValueError('Remote agent requires HTTPS or loopback for isolated tests')
    if len(setting('HOSTED_AGENT_API_KEY', '')) < 32:
        raise ValueError('Runtime and Hosting agent credential is missing')

async def answer(conversation_id, question):
    validate()
    started = time.monotonic()
    from .agent import DatabaseSession
    from .db import Session, Run
    from .business import uid
    session = DatabaseSession(conversation_id)
    history = await session.get_items()
    try:
        async with httpx.AsyncClient(timeout=175, follow_redirects=False) as client:
            response = await client.post(setting('HOSTED_AGENT_URL').rstrip('/') + '/investigate',
                headers={'x-api-key': setting('HOSTED_AGENT_API_KEY')},
                json={'question': question, 'history': history})
    except httpx.HTTPError as exc:
        raise RuntimeError('Hosted agent connection failed; check the lab endpoint') from exc
    if response.status_code != 200:
        raise RuntimeError('Hosted agent unavailable; retry the question after checking its health')
    try:
        value = response.json()
    except ValueError as exc:
        raise RuntimeError('Hosted agent returned an invalid result') from exc
    if value.get('status') != 'completed' or not value.get('evidence') or not isinstance(value.get('items'), list):
        raise RuntimeError('Hosted agent returned an incomplete result')
    value['metrics']['elapsed_seconds'] = round(time.monotonic() - started, 2)
    value['metrics']['tool_calls'] = value['metrics']['actual_tool_invocations']
    run_id = uid('run')
    # Persist transcript and result together. A failed HTTP request appends no partial turn.
    from .db import Conversation
    with Session.begin() as db:
        conv = db.get(Conversation, conversation_id)
        conv.items = [*conv.items, *value['items']]
        db.add(Run(id=run_id, conversation_id=conversation_id, question=question,
            answer=value['answer'], status=value['status'], revision=value['revision'],
            evidence=value['evidence'], metrics=value['metrics'], created_at=datetime.now(timezone.utc)))
    return {'id': run_id, **{key: value[key] for key in ('status', 'answer', 'evidence', 'revision', 'metrics')}}
