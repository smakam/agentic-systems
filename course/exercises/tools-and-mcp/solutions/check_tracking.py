"""Discover and call the fixture-backed tracking server; no paid model calls."""
import asyncio
import json
import os
import sys
from pathlib import Path
from agents import set_tracing_disabled
from agents.mcp import MCPServerStdio

set_tracing_disabled(True)


async def main():
    script = Path(__file__).with_name('tracking_server.py').resolve()
    async with MCPServerStdio(params={'command': sys.executable,
                                     'args': [str(script)], 'env': dict(os.environ)}) as server:
        definitions = await server.list_tools()
        assert [t.name for t in definitions] == ['get_tracking_status']
        print('Tracking input schema:', json.dumps(definitions[0].input_schema))
        for tracking_id, expected in [('DEMO-TRACK-001', 'ok'), ('DEMO-TRACK-UNKNOWN', 'not_found')]:
            result = await server.call_tool('get_tracking_status', {'tracking_id': tracking_id})
            assert not result.is_error
            data = json.loads(result.content[0].text)
            assert data['status'] == expected and data['simulated'] is True
            if expected == 'ok':
                assert data['tracking']['status'] == 'in_transit'
                assert data['tracking']['observed_at'] == '2026-10-10T09:00:00Z'
            print(json.dumps(data))
        print('PASS: tracking discovery, known fixture and explicit not-found response')


if __name__ == '__main__':
    asyncio.run(main())
