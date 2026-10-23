# Agent Design Patterns — learner exercise

## Workspace for this activity

Use the [Test workspace](http://127.0.0.1:5179), **Support workspace**, with the disposable **market_test** database. Inspect agent-role handoffs in [local Langfuse](http://localhost:3000), project **marketplace-support**. Select **Agent design demo** in this workspace, rather than the normal marketplace on port 5178.

## Learner practice — separate order payment from seller payout

Apply the instructor's generate/review/correct flow to a different problem: a seller-order lookup. Inspect whether the final answer distinguishes the buyer's full order payment from the selected seller's line item and payout. No submission or upload is required.

## Instructor demo recap

The instructor showed an accepted product lookup and a return-after-payout explanation. In the verified return rehearsal, Nano omitted why manual review was required; GPT-5.4 identified the completed payout before the return, and Nano added that reason and the supporting policy.

The learner case instead checks order-level versus seller-item-level claims. It also includes a follow-up, so context handoff is inspected within the same exercise rather than in a separate optional section.

The detailed [instructor demo](instructor-demo.md) includes the return setup and trace walkthrough.

## Prepare

1. Open [Test workspace](http://127.0.0.1:5179), sign in as `support` (`demo-marketplace`) and open **Support workspace**.
2. Check documents are indexed and the installed policy is clean; ask the operator to restore Clean policy if needed. Record the revision and demo clock; do not change business state.
3. Use **Agent design demo**, not the Model routing demo. Changing its settings starts a fresh conversation. Memory and routing remain off in this lab.

## Practice — seller lookup and correction

1. Select **Hybrid · generate, review, correct**, **Generator: GPT-5 Nano**, **Reviewer: GPT-5.4**. Start a fresh conversation.
2. Ask: **Show orders for Cedar.**
3. In the same conversation, ask: **I mean the seller.** If the first answer already resolved Cedar & Co. unambiguously, still inspect how the follow-up retains that scope; do not assume the first question must trigger clarification.
4. Inspect the second turn's generator draft, review, application decision and any correction. In the reviewer input, locate the earlier question/answer, current question and original evidence. This is the context-handoff check.
5. Compare its own draft with its final answer. Look especially for full-order buyer payment being presented as a seller-specific amount, or a seller's one delivered line being presented as the entire order.
6. Check the query scope and evidence grain: order/payment fields describe the order; item, shipment and payout fields may describe only Cedar & Co.'s line item. State unknowns rather than inventing missing other-item details.
7. Open **Workflow trace** and follow **Generate draft → Review draft → Workflow decision → Correct draft**, when correction is requested. The reviewer has no tools; generator/correction can call read-only tools. Code permits one correction and no second review.

### Optional reviewer comparison

Repeat the same two questions in fresh conversations with **Generator only: Nano**, or with **Nano generator + Nano reviewer**. Keep all other settings fixed. Each run produces a new draft, so this is practice observing behavior, not a controlled reviewer ranking.

### Review your observations

- Did the draft distinguish whole-order payment from the seller's item and payout?
- Did the reviewer receive enough prior context to resolve “the seller”?
- What specific issue did review identify, and did the final answer actually fix it?
- Was a missing fact retrieved, left unknown, or merely proposed as a next step?

The seeded order-1 contains multiple sellers; verify current records if the workspace has changed. Do not assume a correction is mandatory. A fresh draft may already handle the distinction correctly. Compare with the [reference answers](solutions/answers.md) after inspecting your run. The answer key links a clearly labelled recorded successful correction if your run takes a different branch.

Finish by selecting **Off · normal support** and starting a fresh conversation.
