# Six conversations: scope study

Historical September 2026 study: six scenarios, three questions each, four policies and seventy-two freshly generated answers. Every policy has its own generated history. A conversation is fully correct only if all three answers are fully correct. The classifier is an LLM using GPT-5 Nano with the same business rubric and Nano/GPT-5 answer pool.

Assistant review plus the recorded user adjudications supplied the grades. This is a small one-pass methodology illustration, not a general policy ranking.

| Conversation | Scenario |
| --- | --- |
| [1](#conversation-1) (S1) | Simple lookup to payout investigation |
| [2](#conversation-2) (S2) | Investigation to bounded lookup |
| [3](#conversation-3) (S3) | Clarification and narrowing |
| [4](#conversation-4) (S4) | Fresh evidence after purchase |
| [5](#conversation-5) (S5) | Clock change and eligibility |
| [6](#conversation-6) (S6) | Routine lookup throughout |

<a id="conversation-1"></a>
## Conversation 1 — Simple lookup to payout investigation (S1)

Fixture: 01.

### Question 1

For order-2, list the purchased product, quantity and seller.

**Golden expectation**

Two Ceramic Mug Sets, sold by Everyday Studio.

### Question 2

For that same order, explain why its seller has not received the payout and what must happen before release.

**Golden expectation**

Buyer payment is captured. The shipment is pending and payout is held. Delivery must be confirmed, then the 24-hour hold must pass; an operator must request release. There is no recorded payout failure for this order.

### Question 3

What exact amount is currently payable to that seller for this order, after the marketplace fee?

**Golden expectation**

Everyday Studio is owed INR 1,618.20: gross INR 1,798 less INR 179.80 fee.

### Policy: always nano

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Requested product/quantity/seller or payable amount matches frozen expected facts.

Selection: fixed control

Ceramic Mug Set; 2 units; seller Everyday Studio. Demo date used: 2026-09-27 12:00:00+00. Result: product name, quantity, seller matched. Citation: [evidence:evidence-b25e7be03a59]. Revision: 1.

#### Answer 2 — GPT-5 Nano

Grade: **correct**. Reason: Requested product, payout condition or amount matches the frozen facts. Release eligibility explanation is accepted without repeating the operator UI workflow; no claim of automatic payment is made.

Selection: fixed control

Interpretation: For order-2, the sole item’s payout is currently held because the shipment is still pending delivery and the 24-hour hold/eligibility checks have not completed. The allocated gross is 179800 paise with a fee of 17980 and no refunds; payout amount is 161820 paise and status is held. Once delivered and the hold window passes (and no returns/refunds intervene), the payout can move to completed.

Demo date used: 2026-09-27 12:00:00+00:00. Result: payout exists but held. Citation: [evidence:evidence-c523749b99e2]. Revision: 1.

#### Answer 3 — GPT-5 Nano

Grade: **correct**. Reason: Requested product/quantity/seller or payable amount matches frozen expected facts.

Selection: fixed control

Amount payable after fee: 161,820 paise (₹1,618.20). Status: held until delivery confirmation/eligibility window passes. Demo date: 2026-09-27 12:00:00+00:00. Citation: [evidence:evidence-c523749b99e2]. Revision: 1.

### Policy: always gpt5

#### Answer 1 — GPT-5

Grade: **correct**. Reason: Requested product/quantity/seller or payable amount matches frozen expected facts.

Selection: fixed control

- Interpretation: order-2 refers to the order with id “order-2”.
- Demo date: 2026-09-27.
- Result:
  - Ceramic Mug Set — Qty 2 — Seller: Everyday Studio
- Citation: [evidence-36186a9cd2e0]
- Revision: 1

#### Answer 2 — GPT-5

Grade: **correct**. Reason: Requested product, payout condition or amount matches the frozen facts. Release eligibility explanation is accepted without repeating the operator UI workflow; no claim of automatic payment is made.

Selection: fixed control

Facts
- The order’s payout is in status “held” for ₹1,618.20; no returns or refunds exist on this order item [evidence-a7f3eb6de9b3].
- The event log shows payment captured but no shipment or delivery confirmation events for this order [evidence-44a3220da703].

Policy and required steps
- Payouts require delivery confirmation and a 24‑hour hold after delivery; any requested/approved/received return blocks release [evidence-c7a26902653f].

Conclusion
- The seller hasn’t been paid because delivery isn’t confirmed yet. Release will occur only after delivery is confirmed and 24 hours elapse, provided no return is in progress [evidence-a7f3eb6de9b3] [evidence-44a3220da703] [evidence-c7a26902653f].

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Requested product/quantity/seller or payable amount matches frozen expected facts.

Selection: fixed control

- Interpretation: “same order” = order-2.
- Demo date: 2026-09-27.
- Result: ₹1,618.20 payable after fee.
- Citation: [evidence-565c08a30c7b]
- Revision: 1

### Policy: conversation

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Requested product/quantity/seller or payable amount matches frozen expected facts.

Selection: Requires a bounded retrieval of order_items for a specific order, plus straightforward joins to listings/products/sellers to report product name, quantity, and seller.

Ceramic Mug Set, quantity 2, seller Everyday Studio. Demo date: 2026-09-27. Citation: [evidence:evidence-928d36425cdc]. Revision: 1.

#### Answer 2 — GPT-5 Nano

Grade: **partial**. Reason: Correctly identifies held payout and missing delivery, but omits the material 24-hour post-delivery hold and substitutes vague delivery/returns conditions.

Selection: Requires a bounded retrieval of order_items for a specific order, plus straightforward joins to listings/products/sellers to report product name, quantity, and seller.

Interpretation: The order-2 payout for item-3 is currently held and has not been released. Today’s date: 2026-09-27. Result: Payout status is held (payout-3, amount 1618.20 rupees). Evidence: [evidence-0b46cbbd9cf2], [evidence-4fdbb0390389]. Revision: 1.

Reason and needed action: Payouts remain held until delivery/fulfillment conditions are satisfied (e.g., shipment confirmed and customer delivery acknowledged or returns policy resolved). Since there is a captured payment but no released payout, release will occur once delivery status is confirmed per policy. Evidence shows only payment_captured so far.

#### Answer 3 — GPT-5 Nano

Grade: **correct**. Reason: Requested product/quantity/seller or payable amount matches frozen expected facts.

Selection: Requires a bounded retrieval of order_items for a specific order, plus straightforward joins to listings/products/sellers to report product name, quantity, and seller.

Order-2, seller-3 (Everyday Studio): payable after fees/refunds = 1618.20 INR. Demo date: 2026-09-27. Citation: [evidence:evidence-89b2d9b2b721]. Revision: 1.

### Policy: question

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Requested product/quantity/seller or payable amount matches frozen expected facts.

Selection: Direct bounded retrieval: need a single order's items with product name, quantity, and seller via straightforward joins (order_items -> listings -> products/sellers). No complex inference or policy.

- Interpretation: Ceramic Mug Set, quantity 2, seller Everyday Studio
- Demo date used: 2026-09-27 12:00:00+00:00
- Result: Ceramic Mug Set; quantity 2; seller Everyday Studio
- Citation: [evidence:evidence-0cd75846f7de]
- Revision: 1

#### Answer 2 — GPT-5

Grade: **correct**. Reason: Requested product, payout condition or amount matches the frozen facts. Release eligibility explanation is accepted without repeating the operator UI workflow; no claim of automatic payment is made.

Selection: Determining why a seller payout is not completed requires tracing allocations, payments, shipments, returns/refunds, and payout status, plus policy-based eligibility (delivery/time holds, returns, and any failed/pending events). It needs event history, reconciliation across multiple tables, and careful interpretation of current and historical states to identify blockers and required actions.

- Demo date used: 2026-09-27 12:00:00+00:00
- Facts: Payout for this order item is held, amount ₹1,618.20; no returns/refunds recorded; timeline shows no delivery confirmation event. [evidence:evidence-b5457521410c] [evidence:evidence-cb35360a5bb6]
- Why unpaid: Policy requires delivery confirmation plus a 24-hour hold; returns would block release. No delivery confirmation is recorded yet. [evidence:evidence-ea1f8cb8e44d]
- What must happen: The item must be delivered and 24 hours must elapse without a blocking return, after which the payout can be released. 
- Revision: 1

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Requested product/quantity/seller or payable amount matches frozen expected facts.

Selection: Determining exact payable requires aggregating allocations for the seller from the order, subtracting current marketplace fees and completed refunds, and accounting for any holds or pending payouts across potentially multiple items; it depends on live policy rules and event history (delivery status, 24-hour hold, returns).

- Demo date used: 2026-09-27 12:00:00+00:00
- Result: ₹1,618.20 currently payable to Everyday Studio for order-2 (payout status: held)
- Citation: [evidence:evidence-99f4b7de11df]
- Revision: 1


<a id="conversation-2"></a>
## Conversation 2 — Investigation to bounded lookup (S2)

Fixture: 01.

### Question 1

Investigate the failed payout to Cedar & Co. on order-1. Distinguish the recorded failure from the delivery waiting period.

**Golden expectation**

Cedar payout failed due to a simulated provider timeout. Delivery was September 25 at 12:00 UTC; the September 27 12:00 clock is 48 hours later, so the 24-hour hold has passed. An operator may retry; success is not guaranteed.

### Question 2

How much is the failed payout amount for that seller on this order?

**Golden expectation**

INR 4,498.20.

### Question 3

Which product and how many units on this order belong to that seller?

**Golden expectation**

Two Canvas Weekenders from Cedar & Co.

### Policy: always nano

#### Answer 1 — GPT-5 Nano

Grade: **incorrect**. Reason: Identifies provider timeout but incorrectly claims the 24-hour delivery hold has not matured; actual elapsed time is 48 hours. The question explicitly asks to distinguish these causes.

Selection: fixed control

Interpretation: The payout for Cedar & Co. on order-1 failed (payout-1: amount 449,820 paise; status: failed) due to a simulated provider timeout. The alternative seller (Northstar Goods) has a payout in a held state, not Cedar. The delivery waiting period (the 24-hour hold after delivery) has not matured for Cedar’s item as of the snapshot.

Demo date used: 2026-09-27 12:00:00+00:00.

Evidence: payout failure recorded in events (payout_failed) and linked payout row; Cedar’s item shows payout_status 'failed' with payout_amount_paise 449820. See results for Cedar item-1. [evidence-evidence-81c93f9e3245], [event timeline evidence-evidence-a8288ef7fa88]. Summary of the timeline: payment_captured for order-1, then payout_failed for payout-1 (provider timeout). [evidence:evidence-a8288ef7fa88]

#### Answer 2 — GPT-5 Nano

Grade: **correct**. Reason: Requested failure explanation, payable amount or product quantity matches frozen expected facts.

Selection: fixed control

Interpretation: Cedar & Co. on order-1 has a failed payout of 449,820 paise (4,498.20 INR). Demo date used: 2026-09-27 12:00:00+00:00. Citation: payout-1 shows amount 449820 with status failed in the payout/events trail. Revision: 1. [evidence:evidence-81c93f9e3245], [evidence:evidence-a8288ef7fa88]

#### Answer 3 — GPT-5 Nano

Grade: **correct**. Reason: Requested failure explanation, payable amount or product quantity matches frozen expected facts.

Selection: fixed control

Canvas Weekender, quantity 2. Demo date: 2026-09-27 12:00:00+00:00. [evidence:evidence-9e9f8830f9d1] Revision: 1.

### Policy: always gpt5

#### Answer 1 — GPT-5

Grade: **correct**. Reason: Requested distinction or lookup matches the frozen expected facts; correctly separates expired delivery hold from recorded provider timeout where asked.

Selection: fixed control

- Interpretation: “Cedar & Co.” is the seller on item-1 of order-1; its payout is payout-1 for ₹4,498.20, status failed. [evidence-c0df4305b4db][evidence-52835d22c88a]
- Demo date used: 2026-09-27.
- Delivery/hold: Item-1 delivered 2026-09-25 12:00; policy requires 24h hold, so eligible from 2026-09-26 12:00; no returns recorded. [evidence-03034f14f863][evidence-11762ec61c07][evidence-52835d22c88a]
- Recorded failure: payout-1 failed on 2026-09-27 09:00 due to simulated provider timeout (not a delivery hold). Funds remain unpaid. [evidence-3e2efd23e135]

Revision: 1

#### Answer 2 — GPT-5

Grade: **correct**. Reason: Requested distinction or lookup matches the frozen expected facts; correctly separates expired delivery hold from recorded provider timeout where asked.

Selection: fixed control

- Interpretation: Cedar & Co. is the seller on item-1 of order-1 (payout-1).
- Demo date used: 2026-09-27.
- Result: Failed payout amount is ₹4,498.20.
- Citation: [evidence-6048ea61351f]
- Revision: 1

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Requested distinction or lookup matches the frozen expected facts; correctly separates expired delivery hold from recorded provider timeout where asked.

Selection: fixed control

- Interpretation: Cedar & Co. is the seller on item-1 of order-1.
- Demo date used: 2026-09-27.
- Result: Product Canvas Weekender — 2 units.
- Citation: [evidence-816fdcba08de]
- Revision: 1

### Policy: conversation

#### Answer 1 — GPT-5

Grade: **correct**. Reason: Requested distinction or lookup matches the frozen expected facts; correctly separates expired delivery hold from recorded provider timeout where asked.

Selection: Determining why a specific payout failed requires tracing payouts, allocations, payments, and delivery status, plus policy/holding rules and potential timing windows (delivery wait vs. failure). It involves reconstructing event history and resolving ambiguity between a recorded payout failure and an in-progress delivery delay.

Interpretation: Cedar & Co. is the seller (seller-1) on item-1 of order-1. [evidence-evidence-ec175cdbaade]

Demo date used: 2026-09-27. [evidence-evidence-a1cce92cadd7]

Findings (chronological)
- 2026-09-25 12:00: Item-1 delivered. [evidence-evidence-ec175cdbaade]
- Policy: payout requires delivery + 24-hour hold; returns block release; failures leave funds unpaid until retried. [evidence-evidence-238327227d83]
- Eligibility window: Hold ended 2026-09-26 12:00, so payout eligible from then.
- 2026-09-27 09:00: Payout attempt for payout-1 failed due to simulated provider timeout. [evidence-evidence-ec377e879290]
- Current record: payout-1 status failed; amount ₹4,498.20 (449820 paise), funds unpaid. No return/refund on this item. [evidence-evidence-009ecdb32d20]

Distinction
- Waiting period: Not the cause (it had already elapsed).
- Recorded failure: Provider timeout on payout-1 after eligibility. [evidence-evidence-ec377e879290; evidence-evidence-238327227d83]

Revision: 1.

#### Answer 2 — GPT-5

Grade: **correct**. Reason: Correct requested amount/product lookup, explicit seller-versus-product clarification, or scoped order result, matching the frozen expected facts.

Selection: Determining why a specific payout failed requires tracing payouts, allocations, payments, and delivery status, plus policy/holding rules and potential timing windows (delivery wait vs. failure). It involves reconstructing event history and resolving ambiguity between a recorded payout failure and an in-progress delivery delay.

Interpretation: Cedar & Co. is seller-1 on item-1 of order-1. [evidence-617eb114d145]

Demo date: 2026-09-27. [evidence-617eb114d145]

Result: Failed payout amount ₹4,498.20 (449,820 paise) for payout-1. [evidence-66b2db43cb6b]

Revision: 1.

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Correct requested amount/product lookup, explicit seller-versus-product clarification, or scoped order result, matching the frozen expected facts.

Selection: Determining why a specific payout failed requires tracing payouts, allocations, payments, and delivery status, plus policy/holding rules and potential timing windows (delivery wait vs. failure). It involves reconstructing event history and resolving ambiguity between a recorded payout failure and an in-progress delivery delay.

Interpretation: Cedar & Co. is seller-1 on order-1. [evidence-809d97610e42]

Demo date: 2026-09-27. [evidence-809d97610e42]

Result: Canvas Weekender — 2 units. [evidence-20d9cfae280d]

Revision: 1.

### Policy: question

#### Answer 1 — GPT-5

Grade: **correct**. Reason: Requested failure explanation, payable amount or product quantity matches frozen expected facts.

Selection: Investigating a failed payout involves tracing payout events, allocations, and item-level delivery status over time, reconciling with holds, refunds, and policy-driven eligibility. It requires event chronology, cross-entity joins, and distinguishing a recorded failure from a legitimate post-delivery hold period.

- Interpretation: “Cedar & Co.” = seller-1 on order-1 item-1; payout-1 applies.
- Demo date used: 2026-09-27.
- Facts:
  - Payout-1 status: failed for ₹4,498.20; reason “simulated provider timeout.” [evidence-e84a21f022db] [evidence-cdd705ef404d]
  - Item delivered 2026-09-25 12:00; 24h hold ended 2026-09-26 12:00. [evidence-02448afad18f]
  - Policy: payout requires delivery + 24h hold; failures leave funds unpaid until retried. [evidence-a76d17b20a00]
- Conclusion: The failure was a provider error after the hold window, not a delivery/hold delay.
- Revision: 1

#### Answer 2 — GPT-5 Nano

Grade: **correct**. Reason: Requested failure explanation, payable amount or product quantity matches frozen expected facts.

Selection: Direct lookup of a specific payout record's amount for a known allocation/status; bounded retrieval with straightforward interpretation.

- Amount: ₹4,498.20 (449,820 paise) for Cedar & Co. on order-1.
- Status: failed payout against allocation allocation-1.
- Citation: [evidence:evidence-38b5f63a411b]
- Demo date used: 2026-09-27.

#### Answer 3 — GPT-5 Nano

Grade: **correct**. Reason: Requested failure explanation, payable amount or product quantity matches frozen expected facts.

Selection: Direct bounded data retrieval: identify order_items for a specific order and seller to determine product_id and quantity without needing causal reasoning or policy applications.

- Product: Canvas Weekender
- Quantity: 2 units
- Demo date used: 2026-09-27
- Citation: [evidence:evidence-ad859d1e4e4e]
- Revision: 1


<a id="conversation-3"></a>
## Conversation 3 — Clarification and narrowing (S3)

Fixture: 27.

### Question 1

Please list purchases associated with Cedar.

**Golden expectation**

Ask whether Cedar means seller Cedar & Co. or product Cedar Desk; do not choose silently.

### Question 2

The seller Cedar & Co., not the desk product.

**Golden expectation**

Order-1 contains two Canvas Weekenders sold by Cedar & Co.; no other Cedar seller orders exist.

### Question 3

Within those purchases, show only items that have not been delivered.

**Golden expectation**

None; the Cedar items in order-1 have already been delivered.

### Policy: always nano

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Correct requested amount/product lookup, explicit seller-versus-product clarification, or scoped order result, matching the frozen expected facts.

Selection: fixed control

Cedar matches both: the product Cedar Desk and the seller Cedar & Co. Which scope would you like me to use (or specify both): 
- purchases of Cedar Desk (product)
- purchases from Cedar & Co. (seller)
- or both? (demo date used: 2026-09-27)

#### Answer 2 — GPT-5 Nano

Grade: **incorrect**. Reason: Introduces an unrequested today-only date filter and says no purchases. The clarified seller has order-1 from September 24; the user did not ask only for today.

Selection: fixed control

Interpretation: Purchases by the seller Cedar & Co. (seller-1) on 2026-09-27.

Demo date used: 2026-09-27.

Result: No purchases found for Cedar & Co. in the specified window.

Citation: [evidence:evidence-a088396b301f]

Revision: 1

#### Answer 3 — GPT-5 Nano

Grade: **partial**. Reason: No undelivered items is the right final set, but the explanation relies on the invented today-only scope and falsely implies no relevant purchases, rather than recognizing the existing delivered order. Correct empty result for the wrong reason.

Selection: fixed control

Interpretation: Cedar & Co. (seller-1) purchases on 2026-09-27. Demo date used: 2026-09-27.

Result: No purchases found for Cedar & Co. in the specified window; hence no undelivered items to list.

Citation: [evidence:evidence-a088396b301f]

Revision: 2

### Policy: always gpt5

#### Answer 1 — GPT-5

Grade: **correct**. Reason: Correct requested amount/product lookup, explicit seller-versus-product clarification, or scoped order result, matching the frozen expected facts.

Selection: fixed control

Do you mean purchases for the seller “Cedar & Co.” or for the product “Cedar Desk”?

#### Answer 2 — GPT-5

Grade: **correct**. Reason: Correct requested amount/product lookup, explicit seller-versus-product clarification, or scoped order result, matching the frozen expected facts.

Selection: fixed control

Interpretation: seller “Cedar & Co.” (seller-1) [evidence:evidence-e6f886dc5f31]
Demo date: 2026-09-27

order-1 | 2026-09-24 12:00Z | buyer | Canvas Weekender | qty 2 | ₹2,499.00 | ₹4,998.00 [evidence:evidence-f45f7e596adc]

Revision: 1

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Correct requested amount/product lookup, explicit seller-versus-product clarification, or scoped order result, matching the frozen expected facts.

Selection: fixed control

Interpretation: seller “Cedar & Co.” (seller-1) [evidence:evidence-5a64400b6b7c]
Demo date: 2026-09-27

Undelivered items: none found for this seller’s purchases. [evidence:evidence-8dc659ec0265]

Revision: 1

### Policy: conversation

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Explicitly asks whether Cedar refers to the desk product or the seller, as required.

Selection: Direct bounded retrieval: identify customer by username (Cedar) and list associated orders from the analytics schema; requires straightforward joins between customers and orders with a single identifier. No complex event interpretation or state reconciliation needed.

Cedar matches two entities: Cedar Desk (product-cedar-desk) and Cedar & Co. (seller-1). Do you want purchases of Cedar Desk or purchases from Cedar & Co.? Please specify which alternative. Demo date used: 2026-09-27.

#### Answer 2 — GPT-5 Nano

Grade: **incorrect**. Reason: Adds an unrequested today filter and misses the seller's existing September 24 order.

Selection: Direct bounded retrieval: identify customer by username (Cedar) and list associated orders from the analytics schema; requires straightforward joins between customers and orders with a single identifier. No complex event interpretation or state reconciliation needed.

Interpretation: Purchases for Cedar & Co. (seller-1) today: none found.

Demo date used: 2026-09-27 (clock in snapshot).

Result: 0 rows; no orders for seller_id "seller-1" between 2026-09-27 00:00:00+00:00 and 2026-09-28 00:00:00+00:00.

Citation: [evidence:evidence-8ffa2c43a861]

Revision: 1 (clock 2026-09-27 12:00:00+00:00)

#### Answer 3 — GPT-5 Nano

Grade: **partial**. Reason: Empty undelivered result happens to be correct, but uses an unrequested today-only scope inherited from the erroneous prior answer. It does not establish that the existing seller order is delivered.

Selection: Direct bounded retrieval: identify customer by username (Cedar) and list associated orders from the analytics schema; requires straightforward joins between customers and orders with a single identifier. No complex event interpretation or state reconciliation needed.

Interpretation: Cedar & Co. purchases today with undelivered items: none.

Demo date used: 2026-09-27.

Result: 0 rows; no undelivered items for seller_id "seller-1" between 2026-09-27 00:00:00+00:00 and 2026-09-28 00:00:00+00:00.

Citation: [evidence:evidence-8ffa2c43a861]

Revision: 2 (clock 2026-09-27 12:00:00+00:00)

### Policy: question

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Correct requested amount/product lookup, explicit seller-versus-product clarification, or scoped order result, matching the frozen expected facts.

Selection: Direct bounded retrieval: list orders/purchases for a clearly identifiable customer (Cedar) using existing customer-to-order relationship. No complex event reconstruction or policy/application reasoning required.

Do you mean Cedar Desk (product) or Cedar & Co. (seller)?

#### Answer 2 — GPT-5 Nano

Grade: **incorrect**. Reason: Introduces an unrequested today-only date filter and says no purchases. The clarified seller has order-1 from September 24; the user did not ask only for today.

Selection: Direct bounded retrieval: identify the seller Cedar and fetch associated purchases by joining orders, order_items, listings, and sellers with a simple filter on seller name. No complex policy, time, or incident reasoning needed.

Interpretation: Cedar & Co. (seller-1) purchases today (demo clock 2026-09-27) with inclusive start 2026-09-27 00:00:00+00 and exclusive 2026-09-28 00:00:00+00.

Result: No purchases found for Cedar & Co. today.

Evidence: [evidence:evidence-20e65c50a4ad]
Revision: 1
Demo date used: 2026-09-27 12:00:00+00:00

#### Answer 3 — GPT-5 Nano

Grade: **partial**. Reason: Empty undelivered result happens to be correct, but uses an unrequested today-only scope inherited from the erroneous prior answer. It does not establish that the existing seller order is delivered.

Selection: Task is a bounded read from existing records: identify purchases tied to Cedar & Co. and filter the associated order_items/shipments by non-delivered status. No complex inference or timeline reconstruction required.

Interpretation: Cedar & Co. (seller-1) had no purchases today (demo clock 2026-09-27).

Result: No not-delivered items (no purchases to filter).

Evidence: [evidence:evidence-20e65c50a4ad]

Revision: 1
Demo date used: 2026-09-27 12:00:00+00:00


<a id="conversation-4"></a>
## Conversation 4 — Fresh evidence after purchase (S4)

Fixture: 01.

### Question 1

Give the current unpaid seller balance for Cedar & Co. in rupees.

**Golden expectation**

INR 4,498.20 unpaid.

### Question 2

What is that balance now?

**Golden expectation**

INR 6,747.30 unpaid, including the newly captured purchase; increase INR 2,249.10 is optional.

### Question 3

Explain why the new purchase contributes to money owed even though its shipment is still pending. Is that new payout ready for release?

**Golden expectation**

Captured payment creates the seller allocation/payable immediately. That is different from payout eligibility: the new shipment is pending, so it cannot be released until delivery and the 24-hour hold. New item gross INR 2,499, fee INR 249.90, payable INR 2,249.10.

### Policy: always nano

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Correct unpaid amount after rechecking the relevant data. Incorrect revision labels, where present, are tracked separately from the requested financial fact.

Selection: fixed control

Cedar & Co. unpaid balance: 4498.20 INR (paise 449,820). Demo date used: 2026-09-27 12:00:00+00:00. [evidence:evidence-2abf6224154f], revision 1.

#### Answer 2 — GPT-5 Nano

Grade: **correct**. Reason: Correct unpaid amount after rechecking the relevant data. Incorrect revision labels, where present, are tracked separately from the requested financial fact.

Selection: fixed control

Cedar & Co. current unpaid balance: 6747.30 INR (paise 674,730). Demo date used: 2026-09-27 12:00:00+00:00. [evidence:evidence-4b5cc62baeb3], revision 1.

#### Answer 3 — GPT-5 Nano

Grade: **correct**. Reason: Balance and captured payable versus delivery-dependent release eligibility match the frozen facts. Nano has awkward amount formatting but the rupee balance and conclusion are correct.

Selection: fixed control

Interpretation: The new purchase increases the seller’s gross funds (captured) and sits in unpaid until payout completes, since payouts are not automatic until eligibility is met.

Demo date: 2026-09-27 12:00:00+00:00.

Result: Cedar & Co. unpaid: 6747.30 INR (paise 674,730). Captured 74,9700; Fees 74,970; No payouts completed yet.

Evidence: [evidence:evidence-f0770b8a2457]; revision 1. 
Why it contributes now: unpaid = gross - fee - refunded for payouts not completed; includes held funds. New order raises gross and thus the unpaid bucket even if shipment is pending, until eligibility criteria (delivery, 24-hour hold, active returns) are satisfied. Payout readiness depends on delivery and hold window, so currently not ready for release.

### Policy: always gpt5

#### Answer 1 — GPT-5

Grade: **correct**. Reason: Balance and captured payable versus delivery-dependent release eligibility match the frozen facts. Nano has awkward amount formatting but the rupee balance and conclusion are correct.

Selection: fixed control

- Interpretation: “Cedar & Co.” refers to seller seller-1. [evidence:evidence-3785071c6e97]
- Demo date: 2026-09-27
- Unpaid balance: ₹4,498.20 [evidence:evidence-bff644fd11ed]
- Revision: 1

#### Answer 2 — GPT-5

Grade: **correct**. Reason: Balance and captured payable versus delivery-dependent release eligibility match the frozen facts. Nano has awkward amount formatting but the rupee balance and conclusion are correct.

Selection: fixed control

- Interpretation: “Cedar & Co.” is seller seller-1. [evidence:evidence-17240dde6f43]
- Demo date: 2026-09-27
- Unpaid balance: ₹6,747.30 [evidence:evidence-77dc3ba4facf]
- Revision: 2

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Balance and captured payable versus delivery-dependent release eligibility match the frozen facts. Nano has awkward amount formatting but the rupee balance and conclusion are correct.

Selection: fixed control

- Demo date: 2026-09-27
- Why it increases money owed: The order item was purchased and allocated to Cedar & Co.; a payout record for ₹2,249.10 (₹2499.00 gross − ₹249.90 fee, no refunds) exists in status held. Held payouts count toward the seller’s unpaid balance until completed. [evidence:evidence-568bc6a601ea] [evidence:evidence-28629fda7456] [evidence:evidence-3df679ca664b]
- Is it ready for release? No. Shipment is still pending; payout eligibility requires delivery plus a 24-hour hold and no active returns. [evidence:evidence-568bc6a601ea] [evidence:evidence-3df679ca664b]
- Revision: 2

### Policy: conversation

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Correct unpaid balance before/after the scripted purchase, retrieved from the changed data. Turn 2 contains a confusing paise aside but explicitly corrects it and gives the right rupee value.

Selection: Direct lookup of the unpaid balance for a specified seller from the seller balances view; straightforward bounded retrieval with standard fields (unpaid) and seller identity.

Cedar & Co. (seller-1) current unpaid balance: ₹4,498.20 (449,820 paise). Demo date used: 2026-09-27 12:00:00+00:00. Source: analytics.seller_balances.unpaid. [evidence:evidence-24ba2dca7f16]

#### Answer 2 — GPT-5 Nano

Grade: **correct**. Reason: Correct unpaid balance before/after the scripted purchase, retrieved from the changed data. Turn 2 contains a confusing paise aside but explicitly corrects it and gives the right rupee value.

Selection: Direct lookup of the unpaid balance for a specified seller from the seller balances view; straightforward bounded retrieval with standard fields (unpaid) and seller identity.

Cedar & Co. current unpaid balance: ₹6,747.30 (6,747 paise? actually 674,730 paise). Demo date used: 2026-09-27 12:00:00+00:00. [evidence:evidence-0ec2fc9bf216]; revision 2.

#### Answer 3 — GPT-5 Nano

Grade: **correct**. Reason: Correct requested balance or distinction between a captured seller payable and readiness to release it. Pending shipment prevents release; the question does not require restating every release step.

Selection: Direct lookup of the unpaid balance for a specified seller from the seller balances view; straightforward bounded retrieval with standard fields (unpaid) and seller identity.

- Why it contributes: Unpaid = gross allocations for non-completed payouts minus refunds/fees. A new purchase increases captured and its allocation adds to unpaid until the payout completes; shipment pending does not yet lock a payout as completed.  
- Is the new payout ready? No. Payouts show paid_out = 0 and the allocation isn’t completed/eligible yet (delivery hold + potential returns apply). Current unpaid reflects that awaiting settlement.

Demo date used: 2026-09-27 12:00:00+00:00. [evidence:evidence-a49b7e969a9f]

### Policy: question

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Correct unpaid amount after rechecking the relevant data. Incorrect revision labels, where present, are tracked separately from the requested financial fact.

Selection: Requires direct bounded retrieval of a specific seller's unpaid balance; perform a simple lookup/join to map seller name to ID and read the unpaid value from the seller_balances view, then convert paise to rupees. No complex inference or event reconstruction needed.

Interpretation: Cedar & Co. has an unpaid seller balance.
Demo date: 2026-09-27 12:00:00+00:00 (demo clock).
Result: 4498.20 INR unpaid (449820 paise).
Citation: [evidence:evidence-54695e71133f]
Revision: 1

#### Answer 2 — GPT-5 Nano

Grade: **correct**. Reason: Correct unpaid amount after rechecking the relevant data. Incorrect revision labels, where present, are tracked separately from the requested financial fact.

Selection: Direct bounded retrieval of a known seller's current unpaid balance from the analytics.seller_balances view; straightforward lookup with no inference or event reconstruction needed.

Interpretation: Cedar & Co. has an unpaid seller balance.
Demo date: 2026-09-27 12:00:00+00:00 (demo clock).
Result: 674,730 paise = 6,747.30 INR unpaid.
Citation: [evidence:evidence-fa2d12eb70da]
Revision: 1

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Correct requested balance or distinction between a captured seller payable and readiness to release it. Pending shipment prevents release; the question does not require restating every release step.

Selection: Requires causal explanation of how an order item’s funds become owed (allocation) before delivery, and whether the associated payout is eligible/ready despite pending shipment; involves policy timing, hold periods, refunds, and potentially multiple records (allocations, payouts, events) to determine status.

- Why it counts toward “unpaid”: Seller unpaid includes all non-completed payouts (held or failed), even if shipment is pending; it’s the net allocation (gross minus fee minus refunds) awaiting completion [evidence:evidence-896efe40a8a6]. Cedar & Co.’s new item has a held payout of 224,910 paise (2,249.10 INR), shipment pending [evidence:evidence-02feb916b9b3].
- Is it ready for release? No. Policy requires delivery confirmation plus a 24‑hour hold; pending shipment is not eligible [evidence:evidence-896efe40a8a6][evidence:evidence-02feb916b9b3].
- Demo date: 2026-09-27 12:00:00+00:00. Revision: 2.


<a id="conversation-5"></a>
## Conversation 5 — Clock change and eligibility (S5)

Fixture: 16.

### Question 1

For LAMP, give the product, delivery timestamp and current seller payout status.

**Golden expectation**

One Desk Lamp, delivered September 27 2026 at 12:00 UTC; payout is held.

### Question 2

At the current demo time, can the operator release that payout? Show the elapsed delivery time and the required hold.

**Golden expectation**

Yes: September 28 at 12:30 UTC is 24 hours 30 minutes after delivery, exceeding the 24-hour hold. Payout remains held until the operator requests release.

### Question 3

What amount would the seller receive for that item, and has it actually been paid yet?

**Golden expectation**

INR 1,169.10 is payable. It has not been paid; status is still held.

### Policy: always nano

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: fixed control

Desk Lamp | Delivered 2026-09-27 12:00:00+00:00 | Payout status held | [evidence:evidence-c3ef242cc864] | revision 5

Demo date used: 2026-09-28 11:00:00+00:00

#### Answer 2 — GPT-5 Nano

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: fixed control

Desk Lamp for ord-b8f486c950: Elapsed delivery time since 2026-09-27 12:00:00+00:00 is 24h30m; required hold is 24h. Current payout status is held; eligible after hold with no active returns. Can release payout now if no returns exist. [evidence:evidence-51e51a5a341a]  revision 5; Demo date used: 2026-09-28 12:30:00+00:00.

#### Answer 3 — GPT-5 Nano

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: fixed control

Desk Lamp: Seller would receive 1169.10 INR; payout status is held, not paid yet. [evidence:evidence-119dae0c4ad7] revision 5; Demo date used: 2026-09-28 12:30:00+00:00.

### Policy: always gpt5

#### Answer 1 — GPT-5

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: fixed control

- Interpretation: Order ord-b8f486c950
- Demo date: 2026-09-28 11:00:00+00:00
- Result: Product Desk Lamp; Delivered at 2026-09-27 12:00:00+00:00; Seller payout status held
- Citation: [evidence-2243e527209e]
- Revision: 5

#### Answer 2 — GPT-5

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: fixed control

- Interpretation: Order ord-b8f486c950
- Demo date: 2026-09-28 12:30:00+00:00
- Result: Yes. Elapsed since delivery: 24h 30m (delivered 2026-09-27 12:00:00+00:00). Required hold: 24h after delivery; no returns present; payout currently held but eligible for operator release.
- Citation: [evidence-b5840ac69eda] [evidence-16541cb4d395] [evidence-476c1cea25f7]
- Revision: 5

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: fixed control

- Interpretation: Order ord-b8f486c950
- Demo date: 2026-09-28 12:30:00+00:00
- Result: Seller would receive ₹1,169.10; not paid yet (payout status: held).
- Citation: [evidence-3aa17022ca7e]
- Revision: 5

### Policy: conversation

#### Answer 1 — GPT-5

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: Fetching product, delivery timestamp, and current seller payout status for a specific order requires cross-entity joins (order_items -> listings -> products; shipments for delivery timestamp; allocations/payouts for current payout status) and careful interpretation of current states across multiple records, not a single bounded lookup.

- Interpretation: Order ord-b8f486c950
- Demo date: 2026-09-28
- Product: Desk Lamp
- Delivered at: 2026-09-27 12:00:00+00:00
- Seller payout: held (₹1,169.10)

Citations: [evidence-23175892f102], delivery also confirmed by events [evidence-6554c6d3550c].  
Revision: 5

#### Answer 2 — GPT-5

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: Fetching product, delivery timestamp, and current seller payout status for a specific order requires cross-entity joins (order_items -> listings -> products; shipments for delivery timestamp; allocations/payouts for current payout status) and careful interpretation of current states across multiple records, not a single bounded lookup.

- Demo date: 2026-09-28 12:30:00+00:00
- Delivery to now: 24h 30m (delivered 2026-09-27 12:00:00+00:00) [evidence-4c49ce71b5b7]
- Required hold: 24 hours after delivery; returns block release [evidence-8f7b6ded0e09]
- Returns on this order: none; payout currently held [evidence-53342b515b49]

Conclusion: Yes—the operator can release the held payout now (hold elapsed and no return blocking).  
Revision: 5

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: Fetching product, delivery timestamp, and current seller payout status for a specific order requires cross-entity joins (order_items -> listings -> products; shipments for delivery timestamp; allocations/payouts for current payout status) and careful interpretation of current states across multiple records, not a single bounded lookup.

- Interpretation: Order ord-b8f486c950, item “Desk Lamp”
- Demo date: 2026-09-28
- Seller amount: ₹1,169.10
- Paid yet?: No—payout status is held (not completed)
- Citation: [evidence-2338fd21f215]
- Revision: 5

### Policy: question

#### Answer 1 — GPT-5 Nano

Grade: **partial**. Reason: Identifies Desk Lamp but fails to retrieve the requested delivery timestamp and held payout status; both are available in the fixture.

Selection: The task requests a bounded retrieval of existing fields (product, delivery timestamp, and payout status) for a specific order, which is a direct, well-scoped read from predefined entities and does not require causal inference or timeline reconciliation.

Desk Lamp; delivery timestamp not available from the current bounded query; payout status not determined from available data. Demo date used: 2026-09-28. [evidence:evidence-0eb4060dc267], revision 5.

#### Answer 2 — GPT-5

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: Determining payout release requires synthesizing delivery status, hold window, refunds/fees, and policy eligibility across multiple records, not a straightforward bounded lookup.

Interpretation: order ord-b8f486c950. Demo date: 2026-09-28 12:30 UTC.
Answer: Yes—eligible to release now. No returns, payout is held for ₹1,169.10. Elapsed since delivery: 24h 30m (delivered 2026-09-27 12:00 UTC). Required hold: 24h after delivery.
Citations: delivery and no-returns/payout status [evidence-2d92ea5a7d15, evidence-5c99214fd0d2]; policy hold rule [evidence-6aea15a1eca7]. Revision 5.

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Requested delivery, elapsed hold, eligibility or unpaid amount matches frozen facts.

Selection: Answer requires aggregating allocation (gross, fee, refunded) and payout (status, amount) across the relevant order item, with consideration of timing/hold policy and whether the payout status is completed. It involves cross-table reconciliation and current state beyond a simple lookup.

Interpretation: order ord-b8f486c950. Demo date: 2026-09-28 12:30 UTC.
Result: Seller amount ₹1,169.10; payout status held → not paid yet.
Citation: [evidence:evidence-e16e32e7a111], revision 5.


<a id="conversation-6"></a>
## Conversation 6 — Routine lookup throughout (S6)

Fixture: 01.

### Question 1

List the products and quantities purchased in order-1.

**Golden expectation**

Two Canvas Weekenders and two Desk Lamps.

### Question 2

For the Desk Lamp item in that order, who is the seller and what was the unit purchase price?

**Golden expectation**

Northstar Goods; INR 1,299 per unit.

### Question 3

What is the purchased line total for those lamps, before deducting seller fees?

**Golden expectation**

Two times INR 1,299 = INR 2,598.

### Policy: always nano

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records.

Selection: fixed control

Interpretation: order-1 includes two purchased items: Canvas Weekender (2) and Desk Lamp (2). Demo date used: 2026-09-27 12:00:00+00:00 (demo clock). Result (products and quantities):
- Canvas Weekender — 2
- Desk Lamp — 2

Citation: [evidence:evidence-4dcd0010bce6]
Revision: 1

#### Answer 2 — GPT-5 Nano

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records.

Selection: fixed control

Northstar Goods; unit price ₹1,299.00 per lamp (quantity 2 in order-1). Demo date used: 2026-09-27 12:00:00+00:00. [evidence:evidence-9f1314765c60] | Revision: 1

#### Answer 3 — GPT-5 Nano

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records.

Selection: fixed control

Desk Lamp line total for order-1 (before seller fees): ₹2,598.00 (2 × ₹1,299.00). Demo date: 2026-09-27 12:00:00+00:00. [evidence:evidence-9f1314765c60] | Revision: 1

### Policy: always gpt5

#### Answer 1 — GPT-5

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records. Incidental date boilerplate did not alter these results.

Selection: fixed control

- Interpretation: order-1 is the Order ID.
- Demo date: 2026-09-27.
- Products and quantities:
  - Canvas Weekender — 2
  - Desk Lamp — 2
- Citation: [evidence-66e06cecec3c]
- Revision: 1

#### Answer 2 — GPT-5

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records. Incidental date boilerplate did not alter these results.

Selection: fixed control

- Interpretation: Desk Lamp item in order-1.
- Demo date: 2026-09-27.
- Result: Seller — Northstar Goods; Unit purchase price — ₹1,299.00.
- Citation: [evidence-fd5e1c19d166]
- Revision: 1

#### Answer 3 — GPT-5

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records. Incidental date boilerplate did not alter these results.

Selection: fixed control

- Interpretation: Desk Lamp line in order-1.
- Demo date: 2026-09-27.
- Result: Purchased line total — ₹2,598.00.
- Citation: [evidence-8bc2cb8cef74]
- Revision: 1

### Policy: conversation

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records.

Selection: Direct bounded retrieval: list order_items for a known order_id and fetch product names and quantities; straightforward join across order_items, listings, and products without complex inference.

Canvas Weekender — 2 units; Desk Lamp — 2 units.
Demo date used: 2026-09-27 12:00:00+00:00 (demo clock).
[Evidence: evidence-b192cc966f93]
Revision: 1

#### Answer 2 — GPT-5 Nano

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records.

Selection: Direct bounded retrieval: list order_items for a known order_id and fetch product names and quantities; straightforward join across order_items, listings, and products without complex inference.

Northstar Goods; Desk Lamp; unit_price 1299.00 INR; quantity 2. Demo date used: 2026-09-27 12:00:00+00:00. [Evidence:evidence-bf7c5bea5092]

#### Answer 3 — GPT-5 Nano

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records.

Selection: Direct bounded retrieval: list order_items for a known order_id and fetch product names and quantities; straightforward join across order_items, listings, and products without complex inference.

2598.00 INR.

Demo date used: 2026-09-27 12:00:00+00:00. [Evidence:evidence-bf7c5bea5092]
Revision: 1

### Policy: question

#### Answer 1 — GPT-5 Nano

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records. Incidental date boilerplate did not alter these results.

Selection: Direct bounded retrieval: identify order_items for order_id = 1 and show product names (via listings/products) with quantities; straightforward join-based lookup with clear entities and metrics.

Canvas Weekender — 2 units; Desk Lamp — 2 units. Demo date used: 2026-09-27 12:00:00+00:00 (inclusive start, exclusive next day). Result rows: Canvas Weekender (2), Desk Lamp (2). [evidence:evidence-7ffdc5b37960], revision 1.

#### Answer 2 — GPT-5 Nano

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records. Incidental date boilerplate did not alter these results.

Selection: Direct bounded retrieval: the request targets a single order item (Desk Lamp) and requires straightforward joins to identify its seller and the unit price at purchase; no complex policy, timing, or event reconstruction needed.

Northstar Goods — 2 units at 1299.00 INR each. Demo date: 2026-09-27 12:00:00+00:00. [evidence:evidence-927d220c2cdc], revision 1.

#### Answer 3 — GPT-5 Nano

Grade: **correct**. Reason: Product quantities, seller/unit price and purchased line total match frozen records. Incidental date boilerplate did not alter these results.

Selection: Direct computation: multiply unit price (1299 INR) by quantity (2) for the lamp line; no ambiguity or external data needed.

2598.00 INR total for 2 × 1299.00 INR lamps (before seller fees). Demo date: 2026-09-27 12:00:00+00:00. [evidence:evidence-927d220c2cdc], revision 1.

