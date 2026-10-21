# Model routing reference answers

Use this after completing [the learner exercise](../exercise.md). These are interpretation checks, not text learners must reproduce. Fresh classifications and answers may vary; use the learner's actual trace and current business records.

## Part A — Classifier observations

| Cases | Policy | How classification runs | What the trace should establish |
|---|---|---|---|
| A1–A2 | `keyword_question` | Literal keyword rules, then the configured fallback if none matches | Requested keyword policy, tier/cause, routed alias, and actual answer model |
| A3–A4 | `heuristic_question` | Native LiteLLM heuristic v2 using its bundled trained artifact | Requested heuristic policy, a heuristic decision cause, tier, routed alias, and actual model |
| A5–A6 | `llm_question` | Nano interprets the shipped classifier rubric | Fresh `llm_classifier` decision, classifier alias `eval-nano`, tier, and selected answer model |

The keyword configuration includes `show` and `quantity` in SIMPLE, and `investigate` in COMPLEX. Q1 should therefore show `literal_keyword_match` and SIMPLE → `eval-nano`; Q2 should show the same cause and COMPLEX → `eval-5`. Verify the recorded metadata rather than inferring classification from the answer. If both tiers match, the highest matched tier wins.

Do not prescribe heuristic-v2 or LLM tiers as fixed golden labels for these questions. Both are decisions to inspect. Native SIMPLE maps to Nano; MEDIUM, COMPLEX and REASONING map to GPT-5. The native LLM rubric is not the historical business-context rubric. Heuristic v2 is not the historical default heuristic.

`routing_decision.routed_model` names the selected answer alias, not the classifier. `routing_decision.classifier_model` names the LLM classifier when present. Keyword matching and the local heuristic need no LLM classifier call. The `model` field in the gateway audit and corresponding generation identify the model used for the answer call. A tier, router name, or selected UI option alone does not establish answer correctness.

### Check the business answers

On the unchanged seeded `market_test` revision, order-2 contains a Ceramic Mug Set, quantity two. Its seller payout is held, shipment is pending, and delivery has not been recorded. The post-delivery waiting condition has not been satisfied. An answer claiming the payout has already completed conflicts with the baseline. If records have changed, grade against the recorded current state rather than this seeded reference.

For the three requested observations:

1. Compare Q1's actual tiers, causes and models across A1/A3/A5. Agreement or disagreement is acceptable when accurately documented.
2. Compare Q2 across A2/A4/A6 in the same way. Explain the observed classification, without claiming general classifier superiority from two questions.
3. A stronger selected model does not guarantee a correct answer. Check tool inputs/results and policy evidence independently. An incorrect order identifier can produce an empty lookup even when the route worked.

## Part B — Scope observations

| Scope | First user question | Later user questions | Model calls after tools |
|---|---|---|---|
| Per conversation | Classify and select | Reuse the conversation's selected model while the pin remains valid | Retain that selection |
| Per question | Classify and select | Classify each new question with supplied history; keep or change model | Reuse the current question's selection |

In B1, record the first choice and verify the later `session_affinity_pin` causes. A simple greeting often selects Nano, but pinning would also retain GPT-5 if that were the first choice. A pin lasts up to one hour in this configuration; restart or expiry can end it.

In B2, each new question should have a fresh `llm_classifier` decision. Calls after tools use `user_turn_continuation`. The harder question may select GPT-5, but a model switch is not required to prove reclassification. Inspect the cause, not just whether the model name changed.

The seeded net payout for order-2 is ₹1,618.20. Learners should check the calculation against current records and distinguish hypothetical net amount from eligibility or execution. All three answers need evidence checks; a pinned model or a successful model switch does not prove quality.

The scope comparison holds the LLM classifier, answer pool, security settings and question sequence fixed. It changes when selection is made. Per question is different from per model call: several model calls and tools can occur inside one user question.

## Submission review

- Both tables contain observed values and trace links, not invented expected metadata.
- The final answer and evidence check are recorded for each question.
- Classifier model, routed alias, and actual answer model are distinguished.
- Fresh classification and reused selection are distinguished using cause.
- Conclusions are limited to the observed runs. Cost and latency depend on classification overhead, selected models and cache eligibility; no cache superiority claim is required.
- Failed calls, missing metadata and unexpected results are described as such.

The exercise requires no new rubric, code, score import or dataset upload. Historical reports are optional context and do not substitute for these live observations.
