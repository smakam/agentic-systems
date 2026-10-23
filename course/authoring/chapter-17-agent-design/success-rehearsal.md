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
