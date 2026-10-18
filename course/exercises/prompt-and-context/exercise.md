# Prompt and Context — Exercise

## UI, database and cleanup

**UI:** [test marketplace](http://127.0.0.1:5179/) from Course Setup; use the role/workspace named in each task. **Database:** disposable practice database `market_test`, separate from main `market` and the fixed evaluation baseline `market_eval`. Test UI changes do not update the main marketplace. Save your questions, results and traces locally.

Use Support with OpenAI Agents SDK and a fresh conversation for each condition. Business questions are read-only; the context controls change returned tool data, not stored catalog, documents or business records.

**Cleanup:** restore both suppression controls to off and the original workspace options. No business database reset is required; saved conversations and traces remain.


## Your tasks

Repeat the questions and context comparison covered in the demo. There is no additional challenge and nothing to submit. Keep your observations locally and compare them with the reference solution.

## Before you start

Complete **Course Setup** and start the local stack. Open the [Test marketplace](http://127.0.0.1:5179/), sign in as support or operator, and open **Support workspace**. Use **Agent runtime → OpenAI Agents SDK**. Under **Gateway → Gateway model mapping**, verify **GPT-5.4 (default)**. Leave response caching and long-term memory off. Note the business revision and demo clock and keep them unchanged during comparisons.

Start a fresh conversation for every condition. **New conversation** resets experimental switches, so select the required suppression setting after starting the conversation and check it before asking. Changing a suppression switch also starts a fresh conversation with memory off.

## Part 1: Inspect a complete context investigation

Ask:

> For Cedar & Co., which payouts are currently held, why are they held, and what must happen before each can be released?

Let the agent choose its evidence sources. Open its Langfuse trace and inspect:

- **get_catalog → Preview:** collapse the JSON to its top-level branches, then expand one entity, the unpaid metric and one relationship. Identify currency and money units. Map the remaining sections too: metrics, time guidance, cautions, catalog/ontology versions, validation status/issues and catalog hash. Validation checks structural coverage; it does not prove the business definitions are correct.
- **query_business_data:** seller resolution and current payout, delivery and return records. Inspect the actual SQL and result grain.
- **search_documents:** returned policy passages, source/version and relevant payout conditions.
- **Later model calls:** how earlier tool calls and results become model context, and how final citations support the answer.

In the verified rehearsal the question retrieved all three sources. Tool order and call counts can vary. Record what your trace actually contains; if a source is absent, inspect whether the answer makes an unsupported claim.

Separate stable instructions/tool schemas from the dynamic question, clock/revision, conversation messages and tool results. The application supplies current revision and clock before the first model call for **each question**, including follow-ups. Catalog definitions arrive through the catalog tool, even when the source definitions are relatively stable. Schemas can be recorded separately from the messages array.

## Part 2: Compare normal, suppressed and restored context

Under **Context comparison**, change only one source at a time. Keep the question, model, instructions and business snapshot unchanged.

### A. Policy context

Ask:

> What is the current returns policy?

1. With both suppression controls off, inspect the retrieved passages and answer citations.
2. Enable only **Suppress policy retrieval**. Repeat the exact question in the resulting fresh conversation. Inspect the successful empty tool result and whether the answer declines to confirm unverified rules.
3. Clear both controls, start a fresh conversation and repeat to verify that policy passages return.

### B. Catalog definitions and relationships

Ask:

> For Cedar & Co., break down captured, refunded, fees, paid out, and unpaid amounts by product category in rupees. Explain what unpaid includes and reconcile the totals.

This requires business meanings, money units, item grain and joins from seller/items to product category.

1. With both controls off, inspect the catalog, SQL and reconciliation.
2. Enable only **Suppress catalog context** and repeat the exact question in the resulting fresh conversation. Inspect all queries, errors, recovery attempts and the final completion or stop.
3. Clear both controls, start a fresh conversation and repeat to confirm normal catalog context returns.

Both tools return success: catalog suppression returns null catalog data, while policy suppression returns an empty passage list. The results are marked context suppressed. No tool error or stop instruction is injected. Tool schemas, other business tools and some static SQL guidance remain available; this removes specific context sources rather than all information.

The model may still construct queries with an empty catalog. Do not require failure or a wrong answer. Inspect whether claims are grounded, what SQL was attempted and whether the run completed. No stored ontology, documents or business records change. Restore both suppression settings when finished.

## What to check and record

| Question or condition | Model call | Context item | Static configuration or dynamic input | Source | How it supports the answer |
|---|---|---|---|---|---|
| | | | | | |

Record missing context, actual tool calls, SQL, answer differences and citations. Report observed results without requiring removal to cause a wrong answer. For a fresh run, amounts and eligibility depend on current records and demo time.

See [the reference solution](solutions/answers.md).

Verified GPT-5.4 rehearsal: the normal catalog run completed after correcting one query error; the suppressed run made both successful and erroneous queries before reaching the eight-model-turn limit without a complete conclusion. With policy suppressed, the agent declined to state policy rules because it could not retrieve passages. Treat these as observations, not guaranteed outcomes.
