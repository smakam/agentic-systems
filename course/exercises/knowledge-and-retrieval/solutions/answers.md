# Knowledge and Retrieval worked answers

## Prerequisites

Use the [exercise](../exercise.md) prerequisites and the same Test workspace UI. No learner terminal commands or file edits are required. The ordinary Support chat uses marketplace evidence; questions inside **RAG → Open RAG experiments** use isolated synthetic documents and fixed facts. Neither experiment changes marketplace policies, order records, delivery times or payouts.

## Your task

### Part 1: Inspect retrieval and compare policy versions

#### Quick review: policy and business evidence

A policy-only answer should retrieve the conditions governing payout eligibility and cite the applicable passages. The order question should additionally retrieve current business evidence. Check whether delivery has happened, how much time has elapsed, whether a return blocks release and the recorded payout status. A policy rule or eligibility explanation is not proof that a payout was executed.

Use the actual indexed version, records and citations from your run. Local Langfuse shows ordinary Support investigations; select a tool’s **Preview** for invocation arguments and returned evidence.

#### Policy versions and reindexing

Use **RAG → Open RAG experiments → Policy versions and reindexing** and the question inside that panel. Click **Prepare V1 index** on first use or **Restore V1** before repeating the comparison. Keep the fixed facts and prefilled question unchanged.

| Stage | Selected source | Indexed policy | Expected evidence and answer |
|---|---|---|---|
| Initial V1 | V1: 24-hour wait | V1 | Payment captured, delivery 30 hours ago and no open return satisfy the simulated rule; eligible |
| Select V2 without indexing | V2: 48-hour wait | Still V1 | The preview changed, but retrieval still returns the 24-hour V1 rule; still eligible under that indexed evidence |
| Index selected settings | V2 | V2 | Retrieval returns the 48-hour rule; 30 hours is insufficient, so not yet eligible |

The state indicators and retrieved passage versions establish which evidence the answer used. The generator is not shown the unindexed V2 text when answering against V1. Each ask is independent of earlier answers and long-term memory, so a changed decision should follow the retrieved rule rather than conversation history.

Click **Restore V1** afterward. The implementation atomically replaces only its demo chunks after successful embedding; a failed indexing call should preserve the previous working index. Ordinary marketplace documents have their own **Index documents** control and are unaffected.

This demonstration replaces one small synthetic corpus; it is different from retaining immutable policy versions and selecting them by effective date. The marketplace’s returns-policy versions illustrate that separate capability.

### Part 2: Compare chunking and the passage limit

Select **Chunking and passage limit**. The expanded synthetic policy separates two needed facts across adjacent paragraphs:

- The standard wait is **24 hours after confirmed delivery**.
- Amber Review adds **48 more hours to the standard wait**. The extension does not restate the standard value.

The fixed scenario includes Amber Review and delivery 30 hours ago. With both facts, the total is **72 hours**, so payout is not yet eligible. If only one fact is retrieved, the appropriate answer identifies the missing evidence rather than guessing the absent policy value.

Use the same steps and question as the exercise. Select **Paragraph** and index it, then ask at top K 1 and 4. Select **Two-paragraph overlap**, index again, then ask at top K 1 and 4. Changing top K alone needs no reindexing. Selected and indexed strategies must match when comparing chunkers.

The developer supplies both chunkers. Paragraph mode splits on blank lines and keeps source-line ranges. Overlap joins consecutive pairs of paragraphs at stride one, including a window containing the standard rule and extension together. A top-one window can therefore contain two paragraphs, even though only one chunk is returned.

#### How to interpret the comparison

| Setting | What to inspect | Interpretation |
|---|---|---|
| Paragraph, top K 1 | Does its single paragraph omit one of the two required rules? | A qualified or incomplete decision is appropriate when the missing value cannot be established |
| Paragraph, top K 4 | Are both separate rule paragraphs returned? | More passages can recover the missing fact, at the cost of extra context |
| Overlap, top K 1 | Does the winning window span both paragraphs? | One chunk can provide both facts and support the 72-hour calculation |
| Overlap, top K 4 | How much text repeats across windows? | More overlap/context may add no decision benefit after both facts are present |

In the [verified UI-endpoint rehearsal](ui-results-2026-10-18.json), paragraph/top-one returned only the standard rule and could not establish the extension or numeric total. Paragraph/top-four and both overlap settings retrieved both rules and calculated 72 hours. Retrieved characters were 212, 612, 480 and 1385 for paragraph/1, paragraph/4, overlap/1 and overlap/4 respectively. These are retained observations for the fixed demo question, not guaranteed outputs for every new run.

This is a controlled teaching fixture, not proof that overlap always improves production retrieval. Ranking and model responses can vary; record actual passage coverage, citations, text volume and answer. A similarity score is not confidence, and a citation alone does not prove a supported conclusion. Character counts do not measure total API cost or latency.

Click **Restore paragraph baseline** afterward. Keep your four observations locally; there is no submission and no business-data cleanup. The historical CLI and its saved results remain reference evidence for the earlier version of this lab, not commands learners must execute for the current UI workflow.
