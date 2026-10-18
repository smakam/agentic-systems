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

### Part 2: Additional challenges (optional coding)

#### Challenge 1: Add a tool to the marketplace server

Implement `get_seller_balance(seller_id)` as a bounded, parameterized read of `analytics.seller_balances`. Return seller identity, captured, refunded, fees, paid_out and unpaid in integer paise, using the existing evidence envelope and snapshot. Unknown seller returns no rows. Clarify that unpaid includes held/failed payouts and does not imply release eligibility.

Register the tool in an isolated copy of the existing local marketplace MCP server. Discover it, call it for a known seller and an unknown seller, and compare with the existing query tool under the same snapshot. Prove that input is bound as a value, not concatenated into SQL. Keep production's five-tool allowlist unchanged.

**What to check and record:** implementation diff, discovery schema, calls/results, reconciliation check (`captured = refunded + fees + paid_out + unpaid`) and a note on grain (one row per seller). Compare stored expected facts rather than model wording.

#### Challenge 2: Create a tracking MCP server

Build a separate server exposing `get_tracking_status(tracking_id)` over `tracking-data.json`. It runs as a separate process on the same machine; no extra HTTP backend or database is required. Include status, latest event, observation timestamp and an explicit simulated-data marker. Return a structured not-found response for unknown IDs.

Connect it alongside the marketplace server through a second stdio connection. Ask **“What is the tracking status of DEMO-TRACK-001?”**, inspect the selected tool and returned fixture, then ask **“What is the tracking status of DEMO-TRACK-UNKNOWN?”**. Keep tracking distinct from the marketplace database: this exercise does not add shipment-to-tracking-ID linkage or live carrier data. An HTTP version is optional and uses the same handler.

**What to check and record:** server code, discovery schema, two call outputs, and a two-server connection diagram. Explain how adding a new tool differs from connecting a new server.



Use a separate lab checkout and a disposable practice database for the coding challenges. The tracking service uses only its JSON fixture. When finished, stop the tracking process and restore the lab tool/client configuration. The core read-only task requires no database reset.

See [the worked answers and reference implementations](solutions/answers.md).
