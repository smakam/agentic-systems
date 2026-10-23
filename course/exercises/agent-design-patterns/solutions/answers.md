# Agent Design Patterns — reference answers

These are interpretations of evidence and verified examples, not mandatory outputs. Fresh drafts and review decisions can vary. No submission is required.

## Instructor example: return after completed payout

The prepared order's seller payout was completed before the return request. The return enters manual_review because post-payout returns require manual review and automatic recovery is not implemented. Manual review does not establish that the seller rejected it.

In the fresh 23 October 2026 rehearsal, Nano initially repeated the status without its cause. GPT-5.4 identified the missing reason using the existing payout/return evidence and policy note; Nano added the post-payout explanation and the absence of recorded rejection. Correction made no new tool calls because the relevant evidence was already available. This is a successful correction of the missing explanation, not an assertion that every possible defect was eliminated.

## Learner example: seller lookup

Use the current evidence to resolve Cedar to the seller, retaining the prior conversation context. In the seeded order-1:

- The full buyer payment is 759,600 paise (INR 7,596.00). It covers the entire order.
- Cedar & Co.'s item has quantity 2 at 249,900 paise per unit: gross 499,800 paise (INR 4,998.00).
- That seller-item payout is 449,820 paise (INR 4,498.20), recorded as failed; its shipment is delivered.

The buyer's payment is not Cedar & Co.'s payout. A seller-filtered query does not prove that its returned item is the whole order. Describe the seller's line separately from order-level facts and do not infer unseen other-item details. Check current revisions instead of copying seed values blindly.

In the fresh rehearsal, Nano listed whole-order payment beside seller-item fields without explaining the different scopes. GPT-5.4 flagged that conflation. Nano's final answer separated the full-order payment from Cedar's line item, shipment and failed payout, addressing the identified issue. The reviewer also requested an explicit order identifier; the substantive correction was the evidence-grain distinction.

[Recorded seller follow-up correction](http://localhost:3000/project/marketplace-support/traces/f5572a0bb76ce4e4d0308f62d2ecb08c).

[Recorded return correction](http://localhost:3000/project/marketplace-support/traces/e4f50865dc8ad540661f4670538d7d24).

The isolated seller rehearsal included both a Cedar & Co. seller and a Cedar Desk product. A current workspace without that name collision may resolve the first question immediately. The learner goal remains the seller-versus-order scope distinction; do not claim the same initial mistake or ambiguity must recur.

## Role handoffs and interpretation

The generator passes question, draft, original evidence and relevant prior conversation context to the reviewer. Structured feedback goes to application code. Code accepts the draft or invokes a separate correction agent with that feedback and the generated conversation; correction uses the selected generator model. Generator and correction can use read-only tools. The reviewer makes one structured call without tools or a golden answer. There is no second review.

- Accepted draft: no correction is expected; review acceptance is not a correctness certificate.
- Corrected draft: compare the actual change with source evidence, not merely the “completed” badge.
- Failed stage: report it as failed, not an accepted or successfully corrected answer.
- No change: a valid outcome if the draft was already supported. Different fresh drafts prevent a causal model ranking from one comparison.

## Limitations retained for teaching

The earlier order-1 eligibility example remained incomplete: review caught missing shipment evidence, but correction only acknowledged uncertainty. The 23-hour fresh rehearsal already calculated timing correctly; review removed unsupported monitoring/automatic-release promises rather than fixing elapsed time. Neither is presented as the main successful correction.

See the [rehearsal summary](../../../authoring/chapter-17-agent-design/success-rehearsal.md) for setup and observations. The eighteen-case historical study is separate from these fresh live-path rehearsals.
