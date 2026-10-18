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

### Part 2: Add a seller-balance tool (optional coding)

This is the completed version of the exercise’s **same two templates**, using the same temporary package copy and terminal test. It is not a browser integration. The fixed business operation is useful because an agent can request a seller balance by ID instead of generating SQL.

#### Step 1: Create the same lab copy

Run the preparation commands in [exercise Step 1](../exercise.md#step-1-create-the-lab-copy-and-two-files-from-templates). They copy the existing backend package and create two template files in the printed temporary directory. The Test container supplies dependencies and the read-only `market_test` connection. No running application files are changed.

#### Step 2: Complete the seller-balance handler

The complete final file is [seller_balance_tool.py](seller_balance_tool.py). Its destination is `$TOOLS_MCP_LAB_DIR/marketplace/seller_balance_tool.py`—the same file created from the [handler template](../starter/seller_balance_tool.py).

The completed TODO is:

```python
return ctx.query(
    'SELECT seller_id, name, captured, refunded, fees, paid_out, unpaid '
    'FROM analytics.seller_balances WHERE seller_id = %(seller_id)s',
    {'seller_id': seller_id}, 'Read one seller balance')
```

`ctx.query` retains validation, bounded output, the snapshot and the evidence envelope. The seller ID is a bound value, including when it contains SQL-looking text. The seller balance view has one row per seller and returns money in integer paise. Unpaid is not equivalent to release eligibility.

#### Step 3: Register it in the copied server

The complete final file is [marketplace_mcp_server.py](marketplace_mcp_server.py). Its destination is `$TOOLS_MCP_LAB_DIR/marketplace/mcp_server.py`—the same file created from the [server template](../starter/marketplace_mcp_server.py).

Fill the import TODO near the existing package imports:

```python
from .seller_balance_tool import register_seller_balance
```

Fill the registration TODO immediately after the existing loop:

```python
for fn in build_tool_functions(ctx):
    server.tool(structured_output=False)(fn)
register_seller_balance(server, ctx)
```

The new handler shares the original context. Retain the state resource and `finally: ctx.close()`. That resource remains a resource, not a seventh tool. Production HTTP allowlists do not need editing for this isolated stdio lab.

To use the two complete reference files instead of filling the templates manually, run these commands from the repository root after Step 1:

```sh
cp course/exercises/tools-and-mcp/solutions/seller_balance_tool.py "$TOOLS_MCP_LAB_DIR/marketplace/seller_balance_tool.py"
cp course/exercises/tools-and-mcp/solutions/marketplace_mcp_server.py "$TOOLS_MCP_LAB_DIR/marketplace/mcp_server.py"
```

#### Step 4: Run the same test

```sh
docker exec marketplace-lab-memory-backend-1 mkdir -p /tmp/tools-mcp-lab
docker cp "$TOOLS_MCP_LAB_DIR/." marketplace-lab-memory-backend-1:/tmp/tools-mcp-lab
docker exec -w /tmp/tools-mcp-lab \
  -e PYTHONPATH=/tmp/tools-mcp-lab \
  -e LANGFUSE_TRACING_ENABLED=false -e OTEL_SDK_DISABLED=true \
  marketplace-lab-memory-backend-1 \
  python /tmp/tools-mcp-lab/solutions/check_seller_balance.py
```

The complete supplied client is [check_seller_balance.py](check_seller_balance.py), shared by the exercise and solution. It starts the copied stdio server and performs just two operations:

1. **List tools:** expect six names, including the new `get_seller_balance` alongside the existing five.
2. **Call seller balance:** send `seller_id: seller-1` and display the returned row with seller name and `captured`, `refunded`, `fees`, `paid_out` and `unpaid` in integer paise.

The output begins with:

```text
Discovered 6 MCP tools:
  fetch_evidence
  get_catalog
  get_order_history
  get_seller_balance
  query_business_data
  search_documents
```

The seller-balance result follows. Exact amounts depend on the current Test revision. The script closes the connection and stops its server subprocess afterward. It makes no model calls or business-data writes. Tracing is disabled; inspect this output in the terminal.

Keep the command's working directory and Python path so the subprocess loads the lab package. A database-name assertion rejects connections outside `market_test`.

#### Step 5: Use the same cleanup

```sh
docker exec marketplace-lab-memory-backend-1 rm -rf /tmp/tools-mcp-lab
python3 - <<'PYCODE'
import os
import shutil
from pathlib import Path
lab = Path(os.environ['TOOLS_MCP_LAB_DIR']).resolve()
assert lab.name.startswith('tools-mcp-lab.') and lab.is_dir()
shutil.rmtree(lab)
PYCODE
unset TOOLS_MCP_LAB_DIR
```

Both running applications retain their original five-tool server. No restart or database reset is required.
