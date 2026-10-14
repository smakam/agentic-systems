# Chapter 16: Learner exercise options

Draft for review, October 13, 2026. The slides use Option A. Learners keep their observations locally and compare them with the separate reference answers. No submission is assumed.

## Option A: recorded-evidence worksheet (recommended)

**Time:** 20–30 minutes. **API cost:** none. **Prerequisites:** Chapters 6, 10–11 and 13–15. **Environment:** browser or downloaded documents. No marketplace UI, database connection or reset is required.

Sources:

- [Part 1: Choosing a Classifier](https://sreeni.blog/2026/09/30/model-routing-part-1-choosing-a-classifier/)
- [Part 2: Choosing the Scope](https://sreeni.blog/2026/09/30/model-routing-part-2-choosing-the-scope/)

### Part 1: Repeat the demo

1. Identify the historical model pool, SIMPLE/COMPLEX mapping and tested routing scopes. Explain where the runner, LiteLLM and SDK each participate.
2. Use Table A to compare fixed Nano, fixed GPT-5 and the LLM classifier. Calculate estimated savings versus fixed GPT-5 and the change in fully correct case count. Explain why the lowest token price is insufficient to select the policy.
3. Read the provider-timeout example in Part 1. Record the route selected by the generic heuristic, the essential fact omitted from the answer, and the classifier behavior that improved this specific case.
4. Read the order-2 conversation in Part 2. Record the model used for each question under conversation and question scope. Explain the omitted payout condition and how supplied history reaches the second model after a switch.
5. Use Table B to compare the four policies. State the numerator/denominator of the quality measure. Explain why 72 generated answers are not 72 independent scenarios, and why the classifier replay cannot substitute for this live conversation experiment.
6. Record one finding and one limitation about caching. Explain what the measurements support and what they leave unresolved.

### Table A: September classifier comparison

Costs below are full-price replay estimates for the same 18 cases and include classification. There are 20 answer turns per candidate model. A fully correct case requires every material requested fact in all its turns.

| Policy | Fully correct cases | Estimated total cost | Nano / GPT-5 selections |
| --- | ---: | ---: | ---: |
| Always Nano | 9/18 | $0.023121 | 18/0 |
| Always GPT-5 | 17/18 | $0.456238 | 0/18 |
| LLM classifier | 16/18 | $0.249470 | 9/9 |
| JEV classifier | 16/18 | $0.266017 | 8/10 |

The 18 classifications themselves cost $0.005436 for the LLM and $0.003759 for JEV. These are alternative classifiers; their costs are not added together.

### Table B: September live scope pilot

Each of six distinct scenarios contains three questions. Each policy ran once. A conversation counts as fully correct only when all three answers are correct. Costs are reconstructed from usage and frozen rates, including classification/candidate calls and retrieval embeddings; they are not invoices.

| Policy | Fully correct conversations | Cache-adjusted cost, all six | Full-price cost | Candidate cached input | Model switches |
| --- | ---: | ---: | ---: | ---: | ---: |
| Always Nano | 4/6 | $0.013809 | $0.019529 | 50.6% | 0 |
| Always GPT-5 | 6/6 | $0.271415 | $0.460487 | 64.0% | 0 |
| Per conversation | 4/6 | $0.126447 | $0.206257 | 54.0% | 0 |
| Per question | 4/6 | $0.126897 | $0.219051 | 57.9% | 4 |

### Part 2: Additional challenges

1. **Decision under a stated quality bar.** Suppose this development sample's provisional minimum is 16 fully correct cases out of 18. Among Table A policies that meet it, choose the lowest estimated-cost option. Then repeat with a minimum of 17/18. State why neither answer is a deployment recommendation.
2. **Classifier cost versus total cost.** JEV has lower classification cost. Explain why it has higher total route cost than the LLM policy. Use both model-selection counts and the measured costs.
3. **Fresh test design.** Write three new questions/scenarios: a direct lookup, an ambiguous follow-up and a time/money boundary. Give expected essential facts and identify independently controlled fixture data. Keep references outside the candidate and classifier inputs. Freeze the rubric before testing.
4. **Scope choice.** Name one conversation pattern where pinning is attractive and one where reclassification could help. Identify a risk in each. Explain why a scope change alone did not fix the Cedar ambiguity scenario.
5. **Reliability.** Describe separately what you would do after a provider request fails and after an answer fails a quality check. State what trustworthy signal you need for quality escalation.

### What to check and record

- Identify pool, classification and scope separately.
- Use correct denominators and label replay versus live evidence.
- Include classifier cost and selected-model cost.
- Support the decision with the stated quality bar.
- Retain a limitation, such as known development cases, one pass, mixed review provenance or uncontrolled cache warmth.
- Compare your reasoning with the separate reference answers.

**Cleanup:** none. No services, aliases or business data change in this worksheet.

## Option B: modify a classifier rubric

Learners write a keyword or LLM routing rubric for a small fresh question list, compare it with the baseline and explain disagreements. An offline keyword version needs no model credit. A model-based version incurs classification calls and requires a declared budget.

**Additional preparation needed:** portable runner, frozen starter questions and holdout, mapping/configuration file, expected selection checks, restoration instructions and worked solution. The historical scripts are not a finished learner path.

**Status:** proposed extension, not packaged or run here.

## Option C: live routing experiment

Learners compare one fixed-model baseline with a routing policy on controlled questions, then optionally compare conversation/question scope. Use the test marketplace/practice database `market_test` for a future UI-based lab, or a dedicated CLI lab with `market_eval` fixtures and locking. These are alternative paths and must be named explicitly in the eventual guide.

**Additional preparation needed:** select available teaching models, portable commands, isolated fixture/checkpoint, expected fact rubric, spend guard, versioned result capture and cleanup/restoration of aliases/configuration and services. Preserve `market` and shared evaluation baselines. Re-run candidate quality as well as costs/caching; do not assume historical results apply to current code.

**Status:** proposed paid extension. No current command sequence or fresh outcome is supplied as a completed lab.

