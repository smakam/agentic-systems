"""Complete runnable teaching loop. No Agents SDK runner. Run this file for a free scripted example."""
import json
from solutions.minimal_loop import run_loop


async def _offline_example(max_steps):
    """A fixed example with no network, marketplace reads or API charges."""
    outputs = [
        {'tool_calls': [{'id': 'lookup-1', 'type': 'function',
                         'function': {'name': 'lookup_quantity', 'arguments': '{}'}}]},
        {'content': 'The sample order contains two units.'},
    ]
    async def model(messages, tools):
        return outputs.pop(0)
    async def execute(name, arguments):
        return {'status': 'ok', 'rows': [{'quantity': 2}]}
    tools = [{'type': 'function', 'function': {'name': 'lookup_quantity',
              'description': 'Read the scripted sample quantity',
              'parameters': {'type': 'object', 'properties': {}}}}]
    return await run_loop(model, execute, tools, 'How many units are in the sample order?',
                          instructions='Answer from the tool result.', max_turns=max_steps)

if __name__ == '__main__':
    import argparse
    import asyncio
    parser = argparse.ArgumentParser(description='Run the complete free, offline loop example.')
    parser.add_argument('--max-steps', type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(_offline_example(args.max_steps)), indent=2))
