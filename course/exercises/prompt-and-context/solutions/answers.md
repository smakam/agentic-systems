# Prompt and Context — Worked Answers

## Prerequisites

Use the same Test workspace, GPT-5.4 configuration and fresh-conversation procedure described in the [exercise](../exercise.md). Keep memory and response caching off and preserve the business revision and demo clock across comparison runs.

## Your task

### Part 1: Inspect a complete context investigation

Question:

> For Cedar & Co., which payouts are currently held, why are they held, and what must happen before each can be released?

| Source | What you should find | How it supports the answer |
|---|---|---|
| Catalog | Entity meanings, row grain, units, metrics and relationships | Defines unpaid and supplies the fields/joins needed for the investigation. |
| Business records | Seller identity and current payout, delivery and return state | Establishes the held amounts and current blockers. |
| Retrieved policy | Applicable payout rules with source/version | Explains what must happen before release. |

In the verified reference snapshot, Cedar & Co. had one held payout of **₹2,249.10** for a Canvas Weekender. The item had not been dispatched or delivered, and no active return blocked it. Release required delivery confirmation, the 24-hour hold after delivery, and no active requested/approved/received return. Meeting those conditions does not release the payout automatically; the operator performs the payout. Use your current records and policy evidence if the state differs.

In **get_catalog → Preview**, identify entities, relationships, metrics, currency/money units, time guidance, cautions, catalog/ontology versions, validation and the catalog hash. Expand one entity, one relationship and the unpaid metric. Validation checks structural coverage; business meanings and cardinalities still require review. The relationship map does not imply a separate graph database.

**Stable configuration** includes the support role, tool descriptions/schemas and evidence/citation rules. **Dynamic input** includes each question, its current revision and demo clock, prior conversation messages and tool results. Catalog definitions arrive dynamically through a tool call even when their source is relatively stable. A result appears only after its tool returns; later model calls can use earlier evidence. Policy passages and current business records are separate sources from the catalog.

The verified investigation retrieved all three sources. The exact sequence can include seller resolution, multiple business queries or recovery attempts. Inspect actual calls and citations rather than expecting an identical fixed sequence.

### Part 2: Compare normal, suppressed and restored context

#### A. Policy retrieval

Question:

> What is the current returns policy?

| Condition | Reference observation |
|---|---|
| Normal | Retrieved policy passages and cited the 30-day return window and applicable return/refund rules. |
| Suppressed | Received no passages and declined to summarize the current policy without retrieved evidence. This does not mean the policy does not exist. |
| Restored | Retrieved passages and answered with policy evidence again. |

In the latest demonstrated suppressed run, the model made **two separate search requests**. The first covered the returns window and eligibility, requesting five passages. The second broadened the wording to refunds, damaged/wrong items and non-returnables, requesting eight. Both returned empty passages because suppression was enabled. This was a reformulated search, not an automatic retry of identical arguments. Find those differences in each call's **Preview → query** and **top_k**, rather than in the shared tool description under Attributes. Other runs may use different wording or call counts.

#### B. Catalog context

Question:

> For Cedar & Co., break down captured, refunded, fees, paid out, and unpaid amounts by product category in rupees.

| Condition | Reference observation |
|---|---|
| Normal | Retrieved catalog definitions/relationships, queried business records and completed the category breakdown. |
| Suppressed | Attempted several business queries with missing catalog data, then reached the model-turn limit without a complete conclusion in the demonstrated run. Some queries can still succeed. |
| Restored | Retrieved the catalog and completed a grounded breakdown again. |

At the recorded revision-2 reference snapshot:

| Product category | Captured | Refunded | Fees | Paid out | Unpaid |
|---|---:|---:|---:|---:|---:|
| Travel | ₹7,497.00 | ₹0.00 | ₹749.70 | ₹0.00 | ₹6,747.30 |

These amounts reconcile: captured equals refunded plus fees, paid out and unpaid. Unpaid includes held/failed funds and does not by itself mean ready for release. The category question tests catalog meanings and joins alongside current records; it does not ask the agent to determine release eligibility from policy.

Both suppression controls return successful empty-context responses: null catalog data or an empty passage list. Tool schemas, other business tools and some static SQL guidance remain available. The observed turn-limit stop is not a guaranteed outcome; a completed run must still be checked against its evidence.

Finish with both controls off. Your observations should show which source was removed, how tool use and the answer changed, and whether normal evidence returned after restoration. No business-data reset is needed.
