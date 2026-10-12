# Chapter 8 exercise: Tools and MCP

**Status:** Agreed exercise scope; reference implementation provided for owner dry run.

## Learning goal

Discover and call tools through MCP, distinguish connection transport from tool behavior, extend an existing server, and connect a separate tool system.

## Prerequisites

Use the Chapter 4 local environment and instructor-provided remote endpoint/credentials. Keep experiment code in a separate lab checkout. Use the fixed test database for business reads; do not reset or alter its records. The tracking service uses the supplied JSON fixture and needs no database or carrier account.

## Core task: Repeat the chapter demo

1. Discover the marketplace and memory tools. Group them into business definitions/current data/history, document retrieval, and memory. Explain which groups share a server.
2. Run an order question, a policy question, and a preference-memory example. Inspect tool names, inputs, returned evidence, and trace references. Use a disposable memory owner and remove the preference afterward.
3. Call the same marketplace tool through local stdio and the supplied remote HTTP connection. Record the connection configuration alongside the trace: a tool name alone does not prove transport. Compare result structure and business facts; run-specific evidence handles can differ.
4. In the isolated lab, submit a disallowed write and show the tool rejection. Do not bypass validation or use a privileged database account.

**Submit:** a three-group tool map, local/remote connection diagram, trace or call references, one result comparison, and the rejected-request evidence. Remote access unavailable? Record that prerequisite rather than claim a completed remote call.

## Developer extension 1: Add a tool to the marketplace server

Implement `get_seller_balance(seller_id)` as a bounded, parameterized read of `analytics.seller_balances`. Return seller identity, captured, refunded, fees, paid_out and unpaid in integer paise, using the existing evidence envelope and snapshot. Unknown seller returns no rows. Clarify that unpaid includes held/failed payouts and does not imply release eligibility.

Register the tool in an isolated copy of the existing local marketplace MCP server. Discover it, call it for a known seller and an unknown seller, and compare with the existing query tool under the same snapshot. Prove that input is bound as a value, not concatenated into SQL. Keep production's five-tool allowlist unchanged.

**Submit:** implementation diff, discovery schema, calls/results, reconciliation check (`captured = refunded + fees + paid_out + unpaid`) and a note on grain (one row per seller). Compare stored expected facts rather than model wording.

## Developer extension 2: Create a tracking MCP server

Build a separate server exposing `get_tracking_status(tracking_id)` over `tracking-data.json`. It runs as a separate process on the same machine; no extra HTTP backend or database is required. Include status, latest event, observation timestamp and an explicit simulated-data marker. Return a structured not-found response for unknown IDs.

Connect it alongside the marketplace server through a second stdio connection. Ask about `DEMO-TRACK-001`, inspect the selected tool and returned fixture, then try an unknown ID. Keep tracking distinct from the marketplace database: this exercise does not add shipment-to-tracking-ID linkage or live carrier data. An HTTP version is optional and uses the same handler.

**Submit:** server code, discovery schema, two call outputs, and a two-server connection diagram. Explain how adding a new tool differs from connecting a new server.

## Cleanup and reference solution

Stop the tracking process, remove disposable memory records, and restore the original lab configuration. Do not submit credentials. See [the worked solution](solutions/README.md) and its supplied fixture/server.
