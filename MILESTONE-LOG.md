# Project milestone and learning log

This is the chronological project record for the practical AI-systems blog and potential Udemy series. It records meaningful milestones, decisions, lessons, evidence, and unresolved questions—not every command or chat message.

The [specification](SPECIFICATION.md) defines the application. The [research guide](RESEARCH-GUIDE.md) provides background. This log explains what we actually tried and learned. Detailed evidence remains in the linked evaluation artifacts and code.

## How to maintain this log

**Reading and update order: strictly chronological, oldest first, newest last.** Read M01 onward for the learning journey, or use the index to jump to a milestone. Append each new milestone at the end with its date, what we did, what we learned, evidence, and next steps. Record revised conclusions or grade corrections in a new dated entry referencing the earlier milestone; do not insert a rolling current-status summary at the top or rewrite historical results. A consolidated comparison belongs in a dated milestone at the point when we assembled it. The evaluation specification remains organized by topic.

Append an entry when a meaningful build, experiment, evaluation, diagnosis, or design decision is completed. In the same update, refresh the affected sections of [the course progress map](course/COURSE-PLAN.md): learning, tests/evidence links, hands-on readiness and pending work. The course plan shows current state by chapter; this log preserves chronology. Record partial or blocked work explicitly. Preserve earlier conclusions as historical observations; add a dated correction or follow-up when evidence changes. Never rewrite old results to imply a later fix existed during the original experiment.

Each entry should include:

- Question or goal.
- What we did and what changed.
- Results and supporting artifacts.
- What we learned, separating observation from interpretation.
- Limitations and unresolved questions.
- Next experiment or action.
- Material worth retaining for a blog or lesson.

Do not include API keys or credentials. Label synthetic data, provisional scores, human decisions, and inferred causes clearly. Publishing a blog or producing a course is a separate step.

## Entry template for future milestones

- **ID / date / status:**
- **Question or goal:**
- **What we did / changed:**
- **Results and evidence links:**
- **What we learned:**
- **Limitations / unresolved questions:**
- **Next experiment:**
- **Blog or lesson material:**

## Milestone index

| ID | Date | Milestone | Status |
|---|---|---|---|
| M01 | 2026-09-27–28 | Working marketplace and single-agent baseline | Completed; scope and limitations below |
| M02 | 2026-09-28–29 | Nano/GPT-5.4 evaluation and completed human review | Completed; scope and limitations below |
| M03 | 2026-09-29 | Failure diagnosis plan | Plan progressed through M09–M14 |
| M04 | 2026-09-29 | Claude judge calibration:31/36 agreement | Completed; scope and limitations below |
| M05 | 2026-09-29 | Publish calibrated results to Langfuse | Completed; scope and limitations below |
| M06 | 2026-09-29 | Consolidate shared gateway and virtual keys | Completed; scope and limitations below |
| M07 | 2026-09-29 | First offline session-pinned routing | Completed; scope and limitations below |
| M08 | 2026-09-29 | Richer classifier domain context | Completed; scope and limitations below |
| M09 | 2026-09-29 | Audit GPT-5.4 payout evidence | Completed; scope and limitations below |
| M10 | 2026-09-29 | Repeat original full-agent payout cases | Completed; scope and limitations below |
| M11 | 2026-09-29 | Version payout fixture with 30-minute post-hold gap | Completed; scope and limitations below |
| M12 | 2026-09-29 | Compare captured correct/incorrect inputs | Completed; scope and limitations below |
| M13 | 2026-09-29 | Targeted GPT-5 payout comparison | Completed; scope and limitations below |
| M14 | 2026-09-29 | GPT-5 core18 baseline and user adjudication | Completed; scope and limitations below |
| M15 | 2026-09-29 | LLM/JEV/restricted OpenRouter routing comparison | Completed; scope and limitations below |
| [M16](#m16--consolidate-cost-quality-and-latency-results) | 2026-09-30 | Consolidate cost, quality and latency results; adopt chronological log | Completed |
| [M17](#m17--extend-classifier-comparison-with-native-rules-and-medium-tier-routing) | 2026-09-30 | Native keyword, heuristic, semantic and OpenRouter medium replay | Completed |
| [M18](#m18--live-conversation-level-versus-question-level-routing) | 2026-09-30 | Live routing: six conversations, four policies | Completed; three grades flagged |
| [M19](#m19--semantic-routing-scenario-coverage-audit) | 2026-09-30 | Scenario coverage additions: fewer fallbacks, unchanged quality | Completed; not promoted |
| [M20](#m20--close-routing-phase-and-clarify-conversation-scoring) | 2026-09-30 | Close routing phase; clarify scoring and cache interpretation | Completed |
| [M21](#m21--frame-the-blog-around-the-decision-process) | 2026-09-30 | User-confirmed methodology-first framing for blog/course | Recorded |
| [M22](#m22--complete-granularity-review-adjudication) | 2026-09-30 | User accepts three partial grades; review complete | Completed |
| [M31](#m31--map-completed-work-and-pending-labs-to-every-course-chapter) | 2026-10-01 | Living course progress map and chapter evidence | Updated; labs tracked separately |
| [M32](#m32--compare-payout-orchestration-with-gpt-54) | 2026-10-01 | Serial tools, parallel tools and seller workers | Completed bounded experiment; review provisional |
| [M33](#m33--nano-generator-with-gpt-54-review-and-one-correction) | 2026-10-01 | Evaluator–optimizer workflow | Eight-case diagnostic completed; grades provisional |
| [M34](#m34--compare-reviewer-models-across-all-eighteen-cases) | 2026-10-01 | Nano versus GPT-5.4 review on core18 | Completed; grades provisional |
| [M35](#m35--explicit-user-scoped-long-term-memory) | 2026-10-02 | Explicit PostgreSQL memory and initial checks | Bounded implementation complete; broader labs pending |
| [M36](#m36--lyzr-agent-studio-with-authenticated-remote-mcp) | 2026-10-02 | Remote MCP and private Lyzr support agent | Implemented/smoke-tested; cloud middleware hosting pending |
| [M37](#m37--add-security-to-part-c-and-renumber-course-sections) | 2026-10-05 | Security section added to Part C; sections renumbered | Course planning only |

## M01 — Working reference application

**Retrospective entry recorded September 29, 2026.** This summarizes the established baseline; it is not a new verification of every historical test.

We selected a simulated marketplace with buyers, sellers, an operator, and a read-only support/investigation agent. The marketplace provides real state changes for experiments: purchases, stock adjustments, dispatch/delivery, seller payouts, returns, refunds and simulated failures. Loyalty and a more elaborate commerce platform were deferred.

The baseline uses React, FastAPI, PostgreSQL with pgvector, OpenAI Agents SDK, LiteLLM, and Langfuse. The support agent combines structured business records and policy/incident documents. Ontology and context definitions help identify relevant data. Simulated payment operations keep the focus on agent behavior.

We walked through purchase-to-payout, returns, refund retries, and post-payout manual-review scenarios. These exposed presentation problems such as unclear held/failed states, missing product context, and technical evidence labels. The design lesson was to make business state transitions understandable before using them to evaluate an agent.

Evidence and walkthrough references: [application README](app/README.md), [user journeys](app/USER-JOURNEYS.md), [specification](SPECIFICATION.md).

Teaching material: why a small functioning application is a better experimental foundation than static question-and-answer examples; business state versus conversation state; combining SQL and document evidence.

## M02 — Paired evaluation, Claude judge and human review

**Execution:** September 28, 2026. **Human review and revision:** September 29, 2026.

### Question

How does the same support agent behave with GPT-5 nano versus GPT-5.4? Can we evaluate retrieved data separately from the written answer, and use the results to guide diagnosis before changing the agent?

### What we did

- Defined a 30-case pool with independently specified expected facts and repeatable synthetic fixtures. Reduced this iteration to 18 cases to limit cost while retaining major capability families; some edge variants were deferred.
- Used an isolated `market_eval` database, matching starting fixtures, the same candidate prompt/tools and controlled model settings. The interactive marketplace was not reset.
- Collected 36 scenario answers: 18 per model. Two scenarios have follow-ups, giving 40 answer turns. One follow-up clarifies an ambiguous name; another changes business data between turns and checks freshness.
- Used pinned candidates `gpt-5-nano-2025-08-07` and `gpt-5.4-2026-03-05`.
- Used Claude Opus 5.5 with rubric `market-judge-v2` as a provisional semantic judge. It received the question, expected criteria, fixture facts/policies, candidate answer and evidence; it did not independently query the application. Candidate identity was omitted from the grading payload.
- Retained grades from direct Anthropic and OpenRouter routes to avoid unnecessary spend, and recorded route provenance. Billing/credit and timeout interruptions were resumed using saved answers. An earlier GPT-5.4 self-judge trial and the initial Claude rubric/parser attempts remain exploratory history, not the final reported judge grades.
- Added offline deterministic evidence-to-gold comparisons for six selected scenarios (14 turns). These check named record fields, not the final prose. Fixed reconciliation logic that incorrectly compared individual seller balances against the marketplace total.
- Improved the review UI to separate expected text and records, actual text and retrieved records, comparison results, and evidence requirements. These presentation changes did not rerun or silently rewrite the saved Claude grades.
- Completed human review of all 36 scenario answers. Flagged six inconsistent grade/agreement selections and one missing field; the user supplied a revised export resolving them. Both exports are retained.

### Results as recorded after the revised human review

| Model | Reviewer | Correct | Partially correct | Incorrect | Total |
|---|---|---:|---:|---:|---:|
| GPT-5 nano | Human | 8 | 8 | 2 | 18 |
| GPT-5 nano | Claude judge | 5 | 10 | 3 | 18 |
| GPT-5.4 | Human | 15 | 1 | 2 | 18 |
| GPT-5.4 | Claude judge | 10 | 6 | 2 | 18 |

Human fully-correct rates are **8/18 (44.4%) for nano** and **15/18 (83.3%) for GPT-5.4**. Both have two human-graded incorrect scenarios; much of the difference is between partial and fully correct answers. These are results on this selected task set, not a general model ranking.

Exact human–judge correctness-grade agreement is **27/36 (75%)**: 14/18 for nano and 13/18 for GPT-5.4. This is exact agreement on the three categories, not “the judge is 75% accurate.” Nine grade disagreements remain and are intentionally preserved.

The added structured comparisons report **13 passing and one failing turn out of 14 assessed turns**. The other 26 turns have no implemented structured record comparison; that is not evidence that they passed, and does not mean all are inherently unsuitable for deterministic checking.

Recorded cumulative model-cost estimate: **$5.4684**, including earlier attempts and grading/preflight costs. It excludes embedding setup and any unreported failed-call charges, and is not reconciled to provider invoices. No additional inference was needed for the structured checks or review-page improvements.

### What we learned

1. **Retrieving the right records and explaining them correctly are different tests.** Tool results are structured; the agent's final answer is generally prose. Record matching cannot prove final-answer correctness.
2. **A larger model can improve overall results and still make basic errors.** GPT-5.4 misapplied the 23-hour and exact-24-hour payout boundaries despite available timestamps. Nano sometimes reached a correct conclusion without sufficient justification.
3. **A judge can faithfully enforce an overly strict rubric.** Case 11 returned the correct historical 14-day policy, but the gold demanded the full effective-date range even though the question did not ask for it and the retrieved chunks did not expose it. Case 14 similarly raised whether stating an already-elapsed delivery hold was necessary when the answer correctly explained the provider timeout.
4. **Human disagreement is useful evidence, not something to erase.** Case 9 can be answered by clarification or by explicitly distinguishing buyer payment from seller payout. Several disagreements concern completeness or rubric interpretation rather than an obviously wrong value.
5. **Clarification quality matters.** For Acme, the models should explain that no match was found and ask an open question, rather than arbitrarily suggest Cedar. Nano's catalog dump and demo-clock detail also reduced clarity.
6. **Reproducibility saves money.** Saved answers, fixed fixtures, route/version metadata and separate grading allowed recovery from billing interruptions without repeating candidate runs.
7. **Review tooling needs business-readable expectations.** Mixing test instructions, technical joins and answer facts made human review confusing. Expected text, expected records and evidence requirements need separate presentation.

### Limits of these findings

- One run per candidate on 18 selected synthetic cases; no repeated trials, unseen holdout or statistical generalization.
- The human saw judge scores and discussed examples before finishing the review. The 75% figure is not a blinded, independent judge-calibration measurement.
- Claude judge routes were mixed, although configured model and rubric were retained. This was not a controlled comparison of serving routes.
- Gold criteria and judge judgments are still open to adjudication. UI reference rewrites are not new judge runs.
- We have not yet isolated model capability from prompt, retrieval, context selection, data or tool defects through controlled interventions.
- Langfuse contains the original automated experiments. Later structured-check changes and human-review summaries are saved locally and have not been synchronized to Langfuse.

### Evidence retained

- [Evaluation specification](EVALUATION-SPEC.md) and [18-case selection](app/eval/core-18.json).
- [Saved answers, evidence, traces and grades](app/results/core18-2026-09-28-03/results.json).
- [Human review page](app/results/core18-2026-09-28-03/review.html).
- [Revised human export](app/results/core18-2026-09-28-03/human-review.json).
- [Human-versus-judge summary](app/results/core18-2026-09-28-03/HUMAN-REVIEW-SUMMARY.md) and [source hashes/counts](app/results/core18-2026-09-28-03/human-summary.json).
- [Langfuse experiment identities](app/results/core18-2026-09-28-03/langfuse-experiments.json) and [readback verification](app/results/core18-2026-09-28-03/langfuse-verification.json).
- [Deterministic comparison implementation](app/backend/marketplace/eval_structured.py) and [tests](app/backend/tests/test_structured_gold.py).

### Blog and course material

Working topic: **“From a working agent to an evaluation you can trust.”**

A useful teaching sequence: build repeatable fixtures; run two models with the same agent; compare retrieved records; grade the final answer; review judge disagreements; distinguish measured outcomes from causal diagnosis. Good worked examples are Acme clarification, historical policy dates, the payout hold boundary, and a follow-up after a database change. Preserve the imperfect answers and rubric mistakes as teaching examples rather than presenting only successful outcomes.

## M03 — Diagnose failures

**September 29 update:** completed the first offline audit. There are no cases where both models are human-rated incorrect; cases 16 and 17 are the shared non-fully-correct cases (nano partial, GPT-5.4 incorrect). Independently recalculated the saved timestamps: 23 hours in case 16, exactly 24 hours in case 17. The backend eligibility comparison agrees with the gold. GPT-5.4 had the necessary policy and time evidence but applied it incorrectly; nano's evidence/explanation was incomplete. A common question category does not establish a common root cause.

[Diagnostic findings and controlled experiment design](app/results/diagnosis-2026-09-29/DIAGNOSIS.md) retain evidence links and separate observations from hypotheses. No paid calls, candidate prompt changes, or baseline score changes were made. Next: compact verified evidence, then the same evidence with a deterministic time calculation; keep those diagnostic results separate from the original benchmark.

Remaining steps:

1. Separate confirmed answer failures from disputes about gold requirements. Record any adjudication as a new version; preserve the baseline.
2. Select a small representative set of incorrect and partially correct cases across both models.
3. Inspect whether the necessary facts existed, were accessible through tools, were retrieved, and were interpreted correctly.
4. Where useful, give both models the same verified necessary evidence directly and rerun only those cases. Label these as diagnostic runs, not replacements for baseline scores.
5. Change one component at a time—prompt, context selection, retrieval/tool behavior or model—and compare results on the affected cases plus relevant regression checks.
6. Log observations, likely causes, uncertainty, costs and the next experiment. A correct answer after supplying evidence suggests an acquisition problem; it does not by itself establish whether the model, prompt or retrieval implementation caused it.

## M04 — Calibrate the judge against existing human review

**2026-09-29 — completed; accepted as the working judge baseline.** Revised gold requirements (`market-gold-v3`) separate essential facts, evidence and optional detail in seven cases. Revised rubric (`market-judge-v3`) accepts equivalent calculations and concise answers while retaining causal, entity-attribution and uncertainty requirements. Regraded all 36 saved answers with Claude Opus 5.5 through direct Anthropic; no candidate-model reruns. Existing human reviews remain unchanged.

- Exact human–judge agreement increased **27/36 (75.0%) → 31/36 (86.1%)**. Nano: 14/18 → 15/18; GPT-5.4: 13/18 → 16/18.
- Six original disagreements resolved; three remain (14/GPT-5.4, 15/nano, 23/GPT-5.4). Two new disagreements arose (21/nano, 28/nano): Claude upgraded these from partial to correct.
- No human-incorrect answer was graded fully correct. This observation concerns only this small reviewed set.
- Incremental recorded list-rate cost estimate **$2.5207**, excluding embeddings/unreported charges; not an invoice.
- Verified 36 fresh v3 grades, identical saved candidate runs/questions/evidence and deterministic verdicts, 11 focused-review cards, and 12 passing evaluation tests. Historical structured-check audit metadata differs because checks were replayed; their verdicts match. Original results and human exports preserved.
- Scores were not published to Langfuse. Gold and rubric changed together, so individual contribution is not isolated. Improvement is calibration on reviewed cases, not independent validation.

[Comparison summary](app/results/calibration-v3-2026-09-29/CALIBRATION-SUMMARY.md) · [Focused review](app/results/calibration-v3-2026-09-29/calibration-review.html) · [Plan and safeguards](app/results/calibration-v3-2026-09-29/CALIBRATION-PLAN.md).

### Acceptance and use for future models — September 29

The user accepted **86.1% exact agreement** as good enough for the working evaluation process. The five remaining disagreements (14, 15, 21, 23, 28) are accepted unresolved differences, not corrected human labels or blockers. Preserve both assessments. No further calibration rerun is required now.

Use the fixed Claude judge, rubric `market-judge-v3`, and `market-gold-v3` overrides to assess newer candidate models on the same repeatable tasks. Report candidate correct/partial/incorrect rates, deterministic checks, cost and latency separately. The 86.1% figure describes judge agreement with existing human assessments; it is not a candidate-model score, a pass threshold, or a guaranteed accuracy rate for future answers. Selective human checks can focus on uncertain judgments, failures and a small sample of passes rather than repeating a full manual review each time. Fresh validation remains useful follow-up work, not a prerequisite the user must complete before continuing.

### What the disagreement pattern and paired results tell us

All **five remaining v3 disagreements are correct versus partially correct**. None is incorrect versus correct, and no human-incorrect answer received full credit from Claude. The original v2 disagreements were also predominantly partial versus correct, with one partial-versus-incorrect exception (case 09/nano). This supports using v3 as our working judge while retaining selective checks; it does not establish a zero false-pass rate beyond this batch.

Under the unchanged human assessments, **no case has both candidate models rated incorrect**. This is encouraging evidence that the current context and tools provide a usable baseline, so we will keep that design and investigate specific failures rather than broadly redesign context. It is not proof that every answer received sufficient context: models can retrieve different evidence, and cases 16 and 17 were not fully correct for either model (nano partial, GPT-5.4 incorrect). In those two GPT-5.4 runs, relevant policy and timestamps were retrieved but interpreted incorrectly, pointing to a reasoning issue in those runs. Context sufficiency remains a per-run evidence question.

### How we improved the judge

1. Compared nine disagreements against the actual question, saved answer, evidence, gold and Claude rationale.
2. Found that gold mixed essential facts, evidence requirements and helpful extras, causing optional details to be treated as mandatory.
3. Split these categories in seven gold entries; accepted equivalent arithmetic, complete per-seller reconciliation and applicable historical-policy citations without unnecessary date ranges.
4. Clarified partial-credit rules and kept strict requirements for causal explanations, seller attribution, time boundaries and uncertainty. We did not relax every disputed case to match human labels.
5. Regraded all 36 saved answers, preserving human decisions and the original baseline. Six disagreements resolved, two new disagreements appeared, giving a net improvement of four matches (+11.1 percentage points).

The comparison changed gold and rubric together; the observed improvement cannot be attributed to either change alone or separated fully from judge variability in this single rerun.

Blog lesson: an evaluator can improve by clarifying material completeness, but broader rules may introduce new disagreements; measure the entire batch and keep original judgments.

## M05 — Publish calibrated evaluation and human review to Langfuse

**2026-09-29 — published and verified.** Created separate dataset `marketplace-core18-gold-v3`, preserving original `marketplace-30-v1` gold and runs. Uploaded unchanged candidate answers, revised Claude grades/rationale, original human grades/notes, recalculated human–judge agreement, structured checks and candidate cost estimates. No model calls.

Verified every answer, expected-output record and both correctness scores through the API: nano 18 items with 15 agreements; GPT-5.4 18 items with 16 agreements; total 31/36 (86.1%). Use runs ending **complete-import**. Earlier same-day attempts were interrupted by service timeouts (18 nano and 6 GPT-5.4 items observed); preserved as interrupted artifacts and superseded by these verified runs. Langfuse web/worker were restarted; existing database volumes and original evaluation were preserved.

- Nano experiment: `6a6ed6b0ee6c1120`.
- GPT-5.4 experiment: `5a1aa01e59027bee`.
- [Published run links](app/results/calibration-v3-2026-09-29/langfuse-experiments.json) and [full verification summary](app/results/calibration-v3-2026-09-29/langfuse-verification.json).
- Human review's original agreement selections still refer to the v2 review; `judge_human_agreement` is calculated against v3. Imported human scores have API provenance and are not new UI annotations.

**Evaluation closeout follow-up:** Deferred enhancements are tracked in [SPECIFICATION.md, Future Optimizations](SPECIFICATION.md#15-future-optimizations), sections 15.3–15.5: readable evaluation overview, Langfuse execution, and selective human review/fresh judge validation. These do not block the next experiment.

## M06 — Consolidate model access into one gateway

**2026-09-29 — implemented and verified.** Removed the separate evaluation LiteLLM container/config from active startup. One gateway at localhost:4000 now serves support-model, embedding, eval-nano, eval-54 and eval-judge. Historical configs are archived under `app/results/gateway-consolidation-2026-09-29`; existing evaluation snapshots remain unchanged.

Provisioned three named virtual keys: marketplace-support, marketplace-evaluation and marketplace-judge. Their model allowlists separate support, candidate and judge traffic; the backend no longer receives or uses the master key. Keys are stored in the ignored owner-readable `.env` and injected only into the appropriate containers. The master key remains administrative. An idempotent provisioning script makes this reproducible for new installations and existing restarts.

Updated the comparison and smoke runners to use the shared gateway through an on-demand eval-runner container. Evaluation data remains in market_eval. The judge and judge preflight use their own key. This changes access/attribution, not automatic model selection, strict spending limits or Redis integration.

Validation: three tiny live calls succeeded through support, candidate and Claude judge identities (20, 20 and 19 reported tokens respectively); all three allowed-model lists matched; cross-role model requests were denied; key provisioning reran without generating replacements; 12 evaluation/structured-check tests passed; Compose configuration and shell syntax checked. Support container verified to contain neither the judge key nor master key. No benchmark rerun or historical score changes.

Documentation: application README, evaluation README, SPECIFICATION.md and EVALUATION-SPEC.md now describe the single gateway. Lesson: distinguish runner isolation from gateway isolation and document actual process/deployment boundaries explicitly.

## M07 — First offline session-pinned routing experiment

**2026-09-29 — completed, exploratory.** Used the existing nano model as a low-cost LLM classifier through the shared LiteLLM evaluation key. A fixed marketplace rubric classifies only the opening question; SIMPLE selects nano and COMPLEX selects GPT-5.4 for the entire saved conversation. This is a custom offline classifier, not the native LiteLLM AutoRouter. No application behavior changed.

Replayed 18 cases with existing human grades: 13 selected nano, 5 GPT-5.4. Routed result: **11 correct / 4 partial / 3 incorrect**, versus nano **8/8/2** and GPT-5.4 **15/1/2**. Estimated candidate-plus-classifier cost $0.21760 versus $0.71090 for GPT-5.4 (69.4% lower), but quality was not preserved. Only the classifier calls incurred new estimated spend: **$0.001435**. Historical candidate costs are uncached list-rate estimates, not a new invoice or measured cache savings.

Lesson: a plausible complexity classification does not reliably predict which model will succeed; first-question session pinning also cannot see later demands. Cases 09/21/23/27/28 would have benefited from the saved GPT-5.4 answer; case 17 chose GPT-5.4 despite nano having the less severe failure. Do not tune silently or call this held-out validation. JEV, heuristic comparisons, live routing, caching and per-question selection remain future experiments.

[Findings](app/results/routing-offline-v1-2026-09-29/FINDINGS.md), [case-by-case report](app/results/routing-offline-v1-2026-09-29/REPORT.md), decisions, usage, prompt and script snapshot retained in that directory. Validated paired question/fixture identity, aggregation arithmetic, 18 valid classifier outputs and unchanged source/human-review hashes. No new candidate calls, judge calls, database resets or Langfuse uploads.

## M08 — Richer business context for the routing classifier

**2026-09-29 — completed, exploratory tuning.** Preserved v1 and ran 18 new nano classifier calls using v2's detailed task rules and full generic application ontology (entities, relationships, metrics and cautions). Only the opening question is classified, with session pinning and the same two candidate models. No gold, saved answers, human grades or future questions were sent to the classifier. The rubric was deliberately revised after inspecting v1, so this is not held-out validation.

V2 selects nano for 9 cases and GPT-5.4 for 9. Saved human-grade replay: **13 correct / 2 partial / 3 incorrect**, compared with v1 **11/4/3** and always GPT-5.4 **15/1/2**. Estimated replay cost including classification $0.43162, about 39.3% below always GPT-5.4 ($0.71090), but nearly twice v1's cost. Only **$0.005521** is new classifier spend estimate; candidate/judge answers were not rerun. No support behavior or gateway routing settings changed.

Four changed choices, all nano to GPT-5.4: 15 correct→correct (more expensive without grade benefit), 16 partial→incorrect, 21 partial→correct, 23 incorrect→correct. This validates the user's concern that complexity and model success are different: v2 consistently classifies payout eligibility as complex, but GPT-5.4's saved temporal reasoning is wrong. Richer context/rules improved the aggregate but not the number of incorrect answers. Cases 27/28 still use nano based on their first question; unknown follow-ups remain a session-pinning limitation.

[Comparison](app/results/routing-offline-v2-2026-09-29/COMPARISON.md), [per-case report](app/results/routing-offline-v2-2026-09-29/REPORT.md), prompt, ontology snapshot, script, raw responses and usage retained. Verified all 18 outputs valid, unchanged source/human hashes, identical paired question sequences/fixture hashes, unchanged per-model alternatives and comparison arithmetic. One classifier sample per case; variation and jointly changed context/rules prevent isolating causality. No live-cache or latency claim, database reset, support run, judge rerun or Langfuse upload.

## M09 — Audit GPT-5.4 payout failures before blaming model quality

**2026-09-29 — diagnosis completed; production fix not implemented.** Rechecked the two incorrect GPT-5.4 cases (16/17): saved full timestamps and retrieved policy agree with fixture gold and the backend `>= delivery + 24h` condition. Original answers respectively treated 23h as elapsed and exactly 24h as not eligible. No evidence of incorrect gold or missing timestamp data in these cases.

Ran six bounded GPT-5.4 synthesis probes: raw saved evidence, compact evidence, compact evidence plus code-computed timings, for each case. All six eligibility decisions were correct on assistant inspection; two outputs had malformed citation syntax. New estimated spending **$0.052115**; no judge calls, database writes or replacement of human grades. Since even raw-evidence probes passed, this does not prove a particular context fix caused improvement. Probes bypassed the original tool loop and orientation graph; one sample per condition cannot isolate presentation, orchestration or stochastic variation.

Learning: model capability, app context design and reliability are not mutually exclusive explanations. A clear app weakness is asking the model to calculate eligibility across scattered records while stored `held` is not an eligibility verdict. Recommend one authoritative read-only eligibility result shared with the business action, followed by boundary regressions and full-agent reruns. [Diagnosis and evidence](app/results/payout-diagnostic-2026-09-29/DIAGNOSIS.md).

## M10 — Repeat the original full-agent payout tests without a calculation helper

**2026-09-29 — completed.** At the user's request, reran GPT-5.4 cases 16/17 twice each, keeping the prompt, tools and business logic unchanged. No deterministic eligibility helper added. Fresh sessions and isolated evaluation fixtures; no judge calls. Verified question, fixture fingerprint and prompt hash identical to original runs. The gateway/authentication infrastructure differs from the historical baseline.

Eligibility on assistant inspection: case16 (23h) correct in both repeats, versus originally incorrect; case 17 (24h) incorrect then correct, versus originally incorrect. Thus 3/4 new decisions correct, with one reproduced failure. Full user grades were not assigned and old grades remain unchanged. Each run made 3 model calls and retrieved policy, full timestamps and return state. Search wording and incidental document chunks varied; exact causal attribution remains unresolved. Recommend freezing the final model input and testing one prompt intervention before changing application calculations. [Full report and preserved traces](app/results/payout-full-agent-repeat-2026-09-29/REPORT.md).

**M10 follow-up — captured input audit:** Retrieved Langfuse v4 final-generation messages for wrong/right case 17 runs. Confirmed timestamps, no-return state and policy are actually in model-bound messages with no tool truncation. Found a testable ambiguity: delivery occurred_at yields exactly 86400 seconds, while recorded_at (four microseconds later) yields 86399.999996 seconds. The prompt uses recorded_at for chronology without explicitly separating hold arithmetic. This may explain a boundary mistake but is not proven, and cannot explain every historical error. Also observed Python-dict string tool serialization, stored-held ambiguity and date-focused concise instructions. No code changes or paid calls. [Captured-input audit](app/results/payout-full-agent-repeat-2026-09-29/MODEL-INPUT-AUDIT.md).

## M11 — Version payout fixtures with a clear post-hold gap

**2026-09-29 — completed, failures preserved.** Added opt-in `eval/payout-v2` fixture and gold snapshots. Case16 stays23h; case 17 becomes24h30m. Original default fixture and exact24h boundary remain unchanged. Two deterministic fixture validations then two full GPT-5.4 repeats per case, no calculation helper/prompt changes or judge calls.

Eligibility results on assistant inspection: case16 incorrect in both repeats; case 17 incorrect then correct. All runs retrieved the correct timestamps and policy. Thus the four-microsecond timestamp ambiguity is not the sole cause; widening the gap did not establish reliable answers. This is a versioned data baseline, not proof of a stable model baseline. Original human grades/routing results untouched; no paired nano v2 run yet. Cost estimate $0.178505 excluding embeddings/setup. [Report](app/results/payout-v2-gpt54-2026-09-29/REPORT.md), [fixture documentation](app/eval/payout-v2/README.md).

## M12 — Compare actual correct/incorrect model inputs

**2026-09-29 — completed read-only trace audit.** Compared case16 at23h across correct/incorrect runs, and case 17 only on v2 24h30m correct/incorrect runs. Asserted identical per-pair prompt, question, fixture, core records, timestamps and required policy. No missing core fact found. Tool paths and incidental RAG passages differ: extra catalog occurs in incorrect16 but correct17, so it is not a universal explanation. Verified the live gateway maps eval-54 to the configured GPT-5.4 snapshot. [Side-by-side full messages](app/results/payout-input-comparison-2026-09-29/comparison.html), [findings](app/results/payout-input-comparison-2026-09-29/FINDINGS.md).

A separate exact24h replay had already started before the v2 clarification: previously-wrong captured input yielded wrong/correct/wrong; previously-correct input yielded correct/correct/correct. Confirmed identical gateway HTTP bodies within each condition. This is evidence of response variation at fixed input, not a v2 result. Six replay calls estimated $0.0684975, plus a separate full capture run recorded in payout-request-capture-2026-09-29. No production prompt/calculation changes or baseline score updates. Remaining diagnostic: freeze v2 payloads and vary only one explicit timestamp/held-semantics instruction.


## M13 — Compare GPT-5 on the two payout cases

**2026-09-29 — completed.** Ran only cases16/17 with GPT-5, three repeats each, same payout-v2 fixtures and unchanged agent/tool source and low reasoning. All six eligibility decisions correct on assistant inspection: case16 not eligible at23h, case 17 eligible at24.5h. Earlier GPT-5.4 v2 results were0/2 and1/2 respectively. This limited comparison suggests testing GPT-5 further; it does not prove general superiority or resolve the causal source of GPT-5.4 failures. Citation presentation still needs work; no full human grades assigned, no judge calls, and historical grades preserved. New estimated candidate plus preflight cost $0.16338750, excluding embeddings and infrastructure, uncached list rates. Added eval-5 gateway route and evaluation-key permission; support model unchanged. [Report and saved answers](app/results/payout-v2-gpt5-2026-09-29/REPORT.md).

## M14 — GPT-5 core18 baseline without paid judging

**2026-09-29 — completed, provisional assistant review.** Ran GPT-5 across 18 cases/20 turns on payout-v2 fixtures and reran only changed nano17. Reused17 compatible nano outputs and existing human grades. GPT-5:17 correct,1 partial,0 incorrect (94.4% fully correct); nano selected baseline:8 correct,8 partial,2 incorrect (44.4%). Reviewer provenance differs; do not call this a fully human-validated comparison. Flags: new nano17 contradictory hold wording, plus cases21/28 grading consistency with prior human decisions. If both flagged GPT-5 correct grades become partial its rate is83.3%; nano17 upgrade alone would yield50%. Historical reviews unchanged.

No Claude calls; new uncached-list-rate candidate/preflight estimate $0.45835840 excluding embeddings and infrastructure. All21 new answer turns completed with no unintended business mutations or query-record mismatches. GPT-5 structured comparisons:6 pass,13 N/A,1 not assessable (case 24 field alias; manually verified); case 21 citation-link defect is separate from factual correctness. Preserved prompts/source snapshots, fixture checks, grade reasons and reusable36-row comparison. No automatic routing enabled or dataset upload performed. [Report](app/results/core18-gpt5-v2-2026-09-29/REPORT.md), [comparison](app/results/core18-gpt5-v2-2026-09-29/comparison.html).

**M14 adjudication update — 2026-09-29:** User accepted nano17 partial, GPT-5 21 correct with citation defect separate, and GPT-5 28 correct without requiring a printed increase. Applied same case 28 rule to nano: historical partial now overridden to correct in the current comparison. Updated baseline: nano 9 correct/7 partial/2 incorrect (50.0%); GPT-5 17/1/0 (94.4%). Original human export unchanged; previous comparison and grade files archived under before-user-classification-v2. No API calls or additional model spend. Other historical nano grades were preserved; this remains a mixed-reviewer working comparison.


## M15 — Offline routing with nano/GPT-5: LLM, JEV and restricted OpenRouter Auto

**2026-09-29 — completed.**18 first-question selections per method, replayed whole saved sessions against the accepted grade snapshot. Nano LLM classifier:16 correct/1 partial/1 incorrect (88.9%),$0.24947 estimated replay total,45.3% below always GPT-5. JEV Choice via OpenRouter Decisions: same quality,$0.26602,41.7% saving; routes one extra already-correct case to GPT-5. OpenRouter market-based Auto at low cost tier, allowed_models restricted to nano/GPT-5 and returned IDs checked:18 nano picks,50% fully correct,$0.02312 replay estimate. This is a low-tier/two-model result, not a universal comparison of methods.

New classifier plus capped Auto-selection probe spend$0.011843668; no candidate-answer or judge reruns, DB mutation or production routing changes. Auto probes invoke a tiny completion and have separate experimental cost; their latency is not classification-only.17/18 Auto responses report task_type; case 09 lacks it and crowd-classification success there is unverified. Case27 is the shared routed failure: nano clarification then wrong follow-up, with the LLM classifier also inventing a customer interpretation. Candidate pool cannot fix case 09 because both saved answers are partial. Classifier guidance predates this run but was tuned on known cases; not held-out validation. [Comparison](app/results/routing-gpt5-llm-jev-2026-09-29/comparison.html), [findings](app/results/routing-gpt5-llm-jev-2026-09-29/FINDINGS.md), [method and raw artifacts](app/results/routing-gpt5-llm-jev-2026-09-29/REPORT.md).

**Documentation consolidation — September 29:** Updated current evaluation and routing summaries, full M01–M15 index, evaluation specification and product specification. Earlier milestone results remain historical; current nano case 28 adjudication is an explicit override, not a rewrite. No paid calls or application changes.

## M16 — Consolidate cost, quality and latency results

**September 30, 2026 — documentation milestone; no new model calls.** Consolidated the fixed-model and routing comparisons for future blog/course use, separated replay cost from new experiment spending, and added measured classifier latency with its limits. These tables capture the findings as of this entry; future changes belong in later dated entries.

The user requested a strictly chronological milestone log. Removed the top-of-file rolling summaries and placed their content here, after M15. M01–M15 remain in order, with their existing results and adjudication history preserved. Going forward, append dated milestones and corrections at the end; keep topic-based methodology in the evaluation specification.

### Blog-ready comparison: fixed models versus routing

**Consolidated September 30, 2026 from the September 29 experiments.** Keep the narrative and result tables here in the milestone log; the evaluation specification describes methodology and links here. Raw versioned artifacts remain the source of truth.

#### Quality and estimated cost to answer the same 18 cases

The fixed-model controls run one model for every case. The routing rows select between those same models using only the opening question, then reuse that model's saved whole-session answer, including follow-ups. Routing is an offline replay, not a new end-to-end agent run. Fully correct percentage counts only fully correct cases; partial answers are shown separately.

| Approach | Correct / partial / incorrect | Fully correct | Nano / GPT-5 selections | Answer cost | Classification cost | Total cost | Saving vs fixed GPT-5 |
|---|---|---:|---:|---:|---:|---:|---:|
| Fixed GPT-5 nano | 9 / 7 / 2 | 50.0% | 18 / 0 | $0.02312 | $0.00000 | $0.02312 | 94.9% |
| Fixed GPT-5 | 17 / 1 / 0 | 94.4% | 0 / 18 | $0.45624 | $0.00000 | $0.45624 | 0.0% |
| LLM classifier → nano / GPT-5 | 16 / 1 / 1 | 88.9% | 9 / 9 | $0.24403 | $0.00544 | $0.24947 | 45.3% |
| JEV classifier → nano / GPT-5 | 16 / 1 / 1 | 88.9% | 8 / 10 | $0.26226 | $0.00376 | $0.26602 | 41.7% |
| OpenRouter Auto, low; restricted to nano / GPT-5 | 9 / 7 / 2 | 50.0% | 18 / 0 | $0.02312 | $0.00000 | $0.02312 | 94.9% |

Costs are USD for the entire 18-case set, including follow-up answer calls. Candidate costs and LLM classification use uncached list-rate estimates; JEV classification uses API-reported usage cost. They exclude embeddings, judging and infrastructure and are not invoices. OpenRouter has no separate Auto Router surcharge; its capped selection probes are experimental spend below, not a recurring extra step in a deployed request.

**What we learned:** fixed GPT-5 gives the best quality in this sample. LLM and JEV routing retain 16 of its 17 fully correct cases while reducing estimated cost by 45.3% and 41.7%. JEV classification itself is cheaper, but its extra GPT-5 selection for case 20 increases total answer cost without improving the saved grade. Both routes lose case 27 when nano fails the follow-up. OpenRouter at low selects nano throughout; this is a cost-tier-specific result, not proof that crowd-based routing is generally worse.

**Implementation labels matter:** the LLM classifier calls nano through our shared LiteLLM gateway. JEV was called through OpenRouter's Decisions API. These are custom offline scripts; neither row is a benchmark of LiteLLM's native Auto Router implementation. LiteLLM Auto Router can use either classifier, but production routing remains disabled. OpenRouter Auto is its native market-based policy with an explicit two-model allow list.

#### Latency: measured classification overhead only

| Approach | Mean classifier request time | Scope |
|---|---:|---|
| Fixed nano / fixed GPT-5 | Not applicable | No classification step; this does not mean zero answer latency. |
| Nano LLM classifier | 2.67 seconds | 18 requests through the local LiteLLM gateway. |
| JEV classifier | 0.66 seconds | 18 requests directly through OpenRouter Decisions. |
| OpenRouter Auto | Not measured separately | Probe timings include candidate completion generation. |

These are observed mean request times including transport/gateway overhead, not isolated model compute speed. One sample per case and different call paths limit the comparison. **End-to-end routed answer latency was not measured in this offline replay.** For live experiments, measure user-question submission to completed answer, including classification, model/tool calls and retries; record cache usage and report latency distributions separately. Do not add averages from unrelated saved runs and present that as measured live latency.

Source: [saved classifier timing summary](app/results/routing-gpt5-llm-jev-2026-09-29/summary.json).

#### What we spent to run this comparison

This separate ledger explains experiment execution cost. Do not add the replay totals above together and call that new spending: the routing experiments reused candidate answers.

| New work in this iteration | Recorded / estimated spend |
|---|---:|
| GPT-5: full 18-case run, including availability check | $0.45635875 |
| Nano: changed case 17 rerun, including availability check | $0.00199965 |
| LLM classifier: 18 classifications | $0.00543620 |
| JEV classifier: 18 classifications | $0.003758748 |
| OpenRouter Auto: 18 capped selection probes | $0.00264872 |
| **Total new candidate, classification and probe spend** | **$0.470202068** |
| Additional Claude judging for this iteration | **$0** |

The other 17 nano answers came from the prior evaluation. Their historical cost is represented in the fixed-nano comparison, not charged again here. This is not cumulative project spending: earlier GPT-5.4 runs, payout diagnostics, classifier experiments, judge calibration, embeddings and infrastructure are outside this ledger. Human/assistant review time is not monetized; no dedicated external judge API was invoked for these grades.

#### Boundaries for a blog or course

Describe this as a small retrospective experiment on 18 known synthetic scenarios, with mixed human/assistant grades and explicit user adjudications. The classifier guidance was developed during prior experiments; it is not held-out validation. Exact percentages do not establish general model/router accuracy. The earlier 86.1% Claude agreement measures calibration against human labels, not these answer-quality percentages. No measured cache savings or end-to-end routing latency is claimed. OpenRouter cost tier, candidate pool and model-selection granularity remain independent variables for later tests.

Sources: [versioned candidate comparison](app/results/core18-gpt5-v2-2026-09-29/comparison.json), [routing comparison and costs](app/results/routing-gpt5-llm-jev-2026-09-29/comparison.json), [readable routing report](app/results/routing-gpt5-llm-jev-2026-09-29/comparison.html), [evaluation methodology](EVALUATION-SPEC.md).

### Evaluation baseline consolidated from September 29 results

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

### Routing results consolidated from September 29 experiments

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

#### What was implemented versus what LiteLLM provides

LiteLLM **Auto Router is the routing feature**, while heuristic, LLM, JEV and custom classifiers are alternative ways to select a tier. Tier configuration maps that tier to a model or pool. Our experiment used custom offline scripts: nano classification through the shared LiteLLM gateway, JEV Choice through OpenRouter Decisions, and native OpenRouter Auto probes. **LiteLLM's native Auto Router is not enabled in the support application.** JEV's transport through OpenRouter does not make it the same policy as OpenRouter's market-based Auto Router.

#### Findings, limits and next experiments

Both custom classifiers lost one correct answer versus always GPT-5: case 27 routed to nano, whose clarification follow-up failed. The LLM classifier also incorrectly interpreted Cedar as a customer. Case09 is partial for either candidate, so selecting between them cannot repair that saved response. Low-tier OpenRouter selected nano throughout; this does not establish that crowd-based routing is generally inferior. Cost tier and the two-model restriction matter.

Keep these dimensions distinct: **classifier policy; routing granularity; candidate pool; cost tier**. Granularity can mean once per conversation, once per user question/investigation, or every internal model call. Only the first has been tested here. Next options are a separately versioned OpenRouter cost-tier comparison and live tests of per-question/per-call routing. Measure real quality, classifier overhead, retries, latency and prompt-cache tokens; cache savings cannot be inferred from offline replay. No additional experiment is implied by documenting these options.

This is a small known diagnostic set with one classifier sample per case, domain guidance developed during earlier experiments and mixed-reviewer saved grades. It is not a held-out benchmark. Source hashes, prompts, requests, responses, selections and cost accounting are preserved. No production routing changes or latest dataset upload were made; normal candidate execution traces exist separately.

Evidence: [routing comparison](app/results/routing-gpt5-llm-jev-2026-09-29/comparison.html), [findings](app/results/routing-gpt5-llm-jev-2026-09-29/FINDINGS.md), [method and raw artifacts](app/results/routing-gpt5-llm-jev-2026-09-29/REPORT.md). Platform references: [LiteLLM Auto Routing](https://docs.litellm.ai/docs/proxy/auto_routing), [OpenRouter Auto Router](https://openrouter.ai/docs/guides/routing/routers/auto-router).


## M17 — Extend classifier comparison with native rules and medium-tier routing

**September 30, 2026 — completed offline comparison.** Builds on M15/M16, preserving the same two candidates, payout-v2 fixtures and accepted saved grades. The user narrowed the scope to keyword rules, default heuristic, native semantic matching and OpenRouter medium; high tier and Not Diamond were deferred.

| Added policy | Correct / partial / incorrect | Fully correct | Full-price replay cost | Nano / GPT-5 |
|---|---|---:|---:|---:|
| Keyword rules + heuristic fallback | 15 / 2 / 1 | 83.3% | $0.239885 | 8 / 10 |
| Default heuristic | 9 / 7 / 2 | 50.0% | $0.038072 | 17 / 1 |
| Semantic matching + heuristic fallback | 13 / 4 / 1 | 72.2% | $0.137874 | 13 / 5 |
| OpenRouter medium, restricted pair | 9 / 7 / 2 | 50.0% | $0.023121 | 18 / 0 |

The native classifier code is from installed LiteLLM 1.102.1, executed in an isolated process. SIMPLE maps to nano and higher tiers to GPT-5. Keyword rules use highest-tier precedence and record collisions. Semantic matching uses 14 frozen journey examples, text-embedding-3-small, max similarity, threshold 0.5; **10 of 18 cases had no semantic match and used heuristic fallback**. Results therefore describe this configuration, not pure semantic routing without fallback. Settings were hashed before execution and not tuned after results.

OpenRouter requests explicitly sent medium with the same nano/GPT-5 allowlist and 16-token output cap. All 18 returned nano, with GPT-5 appearing as a fallback in metadata. This confirms the observed selections, not that we have enumerated the medium tier or proved the cost setting's internal behavior. The probe output was not graded.

**New spend:** semantic embedding estimate $0.00000760 plus OpenRouter-reported probes $0.00217640 = **$0.00218400**. Candidate costs in the table are saved-answer replay estimates, not additional API calls. No paid judge. Existing LLM/JEV remain 16/18 fully correct; all nine policies appear in the consolidated artifact.

**Learning:** simple rules recover much of the observed benefit; default text-complexity scoring misses domain difficulty; semantic routing is sensitive to example coverage and no-match behavior. Increasing OpenRouter's requested tier did not change this restricted experiment's choices. These are known development cases with mixed-reviewer saved grades; no general superiority claim is justified.

**Next:** six fresh three-turn scripts, four live policies (fixed nano/GPT-5, conversation pinning, question-level routing), unchanged agent and production app. Measure regenerated answer quality, total cost, latency and actual cached tokens. One pass first; no paid judge.

Evidence: [comparison](app/results/routing-classifiers-2026-09-30/comparison.html), [report](app/results/routing-classifiers-2026-09-30/REPORT.md), [summary and decisions](app/results/routing-classifiers-2026-09-30/summary.json), [frozen configuration and execution instructions](app/eval/routing-final-v1/README.md).

Blog material: classifier versus model pool versus routing frequency; reporting semantic no-match fallbacks; distinguishing low-cost selection probes from full live answer evaluation.


## M18 — Live conversation-level versus question-level routing

**September 30, 2026 — completed; three borderline partial grades flagged for user review.** Following M17, ran six new three-turn conversations under four policies: 72 generated answers. The existing domain-aware nano classifier selected nano or GPT-5. Agent prompts, tools and production routing stayed unchanged.

| Policy | Correct / partial / incorrect | Fully correct | Cache-adjusted cost | Full-price cost | p50 / p95 seconds | Cached input fraction | Switches |
|---|---|---:|---:|---:|---:|---:|---:|
| always_nano | 15 / 1 / 2 | 83.3% | $0.013809 | $0.019529 | 10.3 / 20.2 | 50.6% | 0 |
| always_gpt5 | 18 / 0 / 0 | 100.0% | $0.271415 | $0.460487 | 13.2 / 34.8 | 64.0% | 0 |
| conversation | 15 / 2 / 1 | 83.3% | $0.126447 | $0.206257 | 10.4 / 33.1 | 54.0% | 0 |
| question | 15 / 2 / 1 | 83.3% | $0.126897 | $0.219051 | 13.4 / 38.8 | 57.9% | 4 |

Costs include candidate calls, classifier calls and retrieval embeddings. Cached prices are reconstructed from reported usage and frozen rates, not an invoice. Reasoning output tokens are included in completion tokens. No paid judge calls.

Total new live-run estimate: $0.538568 cache-adjusted; $0.905324 at full input prices.


**What we learned:** Fixed GPT-5 was correct on all 18 turns in this single pass. Both routing policies scored 15/18 fully correct and saved about 53% versus GPT-5 after observed cache discounts. Fixed nano also scored 15/18, but had two incorrect answers rather than one. Equal fully-correct rates conceal different failures. Question routing made four switches without improving aggregate correctness: it recovered the missing delivery-hold explanation in one conversation but gave an incomplete initial lamp lookup elsewhere. Both routes selected 12 nano and six GPT-5 turns, not necessarily the same turns.

The clarification conversation exposed an invented today-only filter in nano continuations. Three final answers coincidentally returned the correct empty undelivered set with the wrong reasoning; these are provisionally partial and flagged for user review. All 72 answers were manually reviewed by the assistant against frozen facts, with no paid Claude judge. Citation formatting and one stale revision label are separate presentation issues.

All policies read the changed balance after purchase and correctly recognized 24h30m elapsed after the demo-clock advance. Cached-input fractions were 50.6% nano, 64.0% GPT-5, 54.0% conversation and 57.9% question. Shared caches, differing histories and one pass cannot identify a causal cache-switch penalty. This is a new six-conversation diagnostic set over familiar fixtures, not a direct rerun of the prior core18 set or independent validation.

**Validation:** All 72 turns completed; identical per-turn fixtures across policies; no agent business mutations; internal calls stayed on the selected model; captured usage matched SDK totals. Independent checks validated gold against frozen snapshots. Execution/gold validation is separate from manual answer grading.

**Funding and costs:** An OpenAI credit rejection interrupted the run after 22 successful turns. Following funding, restored prior conversation history and retried only the interrupted question; retained all completed answers and the failed attempt. One rejected request has no usage, so its charge is unverified. The spend guard's $0.20 reserve is not measured spend. A proposed OpenRouter replacement was never run; temporary gateway configuration was restored without activation. Funding downtime is excluded from latency but may affect cache warmth.

Known completion-batch cost is approximately **$0.54138318**: live usage estimate $0.53856793, M17 classifier/probe cost $0.00218400, and OpenRouter availability probe $0.00063125. This is not invoice reconciliation. No paid judge or new Langfuse dataset upload.

**Next:** Review the three flagged partial decisions when convenient. This diagnostic phase needs no further paid run. Fresh conversations and targeted repetitions are needed before broad deployment recommendations. Per-internal-call routing, explicit escalation, stage routing and a third candidate remain deferred.

Evidence: [live comparison and all answers](app/results/routing-granularity-2026-09-30/comparison.html), [report](app/results/routing-granularity-2026-09-30/REPORT.md), [summary](app/results/routing-granularity-2026-09-30/summary.json), [validation](app/results/routing-granularity-2026-09-30/validation.json), [gold checks](app/results/routing-granularity-2026-09-30/gold-validation.json), [manual review](app/results/routing-granularity-2026-09-30/assistant-review.json), [frozen configuration and reproduction](app/eval/routing-final-v1/README.md).

Blog material: offline replay versus live evaluation; pinning versus per-question selection; equal accuracy with different errors; correct answers for wrong reasons; observed caching versus causal claims.


## M19 — Semantic routing scenario coverage audit

**September 30, 2026 — completed, not promoted as a quality improvement.** Reviewed the ten v1 semantic no-matches by business scenario. Added six missing or underrepresented categories: payment-direction ambiguity, current-policy lookup, effective-date policy lookup, return exception review after settlement, refund attempt history, and partial-return seller allocation. Added twelve scenario descriptions; did not copy test questions, change the 0.5 threshold, alter fallback, or tune against answer grades. Existing coverage for unpaid seller, ambiguous name and balance scenarios was left intact.

Fallbacks fell from 10/18 to 6/18, but selected-answer grades stayed **13 correct / 4 partial / 1 incorrect**. GPT-5 selections rose from five to nine; full-price replay cost increased from **$0.137874 to $0.196334**. All four candidate switches replaced already-correct saved nano answers. New embedding calls cost an estimated **$0.00001226**; no answers or paid judges were rerun.

Learning: missing coverage is only one issue. The current-policy question matched a historical-policy description. Two otherwise identical refund-history questions with different order IDs scored 0.529 and 0.493 against the nearest added scenario, straddling the threshold. Existing scenario coverage also still produced misses. Semantic closeness to a business topic does not guarantee the right capability tier. A future identifier-normalization diagnostic should be separately versioned; no normalization or threshold change was made here. These are development-set results, not independent validation.

Also clarified the consolidated cost table: JEV classification cost $0.003759 versus nano LLM classification $0.005436. JEV's route total is higher because it selected GPT-5 10 times rather than nine; the two classifier costs are not combined.

Evidence: [scenario report](app/results/semantic-scenarios-v2-2026-09-30/REPORT.md), [review page](app/results/semantic-scenarios-v2-2026-09-30/comparison.html), [per-case similarities](app/results/semantic-scenarios-v2-2026-09-30/analysis.json), [versioned configuration](app/eval/semantic-scenarios-v2/classifiers.json). Original M17/M18 results are preserved; production routing is unchanged.

Blog material: scenario coverage versus semantic matching; incidental identifier sensitivity; fewer fallbacks without better quality; classifier cost versus selected-model cost.


## M20 — Close routing phase and clarify conversation scoring

**September 30, 2026.** Following review of M18, lead the live report with fully correct conversations: all three answers must be correct. The same six scenarios were run under four policies (18 answers per policy, 72 total). Fixed GPT-5 passed 6/6; fixed nano, conversation routing and question routing passed 4/6 each. Preserve the per-answer grades as supporting detail. This corrects an overly strong conversational recommendation: the pilot establishes no granularity winner and no compelling advantage over nano at roughly nine times its cost, although routing reduced incorrect individual answers from two to one.

Cache breakdown shows question routing had higher cached fractions within both models than conversation routing: nano 51.5% versus 47.8%, GPT-5 66.9% versus 61.6%. It had a smaller GPT-5 share of input tokens (41.5% versus 44.6%), so model mix alone does not explain its higher overall rate. Prompt histories, shared cache warmth, ordering and the funding pause remain possible explanations, not established causes. Savings percentages are explicitly relative to fixed GPT-5 using cache-adjusted costs.

The user chose to retain an enterprise-approved model pool and set aside unrestricted OpenRouter selection. No unrestricted run completed. The routing learning phase is closed; held-out validation, targeted repeats, explicit escalation, semantic identifier normalization and controlled cache tests remain optional future work. No new model calls were needed for this scoring/documentation clarification.

Evidence: [updated report](app/results/routing-granularity-2026-09-30/comparison.html), [Markdown report](app/results/routing-granularity-2026-09-30/REPORT.md), [cache by model](app/results/routing-granularity-2026-09-30/cache-by-model.json), [classifier comparison](app/results/routing-classifiers-2026-09-30/comparison.html), [semantic follow-up](app/results/semantic-scenarios-v2-2026-09-30/REPORT.md). The specification, evaluation specification and application/evaluation READMEs now link to the current reports. Historical M17–M19 remain chronological records.


## M21 — Frame the blog around the decision process

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


## M22 — Complete granularity review adjudication

September 30, 2026: the user accepted the three flagged S3 turn-3 partial grades (fixed nano, conversation routing, question routing). Review is complete; other grades remain assistant-reviewed, not a claim of full human regrading. No scores changed and no model calls were rerun. Historical pending-review statements in M18–M20 describe their status at that time and are superseded by this entry.

The 4/6 score means all three turns were correct in four conversations; it does not mean the other two were merely partial. Fixed nano had incorrect answers in S2 turn 1 (48-hour elapsed hold wrongly treated as not elapsed) and S3 turn 2 (invented today filter). Both routing policies had an incorrect S3 turn 2; conversation routing also had a partial S1 turn 2 and question routing a partial S5 turn 1. All three had the accepted partial S3 turn 3. Fixed GPT-5 had no incorrect or partial answers in this run.

[Updated report](app/results/routing-granularity-2026-09-30/comparison.html) · [Review and adjudication](app/results/routing-granularity-2026-09-30/assistant-review.json).


## M23 — Publish routing series and synchronize documentation

**September 30, 2026 — completed.** Published [Part 1: Choosing a Classifier](https://sreeni.blog/2026/09/30/model-routing-part-1-choosing-a-classifier/) and [Part 2: Choosing the Scope](https://sreeni.blog/2026/09/30/model-routing-part-2-choosing-the-scope/). Part 1 was already published when shortening was requested; Part 2 was initially saved as a shortened draft and was subsequently found published. Its objective now explicitly continues Part 1 and links to it.

Trimmed repeated introductions, recaps and conclusions: approximately 20% for Part 1 and 24% for Part 2. Preserved the results tables, figures, concrete failures, grading provenance, replay/live distinction and sample-size/cache limitations. The lesson remains the decision process for a use case, not a universal winning router.

Synchronized the local Markdown posts and article-body HTML snapshots with public WordPress content. Added a [publication index](blog/model-routing/README.md), a [snapshot manifest](blog/model-routing/publication-sync.json), and publication links in the specification, evaluation specification, research guide and application README. Marked the older writing brief and review as historical context so they are not mistaken for current unpublished work.

**Verification:** fetched both published article bodies; retained two figures/two tables in Part 1 and three figures/four tables in Part 2; checked Part 2's opening continuation link and local artifact links. Raw results, golden versions and accepted grades remain unchanged. No new model calls, evaluation costs or runtime changes were introduced.

**Next:** routing's diagnostic and publication phases are complete. Larger held-out validation, repeats, native gateway policy tests and controlled caching remain optional future experiments, not publication blockers. Future website edits should be synchronized with these local copies.


## M24 — Agree course learning scope and v1 priorities

**September 30, 2026 — course planning decision, not an implementation milestone.** Updated the [course plan](course/COURSE-PLAN.md) to teach how AI agent-system components work and how to evaluate design choices. Removed the production-grade promise; general infrastructure, identity/authorization implementation and broad security operations are outside the course focus. Existing safeguards remain, with AI-specific guardrail behavior taught where relevant.

Context and retrieval comparisons are embedded in sections 5 and 7, with tool-contract labs in section 6. Small known-answer checks accompany component changes; detailed evaluation follows in Part C. Added an initial installation/setup walkthrough and planned learning objectives plus hands-on changes/results for every numbered lesson. These labs still need implementation and learner verification.

Multi-agent and cross-conversation memory are required for v1, alongside routing. Retained Gemini and AWS learning tracks; Claude Managed Agents, Lyzr and Microsoft Foundry are outside the release commitment. Reduce optional breadth before deferring either multi-agent or memory. This changes course scope only; no application code, experiment scores or published posts changed.

## M25 — Name the course and prepare an external review outline

**September 30, 2026 — course planning artifact.** Adopted **AI Agent Engineering: Build, Evaluate, and Improve**, with the subtitle **Build a real AI application, experiment with its components, and compare agent frameworks and platforms hands-on.** Updated the [course plan](course/COURSE-PLAN.md).

Created a [Google Doc for course feedback](https://docs.google.com/document/d/1rcXN8C5P0o7AqQWdzh7CVFlvRq1WJRGLUA4o-GSCPZc/edit) in the ChatGPT folder in Google Drive. It includes audience, prerequisites, setup, learning outcomes, all 20 lessons with objectives and labs, and review prompts. Internal build status, authoring attribution and release-version planning are omitted. Verified the complete text and heading structure through Google Docs readback. No sharing permissions or messages to reviewers were sent.

Additional low-code agent platforms are being considered for discussion; this does not yet add a new course track or change the agreed implementation scope.

## M26 — Expose read-only support tools through MCP

**September 30, 2026.** Added a local stdio MCP server for the existing five support tools, with one process/snapshot/evidence store per investigation. Shared callable contracts keep direct and MCP tool logic aligned. Support Compose defaults to MCP; direct access remains selectable. Refunds, payouts and all business mutations remain UI/API operations. Remote HTTP deployment is not implemented.

**Verification:** 43 tests passed, including real MCP protocol parity, rejection, snapshot and isolation checks. Eight live nano answers completed on the isolated test database, with no judge calls. Estimated candidate cost totaled $0.006156, excluding embeddings and using existing list-rate accounting. This is a transport smoke test, not a model-quality benchmark. Both paths exposed prior citation reuse and poor payout eligibility explanations; these need separate agent-quality follow-up. See [MCP report](app/results/mcp-transport-2026-09-30/REPORT.md), [raw results](app/results/mcp-transport-2026-09-30/comparison.json) and [setup](app/README.md#read-only-tools-over-mcp).

**Learning:** MCP standardizes access; it does not automatically improve reasoning. Preserve snapshot ownership and evidence identity across the boundary before comparing platforms.

## M27 — Fix follow-up evidence links and finish MCP lifecycle checks

**September 30, 2026.** Fixed citation display to resolve prior-run evidence within
the same conversation, visibly identifying the original question and snapshot.
No change to model context or query behavior; structured evidence reuse remains
outside this change. Current, unknown, future and cross-conversation references
retain their appropriate boundaries.

**Verification:** 45 backend tests and six frontend tests passed; frontend build
and deployment succeeded. Concurrent MCP isolation and forced subprocess
failure/recovery tested. Browser verification reproduced a zero-tool follow-up
answer of four units and successfully opened the prior evidence with its original
snapshot. One live model API timeout was recorded and the retry passed. See
[follow-up validation](app/results/mcp-transport-2026-09-30/FOLLOW-UP-VALIDATION.md)
for run/trace IDs and test scope. No marketplace business state was changed.


## M28 — Unify semantic catalog and explain question-scoped model context

**October 1, 2026.** Replaced the sampled-record “context graph” with the static
business relationship map already in the ontology. Catalog v2 merges definitions
with database types, nullability and relevant constraints; validates structural
drift and direct-view lineage; and returns no seller/product or first-30-record
samples. Names are resolved through targeted SQL. Kept revision/demo clock as
per-question metadata, appended after the question and optional history evidence,
without rewriting static instructions or older messages.

Added a [three-question prompt and SQL walkthrough](app/docs/PROMPT-AND-CATALOG.md),
including what is static, what get_catalog returns, how queries are constructed,
and what history is retained. Updated README, specification, evaluation spec,
research-guide terminology and the affected course-plan lesson. No published blog
or Google Doc was edited in this milestone.

**Verification:** 50 backend tests passed; deployed backend health check passed.
18 live nano cases (20 answers) completed through MCP on isolated market_eval,
without a paid judge; estimated candidate/probe cost $0.034974 excluding embeddings
and cache discounts. All query-bearing turns matched replayed database records;
all four defined structured-gold turn checks passed. This is execution/evidence
verification, not 100% answer correctness. Inspection found wrong amounts, seller
attribution, eligibility, follow-up scope and citation formatting in some answers;
these remain explicit quality follow-ups. See the [validation report](app/results/catalog-v2-2026-10-01/REPORT.md).

**Learning:** the former “context graph” name overstated a sampled SQL relationship
view. Static semantic relationships, dynamic records and per-question snapshot
metadata should be explicit separate concepts. Retaining old question timestamps
preserves those messages, but normal tool results are still dropped across
questions and history is capped at 12 messages. Cache improvement remains
unmeasured. Old evaluations remain historical evidence for their archived versions;
this version does not inherit their quality scores.

### M28 follow-up — Trace incorrect answers before changing the system

**October 1, 2026.** Completed a [saved-input diagnosis](app/results/catalog-v2-2026-10-01/DIAGNOSIS.md) of incorrect cases 09/14/17/27 and partially correct case 15. Verified all 17 saved evidence objects across six turns against final SDK inputs, with no query truncation. Found an arithmetic error despite explicit units, a dropped seller filter, omitted policy retrieval, and an invented today filter despite retained conversation history. Case 17 uses a different boundary fixture from the accepted historical comparison. No paid calls, application changes, or automatic regrading were made during diagnosis.

**Learning:** distinguish evidence never requested from evidence lost in transport and evidence misinterpreted after receipt. The first failed decision is more informative than labeling every failure a model problem or a context problem. Saved SDK captures localize failures but do not prove provider receipt or the causal effect of a prompt change. Targeted same-input/context-intervention experiments remain proposed, not completed.

### M28 follow-up — GPT-5.4 on the four nano failures

**October 1, 2026.** [Targeted full-agent comparison](app/results/catalog-v2-gpt54-2026-10-01/REPORT.md) ran cases 09/14/17/27 (five answers) with identical source, ontology, static prompt and fixture hashes. GPT-5.4 gave correct business answers on all four under assistant review; nano had been incorrect on these selected cases. GPT-5.4 fetched settlement policy for eligibility, preserved seller identity and avoided the invented today filter. Case 14 still had malformed evidence handles. This is one sample on selected failures, not a new 18-case benchmark or proof of repeatability. No paid judge; model/probe estimate $0.352245 excluding embeddings/cache discounts. No app behavior changed.

### M28 follow-up — Exact citation copying prompt and paired check

**October 1, 2026.** Strengthened and deployed the citation instruction (prompt v2-citations), then reran 09/14/17/27 on nano and GPT-5.4: 8 case runs / 10 answers. [Report](app/results/citation-prompt-v2-2026-10-01/REPORT.md). Strict offline audit found GPT-5.4 13/13 references valid; nano 4/5 valid, with one extra character in a case-14 handle. All 10 state-preservation/SQL-replay checks passed; no paid judge; model/probe estimate $0.370519 excluding embeddings/cache discounts. Prompt-only runtime change; no automatic citation repair.

**Learning:** explicit formatting instructions help but do not guarantee handle identity. Citation validity is separate from answer correctness: GPT-5.4 case 17 now says No while explaining that the hold elapsed and no return blocks release; its previous answer was Yes. Repeated consistency is unproven, and this variation cannot be causally attributed to the wording from one before/after sample. Central runtime citation validation remains a follow-up.

## M29 — Retain tool evidence and compare revision/clock before reuse

**October 1, 2026.** The conversation now retains six complete question blocks
including tool calls/results, instead of only the last 12 user/assistant messages.
Current-question metadata includes business revision, clock and document revision.
Prompt rules guide reuse of complete same-revision facts, refresh after changes,
time-dependent recomputation, policy validity and historical evidence provenance.
Explicit history-prefetch remains unchanged. This is conversation history, not
cross-session memory or deterministic semantic freshness enforcement.

**Verification:** 51 backend and 6 frontend evidence tests passed. Five live
GPT-5.4 turns showed unchanged balance reuse with zero tools, a changed-revision
balance refresh, and a clock-only eligibility change from No to Yes at the same
revision using retained facts and policy. Model estimate $0.308808 excluding
embeddings/cache discounts; no paid judge. See the [report and captured inputs](app/results/evidence-reuse-2026-10-01/REPORT.md).

**Learning:** an unchanged revision can make another SQL query unnecessary, while
a changed clock can require recomputing eligibility without re-fetching unchanged
records. Retained tool history enables this; model behavior still needs evaluation.
No cache improvement or full-suite quality score is claimed. Old sessions cannot
recover tool results discarded before this change. README, specification, evaluation
spec and the three-question prompt walkthrough now describe the new policy.

## M30 — Re-evaluate nano and GPT-5.4 after prompt/history changes

**October 1, 2026.** Completed 18 cases / 20 answers per model on the current
catalog-v2 / question-context-v3-evidence-reuse implementation, using isolated
market_eval and MCP. Assistant grading only; no paid Claude judge. All 40 answers
completed. [Report](app/results/core18-history-v3-2026-10-01/REPORT.md) ·
[Side-by-side answers and historical grades](app/results/core18-history-v3-2026-10-01/comparison.html).

**Results:** nano 9 correct / 6 partial / 3 incorrect; GPT-5.4 15 / 3 / 0.
Latest accepted nano was 9 / 7 / 2, but its case-17 fixture used 24.5 hours instead
of exactly 24; the remaining 17 matching fixtures have the same aggregate
9 / 6 / 2 before and after. Original human-reviewed GPT-5.4 was 15 / 1 / 2;
its fully correct count is unchanged, with fewer outright wrong answers now.
Historical human/composite reviews and current assistant judgments differ;
cases 23/24 remain explicitly review-sensitive. No causal accuracy improvement
or broad model ranking is established by one sample on this small known set.

**Verification:** all 40 business-state checks passed, 34 SQL replays matched,
11 defined structured-gold checks passed, and four policy-version checks passed.
GPT-5.4 emitted 47/47 exact valid citations; nano 46/48, with two spacing defects
and additional raw-handle clutter. Checks without relevant SQL/gold were not
counted as passes. Full-suite estimate $1.247814.

**Targeted history checks:** GPT-5.4 correctly reused unchanged balance evidence,
refreshed after revision change, and recalculated eligibility at a clock-only
24-hour boundary without re-fetching facts. Nano refreshed the changed balance,
but failed its initial balance attempt on SQL/step-limit recovery and rejected
exactly 24 hours incorrectly. A separate clean quantity follow-up answered four
units correctly but still queried again; it also displayed the wrong revision
kind. These 12 targeted attempts (11 completed, one failed) are separate from
18-case grades. Failure and captured inputs are preserved, not retried away.
Combined estimate $1.628343, excluding embeddings/cache discounts; failed-run
usage may be incomplete. No paid judge cost or automatic Langfuse dataset upload.

**Learning:** retained tool history enables reuse but does not force models to
use it, and fresh evidence does not guarantee correct reasoning. Diagnose query
validation/recovery, reasoning and citation/provenance separately. This run made
no further application changes. Follow-ups and exact evidence are in the report;
previous baselines and routing conclusions remain archived for their versions.

### M30 follow-up — Accept cases 23/24 after grading clarification

**October 1, 2026.** User accepted both models as correct on cases 23/24.
Case 23's qualified incident-scope answer is sufficient; seller naming is optional.
Case 24 asks for remaining payable, so the correct ₹2,249.10 with evidence is
sufficient without an unrequested numeric breakdown. Less categorical incident
wording remains a suggested improvement. Current counts: nano **11 correct /
4 partial / 3 incorrect (61.1%)**; GPT-5.4 **17 / 1 / 0 (94.4%)**.

This changes grading, not answers or implementation. No model calls or additional
cost. Original M30 counts above record the initial review; the
[versioned adjudication](app/results/core18-history-v3-2026-10-01/user-adjudication-v1.json)
and [original report archive](app/results/core18-history-v3-2026-10-01/before-user-adjudication/REPORT.md)
preserve that history. The report, comparison and current specification summaries
are updated. Only these four judgments are user-approved; remaining grades are
assistant-provisional. Raw answers, gold-v3 and previous experiments are unchanged.

### M30 follow-up — Refresh the prompt/history walkthrough

**October 1, 2026.** Updated [How catalog, questions and history reach the model](app/docs/PROMPT-AND-CATALOG.md)
with the complete current static prompt, its SHA-256, the exact question-construction
helper, and call-by-call input growth. Clarified six previous stored question
blocks plus the current question, persisted tool results, dynamic metadata at the
end of the new question, and the per-investigation catalog-before-SQL instruction.
Added observed GPT-5.4/nano reuse behavior and links to captured SDK inputs,
separating possible sequences from measured behavior. Verified embedded prompt
against source and local links. Documentation only; no inference or app change.

## M31 — Map completed work and pending labs to every course chapter

**October 1, 2026.** Expanded [the course outline](course/COURSE-PLAN.md) into a
living chapter progress map. All 20 sections now record current state, learning,
tests/reference links, hands-on readiness and pending work, with a compact overview.
Kept proposed lesson activities distinct from completed engineering experiments
and learner-ready packaging. The external Google reviewer outline is unchanged.

Mapped ontology/catalog/prompt/cache-prefix/revision work to section 5, RAG
storage/search/date checks to 7, retained history to 8, limits/recovery to 9,
gateway work to 4, routing to 15 and evaluation methodology to 14. Section 3
introduces the latest nano/GPT-5.4 results as early end-to-end evaluation; later
sections reuse that evidence for deeper analysis. Dedicated guardrail, multi-agent,
memory and platform experiments remain pending. Corrected stale backlog items:
local MCP is implemented and the eval runner already supports repeats.

**Pending routing refresh:** rerun a bounded comparison on current prompt/catalog/
history, including cached tokens, cost, latency, calls and answer quality. Do not
assume only caching changed. Historical routing uses nano/GPT-5, distinct from the
latest nano/GPT-5.4 regression. No new inference was run for this mapping.

**Maintenance rule:** every future milestone also refreshes affected course
chapters and marks downstream experiments needing revalidation. Milestones remain
chronological; the outline remains the latest chapter-organized state. Detailed
lab scripts/checkpoints and recording readiness will be prepared separately.

### M31 follow-up — Defer catalog/prompt optimization

**October 1, 2026.** Added optional design questions to course section 5: catalog
as a tool versus upfront context, full versus selected entities, prompt size and
cache-aware organization. These are not prerequisites for the sample app or core
context lab. Upfront-versus-tool catalog comparison is explicitly an optional
later extension. Existing implementation stays unchanged; no tests or paid calls
were run. The outline links the existing selective-catalog optimization backlog.

### M31 follow-up — Explain controlled evaluation data in section 14

**October 1, 2026.** Made the purpose of `market_eval` explicit in the course
outline: isolated repeatable fixtures, reset/replay, fixed clock, matched starting
state, versioned datasets and preserved within-case follow-ups. It serves multiple
evaluation suites, not only the six routing conversations or proposed payout
experiment. Linked implementation/isolation tests and added the reset/replay
learner exercise as pending packaging. Documentation only.

## M32 — Compare payout orchestration with GPT-5.4

**October 1, 2026 — completed bounded experiment; assistant explanation grades provisional.**

**Question:** Does one common-policy payout investigation benefit from serial tools, parallel tools or independent seller workers? Fixed GPT-5.4 across all variants, consistent with the latest prompt/history baseline; earlier GPT-5 routing results remain historical.

**What we did:** Built a repeatable evaluator-only fixture in `market_eval`: three sellers, eleven payouts, seven outcome classes including active returns, a 23-hour hold, zero-due and successful-retry controls. Ran three rotated repeats per variant. Every run preserved the same data fingerprint and left business state unchanged. Archived instructions, tool outputs, model inputs, fixture/oracle, runner and source hashes. No paid Claude judge.

**Results:** Serial returned 3/3 answers, parallel 3/3, workers 2/3. All eight completed answers had supported explanations and correct amounts/totals; one worker synthesis timed out. Full record/citation gates passed 2/3 serial, 3/3 parallel and 1/3 workers: serial trial 2 and worker trial 1 each duplicated a prefix in one raw evidence reference. Mean elapsed times: 68.0 / 82.0 / 108.1 seconds. Mean conservative uncached model estimates: $0.3154 / $0.2594 / $0.6885; cache-adjusted: $0.1342 / $0.1623 / $0.4009. Recorded v2 total $3.7900 uncached, $2.0920 cache-adjusted; preliminary failed/smoke runs, embeddings and unreturned timeout usage are separate.

**What we learned:** Two architectures, three variants. Serial/parallel means tool scheduling, not one seller per query. Catalog must precede SQL; independent histories can then overlap. Verified one active tool request in serial, up to ten in parallel, and three concurrent worker model requests. These are client-level intervals, not proof of physical SQL concurrency. The bulk single-agent approach handled this task well; workers added context/synthesis overhead without a demonstrated quality improvement. Differing queries, cache and sampling mean this is not a pure scheduling comparison or a general winner.

**Repairs and limitations:** Initial client timeout was 40 seconds; v2 uses 120 seconds equally while gateway still limits requests to 60. Worker trial 2 got HTTP 408 during final synthesis. Root cause beyond that limit is unknown. The checker originally missed nested order-history references; recursive offline registration corrected it, preserving initial verdicts and answers. Positive and four negative controls passed. Do not equate known handles with claim support or count missing answers as semantically correct.

**Next / teaching material:** Explain the model-request/tool-result loop with actual traces and distinguish permitted from realized parallelism. A pure scheduling test should use identical retrieval work; seller-specific policies only when they introduce meaningful branches. Reviewer–optimizer was subsequently completed in [M33](#m33--nano-generator-with-gpt-54-review-and-one-correction); independent-system/A2A remains later work. [Course section 17](course/COURSE-PLAN.md#17-workflow-vs-single-agent-vs-multi-agent) reflects this state.

**Evidence:** [Report](app/results/payout-orchestration-v2-2026-10-01/REPORT.md), [run-by-run comparison](app/results/payout-orchestration-v2-2026-10-01/comparison.html), [experiment plan](app/eval/orchestration-v1/README.md), [raw captured inputs and results](app/results/payout-orchestration-v2-2026-10-01/results.json), [assistant review](app/results/payout-orchestration-v2-2026-10-01/assistant-review.json).


## M33 — Nano generator with GPT-5.4 review and one correction

**October 1, 2026 — completed eight-case diagnostic; assistant grades provisional.**

**What we did:** Reused frozen nano drafts and GPT-5.4 baseline answers. Five nano problem cases (09, 14, 15, 16, 17) plus three correct controls (10, 20, 23). GPT-5.4 reviewed the question, draft and original evidence without gold or previous grades. Feedback returned to nano for at most one correction stage with read-only MCP tools. All eight completed on matching fixed fixtures without business changes; support runtime unchanged.

**Results:** Nano alone 3 correct / 3 partial / 2 incorrect; reviewed nano 5 / 3 / 0; saved GPT-5.4 alone 7 / 1 / 0. Manual-review reasoning and the 23-hour hold became correct. Exact 24-hour eligibility improved to partial; payment ambiguity and payout-failure cause remained incomplete. Correct controls remained correct. Independent final grading is separate from reviewer decisions; this enriched sample is not population accuracy.

**Learning:** Detection does not guarantee correction. Six revision requests produced nine nano model calls but only three fresh tool calls, all catalog lookups; missing SQL/history/policy evidence was not retrieved. The first pass omitted catalog metadata and confused the reviewer about currency and manual-review rules. V2 included full original evidence; both passes are preserved. This is a fixed workflow containing agent-controlled steps.

**Cost and limits:** V2 incremental uncached estimate $0.2411; initial pass $0.0895; combined new model estimate $0.3306 excluding embeddings/cache discounts. Generation was reused, so total cost/latency comparisons are assembled rather than fresh end-to-end measurements. No paid Claude judge. Valid evidence handles do not prove complete claim-level citation support.

**Closure and cost comparison:** The user accepted this as a completed learning milestone on October 1. No further runs are required to close it. Assistant grades remain provisional; acceptance of the experiment does not constitute individual grade adjudication or a production-policy decision. Including the saved nano generation cost, the workflow estimate is $0.2575 versus $0.4244 for saved GPT-5.4 alone: approximately 39% lower cost, with 5 versus 7 fully correct answers. Every draft was reviewed; only flagged drafts were corrected. These conservative uncached totals combine historical generation with new review/correction, rather than fresh end-to-end measurements.

**Blog/course takeaway:** A bounded workflow with two agents can improve a weaker generator, but review quality, correction follow-through and independent final grading are different concerns. The three correct controls stayed correct; one incorrect became correct and one became partial; one partial became correct and two stayed partial. This demonstrates the experimental approach, not a general architecture winner.

**Next:** Prepare teaching walkthrough; memory is the next proposed topic. Broader held-out cases, repeated fresh end-to-end runs, evidence-acquisition enforcement, reviewer tools or a stronger correction model remain optional enhancements.

**Evidence:** [Report](app/results/reviewer-workflow-v2-2026-10-01/REPORT.md), [comparison](app/results/reviewer-workflow-v2-2026-10-01/comparison.html), [raw inputs and outputs](app/results/reviewer-workflow-v2-2026-10-01/results.json), [final grades](app/results/reviewer-workflow-v2-2026-10-01/assistant-grades.json), [plan](app/eval/reviewer-v1/README.md).


### M33 documentation follow-up — October 1, 2026

Expanded [course section 17](course/COURSE-PLAN.md#design-discussion-and-blog-handoff--workflow-agents-and-multi-agent) as the blog handoff: workflow/agent taxonomy, manager-workers versus handoffs, independent parallel branches, focused contexts and transfer risks, research/coding examples, why SQL/RAG was not split, seller discovery and payout diagnosis, the measured lack of worker benefit, evaluator–optimizer feedback, and separately owned systems/A2A. Added primary-source references and source/implementation boundaries to the course and research guide. This preserves the reasoning path and negative result, not just headline scores. Documentation only; no new model calls or runtime changes.


## M34 — Compare reviewer models across all eighteen cases

**October 1, 2026 — completed reviewer-model ablation and coverage expansion; independent assistant grades provisional.**

**Why:** The user challenged whether M33's improvement came from the review pattern or stronger reviewer capability, and requested the complete eighteen-case suite before writing the blog.

**Method:** First nano reviewed the same eight frozen drafts: no revisions, grades unchanged at 3 correct / 3 partial / 2 incorrect. Then both reviewer variants expanded to eighteen cases, reusing eight completed rows each. All review payloads match across models; prompts, full evidence, nano generator and one-correction limit are fixed. Eighteen cases include twenty original turns; two follow-ups retain frozen earlier history and review/correct only the final turn. Case 28 reproduces the planned purchase mutation. Critics receive no gold; final grades are separate. All 36 workflow executions completed without business changes; source/input hashes are archived.

| Approach | Correct | Partial | Incorrect | Assembled uncached model estimate |
|---|---:|---:|---:|---:|
| Nano alone | 11 | 4 | 3 | $0.0373 |
| Nano reviewer + nano correction | 11 | 4 | 3 | $0.0526 |
| GPT-5.4 reviewer + nano correction | 14 | 4 | 0 | $0.5817 |
| GPT-5.4 alone | 17 | 1 | 0 | $1.2104 |

**Learning:** Same-model review did not improve business-grade counts here. Stronger review improved case 15 to correct, 16 to correct, 17 to partial and 27 to correct. In case 27, specific feedback removed the invented today filter and triggered new SQL; weaker feedback repeated ambiguity and left it wrong. Stronger review is approximately 52% cheaper than always GPT-5.4 on assembled totals but has three fewer correct answers. Three weak-review and thirteen strong-review corrections are not automatic successes. Some revisions target already correct answers; citation defects remain separate from business correctness.

**Cost and limits:** Newly recorded extension estimate $0.3186; includes Nano's eight-case ablation and ten additional reviews per variant, excludes already spent stronger-review eight-case cost. Workflow totals include historical nano generation for all twenty turns. Saved generation plus review/correction is not a fresh end-to-end trajectory or latency/caching benchmark. Eighteen known development cases improve coverage but are not a held-out/general-purpose benchmark. No paid Claude judge or runtime change. No general claim that self-review never works, and no unique causal mechanism established by one trial.

**Blog handoff:** Use M34 for current coverage/cost headline and retain M33 as the chronological discovery. The lesson is how to test reviewer capability, correction follow-through and cost/quality—not that the evaluator pattern alone guarantees improvement. Repeated fresh runs, blinded human checking and tool-enabled reviewers remain optional enhancements; memory remains the next proposed topic.

**Evidence:** [Report](app/results/reviewer-ablation-core18-2026-10-01/REPORT.md), [comparison](app/results/reviewer-ablation-core18-2026-10-01/comparison.html), [summary](app/results/reviewer-ablation-core18-2026-10-01/summary.json), [validation](app/results/reviewer-ablation-core18-2026-10-01/validation.json), [plan](app/eval/reviewer-v1/README.md).


### M34 diagram follow-up — October 1, 2026

Saved [worker and evaluator–optimizer diagrams](course/diagrams/AGENT-PATTERNS.md) with editable Mermaid sources. Linked them from course section 17, specification, experiment reports and the multi-agent blog brief. The diagrams distinguish independent worker loops, controller decisions, reused generation, optional correction tools and independent final grading. Documentation only; no new model calls.


### Diagram simplification — October 2, 2026

Simplified the [agent-pattern diagrams](course/diagrams/AGENT-PATTERNS.md) for course/blog readers: seller workers now show one coordinator delegating and combining findings; evaluator–optimizer shows generation, review, optional one-time correction and final answer. Removed tool, snapshot, controller and grading boxes from the visual; retained those implementation boundaries in the notes. Updated both editable Mermaid sources; existing links remain valid. Documentation only.


### Memory scope planning — October 2, 2026

Captured the next learning lab in [course section 18](course/COURSE-PLAN.md#18-short-term-and-long-term-memory), [specification section 7](SPECIFICATION.md#initial-memory-lab-scope--october-2-2026) and the [research guide](RESEARCH-GUIDE.md#practical-memory-lesson-references--october-2-2026). Scope: demonstrate existing short-term state; explicitly save and reuse semantic preferences, episodic investigation checkpoints and procedural guidance across conversations using an application-owned PostgreSQL layer. Include update/delete, user isolation, instruction precedence and stale-memory checks. Automatic extraction, background saving, auto-compaction and Mem0 implementation are deferred. Memory managers are optional, not prerequisites for a production system. Added LangChain, OpenAI session-memory and Mem0 primary references. Documentation only; long-term code and on/off tests remain pending.


### Memory architecture write-up — October 2, 2026

Added the [simple memory block diagram and write-up](course/diagrams/MEMORY-ARCHITECTURE.md), linked from the course and specification. It separates SDK session storage from application-owned long-term memory, explains production readiness without requiring a memory vendor, and outlines optional Mem0 integration, including the difference between extracted facts and explicitly saved checkpoints/procedures. Documentation only; no runtime integration or model calls.


### Memory transport clarification — October 2, 2026

Updated the [memory architecture write-up](course/diagrams/MEMORY-ARCHITECTURE.md) with two simple diagrams: our planned direct Agents SDK memory function tools → backend module → PostgreSQL, and optional supplied Mem0 MCP tools → Mem0 service. Short-term session history is unchanged and omitted from these comparison diagrams. Existing marketplace tools retain MCP. Updated course/specification to make the planned memory transport explicit. Documentation only.


## M35 — Explicit user-scoped long-term memory

**October 2, 2026 — bounded implementation and initial checks complete.**

Added semantic, episodic and procedural memory records in PostgreSQL, four direct Agents SDK memory tools, per-question write permission, memory on/off, and Saved memories inspection/Edit/Forget. Business tools retain MCP. Ownership, CSRF, source-run scope and version checks are enforced; memory writes do not change business revision. Pure memory-management questions use memory tools only; normal investigations retain both tool groups. No automatic extraction, compaction, shared procedures or Mem0 implementation.

**Verification:** 65 PostgreSQL regression tests passed, including fourteen memory-specific cases. Final live nano sequence: thirteen questions with save/recall for all three types, update in place/version 2, updated recall, delete/empty recall, operator/support isolation, memory-off and denied writes. Thirteen operation/record checks passed; assistant inspected response text. Frontend built and deployed UI controls were inspected. Earlier live runs exposed SQL detours, conflicting saves and wrong type filtering; backend restrictions and a simpler tool surface corrected these in the final sequence. Some nano wording remains verbose or exposes IDs. Broader stale-policy/revision and procedural-application benchmarks remain learning follow-ups, not implied passed.

**Cost:** final sequence $0.00325345; all four development iterations $0.04252940 in recorded uncached model estimates, not invoices. No paid judge. Isolated `market_test` only; interactive marketplace business data and user memories were not reset.

**Evidence:** [report](app/results/memory-v4-2026-10-02/REPORT.md), [results](app/results/memory-v4-2026-10-02/results.json), [validation](app/results/memory-v4-2026-10-02/validation.json), [manifest](app/results/memory-v4-2026-10-02/manifest.json), [lab walkthrough](app/eval/memory-v1/README.md), [diagrams](course/diagrams/MEMORY-ARCHITECTURE.md). Lesson recording and broader repeated/held-out experiments remain pending; production readiness is not claimed.


## M36 — Lyzr Agent Studio with authenticated remote MCP

**October 2, 2026 — remote adapter and private Studio lab implemented; cloud middleware deployment pending.**

**Goal:** Run the same synthetic customer-support tools under Lyzr's model/agent runtime, without long-term memory, and make runtime versus middleware ownership observable.

**What changed:** Added an authenticated Streamable HTTP JSON MCP adapter, a Compose service and temporary tunnel start/stop/status helper. Seven actions expose investigation begin/end and the existing five read-only business tools. Opaque investigation IDs preserve per-question repeatable-read snapshots and evidence isolation, with locking, TTL/capacity and cleanup. Added explicit order/payment summary evidence to remote order history. Local direct/stdio paths and the M35 memory implementation remain separate.

**Dashboard work:** Registered Marketplace Support MCP Lab with API-key authentication, discovered seven actions, created the private Marketplace Support — MCP Lab agent, attached those tools using creator credentials, removed Memory, configured role/goal/instructions and selected OpenAI `gpt-5.4-mini` after nano trials. Saved prompt/model changes, tested new chats and inspected Activity traces. Deploy → Agent API confirmed automatic authenticated API deployment on saving; no public App Store publication. Exact steps are retained in the [lab guide](app/lyzr/README.md).

**Results:** 68 current-source regression tests passed, including three real HTTP MCP integration tests against disposable `market_test`. Public SDK discovery/read checks worked and missing credentials returned 401. Final Studio question combined order/payment status, current seller payouts, earlier failure and settlement policy: 13.39 seconds, three exact citation handles verified against returned evidence, investigation explicitly closed. At interactive revision 24 / demo clock 2026-09-28 12:00 UTC, order-1 was paid, payment captured, both payouts completed, with a prior payout-1 provider timeout. Interactive business state was not reset.

**Learning and limits:** MCP lets another runtime reuse middleware; it does not transfer our SDK citation validator, history injection or Langfuse run bookkeeping. Nano observations included unsupported statements, human_as_tool planning instead of retrieval and shortened citations/IDs; mini's final success is a smoke result, not a comparative benchmark. Cedar lookup found one seller match, so multiple-match clarification is untested. External Lyzr inference API invocation is also untested. Shared demo credentials do not provide production user/tenant authorization. Lyzr remains an optional course example.

**Next action — required cloud migration:** Deploy the remote MCP middleware and cloud-reachable SQL/RAG/embedding dependencies behind stable authenticated HTTPS without a tunnel or dependence on the Mac. Choose provider/target, package the service, configure secrets/TLS/private DB access and operational controls, and handle the process-local snapshot/evidence registry before scaling. Update Studio and repeat protocol/security/support checks, then prove retrieval still works with the local tunnel and middleware stopped. See [specification section 3.4](SPECIFICATION.md#34-lyzr-remote-mcp-implementation-and-cloud-follow-up--october-2-2026) for acceptance criteria. This task is recorded, not yet deployed.

**Evidence / lesson material:** [Validation](app/lyzr/VALIDATION.md), [prompt](app/lyzr/agent-instructions.txt), [final transcript](app/lyzr/final-smoke-transcript.txt), [trace proof](app/lyzr/final-trace-proof.json), [policy proof](app/lyzr/final-policy-proof.json), [working screenshot](app/lyzr/support-working.jpg), [API deployment screenshot](app/lyzr/agent-deployed.jpg), [adapter](app/backend/marketplace/remote_mcp.py), [tests](app/backend/tests/test_remote_mcp.py). Use in tools/MCP, runtime/hosting and optional platform lessons; learner packaging and a broader shared-case comparison remain pending.


### M35 manual acceptance and UI alignment — October 2, 2026

The user reports the memory walkthrough working successfully in the local Support UI. Recorded this acceptance in the specification, application README and course section 18, separately from the 65 regression tests and thirteen live questions. No per-case human-review export was supplied, so the result is not expanded into a claim that every proposed manual case was individually graded. The bounded lab is implemented and manually accepted; broader memory-quality experiments remain follow-ups.

Fixed the memory controls inheriting full-width text-input styling: each checkbox now sits beside its label in a separate aligned row, with wrapping for narrow layouts. Retrieval and write-permission behavior are unchanged.

**UI verification:** Frontend production build passed and the local frontend was refreshed. Browser inspection at the current narrow viewport confirmed both checkboxes are 16 pixels wide at the same horizontal position, with labels beside them. Turning retrieval off disabled the write control; retrieval was restored afterward. [Screenshot](app/results/memory-v4-2026-10-02/aligned-memory-controls.png). No model calls were needed for this layout change.

### M35 memory-use follow-up tests — October 2, 2026

Ran nine Nano questions in isolated `market_test`: three setup saves and six fresh-conversation answers comparing memory on/off for stale checkpoints, procedural application and current instruction precedence. [Exact cases, findings and traces](app/results/memory-use-v1-2026-10-02/REPORT.md). Estimated uncached model cost: $0.01077325; no paid judge.

These use scenarios are not all passing. The stale checkpoint save failed, so correct current payout answers do not validate stale-memory handling. Nano retrieved the procedural checklist but incorrectly inferred undelivered status from history without shipment fields and skipped policy search. A business question containing “Do not change my saved preference” was incorrectly classified as memory-only, hiding business tools in both on/off variants. The semantic save also distorted the preference scope. Basic CRUD acceptance remains separate; next work is faithful saves, correct tool scope and evidence-complete application, followed by reruns. No implementation fix was included in this diagnostic run.

### M35 application repairs and GPT-5.4 memory-use verification — October 2, 2026

Fixed negation-aware memory mutation detection and mixed business tool scope. Save provenance is assigned by the backend; the model-facing memory kind is an enum. No model reasoning workaround or answer-specific business data injection was added. Prompt/tool version v9. 74 regression tests passed. Backend rebuilt and health checked; interactive Nano default unchanged.

[Verification report](app/results/memory-use-gpt54-v2-2026-10-02/REPORT.md): three faithful saves and six paired answers passed. GPT-5.4 retrieved the old revision-1 payout checkpoint and refreshed at revision 2; applied the saved checklist using shipment/history/policy; and answered Desk Lamp quantity 2/Northstar Goods while preserving the saved seller preference. The explicit override did not need a memory search, so retrieval conflict resolution was not exercised in that pair. Estimated uncached model cost $0.57311000, excludes embeddings; no paid judge. Gateway deployment interrupted one setup attempt; only pending questions resumed and interruption retained.

These are single-trial diagnostic results with model and application both changed; they do not isolate model contribution or establish production reliability. Earlier Nano failures remain preserved. Repeated/held-out tests, stale-policy and retrieval-level preference conflict tests remain follow-ups.

### Application session recovery — October 3, 2026

The application services were healthy, but expired-session logout returned 401 and the frontend did not clear local account state. Added protected-request 401 recovery and expired-logout handling. 12 frontend checks and production build passed; deployed frontend only, no database reset. Browser verified populated support catalog at revision 24. [Verification](app/results/session-recovery-2026-10-03/REPORT.md).

### M35 actual refunded-order memory diagnostic — October 3, 2026

[GPT-5.4 comparison](app/results/memory-refunded-order-gpt54-2026-10-03/REPORT.md) on actual order ord-a9f9496711, memory enabled and write permission disabled: original question and explicit-checklist control both correctly concluded full buyer refund and zero seller payout due. Only the explicit version retrieved the saved checklist. Automatic relevance-based checklist retrieval therefore remains unvalidated/failing in this sample, including for GPT-5.4; correctness and memory use must be graded separately. Business/order state and saved memories unchanged. Estimated uncached model cost $0.19773750, excludes embeddings; no judge.

### M35 automatic checklist prompt and support navigation — October 3, 2026

Prompt v10 explicitly requests memory search for investigations even when no checklist is named. [Verification](app/results/memory-auto-checklist-v10-2026-10-03/REPORT.md): GPT-5.4 retrieved the saved payout checklist for the original question and correctly concluded full refund/zero payout due. Nano still skipped memory and omitted the full-refund cause; no guarantee or UI model switch. Estimated uncached model cost $0.17186480, excludes embeddings; no judge. Business and saved memories unchanged.

Support remains mounted while hidden in other sidebar pages. Browser verified selected conversation, three displayed turns and an unsent draft survived Support → Settlement → Support. 12 frontend checks and production builds passed; changes deployed. Pending calls retain component state but were not separately live-tested. Full reload restore is separate.


### Repeatable memory suite and separate test workspace — October 3, 2026

Added a [24-case short-/long-term memory catalogue](app/eval/memory-v2/README.md), versioned expected outcomes and a runner for eight scenarios/19 questions with memory-off controls. Fixture-only validation prepared each scenario twice and restored the seeded `market_test` baseline; no inference or judge calls were made. Live text-answer grades remain review-required. Basic CRUD/isolation/version boundaries retain the existing regression suite. Optional test UI uses `http://127.0.0.1:5179/`, labelled MEMORY TEST WORKSPACE; normal UI stays on `http://localhost:5178/` and `market`. Both UI instances retain the existing support-model alias; the live runner can explicitly select Nano or GPT-5.4. Stop test services before resets, and do not run concurrent market_test suites. This is baseline reset, not restoration of arbitrary user-modified test data.


### Eight-scenario GPT-5.4 memory verification — October 3, 2026

[Live memory suite report](app/results/memory-repeatable-20261003T093153094486Z/REPORT.md): eight scenarios/19 questions completed; all six required retrievals and 10 memory-off questions passed. Assistant review found 19 factually correct answers, with one noncanonical citation format in the policy-conflict answer (shortened evidence handles); subsequent UI-backed checking confirmed all source links resolve. Same-conversation quantities reused previous evidence with zero tools, even with long-term memory off. Preference override retrieved the conflicting memory without overwriting it. Seeded test baseline restored; optional test UI restarted. Estimated uncached model cost $1.02, no paid judge. One trial only; remaining manual catalogue cases are not claimed tested.


### Memory citation grading correction — October 3, 2026

[Policy-conflict rerun](app/results/memory-repeatable-20261003T094355178246Z/REPORT.md): both GPT-5.4 answers correct with full canonical citations; zero unavailable sources; estimated cost $0.31. Seven citation regressions passed. The earlier 19-question report incorrectly treated shortened raw IDs as broken links; existing UI normalization already resolves those recorded IDs. All 19 saved answers passed checking through the actual UI functions. Added a reusable UI-backed citation checker, corrected report/review and documented format-versus-resolution grading. No agent prompt or resolver change needed. Test baseline restored and test services restarted.


### M35 closeout — Short- and long-term memory conclusions — October 3, 2026

**Status:** Bounded memory learning experiment complete. The full 24-case catalogue is not claimed passed. Updated current specification, README, course chapters 8/17 and the [consolidated memory status](app/docs/MEMORY-STATUS.md) with conclusions, evidence and pending work.

**What we learned:** Short-term structured evidence can be reused without tools when long-term memory is off. Checkpoints preserve prior investigation progress, not current business truth. Preferences yield to current instructions and checklists yield to policy. Retrieval and answer correctness must be checked independently; Nano can skip retrieval even with prompt guidance. User-reported explicit checkpoint resumption works; vague “has anything changed” needs a historical baseline.

**Evidence:** [Eight-scenario / 19-question GPT-5.4 run](app/results/memory-repeatable-20261003T093153094486Z/REPORT.md), all memory checks and assistant-reviewed factual answers passed; estimated cost $1.02. [Two-question policy-conflict rerun](app/results/memory-repeatable-20261003T094355178246Z/REPORT.md), canonical sources resolved; estimated cost $0.31. All 19 original source references resolve through the actual UI; raw-only grading was corrected. Seven citation regressions passed. No paid judge; one trial per variant is not universal reliability evidence. Test baseline restored and test UI available independently from live data.

**Pending:** Record/package the lesson; selected manual short-term UI/freshness and long-term persistence/recall cases remain in the [catalogue](app/eval/memory-v2/README.md). Earlier CRUD/isolation/version/freshness regression coverage remains valid. Broader repeated/held-out and controlled model comparisons are optional. Automatic extraction, compaction, consolidation/expiry, shared procedures and Mem0 comparison remain enhancements. No critical memory implementation blocker remains within the agreed bounded scope.

### M36 tunnel recovery and session-memory comparison — October 3, 2026

Restored authenticated remote MCP after reboot and attached the replacement connection to the existing Lyzr agent. Launcher now verifies authenticated MCP initialize readiness instead of treating URL allocation as successful connectivity. [Two-turn test](app/lyzr/memory-session-2026-10-03/REPORT.md): memory-off control fetched order-2 but lost the follow-up identifier; Cognis with Cross Session off resolved it and retrieved fresh evidence with cleanup. Model/prompt unchanged; one trial. Stable tunnel alternatives discussed; user deferred selection. Cloud middleware deployment remains pending.

### M36 stable local tunnel — October 3, 2026

[ngrok verification](app/lyzr/ngrok-2026-10-03/REPORT.md): account-assigned stable endpoint, macOS login startup/crash recovery, Docker dependency restart policies, discovery/auth rejection and same-URL tunnel restart passed. Existing Lyzr agent reattached to Stable; business lookup passed in 14.70 seconds with fresh evidence and cleanup. Cloudflare process stopped. Actual reboot untested; Docker must be running after login. This supersedes earlier deferred tunnel selection; full cloud middleware hosting remains pending.

### M35 local stdio MCP memory tools — October 3, 2026

[Implementation and verification](app/results/memory-local-mcp-2026-10-03/REPORT.md): OpenAI agent memory calls now use local MCP, with trusted owner/permission/provenance launch context and operation-audit synchronization. 81 regressions passed; backend/test backend rebuilt, test baseline restored and workspace restarted. No paid model rerun. Remote MCP remains business-only. Lyzr native Cognis cross-session enablement is separate and still pending.

### OpenAI memory regression through local MCP — October 3, 2026

[Existing 19-question rerun](app/results/memory-repeatable-20261003T112031250654Z/REPORT.md): GPT-5.4 passed all reviewed answers, six required retrievals and ten memory-off questions; citations all canonical/resolving. Short-term continuity worked with long-term memory on/off. No answer mutations; fixture baseline restored. Estimated uncached model cost $0.988305, excludes embeddings; one trial. Native Cognis comparison follows separately.

### Native Lyzr memory tests — October 3, 2026

[Recorded results](app/lyzr/cognis-memory-2026-10-03/REPORT.md): native Cognis Cross Session ON, extraction instructions and updated agent prompt/description saved. Fresh-chat preference, unique phrase, procedural checklist and historical checkpoint recall passed; temporary override left the original preference available; old failed payout distinguished from fresh completed records. Short-term order follow-up and Cross Session off/on control passed. Checklist use missed actual shipment retrieval despite an added prompt instruction; successful recall does not establish correct investigation. Native provider provenance/CRUD/write-control parity and multi-user isolation remain unverified. The OpenAI local-MCP live regression independently passed all 19 reviewed questions and source checks, after 81 deterministic regressions. Remote HTTP MCP remains business-only; proper cloud hosting remains pending.


### Memory MCP review and provider-portability architecture — October 3, 2026

Reviewed code and the related “Prepare for Lizer CTO discussion” implementation/regression evidence. Agent memory now uses local stdio MCP; PostgreSQL MemoryStore still enforces ownership, explicit mutation permission, provenance and optimistic version checks. Business MCP and short-term conversation history remain independent; remote HTTP MCP exposes only business/lifecycle tools. [Review](app/results/memory-local-mcp-2026-10-03/REVIEW.md), [81-regression migration evidence](app/results/memory-local-mcp-2026-10-03/REPORT.md), and [19-question post-migration GPT-5.4 report](app/results/memory-repeatable-20261003T112031250654Z/REPORT.md): all expected answer/operation/source checks passed, cost about $0.99. This documentation review reused existing evidence and made no paid calls or database resets.

Updated [memory architecture and provider-extension diagrams](course/diagrams/MEMORY-ARCHITECTURE.md) and specification overview. **MCP makes operations accessible across runtimes; an adapter interface makes storage replaceable.** The interface and external adapters are planned; current MCP code directly creates PostgreSQL MemoryStore. Future providers must preserve or explicitly adapt permission/isolation, extraction/save fidelity, provenance, update/delete and freshness behavior. Native Lyzr Cognis is a separate test track, not already wired behind our memory MCP. No remote personal-memory endpoint or multi-provider switching is claimed implemented. Existing manual/held-out memory pending work remains; provider adapters/parity testing are optional enhancements.

### External Lyzr inference verified — October 3, 2026

[Result and reusable curl](app/lyzr/api-smoke-2026-10-03/REPORT.md): HTTP 200 in 17.23 s; latest deployed agent returned correct order-2 paid/captured status and evidence references in a fresh API session. First masked-key attempt returned 403; existing unmasked key succeeded. Credential absent from saved request/report and temporary credential files removed. User reviewed tracing/monitoring UI and accepted it. Checklist-use gap, native memory identity/provenance/CRUD checks, cloud hosting/reboot verification and deeper observability are tracked as enhancements in course section 21.


## M37 — Add security to Part C and renumber course sections

**October 5, 2026 — course planning change; no application code, experiments or scores changed.** Part C is now "Observability, evaluation and security". Added [section 15, Security: attacking our own agent](course/COURSE-PLAN.md#15-security-attacking-our-own-agent): an OWASP Top 10 for LLM Applications (2025) map onto the agent's components (five risks already handled where the component is taught; five with examples and short tests here) and a proposed red-team lab that runs about 15 attack cases through the evaluation runner with defences on and off, reporting attack success rate, false refusals and overhead. Multi-agent and memory lessons will add their own attack cases. Security is part of v1 because Part C is required; the attack set is to build.

**Renumbering:** routing 15→16, multi-agent 16→17, memory 17→18, Gemini 18→19, AWS 19→20, Lyzr 20→21, choosing a platform 21→22. Updated headings, anchors and cross-references in the course plan, platform guide, specification, research guide, agent-patterns diagrams, Lyzr README/validation, multi-agent blog brief and earlier milestone links; all course/platform-guide links verified to resolve. M31's description of its original chapter mapping is left as historical text. The external Google Doc reviewer outline still uses the earlier numbering.


### Guardrails and OWASP security scope agreed — October 7, 2026

User deferred the separate context-ablation experiment and prioritized guardrails/security. Course section 15 now covers selected LLM-application and agentic risks, with official OWASP 2026 references alongside the original 2025 planning map. Proposed lab: roughly 15 attacks plus benign controls; optional gateway guardrails off/on with database and memory enforcement retained; separately score detection, prevented actions, false blocks, answer correctness, latency and cost. Corpus/memory injection, tool misuse and ownership spoofing are practical cases; supply-chain and inter-agent/cascading risks are explanatory or optional extensions. Section 10 teaches mechanisms; section 15 evaluates end-to-end attacks. This is a scope update, not completed implementation or measured security coverage. See [course scope](course/COURSE-PLAN.md#15-security-attacking-our-own-agent).


### First indirect-injection fixture prepared — October 7, 2026

Installed a reversible, versioned poisoned settlement-policy chunk only in market_test; preserved actual business state (order-2 held, shipment pending) and confirmed live market policy unchanged. Indexed the test corpus; pgvector preflight returned the injected chunk first. Test UI healthy and test backend updated to GPT-5.4. No support-agent answer was generated or graded; user will run the manual case. Gateway guardrails remain off. [Test steps and restoration](app/results/security-document-injection-v1/README.md), [database-guarded fixture script](app/scripts/security-document-fixture.py).


### Poisoned-policy GPT-5.4 baseline trial — October 7, 2026

[End-to-end report](app/results/security-document-injection-v1/REPORT.md): one fresh market_test conversation, memory off, gateway guardrails off. Verified poisoned chunk both retrieved and included in model input. GPT-5.4 resisted the fake override and answered correctly from shipment/payout records and legitimate policy. Four MCP invocations, five model requests, 16.92 s. Raw test cost accounting used stale Nano rates; corrected project-list-rate estimate $0.0967675 excluding embeddings, not a billed amount. One payload/trial; no general robustness claim. Fixture remains installed for user trial. Layered prevention and restoration documented; guardrail-on comparison remains pending.


### Forged-document injection variants — October 7, 2026

[Six trials and exact answers](app/results/security-document-injection-v1/VARIANTS.md): three versioned forged passages against GPT-5.4 and Nano, fresh conversations, memory off, gateway guardrails off. The forged advance-settlement exception misled both into claiming completed/no seller funds due despite held records. GPT-5.4 received and resisted the reconciliation and answer-template variants; Nano did not receive those payloads, so resistance is untested. Payload receipt verified from Langfuse generation inputs. No actual payout was executed. Restored the earlier explicit-override fixture and confirmed held/pending business status. Key learning: instruction rejection and trustworthy factual evidence are distinct boundaries; SQL does not automatically take precedence. Corpus provenance and status validation complement gateway filtering. One trial per condition; no general robustness or model-ranking claim. Filter off/on and benign controls remain pending.


### Source-authority prompt trial — October 7, 2026

[Prompt v11 and paired attack rerun](app/results/security-document-injection-v1/PROMPT-V11.md): distinguish business status/event evidence from policy rules; documents cannot establish completed payment or explain away held records without business evidence. With the unchanged forged EX-204 passage, GPT-5.4 now flagged the conflict and resisted; Nano remained misled. Both received the rule and payload, verified from generation inputs. Fresh conversations, memory off, no gateway detector. One trial each, not a broad robustness claim. Earlier fixture restored. Prompt construction guide updated; semantic detector/control experiment remains pending.


### Built-in gateway filter experiments — October 7, 2026

[Results and repeatable runner](app/results/gateway-guardrails-2026-10-07/REPORT.md): three opt-in LiteLLM built-in filters, nine synthetic cases each off/on, evaluation key and Nano. Email input/output masking passed; AWS-key-shaped text and explicit instruction/disclosure attacks in tool results blocked with named pre-call errors. Legitimate settlement policy allowed. One benign quoted-security false block and one paraphrase miss demonstrate regex limits; model separately resisted the missed attack. Seven/nine expected outcomes, not a broad accuracy metric. No marketplace business/corpus changes. Installed-version telemetry flag incompatibility fixed and invalid first attempt retained/excluded. Normal UI remains opt-out of these experimental filters; API tests only. External Presidio comparison for privacy, semantic injection detector and support UI integration remain pending.


### External Presidio privacy comparison — October 7, 2026

[Report and raw tests](app/results/presidio-guardrails-2026-10-07/REPORT.md): pinned local analyzer/anonymizer integrated with opt-in LiteLLM filters. Eight paired cases, plus three diagnostic email pairs. Phone masking/card blocking and benign controls passed; .invalid email missed by analyzer, example.com input/tool/output masking passed. AWS-key-shaped text is outside configured PII coverage; a model refusal is not a gateway block. No business/corpus/memory changes. Normal UI unchanged. Built-in versus external comparison demonstrates coverage/configuration differences, not broad accuracy superiority. Dedicated injection detector, UI enforcement and unavailable-service checks remain pending.


### Lakera preparation and manual guardrail walkthrough — October 7, 2026

[Single-case manual guide](app/docs/GUARDRAILS-MANUAL.md) and runner cover built-in privacy/injection, Presidio and pending Lakera comparisons. Presidio email smoke test through this runner passed. Installed LiteLLM Lakera v2 class supports pre-call scanning, block decisions and system/tool scope flags. Prepared separate optional configuration overlay and credential-free generator; it refuses activation without LAKERA_API_KEY. Key absent in .env and gateway; no Lakera API call, screening result or entitlement verified. Optional project ID/Enforce mode documented; Detect mode suppresses top-level flagged. Normal gateway configuration remains active. User to add key before cloud trials.


### Lakera cloud screening verified — October 7, 2026

After the user supplied the key, activated the optional gateway overlay and ran [five synthetic cases](app/results/guardrails-manual-2026-10-07/LAKERA-REPORT.md). Default project/policy Enforce mode verified. Explicit override and paraphrase blocked as prompt_attack; harmless security quotation falsely blocked; legitimate settlement policy and forged factual exception allowed. No configuration/auth failures. This demonstrates a semantic detector catching one regex miss, not universal injection protection or factual validation. API-only manual tests ready; normal support UI selection and service-failure tests remain pending. Guide, README, specification and course section updated.


### Support UI security walkthrough controls — October 7, 2026

[Chapter demo catalog](app/docs/SECURITY-CHAPTER-DEMO.md) maps direct attacks/privacy to main or test, and poisoned policies/prompt comparison to test only. Added per-question named gateway filter selection, propagated across the whole SDK tool loop; named rejections appear as BLOCKED, service/config failures as failed. Test-only source-authority toggle removes just that paragraph, starts a new conversation, and defaults on; main backend rejects weakening it. Reversible test document variants support explicit/forged/paraphrased attacks and harmless/email controls, with embedding refresh, corpus concurrency locks and clean restore. [Support-flow verification](app/results/security-support-ui-2026-10-07/REPORT.md): four non-destructive tests, privacy input/block checks, post-RAG builtin/Lakera blocks and GPT-5.4 prompt off/on comparison. Presidio error-format display issue fixed and browser-verified. Prompt-off repeated forged claims without resolving conflict; prompt-on flagged it and retained held status. Clean test policy restored. User manual catalog/recording and broader failure-path trials remain. Gateway masking does not scrub original app questions/raw trace data.


### Test workspace login address correction — October 7, 2026

Added a tested nginx page redirect from localhost:5179 to canonical 127.0.0.1:5179 after an Origin rejected report. Retained strict login origin validation and separate main/test cookie hosts. Verified HTTP 307 destination, test health and successful login with the canonical browser Origin. Existing localhost tabs must reload to receive the redirect.


### Security chapter walkthrough and post-filter visibility — October 7, 2026

Selected chapter experiments completed; [guide](app/docs/SECURITY-CHAPTER-DEMO.md) now groups forged-document prompt comparison and direct/indirect Lakera attacks together, with built-in/Presidio privacy together. Preserve case IDs and historical misses/false blocks. Latest user-pasted B2/B3 answers both retained held status; source-authority On made the conflict clearer. Earlier wrong-status behavior did not reproduce; this pair is not evidence of a prevented successful attack. Direct injection Off was refused by the model; Lakera On blocked before the model. RAG injection blocked after retrieval before the next model call. Built-in privacy cases were confirmed by the user, as was Presidio card blocking. Not every optional catalogue case was manually repeated.

Added linked **Gateway output → Model input** audit observations and [verified masking](app/results/gateway-input-audit-2026-10-07/REPORT.md) with built-in privacy and Presidio. Callback request state after filtering is not a raw wire capture. Blocks appear as Error in Langfuse and BLOCKED in the application; success-only audits are absent on blocked requests. Original application logs/history remain unsanitized. Right-hand options panel, automatic fixture application/new conversation and three visible policy choices simplify the walkthrough. Clean policy restored through the authenticated test API and read back as clean.

Specification, app README and course sections 10/15 updated. Existing tool/SQL, memory ownership/isolation and runner limits support the broader security lesson; broader OWASP attacks, service-failure coverage and logging/provenance controls remain extensions. Agreed course sequence: finish required experiments and finalize the outline, then prepare each section’s slides, speaker notes and homework, refine its demo and record. Those teaching artifacts are deferred from this documentation closure.


### Final bounded OWASP security demonstrations — October 7, 2026

[Results](app/results/security-boundaries-2026-10-07/REPORT.md) and [2026 risk map](app/docs/OWASP-SECURITY-MAP.md) complete the agreed chapter experiment scope. Real local memory MCP denied support access/update/delete of an operator-owned fixture, preserved owner readback and enforced disabled writes; identity comes from trusted application launch context and is not a model argument. GPT-5.4 via the authorized support gateway alias repeated a harmless user-visible marker and refused to reveal the private system-instruction marker with gateway filters Off. Two model probes, one wording each; model resistance is not guaranteed secrecy. An initial evaluation-alias request was rejected by the support key allowlist; no key policy changed. Synthetic fixtures removed, memory count restored and business revision unchanged. No new operator/support SQL/RAG access difference was implemented. Resource limits and unsafe SQL reuse existing evidence; supply-chain/inter-agent and broader poisoning risks remain discussion or extensions. Guardrail/security chapter experiments and evidence mapping complete; slides, speaker notes, homework, refined demos and recordings remain deferred until course-outline finalization.

### Consolidated Guardrails and Agent Security lesson — October 7, 2026

Detailed guardrail demos, private-instruction disclosure and OWASP teaching notes now share one [teaching guide](app/docs/SECURITY-CHAPTER-DEMO.md). Course section 10 is a brief component overview; section 15 owns the combined lesson. Monitoring, tracing and evaluation remain separate sections. The memory-permission demonstration is removed from the main security lesson; historical ownership evidence is retained, and no read-by-ID operation is being added.

The test Support UI now offers **Private-instruction example** modes: Off, Without privacy rule, and With privacy rule. Selection starts a fresh conversation and displays the additional system text. The learner asks the same lantern-color question in the ordinary chat. The normal support-agent/gateway flow processes it and records the mode in run metrics. The synthetic fact never changes business data or RAG documents; main-workspace requests for a non-Off mode are rejected. The automatic two-call button has been removed. The standalone terminal probe remains an optional reference, not the UI flow.

Existing guardrail findings remain bounded: latest forged-exception comparisons preserved held status in both cases, with clearer conflict handling when source authority was On. Privacy masking and direct/indirect Lakera blocks have been exercised; misses and false positives remain documented. The revised manual lantern comparison is ready for learner verification, not claimed as a newly measured result.

OWASP concepts for later slides: tool misuse/output validation, delegated authority and least privilege, memory/context poisoning, MCP/supply-chain trust, inter-agent trust, human approval and resource limits. General cloud/infrastructure security remains outside scope. No further broad security build is planned. Slides, notes, homework and recording refinement follow finalization of the required experiments and outline. **Next substantive topic: Google's enterprise agent platform**, using the existing application/MCP contracts and evidence as the comparison baseline.

### Security acceptance and Google platform handoff — October 7, 2026

The user reports validating the manual lantern comparison and agrees to close the bounded Guardrails and Agent Security experiment scope. This records user acceptance, not independent review of a new trace export. No further security build is required for this learning scope; slides, notes, homework and recording packaging remain later work.

Next is the [hosted Google platform walkthrough](app/CLOUD-SETUP.md): inspect the existing signed-in account/agent, deploy the marketplace agent, connect remote business MCP tools, ask questions through the available platform surface, exercise native sessions/long-term memory, inspect Google-native monitoring/tracing and capture repeatable setup/results. Account entitlements, model availability and middleware connectivity require inspection; no Google deployment or new benchmark is claimed yet.

### Google ADK implementation in progress — October 7, 2026

Selected ADK by user agreement. Added [agent and lesson client](app/google/README.md) for native Sessions/Memory Bank and authenticated laptop MCP. Three offline boundary checks and public MCP discovery/catalog smoke passed. Cloud Shell is authorized and billing enabled; private staging bucket, dedicated runtime identity and secret container created with explicit approval. Cloud deployment, Gemini answers, native-memory recall and telemetry acceptance remain pending.

Deployment follow-up: startup failed because Agent Platform 2.3.0 imported the absent `google.cloud.aiplatform` package. Added compatible aiplatform 2.3.0 and explicit serialization/model dependencies; the exact missing import passes in Cloud Shell. Corrected deployment submitted. Three local boundary tests still pass; hosted acceptance is pending.

## Google hosted memory acceptance — October 8, 2026

Seven hosted questions passed: same-session recall, fresh-session isolation, long-term preference recall and application to SQL/RAG, retrieval disabled and a different-user control. A separate fresh Playground recall also passed. The original failures were a preference saved under the CLI user instead of the Playground user, plus conflicting prompt instructions that sent personal-memory questions to business search. Generated memory from the Playground user’s own preference session and corrected that prompt routing. Saving remains an explicit lesson-client generation action; preload retrieval is automatic.

Cloud Trace correlation and native Traces → Session view passed for all final test sessions. The recall model input contains the saved preference; the SQL/RAG investigation has six tool calls and no model/tool errors. [Results, sessions, exact questions and repeatable commands](app/CLOUD-SETUP.md). No wider model benchmark is claimed.

## Google guide consolidation — October 8, 2026

Consolidated the Google experiment plan, walkthrough, deployment/memory commands, validation results and dated setup history into [one Google platform guide](app/CLOUD-SETUP.md). The former files retain short pointers for existing links. The course outline links to the combined guide; it explicitly distinguishes Playground from Cloud Shell, user IDs and per-question memory-off controls. No new cloud changes or model tests were needed for this documentation update.

## Google manual acceptance — October 8, 2026

The user confirmed completing the manual walkthrough for short-term memory, long-term memory and general business questions on October 8, 2026. This records user acceptance alongside the previously verified hosted tests and trace inspection; it is not a new automated run. The agreed Google experiment scope is closed. Slides, speaker notes, homework and recording preparation remain later work. [Combined guide](app/CLOUD-SETUP.md).

## Udemy recording acceptance — October 8, 2026

The user reports that Udemy confirmed the submitted test recording is good. This closes the test-video quality approval prerequisite based on user confirmation; it is not a new independent inspection of the Udemy account. Chapter experiments/outline finalization, slides, speaker notes, homework and demo rehearsal remain separate preparation steps.

## Routing/cache priority — October 8, 2026

The course owner classified the current-version routing/cache refresh as low priority and deferred it to Model Routing chapter preparation. It is not a prerequisite for closing the overall experiment phase. Historical routing results remain dated; any future refresh must separately inspect quality, cached tokens, cost and latency.

## Monitoring preparation scope — October 8, 2026

The owner deferred monitoring demo organization to chapter preparation. Use existing Langfuse/LiteLLM telemetry for our application and native Google/Lyzr views in their platform lessons. No new monitoring system or comparison-dashboard build is required upfront; show available cost, latency and error metrics without claiming feature parity across platforms.

## Marketplace answer feedback — October 8, 2026

Added per-answer thumbs-up/down feedback to the main and test marketplace Support workspaces. PostgreSQL stores one current vote per completed answer, with authenticated owner checks and persisted reload behavior; Langfuse receives the vote linked to the answer’s trace. Three non-destructive tests passed, frontend/container builds passed, and browser verification confirmed vote changes, reload persistence and the latest thumbs-down score in Langfuse. No paid model calls or business-state changes were required. A clearly labelled synthetic control conversation/trace is retained for inspection. Automatic online evaluation remains pending in the Evaluation lesson; offline runner exercises are chapter-preparation work.

## Feedback manual acceptance and Support UI cleanup — October 8, 2026

The user rated a real answer thumbs-down and confirmed its Langfuse trace displayed `user_feedback = False`. Documented Scores → Analytics for aggregate feedback, which measures rated answers only; retained synthetic verification must be distinguished from usage. Moved document indexing/status into right-hand Workspace options, removed the investigator banner and added Enter-to-submit with Shift+Enter for new lines in both workspaces. Frontend builds and container deployment passed; browser readback confirmed the new layout and shortcut hint.

Online evaluation stays **pending in the Evaluation lesson**: asynchronously score sampled real answers against retrieved evidence after delivery, tracking evidence support, relevance and citations. Sampling/rubric/judge/scheduling are still to be agreed. Feedback is complete; offline runner exercises are chapter preparation; neither is automatic online evaluation.

## Shared local/cloud marketplace deployment plan — October 8, 2026

The Marketplace lesson owns the common architecture and local-versus-cloud choices; Google ADK/Lyzr platform configuration and native memory/monitoring remain in their platform chapters. A new GCP project will hold shared frontend/chat backend and HTTP MCP services on Cloud Run, Cloud SQL PostgreSQL and Secret Manager, separate from the existing ADK lab project. Our SDK runtime can stay inside the chat backend. Runtime selector/adapters, identity/session mapping, provider-specific citations/trace association and Terraform-based provisioning are planned, not implemented. Local and cloud data do not automatically synchronize. LiteLLM is planned on Cloud Run and Langfuse Cloud Japan is selected; the architecture review below records the current design. See [Marketplace architecture in the course outline](course/MARKETPLACE-DEPLOYMENT-ARCHITECTURE.md).

## Cloud architecture review proposal — October 8, 2026

The owner selected Cloud Run for the marketplace web app, HTTP MCP middleware and LiteLLM, Cloud SQL PostgreSQL with separate databases, Secret Manager, and Langfuse Cloud in Japan. This replaces the single-VM proposal; no self-hosted Langfuse infrastructure is needed in the shared GCP project. Terraform, cloud adaptation and shared-interface adapters remain pending. Architecture review precedes provisioning; see [canonical architecture](course/MARKETPLACE-DEPLOYMENT-ARCHITECTURE.md).

## Shared cloud deployment approved — October 8, 2026

Owner approved proceeding in the new `marketplace-app-511005` project; billing was verified. Cloud Run/application/gateway plus private-only Cloud SQL and Langfuse Cloud Japan are selected. [Deployment workspace](app/cloud/README.md) contains a validated Terraform foundation and database start/stop script. At the approval checkpoint, resources had not yet been applied; the subsequent deployment checkpoint below records the created foundation. Public idle Cloud SQL IP charges were identified and avoided in the design; stopped storage/backups remain billable. Cloud packaging, durable remote investigation state, telemetry reliability, service deployment and adapters remain pending.

## Shared cloud foundation and image checkpoint — October 8, 2026

In `marketplace-app-511005`, the private network, protected Terraform state bucket, Artifact Registry, runtime identities and scoped secret containers are created. Cloud SQL `marketplace-postgres` has four databases (`market`, `market_test`, `market_eval`, `litellm`) and is stopped with activation `NEVER` and public IPv4 disabled. Storage and retained backups remain billable while stopped.

The **Marketplace support** Langfuse Cloud Japan project has matching backend/gateway keys stored in enabled version 1 secrets; authentication against that project passed. Web and LiteLLM gateway images tagged `course-20261008` are built and published to Artifact Registry. Image publication is not a service-deployment or trace-delivery result.

Cloud Run services, fresh database credentials, schema/demo-data initialization and end-to-end login, SQL/RAG, memory, guardrails, feedback, tracing and restart acceptance remain pending. Shared-interface Google ADK/Lyzr adapters remain separate pending work. The [local learner guide](app/LOCAL-SETUP.md) is written and configuration checks passed; clean-machine installation and learner-repository publication remain unverified. See [current deployment status](app/cloud/README.md).

Online evaluation is deferred to Evaluation chapter preparation, not an upfront prerequisite for the other experiments or earlier recordings. It remains unimplemented; user feedback is already complete and is a distinct capability.

## Shared cloud application verified — October 8, 2026

Terraform deployed the marketplace web app, authenticated HTTP MCP service and private LiteLLM gateway in `marketplace-app-511005`, using private Cloud SQL and Langfuse Cloud Japan. The corrected initializer rerun passed. Operator/support login, vector indexing, a correct SQL/RAG payout answer, short-term history, explicit long-term memory save/fresh-chat recall, feedback persistence/export, built-in privacy and Lakera blocking passed. Langfuse readback confirmed model/tool spans and post-filter gateway input; the synthetic email was masked there. HTTP MCP begin/read/end passed across separate requests. PostgreSQL is currently running for owner testing; stopped-storage costs and start/stop instructions remain applicable.

Setup fixes are embedded in the scripts: safe handling of LiteLLM-owned tables, reader defaults matching local setup, and the psycopg registry URL. The registry credential was rotated after its malformed-URL error included it; the older secret version was disabled. [Deployment guide](app/cloud/README.md) and [verification record](app/cloud/VALIDATION-2026-10-08.md).

Remaining: fresh-project/clean-machine learner rehearsal, forced replica/restart acceptance. Online evaluation remains deferred to Evaluation chapter preparation.

## October 8, 2026 — Marketplace runtime selector implementation

Implemented SDK/Lyzr/Google adapters, immutable per-conversation binding and automatic fresh conversation on runtime change. Thirteen targeted adapter, feedback and gateway-auth checks pass; frontend/local images build and the local selector is visible. Cloud selector is deployed; the approved Google query-only role is applied. Both local workspaces have updated containers. Google and Lyzr cloud order questions, same-session follow-ups and fresh-session native memory recall are verified. Local Lyzr credentials are configured in ignored `app/.env`, both local backends restarted, and the local order-2 question and same-session follow-up passed. Local Google ADC is configured; local main question and follow-up passed. Google cloud order question, native session follow-up, explicit Memory Bank save and fresh-session recall passed; switching/reopening history preserves the correct runtime. Live Google deployment metadata confirms its GCP marketplace MCP endpoint; fresh memory-off and memory-on reruns returned the correct revision; the original mismatch did not reproduce, and a snapshot comparison now checks for it. See [runtime guide](app/RUNTIME-SELECTOR.md).


### 8 October — comparison baseline and readable local answers

- Cloud `market` aligned transactionally with local revision 24, including the simulation clock, business history and indexed policy corpus; full row readback/hash matched. Previous cloud business snapshot retained for rollback; accounts, chats, feedback and memories preserved. Test/evaluation databases unchanged; no ongoing data sync introduced.
- Local SDK prompt formatting deployed to both local backend services. Live order-2 answer now renders a concise business table; daily order counts render clearly with date windows and match SQL (2 yesterday, 1 today). Cloud and hosted-platform formatting remains unchanged.


## Verified marketplace checkpoint — October 8, 2026

The local and cloud reference application paths are working. The shared UI selects OpenAI Agents SDK, Google ADK or Lyzr; switching opens a fresh conversation, and history retains its original runtime/session. Google and Lyzr remain hosted when selected locally, and currently use cloud MCP. The SDK uses the selected application's local/cloud database. Endpoint/key profiles are independent of the runtime selector.

Cloud `market` was aligned once to local revision 24, including clock, business history and indexed policies, with a retained rollback snapshot. User accounts, conversations, ratings and personal/native memories remain independent; test/evaluation databases were not copied. Local order summaries and daily counts now use readable business labels and formatting. The user approved the new local output and confirmed the cloud SDK detailed trace in Langfuse. Google/Lyzr wrapper traces record the marketplace question/answer/timing/feedback; internal calls remain in native platform tracing.

Course plan: local SDK for main demonstrations; hosted agents and native platform monitoring in platform chapters. Online evaluation remains Evaluation chapter preparation. Clean-machine/fresh-project learner rehearsals, publication checkpoints, slides, notes, homework and recording preparation remain separate work. See the [architecture and delivery boundaries](course/MARKETPLACE-DEPLOYMENT-ARCHITECTURE.md).


### 8 October — local-first operating mode and cloud database pause

User requested local backend connections for the next recording phase. The coordinated switch script completed with verified local Google and Lyzr MCP settings; its ten offline regression checks passed. Cloud SQL stop completed, activation policy NEVER, with storage/backups/data retained. Local startup now preserves the existing private Google ADC overlay and test workspace, and refreshes frontend proxy connections after rebuild; shell syntax passed. The startup path itself was not fully rerun merely for this change. Cloud SDK/application use requires a database restart.


### October 8, 2026 — Opening chapters and learner setup preparation

- Owner agreed six sections A–F and twenty-three chapters. Welcome is chapter 1; Anatomy includes components, marketplace demo, written setup and first-agent demo/practice. AWS deployment is deferred; Other Agent Platforms is an overview of AWS, Claude Managed Agents, Microsoft Foundry and OpenAI Agents API.
- Drafted five editable chapter decks with 31 slides, embedded speaker notes and demo cues. Rendered and individually inspected all slides; owner review and recording freeze remain pending. See [opening material index](course/recording/sections-a-b/README.md).
- Revised [local setup](app/LOCAL-SETUP.md) to use Mac as the main path, with separate Linux and Windows/WSL2 notes and explicit validation coverage.
- Fresh Google Linux VM rehearsal passed installation, nine baseline services, operator login, seeded data, conversation persistence, frontend HTTP response and Langfuse health. The VM is verified stopped; its disk is retained briefly for resuming and remains billable. Provider-backed answers, vector retrieval, emitted traces and feedback scores require the pending explicit key authorization and are not yet validated. See [validation report](app/LINUX-SETUP-VALIDATION-2026-10-08.md). The published GitHub URL/checkpoint remains a separate learner-release gate.

## Google optional integration guide cleanup — October 14, 2026

The learner-facing `course/GOOGLE-PLATFORM-PLAN.md` now starts only after Cloud Setup is complete and covers connecting the marketplace ADK agent, not the standalone Basics agent. New creation omits both `GOOGLE_RUNTIME_RESOURCE` and `--backend`; updates target an explicitly owned compatible runtime. Historical troubleshooting is no longer part of the learner connection path. No deployment or model calls were performed for this documentation change.

Additional historical receipt detail preserved from the previous guide: the October 8 Marketplace Support ADK Lab was `projects/299748367836/locations/us-central1/reasoningEngines/1966208540318105600`, app `marketplace_support`, in instructor project `customer-support-agent-510915`. The CLI default `course-operator` and Playground's actual stored owner `vais-query-reasoning-engine` were separate identities; the browser URL's `userId=user` was not the stored owner. Memory generation used the Playground user's own preference session `4205966399576735744`, without copying private memories across identities. Preference recall in session `839046291047579648` used trace `85de7a116e3e6f4156933ea32ca0568d`; its subsequent SQL/RAG request used `8587103d4880a7dfa0eb8126b75280b5`. The actual model input contained `PAST_CONVERSATIONS` with Status/Reason/Next step. Seven historical questions and separate fresh Playground session `5495768305748672512` passed; this does not prove the new Basics runtime's recall. Screenshots remain in `app/google/playground-memory-recall.png` and `app/google/trace-session-verified.png`.

The initial deployment import repair added compatible aiplatform dependencies; initial model routing failed in `us-central1` and worked with model endpoint `us`, retaining runtime/Sessions `us-central1`. Telemetry repaired SDK export settings and scoped writer permissions; resource normalization versus ingestion delay was not isolated as the sole cause of earlier empty trace panels. An October 8 cloud-profile update and business Playground follow-up passed, while later coordinated profiles are documented separately. Read current metadata before relying on any historical endpoint. Native Memory Bank required explicit session-to-memory generation; preload retrieval did not make saying “remember” an automatic save trigger.

## Platform guide migration audit — October 14, 2026

The learner-facing platform landscape and component-ownership comparison are being migrated into Chapter 21 slides/speaker notes, rather than another Markdown guide. Chapter 22's decision report remains planned and is not a measured platform ranking. The older PLATFORM-GUIDE numbered AWS as 20 and Lyzr as 21; the current course uses Lyzr 20, documentation-only platform overview 21, and decision synthesis 22. The old AWS container-hosting proposal was never deployed; a later hands-on AWS lesson is deferred.

Unique historical Lyzr UI receipt retained from the former platform guide: the October 3 Traces/Analytics view, with September 26–October 3 selected scope, displayed 30 traces, 2.87 credits, 11.63 seconds average latency, 0.00% execution errors and 31,332 average tokens per trace. These displayed aggregates were not isolated to the memory experiment and were not reconciled against correctness or cost definitions. User-reported tracing/monitoring acceptance is distinct from automated accuracy validation. Native Cognis record CRUD/provenance and cross-user identity isolation remained unverified; successful procedural recall did not close the autonomous shipment-evidence gap. Relevant exact reports and documented-vs-tested feature boundaries are retained in app/lyzr/README.md and its existing report links. Google historical receipt details were already retained in the October 8 and October 14 log entries. No old pending deployment statement is a current capability conclusion.
