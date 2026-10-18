"""List the lab MCP tools and call seller balance once; no model calls."""
import asyncio
import json
import os
import sys
from psycopg.conninfo import conninfo_to_dict
from agents import set_tracing_disabled
from agents.mcp import MCPServerStdio

set_tracing_disabled(True)


async def main():
    assert conninfo_to_dict(os.environ['READ_DATABASE_URL'])['dbname'] == 'market_test', 'Run this lab against market_test only'
    async with MCPServerStdio(params={'command': sys.executable,
                                     'args': ['-m', 'marketplace.mcp_server'],
                                     'env': dict(os.environ)}) as server:
        definitions = await server.list_tools()
        names = sorted(tool.name for tool in definitions)
        print(f'Discovered {len(names)} MCP tools:')
        for name in names:
            print(f'  {name}')
        assert len(names) == 6 and 'get_seller_balance' in names, 'Register the seller-balance tool in the copied server'

        result = await server.call_tool('get_seller_balance', {'seller_id': 'seller-1'})
        assert not result.is_error, result.content
        data = json.loads(result.content[0].text)
        print('\nget_seller_balance(seller_id="seller-1") — amounts in paise:')
        print(json.dumps(data['rows'], indent=2, default=str))


if __name__ == '__main__':
    asyncio.run(main())
