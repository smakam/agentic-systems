# Chapter 17 — fresh workflow rehearsal, 23 October 2026

One fresh pass through three previously improved historical scenarios, using the current live workflow path: Nano generator/correction, GPT-5.4 reviewer, one optional correction, original evidence and retained context. Runs used the isolated market_eval database, which was backed up and restored. The interactive market_test data was not modified.

## Main instructor example — return after payout

Prepared a new Desk Lamp purchase; dispatched and delivered it; advanced the demo clock 24 hours; completed its simulated seller payout; requested a return afterward. The return became manual_review.

Question: **Why is the return for <new order ID> in manual review? Did the seller reject it?**

Draft repeated the status without explaining the cause. Review identified the existing completed-payout evidence and post-payout return rule. Correction added the reason and preserved the absence of a recorded seller rejection. No new correction-stage tools were needed. This addresses the missing explanation.

[Recorded trace](http://localhost:3000/project/marketplace-support/traces/e4f50865dc8ad540661f4670538d7d24).

## Learner example — seller follow-up

Fixture included Cedar & Co. seller and Cedar Desk product. Questions: **Show orders for Cedar.** then **I mean the seller.**

Follow-up draft mixed full-order payment with the seller's item and payout without identifying the scope difference. Review requested a clear order-level versus item-level distinction; correction made that distinction using existing evidence. The current Test workspace may lack the name collision, so first-turn behavior can differ.

[Recorded follow-up trace](http://localhost:3000/project/marketplace-support/traces/f5572a0bb76ce4e4d0308f62d2ecb08c).

## Not selected — 23-hour hold

Fresh Nano draft already calculated 23 hours correctly. Review removed unsupported offers of monitoring, automatic release and policy exceptions. It did not reproduce the historical timing error; do not claim it did.

## Bounds

All four workflow turns completed; business fingerprints were unchanged during answer generation. Displayed conservative model-cost estimates total approximately USD 0.873 across the four turns, using the app's GPT-5.4-equivalent rates for all roles, not actual model-specific billing. These are interaction demonstrations, not a new quality benchmark. Fresh generator drafts can be correct, vary or fail; use the recorded before/after when a live run differs. No repeat-until-failure selection was used.

## Deployed scenario and final one-question verification

The Test UI now has **Create return-after-payout scenario**, backed by a Test-only authenticated endpoint for support/operator roles. Dedicated synthetic seller/product records preserve existing sellers' inventory/balances and the demo clock. Recorded history establishes payment, delivery, the waiting period, completed payout and then manual-review return. Repeated clicks reuse the same suitable scenario. Its creation and reuse were verified through the UI; all targeted access/integrity/workflow checks passed (9), and the frontend production build passed.

The exact UI-created order was tested with Nano alone and with Nano/GPT-5.4 review. Nano alone queried the order identifier as a return identifier and reported no result. The separate hybrid draft found the records but omitted the post-payout cause and inferred review state from the scenario audit event. GPT-5.4 identified the missing cause and unsupported audit-event interpretation. The correction added the policy and actual payout-before-return chronology. This verifies the causal explanation correction on the new scenario; the two different drafts are not a controlled reviewer-only comparison.

[UI-created scenario hybrid trace](http://localhost:3000/project/marketplace-support/traces/ef30c8655cdaa281a4043e28fdf20da9).

### All learner candidates tested

| Question | Runs | Result |
|---|---:|---|
| Show orders for Cedar & Co. | 1 | Accepted; did not request payment/payout fields, so not selected. |
| For order-1, show the items supplied by Cedar & Co., the buyer payment amount, and the seller payout amount and status. | 2 | One turn-limit failure before review; one correction removed unsupported payment-status/retry claims. Not selected. |
| Show the orders for seller Cedar & Co. Include order payment, item quantity and seller payout details. | 2 | One meaningful order-versus-seller payment clarification; one accepted draft. Selected as practice with recorded successful comparison, not a guaranteed live correction. |

[Selected correction](http://localhost:3000/project/marketplace-support/traces/d33e6c4b1d6dd6e6bae2602b3d214671) · [Accepted repeat](http://localhost:3000/project/marketplace-support/traces/485b93fe673155b73e182372f5e28002).

No original prompt was retried until a desired mistake appeared: the two expanded candidate questions and two repeats per candidate were specified before execution, and failures/acceptances are retained. These small repetitions establish inspectable examples, not statistical reliability. The historical 11/18 to 14/18 slide result is unchanged.
