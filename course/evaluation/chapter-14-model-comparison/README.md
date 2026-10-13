# Marketplace evaluation: paired human and Claude comparison

18 cases, 20 answer turns per model, one candidate trial; Claude v3 regrades unchanged saved outputs. Human labels not supplied to judge. Calibration, not independent judge accuracy.

This report uses the September baseline human review and Claude v3 calibration on the same saved outputs. It does not use the later October 1 assistant-reviewed regression grades.

## Summary

| Model | Evaluator | Correct | Partial | Incorrect |
| --- | --- | ---: | ---: | ---: |
| gpt-5-nano-2025-08-07 | Human | 8 | 8 | 2 |
| gpt-5-nano-2025-08-07 | Claude | 9 | 7 | 2 |
| gpt-5.4-2026-03-05 | Human | 15 | 1 | 2 |
| gpt-5.4-2026-03-05 | Claude | 13 | 3 | 2 |

Correctness: 0 incorrect, 1 partially correct, 2 correct. Scores are case-level; a multi-turn case must satisfy the complete question sequence. Claude readability and evidence assessments are separate fields; comparable human numerical scores for those dimensions were not recorded.

Exact grade agreement: nano 15/18 and GPT-5.4 16/18.

## Eighteen cases

| Case | Questions | Nano human | Nano Claude | GPT-5.4 human | GPT-5.4 Claude |
| --- | --- | --- | --- | --- | --- |
| 02 | What products and quantities are in order-1, and who sells them? | correct (2) | correct (2) | correct (2) | correct (2) |
| 04 | Show orders placed today for Cedar & Co. that are not yet delivered. | correct (2) | correct (2) | correct (2) | correct (2) |
| 08 | Show orders for Acme. | correct (2) | correct (2) | partially_correct (1) | partially_correct (1) |
| 09 | Has the payment gone through for order-1? | partially_correct (1) | partially_correct (1) | correct (2) | correct (2) |
| 10 | What is the current return window? | correct (2) | correct (2) | correct (2) | correct (2) |
| 11 | What return window did the policy specify on June 1, 2025? | correct (2) | correct (2) | correct (2) | correct (2) |
| 14 | Why has Cedar not been paid for order-1? | partially_correct (1) | partially_correct (1) | correct (2) | partially_correct (1) |
| 15 | Why is the return for ord-f378827237 in manual review? Did the seller reject it? | correct (2) | partially_correct (1) | correct (2) | correct (2) |
| 16 | Can the operator release the payout for ord-b8f486c950 now? | partially_correct (1) | partially_correct (1) | incorrect (0) | incorrect (0) |
| 17 | Can the operator release the payout for ord-b3431443e7 now? | partially_correct (1) | partially_correct (1) | incorrect (0) | incorrect (0) |
| 20 | Explain the refund history for ord-6f3604a5fe. | correct (2) | correct (2) | correct (2) | correct (2) |
| 21 | Explain the refund history for ord-aaa1768930. | partially_correct (1) | correct (2) | correct (2) | correct (2) |
| 23 | Did the payout incident affect every seller? | incorrect (0) | incorrect (0) | correct (2) | partially_correct (1) |
| 24 | After returning one Canvas Weekender, what remains payable to Cedar? | partially_correct (1) | partially_correct (1) | correct (2) | correct (2) |
| 26 | Reconcile all captured money across seller balances. | correct (2) | correct (2) | correct (2) | correct (2) |
| 27 | Show orders for Cedar. / Follow-up: I mean the seller. | incorrect (0) | incorrect (0) | correct (2) | correct (2) |
| 28 | What is Cedar's unpaid balance? / Follow-up: What is it now? | partially_correct (1) | correct (2) | correct (2) | correct (2) |
| 30 | Refund ord-b59d8ba410 now and tell me when you have sent the money. | partially_correct (1) | partially_correct (1) | correct (2) | correct (2) |

## Per-case references, answers and reasons

[Full raw comparison](comparison.json) contains both outputs, retrieved evidence, reference requirements, human notes, Claude rationale and checks for every case. [HTML review](comparison.html) expands each case. Human notes are absent for some cases and are explicitly marked rather than inferred.

## How to interpret the checks

Historical deterministic checks verify execution completion, unchanged business state, citation handle resolution and database replay fidelity. Some cases also compare returned evidence rows against a structured reference contract. These evidence checks do not parse or verify the final answer JSON. They are separate from the new native Langfuse final-output comparison. A passed evidence check does not establish semantic correctness.

## Provenance and limits

Human judgments come from the original saved human-review file. Claude v3 judgments regrade the same answers using clarified gold/rubric. Both references are retained here because optional-detail clarifications can affect disagreement. Human labels were not sent to Claude. The 31/36 agreement is calibration on reviewed examples, not independent validation or general judge accuracy. No model calls were made to build this report.

References, rubric and model outputs must stay versioned. A changed grade with an unchanged answer is regrading, not model improvement. This one-trial known-case study does not establish a general model ranking.

| Source | SHA-256 |
| --- | --- |
| `app/results/calibration-v3-2026-09-29/results.json` | `a629d9bbdeca4d8eaf08562aecccc2e3731cdf3a1e25ad27fecc37c006aeae50` |
| `app/results/core18-2026-09-28-03/human-review.json` | `1e2f2525b90eeb5e60d2e60293ef8737d565d19b5cf865eb9ae99a6f25963b6a` |
| `app/results/calibration-v3-2026-09-29/gold-v3.json` | `4a857323eda3ff10186691eab1e8c8308c958240538a45d6a43e5af061bf9ec8` |
