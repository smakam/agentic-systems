# Session State — exercise

## Purpose and workspace

Repeat the four instructor checks, including the two-/six-/eight-block comparison, then test manual compaction in the two-block conversation. Use the **Test marketplace → Support → OpenAI Agents SDK** from Course Setup. Keep long-term memory, response caching, RAG experiments and other comparisons off. All required practice runs in the browser; no source edits, terminal commands or database copies are needed.

One question block includes the user question, associated assistant responses, tool calls and tool results. Full history stays stored even when older blocks are omitted or summarized for model input. Use a new conversation for each comparison and keep the same model and questions.

## 1. Repeat the continuity, reuse and freshness checks

Prepare a fresh Test order with two units and a pending shipment using the marketplace workflow. Note its order ID and a valid seller ID, ideally its seller. Do not use or reset the fixed evaluation database.

1. In a new conversation ask: **“What is the current shipment status for <order ID>? Cite the evidence.”** Replace the placeholder. Follow up: **“How many units are in that order?”** Inspect the history and tool arguments: the order reference should carry across questions. A fresh quantity query is valid if the first result did not contain quantity.
2. In another new conversation ask: **“For <seller ID>, show the current captured, refunded, fees, paid-out and unpaid amounts. Cite the evidence.”** Confirm the structured result contains all five amounts; note the revision and evidence handle. Without changing data or clock, follow up: **“What is that seller’s current unpaid balance?”** Inspect the tool calls for evidence reuse without new balance SQL.
3. Keep that balance conversation open. Dispatch the prepared pending shipment through the Test marketplace. Confirm success and a newer business revision. Return to the balance conversation and ask: **“What is that seller’s current unpaid balance? Cite current evidence.”** Inspect the new SQL result and revision. The amount may remain unchanged: the global revision can require refresh after an unrelated change.

Reuse and refresh are instructions to the model, not guaranteed middleware behavior. Record what the trace actually shows. An unchanged revision permits reuse only when earlier successful, non-truncated records fully cover the question. Current time and policy applicability still matter.

## 2. Compare two-, six- and eight-block windows

This is the fourth instructor check. Repeat it with the same label question for each setting.

Open **Workspace options → Session history → History strategy**. Select two blocks for the first run, six for the second, and eight for the third. Selecting a different strategy starts a new conversation. If repeating the same setting, use **New conversation** yourself.

Use this identical sequence for each setting, sending one question at a time:

1. **“For this conversation, use the fictional label cedar-window-731 for my sample. Reply only: noted.”**
2. **“What is 1 plus ten? Answer in one short sentence.”**
3. **“What is 2 plus ten? Answer in one short sentence.”**
4. **“What is 3 plus ten? Answer in one short sentence.”**
5. **“What is 4 plus ten? Answer in one short sentence.”**
6. **“What is 5 plus ten? Answer in one short sentence.”**
7. **“What is 6 plus ten? Answer in one short sentence.”**
8. **“What fictional label did I give my sample at the beginning?”**

Do not repeat the label in the intervening questions. Check that the assistant did not repeat it either. Under the eighth answer, expand **Session history → Selected prior history supplied to the model**. Compare this with the original messages still visible in the conversation.

| Setting | What to inspect before judging recall |
|---|---|
| Two blocks | Which two prior question blocks were supplied? |
| Six blocks | Is the first label block outside the supplied window? |
| Eight blocks | Do all seven available prior blocks, including the label, reach the model? |

The limit is on prior blocks: the eighth question has seven previous blocks, not eight. A correct guess or failed recall alone does not prove which history was supplied.

## 3. Trigger compaction manually

Use the **two-block comparison conversation** after its recall question. This learner extension shows whether summarizing stored history restores a detail that the two-block input omitted. If the conversation is unavailable, select two blocks and repeat the exact eight-question sequence above in a fresh conversation.

1. Confirm **Sliding window — two blocks** is still selected. Inspect the recall answer’s selected input: it should omit the original label block. Expected: the answer cannot recall the label from that input. Record what actually happened.
2. **Stay in the same conversation and keep the two-block setting.** Open **Workspace options → Session history** and click **Compact history**. Do not start a new conversation or type the label again.
3. Inspect **Compacted conversation summary**. Does it preserve the original label accurately? The summarizer reads full stored history, including blocks outside the two-block window.
4. Ask the identical question again: **“What fictional label did I give my sample at the beginning?”** Expected: the answer now recalls the label from the saved summary.
5. Inspect the next answer’s supplied history and compare it with the pre-compaction input. The summary should supply the label; the selected window remains two blocks. Original messages remain stored. Compaction does not mean all original blocks are sent to the answer model.
6. Record omissions or incorrect recall. If the summary omits or changes the label, that is a summary failure. If it preserves the label but the answer fails, investigate answer generation. A correct guess before compaction does not prove the label was in the earlier input.
7. Optionally add a few exchanges and inspect their inclusion alongside the summary. Compaction does not run automatically. Clicking again after new history refreshes the summary; repeating the click without changes reuses it without another model call. No minimum number of exchanges is required.

Compaction itself makes a model call, and the UI shows its input/output token usage. A summary may omit details or introduce errors. Compare its contents and the answer; do not assume summary-only input is always better or cheaper. Token-budget selection and selective history retrieval are discussed conceptually, not provided by these controls.

## Record observations

For each window and manual-compaction run, record the setting, stored versus supplied blocks, whether the label appears in the supplied input, final answer, citations where relevant, and model usage. For the business checks also record revisions and fresh versus reused tool evidence. Keep observations locally; there is no submission destination.

## Finish

Use **Reset to defaults** to restore the six-block default and normal workspace settings. It keeps the current conversation open and preserves stored messages and business data; the next question stops using the active summary. Start a new conversation yourself for a clean comparison. Test orders remain in the practice database.

[Worked answers](solutions/answers.md)
