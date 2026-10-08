# Marketplace roles and journey walkthroughs

This is the human guide to operating the simulated marketplace and checking its business flows. It complements the [application README](README.md), [product specification](../SPECIFICATION.md) and [agent evaluation specification](../EVALUATION-SPEC.md). All payments, refunds, shipping and payouts are simulated.

These journeys check application behavior. Agent evaluations separately check whether the support assistant explains that behavior accurately using records and policies.

## Roles and responsibilities

| Account | What it sees | What it does |
|---|---|---|
| Buyer (`buyer`, `buyer2`) | Marketplace catalog and its own orders/returns | Purchases items and requests returns for its delivered items |
| Seller (`seller`, Cedar & Co.) | Its own listings, order items, fulfillment and settlement | Adjusts its stock; dispatches and marks its items delivered; approves or receives returns |
| Operator (`operator`) | All sellers' catalog, orders, fulfillment and settlements; support workspace | Performs seller operations across sellers; simulates refunds/payouts; advances demo clock; investigates through support chat |
| Support (`support`) | Business records across sellers and support workspace | Investigates with read-only tools; cannot dispatch, refund, release payouts or change stock |

Operator is the demo's business administrator, not a separate infrastructure super-admin. Product/listing creation and seller onboarding are deferred. Adjust stock changes the quantity of an existing listing, not its product definition. Only Cedar has a seeded seller login; use operator for Northstar or Everyday Studio items.

One order can contain items from several sellers. Fulfillment and payout allocations attach to individual order items, which can have quantity greater than one. Seller balances aggregate those allocations; they are not themselves individual payout instructions.

## Before each journey

Use a fresh purchase unless explicitly continuing a prior branch. Record the order ID, product, quantity and seller. Switching accounts must not change which order you are following. The demo clock, not the real wall clock, controls delivery hold and return eligibility.

Do not reset the interactive database merely to follow this guide. A reset erases its business state and conversations. Automated reproduction belongs in the isolated evaluation/test databases.

## 1. Happy path: buyer purchases, receives goods, seller receives payout

| Step | Actor and action | Expected result |
|---|---|---|
| 1 | Buyer purchases one Canvas Weekender | Order and captured buyer payment created; stock decreases by one. Item has pending shipment and held payout allocation. Save order ID. |
| 2 | Seller opens its Orders & fulfillment and dispatches that item | Shipment becomes dispatched. Operator can also do this. |
| 3 | Seller marks it delivered | Shipment becomes delivered and records demo delivery time. This is a manual simulation of delivery confirmation. |
| 4 | Operator attempts Release payout before 24 hours have elapsed | Rejected with delivery/24-hour-hold explanation; no payout completes. This is an eligibility rejection, not a provider failure. |
| 5 | Operator advances demo clock 24 hours after delivery | Hold is satisfied. Merely advancing time does not release money. |
| 6 | Operator opens Seller settlement and releases that item's payout | Payout becomes completed. For one Canvas Weekender: buyer paid ₹2,499, marketplace fee ₹249.90, seller payout ₹2,249.10. |
| 7 | Support asks why/how the seller was paid for that order | Assistant should explain delivery, hold and completed payout using current records and relevant evidence. |

Dispatch, delivery and payout release are manual demo actions. Automatic fulfillment/payment scheduling is not implemented. Payout records appear before eligibility; being listed does not mean they can already be paid. A completed payout must not be released a second time.

## 2. Normal refund before seller payout

Start a different purchase and dispatch/deliver it, but **do not release its payout**.

| Step | Actor and action | Expected result |
|---|---|---|
| 1 | Buyer requests Return one unit | Return becomes requested. Delivery is required; the return must be within 30 days and cannot exceed remaining returnable quantity. |
| 2 | Seller or operator approves return | Return becomes approved. This is permission to return, not a refund. |
| 3 | Seller or operator clicks Receive return | Return becomes received: the demo records that the item came back. No buyer refund has completed yet. |
| 4 | Operator completes refund | Refund becomes completed; return becomes refunded. Refund equals purchase unit price × returned quantity. Stock is restored for those units. |
| 5 | Inspect settlement | Refunded amount increases; fee and seller payable are recalculated. A fully refunded item has ₹0 payable and displays “No payout due — fully refunded.” |
| 6 | Support asks for refund history | Answer should distinguish request, approval, receipt and completed refund; cite events and current records. |

Requested, approved and received returns block payout. A failed refund does not restore stock or change completed-refund totals. For a partial return, only returned units are refunded; the remaining seller payable can later be released when eligible.

The underlying payout record may retain `held` with zero amount after a full refund. It is not a completed payout and does not mean positive money is still due. The UI explains this as no payout due.

## 3. Return after seller payout: manual review

Continue a completed happy-path purchase from journey 1, within the 30-day return window.

1. Buyer requests a return.
2. Return enters **manual_review**, because the seller payout already completed.
3. No automatic refund or recovery of seller funds occurs. The normal approve → receive → refund path cannot complete this case in the current demo; a resolution workflow is deferred.
4. Support asks: “Why is this return in manual review? Did the seller reject it?”
5. Correct explanation: the seller had already been paid and automatic recovery is unsupported. Seller rejection must not be invented. A missing refund ID describes the current state, not the reason for review.

The 24-hour payout hold and 30-day return window are different rules. Passing 24 hours does not itself prevent a return; completed payout changes its handling.

## 4. Failed refund, then successful retry

Start a new normal return and proceed through **received**, without completing its refund or seller payout.

1. Operator chooses the refund's simulated failure action.
2. Refund attempt displays **failed**; return remains **received**. Buyer has not been refunded; financial totals and stock remain unchanged.
3. Operator retries successfully.
4. Refund becomes completed, return becomes refunded and exactly one refund amount is applied. The failed attempt remains in event history even though the current refund row now says completed.
5. Support asks: “Explain the refund history for [order ID].” Expected: failed attempt followed by successful retry, exact amount once, and resulting seller payable. A final-state-only answer misses the history.

## 5. Failed payout, then successful retry

Use an item that is delivered, has passed the 24-hour hold, has positive payable funds and has no blocking return.

1. Operator selects the payout's simulated failure action.
2. Payout becomes failed; seller balance remains unpaid. Inspect the failure event.
3. Operator retries successfully.
4. Payout becomes completed, unpaid decreases and paid-out increases by the same amount. No duplicate payment occurs.
5. Support asks for payout history. Expected: distinguish failure from retry completion; a failure affecting one payout is not evidence that all sellers were affected.

This differs from clicking Release payout too early: a hold rejection leaves the payout held and does not simulate a provider failure.

## 6. Additional boundary checks

- Seller sees and manages only owned listings/items; operator can manage all sellers.
- Support may inspect orders, fulfillment timelines and settlement, but must not mutate them.
- Return before delivery, return outside 30 days, excessive return quantity and refund before receipt are rejected.
- An active return blocks payout even after the delivery hold expires.
- Repeated clicks must not create duplicate completed refunds or payouts.
- A multi-seller order can be partially delivered; do not confuse one item's status with every item in the order.

## Walkthrough record and reusable test record

The discussion covered these example orders: Desk Lamp `ord-23b1f11c7b` (happy path then post-payout manual review), Canvas Weekender `ord-ace5ffc579` (normal refund), and Trail Backpack `ord-a9f9496711` (failed refund then retry). These are historical conversation references, not guaranteed current records or stable evaluation fixtures. Their state was not rechecked while writing this guide.

This guide was checked against the current business transition code and policies on 2026-09-28. It does not claim a fresh UI execution of every journey. The README's dated verification record is historical, not a live status report.

For future runs, record one row per journey:

| Date / app version | Journey | Order/item IDs | Clock / starting state | Steps run | Expected vs observed | Result / evidence |
|---|---|---|---|---|---|---|
| Fill when executed | 1–6 | Actual IDs | Demo timestamp and state | Include skipped steps | Note discrepancies | Pass / fail / not run, screenshot or event references |

Keep expected application behavior here. Keep run results in dated test records, and agent answer grading in the evaluation artifacts. This human guide is not automatically ingested into RAG; policies under `data/docs` remain the agent's documented business-rule sources.
