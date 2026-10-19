# Session State — worked answers

Follow the browser steps in the [exercise](../exercise.md). These are expected input-selection observations; inspect actual results rather than treating model recall or evidence reuse as guaranteed.

## Continuity and evidence freshness

- The follow-up “that order” resolves to the earlier order ID from the selected conversation history. Quantity may require new SQL if it was not in the first result.
- When the same seller’s successful structured balance result already contains unpaid funds and the business revision is unchanged, the model is instructed to reuse it without another query. Inspect actual tool calls and the original evidence handle. Prompt instructions do not guarantee compliance.
- After dispatch advances the business revision, the current balance question should obtain fresh SQL evidence. Dispatch need not change the balance amount: the global revision is intentionally conservative. Freshness is demonstrated by the new query and snapshot, not a forced amount change.

## Window comparison

The fourth instructor check and repeated learner comparison use the same seven prior blocks. The eighth recall question receives:

| History strategy | Prior blocks supplied | Original label in input? |
|---|---|---|
| Two blocks | Blocks 6–7 | No |
| Six blocks | Blocks 2–7 | No |
| Eight blocks | Blocks 1–7 | Yes |

Full stored history still contains all seven prior blocks in every case. The current recall question is supplied separately. Whole blocks preserve tool-call/result pairs. The final response may be wrong even with the label present, or may guess it despite absence; inspect the supplied input to distinguish those cases.

## Manual compaction

Use the **same two-block conversation** before and after compaction; keep its window setting unchanged and do not repeat the label in a new user message.

| Stage | Evidence available to the answer model | Expected observation |
|---|---|---|
| Before compaction | Last two prior blocks; original label omitted | Cannot recover the label from the supplied input |
| After Compact history | Saved summary of full stored history, plus any later exchanges | Recalls `cedar-window-731` if the summary preserved it |

Inspect the supplied input and summary as well as both answers. A pre-compaction guess is not proof of input coverage. This comparison demonstrates summary-based recovery of older details, not an increase in the two-block window.

**Compact history** summarizes all available stored history in the selected conversation when clicked. It has no six-block threshold and does not automatically retain two recent blocks. Immediately after compaction, the next question receives the historical summary; exchanges added afterward are supplied alongside it, subject to the selected window. Stored original messages are not deleted or rewritten.

The summary should preserve `cedar-window-731` because it occurs in the full stored first block. Check the generated text: if the label was dropped or changed, report a summary failure, not successful compaction. If the summary contains it but the answer fails, investigate answer generation separately.

Compaction is manual. New questions do not invoke the summarizer. Clicking again after new exchanges refreshes the summary from the full stored history. Clicking again without changes reuses the matching saved summary and reports zero new summary calls. The summary is scoped to the owned conversation and is historical, untrusted context, not current business evidence or higher-priority instructions.

The UI reports summary-generation usage separately. The subsequent answer’s tokens reflect the summary included in its input; this is not another summary-generation call. Short examples may not save tokens. Compare actual usage and preservation of details.

## Reset and interpretation

Reset to defaults keeps the conversation open, restores the normal six-block window and stops applying its active compacted summary to subsequent questions. The full conversation, old displayed answers, saved memories and business records remain intact. Choose a new conversation for a clean comparison.

The Test UI supports window comparison and manual compaction. No additional learner files or terminal scripts are required.
