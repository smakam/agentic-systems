# Chapter 10 — Session state

Status: instructions, executable reference solutions, offline checks and live validation are complete as of October 10. Final live checks used GPT-5.4 through an isolated OpenRouter gateway after direct OpenAI credits ran out. See [reference solution, measured results and runnable setup](solutions/README.md). Instructor UI rehearsal remains separate.

## Repeatable starting state

Keep the fixed evaluation database unchanged. Create a disposable lab database from the same baseline for each rehearsal. Use the same model alias and mapping, history strategy, input questions, and initial marketplace state in each comparison. Record these settings with the results. Reset only the disposable lab between complete runs; never reset the fixed evaluation or interactive marketplace database.

Store full conversation history in PostgreSQL. Apply history-selection changes only to the input selected for the next model call. Preserve complete tool-call/result pairs and current investigation metadata.

## Core exercise — repeat the three demos

1. In a new conversation, ask for a prepared order's shipment status. Follow up with “How many units are in that order?” Inspect the next model input and show how the earlier question supplies the order reference.
2. In the same conversation, dispatch the prepared shipment through the marketplace. Ask for its current status again. Compare business revisions, fresh tool evidence, and the answer. History preserves the reference; fresh evidence establishes the current status. Refresh is instructed by the prompt, so verify it in the trace.
3. In another new conversation, introduce a distinctive fictional label. Add six unrelated question blocks without repeating the label in questions or answers. Ask for the original label. Verify that it remains in stored history but is absent from the selected six-block history and the actual next model input. Do not rely only on the final answer to prove exclusion.

Submit the questions, relevant trace/input excerpts, revisions, and a short explanation for each case. Redact credentials and provider reasoning items.

## Developer extension 1 — change the window

Make the question-block window configurable in a lab implementation. Compare the same saved conversation with windows of two, six, and eight blocks. Verify which original details are included, input size, and complete tool-call/result pairs. Increasing the window should recover an early detail only if its block now falls inside the window. Restore the production default of six afterwards.

## Developer extension 2 — summary plus recent turns

Replace the lab's pure sliding window with a summary of older turns plus two recent complete question blocks. Keep the full stored history unchanged. Label the summary as historical, untrusted conversation data, not instructions or current business evidence. Preserve identifiers and important user facts, and keep current revision, clock, and document metadata separate.

Use the same early-detail conversation as the window comparison. Compare retained details, input size, summary-generation usage, answer usage, and answers. Inspect omissions and unsupported additions in the summary. A smaller input is not evidence of better accuracy.

## Cleanup

Restore the six-block selection policy and remove only disposable lab conversations/data. Retain sanitized results and settings so another person can reproduce the experiment. The fixed evaluation database must remain unchanged.
