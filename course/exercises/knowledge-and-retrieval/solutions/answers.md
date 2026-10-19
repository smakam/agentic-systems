# Knowledge and Retrieval worked answers

## Prerequisites

Use the [exercise](../exercise.md) prerequisites and the same Test workspace UI. No learner terminal commands or file edits are required. The ordinary Support chat uses marketplace evidence; policy-version mode uses isolated policy documents with current Test order records; chunking uses synthetic documents and fixed facts. Preparing a missing suitable order can add labelled Test records. Neither policy switch executes payouts or rewrites existing records.

## Your task

### Part 1: Inspect retrieval and compare policy versions

#### Quick review: policy and business evidence

A policy-only answer should retrieve the conditions governing payout eligibility and cite the applicable passages. The order question should additionally retrieve current business evidence. Check whether delivery has happened, how much time has elapsed, whether a return blocks release and the recorded payout status. A policy rule or eligibility explanation is not proof that a payout was executed.

Use the actual indexed version, records and citations from your run. Local Langfuse shows ordinary Support investigations; select a tool’s **Preview** for invocation arguments and returned evidence.

#### Policy versions and order eligibility

Use **Prepare demo order** in the policy-version experiment. Read the returned ID and use **Use order question**. A suitable existing order is reused; otherwise a labelled Test order is created at delivery age 30 hours relative to the current demo clock. The application reads its payment, delivery, return and payout records for each answer. Fixed synthetic order facts are not supplied in this mode.

| Selected policy | Required wait | Expected explanation for the same suitable order |
|---|---:|---|
| V1 | 24 hours | Eligible: captured, delivered at least 24 hours ago, no active return |
| V2 | 48 hours | Not yet eligible: the same delivery is less than 48 hours old |

Inspect the actual order records, elapsed hours, source text and retrieved citations. Payout status remains held in both runs. The comparison changes the explanation under the selected lab policy, not the business action or operational payout rules. Keep the demo clock and records unchanged between runs; if they change, prepare a suitable order and repeat both versions.

Version changes prepare documents automatically. Unchanged content reuses cached embeddings; selecting an already prepared version, changing passage limits, asking another question or resetting unchanged settings does not require new document embeddings. Questions still use query embeddings and model calls. Turn the experiment Off afterward. To compare V1 again, select V1 in the policy version control.

Preparation can add a dedicated lab seller/product and a new Test order, affecting Test counts and aggregate totals. It does not alter existing orders, seller balances, inventory or the demo clock. Reset keeps the created records and conversation history. The [verified order-backed rehearsal](order-policy-results-2026-10-19.json) reused the same recorded order at delivery age 30 hours: V1 answered eligible and V2 answered not yet eligible, both citing the order records and retrieved policy. The recorded payout remained held. The saved older main-chat evidence documents the previous synthetic version experiment only; its chunking observations remain separately labelled below.

### Part 2: Compare chunking and the passage limit

Select **Chunking and passage limit**. The expanded synthetic policy separates two needed facts across adjacent paragraphs:

- The standard wait is **24 hours after confirmed delivery**.
- Amber Review adds **48 more hours to the standard wait**. The extension does not restate the standard value.

The fixed scenario includes Amber Review and delivery 30 hours ago. With both facts, the total is **72 hours**, so payout is not yet eligible. If only one fact is retrieved, the appropriate answer identifies the missing evidence rather than guessing the absent policy value.

Use the same steps and question as the exercise. Select **Paragraph**, wait for **Ready**, then ask in the main question box at top K 1 and 4. Select **Two-paragraph overlap**, wait for automatic preparation to finish, then ask at top K 1 and 4. Use a fresh conversation for each comparison. Changing top K alone needs no reindexing. Selected and indexed strategies must match when comparing chunkers.

The developer supplies both chunkers. Paragraph mode splits on blank lines and keeps source-line ranges. Overlap joins consecutive pairs of paragraphs at stride one, including a window containing the standard rule and extension together. A top-one window can therefore contain two paragraphs, even though only one chunk is returned.

#### How to interpret the comparison

| Setting | What to inspect | Interpretation |
|---|---|---|
| Paragraph, top K 1 | Does its single paragraph omit one of the two required rules? | A qualified or incomplete decision is appropriate when the missing value cannot be established |
| Paragraph, top K 4 | Are both separate rule paragraphs returned? | More passages can recover the missing fact, at the cost of extra context |
| Overlap, top K 1 | Does the winning window span both paragraphs? | One chunk can provide both facts and support the 72-hour calculation |
| Overlap, top K 4 | How much text repeats across windows? | More overlap/context may add no decision benefit after both facts are present |

In the earlier [verified main-chat rehearsal](main-chat-results-2026-10-19.json), paragraph/top-one returned only the standard rule and could not establish the extension or numeric total. Paragraph/top-four and both overlap settings retrieved both rules and calculated 72 hours. Retrieved characters were 212, 612, 480 and 1385 for paragraph/1, paragraph/4, overlap/1 and overlap/4 respectively. These are retained observations for the fixed demo question, not guaranteed outputs for every new run. The [new order-feature regression rehearsal](chunking-results-2026-10-19.json) reproduced the same passage-coverage pattern across all four settings.

This is a controlled teaching fixture, not proof that overlap always improves production retrieval. Ranking and model responses can vary; record actual passage coverage, citations, text volume and answer. A similarity score is not confidence, and a citation alone does not prove a supported conclusion. Character counts do not measure total API cost or latency.

Click **Restore paragraph baseline** and turn RAG experiments **Off** afterward. **Reset to defaults** also restores the existing demo baselines and normal workspace options; it keeps the current conversation, history, saved memories and business data. An existing conversation retains its runtime and memory-provider binding; choose New conversation yourself for a clean comparison. Keep your four observations locally; there is no submission and no business-data cleanup. The historical CLI and its saved results remain reference evidence for the earlier version of this lab, not commands learners must execute for the current UI workflow.
