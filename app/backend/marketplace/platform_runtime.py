"""Hosted runtime adapters. Identity and session routing stay in trusted backend code."""
import asyncio
import hashlib
import json
import logging
import os
import re
import time
from contextlib import nullcontext
from datetime import datetime, timezone

import httpx
from fastapi.encoders import jsonable_encoder

from .business import uid
from .db import Run
from .platform_evidence import google_sources, lyzr_sources

RUNTIMES = {'sdk': 'OpenAI Agents SDK', 'lyzr': 'Lyzr', 'google': 'Google ADK'}
BINDING_TYPE = 'marketplace_runtime'
RESOURCE_RE = re.compile(r'^projects/[^/]+/locations/([a-z0-9-]+)/reasoningEngines/[0-9]+$')


def binding(conversation):
    for item in conversation.items or []:
        if item.get('type') == BINDING_TYPE:
            return dict(item)
    return {'runtime': 'sdk'}


def options():
    return [
        {'id': key, 'label': label, 'configured': configured(key),
         'memory_controls': key != 'lyzr', 'local_tools': key == 'sdk'}
        for key, label in RUNTIMES.items()
    ]


def configured(runtime):
    if runtime == 'sdk':
        return True
    if runtime == 'lyzr':
        return bool(os.getenv('LYZR_API_KEY') and os.getenv('LYZR_AGENT_ID'))
    if runtime == 'google':
        return bool(RESOURCE_RE.fullmatch(os.getenv('GOOGLE_RUNTIME_RESOURCE', '')))
    return False


def platform_user(owner_id):
    namespace = os.getenv('MARKETPLACE_IDENTITY_NAMESPACE', 'marketplace-local')
    return 'marketplace-' + hashlib.sha256((namespace + ':' + owner_id).encode()).hexdigest()


def initial_items(runtime, owner_id, conversation_id):
    if runtime == 'sdk':
        return []
    if runtime not in RUNTIMES:
        raise ValueError('Unknown runtime')
    target = os.getenv('LYZR_AGENT_ID') if runtime == 'lyzr' else os.getenv('GOOGLE_RUNTIME_RESOURCE')
    return [{'type': BINDING_TYPE, 'runtime': runtime, 'target': target,
             'user_id': platform_user(owner_id),
             'session_id': 'marketplace-' + conversation_id if runtime == 'lyzr' else None}]


def validate_controls(runtime, body):
    if runtime == 'sdk':
        return
    if body.guardrail != 'off' or not body.source_authority or body.marker_mode != 'off':
        raise ValueError('Marketplace guardrails and test prompts apply only to the SDK runtime')
    if runtime == 'lyzr' and (body.memory_enabled or body.memory_write):
        raise ValueError('Lyzr memory is managed by the deployed agent, not per-question marketplace controls')
    if body.memory_write and not body.memory_enabled:
        raise ValueError('Enable memory before requesting a Memory Bank save')


async def google_headers():
    # ADC works with a mounted local credential file and Cloud Run's service identity.
    # Refresh runs outside the event loop; tokens never reach the browser or logs.
    def token():
        import google.auth
        from google.auth.transport.requests import Request
        credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        credentials.refresh(Request())
        return credentials.token
    return {'Authorization': 'Bearer ' + await asyncio.to_thread(token)}


def google_url(resource):
    match = RESOURCE_RE.fullmatch(resource or '')
    if not match:
        raise ValueError('Invalid Google runtime resource')
    return f'https://{match.group(1)}-aiplatform.googleapis.com/v1/{resource}'


async def google_query(client, base, method, arguments, headers):
    response = await client.post(base + ':query', headers=headers,
                                 json={'class_method': method, 'input': arguments})
    response.raise_for_status()
    result = response.json()
    if not isinstance(result, dict) or 'output' not in result:
        raise ValueError('Google runtime returned an invalid query envelope')
    return result['output']


def event_answer(events):
    final = ''
    partial = ''
    for event in events:
        if event.get('error_code') or event.get('errorCode') or event.get('error_message'):
            raise ValueError('Google runtime reported a model error')
        content = event.get('content') or {}
        if content.get('role') == 'user':
            continue
        parts = content.get('parts') or []
        if any('function_call' in p or 'functionCall' in p for p in parts):
            continue
        text = ''.join(p.get('text', '') for p in parts if not p.get('thought'))
        if text:
            if event.get('partial'):
                partial += text
            else:
                final = text
                partial = ''
    if not final and not partial:
        raise ValueError('Google runtime returned no answer')
    return final or partial


async def google_stream(client, base, arguments, headers, evidence=None):
    events = []
    async with client.stream('POST', base + ':streamQuery', params={'alt': 'sse'},
                             headers=headers, json={'class_method': 'async_stream_query', 'input': arguments}) as response:
        response.raise_for_status()
        async for line in response.aiter_lines():
            if not line.strip() or line.startswith((':', 'event:', 'id:', 'retry:')):
                continue
            payload = line[5:].strip() if line.startswith('data:') else line
            if payload == '[DONE]':
                continue
            event = json.loads(payload)
            if isinstance(event, dict) and 'output' in event:
                event = event['output']
            if not isinstance(event, dict):
                raise ValueError('Invalid Google runtime event')
            events.append(event)
    if evidence is not None:
        evidence.update(google_sources(events))
    return event_answer(events)


async def lyzr_evidence(client, route, answer, since):
    headers = {'x-api-key': os.environ['LYZR_API_KEY']}
    base = 'https://agent-prod.studio.lyzr.ai/v3/traces'
    for attempt in range(6):
        response = await client.get(base, headers=headers,
            params={'agent_id': route['target'], 'session_id': route['session_id'],
                    'start_time': since.isoformat(), 'limit': 5}, timeout=10)
        response.raise_for_status()
        traces = response.json()
        if not isinstance(traces, list):
            return {}
        for trace in traces:
            if (trace.get('agent_id') not in (None, route['target']) or trace.get('session_id') != route['session_id']
                    or not re.fullmatch(r'[a-zA-Z0-9-]+', str(trace.get('trace_id', '')))):
                continue
            detail = await client.get(base + '/' + trace['trace_id'], headers=headers, timeout=10)
            detail.raise_for_status()
            payload = detail.json()
            # The listing can omit agent_id; the inference span carries both identities.
            if not any(s.get('SpanName') == 'inference'
                       and s.get('SpanAttributes', {}).get('agent_id') == route['target']
                       and s.get('SpanAttributes', {}).get('session_id') == route['session_id']
                       and str(s.get('SpanAttributes', {}).get('output', '')).strip() == answer.strip()
                       for s in payload.get('spans', [])):
                continue
            records = lyzr_sources(payload, answer)
            if records:
                return records
        if attempt < 5:
            await asyncio.sleep(2)
    return {}


async def refresh_lyzr_sources(db, conversation, run):
    """Retry recent missing evidence on history read; never rerun the model/tools."""
    created = run.created_at.replace(tzinfo=timezone.utc) if run.created_at.tzinfo is None else run.created_at
    if (run.status != 'completed' or run.evidence or binding(conversation)['runtime'] != 'lyzr'
            or (datetime.now(timezone.utc) - created).total_seconds() > 900):
        return
    try:
        async with httpx.AsyncClient() as client:
            sources = await asyncio.wait_for(
                lyzr_evidence(client, binding(conversation), run.answer, created), timeout=20)
        if sources:
            run.evidence = sources
            db.commit()
    except Exception:
        logging.getLogger(__name__).warning('Lyzr source trace retry unavailable')


async def hosted_answer(db, conversation, question, body):
    route = binding(conversation)
    runtime = route['runtime']
    if runtime not in ('lyzr', 'google'):
        raise ValueError('Hosted adapter requires a platform conversation')
    if not configured(runtime):
        raise ValueError('Selected platform is not configured')
    run = Run(id=uid('run'), conversation_id=conversation.id, revision=0,
              question=question, answer='', status='running', evidence={},
              metrics={'runtime': runtime}, created_at=datetime.now(timezone.utc))
    db.add(run)
    db.commit()
    started = time.monotonic()
    metrics = {'runtime': runtime, 'platform_session_id': route.get('session_id'),
               'data_scope': 'Hosted agent middleware configuration',
               'memory_enabled': None}
    lf = None
    try:
        if os.getenv('LANGFUSE_PUBLIC_KEY') and os.getenv('LANGFUSE_SECRET_KEY'):
            from langfuse import get_client
            lf = get_client()
        span = lf.start_as_current_observation(name='marketplace-hosted-answer', as_type='span',
                input=question, metadata={'runtime': runtime, 'conversation_id': conversation.id, 'run_id': run.id}) if lf else nullcontext()
        with span as observation:
            if observation:
                metrics['trace_id'] = observation.trace_id
            async with asyncio.timeout(150):
                async with httpx.AsyncClient(timeout=120, follow_redirects=False) as client:
                    if runtime == 'lyzr':
                        response = await client.post('https://agent-prod.studio.lyzr.ai/v3/inference/chat/',
                            headers={'x-api-key': os.environ['LYZR_API_KEY']},
                            json={'user_id': route['user_id'], 'agent_id': route['target'],
                                  'session_id': route['session_id'], 'message': question})
                        response.raise_for_status()
                        answer = response.json().get('response')
                        if not isinstance(answer, str) or not answer.strip():
                            raise ValueError('Lyzr returned no answer')
                        try:
                            run.evidence = await asyncio.wait_for(
                                lyzr_evidence(client, route, answer, run.created_at), timeout=20)
                        except Exception:
                            # Evidence availability must not discard a successful answer.
                            logging.getLogger(__name__).warning('Lyzr source trace unavailable')
                    else:
                        headers = await google_headers()
                        base = google_url(route['target'])
                        if not route.get('session_id'):
                            created = await google_query(client, base, 'async_create_session',
                                {'user_id': route['user_id']}, headers)
                            if not isinstance(created, dict) or not created.get('id'):
                                raise ValueError('Google session creation returned no session ID')
                            route['session_id'] = created['id']
                            conversation.items = [route]
                            db.commit()  # Persist before dispatch; retries and follow-ups reuse this session.
                        metrics['platform_session_id'] = route['session_id']
                        sources = {}
                        answer = await google_stream(client, base,
                            {'user_id': route['user_id'], 'session_id': route['session_id'], 'message': question,
                             'run_config': {'max_llm_calls': 12}}, headers, evidence=sources)
                        run.evidence = sources
                    run.answer = answer
                    run.status = 'completed'
                    if observation:
                        observation.update(output=answer)
    except Exception as exc:
        run.status = 'failed'
        run.answer = 'The selected platform could not complete this question. Check its credentials, deployment and middleware connection, then retry.'
        metrics['error_type'] = type(exc).__name__
        if isinstance(exc, httpx.HTTPStatusError):
            metrics['platform_http_status'] = exc.response.status_code
        logging.getLogger(__name__).warning('Hosted runtime failed: %s (%s)', runtime, type(exc).__name__)
    finally:
        metrics['elapsed_seconds'] = round(time.monotonic() - started, 2)
        run.metrics = metrics
        db.commit()
        if lf:
            try:
                await asyncio.to_thread(lf.flush)
            except Exception:
                logging.getLogger(__name__).warning('Hosted answer trace export unavailable')
    return jsonable_encoder(run)
