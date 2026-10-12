# Chapter Five — worked solution

This is an expected-results guide, not an exact model-answer script. Use current rows/events for your own references. All values below use the clean seed’s **one Canvas Weekender at ₹2,499** and the simulation’s 10% marketplace fee. Your edited listing/quantity may differ.

## Purchase and payout

A new purchase creates a paid order and captured payment. Its shipment starts pending and payout starts held immediately at purchase. Dispatch changes the shipment to dispatched; manual delivery changes it to delivered. Early payout release is rejected and stays held. After delivery +24 hours, the operator can release it if no active return blocks it and payable is positive. Successful release marks the payout completed. The order remains paid; that is this simulation’s simplified order model.

For the example: gross ₹2,499; fee ₹249.90; seller share ₹2,249.10. A purchase increases that seller’s captured balance by ₹2,499 and unpaid by ₹2,249.10, assuming no simultaneous refund/payout. It does not increase paid-out. The successful later payout moves ₹2,249.10 from unpaid to paid-out, without creating another buyer payment. Compare deltas against the recorded starting balances, not an assumed zero.

## Return and failure cases

| Scenario | Expected result |
|---|---|
| Full return before payout | Request → approved → received → refunded. Receipt means the physical goods arrived back. Full successful refund increases refunded by ₹2,499, recalculates remaining fee/payable to zero, and restores that quantity to stock. The order still says paid. |
| Partial return | Refund the returned quantity only. Recalculate fee and remaining seller share; do not assume every item in a multi-item order returned. |
| Return after payout | Manual review. Automatic seller-fund recovery and a normal post-payout refund are not implemented. |
| Failed refund | Current refund says failed; returned goods remain received; allocation’s refunded amount, fee, payable and stock do not change. Successful retry applies the amount once and marks return refunded. Both attempts remain in event history. |
| Failed payout | Eligible payout says failed; seller funds remain unpaid. Successful retry marks completed and moves the amount once. Early hold rejection is different and leaves held. |
| Active return | Requested/approved/received return blocks payout even after the clock hold. |
| Permissions | Buyer acts on own orders; seller manages own items; operator handles all marketplace operations; support can read/investigate but cannot mutate business records. |

## Agent comparison

Before purchase, the answer must agree with recorded seller balances. After purchase, the new answer should show the gross and unpaid deltas above and cite current evidence. Its investigation revision must reflect the completed purchase. Check the actual tool output and citations; an answer that merely claims to have refreshed is insufficient. If the model gives an unsupported/stale answer, record that as a failure, not a new business rule.

Policy retrieval should support delivered +24h, active-return blockers and manual operator release. A trace usually contains one or more model observations plus tool observations; do not expect an identical call sequence. Distinguish model requests from tool invocations. Empty cost telemetry cannot establish that the run was free.

## Code responsibilities

- `api.py`: authenticates the caller, checks conversation ownership and dispatches the question.
- `agent.py`: configures instructions/model/tools and calls the OpenAI Agents SDK runner, which manages the loop.
- `mcp_client.py`: connects the local MCP tool server and maintains investigation context.
- `tool_contracts.py`: defines model-visible tool signatures for catalog, SQL, policy search, evidence fetch and order history; MCP exposes these contracts.

MCP connection and tool contracts are related but separate responsibilities. The runtime invokes permitted tools and feeds results back to the model. An OpenAI model can be reached directly or through OpenRouter, selected behind the LiteLLM alias.

## Validation scope

Validation receipts are recorded separately. Business-state checks can be deterministic; model output wording/tool choices remain variable. A saved passing run does not guarantee every future run. Check current trace/evidence before recording. No fresh UI rehearsal is claimed solely from a code or API check.


### Verified rehearsal evidence — 12 October 2026

[Validation report](../../../../app/results/chapter-05-validation-2026-10-12/REPORT.md): six deterministic business cases and three live MCP agent questions passed. Before/after balances, fresh query revisions, policy evidence and local Langfuse observations were checked. Only synthetic records were used. UI recording rehearsal remains separate.
