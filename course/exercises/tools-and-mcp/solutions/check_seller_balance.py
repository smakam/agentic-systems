"""Discover and call the lab tool through real stdio; no model or data writes."""
import asyncio
import json
import os
import sys
from psycopg.conninfo import conninfo_to_dict
from agents import set_tracing_disabled
from agents.mcp import MCPServerStdio

set_tracing_disabled(True)


def decode(result):
    assert not result.is_error, result.content
    return json.loads(result.content[0].text)


async def main():
    # The commands use the existing Test backend's read-only database connection.
    assert conninfo_to_dict(os.environ['READ_DATABASE_URL'])['dbname'] == 'market_test', 'Run this lab against market_test only'
    async with MCPServerStdio(params={'command': sys.executable,
                                     'args': ['-m', 'marketplace.mcp_server'],
                                     'env': dict(os.environ)}) as server:
        definitions = await server.list_tools()
        names = {tool.name for tool in definitions}
        assert names == {'get_catalog', 'query_business_data', 'search_documents',
                         'fetch_evidence', 'get_order_history', 'get_seller_balance'}
        print('Discovered tools:', ', '.join(sorted(names)))
        definition = next(t for t in definitions if t.name == 'get_seller_balance')
        print('Seller-balance input schema:', json.dumps(definition.input_schema))
        known = decode(await server.call_tool('get_seller_balance', {'seller_id': 'seller-1'}))
        unknown = decode(await server.call_tool('get_seller_balance', {'seller_id': 'seller-does-not-exist'}))
        bound = decode(await server.call_tool('get_seller_balance', {'seller_id': "seller-1' OR '1'='1"}))
        assert bound['rows'] == [], 'Seller input must remain a bound value'
        sql = decode(await server.call_tool('query_business_data', {
            'sql': 'SELECT seller_id, name, captured, refunded, fees, paid_out, unpaid FROM analytics.seller_balances WHERE seller_id = %(seller_id)s',
            'parameters_json': json.dumps({'seller_id': 'seller-1'}),
            'purpose': 'Compare the lab seller-balance tool with the normal query tool'}))
        assert known['rows'] == sql['rows'] and known['snapshot'] == sql['snapshot']
        assert len(known['rows']) == 1 and unknown['rows'] == []
        row = known['rows'][0]
        for field in ('captured', 'refunded', 'fees', 'paid_out', 'unpaid'):
            assert isinstance(row[field], int)
        assert row['captured'] == sum(row[k] for k in ('refunded', 'fees', 'paid_out', 'unpaid'))
        print('Known seller:', json.dumps(known, default=str))
        print('Unknown seller:', json.dumps(unknown, default=str))
        print('PASS: six tools; known/unknown results; same snapshot and rows; reconciliation')


if __name__ == '__main__':
    asyncio.run(main())
