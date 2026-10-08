# Backend switch smoke check — October 8, 2026

All six one-question checks passed through the actual marketplace applications. The question was: “What is the status of order-2? Include the current investigation demo clock and cite the evidence.” Each runtime started a fresh conversation. Follow-ups and native long-term memory save/recall were not rerun; this is a connection/source smoke check, not exhaustive agent acceptance.

| Application/profile | Runtime | Result | Snapshot | Answer time | Screenshot |
|---|---|---|---|---|---|
| Local | OpenAI SDK | Paid order; no return/refund; held ₹1,618.20 payout; database/event evidence | September 28, revision 24 | 9.2 s | [Local SDK](results/backend-switch-smoke-20261008/local-sdk.png) |
| Local | Google ADK | Paid order; captured ₹1,798 payment; pending shipment; held ₹1,618.20 payout; evidence citations | September 28, revision 24 | 40.02 s | [Local Google](results/backend-switch-smoke-20261008/local-google.png) |
| Local | Lyzr | Paid order; captured payment; no returns/refunds; held payout; evidence citations | September 28 | 13.22 s | [Local Lyzr](results/backend-switch-smoke-20261008/local-lyzr.png) |
| Cloud | OpenAI SDK | Paid order; no return/refund; held ₹1,618.20 payout; database/event evidence | September 27, revision 1 | 60.83 s | [Cloud SDK](results/backend-switch-smoke-20261008/cloud-sdk.png) |
| Cloud | Google ADK | Paid order; pending shipment; held payout; delivery/24-hour hold policy with citations | September 27, revision 1 | 37.07 s | [Cloud Google](results/backend-switch-smoke-20261008/cloud-google.png) |
| Cloud | Lyzr | Paid order; captured payment; held payout; evidence citations | September 27 | 16.57 s | [Cloud Lyzr](results/backend-switch-smoke-20261008/cloud-lyzr.png) |

## Repair and configuration checks

The initial switch updated Google's environment metadata correctly, but its serialized MCP client retained the cloud URL while runtime authentication switched to the local secret. Resolving the URL when the deployed process creates its MCP client fixed this mismatch. The repaired local deployment completed, then the coordinated script successfully switched Google and Lyzr to cloud. Readback confirmed the cloud URL/secret pair and the `runtime-url-v1` compatibility marker. The script rejects older packaged deployments on apply.

Google packaging/policy regression checks: 4 passed in the pinned Cloud Shell environment. Hosted adapter/API checks: 8 passed against the isolated local test database. Coordinated switch checks: 10 passed offline. Frontend production build passed. URL and credentials are absent from the serialized agent.

Memory controls are SDK-only in the shared chat. Google/Lyzr follow hosted configuration; the Google adapter sends neither memory state overrides nor session-save requests. Google deployed retrieval remains enabled. Earlier native memory save/recall tests in the selector guide are historical evidence; they do not imply automatic session saving in the current chat.

The cloud memory UI update was applied through the existing Terraform state. A Cloud Shell quota-project mismatch initially blocked refresh; selecting the marketplace project fixed it. No resources were deleted. Cloud web/MCP image readback confirmed ready status. A small follow-up UI cleanup removes an empty legacy Google memory footer label.

## Handoff

Hosted agents are now configured for **local**; Cloud SQL is parked. To start your own local walkthrough, keep Docker/tunnel running and execute `python3 scripts/switch-backend.py local --apply` from `app`, then start fresh conversations. This changes the shared Google and Lyzr agents for all callers. SDK always uses the application environment. Your independent walkthrough remains pending.


## Shared formatting and source viewer

Markdown tables and safe line breaks now render across all runtimes. Google tool responses and Lyzr's matching inference/tool trace supply saved source envelopes to the existing evidence viewer. The Lyzr listing returns a null agent field, so identity is verified in the inference span against the stored agent/session and exact final answer. Provider metadata is excluded. Evidence lookup is bounded and failure leaves the successful answer intact with unavailable citations clearly labelled.

Validation: 16 backend adapter/evidence checks and 15 frontend checks pass. Both local hosted smoke-test answers were restored from their actual tool records; clicked database buttons display revision-24 order/payment rows. [Local Google source](results/backend-switch-smoke-20261008/local-google-source.png) and [Local Lyzr source](results/backend-switch-smoke-20261008/local-lyzr-source.png).

Final cloud r15 was applied through the existing Terraform state, with no deletion. Web ready status and immutable image were read back: `sha256:f70aaca1a54518c20966cf19135e4db5e87dd9ee7db0f449798695ac0b1340df`. Web and MCP both report ready and route 100% of traffic to the latest revision. Fresh cloud Google order-2 passed in 102.67 seconds with five saved source envelopes; clicked database rows show revision 1. [Google cloud source](results/backend-switch-smoke-20261008/cloud-google-source.png). Lyzr status table rendered, but initial trace lookup yielded no sources; its recent-history retry recovered four actual envelopes. Fresh cloud Lyzr status rerun passed in 24.56 seconds with four saved sources appearing automatically. Clicked database rows show revision 1. [Lyzr cloud source](results/backend-switch-smoke-20261008/cloud-lyzr-source.png). Older answer history is not automatically backfilled.

Delayed Lyzr trace recovery also retries a missing source bundle when reading the newest completed answer (within 15 minutes). Existing source bundles remain immutable. The retry uses the stored agent/session and exact answer, makes no inference or business tool calls, and remains optional if telemetry is unavailable. Five answer-history/feedback and cloud-auth checks also pass.


## Additional cloud concurrency repair

An additional Lyzr payout question hit the app's 120-second provider read timeout. Its native trace recorded successful order-history retrieval followed by roughly 181-second catalog/policy tool timeouts. The cloud registry held a PostgreSQL row lock while awaiting a tool, while another call synchronously waited for that lock on the same event loop. The original blocking behavior was reproduced against a separate disposable PostgreSQL instance (`LockNotAvailable` with a short test lock timeout). Async PostgreSQL lock waits let the awaited tool complete while retaining serialized evidence/call budgets across replicas. Both durable-registry tests pass, including concurrent delayed retrieval plus catalog and the existing restart/drift/expiry test. The repair was deployed as r14; the same payout question then passed in 80.29 seconds with five saved sources, a rendered Status/Reason/Next step table, and clickable database/policy buttons. The policy viewer opened the actual retrieved settlement, incident, runbook and returns passages. [Payout policy proof](results/backend-switch-smoke-20261008/cloud-lyzr-policy.png). The disposable test database was removed after validation.


Final verification: local main/test proxy health passed; cloud web/MCP image and traffic readback passed. Sixteen adapter/evidence tests, five history/auth checks, two durable-registry checks and fifteen frontend checks passed (38 targeted checks). The r15 follow-up retains catalog definitions in source envelopes; its regression check passed. No additional paid agent rerun was needed for that field-retention change. [Formatted cloud Lyzr answer](results/backend-switch-smoke-20261008/cloud-lyzr-formatted.png).


### Local-first pause acceptance — October 8

Both Google and Lyzr local profile settings were read back as verified by the switching script. Fresh direct local marketplace API questions completed through each hosted runtime while Cloud SQL was stopped. Google reported paid/captured/pending; Lyzr reported paid/captured/held and no return/refund. Saved source evidence was present for both. The first smoke predicate incorrectly required an unrequested payout amount in every answer; the saved responses were regraded for the requested order/payment status and evidence instead, without another inference run. Both passed. Cloud database activation policy is NEVER; restart before using cloud chat/SDK/MCP. Local UI remains on the SDK for the user's recording work.
