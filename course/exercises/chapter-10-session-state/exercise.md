# Chapter 10 — Session state

Status: instructions, reference solutions and saved validation are available. Use the normal configured gateway for learner runs. Instructor UI rehearsal remains separate.

## Choose your practice path

- **Part 1: UI practice.** Use the already running local marketplace and Langfuse from Course Setup. Prepare a fresh demo order in the regular interactive marketplace; keep the fixed test database unchanged. You do not need to create or reset a lab database just to repeat these UI questions.
- **Part 2: optional developer challenges.** If you want to change the history-selection code, use the disposable lab setup in the solution. The database-copy and script commands apply to this path, or to an automated instructor rehearsal.

## Starting state for the scripted developer lab

Keep the fixed evaluation database unchanged. For scripted developer runs, create a disposable lab database from the same baseline for each comparison. Use the same model alias and mapping, history strategy, input questions, and initial marketplace state in each comparison. Record these settings with the results. Reset only the disposable lab between complete runs; never reset the fixed evaluation or interactive marketplace database.

For developer implementations, store full conversation history in PostgreSQL. Apply history-selection changes only to the input selected for the next model call. Preserve complete tool-call/result pairs and current investigation metadata.

## Part 1 — repeat the three demos

1. In a new conversation, prepare a fresh demo order with two units and a pending shipment. Ask: “What is the current shipment status for <your prepared order ID>? Cite the evidence.” Replace the placeholder with the actual order ID. Follow up with “How many units are in that order?” Inspect the next model input and show how the earlier question supplies the order reference.
2. In the same conversation, dispatch the prepared shipment through the marketplace. Ask: “What is the current shipment status of that order now? Cite current evidence.” Compare business revisions, fresh tool evidence, and the answer. History preserves the reference; fresh evidence establishes the current status. Refresh is instructed by the prompt, so verify it in the trace.
3. In another new conversation, introduce a distinctive fictional label. Add six unrelated question blocks without repeating the label in questions or answers. Ask for the original label. Verify that it remains in stored history but is absent from the selected six-block history and the actual next model input. Do not rely only on the final answer to prove exclusion.

Keep the questions, relevant trace/input excerpts, revisions, and a short explanation for each case locally for comparison with the solution. There is no submission destination. Redact credentials and provider reasoning items.

## Part 2 — optional developer challenges

### Developer extension 1 — change the window

Use the same seven-block history fixture for every strategy. These are the exact user messages:

1. “My fictional sample label is cedar-window-731.”
2. “What is 1 plus ten?”
3. “What is 2 plus ten?”
4. “What is 3 plus ten?”
5. “What is 4 plus ten?”
6. “What is 5 plus ten?”
7. “What is 6 plus ten?”

Then ask the same eighth question for each comparison: **“What fictional label did I give my sample at the beginning?”**

The reference runner supplies the first seven exchanges as a fixed fixture, including their known answers; it makes a real model call for the eighth question. It does not generate seven new answers for every strategy. Use a separate lab conversation restored to that identical fixture for each strategy so one comparison does not append extra turns to the next.

| Selection policy | Prior blocks supplied for the eighth question |
|---|---|
| Two-block window | Blocks 6–7 |
| Six-block window | Blocks 2–7 |
| Eight-block limit | All seven available blocks |

There are seven prior blocks, not eight to ten. An eight-block limit can include all seven. Inspect whether the label is in the actual model input before judging the answer; missing input and incorrect recall are separate observations.

Make the question-block window configurable in a lab implementation. Compare the same saved conversation with windows of two, six, and eight blocks. Verify which original details are included, input size, and complete tool-call/result pairs. Increasing the window should recover an early detail only if its block now falls inside the window. Restore the production default of six afterwards.

### Developer extension 2 — summary plus recent turns

This uses the same seven-block fixture and eighth recall question from extension one. Summarize blocks 1–5, and keep blocks 6–7 verbatim. The new input is the older-history summary plus the two recent complete blocks and the current recall question.

Why retain the last two blocks? A summary can lose exact wording, identifiers or tool evidence. Keeping recent blocks intact preserves the immediate exchange while testing whether a summary carries older context. Two is a chosen lab setting, not a universal rule. Summary-only is possible, but is a different comparison and is not required here.

Keeping stored history unchanged means creating the summary for model input without deleting or rewriting the full saved conversation. Treating it as historical data means it describes earlier exchanges, not new agent instructions or proof of current business status. Preserve the fictional label in the summary so the final question can be answered. In a business conversation, preserve order identifiers and evidence provenance too; current revision and clock must still govern freshness.

Replace the lab's pure sliding window with a summary of older turns plus two recent complete question blocks. Keep the full stored history unchanged. Label the summary as historical, untrusted conversation data, not instructions or current business evidence. Preserve identifiers and important user facts, and keep current revision, clock, and document metadata separate.

Use the same early-detail conversation as the window comparison. Compare retained details, input size, summary-generation usage, answer usage, and answers. Inspect omissions and unsupported additions in the summary. A smaller input is not evidence of better accuracy.

## What to check and record

For both extensions record the selected blocks or summary, whether the original label reaches the actual model input, the final answer, input characters/tokens, and usage. For compaction also record the summary-generation usage. Do not assume summaries save money or improve answers; the supplied short fixture can make the summary larger than the older text it replaces.

## Cleanup

Restore the six-block selection policy and remove only disposable lab conversations/data. Retain sanitized results and settings so another person can reproduce the experiment. The fixed evaluation database must remain unchanged.
