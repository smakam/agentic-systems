# Chapter 8 exercise: Tools and MCP

The solution is separate so you can try the tasks before checking the reference implementation.

## Learning goal

Discover and call tools through MCP, distinguish connection transport from tool behavior, extend an existing server, and connect a separate tool system.

## Prerequisites

Use the local environment from **Course Setup**. Cloud deployment is optional and uses your own endpoints/credentials. Keep experiment code in a separate lab checkout. Use the fixed test database for business reads; do not reset or alter its records. The tracking service uses the supplied JSON fixture and needs no database or carrier account.

## Part 1: Repeat what was covered in the demo

Use **OpenAI Agents SDK** in the test marketplace Support workspace. Run the sample questions, or inspect the supplied historical traces from the speaker notes. Fresh runs use your own records and return their own trace IDs; an instructor trace is not your new run.

1. Discover the marketplace and memory tools. Group them into **business**, **retrieval** and **memory**. Business and retrieval share the marketplace server; `fetch_evidence` retrieves saved results for those two groups. Personal memory uses a separate server.
2. Run the order and policy questions below in fresh conversations with long-term memory off. Inspect tool names, input arguments, returned records/passages, evidence handles and the final answer.
3. Use the memory save-and-recall sequence below. Inspect its separate memory calls and clean up only the preference created for this exercise.

| Example | Sample question / operation | What to inspect |
|---|---|---|
| Business order records | **“What products, quantities and sellers are in order-1? Retrieve current records.”** | Catalog definitions and order-history/SQL results used by the answer |
| Business balance example from the saved trace | **“What are Cedar & Co.'s captured amount and unpaid balance?”** | Bound SQL, current seller-balance records and evidence |
| Document retrieval | **“What must happen before a seller payout can be released?”** | `search_documents` query, applicable policy passages and citations |
| Memory save | **“Remember that my tools-and-mcp-demo display preference is amounts in rupees.”** | `save_memory` inputs and saved record ID/version |
| Memory recall in a new chat | **“What display preference did I save for tools-and-mcp-demo?”** | `search_memories` and the returned user-scoped preference |

### Memory settings and cleanup

Enable long-term memory and allow memory changes for the **save** question. Use the unique `tools-and-mcp-demo` label so this practice does not replace an existing preference. For recall, start a new chat under the same login, enable memory, and leave memory changes off. Conversation history alone should not be the source of the recalled preference.

When finished, allow memory changes for a new question and ask: **“Forget only the tools-and-mcp-demo display preference I just saved.”** Inspect `delete_memory`; if the agent finds multiple matching records, select only this exercise's record. Use a fresh chat to check that it is no longer returned. Old conversation messages remain. Do not delete other memories or reset the workspace.

### Optional: compare cloud HTTP MCP

First complete the optional [cloud setup guide](../../../app/CLOUD-SETUP.md) from **Course Setup**. Skip live cloud calls if you have not deployed that environment; you can inspect the supplied historical remote trace instead.

1. Open **your cloud marketplace URL**, sign in to Support and select OpenAI Agents SDK.
2. Ask the same order question: **“What products, quantities and sellers are in order-1? Retrieve current records.”**
3. Open the corresponding trace in **your Langfuse Cloud project**. Inspect model requests, MCP tool inputs/results and final evidence. Record your own trace ID.
4. Compare local **stdio** with cloud **HTTP** using configuration and run metadata alongside the traces. Identical tool names do not prove transport. Compare business facts only if both deployments have the same starting records; local and cloud data do not synchronize automatically.

There is no rejected-write demo or required cloud deployment in this exercise.

### What to check and record

Keep the tool-category map, questions/operations, relevant tool inputs/results, trace IDs and connection metadata locally. Use these to compare with the solution; there is no submission destination. The speaker notes include historical business, policy, memory and remote trace references, identified by their originating environment.

## Part 2: Additional challenges

### Challenge 1: Add a tool to the marketplace server

Implement `get_seller_balance(seller_id)` as a bounded, parameterized read of `analytics.seller_balances`. Return seller identity, captured, refunded, fees, paid_out and unpaid in integer paise, using the existing evidence envelope and snapshot. Unknown seller returns no rows. Clarify that unpaid includes held/failed payouts and does not imply release eligibility.

Register the tool in an isolated copy of the existing local marketplace MCP server. Discover it, call it for a known seller and an unknown seller, and compare with the existing query tool under the same snapshot. Prove that input is bound as a value, not concatenated into SQL. Keep production's five-tool allowlist unchanged.

**What to check and record:** implementation diff, discovery schema, calls/results, reconciliation check (`captured = refunded + fees + paid_out + unpaid`) and a note on grain (one row per seller). Compare stored expected facts rather than model wording.

### Challenge 2: Create a tracking MCP server

Build a separate server exposing `get_tracking_status(tracking_id)` over `tracking-data.json`. It runs as a separate process on the same machine; no extra HTTP backend or database is required. Include status, latest event, observation timestamp and an explicit simulated-data marker. Return a structured not-found response for unknown IDs.

Connect it alongside the marketplace server through a second stdio connection. Ask **“What is the tracking status of DEMO-TRACK-001?”**, inspect the selected tool and returned fixture, then ask **“What is the tracking status of DEMO-TRACK-UNKNOWN?”**. Keep tracking distinct from the marketplace database: this exercise does not add shipment-to-tracking-ID linkage or live carrier data. An HTTP version is optional and uses the same handler.

**What to check and record:** server code, discovery schema, two call outputs, and a two-server connection diagram. Explain how adding a new tool differs from connecting a new server.

## Cleanup and reference solution

Stop the tracking process, remove disposable memory records, and restore the original lab configuration. Keep credentials out of recorded results. See [the worked solution](solutions/README.md) and its supplied fixture/server.
