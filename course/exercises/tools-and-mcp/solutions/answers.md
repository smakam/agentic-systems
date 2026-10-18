# Tools and MCP worked answers

## Prerequisites

Use the running Test marketplace and SDK runtime from [Course Setup](../../../../app/LOCAL-SETUP.md), with GPT-5.4, memory and experimental options off. Open local Langfuse. Cloud comparison requires your own completed [cloud setup](../../../../app/CLOUD-SETUP.md). The coding challenges use a separate lab checkout and disposable practice data.

## Your task

### Part 1: Inspect the tool inputs and outputs

The local and optional cloud activities use the same question:

> For order-1, show each seller’s name, payout amount and status, the payout attempt history, and what the policy requires before release.

The question combines seller names and current money records, attempt history and policy. In the local rehearsal it produced all four tools below as model-requested calls. The application does not preload the history. A fresh run may choose a different sequence, repeat calls or reuse valid evidence in a follow-up; judge the actual evidence supporting the answer.

| Tool | Expected input | Expected output and interpretation |
|---|---|---|
| `get_catalog` | Empty business argument object | Definitions, types, relationships, metrics and units; not current business rows |
| `get_order_history` | The requested `order_id` | Current order-related records and recorded chronological events, including failed and successful attempts where present |
| `query_business_data` | SQL, `parameters_json` and a readable purpose | Validated, bounded rows/columns with evidence and snapshot metadata. Inspect bound order values and joins used to resolve sellers and amounts. |
| `search_documents` | Query; optional `effective_at`, `scope` and `top_k` | Applicable policy/runbook chunks with source/version details and an evidence reference |

Use **Preview** on the selected tool to see the actual arguments and output. The tool description in **Attributes** is the contract, which stays the same across different calls.

The retrieval passage limit is an input: `top_k` requests at most that many chunks (default four; permitted range one to eight). The actual output count may be lower. `effective_at` selects the date/time at which a policy must be valid; when omitted it defaults to the investigation’s demo clock. Scope filters eligible documents. An evidence reference identifies the saved result used by a citation; it is separate from the document source/version.

For the Test revision-2 fixture, order-1 has Cedar & Co.’s failed payout of ₹4,498.20 and Northstar Goods’ held payout of ₹2,338.20. The event timeline records a simulated provider timeout for the failed payout; the rehearsal found no recorded success or retry for that order. Delivery plus a 24-hour hold and no blocking requested/approved/received return determine ordinary eligibility. A failed payout leaves funds unpaid and needs a separate operator retry; an eligible held payout is not automatically a completed payment. Confirm these facts against your own records, rather than treating the fixture amounts as universal expected values.

The two functional groups **business** and **retrieval** share the marketplace MCP server. `fetch_evidence` retrieves a retained result in that investigation; it is not a fresh SQL or document search and is not required for this exercise. Personal memory uses a separate server and is covered in the instructor demonstration, with no learner memory task here.

#### Local versus optional cloud connection

In each trace select **top-level support-investigation → Attributes → Metadata**:

| Execution | Metadata to inspect | What it establishes |
|---|---|---|
| Local SDK baseline | `mcp_transport: stdio` | A subprocess connection in the SDK runtime environment |
| Cloud SDK HTTP path | `mcp_transport: http` plus `mcp_endpoint_host` | An HTTP connection and its destination host |

The optional cloud activity repeats the **same question** from Part 1 and inspects the same tool contracts. HTTP can reach either a laptop through a tunnel or a cloud MCP endpoint. A cloud runtime can itself launch stdio, so transport and hosting location are different concepts. The Langfuse project where a trace is stored is not proof of the MCP transport. Local and cloud business records can differ.

Use a fresh trace with metadata present. If opening the instructor’s older cloud example from the speaker notes, expand the Langfuse date range to include its recording date. A trace ID filter still respects the selected date range. Instructor examples belong to their originating local or cloud project; a learner’s execution produces new trace IDs.

Finish with experimental settings off. Stop Cloud SQL when cloud practice is finished; storage and backup charges may remain while stopped. Keep observations locally; there is no submission or business-data reset.

### Part 2: Additional challenges (optional coding)

#### Challenge 1: Seller balance implementation

Copy [seller_balance_tool.py](seller_balance_tool.py) into a lab module in the backend package. In a lab copy of `marketplace/mcp_server.py`, after registering the five existing tools, call `register_seller_balance(server, ctx)`. The shared context gives the new tool the same snapshot and retained evidence lifecycle. Discover six tools in the lab. Do not edit production's HTTP client allowlist for this local extension.

The helper binds `seller_id` through psycopg parameters. A known seller returns at most one row; an unknown ID returns an empty rows collection. Verify the five money fields are integers, match the existing query tool, and satisfy the reconciliation equation. Seller totals must not be repeated across an item join and summed. The fixture's actual values depend on the fixed snapshot; do not manufacture numeric expected results. A malicious-looking ID remains a bound value and cannot become a SQL statement. Do not expose exception details or connection credentials in a published tool.

#### Challenge 2: Separate tracking server

Run [tracking_server.py](tracking_server.py) with the same Python/dependencies as the backend. Launch it through `MCPServerStdio` with an absolute script path. Keep both the marketplace and tracking connection contexts open for the whole agent run and include both server objects in `Agent(mcp_servers=[marketplace_server, tracking_server])`. The server reads its JSON relative to its script, independent of the working directory.

For a quick check using the existing Docker backend, run these from the repository root:

```sh
docker cp course/exercises/tools-and-mcp/solutions marketplace-lab-backend-1:/tmp/ch8-solutions
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


Stop the tracking process and restore only the temporary lab configuration when finished. These extensions do not require editing the running regular marketplace or resetting its data.
