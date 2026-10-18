"""Keep two MCP connections open and call each; no paid model calls."""
import asyncio
import json
import os
import sys
from pathlib import Path
from psycopg.conninfo import conninfo_to_dict
from agents import set_tracing_disabled
from agents.mcp import MCPServerStdio

set_tracing_disabled(True)


async def main():
    assert conninfo_to_dict(os.environ['READ_DATABASE_URL'])['dbname'] == 'market_test', 'Run this lab against market_test only'
    env = dict(os.environ)
    async with MCPServerStdio(params={'command': sys.executable, 'args': ['-m', 'marketplace.mcp_server'], 'env': env}) as marketplace:
        async with MCPServerStdio(params={'command': sys.executable, 'args': [str(Path(__file__).with_name('tracking_server.py').resolve())], 'env': env}) as tracking:
            business_tools = await marketplace.list_tools()
            tracking_tools = await tracking.list_tools()
            assert len(business_tools) == 6 and len(tracking_tools) == 1
            print('Marketplace connection:', ', '.join(t.name for t in business_tools))
            print('Tracking connection:', ', '.join(t.name for t in tracking_tools))
            for server, name, args in [(marketplace, 'get_seller_balance', {'seller_id': 'seller-1'}),
                                       (tracking, 'get_tracking_status', {'tracking_id': 'DEMO-TRACK-001'})]:
                result = await server.call_tool(name, args)
                assert not result.is_error
                print(name, json.dumps(json.loads(result.content[0].text), default=str))
            print('PASS: two independent stdio connections, both discoverable and callable')


if __name__ == '__main__':
    asyncio.run(main())
