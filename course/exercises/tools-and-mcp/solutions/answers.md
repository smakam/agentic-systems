# Tools and MCP worked answers

## Prerequisites

Use the running Test marketplace and SDK runtime from [Course Setup](../../../../app/LOCAL-SETUP.md), with GPT-5.4, memory and experimental options off. Open local Langfuse. Cloud comparison requires your own completed [cloud setup](../../../../app/CLOUD-SETUP.md). The coding challenges use an isolated temporary package copy and read-only Test data.

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

These solutions run in an **isolated temporary copy**, using the existing Test backend’s Python dependencies and read-only `market_test` connection. They do not replace the running application's files or require a restart. Run the commands below from the repository root, in the same terminal. Complete the Docker-based [Course Setup](../../../../app/LOCAL-SETUP.md) first; the Test backend container must be running.

#### Challenge 1: Add a seller-balance tool

**Complete solution files and destinations**

| Supplied final file | Destination inside the temporary backend package | Purpose |
|---|---|---|
| [seller_balance_tool.py](seller_balance_tool.py) | `marketplace/seller_balance_tool.py` | Registers `get_seller_balance(seller_id)` using the existing investigation context |
| [marketplace_mcp_server.py](marketplace_mcp_server.py) | `marketplace/mcp_server.py` | Complete server file, including imports, the five existing tools, new registration and state resource |
| [check_seller_balance.py](check_seller_balance.py) | `solutions/check_seller_balance.py` | Complete stdio discovery and result check; no model calls |

The original package is `app/backend/marketplace/`. The commands copy it to a temporary directory before changing either file. In the final server file, `from .seller_balance_tool import register_seller_balance` imports the helper. Immediately after the loop registering the original five tools, `register_seller_balance(server, ctx)` adds the sixth. Both use the **same `ctx`**, so the snapshot, retained evidence and lifecycle remain shared. The bookkeeping resource remains a resource, not a seventh tool.

**1. Prepare the isolated copy.**

```sh
export TOOLS_MCP_LAB_DIR="$(mktemp -d "${TMPDIR:-/tmp}/tools-mcp-lab.XXXXXX")"
mkdir -p "$TOOLS_MCP_LAB_DIR/marketplace" "$TOOLS_MCP_LAB_DIR/solutions"
cp -R app/backend/marketplace/. "$TOOLS_MCP_LAB_DIR/marketplace/"
cp -R course/exercises/tools-and-mcp/solutions/. "$TOOLS_MCP_LAB_DIR/solutions/"
cp "$TOOLS_MCP_LAB_DIR/solutions/seller_balance_tool.py" "$TOOLS_MCP_LAB_DIR/marketplace/seller_balance_tool.py"
cp "$TOOLS_MCP_LAB_DIR/solutions/marketplace_mcp_server.py" "$TOOLS_MCP_LAB_DIR/marketplace/mcp_server.py"
docker exec marketplace-lab-memory-backend-1 mkdir -p /tmp/tools-mcp-lab
docker cp "$TOOLS_MCP_LAB_DIR/." marketplace-lab-memory-backend-1:/tmp/tools-mcp-lab
```

`marketplace-lab-memory-backend-1` is the Test backend from Course Setup. The scripts explicitly reject a database other than `market_test`. Keep the temporary path shown above for this lab; it is separate from the container's running `/app/marketplace` package.

**2. Discover and call the new tool.**

```sh
docker exec -w /tmp/tools-mcp-lab \
  -e PYTHONPATH=/tmp/tools-mcp-lab \
  -e LANGFUSE_TRACING_ENABLED=false -e OTEL_SDK_DISABLED=true \
  marketplace-lab-memory-backend-1 \
  python /tmp/tools-mcp-lab/solutions/check_seller_balance.py
```

The working directory **and** Python path select the lab package. Omitting the working directory can cause a subprocess to import the running application package instead, which only exposes five tools. This command launches a new stdio server, connects, discovers tools, calls them and closes the connection on exit. Tracing is disabled for these command-line checks; inspect their printed inputs/schema and results in the terminal.

**Expected result:** six discovered tools: `get_catalog`, `query_business_data`, `search_documents`, `fetch_evidence`, `get_order_history` and `get_seller_balance`. The new input schema requires a string `seller_id`. The check calls `seller-1`, an unknown seller and an SQL-looking seller string that must remain a bound value, and compares the known result with the same SELECT through `query_business_data`.

A known seller returns one row with the seller's name and integer `captured`, `refunded`, `fees`, `paid_out` and `unpaid` values in **paise**. An unknown ID returns `status: empty`, no rows and a zero row count. Rows and snapshot must match the original query tool. The check asserts:

```text
captured = refunded + fees + paid_out + unpaid
```

It finishes with `PASS: six tools; known/unknown results; same snapshot and rows; reconciliation`. Amounts depend on your current Test revision, so the script checks the equation rather than assuming fixed values. `unpaid` does not establish payout eligibility.

The helper uses a fixed, bounded SELECT against `analytics.seller_balances` with a bound seller parameter; it does not ask the model to write SQL. Avoid joining and re-summing seller totals across order items. This local extension does not require changing the production HTTP tool allowlist, frontend or agent configuration.

#### Challenge 2: Connect a separate simulated tracking server

Use the temporary copy prepared above. If starting directly with this challenge, run Challenge 1's preparation first. All files below were copied into its `solutions` directory.

| Complete solution file | Purpose |
|---|---|
| [tracking_server.py](tracking_server.py) | Independent MCP server exposing `get_tracking_status(tracking_id)` |
| [tracking-data.json](tracking-data.json) | Simulated tracking fixture, stored beside the server script |
| [check_tracking.py](check_tracking.py) | Discover tracking and check known/unknown IDs without a model |
| [check_two_servers.py](check_two_servers.py) | Keep both stdio connections open and discover/call each server |
| [run_two_server_agent.py](run_two_server_agent.py) | Complete optional agent host using both MCP servers |

**1. Check the tracking server independently.**

```sh
docker exec -w /tmp/tools-mcp-lab \
  -e PYTHONPATH=/tmp/tools-mcp-lab \
  -e LANGFUSE_TRACING_ENABLED=false -e OTEL_SDK_DISABLED=true \
  marketplace-lab-memory-backend-1 \
  python /tmp/tools-mcp-lab/solutions/check_tracking.py
```

The client launches the server using an absolute script path. The server loads JSON relative to its own file, so fixture lookup does not depend on the caller's working directory. Its input schema requires a string `tracking_id`. Expect:

- `DEMO-TRACK-001`: `status: ok`, `simulated: true`, tracking status `in_transit`, the demonstration sorting-centre event, and observation time `2026-10-10T09:00:00Z`.
- `DEMO-TRACK-UNKNOWN`: `status: not_found`, the supplied ID and `simulated: true`.
- Final line: `PASS: tracking discovery, known fixture and explicit not-found response`.

These are fixture records, not a carrier integration. The timestamp is not a live freshness claim.

**2. Connect both servers from one host.**

```sh
docker exec -w /tmp/tools-mcp-lab \
  -e PYTHONPATH=/tmp/tools-mcp-lab \
  -e LANGFUSE_TRACING_ENABLED=false -e OTEL_SDK_DISABLED=true \
  marketplace-lab-memory-backend-1 \
  python /tmp/tools-mcp-lab/solutions/check_two_servers.py
```

Expect six marketplace tools on one connection and only `get_tracking_status` on the other. The script calls seller balance and tracking while **both connections remain open**, then prints `PASS: two independent stdio connections, both discoverable and callable`. Both servers run on the same machine; separate servers do not require separate hosts or databases. No model call is made in either check.

**3. Optional: let an agent choose between both servers.**

This step uses the Test gateway's configured `support-model-test` alias and incurs normal model usage charges. The complete host file opens two `MCPServerStdio` contexts and passes both objects to `Agent(mcp_servers=[marketplace, tracking])`. Both contexts remain active until the runner finishes. It is a command-line lab, not a new option in the running marketplace UI; tracing is disabled and the terminal prints the actual model-requested tool names.

```sh
docker exec -w /tmp/tools-mcp-lab \
  -e PYTHONPATH=/tmp/tools-mcp-lab \
  -e LANGFUSE_TRACING_ENABLED=false -e OTEL_SDK_DISABLED=true \
  marketplace-lab-memory-backend-1 \
  python /tmp/tools-mcp-lab/solutions/run_two_server_agent.py \
  'Show the balance for seller-1 and the simulated tracking status for DEMO-TRACK-001. Keep the two results separate.'
```

Expect a grounded seller balance and the simulated tracking result, presented separately. Inspect the printed tool names rather than assuming a fixed call sequence: the model can choose the new balance tool or the original SQL tool. Tracking data must come from the tracking server. The script bounds the run to four model turns and a two-minute timeout.

To try a missing tracking record, run:

```sh
docker exec -w /tmp/tools-mcp-lab \
  -e PYTHONPATH=/tmp/tools-mcp-lab \
  -e LANGFUSE_TRACING_ENABLED=false -e OTEL_SDK_DISABLED=true \
  marketplace-lab-memory-backend-1 \
  python /tmp/tools-mcp-lab/solutions/run_two_server_agent.py \
  'What is the simulated tracking status for DEMO-TRACK-UNKNOWN?'
```

Expect an explicit not-found answer, without an invented shipment status. The deterministic check in step 1 verifies this tool response even if you skip the paid agent run.

**4. Remove the temporary lab files.**

All subprocesses stop when their client contexts close. After the commands finish, remove only the temporary copies created above:

```sh
docker exec marketplace-lab-memory-backend-1 rm -rf /tmp/tools-mcp-lab
python3 - <<'PY'
import os
import shutil
from pathlib import Path
lab = Path(os.environ['TOOLS_MCP_LAB_DIR']).resolve()
assert lab.name.startswith('tools-mcp-lab.') and lab.is_dir()
shutil.rmtree(lab)
PY
unset TOOLS_MCP_LAB_DIR
```

No database reset or application restart is needed. The running marketplace keeps its original five-tool contract throughout this lab.
