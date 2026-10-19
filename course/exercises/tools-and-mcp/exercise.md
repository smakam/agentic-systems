# Tools and MCP exercise

## Prerequisites

- Complete [Course Setup](../../../app/LOCAL-SETUP.md) and keep the application running.
- Open the [Test marketplace](http://127.0.0.1:5179/) as Support or Operator and select **Support workspace → OpenAI Agents SDK**.
- Under **Gateway → Gateway model mapping**, restore the GPT-5.4 default. Keep long-term memory, response caching, guardrails and context suppression off.
- Open [local Langfuse](http://localhost:3000/) and the marketplace support project.
- Keep the business records and demo clock unchanged during the comparison. Use your own trace results; fixed amounts and tool sequences are not guaranteed across datasets or model runs.

## Your task

### Part 1: Inspect the tool inputs and outputs

Start a **New conversation** and ask:

> For order-1, show each seller’s name, payout amount and status, the payout attempt history, and what the policy requires before release.

Open the corresponding Langfuse trace. Select each tool and use **Preview** to inspect the actual input and output. **Attributes** describes the tool contract and metadata; it is not the place to read the invocation arguments.

| Tool | Input to inspect | Output to inspect |
|---|---|---|
| `get_catalog` | No business arguments | Entity definitions, field types, relationships, metrics and units |
| `get_order_history` | `order_id` | Current order-related records and chronological event evidence, including recorded failures or retries |
| `query_business_data` | SQL, bound parameters and purpose | Rows, columns, snapshot details and evidence reference |
| `search_documents` | Query text, effective time, scope and maximum passages (`top_k`) | Policy/runbook passages, source/version details and evidence reference |

Explain how the tool results support the final answer. Distinguish current payout status from earlier attempts, and policy eligibility from an actual completed payout. Money is stored in paise and displayed in rupees.

This question produced all four model-requested tools in the recording rehearsal. Their order and number of calls can vary. If a tool is absent in your run, record that observation and inspect whether the needed evidence was obtained another way. Do not assume a missing tool means the answer is unsupported without checking its inputs and evidence.

To identify the local connection, select the **top-level support-investigation → Attributes → Metadata** and find **`mcp_transport: stdio`**. Tool names alone do not establish the transport. The model requests history through the tool; the application no longer preloads it into the question.

Memory tools are demonstrated by the instructor; there is no memory save, recall or deletion task in this exercise. `fetch_evidence` is available for retained results but is not a required call here.

#### Optional: repeat the same question through cloud HTTP MCP

First complete the [cloud setup guide](../../../app/CLOUD-SETUP.md) and start your cloud services, including Cloud SQL. Use your own cloud marketplace and Langfuse project. If you have not set up cloud, skip this optional activity.

1. Open your cloud marketplace, sign in as Support or Operator and select **OpenAI Agents SDK**.
2. Start a fresh conversation with memory off and ask the **exact same question**:

   > For order-1, show each seller’s name, payout amount and status, the payout attempt history, and what the policy requires before release.

3. In the resulting cloud Langfuse trace, inspect the same four tools’ actual arguments and results. Model-selected calls can vary just as they do locally.
4. Select **top-level support-investigation → Attributes → Metadata**. Compare **`mcp_transport: http`** and **`mcp_endpoint_host`** with the local stdio trace. A Cloud Run endpoint identifies the cloud MCP service; a tunnel endpoint identifies a separately reachable laptop service. HTTP describes transport, not where the agent itself runs.
5. Compare tool contracts rather than assuming identical balances: local and cloud databases are independent. Stop Cloud SQL when you finish using cloud; storage and backup charges can remain while it is stopped.

Keep your question, trace references, important inputs/outputs and transport observations locally. Nothing needs to be submitted. Complete Part 1 before checking the [worked answers](solutions/answers.md).

### Part 2: Add a seller-balance tool (optional coding)

**Purpose:** create a new MCP tool, `get_seller_balance(seller_id)`, that returns one seller’s captured, refunded, fee, paid-out and unpaid amounts. The model can request this operation without composing SQL. You will define its handler, register it with the existing marketplace MCP server and inspect its real input/output contract.

**Where this runs:** a temporary copy of the backend package, tested entirely in the terminal. The test launches that copied MCP server as a separate stdio process, calls it and stops it. It uses the existing Test container’s Python environment and read-only `market_test` connection. Neither running marketplace application is edited or restarted.

#### Step 1: Create the lab copy and two files from templates

Run from the repository root, in one terminal, with the Docker Test backend running from Course Setup. Keep this terminal open for the remaining steps.

```sh
export TOOLS_MCP_LAB_DIR="$(mktemp -d "${TMPDIR:-/tmp}/tools-mcp-lab.XXXXXX")"
mkdir -p "$TOOLS_MCP_LAB_DIR/marketplace" "$TOOLS_MCP_LAB_DIR/solutions"
cp -R app/backend/marketplace/. "$TOOLS_MCP_LAB_DIR/marketplace/"
cp course/exercises/tools-and-mcp/starter/seller_balance_tool.py "$TOOLS_MCP_LAB_DIR/marketplace/seller_balance_tool.py"
cp course/exercises/tools-and-mcp/starter/mcp_server.py "$TOOLS_MCP_LAB_DIR/marketplace/mcp_server.py"
cp course/exercises/tools-and-mcp/solutions/check_seller_balance.py "$TOOLS_MCP_LAB_DIR/solutions/"
printf 'Edit the two files in: %s/marketplace\n' "$TOOLS_MCP_LAB_DIR"
```

These commands create the following two files in the printed temporary directory. Open them in your editor; complete only the marked TODOs.

| File you create | Template | What you must implement |
|---|---|---|
| `marketplace/seller_balance_tool.py` | [Handler template](starter/seller_balance_tool.py) | Return one seller’s balance using `ctx.query` with a fixed SELECT and a bound seller-ID parameter |
| `marketplace/mcp_server.py` | [Server template](starter/mcp_server.py) | Import the registration helper, then call it immediately after the existing tool-registration loop, using the same `server` and `ctx` |

The other backend files and the [test script](solutions/check_seller_balance.py) are supplied unchanged. You do not need to write a client or change the browser application.

#### Step 2: Complete the seller-balance handler in `marketplace/seller_balance_tool.py`

Open `$TOOLS_MCP_LAB_DIR/marketplace/seller_balance_tool.py`. Inside `get_seller_balance(seller_id)`, replace the placeholder with a call to `ctx.query(sql, parameters, purpose)` that:

- Selects `seller_id`, `name`, `captured`, `refunded`, `fees`, `paid_out` and `unpaid` from `analytics.seller_balances`.
- Filters to the requested seller with `WHERE seller_id = %(seller_id)s` and passes `{'seller_id': seller_id}` separately. Do not concatenate the input into SQL.
- Returns the existing query result envelope, including snapshot and evidence reference. An unknown seller returns no rows.

Money stays in integer paise. One row represents one seller; do not join and repeat seller totals across order items. Unpaid includes held/failed payouts and is not proof that funds are eligible for release.

#### Step 3: Register the handler in `marketplace/mcp_server.py`

Open `$TOOLS_MCP_LAB_DIR/marketplace/mcp_server.py` and complete the import TODO and the registration TODO. Keep the existing five tools, state resource and context cleanup. Register the new helper with the same investigation context so the six tools share its snapshot and evidence lifecycle.

#### Step 4: Run the supplied terminal test

After saving both files, return to the **same terminal used for Step 1**, with the **repository root** as its current folder (not the temporary marketplace folder). Run the whole block below. The first command refreshes only the supplied test script; the next two copy your lab into the temporary Docker folder. The final `docker exec` runs the Python client.

```sh
cp course/exercises/tools-and-mcp/solutions/check_seller_balance.py "$TOOLS_MCP_LAB_DIR/solutions/check_seller_balance.py"
docker exec marketplace-lab-memory-backend-1 mkdir -p /tmp/tools-mcp-lab
docker cp "$TOOLS_MCP_LAB_DIR/." marketplace-lab-memory-backend-1:/tmp/tools-mcp-lab
docker exec -w /tmp/tools-mcp-lab \
  -e PYTHONPATH=/tmp/tools-mcp-lab \
  -e LANGFUSE_TRACING_ENABLED=false -e OTEL_SDK_DISABLED=true \
  marketplace-lab-memory-backend-1 \
  python /tmp/tools-mcp-lab/solutions/check_seller_balance.py
```

The Python client, `check_seller_balance.py`, does both operations below. There is no separate command for discovery:

1. Lists the **six MCP tools**: the original five plus `get_seller_balance`.
2. Calls **`get_seller_balance` with `seller_id="seller-1"`** and prints that seller’s name and balance fields in paise. In the supplied dataset, this seller is **Cedar & Co.**

Inside the client, `server.list_tools()` gets the tool list, then `server.call_tool("get_seller_balance", {"seller_id": "seller-1"})` requests that seller’s balance. These calls are already supplied; you do not need to add them.

The output starts with `Discovered 6 MCP tools:` and includes `get_seller_balance`. It then shows that seller’s `captured`, `refunded`, `fees`, `paid_out` and `unpaid` amounts. This demonstrates that you registered the new tool and can call it. Exact amounts depend on the Test revision. It makes no model calls.

If discovery shows only five tools, check the registration TODO and keep both the supplied working-directory and Python-path settings. If the handler raises `NotImplementedError`, its TODO is unfinished. After another edit, repeat the same test commands to copy the updated files into the temporary container directory.

#### Step 5: Remove the temporary lab copy

The test closes its server process automatically. This last step only removes the temporary folders on your computer and in Docker after you finish. It does not delete application files or business records:

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

Keep the two completed files and your discovery/input/output observations if useful. No database reset is needed. [Worked answers](solutions/answers.md) use these same files, steps and test command, with the TODOs completed.
