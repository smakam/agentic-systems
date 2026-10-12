# Session State — worked solution

## UI, database and cleanup

**UI:** [test marketplace](http://127.0.0.1:5179/) from Course Setup; use the role/workspace named in each task. **Database:** disposable practice database `market_test`, separate from main `market` and the fixed evaluation baseline `market_eval`. Test UI changes do not update the main marketplace. Save your questions, results and traces locally.

Part 1 uses Support with OpenAI Agents SDK and newly prepared test orders. Dispatch those orders in the same test marketplace; the fixed evaluation baseline remains unchanged.

**Developer lab:** the optional reference runner uses a temporary backend code copy and disposable `ch10_session_lab`, not the database behind the test UI. The reference resets only that lab between comparisons.

**Cleanup:** the reference runner restores its temporary in-memory session class in `finally`; it does not undo source-file edits. If implementing your own approach, restore the original six-block sliding window and history selector, undo other source/configuration edits and restart the affected backend. Save outputs before deleting the disposable lab. Reset the UI practice database only when a clean seed is needed and no other test user or runner is active; never reset `market_eval`.


This solution follows the three tasks in the [exercise](../exercise.md). Part 1 uses the existing UI. The two optional developer extensions use an isolated code lab. Production history selection stays unchanged.

## 1. Repeat the three demos

### A. Follow-up continuity

Prepare a fresh order with two units and a pending shipment in the test marketplace (`market_test`). Keep the fixed evaluation database `market_eval` unchanged. In a new OpenAI Agents SDK Support conversation ask:

1. “What is the current shipment status for <your prepared order ID>? Cite the evidence.” Replace the placeholder with your order ID.
2. “How many units are in that order?”

Expected observation: history supplies the order reference, so the follow-up refers to the same order. The saved run returned two units without another business-tool call. Inspect actual model input and the answer; a new run can choose additional tools.

### B. Refresh after dispatch

Dispatch that shipment through the seller view, then return to the same Support conversation and ask:

“What is the current shipment status of that order now? Cite current evidence.”

Expected observation: the business revision advances, the agent obtains fresh records, and the answer reports the dispatched status. Earlier pending status remains historical evidence. Compare the tool result's snapshot with the current revision.

### C. Six-question-block boundary

Start another conversation with long-term memory disabled. Introduce the fictional label cedar-window-731, then ask six unrelated arithmetic questions without repeating the label:

- “What is 1 plus ten?”
- “What is 2 plus ten?”
- “What is 3 plus ten?”
- “What is 4 plus ten?”
- “What is 5 plus ten?”
- “What is 6 plus ten?”

Now ask: “What fictional label did I give my sample at the beginning?”

Expected observation: seven stored prior blocks become six supplied blocks. The first label block remains stored but is absent from actual input for this eighth question. Compare stored history with the generation input in Langfuse or the saved captured-input record. A wrong answer alone does not prove exclusion. The saved answer incorrectly denied that the label had ever been given; this is a limitation of selected context, not truth about the complete conversation.

No database-copy commands are needed merely to repeat these UI questions. An automated rehearsal is optional and uses the isolated setup below with `validate_demos.py`.

### Saved demo evidence

[Demo results](demo-results-2026-10-10.json) contain the eleven exact recorded questions, generated order ID, snapshots, selected inputs and traces. Fresh runs use a new order and return new trace IDs.

| Saved operation | Trace ID |
|---|---|
| Initial status | `0e1638805b5bf0af2ed7b5d719d51d32` |
| Quantity follow-up | `81a6601ef96763ce592a9414e00731cd` |
| Status after dispatch | `cd16ec570ade71d09c563112ff8c5682` |
| Eighth-question label recall | `47568b87f54048e7a9513ff68238f800` |

All eleven demo traces and four comparison traces were verified in local Langfuse on October 12. This was readback of saved traces, not a new paid model run or instructor UI rehearsal.

## 2. Developer extension one — change the window

**What changes:** the number of complete prior question blocks selected for model input. No new summarization method is needed. This is a code change in a lab, not a currently exposed UI setting.

Use the exact seven-block fixture and eighth recall question written in the [exercise](../exercise.md#developer-extension-1--change-the-window). The reference supplies those seven exchanges, including known answers, identically to each strategy. It generates only the final recall answer. Each strategy gets its own reset fixture so earlier comparisons do not add extra history.

The implementation is [recent_window and lab_session_class](session_strategies.py). Configure the lab session with `window=2`, `window=6` and `window=8`. Always keep a user question's ensuing calls/results together, preserve full stored history, and supply current investigation metadata separately.

| Window | Prior blocks supplied | Label in actual input | Saved recall result |
|---|---|---|---|
| 2 | Blocks 6–7 | No | Incorrectly chose “ten” |
| 6 | Blocks 2–7 | No | Incorrectly denied the original label |
| 8-block limit | All seven available blocks | Yes | Correct label |

The lesson is input inclusion. A larger window recovers the early label in this fixture because its block is now supplied; this is not proof that a larger window always improves answers. Inspect actual input before interpreting recall.

### One-time setup for either developer extension

Changing selection in an isolated code copy needs a destination database. This setup copies the baseline into `ch10_session_lab` and loads the scripts; it does not modify `market_eval` or main `market`. It is for developer experiments or scripted rehearsal, not Part 1 UI practice.

Run from the repository root with the normal local Docker stack and configured gateway:

```sh
bash course/exercises/chapter-10-session-state/solutions/reset_lab.sh
docker compose -f app/compose.yaml exec -T backend mkdir -p /tmp/ch10-code/marketplace /tmp/ch10-exercises
docker cp app/backend/marketplace/. marketplace-lab-backend-1:/tmp/ch10-code/marketplace
docker cp course/exercises/chapter-10-session-state/solutions/. marketplace-lab-backend-1:/tmp/ch10-exercises
```

Do not reset while another lab runner is active. Both runners refuse a database other than `ch10_session_lab`. The connection strings below are local lab credentials, not cloud or provider credentials.

### Run only the window comparison

```sh
docker compose -f app/compose.yaml exec -T -w /tmp/ch10-code backend env PYTHONPATH=/tmp/ch10-code DATABASE_URL=postgresql+psycopg://market:market-local@postgres:5432/ch10_session_lab READ_DATABASE_URL=postgresql://agent_reader:reader-local@postgres:5432/ch10_session_lab CH10_OUTPUT=/tmp/ch10-window-results.json python /tmp/ch10-exercises/compare_strategies.py --comparison windows
docker cp marketplace-lab-backend-1:/tmp/ch10-window-results.json /tmp/ch10-window-results.json
```

This mode makes three final-answer calls, one per window, and no summary call. Record the resolved model, selected input, answer, tokens and usage. The runner restores the original session class in `finally`; the production default remains six blocks.

## 3. Developer extension two — compaction plus sliding window

**What changes:** how older context is represented in model input. Use the same seven-block fixture and final recall question as extension one. Summarize blocks 1–5 and keep blocks 6–7 intact.

The implementation is [summary_and_recent](session_strategies.py): build a historical summary of the older blocks, then place it before the two recent complete blocks. Current revision, clock and document metadata remain separate. Full stored history is not rewritten or deleted.

Why keep two recent blocks? Summaries can omit exact words, identifiers and tool evidence. Recent full blocks preserve the immediate exchange while the summary tries to carry older details. Two is a lab choice, not a universal requirement; summary-only would be a different experiment.

Preserve the fictional label so the final question can be answered. In a business conversation, preserve relevant order identifiers and evidence provenance too. The summary describes past exchanges, not new agent instructions or proof of current business status. Current freshness metadata still governs evidence reuse.

### Run only the summary comparison

Reuse the isolated setup from extension one. It does not need a second database or another provider configuration:

```sh
docker compose -f app/compose.yaml exec -T -w /tmp/ch10-code backend env PYTHONPATH=/tmp/ch10-code DATABASE_URL=postgresql+psycopg://market:market-local@postgres:5432/ch10_session_lab READ_DATABASE_URL=postgresql://agent_reader:reader-local@postgres:5432/ch10_session_lab CH10_OUTPUT=/tmp/ch10-summary-results.json python /tmp/ch10-exercises/compare_strategies.py --comparison summary
docker cp marketplace-lab-backend-1:/tmp/ch10-summary-results.json /tmp/ch10-summary-results.json
```

This mode makes one older-history summary call and one final-answer call. Compare its input and answer with the window results. `--comparison all` runs both extensions together if desired.

### Saved comparison and interpretation

[Strategy results](strategy-results-2026-10-10.json) retain original inputs, summaries, outputs and usage. The stored seven-block fixture was preserved in all cases.

| Strategy | Label in input | Correct label recalled | Selected serialized characters | Answer input tokens |
|---|---|---|---:|---:|
| Two blocks | No | No | 214 | 2,014 |
| Six blocks | No | No | 642 | 2,110 |
| Eight-block limit | Yes | Yes | 790 | 2,137 |
| Summary + two recent blocks | Yes | Yes | 1,209 | 2,254 |

The summary retained the label, but did not save input size for this short fixture: its wrapper and text were larger than the older turns they replaced. Summary generation added 230 input and 155 output tokens, 385 total. Include that call when comparing usage. Characters are not tokens; recorded cost estimates are not invoices. This experiment does not show a general accuracy or cost advantage for compaction.

| Comparison | Saved trace ID |
|---|---|
| Two blocks | `e858cca776504cea0457edc2a3de7422` |
| Six blocks | `ca2f4aa7d6944458d7d5e057da1f6be1` |
| Eight-block limit | `2b25e2bca25342b7446a07e705cb3f99` |
| Summary + two | `cb6a6d59aa3d07051f5699f27019efe9` |

Summary-generation usage is separate from the four answer traces; no separate summary trace ID is claimed.

## Checks and cleanup for the developer lab

Offline contract checks need no database or paid API:

```sh
python3 -m unittest discover -s course/exercises/chapter-10-session-state/solutions -p 'test_*.py' -v
```

After saving results, remove only the disposable database if no lab runner is active:

```sh
docker compose -f app/compose.yaml exec -T postgres dropdb -U postgres ch10_session_lab
```

The drop command above is only for `ch10_session_lab`; never substitute `market_test`, `market_eval` or main `market`. If repeating an automated demo, reset only the disposable lab first. [Historical validation](../../../../app/results/chapter-10-validation-2026-10-10/historical-validation.md) retains execution provenance and earlier attempts separately from the learner setup. The revised CLI selectors are checked without fresh paid model calls; instructor UI rehearsal remains separate.
