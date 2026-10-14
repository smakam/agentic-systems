# Chapter 20 reference answers

These are evidence checkpoints, not promised fresh model outputs. The core lab uses native Lyzr KB retrieval; the optional exercise connects a separate marketplace agent to your GCP backend.

## Native Basics

| Question | Fixture boundary |
|---|---|
| Products and quantities in order-demo-1 | Ceramic Mug Set × 2 |
| Same-chat payout follow-up | Held, for order-demo-1 |
| Payout for order-demo-2 | Released |
| Payment for order-demo-3 | Refunded |
| Payment for order-demo-999 | Absent from the complete fictional catalogue; do not invent status |
| Ambiguous fresh-chat follow-up | Request the order identity; do not silently inherit another session |
| Release eligibility | Not established: there is no eligibility policy/live clock in this fixture |

The KB's source comes from the same fictional JSON as Google Basics. Google executes a native Python lookup function; Lyzr retrieves indexed source records. Compare the actual grounding path, not the two platforms' answer quality from a handful of runs.

## Optional integration

The browser calls the GCP web backend; it calls the authenticated Lyzr inference API. The hosted agent calls the GCP MCP endpoint with a separate credential. MCP supplies scoped read-only business evidence from the cloud database/policy target. The runtime selector chooses the hosted agent; it does not move its KB, tools or data target.

Inspect begin/end investigation and source-bearing read tools. An answer alone does not prove the cloud target: record configuration and a matching native tool result. Application Langfuse may expose the hosted-call boundary while Lyzr native traces expose internal model/tool execution.

Keep session continuity separate from cross-session Cognis memory. Verify memory formation, stored record, fresh-session retrieval and answer use independently. Missing native visibility is a recorded limitation, not a reason to substitute local memory semantics.

## Operational interpretation

Hosted Studio removes some runtime/build plumbing; developers retain tool authorization, source quality, identity and integration responsibilities. Private/VPC/on-premise options require the appropriate enterprise deployment arrangement; model providers and network/telemetry routes still determine where data goes. ADK/API access is not evidence of fully local inference.

Model/context tokens, indexing/retrieval, enabled tools/features and plan usage drive costs; optional GCP compute/database/network/telemetry adds separate charges. Account billing and contract terms govern actual rates. Native safety/evaluation features are capabilities, not proof every policy is enabled or every answer is correct.

## Acceptance and cleanup

Record failed and unverified checks alongside successful ones. Preserve instructor/shared resources and remove only your own optional integration resources. The main course lesson does not require this optional deployment to pass.

## Bounded rehearsal evidence

The prepared Basics agent passed API products/quantity for order-demo-1, released payout for order-demo-2, missing order-demo-999 and a fresh same-session follow-up returning held. Cognis was explicitly enabled with Cross Session OFF after the initial follow-up without session memory requested an ID. Returned `module_outputs.documents` contain source text, metadata and relevance scores; the scores do not grade correctness. Native UI lookup, same-chat follow-up and missing-ID checks also passed. Activity exposed kb_documents_retrieved with the actual orders-knowledge.txt source chunk. The bounded optional cross-session API experiment also passed, as described below. See `app/lyzr/basics/verification.json`.

## Optional native cross-session reference

With Cognis Cross Session ON and explicit preference-retention instructions, a fresh synthetic owner began with zero records. A conversation preference automatically produced a native record containing cobalt-sparrow and the three headings, matching the original user text and owner/agent/source-session references. Fresh same-owner recall reproduced the preference; a fresh order-demo-2 answer stated released with the saved headings and KB evidence. A different synthetic owner had zero records and no verified preference. Four model calls were used; no direct memory-add call seeded the result.

This verifies a bounded native API path, not every Playground UI surface or universal isolation/deletion behavior. Restore the core default Cross Session OFF after the experiment. See app/lyzr/basics/cross-session-verification.json.
