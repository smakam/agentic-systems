"""Optional paid one-shot agent using both lab MCP servers; no running UI edits."""
import asyncio
import os
import sys
from pathlib import Path
from psycopg.conninfo import conninfo_to_dict
from agents import Agent, Runner, ModelSettings, OpenAIChatCompletionsModel, set_tracing_disabled
from agents.mcp import MCPServerStdio
from openai.types.shared import Reasoning
from marketplace.tools import client

set_tracing_disabled(True)


async def main():
    assert conninfo_to_dict(os.environ['READ_DATABASE_URL'])['dbname'] == 'market_test', 'Run this lab against market_test only'
    if len(sys.argv) != 2:
        raise SystemExit('Pass one quoted question as the argument')
    env = dict(os.environ)
    async with MCPServerStdio(params={'command': sys.executable, 'args': ['-m', 'marketplace.mcp_server'], 'env': env}) as marketplace:
        async with MCPServerStdio(params={'command': sys.executable, 'args': [str(Path(__file__).with_name('tracking_server.py').resolve())], 'env': env}) as tracking:
            api = client()
            try:
                agent = Agent(name='Read-only marketplace and tracking lab',
                    instructions='Answer using the supplied read-only tools. Tracking records are simulated fixtures, not live carrier data. Keep marketplace balances separate from tracking records. Report missing records rather than inventing them. Display money in rupees by dividing stored paise by 100.',
                    model=OpenAIChatCompletionsModel(model='support-model-test', openai_client=api),
                    model_settings=ModelSettings(max_tokens=1000, reasoning=Reasoning(effort='low'), parallel_tool_calls=False),
                    mcp_servers=[marketplace, tracking])
                result = await asyncio.wait_for(Runner.run(agent, sys.argv[1], max_turns=4), timeout=120)
                calls = [item.raw_item.name for item in result.new_items
                         if item.type == 'tool_call_item' and hasattr(item.raw_item, 'name')]
                print('Model-requested tools:', ', '.join(calls))
                print(result.final_output)
            finally:
                await api.close()


if __name__ == '__main__':
    asyncio.run(main())
