# Agent Design Patterns — reference answers

These are interpretations of evidence and verified examples, not mandatory outputs. Fresh drafts and review decisions can vary. No submission is required.

## Instructor example: return after completed payout

The instructor button creates a dedicated simulated order whose seller payout was completed before the return request. The return enters manual_review because post-payout returns require manual review and automatic recovery is not implemented. Manual review does not establish that the seller rejected it.

In the fresh 23 October 2026 rehearsal, Nano initially repeated the status without its cause. GPT-5.4 identified the missing reason using the existing payout/return evidence and policy note; Nano added the post-payout explanation and the absence of recorded rejection. Correction made no new tool calls because the relevant evidence was already available. This is a successful correction of the missing explanation, not an assertion that every possible defect was eliminated.

## Learner example: seller lookup

The learner asks explicitly for seller Cedar & Co., including payment, quantity and payout details, in one question. No clarification follow-up is needed. In the seeded order-1:

- The full buyer payment is 759,600 paise (INR 7,596.00). It covers the entire order.
- Cedar & Co.'s item has quantity 2 at 249,900 paise per unit: gross 499,800 paise (INR 4,998.00).
- That seller-item payout is 449,820 paise (INR 4,498.20), recorded as failed; its shipment is delivered.

The buyer's payment is not Cedar & Co.'s payout. A seller-filtered query does not prove that its returned item is the whole order. Describe the seller's line separately from order-level facts and do not infer unseen other-item details. Check current revisions instead of copying seed values blindly.

In the fresh one-question verification, the exact seller-detail question was run twice. In one hybrid run, Nano displayed correct values but failed to explain why the full order payment exceeded Cedar's allocation. GPT-5.4 identified the missing order-versus-item distinction. Nano's final answer explicitly distinguished the entire order payment from Cedar's allocation gross and net payout, addressing that substantive omission. No new evidence was needed. The other draft was accepted; a correction is not guaranteed.

[Recorded one-question seller correction](http://localhost:3000/project/marketplace-support/traces/d33e6c4b1d6dd6e6bae2602b3d214671).

[Accepted repeat of the same seller question](http://localhost:3000/project/marketplace-support/traces/485b93fe673155b73e182372f5e28002).

[Recorded correction on the UI-created instructor scenario](http://localhost:3000/project/marketplace-support/traces/ef30c8655cdaa281a4043e28fdf20da9).

The earlier two-turn seller/name-collision rehearsal is historical context only. It is not required by this simplified learner exercise.

## Role handoffs and interpretation

The generator passes question, draft, original evidence and relevant prior conversation context to the reviewer. Structured feedback goes to application code. Code accepts the draft or invokes a separate correction agent with that feedback and the generated conversation; correction uses the selected generator model. Generator and correction can use read-only tools. The reviewer makes one structured call without tools or a golden answer. There is no second review.

- Accepted draft: no correction is expected; review acceptance is not a correctness certificate.
- Corrected draft: compare the actual change with source evidence, not merely the “completed” badge.
- Failed stage: report it as failed, not an accepted or successfully corrected answer.
- No change: a valid outcome if the draft was already supported. Different fresh drafts prevent a causal model ranking from one comparison.

## Limitations retained for teaching

The earlier order-1 eligibility example remained incomplete: review caught missing shipment evidence, but correction only acknowledged uncertainty. The 23-hour fresh rehearsal already calculated timing correctly; review removed unsupported monitoring/automatic-release promises rather than fixing elapsed time. Neither is presented as the main successful correction.

See the rehearsal summary (historical instructor evidence; retained separately) for setup and observations. The eighteen-case historical study is separate from these fresh live-path rehearsals.
