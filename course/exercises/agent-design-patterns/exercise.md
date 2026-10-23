# Agent Design Patterns — learner exercise

## Workspace and prerequisites

Use the [Test workspace](http://127.0.0.1:5179), **Support workspace**, **Agent design patterns**, with indexed documents and the clean policy corpus. Routing and long-term memory stay off. Keep business data unchanged during the investigations. No submission or upload is required.

The existing seeded **order-1** contains items from more than one seller, one full buyer payment and separate seller-item payouts. No scenario creation is needed for this learner case. Extra orders may exist; use the current records.

## Instructor demo recap

The [detailed instructor demo](instructor-demo.md) first shows an accepted product lookup, then a prepared return after the seller was paid. In the verified hybrid run, Nano omitted why manual review was required; GPT-5.4 identified the completed payout before the return, and Nano added that reason and the supporting policy. The Create scenario button prepares that instructor example.

## Your task — inspect a payment-versus-payout correction

Use this one question, without a clarification follow-up:

**Show the orders for seller Cedar & Co. Include order payment, item quantity and seller payout details.**

1. Select **Generator only**, **Generator: GPT-5 Nano**. Start a fresh conversation and ask the question. Inspect the answer and evidence.
2. Select **Hybrid · generate, review, correct**, **Generator: GPT-5 Nano**, **Reviewer: GPT-5.4**. Ask exactly the same question in the fresh conversation created by changing the settings.
3. Expand **Generate draft** and **Review draft**. Identify what, if anything, review considers unsupported or missing. The learning focus is whether order-level buyer payment is clearly separated from seller-item allocation and payout.
4. Inspect **Workflow decision** and any **Correct draft**. Compare the hybrid run's own draft with its final answer. The separate generator-only answer is another fresh generation, not a matched baseline for claiming a reviewer effect.
5. Check the cited records and query scope: does a field describe the whole order, the seller's item, or its allocation/payout? Did the correction clarify the distinction without changing valid amounts or inventing unseen items?
6. Open **Workflow trace** and inspect the draft/evidence passed to review, its feedback, the application branch, and the correction output. The reviewer has no tools; generator/correction can use read-only tools. Code permits one correction, with no second review.

## If your run is already correct

In the fresh verification, this exact seller-detail question produced the substantive clarification in **one of two hybrid runs**; the other draft was accepted. Do not keep rerunning until a mistake appears. An accepted draft is a valid observation, but does not itself demonstrate a correction.

If your draft is accepted, inspect the [recorded successful seller correction](http://localhost:3000/project/marketplace-support/traces/d33e6c4b1d6dd6e6bae2602b3d214671). Compare its original draft, reviewer finding and final answer, clearly labelling that comparison as recorded. This gives every learner an actual correction to inspect without claiming a guaranteed live outcome.

## Check your understanding

- Which amounts cover the whole order and which cover the selected seller's item?
- What exact omission or unsupported claim did the reviewer identify?
- Did the final answer fix it, and which evidence supports that judgment?
- What would remain unresolved if correction only suggested a query instead of executing it?

An optional extra comparison can use Nano as reviewer, but it is not required. Read the separate [reference answers](solutions/answers.md) after inspecting the drafts and evidence.

Finish with **Off · normal support** and a fresh conversation.
