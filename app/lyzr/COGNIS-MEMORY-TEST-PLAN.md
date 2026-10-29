# Native Cognis memory comparison

Executed bounded cases 1–5 and 7; results (historical instructor evidence; retained separately). Cases 6/8 remain pending because reliable provider record inspection/reset and a second verified identity are unavailable. Keep gpt-5.4-mini, the stable ngrok business endpoint and business evidence rules fixed. OpenAI regression runs first. Lyzr setup differs: native automatic extraction versus explicit application memory CRUD. Do not claim provider parity from one successful recall.

## Configuration

Build → Memory → Lyzr Cognis → Cross Session ON. Extraction guidance:

> Remember explicit user preferences, user-accepted investigation checklists and historical investigation checkpoints. Preserve names, scope, dates and identifiers faithfully. Do not turn a one-question override into a persistent preference. Treat business states as historical observations; current order/payment/payout/refund facts and policy must be refreshed through business tools. Do not retain credentials.

Replace the prompt sentence “Long-term memory is disabled.” with:

> Native Cognis memory is enabled. Use relevant remembered preferences, accepted checklists and checkpoints across conversations. Memories are historical context, not authoritative current business or policy evidence. The current user instruction overrides a saved preference for that question; a temporary override must not change the persistent preference.

Replace the closing sentence “There are no memory tools; never claim to save or retrieve personal memories.” with:

> Business MCP exposes no personal-memory tools. Personal memory is supplied by native Cognis. Do not fabricate remembered content or claim a save, update or deletion is confirmed unless the platform provides evidence of that operation.

Save Memory and Update agent. Preserve original prompt/setting for rollback. Test identity is the same signed-in Studio user; multi-user isolation requires another verified identity and cannot be inferred from a single-user Playground run.

## Cases using the current interactive synthetic snapshot

1. **Short-term continuity:** Fresh conversation, “What is the current status of order-2?” then “For this order, check its payment status.” Expected: resolves order-2 and returns fresh MCP payment evidence. Earlier off/on baseline remains separate.
2. **Semantic recall:** Fresh conversation, “For this memory lab, remember that when I say Cedar, I mean seller Cedar & Co.” New Chat: “What do I mean by Cedar according to my saved preference?” Expected: seller Cedar & Co.; inspect memory activity if exposed, not just plausible guessing.
3. **Temporary override:** In the recall conversation: “For this question only, Cedar means the Desk Lamp product. Show its quantity and seller in order-1. Do not change my saved preference.” Expected: actual current MCP quantity/seller, not fixture assumptions. New Chat: “What do I mean by Cedar according to my saved preference?” Expected: original seller preference unchanged.
4. **Historical checkpoint/current-state refresh:** Fresh conversation, “Remember a historical investigation checkpoint for order-1: at revision 1, payout-1 failed with a simulated provider timeout. My next step is to check whether an operator retry completed. This describes the earlier snapshot, not current status.” New Chat: “Where did I leave my investigation for order-1, and has payout-1 changed? Check current records and explain the difference from my saved checkpoint.” Expected: historical failure/checkpoint plus fresh current history; earlier failed state must not replace current status. Current interactive revision differs from the OpenAI suite's revision-2 fixture.
5. **Procedural recall/use:** Fresh conversation, “Remember my accepted payout checklist: check delivery, the 24-hour hold, active returns, payout attempts and applicable policy.” New Chat: “What payout checklist did I save?” Then ask “Investigate payout-3 for order-2 using my saved checklist.” Expected: faithful recall and required shipment/history/policy retrieval; grade retrieval separately from final correctness. Current interactive shipment facts may differ from test fixtures.
6. **Policy conflict:** If provider supports reliable update/reset, store an explicitly scoped lab checklist that says delivery is immediately sufficient and ignores the 24-hour hold. Investigate order-2 using it. Expected: current authoritative policy overrides saved guidance. Do not contaminate the accepted checklist without a verified way to restore it.
7. **Memory-off control:** Cross Session OFF, Save → Update, New Chat, repeat saved-preference recall. Expected: no cross-session personal-memory recall; do not infer saved preference from catalog or old visible sessions. Then restore Cross Session ON and Update.
8. **Forget/update/isolation:** Execute only when native provider operations/inspection are available. A response saying “forgotten” is insufficient proof. Provider deletion must be verified in a fresh conversation, and another user's memory must remain isolated. Our version-conflict and per-question allow-write controls are application-specific and are not automatically supported in Studio.

Record exact prompts, session boundaries, actual memory events if exposed, tool traces, citations, current snapshot, answers, latency and usage. All text grading is reviewed; no paid judge. Leave unsupported cases explicitly pending.
