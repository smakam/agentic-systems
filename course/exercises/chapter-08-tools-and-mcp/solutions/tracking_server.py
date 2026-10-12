"""Standalone simulated tracking MCP server; run using the backend environment."""
import json
from pathlib import Path
from mcp.server import MCPServer

RECORDS = json.loads(Path(__file__).with_name('tracking-data.json').read_text())
server = MCPServer('Simulated courier tracking')

@server.tool(structured_output=False)
def get_tracking_status(tracking_id: str) -> dict:
    """Read a supplied simulated tracking record; never live carrier information."""
    record = RECORDS.get(tracking_id)
    if record is None:
        return {'status': 'not_found', 'tracking_id': tracking_id, 'simulated': True}
    return {'status': 'ok', 'tracking_id': tracking_id, 'simulated': True, 'tracking': dict(record)}

if __name__ == '__main__':
    server.run(transport='stdio')
