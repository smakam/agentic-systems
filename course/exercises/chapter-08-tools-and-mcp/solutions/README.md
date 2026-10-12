# Chapter 8 worked solution

This is a reference implementation and expected-output guide, not a claim that the owner has rehearsed every application trace.

## Core task

| Group | Tools | Server / authority |
|---|---|---|
| Business definitions, current data, history | get_catalog, query_business_data, get_order_history | Marketplace MCP / catalog and database |
| Document retrieval | search_documents | Same marketplace MCP / document retrieval |
| Retained evidence | fetch_evidence | Same marketplace MCP / evidence owned by the investigation |
| Preference memory | search_memories, save_memory, update_memory, delete_memory | Separate SDK memory MCP / owner-scoped preferences |

The three teaching groups are business, retrieval, and memory; retained evidence supports the first two. `get_catalog` returns definitions/schema, not current business rows. Hosted native memory may have different tools; use the SDK memory path for this exercise.

Local: SDK → stdio marketplace subprocess → database/retrieval. Remote: SDK HTTP MCP client → authenticated HTTPS marketplace MCP service → database/retrieval. A tunnel changes reachability, not the tool contract. A cloud runtime can still launch stdio, so identify transport from actual configuration and metadata. Compare fixed business facts and envelope structure, not identical handles. A write must be rejected by SQL validation/read-only permissions.

## Seller balance implementation

Copy [seller_balance_tool.py](seller_balance_tool.py) into a lab module in the backend package. In a lab copy of `marketplace/mcp_server.py`, after registering the five existing tools, call `register_seller_balance(server, ctx)`. The shared context gives the new tool the same snapshot and retained evidence lifecycle. Discover six tools in the lab. Do not edit production's HTTP client allowlist for this local extension.

The helper binds `seller_id` through psycopg parameters. A known seller returns at most one row; an unknown ID returns an empty rows collection. Verify the five money fields are integers, match the existing query tool, and satisfy the reconciliation equation. Seller totals must not be repeated across an item join and summed. The fixture's actual values depend on the fixed snapshot; do not manufacture numeric expected results. A malicious-looking ID remains a bound value and cannot become a SQL statement. Do not expose exception details or connection credentials in a published tool.

## Separate tracking server

Run [tracking_server.py](tracking_server.py) with the same Python/dependencies as the backend. Launch it through `MCPServerStdio` with an absolute script path. Keep both the marketplace and tracking connection contexts open for the whole agent run and include both server objects in `Agent(mcp_servers=[marketplace_server, tracking_server])`. The server reads its JSON relative to its script, independent of the working directory.

For a quick check using the existing Docker backend, run these from the repository root:

```sh
docker cp course/exercises/chapter-08-tools-and-mcp/solutions marketplace-lab-backend-1:/tmp/ch8-solutions
docker compose -f app/compose.yaml exec -T backend python -c 'import asyncio,json,sys
from agents.mcp import MCPServerStdio
async def run():
    async with MCPServerStdio(params={"command":sys.executable,"args":["/tmp/ch8-solutions/tracking_server.py"]}) as server:
        print([tool.name for tool in await server.list_tools()])
        for tracking_id in ("DEMO-TRACK-001", "unknown"):
            result=await server.call_tool("get_tracking_status", {"tracking_id":tracking_id})
            print(json.loads(result.content[0].text))
asyncio.run(run())'
```

This starts/stops the tracking subprocess within the check and makes no model calls. To integrate with an agent, use the same connection alongside `marketplace.mcp_client.open_mcp()` inside the backend environment; keep both `async with` contexts active until `Runner.run` returns. Do this in a lab script, rather than modifying the production agent just to demonstrate discovery.

For `DEMO-TRACK-001`, expect `status: ok`, `simulated: true`, tracking status `in_transit`, the sorting-centre event, and observation time `2026-10-10T09:00:00Z`. For an unknown ID, expect `status: not_found` with the supplied ID and `simulated: true`. Never interpret the timestamp as live freshness or imply a real shipment lookup.

The marketplace extension reuses its existing context and database. Tracking owns a separate contract, process and fixture. Both can run on the same machine. No new database, carrier account, application login, or marketplace write is needed.
