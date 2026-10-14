# Instructor demo: a standalone Lyzr support agent

## Workspace and preparation

Use **Lyzr Studio → Support Agent Basics → Playground**. Complete [setup-guide.md](setup-guide.md) once before the demonstration. Confirm the separate fictional KB is ready and attached. This lab does not use marketplace chat, SQL, MCP, a tunnel or the existing Marketplace Support agent. The [prepared Basics agent](https://studio.lyzr.ai/create-new-agent/6acf95f3272a149412fd9e7c?tab=playground) passed bounded API lookup, missing-ID and same-session follow-up checks. Native Cognis is enabled with Cross Session OFF. Native Playground lookup, same-chat follow-up and missing-ID checks passed, with actual KB source chunks visible in Activity; label observed results and failures accurately.

## A. Knowledge retrieval and native execution

1. Start a fresh chat. Ask **“What products and quantities are in order-demo-1?”**
2. Expected fixture facts: **Ceramic Mug Set, quantity 2**. Inspect the retrieved source record and dataset/as-of marker.
3. Open native Activity/Traces. Find model input/output and Knowledge Base retrieval, including actual retrieved chunks. A KB search is not a Python function-tool call.
4. Record the configured and reported model, session identity, source records, latency and usage when available. Missing cost is not zero.

## B. Same-session context versus a new chat

1. In the same chat ask **“What is its payout status?”** Expected: **held**, for order-demo-1.
2. Inspect retained order context and fresh retrieval if it occurs.
3. Start a new chat and ask only **“What is its payout status?”** Observe whether it requests an order ID. Do not call a guessed order memory recall.

## C. Missing records and evidence limits

1. In another fresh chat ask **“What is the payment status of order-demo-999?”**
2. Expected boundary: the complete fictional catalogue contains only order-demo-1, -2 and -3. No payment status should be invented for -999.
3. Distinguish an absent fixture record from failed KB retrieval. If sources are missing, the answer should state the retrieval limit.
4. Ask **“Is order-demo-1 eligible for payout release now?”** The fixture supplies payout status, not eligibility policy or a live clock; inspect whether the answer respects that limit.

## D. Optional native memory inspection

1. This is an optional, unverified extension. Core Cross Session is OFF; changing it requires its own extraction/retrieval checks. Inspect the actual Cognis/session settings. State **“I prefer support answers in a compact table with Finding, Evidence and Next action.”**
2. Inspect native extraction/storage if available. Acknowledgement and answer formatting alone do not prove a save.
3. In a fresh chat ask about order-demo-2 payout status (**released**). Inspect actual memory retrieval/context separately from KB retrieval.
4. Record successful generation, storage, retrieval and answer use as distinct observations. Native identity, deletion and provenance guarantees require their own checks.

The main demonstration is complete after A–C. Do not repeat deployment steps during every query. Use actual results rather than guaranteed model wording.
