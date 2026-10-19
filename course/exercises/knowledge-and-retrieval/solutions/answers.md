# Knowledge and Retrieval worked answers

## Prerequisites

Use the [exercise](../exercise.md) prerequisites and the same Test workspace UI. No learner terminal commands or file edits are required. The ordinary Support chat uses marketplace evidence; policy-version mode uses isolated policy documents with current Test order records; chunking asks policy-only questions about isolated lab documents, without fixed order facts. Preparing a missing suitable order can add labelled Test records. Neither policy switch executes payouts or rewrites existing records.

## Your task

### RAG calls and policy versions

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

Preparation can add a dedicated lab seller/product and a new Test order, affecting Test counts and aggregate totals. It does not alter existing orders, seller balances, inventory or the demo clock. Reset keeps the created records and conversation history.

### Chunking and passage-limit observations

Select **Chunking and passage limit**. The expanded synthetic policy separates two needed facts across adjacent paragraphs:

- The standard wait is **24 hours after confirmed delivery**.
- Amber products add **48 more hours to the standard wait**. The extension does not restate the standard value.

This is now a policy-only question: “What is the total payout waiting time for Amber products? Explain the standard wait and additional wait, with policy citations.” With both rules, the total is **72 hours**. Regular products use the standard **24-hour** wait. No order or fixed delivery scenario is supplied. If only one fact is retrieved, the appropriate answer identifies the missing evidence rather than guessing the absent policy value.

Use the same steps and question as the exercise. Select **Paragraph**, wait for **Ready**, then ask in the main question box at top K 1 and 4. Select **Two-paragraph overlap**, wait for automatic preparation to finish, then ask at top K 1 and 4. Use a fresh conversation for each comparison. Changing top K alone needs no reindexing. Selected and indexed strategies must match when comparing chunkers.

The developer supplies both chunkers. Paragraph mode splits on blank lines and keeps source-line ranges. Overlap joins consecutive pairs of paragraphs at stride one, including a window containing the standard rule and extension together. A top-one window can therefore contain two paragraphs, even though only one chunk is returned.

The instructor rehearsal returned only the additional 48-hour rule for paragraph/top-one and correctly declined to state a numeric total. Paragraph/top-four and both overlap settings retrieved both rules and answered 72 hours. No fixed scenario facts or order records were supplied.

#### How to interpret the comparison

| Setting | What to inspect | Interpretation |
|---|---|---|
| Paragraph, top K 1 | Does its single paragraph omit one of the two required rules? | A qualified or incomplete decision is appropriate when the missing value cannot be established |
| Paragraph, top K 4 | Are both separate rule paragraphs returned? | More passages can recover the missing fact, at the cost of extra context |
| Overlap, top K 1 | Does the winning window span both paragraphs? | One chunk can provide both facts and support the 72-hour calculation |
| Overlap, top K 4 | How much text repeats across windows? | More overlap/context may add no decision benefit after both facts are present |

This is a controlled teaching fixture, not proof that overlap always improves production retrieval. Ranking and model responses can vary; record actual passage coverage, citations, text volume and answer. A similarity score is not confidence, and a citation alone does not prove a supported conclusion. Character counts do not measure total API cost or latency.

Turn RAG experiments **Off** afterward. **Reset to defaults** also restores the existing demo baselines and normal workspace options; it keeps the current conversation, history, saved memories and business data. An existing conversation retains its runtime and memory-provider binding; choose New conversation yourself for a clean comparison. Keep your four observations locally; there is no submission and no business-data cleanup.
