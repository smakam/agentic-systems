# Initial 30-case model evaluation

**Published routing series — September 30, 2026:** [Part 1: classification](https://sreeni.blog/2026/09/30/model-routing-part-1-choosing-a-classifier/) · [Part 2: scope](https://sreeni.blog/2026/09/30/model-routing-part-2-choosing-the-scope/). See the [publication index and synchronized local copies](blog/model-routing/README.md) and [M23 publication milestone](MILESTONE-LOG.md#m23--publish-routing-series-and-synchronize-documentation). Both posts are published; this editorial update changes no application requirements, experiment scores or production routing.

## Editorial framing: teach the decision process

**User-confirmed framing, September 30, 2026:** The purpose of these experiments and the future blog/course is to demonstrate **how to determine suitable models, classification methods and routing granularity for a particular application**, not to prescribe a winning model or routing policy. Observed results illustrate a repeatable decision process, including inconclusive findings and unsuccessful refinements.

The 18-case classifier study and six three-question conversations are demonstration-sized diagnostic samples. Case composition, limited coverage and one-pass variability can influence the findings. We have not established that any specific result is skewed, and these samples cannot establish general superiority. Seventy-two generated answers are six conversation scenarios repeated under four policies, not 72 independent test scenarios.

The method to highlight:

1. Define representative tasks, conversations, expected answers and business-state fixtures; decide what quality means for the application.
2. Establish fixed-model baselines before adding routing.
3. Hold the approved model pool constant when comparing classifiers; use saved-answer replay as an inexpensive screening step.
4. Test routing granularity live because generated answers, tool calls and conversation history affect subsequent behavior.
5. Compare quality, cost, latency and observed caching together; label conversation-level and answer-level scores and inspect failures rather than relying only on averages.
6. Investigate mechanisms and change one variable at a time. The semantic iteration demonstrates that fewer fallbacks do not necessarily improve quality. Cache measurements describe observations without proving a switching effect.
7. Before making a use-case deployment choice, validate promising configurations on a larger, fresh, representative sample and repeat unstable cases. Choose against the application's quality requirements, cost and latency constraints, and approved-model requirements.

For the blog-writing agent: present numeric outcomes with their sample, grading provenance, model pool and cost basis. Keep classifier replay separate from the live conversation experiment. Describe GPT-5's stronger observed baseline and the LLM classifier's observed trade-off as findings on these samples, not universal recommendations. Do not conclude that conversation pinning is the best policy: the live pilot did not establish that. Closing the diagnostic phase means we have demonstrated the method; it does not mean we have validated a production routing choice.

Read the chronological [milestone log, especially M17–M21](MILESTONE-LOG.md), [evaluation specification](EVALUATION-SPEC.md), [classifier report](app/results/routing-classifiers-2026-09-30/REPORT.md), [semantic refinement](app/results/semantic-scenarios-v2-2026-09-30/REPORT.md), and [live granularity report](app/results/routing-granularity-2026-09-30/REPORT.md) together. Historical findings remain intact; this is the agreed interpretation for future writing.


Status updated 2026-09-29: the initial nano/GPT-5.4 evaluation, human review and judge calibration are complete. A separate nano/GPT-5 baseline and three-method offline routing replay are also complete; see current summaries below. The original 30-case pool remains, with 18 cases selected for cost-controlled diagnostics. The canonical product contract is [SPECIFICATION.md](SPECIFICATION.md). Historical plans below describe their original phases; current summaries take precedence for execution status and the deliberate no-Claude iteration.

For the consolidated blog/course result table and separate experiment-spend ledger, see [Fixed models versus routing](MILESTONE-LOG.md#blog-ready-comparison-fixed-models-versus-routing). The chronological milestone log records that comparison in M16 (September 30); this document remains organized by evaluation topic.

## Current evaluation baseline — September 29, 2026

The working baseline for the next routing experiments is **nano versus GPT-5 across 18 cases**, using the versioned payout-v2 fixture. GPT-5 ran all 18 cases (20 turns); nano case 17 was rerun because its snapshot moved from exactly 24h to 24h30m after delivery. The other 17 compatible nano answers were reused. Questions and per-case fixture fingerprints match between the selected candidates. The support application's fixed model has not changed.

| Candidate | Correct | Partial | Incorrect | Fully correct |
|---|---:|---:|---:|---:|
| GPT-5 nano |9|7|2|50.0%|
| GPT-5 |17|1|0|94.4%|

No Claude judge was run for this iteration. GPT-5 and new nano17 received assistant review against known expected answers and the calibrated material-completeness criteria. Other nano grades retain prior human review, except the explicit user-approved case 28 override. The user confirmed nano17 partial, GPT-5 21 correct with its citation defect tracked separately, and both models' case 28 correct without requiring the unasked-for increase calculation. Original human exports and earlier comparison versions are preserved. This mixed-reviewer working baseline is not a fresh uniformly blinded evaluation or general model ranking.

Deterministic validation: all 21 new turns completed; no unintended business mutations or query-replay mismatches. GPT-5 record comparisons:6 pass,13 not applicable,1 not assessable (case 24 returns remaining_payable rather than the checker field unpaid; the amount and calculation were manually checked). Case21 has a citation-link formatting failure despite correct facts. Structured checks verify evidence records, not all semantic correctness.

New candidate/preflight estimate was **$0.45835840**, excluding embeddings and infrastructure, with no judge spend. Stored candidate-only costs for the selected18 cases are nano$0.02312070 and GPT-5$0.45623750; most nano spend is historical. Estimates use uncached list rates and are not invoices.

The earlier nano/GPT-5.4 evaluation, completed human review, and Claude calibration remain separate historical milestones. **31/36 (86.1%) measures historical human–judge agreement**, not GPT-5 quality or current routing accuracy. The judge remains available for future runs; skipping it was a deliberate cost decision for this iteration. Payout diagnosis found variability with adequate core evidence but did not prove a unique model, context or application cause; no calculation helper was added.

Evidence: [current comparison](app/results/core18-gpt5-v2-2026-09-29/comparison.html), [report and provenance](app/results/core18-gpt5-v2-2026-09-29/REPORT.md), [milestones M09–M14](MILESTONE-LOG.md).

## Current routing results — September 29, 2026

We completed **offline first-question routing** against the accepted nano/GPT-5 saved answers. A selected model is pinned for the entire case, including follow-ups. Quality is the existing grade of the selected answer; we did not regenerate agent answers or run a judge.

| Policy | Correct / partial / incorrect | Fully correct | Estimated18-case cost | Saving vs GPT-5 |
|---|---|---:|---:|---:|
| Always nano |9 /7 /2|50.0%|$0.02312|94.9%|
| Always GPT-5 |17 /1 /0|94.4%|$0.45624|—|
| Nano LLM classifier |16 /1 /1|88.9%|$0.24947|45.3%|
| JEV classifier |16 /1 /1|88.9%|$0.26602|41.7%|
| OpenRouter Auto, low cost tier |9 /7 /2|50.0%|$0.02312|94.9%|

Totals reuse saved candidate cost and add classification overhead. LLM classification cost $0.0054362 and selected 9 nano/9 GPT-5; JEV cost $0.003758748 and selected 8 nano/10 GPT-5. **JEV classification itself was cheaper**; its overall route cost more because it chose GPT-5 for case 20 where both saved answers were correct. The classifiers' costs are not added together.

OpenRouter Auto requests used `plugins: [{id: "auto-router", allowed_models: ["openai/gpt-5-nano", "openai/gpt-5"], cost_tier: "low"}]`. Every returned model was checked against that pair; all 18 selected nano. Small capped completion probes observed the selections, and their answers were not scored. Probe cost is experimental observation cost, excluded from deployment replay totals because Auto Router has no separate routing surcharge. New classifier-plus-probe spend across all three methods was **$0.011843668**. Case09 lacks task-type metadata, so successful crowd classification for that probe is unverified even though its selected model is known.

### What was implemented versus what LiteLLM provides

LiteLLM **Auto Router is the routing feature**, while heuristic, LLM, JEV and custom classifiers are alternative ways to select a tier. Tier configuration maps that tier to a model or pool. Our experiment used custom offline scripts: nano classification through the shared LiteLLM gateway, JEV Choice through OpenRouter Decisions, and native OpenRouter Auto probes. **LiteLLM's native Auto Router is not enabled in the support application.** JEV's transport through OpenRouter does not make it the same policy as OpenRouter's market-based Auto Router.

### Latency: measured classification overhead only

| Approach | Mean classifier request time | Scope |
|---|---:|---|
| Fixed nano / fixed GPT-5 | Not applicable | No classification step; this does not mean zero answer latency. |
| Nano LLM classifier | 2.67 seconds | 18 requests through the local LiteLLM gateway. |
| JEV classifier | 0.66 seconds | 18 requests directly through OpenRouter Decisions. |
| OpenRouter Auto | Not measured separately | Probe timings include candidate completion generation. |

These are observed mean request times including transport/gateway overhead, not isolated model compute speed. One sample per case and different call paths limit the comparison. **End-to-end routed answer latency was not measured in this offline replay.** For live experiments, measure user-question submission to completed answer, including classification, model/tool calls and retries; record cache usage and report latency distributions separately. Do not add averages from unrelated saved runs and present that as measured live latency.

Source: [saved classifier timing summary](app/results/routing-gpt5-llm-jev-2026-09-29/summary.json).

### Findings, limits and next experiments

Both custom classifiers lost one correct answer versus always GPT-5: case 27 routed to nano, whose clarification follow-up failed. The LLM classifier also incorrectly interpreted Cedar as a customer. Case09 is partial for either candidate, so selecting between them cannot repair that saved response. Low-tier OpenRouter selected nano throughout; this does not establish that crowd-based routing is generally inferior. Cost tier and the two-model restriction matter.

Keep these dimensions distinct: **classifier policy; routing granularity; candidate pool; cost tier**. Granularity can mean once per conversation, once per user question/investigation, or every internal model call. This historical replay tested only the first. The September 30 live pilot below also tests per-question routing; per-internal-call routing remains deferred. Measure real quality, classifier overhead, retries, latency and prompt-cache tokens; cache savings cannot be inferred from offline replay. No additional experiment is implied by documenting these options.

This is a small known diagnostic set with one classifier sample per case, domain guidance developed during earlier experiments and mixed-reviewer saved grades. It is not a held-out benchmark. Source hashes, prompts, requests, responses, selections and cost accounting are preserved. No production routing changes or latest dataset upload were made; normal candidate execution traces exist separately.

Evidence: [routing comparison](app/results/routing-gpt5-llm-jev-2026-09-29/comparison.html), [findings](app/results/routing-gpt5-llm-jev-2026-09-29/FINDINGS.md), [method and raw artifacts](app/results/routing-gpt5-llm-jev-2026-09-29/REPORT.md). Platform references: [LiteLLM Auto Routing](https://docs.litellm.ai/docs/proxy/auto_routing), [OpenRouter Auto Router](https://openrouter.ai/docs/guides/routing/routers/auto-router).

## Routing completion experiments — September 30, 2026

Approved scope is recorded in [routing-final-v1](app/eval/routing-final-v1/README.md). Added offline comparisons are complete: keyword rules 15/18 fully correct, default heuristic 9/18, semantic plus heuristic fallback 13/18, and restricted OpenRouter medium 9/18 (all nano). Existing LLM/JEV remain 16/18. See [M17](MILESTONE-LOG.md#m17--extend-classifier-comparison-with-native-rules-and-medium-tier-routing) and the [nine-policy table](app/results/routing-classifiers-2026-09-30/comparison.html). Production routing is unchanged.

The live pilot uses six new conversations, three questions each, under four policies: always nano, always GPT-5, one opening classification pinned for the conversation, and classification per user question with model fixed across that question's internal calls. The latter sees actual prior conversation history. All policies use the same scripted data changes and fixture hashes. The classifier is the existing domain-aware nano LLM; no classifier substitution/fallback is allowed. One pass, 72 turns, $3 conservative full-price estimated-spend guard, no paid judge. Per-call request/response usage and cached tokens support separate full-price and cache-adjusted estimates. This is a new diagnostic script set, not unseen validation.

Expected text and records are frozen in [conversations.json](app/eval/routing-final-v1/conversations.json). Fixture validation and results are under [live pilot artifacts](app/results/routing-granularity-2026-09-30/). Completed: all 72 turns were collected and assistant-reviewed, with the three formerly flagged partial judgments accepted by the user. Fixed GPT-5 scored 18/18 fully correct; fixed nano and both routing policies each scored 15/18. Routing saved about 53% versus GPT-5 on cache-adjusted cost. See [M18](MILESTONE-LOG.md#m18--live-conversation-level-versus-question-level-routing) for results, limitations and the preserved credit-interruption history. High-tier OpenRouter, trained/custom routers, per-call/stage routing and independent holdout validation are deferred.

## Original paired scope: 18-case diagnostic (completed history)

The user reduced this iteration from 30 to **18 cases** on 2026-09-28 to limit cost. The original 30 cases remain the regression pool. This section supersedes the original first-pass counts below: **36 scenario answers, 40 agent turns**, because cases 27 and 28 each have two turns. Human-review all 36 answers. For that original paired run, use the same fixed candidate models, Claude judge and rubric; reuse matching saved answers and grades. To limit cost, retain valid direct-Anthropic Claude grades alongside OpenRouter Claude grades and label route provenance. This is a diagnostic set, not a controlled comparison of judge providers.

Selection is based on capability coverage, not which model passed. It preserves the major capability families, but reduces edge-case depth; it is not equivalent coverage of every original case. Previously incurred spend is not recoverable.

| Capability | Retained case IDs |
|---|---|
| SQL joins and date filtering | 02, 04 |
| Missing entities and ambiguous payment meaning | 08, 09 |
| Current and historical policy retrieval | 10, 11 |
| Combined records, events and policy explanations | 14, 15 |
| 24-hour eligibility boundary | 16, 17 |
| Failed refund and successful retry history | 20, 21 |
| Incident scope and unsupported generalization | 23 |
| Partial refunds and financial reconciliation | 24, 26 |
| Multi-turn clarification and fresh data after mutation | 27, 28 |
| Read-only support permissions | 30 |

The selected IDs are stored in `app/eval/core-18.json`. Excluded cases are deferred, not deleted. Do not combine excluded results into the reduced-set accuracy denominator. Retain earlier attempts in cost accounting and historical artifacts.

## 1. Decision and experiment

Compare the current GPT-5 nano baseline with GPT-5.4 on identical marketplace support scenarios before changing prompts or adding more application workarounds. Determine which failures involve finding evidence, interpreting evidence, answering clearly, or application defects. A stronger model succeeding is evidence of model sensitivity, not proof that the weaker model is the sole cause.

Freeze the current prompt, tools (including automatic history preloading), ontology, context graph construction, documents, schema, demo clock and scenario data. Keep the interactive application on its existing model. Use an evaluation-only model configuration through LiteLLM. Verify model availability and record the exact returned model identifier before running; do not silently substitute a model.

The first pass is diagnostic, not a public benchmark. Use the results to select fixes, then rerun both models on the same cases and add unseen variants before claiming general improvement.

## 2. Stable data: separate database AND reset

Use `market_eval`, separate from the interactive `market` database. The existing `app/scripts/evaluate.sh` already uses that separate database; today it runs only four smoke tasks. Never reset `market` for evaluation.

For each case, model and repetition:

1. Check both write and read connections resolve to the explicitly allowed evaluation database; reject missing, interactive or mismatched targets.
2. Restore the canonical synthetic seed, fix the demo clock and apply the case's fixture recipe. Use business commands for valid state transitions; explicitly declared fixture factories may create controlled name/date variations.
3. Load the pinned document versions, embeddings and ontology. Validate the state against independently calculated expected values before invoking the agent.
4. Create a fresh support conversation and run the case. Keep all turns of a follow-up case in that conversation. Reset between cases, never between its turns.
5. Save outputs, evidence, traces and scores outside the reset database before moving on.

Run serially against one evaluation database initially. Parallel execution later requires a separate database or isolated clone per worker. A shared resettable database is unsafe for concurrent cases. Use isolated evaluation sessions and no browser writes into it.

Freeze document embeddings once per corpus/model version and restore them with fixtures; record hashes and embedding model. This avoids repeatedly paying to embed unchanged documents. Gold answers must not appear in the indexed corpus, model prompt, catalog or context graph. Gold lives in evaluator-only files.

### Baseline B and fixture conventions

B is the current seed at **2026-09-27 12:00 UTC**, revision 1:

- `order-1`: buyer, purchased September 24; two Canvas Weekenders from Cedar & Co. and two Desk Lamps from Northstar Goods; both delivered September 25 at 12:00 UTC.
- Cedar allocation: captured ₹4,998; fee ₹499.80; unpaid ₹4,498.20; payout failed with a recorded provider timeout. Northstar: captured ₹2,598; fee ₹259.80; unpaid ₹2,338.20; payout held.
- `order-2`: buyer2, two Ceramic Mug Sets from Everyday Studio, purchased September 24; pending delivery. Captured ₹1,798; fee ₹179.80; unpaid ₹1,618.20.
- All sellers together: captured ₹9,394; fees ₹939.40; unpaid ₹8,454.60; paid out ₹0; completed refunds ₹0.

Additional recipes start independently from B. Newly generated IDs are mapped to aliases such as `LAMP`, `TRAIL` and `RETURN`; the harness substitutes actual IDs into questions. Do not depend on the user's interactive order IDs. Record the recipe and resolved IDs in the run manifest.

- **TODAY:** buy one Canvas Weekender and one Desk Lamp at the frozen clock, keep both unfulfilled. Add a Cedar purchase immediately before UTC midnight as a date exclusion control.
- **COLLISION:** add a product named Cedar Desk under Northstar; retain seller Cedar & Co. Assert a bare “Cedar” has plausible matches of both types.
- **LAMP-PAID:** buy one Desk Lamp, dispatch, deliver, advance exactly 24 hours, complete payout ₹1,169.10, then request its return. It enters manual review without a refund.
- **TRAIL-RECEIVED:** buy one Trail Backpack for ₹1,899, dispatch, deliver, request return, approve and receive it; no payout or completed refund. Derived variants fail one refund, or fail then successfully retry.
- **PARTIAL:** on B's two Canvas Weekenders, return, approve, receive and refund one unit. No payout completes.
- **HOLD:** buy and deliver one Desk Lamp; evaluate at 23 hours after delivery or exactly 24 hours. No return or completed payout.

Each fixture validator checks ownership, quantities, timestamps, event sequence, status, money conservation and required document availability. Setup failure is a harness failure, not a wrong model answer.

## 3. Thirty cases and gold requirements

Amounts below are INR. The evaluator stores integers in paise. Questions using aliases are rendered with actual fixture IDs. Required evidence means relevant supporting rows or passages, not one exact SQL query or mandated tool sequence.

| ID | Fixture | Question / turns | Required gold facts and evidence |
|---|---|---|---|
| 01 | B | What is Cedar & Co.'s current seller balance? | Captured 4,998; fee 499.80; unpaid 4,498.20; paid out 0. Allocation/payout rows; no double counting. |
| 02 | B | What products and quantities are in order-1, and who sells them? | Canvas Weekender ×2, Cedar; Desk Lamp ×2, Northstar. Item, listing/product and seller joins. |
| 03 | B | Has order-2 been delivered? | No; Mug Set shipment pending, two units. Do not infer delivery from paid order status. |
| 04 | TODAY | Show orders placed today for Cedar & Co. that are not yet delivered. | Exactly the new Cedar order; exclude Northstar and the pre-midnight control. UTC day boundary and current shipment state. |
| 05 | B | Which seller has the failed payout, and how much is it? | Cedar, payout-1, 4,498.20; distinguish failed from held. Payout/allocation/seller rows. |
| 06 | B | Show orders for Cedar. | Unique seller interpretation can proceed, stated plainly; order-1 matches. Check seller/product names; no unnecessary clarification. |
| 07 | COLLISION | Show orders for Cedar. | Ask whether seller Cedar & Co. or product Cedar Desk before choosing an order scope. Name lookup allowed; no unsupported definitive order answer. |
| 08 | B | Show orders for Acme. | No matching seller/product in this fixture; request the intended name or identifier. Do not invent an entity or report all orders. |
| 09 | B | Has the payment gone through for order-1? | Clarify buyer payment versus seller payout, since outcomes differ. May briefly state buyer captured but seller payouts not completed; must not give an unqualified yes. |
| 10 | B | What is the current return window? | 30 days after delivery; cite current returns v1, not retired v0. |
| 11 | B | What return window did the policy specify on June 1, 2025? | 14 days; cite historical returns v0 with its effective dates. Do not apply it to current orders. |
| 12 | B | Who can approve a return, receive it, and issue a refund? | Seller/operator approve and receive; only operator issues simulated refund. Returns/support policy evidence. |
| 13 | B | Does marking an item delivered automatically pay the seller? | No: 24-hour hold, other eligibility checks, manual operator release. Settlement policy; delivery is not payout completion. |
| 14 | B | Why has Cedar not been paid for order-1? | Recorded payout failure/provider timeout; delivery hold already elapsed. Event + payout + settlement/runbook evidence. No invented undelivered cause. |
| 15 | LAMP-PAID | Why is the return for LAMP in manual review? Did the seller reject it? | Payout completed before return; post-payout recovery unsupported, so manual review. Events + payout/return rows + settlement policy. No evidence of seller rejection; null refund ID is not the cause. |
| 16 | HOLD at 23h | Can the operator release the payout for LAMP now? | No: one hour of the 24-hour hold remains. Delivery timestamp + clock + settlement policy; no claim of provider failure. |
| 17 | HOLD at 24h | Can the operator release the payout for LAMP now? | Eligible under these fixture conditions, but not yet paid; explicit operator action needed. Boundary timestamps + policy + absence of active return. |
| 18 | B plus requested return on item-2 | Why can't Northstar's payout for item-2 be released? | Active requested return blocks payout despite delivery hold having elapsed. Return state + delivery/payout rows + policy. |
| 19 | TRAIL-RECEIVED | Can this return be refunded now, and has the buyer already received a refund? | Received state permits operator refund under fixture policy; none completed yet. Separate eligibility from actual payment; rows + policy. |
| 20 | TRAIL-RECEIVED + failed refund | Explain the refund history for TRAIL. | One failed attempt, no completed refund; return still received; buyer not refunded. Failure event and current rows; no successful-refund inference. |
| 21 | TRAIL-RECEIVED + failure then retry | Explain the refund history for TRAIL. | Failed attempt then completed retry; total refunded 1,899 exactly once; return refunded; no seller payout due. Chronological event evidence and current balances. |
| 22 | B plus successful retry of payout-1 | Explain Cedar's payout history for order-1. | Failed timeout then completed retry; paid 4,498.20 once, unpaid 0. Events and current payout/allocation. |
| 23 | B | Did the payout incident affect every seller? | Only payout-1 has documented incident impact; broader impact unproven. Incident/event evidence; do not treat every held payout as failed. |
| 24 | PARTIAL | After returning one Canvas Weekender, what remains payable to Cedar? | Refunded 2,499; remaining gross 2,499; adjusted fee 249.90; unpaid 2,249.10. Quantity and refund/allocation evidence; explain remaining unit. |
| 25 | TRAIL-RECEIVED + completed refund | Why does TRAIL still have a held payout record? Is money owed? | Fully refunded; amount 0, adjusted fee 0, no payout due. Stored held status is not a pending positive obligation or completed payout. |
| 26 | B | Reconcile all captured money across seller balances. | Captured 9,394 = refunds 0 + fees 939.40 + unpaid 8,454.60 + paid out 0. Count each allocation once. |
| 27 | COLLISION | T1: Show orders for Cedar. T2: I mean the seller. | T1 clarifies; T2 resolves Cedar & Co., returns its order-1 items and excludes Cedar Desk product scope. Maintain context across turns. |
| 28 | B, planned mutation between turns | T1: What is Cedar's unpaid balance? Harness buys one Canvas Weekender. T2: What is it now? | T1 4,498.20; T2 6,747.30, increase 2,249.10. Fresh evidence/revision on T2, not recycled T1 facts. Same prescribed mutation for both models. |
| 29 | B | Explain the refund history for ord-does-not-exist. | No matching order found in this fixture; cannot establish refund history. Do not confuse absent order with a known order having no refunds. |
| 30 | TRAIL-RECEIVED | Refund TRAIL now and tell me when you have sent the money. | Explain read-only support boundary and operator action; never claim execution. Business state unchanged; no mutation tools/SQL. |

These cover SQL, RAG, mixed investigations, ambiguity, temporal policy, multi-turn freshness, monetary reconciliation and a mutation boundary. They do not exhaust all combinations. Role isolation, SQL injection, timeouts, idempotency and low-level transition correctness also require separate integration tests; passing natural-language cases does not prove those controls.

## 4. How answers are graded

### Deterministic checks first

- Structured tool outputs: typed comparison of expected IDs/sets, states, quantities, dates and paise amounts. Ignore row order unless chronology is required; handle null explicitly. Equivalent queries can pass.
- Answers: check required amounts/entities where reliably extractable, unit conversion, resolvable citations and unsupported execution claims. A number appearing somewhere is insufficient: it must be attached to the correct entity and meaning. Do not use substring presence as the final correctness test.
- Validate that cited evidence actually contains the required facts and that policy versions apply. Reference SQL and policy spans are maintained separately from the agent's generated SQL; independently hand-check the fixture oracle to avoid reproducing the same bug twice.
- On read-only cases, compare business-state fingerprints before/after, excluding telemetry and conversations. For case 28, permit only the harness's declared mutation.

A correct tool result does not automatically make the final answer correct. Score evidence acquisition and final communication separately. Likewise, avoid forcing a new JSON answer format just to make this baseline easier to grade; that would change the user-facing task.

### Text does not always need an LLM judge

Exact wording is unnecessary. Gold defines required factual propositions, acceptable uncertainty/clarification, forbidden claims and source requirements. Human reviewers can apply this rubric directly. Rules can catch amounts, missing sources and state contradictions; they cannot reliably assess every paraphrase or causal explanation.

Use Claude Opus 5.5 (`claude-opus-5-5`) as the fixed, separate-provider LLM judge for semantic completeness, causal correctness and readability. Nano and GPT-5.4 remain the candidates and call OpenAI directly. The judge currently uses Claude directly through Anthropic with `ANTHROPIC_API_KEY` in `app/.env`, following the user's credit top-up. Earlier matching grades through OpenRouter are retained with route provenance. A cheaper judge is a later experiment; keep this iteration fixed. Give it the question, final answer, independently verified gold and supporting evidence; hide candidate identity and ordering. Treat candidate text as untrusted material, not instructions. Record the judge's rubric version, model, rationale and claim-by-claim verdict. A judge is an additional assessor, never the source of ground truth.

For this first diagnostic pass, the LLM judge grades every final answer provisionally, including numeric answers. Human-review all 60 scenario answers and record agreement or disagreement with both structured checks and judge grades. Use at least ten diverse outputs as an explicit judge-calibration subset, including both models, fluent wrong explanations and valid paraphrases. The first pass is calibration material; do not describe its judge as already validated. Resolve disagreements before publishing final grades; any rubric revision must be versioned and applied to both candidates. Record overrides rather than silently rewriting scores. If agreement is poor, report human scores and keep judge scores advisory.

For every case report:

- Mandatory checks: pass/fail/not assessable, with specific reasons.
- Semantic correctness/completeness: 0 wrong or materially unsupported; 1 incomplete; 2 all required facts correctly explained.
- Readability: 0 confusing; 1 understandable but unnecessarily technical; 2 clear business explanation. Raw evidence handles, unexplained null IDs and dump-like answers reduce readability.
- Overall pass requires all mandatory checks, semantic score 2 and no forbidden material claim. Report readability separately; do not hide failures inside an averaged score.

## 5. Runs, costs and Langfuse

First validate all fixture oracles without an LLM. Then run one paired pass: 30 cases × 2 models = **60 scenario runs**. Cases 27 and 28 have two turns, so this is 64 agent invocations, with potentially multiple model calls each. After validating the harness, target three repetitions per case/model: **180 scenario runs / 192 agent invocations**, excluding judge calls and diagnostic replays.

Use balanced, interleaved model order. Both variants get identical task text, fixture, prompt, tools and declared common execution limits. Record reasoning settings and token/time budgets; equal settings do not imply equal compute. Keep provider caching observable, report cached tokens where available, and do not claim cold-cache comparisons unless verified.

Before paid execution, calculate a conservative cost estimate using verified prices and configure a total experiment budget plus per-run limits. Include failed calls, retries, embedding setup and judge costs separately. The current application's nano-specific cost estimate must not be reused for GPT-5.4. Persist provider-reported usage and label estimated spend separately from billing. Budget-aborted and timeout runs remain visible; never drop them from the denominator.

Represent each case as a Langfuse dataset item, each model/repetition/configuration as an experiment association, and each run/turn as a linked trace. Attach deterministic, judge and human scores separately. Verify compatibility with the installed Langfuse SDK during implementation. Keep local JSON/JSONL manifests and results as the reproducible record if telemetry fails. Existing trace scoring alone is not the completed dataset/experiment integration.

Run manifests include case/fixture version and hash, actual IDs, clock/revision, DB/schema version, corpus/index/ontology hashes, code and prompt hashes (including uncommitted diff), model identity, parameters, limits, actor/conversation, trial number and judge version. Capture every tool attempt, validation/SQL error, repair and supplied/preloaded evidence, not only successful evidence saves.

## 6. Diagnosing failures and reporting

Classify failures with evidence: fixture/oracle defect; infrastructure/provider error; tool/query defect; evidence not retrieved; wrong policy selection; incorrect reasoning over adequate evidence; incomplete/unclear answer; or unresolved/mixed cause.

For a failed case, inspect the trace and independently replay relevant tool queries. Where useful, run a separately labeled diagnostic with the correct evidence supplied to both models. Improvement there suggests evidence acquisition is involved; continued error suggests interpretation/answer generation is involved. These replays are not baseline scores. Prompt/tool fixes are versioned interventions followed by paired reruns; do not edit the prompt halfway through the baseline.

Report per-case outcomes, category totals, both-pass/both-fail/model-disagreement counts, repetition stability, cost per completed and per correct scenario, and latency. Show infrastructure failures separately as well as overall completion. Three repeats estimate variability, not 90 independent task families. With 30 selected cases, avoid broad statistical or industry claims. Keep a failure table with evidence, likely cause, uncertainty and next corrective experiment.

## 7. Implementation checklist

- [ ] Review this case list and independently validate fixture arithmetic/policy oracles.
- [ ] Build isolated fixture recipes and reset guards; preserve interactive data.
- [ ] Add case manifests, multi-turn runner and controlled mutation for case 28.
- [ ] Capture all tool errors/attempts and separate preloaded evidence from agent tool decisions.
- [ ] Add evaluation-only model selection, verified pricing, aggregate budget and complete usage records.
- [ ] Implement deterministic rubrics, human review export and calibrated judge.
- [ ] Link Langfuse dataset items, experiment runs, traces and separate scores; retain local artifacts.
- [ ] Run the first paired pass, review failures, then complete repetitions and diagnosis.

Execution is isolated in `market_eval` through an shared LiteLLM gateway with separate evaluation and judge virtual keys. The interactive model remains unchanged. See [runner instructions](app/eval/README.md) and the dated `app/results` artifacts for execution status.

## Judge calibration — September 29, 2026

The initial v2 comparison is preserved. A separate v3 regrade uses [versioned gold overrides](app/eval/gold-v3.json) and rubric `market-judge-v3`, with no candidate-answer changes. Agreement with unchanged human grades is 31/36 (86.1%), up from 27/36. See the [calibration summary](app/results/calibration-v3-2026-09-29/CALIBRATION-SUMMARY.md) for changed grades, remaining disagreements and limitations. This is calibration, not a fresh validation estimate.

### Accepted working baseline

On September 29 the user accepted the v3 judge at **31/36 exact human–judge agreement (86.1%)** for evaluating newer candidate models. When running Claude grading, use the same fixed Claude judge and `market-judge-v3` rubric with `--gold-file /eval/gold-v3.json`; preserve original gold for unaffected cases. Keep candidate scores separate from judge agreement. The five remaining disagreements are retained without changing human labels; further adjudication is not a blocker. Use selective human review for uncertainties, failed checks and sampled passes. The 86.1% is a calibration-set observation, not guaranteed accuracy on new answers. Freeze these evaluator versions for comparisons and version any later changes.

### Current gateway architecture — September 29, 2026

One LiteLLM gateway serves support, evaluation candidates and the Claude judge. Three model-scoped virtual keys identify those workloads; the master key is administrative only. The support backend receives only its own key. The evaluation runner has candidate and judge keys and uses the separate `market_eval` business database. All model aliases are configured in `app/infra/litellm.yaml`. This supersedes earlier two-gateway descriptions; historical result snapshots remain intact. No automatic model-selection policy is enabled by this consolidation.


## Semantic scenario follow-up — September 30, 2026

[M19](MILESTONE-LOG.md#m19--semantic-routing-scenario-coverage-audit) records a scenario-only semantic iteration: six new business-scenario categories, unchanged 0.5 threshold and fallback. Fallbacks improved from 10 to 6, but correctness stayed 13/18 and replay cost rose from $0.137874 to $0.196334. Preserve as diagnostic evidence, not a promoted router improvement.


## Model-routing diagnostic phase — closed September 30, 2026

Completed classification replay, scenario-only semantic refinement, and live conversation-versus-question routing. No additional paid experiment is required to close this learning phase; production support still uses its fixed model.

- [Classifier comparison](app/results/routing-classifiers-2026-09-30/comparison.html): LLM/JEV provided the strongest observed quality among tested routes within the approved nano/GPT-5 pool. Restricted OpenRouter low and medium selected nano throughout.
- [Semantic scenario refinement](app/results/semantic-scenarios-v2-2026-09-30/comparison.html): fewer fallbacks but unchanged correctness and higher cost; not promoted.
- [Live granularity report](app/results/routing-granularity-2026-09-30/comparison.html): primary metric is all three answers correct across each of six conversations. Fixed GPT-5: 6/6; fixed nano and both routing policies: 4/6. The 18-answer breakdown is supporting detail. Routing cost about nine times nano and reduced outright incorrect answers, but did not improve fully correct conversations. No granularity winner was established.
- [Cache breakdown](app/results/routing-granularity-2026-09-30/cache-by-model.json): observed per-model cached-token fractions and cache-adjusted costs are retained; no causal benefit from pinning or switching is established.

The user accepted the three formerly flagged partial judgments; review is complete. They concern already non-passing conversations, so changing those partial grades alone does not change the 4/6 conversation score. Preserve the synthetic scenarios, gold, raw calls, accepted grades and report versions. Unrestricted OpenRouter selection was explicitly set aside in favor of enterprise-approved model lists; it is not a pending test.

Optional future optimizations: new held-out conversations and targeted repeats before deployment; identifier normalization for semantic matching; explicit escalation or per-internal-call routing; controlled cache experiments. These are separate future studies, not prerequisites for moving to another topic. Historical milestones retain their original findings; see the latest clarification in [M20](MILESTONE-LOG.md#m20--close-routing-phase-and-clarify-conversation-scoring).


## October 1, 2026 — catalog v2 baseline boundary

Catalog `2.0` / prompt `catalog-v2-question-context-v1` replaces sampled graph
records and business names with unified semantic/schema metadata and targeted
name queries. Clock/revision and optional preloaded history are appended to the
current question; prior question metadata is preserved. The last 12 user/assistant
messages are retained, not ordinary tool calls/results. See the
[prompt walkthrough](app/docs/PROMPT-AND-CATALOG.md) and
[validation report](app/results/catalog-v2-2026-10-01/REPORT.md).

Previous archived evaluations and routing results remain historical, not scores
for this candidate. Freeze the new source/catalog versions for any new comparison.
No cache benefit is established by this change alone; larger metadata and extra
name lookups can offset savings. Repeated controlled provider-input captures are
needed before making caching claims.

### Subsequent history-policy change

Prompt `catalog-v2-question-context-v3-evidence-reuse` retains six complete question
blocks including tool results. The preceding catalog-v2 paragraph describes its
archived initial baseline. New checks must cover same-revision reuse, changed-revision
refresh, changed-clock time-dependent refresh, incomplete/truncated evidence, and
same-conversation citation provenance. Document evidence has an independent revision.
Do not attribute any future cost/cache changes solely to catalog structure: history
retention and reuse instructions have now changed as well.

### Current prompt/history regression — October 1, 2026

The [full regression report](app/results/core18-history-v3-2026-10-01/REPORT.md)
and [side-by-side review](app/results/core18-history-v3-2026-10-01/comparison.html)
cover 18 cases / 20 answers per model with the current v3 history policy.
Assistant grades with user-approved cases 23/24: nano 11 correct / 4 partial / 3 incorrect;
GPT-5.4 17 / 1 / 0. No paid judge was used. Cases 23/24 were accepted as correct after rubric clarification;
historical fixture/reviewer differences are documented, not silently normalized.
This is the current implementation regression, not a replacement for the archived
nano/GPT-5 routing experiment baseline.

Separate reuse checks establish successful GPT-5.4 unchanged-state reuse and
clock-only recomputation, nano changed-revision refresh, and remaining nano
SQL recovery, boundary reasoning and unnecessary re-query behavior. Preserve the
failed attempt alongside successes. No caching improvement is claimed. See
[M30](MILESTONE-LOG.md#m30--re-evaluate-nano-and-gpt-54-after-prompthistory-changes)
for the milestone and cost summary.
