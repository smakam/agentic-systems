# Chapter 8 worked solution

## UI, database and cleanup

**UI:** [test marketplace](http://127.0.0.1:5179/) from Course Setup; use the role/workspace named in each task. **Database:** disposable practice database `market_test`, separate from main `market` and the fixed evaluation baseline `market_eval`. Test UI changes do not update the main marketplace. Save your questions, results and traces locally.

For order and balance comparisons, keep the practice database state fixed while comparing answers. For memory practice, use the same test login and delete only the uniquely labelled preference you create.

**Developer and cloud exceptions:** the seller-balance tool runs in an isolated code copy, explicitly connected to `market_test` or a disposable copy of it; do not inherit a main-database connection. The tracking server reads its JSON fixture and needs no business database. Optional cloud HTTP MCP uses your own cloud UI, MCP endpoint and independent cloud database.

**Cleanup:** stop the tracking process, delete only the exercise memory and restore temporary tool/client configuration. If you edited running application code, undo those edits and restart the affected backend. Read-only business questions do not require a database reset.


This is a reference implementation and expected-output guide, not a claim that the owner has rehearsed every application trace.

## Core task

| Group | Tools | Server / authority |
|---|---|---|
| Business definitions, current data, history | get_catalog, query_business_data, get_order_history | Marketplace MCP / catalog and database |
| Document retrieval | search_documents | Same marketplace MCP / document retrieval |
| Retained evidence | fetch_evidence | Same marketplace MCP / evidence owned by the investigation |
| Preference memory | search_memories, save_memory, update_memory, delete_memory | Separate SDK memory MCP / owner-scoped preferences |

The three teaching groups are business, retrieval, and memory; retained evidence supports the first two. `get_catalog` returns definitions/schema, not current business rows. Hosted native memory may have different tools; use the SDK memory path for this exercise.

Local: SDK → stdio marketplace subprocess → database/retrieval. Remote: SDK HTTP MCP client → authenticated HTTPS marketplace MCP service → database/retrieval. A tunnel changes reachability, not the tool contract. A cloud runtime can still launch stdio, so identify transport from actual configuration and metadata. Compare fixed business facts and envelope structure, not identical handles. Read-only SQL validation and database permissions are implementation safeguards, not a required rejected-write demo.

## Sample questions: expected observations

- **Order question:** answer from current order records, with quantities, product and seller names supported by the returned evidence. Do not require a fixed tool sequence or identical wording; a successful tool result can still be misinterpreted.
- **Seller balance:** captured/unpaid values must match the queried seller balance for the active snapshot. Money is stored in integer paise and displayed in rupees. A previous historical run is not a promised numeric baseline for your data.
- **Payout policy:** retrieved passages should support the delivery requirement, 24-hour hold and blocking returns. If applicable evidence is unavailable, record that outcome rather than invent a rule.
- **Memory:** explicitly save the uniquely labelled display preference, then recall it in a fresh conversation under the same user with memory enabled. Inspect `search_memories`; an answer inferred from current chat history does not establish long-term recall. Delete only that saved exercise record afterward and verify from another fresh chat. Historical conversation messages remain.
- **Optional cloud:** the same order question should return evidence from the cloud database. Identify HTTP using run/configuration metadata and inspect the associated cloud Langfuse trace. Record parity requires aligned starting data; local and cloud records are otherwise independent. This step requires the optional [cloud setup](../../../../app/CLOUD-SETUP.md).

## Historical trace references

These were captured in previous verified runs; this document does not claim a fresh rerun in the learner's environment. Local traces belong to the instructor's local Langfuse project; remote traces belong to the instructor's cloud project. Use the run question/operation and metadata to identify them. A fresh learner execution creates a different ID.

| Environment / operation | Question or retained operation | Trace ID |
|---|---|---|
| Local business stdio | What are Cedar & Co.'s captured amount and unpaid balance? | `75fd6b9921fb40ac72dbadaa45ef00bd` |
| Local document retrieval | What must happen before a seller payout can be released? | `b23d55fec67be91f3a7530589cc5bf1d` |
| Local memory MCP recall | What do I mean by Cedar according to my saved preference? | `987d03dd4cd0b137bd93154ddabc9735` |
| Cloud HTTP MCP | Saved order/history investigation: catalog, order history and SQL calls | `a77bb8845f0a5f206e488a62df783c18` |
| Cloud HTTP follow-up | Saved fresh SQL follow-up investigation | `83f35257e01c32b222d848787f424a22` |

The cloud acceptance export retains results/operations/metadata but not the original question text. The fresh order question supplied in the exercise is a runnable example, not a reconstruction of that exact historical prompt. Existing cloud behavior was verified; fresh-project setup rehearsal is deferred.

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
