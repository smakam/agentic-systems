"""Native-runtime lesson client: ask, new-session, save and inspect memory."""
import argparse
import asyncio
import json
from pathlib import Path
import agentplatform


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['new-session', 'ask', 'save', 'memory', 'session'])
    parser.add_argument('--user', default='course-operator')
    parser.add_argument('--session')
    parser.add_argument('--question')
    parser.add_argument('--memory-off', action='store_true')
    args = parser.parse_args()
    settings = json.loads(Path('deployment.json').read_text())
    client = agentplatform.Client(project=settings['project'], location=settings['location'])
    runtime = client.runtimes.get(name=settings['resource_name'])
    if args.action == 'new-session':
        result = await runtime.async_create_session(user_id=args.user, state={'memory_enabled': not args.memory_off})
        print(json.dumps(result, default=str, indent=2))
    elif args.action == 'ask':
        if not args.question or not args.session:
            parser.error('ask requires --question and --session')
        async for event in runtime.async_stream_query(
            user_id=args.user, session_id=args.session, message=args.question,
            state_delta={'memory_enabled': not args.memory_off},
            run_config={'max_llm_calls': 12}):
            print(json.dumps(event, default=str))
    elif args.action in ('save', 'session'):
        if not args.session:
            parser.error('save/session requires --session')
        session = await runtime.async_get_session(user_id=args.user, session_id=args.session)
        if args.action == 'session':
            print(json.dumps(session, default=str, indent=2))
        else:
            result = await runtime.async_add_session_to_memory(session=session)
            print(json.dumps({'generation_result': result, 'note': 'Generation requested; inspect memory before claiming recall readiness.'}, default=str))
    else:
        if not args.question:
            parser.error('memory requires --question as retrieval query')
        print(json.dumps(await runtime.async_search_memory(user_id=args.user, query=args.question), default=str, indent=2))


if __name__ == '__main__':
    asyncio.run(main())
