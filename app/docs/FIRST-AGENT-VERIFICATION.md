# First agent — model, evidence and trace checks

Use these checks in Chapter Five, after the local setup and login checks are complete. They send paid model/embedding requests through the selected provider.


Use a newly seeded workspace for the stated business expectations. An existing workspace may have different order status because you changed it in a prior lesson.

1. Start a new conversation. Leave gateway guardrails **Off**, long-term memory **Off**, and memory changes **Off**. Keep source authority at its normal enabled setting.
2. Ask: **“What products, quantities and sellers are in order-1?”** Expected seed: two Canvas Weekenders from Cedar & Co. and two Desk Lamps from Northstar Goods. Open the database citation to inspect records; prose alone is not evidence.
3. In that same conversation, ask: **“What is the total quantity of those items?”** Expected total: **4**. This checks short-term conversation context, regardless of whether the model reuses records or queries again.
4. In a new conversation, ask: **“What does the payout policy require before a seller can be paid?”** Inspect policy citations and the search result. The normal policy requires confirmed delivery plus a 24-hour hold, subject to blockers such as active returns. Verify vector versus lexical retrieval in the returned technical details.
5. Open the answer's trace in local Langfuse, project **Support experiments**. One question execution is one trace; generations and tool calls are observations within it. Follow model input → tool result → subsequent generation → final answer. Tool selection is model-dependent, so every question need not follow an identical sequence.
6. Give a completed answer thumbs-down, reload/reopen the conversation, and check the vote persists. Its trace should show `user_feedback = False`; thumbs-up is `True`. PostgreSQL is authoritative; score export to Langfuse is best effort. Scores analytics summarize **rated** answers, not correctness.

The conversation must belong to the signed-in user to rate it. If an answer is incorrect, preserve the trace and evidence; don't change the fixture merely to make it pass. Saved [regression answers](../results/core18-history-v3-2026-10-01/REPORT.md) can be inspected without paying to rerun a benchmark.

Long-term-memory exercises belong to the later memory chapter; they are not required for setup completion. See the [memory catalogue](../eval/memory-v2/README.md) when reaching that lesson.

