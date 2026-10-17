# Chapter 6: historical 18-case model-selection comparison

This learner reference supports the scores on the Chapter 6 model-selection slide. It summarizes the saved October 1 regression, not a new run and not the separate September human/Claude calibration study.

October 1, 2026. **18 cases / 20 answers per model**, nano versus GPT-5.4, using the current catalog-v2 / question-context-v3-evidence-reuse implementation. No paid judge. Grades are assistant-reviewed, with user-approved upgrades for cases 23/24 on both models. Other cases remain assistant-provisional; historical accepted grades are not overwritten.

## Business correctness

| Model | Correct | Partially correct | Incorrect | Fully correct cases |
|---|---:|---:|---:|---:|
| GPT-5 nano | 11 | 4 | 3 | 61.1% |
| GPT-5.4 | 17 | 1 | 0 | 94.4% |

GPT-5.4 handled the two payout boundaries and the ambiguous seller follow-up correctly in this run. Nano remained incorrect on 16 (allows release after 23 hours), 17 (rejects exactly 24 hours), and 27 (invented today-only filter after clarification). These are case-level scores: multi-turn cases 27/28 must satisfy both turns. They are not counts out of 20 answers.

The only shared partial case is 09: neither distinguishes buyer payment from seller payout. Nano additionally misses the cause in 14/15 and the explicit read-only refusal in 30.

**User-approved adjudication, October 1:** cases 23/24 are correct for both models. For 23, evaluate the qualified response as a whole: both identify the only confirmed affected payout and caution against broader attribution; naming Cedar is optional. A less categorical opening is still preferable. For 24, both give the correct ₹2,249.10 with evidence; an unrequested numeric breakdown is optional. These are grading clarifications, not improved model outputs. No rerun or paid grading occurred.

Original assistant counts were nano 9/6/3 and GPT-5.4 15/3/0. Original review archive and versioned adjudication with reference overrides preserve the change. The archived raw gold-v3 and deterministic checks are unchanged. Nano case 20 remains graded on correct refund facts despite secondary event-revision/identifier defects recorded for review.


## Case-level final grades

Source case identifiers are retained so the saved study can be audited. Earlier-versus-current arrows have been removed; these are the final grades used on the slide.

| Source case | GPT-5 nano | GPT-5.4 |
| --- | --- | --- |
| 02 | correct | correct |
| 04 | correct | correct |
| 08 | correct | correct |
| 09 | partially_correct | partially_correct |
| 10 | correct | correct |
| 11 | correct | correct |
| 14 | partially_correct | correct |
| 15 | partially_correct | correct |
| 16 | incorrect | correct |
| 17 | incorrect | correct |
| 20 | correct | correct |
| 21 | correct | correct |
| 23 | correct | correct |
| 24 | correct | correct |
| 26 | correct | correct |
| 27 | incorrect | correct |
| 28 | correct | correct |
| 30 | partially_correct | correct |

## Method and limits

The paired study used the same 18 fixtures and question sequences, MCP tools, low reasoning effort, up to eight agent steps, 150 seconds and 4,096 completion tokens. Two cases contain follow-ups, so each model generated 20 answers. A multi-turn case must satisfy the complete sequence. Model-specific monetary limits did not stop either full suite. No new paid judge was run.

Grades were reviewed by the assistant, with user-approved grading clarifications for cases 23 and 24. Other grades remain provisional. Regrading unchanged answers is not model improvement. One run on a known case set cannot establish a universal model ranking or predict all production workloads.

The stronger observed result motivated choosing GPT-5.4 for this application baseline. Later targeted tests and the Chapter 14 human/Claude calibration are separate studies and must not be merged into these scores.

## Provenance

Source: the saved `app/results/core18-history-v3-2026-10-01/REPORT.md` in the instructor workspace. This page reproduces its final summary and case grades without changing outputs, fixtures or judgments. Detailed evaluation methodology is taught later in the course.
