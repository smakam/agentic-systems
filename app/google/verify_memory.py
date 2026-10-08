"""Hosted memory verification, using an existing saved preference for the user.

Run after explicitly generating Memory Bank from the preference session.
Results retain questions, sessions, tool calls and answer events for review.
"""
import argparse
import asyncio
import json
import time
from pathlib import Path

import agentplatform


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user', default='vais-query-reasoning-engine')
    args = parser.parse_args()
    settings = json.loads(Path('deployment.json').read_text())
    client = agentplatform.Client(project=settings['project'], location=settings['location'])
    runtime = client.runtimes.get(name=settings['resource_name'])
    results = []

    async def create(memory=True, user=None):
        session = await runtime.async_create_session(user_id=user or args.user, state={'memory_enabled': memory})
        return session['id']

    async def ask(label, session, question, memory=True, user=None):
        events = []
        start = time.monotonic()
        async for event in runtime.async_stream_query(user_id=user or args.user, session_id=session, message=question, state_delta={'memory_enabled': memory}, run_config={'max_llm_calls': 12}):
            events.append(event)
        tools = [p['function_call']['name'] for e in events for p in (e.get('content') or {}).get('parts', []) if p.get('function_call')]
        answers = [p['text'] for e in events for p in (e.get('content') or {}).get('parts', []) if p.get('text')]
        errors = [e for e in events if e.get('error_code') or e.get('error_message')]
        result = dict(label=label, session=session, user=user or args.user, question=question, memory=memory, seconds=round(time.monotonic()-start, 2), tools=tools, answers=answers, errors=errors, events=events)
        results.append(result)
        Path('memory-verification-results.json').write_text(json.dumps(results, indent=2, default=str))
        print(json.dumps({k: v for k, v in result.items() if k != 'events'}, default=str), flush=True)
        if errors:
            raise RuntimeError(f'{label} returned error events')

    memories = await runtime.async_search_memory(user_id=args.user, query='preferred format for payout investigation answers')
    print('STORED_MEMORY', json.dumps(memories, default=str), flush=True)
    if not memories.get('memories'):
        raise RuntimeError('Generate and verify the saved preference first')
    short = await create(memory=False)
    await ask('short_seed', short, 'For this conversation only, call the demo lantern blue mango. Acknowledge that name.', memory=False)
    await ask('short_followup', short, 'What name did I just give the demo lantern?', memory=False)
    fresh = await create(memory=False)
    await ask('short_new_session', fresh, 'What name did I give the demo lantern in the previous conversation?', memory=False)
    recall = await create()
    await ask('long_recall', recall, 'What is my preferred format for payout investigation answers?')
    await ask('long_apply_sql_rag', recall, 'Why is the payout for order-2 held, and what does the payout policy say?')
    off = await create(memory=False)
    await ask('long_memory_off', off, 'What is my preferred format for payout investigation answers?', memory=False)
    other_user = 'memory-verification-other-user'
    other = await create(user=other_user)
    await ask('long_other_user', other, 'What is my preferred format for payout investigation answers?', user=other_user)
    print('RUN_COMPLETE: inspect answers and native trace ingestion before declaring a pass', flush=True)


if __name__ == '__main__':
    asyncio.run(main())
