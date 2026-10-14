# Chapter 17: Agent Design Patterns — reference answers

These are reference interpretations, not fixed text or mandatory branch outcomes. Model generation and review can vary; check current business data and the evidence in each run.

## Settings and expected role structure

- A1: one generator role, selected Nano model, read-only tool loop; no reviewer or correction.
- A2: Nano generator → Nano reviewer → application decision → optional Nano correction.
- A3: Nano generator → GPT-5.4 reviewer → application decision → optional Nano correction.
- Part B keeps Nano generator and GPT-5.4 reviewer through two questions in one conversation. The second question may use retained context, but current evidence must match the snapshot.
- “Off” returns to normal support. “Generator only” changes the fixed demo generator model without adding review.

The generator passes its draft and original evidence to review, alongside the question/snapshot and relevant prior conversation context. The reviewer returns `needs_revision`, `issues`, `correction_instructions` and `sufficient_evidence`. Application code accepts the draft or makes at most one correction attempt. The correction receives the generated conversation and feedback, treated as a hypothesis, and uses the generator model. It can call read-only tools. The reviewer is an SDK Agent configured for one structured call with no tools and no golden answer.

## Business facts to check in the seeded workspace

For order-2, buyer payment is captured, Ceramic Mug Set quantity is two, shipment is pending and seller payout is held. Buyer payment received does not mean the seller was paid. The payout policy requires delivery confirmation and the stated hold, subject to the applicable return rules. A supported answer should cite both current records and applicable policy; catalog definitions alone do not prove a policy rule or current delivery status.

For order-1, the seeded items are two Canvas Weekenders and two Desk Lamps. The recorded seller payout attempt for the first item failed, while the other item’s payout is held. A failed transfer is a recorded attempt outcome, not proof of policy ineligibility. Check the event history for the attempt and shipment/delivery records plus the applicable policy for any release-eligibility claim. Do not substitute a current payout row for a chronological account.

Changed data can yield different valid facts. Grade evidence use and role interpretation against the current revision, not these seed facts alone.

## How to interpret observations

- Accepted draft: reviewer returned `needs_revision=false`, code recorded `accept_draft`, and no correction stage was expected. This is not an independent correctness certificate.
- Correction: `needs_revision=true`, code recorded `correct_once`, and the trace contains **Correct draft**. Compare its claims with the draft and evidence. Correction can preserve uncertainty or still miss facts.
- Failed stage: name it and inspect the error trace. No successful hybrid completion should be claimed.
- No difference between A2 and A3: valid observation; it does not prove reviewers are equivalent. Different outputs also do not isolate reviewer capability because fresh generator drafts were created for each run.

## Recorded instructor rehearsal

The simple order-2 lookup was accepted by GPT-5.4 review after Nano generation. The complex order-1 eligibility question was flagged for missing delivery evidence and unsupported conclusions. Nano correction made uncertainty explicit but did not retrieve the missing shipment data. The controller and role handoffs worked; the final business answer remained incomplete. These saved examples teach debugging, not a performance ranking.

## Four short-answer points

1. The handoff should include question, snapshot, draft and source evidence, followed by specific structured feedback. Passing only prose loses the evidence contract.
2. Code owns the branch and bound. Generator/correction have read-only tools; the reviewer has none. One role can contain several model calls, so generation count is not agent count.
3. A cited claim must match its evidence and time/scope. Missing facts should be retrieved or clearly stated as unknown; feedback is not authority.
4. Describe observed changes and limits. Avoid “hybrid is always better”, “the reviewer approved so it is correct”, or treating one live repetition as a controlled benchmark.

See [verification](../verification.md) for what was actually checked. The historical eighteen-case reviewer ablation and seller-delegation study are separate evidence from this live lab.
