# Validation status — 2026-10-02

Agent: Marketplace Support — MCP Lab
Studio: https://studio.lyzr.ai/create-new-agent/6abfbf34013b6eb4db9ff6f0?tab=playground
Model: OpenAI gpt-5.4-mini. Memory feature removed. Seven remote MCP actions attached.

## Verified

- Complete current-source test suite: 68 passed (including 3 new HTTP MCP tests).
- Public tunnel: MCP SDK initialize and all seven tools discovered.
- Catalog, SQL, order history, policy retrieval and investigation cleanup exercised through Studio or public SDK.
- Unauthenticated access returns HTTP 401; tests reject untrusted hosts/origins and business writes.
- Snapshot/evidence isolation, expiry, capacity, missing order and order/payment summary retrieval tested.
- Final Studio end-to-end question: current order/payment states, current seller payouts, historical failure, and settlement policy. Response completed in 13.39 seconds.
- Actual records at revision 24 / demo clock 2026-09-28 12:00 UTC: order-1 paid, payment captured, payout-1 and payout-2 completed; payout-1 previously failed with a simulated provider timeout.
- All three final citation handles match actual returned evidence. end_investigation closed the snapshot.

The final answer, trace proofs, policy payload, transcript and screenshot are saved in this directory. No interactive business state was reset; tests used market_test.

## Observed limitations

GPT-5 nano reached tools and repaired a SQL error, but added unsupported payment/payout statements. It also used Lyzr's human_as_tool to narrate planned work without executing. GPT-5.4 nano completed a history/policy test, but a later Cedar query shortened citations and changed an order ID. The saved mini model plus stronger instructions passed the final smoke test; this is not a broad model evaluation or a guarantee of correctness.

The Cedar name-resolution query checked both sellers and products and found only seller Cedar & Co. in the current database. It therefore did not exercise the multiple-match clarification branch.

Lyzr runs the agent loop. Existing application-side OpenAI final-answer validation and Langfuse run recording are not executed by this remote-tool integration. Tool-side SQL restrictions, read-only DB permissions, retrieval and evidence contracts remain active. This is a single-principal synthetic-data demo, not production tenant authorization.

Keep the Mac awake, Docker and tunnel running. The endpoint is in .remote-mcp/endpoint.txt; a restarted tunnel gets a new URL that must be updated in Studio. Use scripts/remote-mcp.sh stop to close external reachability.

## API deployment

Deploy → Agent API confirmed Agent deployed on 2026-10-02. API deployment is automatic on saving; no public App Store publication was performed. MCP service remained running. Dashboard status and prior Playground execution are verified; external API invocation has not been separately tested.

## Reconnection and session memory — October 3, 2026

Controlled two-turn comparison (historical instructor evidence; retained separately): working MCP with Memory off answered order-2, then asked for its ID on the follow-up. With Cognis enabled and Cross Session off, a fresh session resolved the same follow-up to order-2 and fetched fresh payment evidence. This one smoke comparison verifies session continuity, not broad memory quality or Cognis internal storage behavior. Current agent uses the Reconnected MCP entry. Stable-hostname tunnel choice is deferred; quick-tunnel URL still changes on restart.

## Stable ngrok endpoint — October 3, 2026

Verification and lifecycle (historical instructor evidence; retained separately): authenticated initialize/tools discovery, missing-key 401, same URL after service restart, and Lyzr order-2 lookup in 14.70 seconds with actual ngrok tool trace and cleanup. Login startup configured outside Documents after a macOS access failure. Docker dependencies use unless-stopped; actual reboot and Docker login preference untested. Old Cloudflare process stopped; Stable replaces Reconnected as active attachment.

## Subsequent stable endpoint and native memory validation

The earlier Reconnected/temporary-endpoint state is historical. Current agent uses Stable ngrok and native Cognis Cross Session ON. Native memory report (historical instructor evidence; retained separately) records passed recall/control tests and the shipment-retrieval gap in autonomous checklist use. Provider CRUD/provenance/isolation parity is unverified.

### External agent API verified — October 3, 2026

Result and reusable curl (historical instructor evidence; retained separately): HTTP 200 in 17.23 s; latest deployed agent returned correct order-2 paid/captured status and evidence references in a fresh API session. First masked-key attempt returned 403; existing unmasked key succeeded. Credential absent from saved request/report and temporary credential files removed. User reviewed tracing/monitoring UI and accepted it. Checklist-use gap, native memory identity/provenance/CRUD checks, cloud hosting/reboot verification and deeper observability are tracked as enhancements in course section 21.
