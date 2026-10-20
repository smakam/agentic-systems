"""Real model + one local sample tool, orchestrated without Agents SDK Runner."""
import asyncio
import json
from solutions.minimal_loop import run_loop

TOOLS = [{'type': 'function', 'function': {
    'name': 'lookup_quantity',
    'description': 'Read the quantity for the sample order.',
    'parameters': {'type': 'object', 'properties': {}, 'additionalProperties': False},
}}]

async def execute(name, arguments):
    """Local sample data only: no MCP server or marketplace database."""
    if name != 'lookup_quantity' or arguments:
        raise ValueError('Unknown tool or unexpected arguments')
    return {'order_id': 'sample-order', 'quantity': 2}

async def main():
    # Course backend supplies the configured gateway client and credentials.
    from marketplace.tools import client
    api = client()
    try:
        async def model(messages, tools):
            response = await api.chat.completions.create(
                model='support-model-test', messages=messages, tools=tools,
                parallel_tool_calls=False, max_completion_tokens=1024)
            return response.choices[0].message.model_dump(exclude_none=True)
        result = await asyncio.wait_for(run_loop(
            model, execute, TOOLS, 'How many units are in the sample order?',
            instructions='Use lookup_quantity to retrieve the sample order quantity before answering. Answer only from the returned result.',
            max_turns=8), timeout=150)
        print(json.dumps(result, indent=2))
    finally:
        await api.close()

if __name__ == '__main__':
    asyncio.run(main())
