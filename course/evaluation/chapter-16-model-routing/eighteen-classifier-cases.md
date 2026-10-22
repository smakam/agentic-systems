# Eighteen cases: classifier study

Historical September 2026 saved-answer comparison. These are the cases underlying the slide results, not the new native gateway demo. Each classifier selected a candidate trajectory without seeing the expected answers or grades. Two cases include follow-ups; a case passes only if its required turns pass.

The small known-case sample illustrates methodology. Repeat with more representative cases and consistent grading before drawing broader conclusions.

| No. | Original case | Opening question |
| --- | --- | --- |
| [1](#case-1) | 02 | What products and quantities are in order-1, and who sells them? |
| [2](#case-2) | 04 | Show orders placed today for Cedar & Co. that are not yet delivered. |
| [3](#case-3) | 08 | Show orders for Acme. |
| [4](#case-4) | 09 | Has the payment gone through for order-1? |
| [5](#case-5) | 10 | What is the current return window? |
| [6](#case-6) | 11 | What return window did the policy specify on June 1, 2025? |
| [7](#case-7) | 14 | Why has Cedar not been paid for order-1? |
| [8](#case-8) | 15 | Why is the return for ord-f378827237 in manual review? Did the seller reject it? |
| [9](#case-9) | 16 | Can the operator release the payout for ord-b8f486c950 now? |
| [10](#case-10) | 17 | Can the operator release the payout for ord-b3431443e7 now? |
| [11](#case-11) | 20 | Explain the refund history for ord-6f3604a5fe. |
| [12](#case-12) | 21 | Explain the refund history for ord-aaa1768930. |
| [13](#case-13) | 23 | Did the payout incident affect every seller? |
| [14](#case-14) | 24 | After returning one Canvas Weekender, what remains payable to Cedar? |
| [15](#case-15) | 26 | Reconcile all captured money across seller balances. |
| [16](#case-16) | 27 | Show orders for Cedar. |
| [17](#case-17) | 28 | What is Cedar's unpaid balance? |
| [18](#case-18) | 30 | Refund ord-b59d8ba410 now and tell me when you have sent the money. |

<a id="case-1"></a>
## Case 1 — original case 02

**Questions**

1. What products and quantities are in order-1, and who sells them?

**Golden expectation**

['Order order-1 contains Canvas Weekender ×2, sold by Cedar & Co., and Desk Lamp ×2, sold by Northstar Goods.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 Nano | SIMPLE | correct |
| JEV classifier | GPT-5 Nano | SIMPLE | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | correct |
| Keyword rules + heuristic fallback | GPT-5 Nano | SIMPLE | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Correct products, quantities and sellers.

#### Answer 1

Interpretation: order-1
Result:
- Canvas Weekender — qty 2 — sold by Cedar & Co.
- Desk Lamp — qty 2 — sold by Northstar Goods
Citation: [evidence-c5088b410491]
Revision: 1 (demo clock 2026-09-27 12:00:00+00:00)


### GPT-5 Nano — saved answer

Case grade: **correct**. Review: 

#### Answer 1

Interpretation: Order-1 contains two items: Canvas Weekender by Cedar & Co. and Desk Lamp by Northstar Goods, each with quantity 2.
Demo date used: 2026-09-27 12:00:00+00:00 (demo clock).
Result: 
- Canvas Weekender — Cedar & Co. — quantity 2
- Desk Lamp — Northstar Goods — quantity 2
[Citation: evidence-7d04a8b7e233]
Revision: 1


<a id="case-2"></a>
## Case 2 — original case 04

**Questions**

1. Show orders placed today for Cedar & Co. that are not yet delivered.

**Golden expectation**

['One order matches: {TODAY.order}, placed September 27, 2026 at 12:00 UTC for Cedar & Co. Its shipment is pending. The order contains one Canvas Weekender.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 Nano | SIMPLE | correct |
| JEV classifier | GPT-5 Nano | SIMPLE | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | correct |
| Keyword rules + heuristic fallback | GPT-5 Nano | SIMPLE | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Correct sole Cedar order for the UTC day and pending shipment.

#### Answer 1

- Interpretation: Seller “Cedar & Co.” (seller-1)
- Demo date: 2026-09-27
- Result:
  - ord-eefcffe1c2 — Canvas Weekender x1, ₹2,499.00; payment captured; shipment pending (not delivered)
- Citation: [evidence-1edac1373352], [evidence-98aa326fea39]
- Revision: 4


### GPT-5 Nano — saved answer

Case grade: **correct**. Review: 

#### Answer 1

Interpretation: Cedar & Co. order(s) placed today not yet delivered.

Demo date used: 2026-09-27 (clock from snapshot)

Result: 1 order
- Order ID: ord-eefcffe1c2
- Created at: 2026-09-27 12:00:00+00
- Customer: buyer
- Shipment status: pending
- Delivered at: null

Citation: [evidence:evidence-da86493cba3e]
Revision: 4


<a id="case-3"></a>
## Case 3 — original case 08

**Questions**

1. Show orders for Acme.

**Golden expectation**

['I could not find a seller or product named Acme. Could you provide the intended name or identifier?']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 Nano | SIMPLE | correct |
| JEV classifier | GPT-5 Nano | SIMPLE | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | correct |
| Keyword rules + heuristic fallback | GPT-5 Nano | SIMPLE | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Identifies absent entity and asks seller/product plus exact name without guessing.

#### Answer 1

I can’t find “Acme” as a seller or product in the current catalog. Is Acme a seller or a product, and what’s the exact name or ID you want me to use? [evidence:evidence-8c49f77d6bad]


### GPT-5 Nano — saved answer

Case grade: **correct**. Review: Correctly identified no match and requested clarification. Avoid suggesting Cedar without evidence, listing every product, and showing the demo clock. The response could be shorter.

#### Answer 1

Acme does not match any seller or product name in the catalog. Did you mean the seller Cedar & Co. or one of these products: Canvas Weekender, Desk Lamp, Ceramic Mug Set, Trail Backpack, Wireless Keyboard, Linen Notebook? (Demo clock: 2026-09-27 12:00:00+00:00)


<a id="case-4"></a>
## Case 4 — original case 09

**Questions**

1. Has the payment gone through for order-1?

**Golden expectation**

['Do you mean the buyer’s payment or the payment to the sellers?']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 Nano | SIMPLE | partially_correct |
| JEV classifier | GPT-5 Nano | SIMPLE | partially_correct |
| OpenRouter low | GPT-5 Nano | Not supplied | partially_correct |
| Keyword rules + heuristic fallback | GPT-5 Nano | SIMPLE | partially_correct |
| Default heuristic | GPT-5 Nano | SIMPLE | partially_correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | partially_correct |

### GPT-5 — saved answer

Case grade: **partially_correct**. Review: Correct buyer capture fact, but gives an unqualified yes without distinguishing seller payout failure or asking which payment. Same material omission as the saved nano answer.

#### Answer 1

Interpretation: order-1
Demo date: 2026-09-27
Result: Yes—payment captured for ₹7,596.00 (payment-1) on 2026-09-24.
Citation: [evidence-387c5bd1d9e3]
Revision: 1


### GPT-5 Nano — saved answer

Case grade: **partially_correct**. Review: 

#### Answer 1

Interpretation: The payment has gone through (captured) for order-1.
Demo date used: 2026-09-27 12:00:00+00:00 (demo clock).
Result: Order status = paid; Payment status = captured; Amount = 759600 paise = INR 7596.00; Payment ID = payment-1.
Citation: [evidence:evidence-4dbc53f28e08]
Revision: 1


<a id="case-5"></a>
## Case 5 — original case 10

**Questions**

1. What is the current return window?

**Golden expectation**

['The current return window is 30 days after delivery.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 Nano | SIMPLE | correct |
| JEV classifier | GPT-5 Nano | SIMPLE | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | correct |
| Keyword rules + heuristic fallback | GPT-5 Nano | SIMPLE | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Correct current 30-day policy, supported by current policy retrieval.

#### Answer 1

30 days after delivery. [evidence:evidence-7b94b7aecc4b]


### GPT-5 Nano — saved answer

Case grade: **correct**. Review: 

#### Answer 1

Interpretation: The current return window is 30 days after delivery. Demo date used: 2026-09-27. Evidence: [evidence-0cf9189d4f1c].


<a id="case-6"></a>
## Case 6 — original case 11

**Questions**

1. What return window did the policy specify on June 1, 2025?

**Golden expectation**

['On June 1, 2025, the policy specified a 14-day return window.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 Nano | SIMPLE | correct |
| JEV classifier | GPT-5 Nano | SIMPLE | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | correct |
| Keyword rules + heuristic fallback | GPT-5 | COMPLEX | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Correct historical 14-day window and effective date; historical policy retrieval verified.

#### Answer 1

14 days [evidence-dfc9693739fd]. Interpretation: returns policy effective on 2025-06-01. Revision: 1.


### GPT-5 Nano — saved answer

Case grade: **correct**. Review: 

#### Answer 1

Interpretation: Return window was 14 days under the retired returns policy version (v0).  
Demo date used: 2025-06-01 (effective_at).  
Result: 14 days.  
Citation: [evidence:evidence-0a2add631505]  
Revision: 1 (policy snapshot used: returns-v0.md, v0).


<a id="case-7"></a>
## Case 7 — original case 14

**Questions**

1. Why has Cedar not been paid for order-1?

**Golden expectation**

['Cedar has not been paid for order-1 because the recorded payout attempt failed with a provider timeout. The delivery hold has already elapsed.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 | COMPLEX | correct |
| JEV classifier | GPT-5 | COMPLEX | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | partially_correct |
| Keyword rules + heuristic fallback | GPT-5 | COMPLEX | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | partially_correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | partially_correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Identifies recorded provider timeout and failed Cedar payout, without inventing non-delivery.

#### Answer 1

- Interpretation: “Cedar” = seller Cedar & Co. (seller-1)
- Demo date: 2026-09-27
- Result: Cedar’s payout for order-1 failed due to a provider timeout. Current payout status: failed; amount ₹4,498.20 not paid out. The item was delivered on 2026-09-25, so failure was not due to eligibility but the provider error. [evidence: evidence-f946b6fb3cbe; evidence-8bd469aed0e7]
- Revision: 1


### GPT-5 Nano — saved answer

Case grade: **partially_correct**. Review: did not mention provider timeout for failure

#### Answer 1

Interpretation: Cedar & Co. has a payout for part of order-1, but the payout is not completed; status is failed (allocation-1, payout-1). The item delivered 2026-09-25, but payout failed, so Cedar is not paid yet.

Demo date used: 2026-09-27.

Result: payout failed; no completed payout yet. Next step: review payout retry and related events.

[citation: evidence-a4eb8c7a7192]


<a id="case-8"></a>
## Case 8 — original case 15

**Questions**

1. Why is the return for ord-f378827237 in manual review? Did the seller reject it?

**Golden expectation**

['The return for order {LAMP.order} is in manual review because the seller was paid before the return was requested. This demo does not support recovering that payout automatically. There is no evidence that the seller rejected the return.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 | COMPLEX | correct |
| JEV classifier | GPT-5 | COMPLEX | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | correct |
| Keyword rules + heuristic fallback | GPT-5 | COMPLEX | correct |
| Default heuristic | GPT-5 | MEDIUM | correct |
| Semantic matching + heuristic fallback | GPT-5 | MEDIUM | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Explains paid-before-return policy trigger and absence of seller rejection. It does not explicitly spell out unsupported recovery, but the causal explanation answers the question.

#### Answer 1

- Why manual review: The item’s seller payout was already completed before the buyer requested the return, and post‑payout refunds require manual review in this demo. [evidence:evidence-235d5fa24194] [evidence:evidence-3fa4897bb7fa] [evidence:evidence-a81efedf3654]
- Did the seller reject it: No rejection is recorded; the timeline only shows the buyer’s return request, not a seller decision. [evidence:evidence-3fa4897bb7fa]


### GPT-5 Nano — saved answer

Case grade: **correct**. Review: 

#### Answer 1

Interpretation: The return for ord-f378827237 item item-24111a4b9b is in manual_review (return_status = manual_review); there is no recorded seller rejection. The event timeline shows a buyer-initiated return request on 2026-09-28 and a payout was processed earlier; no follow-up rejection event is present. So, it’s awaiting decision, not rejected by the seller. [evidence:evidence-1b676e4bbbd0] [evidence:evidence-2428a2fa97c5] Demo date used: 2026-09-28.


<a id="case-9"></a>
## Case 9 — original case 16

**Questions**

1. Can the operator release the payout for ord-b8f486c950 now?

**Golden expectation**

['No. The payout for order {LAMP.order} cannot be released yet: only 23 hours have passed since delivery, so one hour of the 24-hour hold remains.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 | COMPLEX | correct |
| JEV classifier | GPT-5 | COMPLEX | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | partially_correct |
| Keyword rules + heuristic fallback | GPT-5 | COMPLEX | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | partially_correct |
| Semantic matching + heuristic fallback | GPT-5 | COMPLEX | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Correct no decision, hold endpoint and snapshot clock establish one hour remains.

#### Answer 1

No. Delivery was at 2026-09-27 12:00:00+00:00; the 24-hour hold ends at 2026-09-28 12:00:00+00:00. No returns are recorded, and the payout is held for ₹1,169.10. Policy requires delivery confirmation plus a 24-hour hold; returns would block release. Interpretation: payout eligibility for order ord-b8f486c950. Demo clock: 2026-09-28 11:00:00+00:00. Citations: delivery and records [evidence-71d4a03aabd1; evidence-5adc2558dbe8], policy [evidence-5c7b9f935b9d]. Revision: 5.


### GPT-5 Nano — saved answer

Case grade: **partially_correct**. Review: 

#### Answer 1

Interpretation: The ord-b8f486c950 payout is currently held and cannot be released yet (payout status: held; amount 116910 paise = ₹1169.10).

Demo date used: 2026-09-28 (clock in snapshot).

Result: Payout remains on hold; no release action possible at this moment.

Citation: [evidence:evidence-96e37ad1445c] (current payout_status and amount for order)

Revision: 5


<a id="case-10"></a>
## Case 10 — original case 17

**Questions**

1. Can the operator release the payout for ord-b3431443e7 now?

**Golden expectation**

['Yes. At 2026-09-28 12:30 UTC, delivery at 2026-09-27 12:00 UTC was 24.5 hours ago. No active return blocks release. Eligible, not already paid; operator action required.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 | COMPLEX | correct |
| JEV classifier | GPT-5 | COMPLEX | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | partially_correct |
| Keyword rules + heuristic fallback | GPT-5 | COMPLEX | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | partially_correct |
| Semantic matching + heuristic fallback | GPT-5 | COMPLEX | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Correct eligibility, passed hold, no returns and still-held unpaid state.

#### Answer 1

Interpretation: Order ord-b3431443e7
Demo date used: 2026-09-28
Result: Yes—eligible to release now. Delivered 2026-09-27 12:00Z; 24-hour hold passed; no returns; payout currently held for ₹1,169.10.
Citations: delivery and no returns [evidence-d49b02b0c0a7, evidence-777722304f9c]; policy requires delivery + 24h and no active returns [evidence-91b4e247d5bf].
Revision: 5


### GPT-5 Nano — saved answer

Case grade: **partially_correct**. Review: User confirmed partial: release decision is correct but within-the-hold-window wording contradicts elapsed-hold explanation.

#### Answer 1

Yes. As of 2026-09-28 12:30:00+00:00 (demo clock), the payout for ord-b3431443e7 is held but eligible for release after the 24-hour hold and no returns/refunds are pending. Release would move 116910 paise (1169.10 INR) to completed payout.

Evidence: payout-7380e42197 held; order history shows no returns/refunds and delivery completed within the hold window. [evidence:12db3b247bff] [evidence:b3bb09ff2d1d]


<a id="case-11"></a>
## Case 11 — original case 20

**Questions**

1. Explain the refund history for ord-6f3604a5fe.

**Golden expectation**

['Order {TRAIL.order} has one failed refund attempt and no completed refund. The return remains received, and the buyer has not been refunded.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 Nano | SIMPLE | correct |
| JEV classifier | GPT-5 | COMPLEX | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | correct |
| Keyword rules + heuristic fallback | GPT-5 | COMPLEX | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Correct failed attempt, no money refunded, received return history and intended versus actual amounts.

#### Answer 1

Summary [evidence: evidence-930a64e5ebb7, evidence-2f68e7c96ec9]
Order ord-6f3604a5fe had a return with one refund attempt that failed; no money was refunded, and the seller’s payout remains calculated but held.

Chronology [evidence: evidence-930a64e5ebb7]
- Purchase recorded.
- Item dispatched and delivered.
- Buyer requested a return; return approved and received.
- Refund attempt recorded with outcome “failed.”

Final amounts [evidence: evidence-2f68e7c96ec9]
- Intended refund: ₹1,899.00; actually refunded: ₹0.00.
- Allocation: gross ₹1,899.00; fee ₹189.90.
- Seller payable (payout amount): ₹1,709.10 (status: held).


### GPT-5 Nano — saved answer

Case grade: **correct**. Review: 

#### Answer 1

Short summary:
Refund process for ord-6f3604a5fe started with a return, but the refund attempt failed; a payout of 170,910 paise is currently held. The refund is not completed, and no payout is yet released. [evidence:evidence-2b18f8b86b70] [evidence:evidence-94bc625b22e1]

Chronological business steps:
- Purchase and dispatch for order ord-6f3604a5fe (revision 2). [evidence:evidence-94bc625b22e1]
- Dispatch acknowledged (revision 3); delivery confirmed (revision 4). [evidence:evidence-94bc625b22e1]
- Buyer requests return (revision 5); operator approves (revision 6). [evidence:evidence-94bc625b22e1]
- Return received (revision 7). [evidence:evidence-94bc625b22e1]
- Refund attempt recorded as failed (revision 8); gross 189,900 paise, refund 0 paise; fee 18,990 paise; payout 170,910 paise held. [evidence:evidence-2b18f8b86b70]

Final refund and seller payable amounts:
- Refund amount: 189,900 paise; refunded so far: 0 paise. [evidence:evidence-2b18f8b86b70]
- Payout held: 170,910 paise. No payout released yet. [evidence:evidence-2b18f8b86b70]


<a id="case-12"></a>
## Case 12 — original case 21

**Questions**

1. Explain the refund history for ord-aaa1768930.

**Golden expectation**

['The refund for order {TRAIL.order} failed initially, then succeeded on retry. The buyer was refunded ₹1,899 once. The return is now refunded, and no seller payout is due for this item.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 | COMPLEX | correct |
| JEV classifier | GPT-5 | COMPLEX | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | partially_correct |
| Keyword rules + heuristic fallback | GPT-5 | COMPLEX | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | partially_correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | partially_correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: User confirmed correct factual answer. Citation-link defect remains a separate presentation finding; no downgrade for that defect.

#### Answer 1

Summary
Order ord-aaa1768930 was purchased, delivered, then returned. An initial refund attempt failed, followed by a successful full refund. Allocation is fully refunded; payout shows held with zero amount. [evidence-evidence-a834554741f1][evidence-evidence-9e7b42592090]

Chronological business steps
- Purchase of 1 item. 
- Shipment dispatched and delivered.
- Buyer requested a return; operator approved and received it.
- Refund attempt recorded as failed.
- Subsequent refund completed successfully. [evidence-evidence-a834554741f1]

Final amounts
- Gross: ₹1,899.00; Refunded: ₹1,899.00; Refund status: completed.
- Payout status: held; Payout amount: ₹0.00.
No payout due - fully refunded; a stored held status does not mean money is owed. [evidence-evidence-9e7b42592090]


### GPT-5 Nano — saved answer

Case grade: **partially_correct**. Review: 

#### Answer 1

Short summary:
- Refund path completed for ord-aaa1768930; initial refund attempt failed, then completed. No payout due - fully refunded. [evidence:evidence-6e406a541b21]

Chronological business steps:
- Purchase: order placed for item-ebe8569888. [evidence-6e406a541b21]
- Dispatch and deliver: item dispatched and delivered to buyer. [evidence-6e406a541b21]
- Return flow: buyer requested return; operator approved; item received back. [evidence-6e406a541b21]
- Refund attempts: refund initiated, first outcome failed, then completed. [evidence-6e406a541b21]

Final refund and seller payable amounts:
- Refund amount: 1899.00 INR (189900 paise) completed. Payout amount: 0 paise. Therefore: No payout due - fully refunded. [evidence:evidence-6e406a541b21]


<a id="case-13"></a>
## Case 13 — original case 23

**Questions**

1. Did the payout incident affect every seller?

**Golden expectation**

['The documented incident affects payout-1 for Cedar & Co. There is insufficient evidence to say it affected every seller.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 | COMPLEX | correct |
| JEV classifier | GPT-5 | COMPLEX | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | incorrect |
| Keyword rules + heuristic fallback | GPT-5 | COMPLEX | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | incorrect |
| Semantic matching + heuristic fallback | GPT-5 | COMPLEX | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Correctly limits documented impact to Cedar payout-1 and does not assert other sellers definitely unaffected.

#### Answer 1

Interpretation: “payout incident” refers to the confirmed incident about payout failures.
Demo date: 2026-09-27
Result: No. The incident evidences only payout-1 failing for Cedar & Co.; no broader seller impact is recorded.
Citations: incident scope and note [evidence-9dbd95f0ef2b]; affected payout and seller [evidence-e866a2772c43].
Revision: 1


### GPT-5 Nano — saved answer

Case grade: **incorrect**. Review: 

#### Answer 1

Ambiguity: does “Cedar” refer to Cedar & Co. (seller-1) or to a product whose name includes Cedar? Please confirm which you mean.


<a id="case-14"></a>
## Case 14 — original case 24

**Questions**

1. After returning one Canvas Weekender, what remains payable to Cedar?

**Golden expectation**

['₹2,249.10 remains payable to Cedar. One Canvas Weekender was refunded for ₹2,499. The other unit has ₹2,499 remaining gross value, less the adjusted marketplace fee of ₹249.90.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 | COMPLEX | correct |
| JEV classifier | GPT-5 | COMPLEX | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | partially_correct |
| Keyword rules + heuristic fallback | GPT-5 Nano | SIMPLE | partially_correct |
| Default heuristic | GPT-5 Nano | SIMPLE | partially_correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | partially_correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Correct INR2249.10. SQL explicitly retrieves purchased/returned quantities, gross4998, refund2499, adjusted fee249.90 and computes remaining payable. Unlike saved nano24, support includes item/refund linkage, not just a seller balance lookup. Concise response accepted under material-completeness rubric.

#### Answer 1

- Interpretation: Cedar = seller “Cedar & Co.”; product “Canvas Weekender”
- Demo date: 2026-09-27
- Result: Remaining payable after returning one unit is ₹2,249.10
- Citation: [evidence-181712f2defe]
- Revision: 5


### GPT-5 Nano — saved answer

Case grade: **partially_correct**. Review: 

#### Answer 1

Interpretation: Cedar & Co. (seller-1) remains payable 2249.10 INR after returning one Canvas Weekender.

Demo date: 2026-09-27 12:00:00+00:00 (clock in snapshot).

Result: 224910 paise unpaid.

Citation: [evidence:evidence-c3b9ea0cba68]

Revision: 5


<a id="case-15"></a>
## Case 15 — original case 26

**Questions**

1. Reconcile all captured money across seller balances.

**Golden expectation**

['The ₹9,394 captured reconciles to ₹0 refunded + ₹939.40 marketplace fees + ₹8,454.60 unpaid to sellers + ₹0 paid out. There is no unexplained difference.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 | COMPLEX | correct |
| JEV classifier | GPT-5 | COMPLEX | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | correct |
| Keyword rules + heuristic fallback | GPT-5 | COMPLEX | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: All seller balances and aggregate reconcile exactly, no double counting.

#### Answer 1

Interpretation: Reconcile captured vs refunded+fees+paid_out+unpaid by seller. Demo date: 2026-09-27.

Seller              | Captured | Refunded | Fees  | Paid out | Unpaid  | Check
Cedar & Co.         | ₹4,998.00| ₹0.00    | ₹499.80| ₹0.00   | ₹4,498.20| OK
Everyday Studio     | ₹1,798.00| ₹0.00    | ₹179.80| ₹0.00   | ₹1,618.20| OK
Northstar Goods     | ₹2,598.00| ₹0.00    | ₹259.80| ₹0.00   | ₹2,338.20| OK
Total               | ₹9,394.00| ₹0.00    | ₹939.40| ₹0.00   | ₹8,454.60| OK

Citation: [evidence-97492ebb4ba3]. Revision: 1.


### GPT-5 Nano — saved answer

Case grade: **correct**. Review: 

#### Answer 1

Interpretation: Reconciled seller balances across all captured funds; 0 paise discrepancy per seller as of the demo clock.

Demo date used: 2026-09-27 12:00:00+00:00 (clock in snapshot)

Result (paise → INR)
- Cedar & Co. (seller-1): captured 499800; refunded 0; fees 49980; unpaid 449820; paid_out 0; reconciliation_diff 0
  - In rupees: 4,998.00 | fees 499.80 | unpaid 4,498.20 | payout 0.00
  - [evidence:evidence-d1e8e3aea37d]
- Northstar Goods (seller-2): captured 259800; refunded 0; fees 25980; unpaid 233820; paid_out 0; reconciliation_diff 0
  - In rupees: 2,598.00 | fees 259.80 | unpaid 2,338.20 | payout 0.00
  - [evidence:evidence-d1e8e3aea37d]
- Everyday Studio (seller-3): captured 179800; refunded 0; fees 17980; unpaid 161820; paid_out 0; reconciliation_diff 0
  - In rupees: 1,798.00 | fees 179.80 | unpaid 1,618.20 | payout 0.00
  - [evidence:evidence-d1e8e3aea37d]

Cited: seller_balances data from analytics.seller_balances joined with analytics.sellers.


<a id="case-16"></a>
## Case 16 — original case 27

**Questions**

1. Show orders for Cedar.
2. I mean the seller.

**Golden expectation**

['Do you mean the seller Cedar & Co., or the product Cedar Desk?', 'For the seller Cedar & Co., the matching order is order-1, containing two Canvas Weekenders sold by Cedar & Co.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 Nano | SIMPLE | incorrect |
| JEV classifier | GPT-5 Nano | SIMPLE | incorrect |
| OpenRouter low | GPT-5 Nano | Not supplied | incorrect |
| Keyword rules + heuristic fallback | GPT-5 Nano | SIMPLE | incorrect |
| Default heuristic | GPT-5 Nano | SIMPLE | incorrect |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | incorrect |

### GPT-5 — saved answer

Case grade: **correct**. Review: Clarifies ambiguous Cedar, then correctly returns Cedar seller order-1 and two Canvas Weekenders. Printed payment7596 is whole-order payment, not seller proceeds; labeling could be clearer but no wrong value.

#### Answer 1

Did you mean the seller “Cedar & Co.” or the product “Cedar Desk”?

#### Answer 2

Interpretation: seller “Cedar & Co.” (seller-1). Demo date: 2026-09-27.

Orders:
- order-1 (2026-09-24) buyer; item-1 Canvas Weekender x2 @ ₹2,499.00 = ₹4,998.00; payment payment-1 ₹7,596.00

Citation: [evidence-8fb7214bd171], [evidence-89f0245a278e]. Revision: 1.


### GPT-5 Nano — saved answer

Case grade: **incorrect**. Review: 

#### Answer 1

There are two plausible matches for “Cedar”:
- Cedar Desk (product)
- Cedar & Co. (seller)

Which would you like me to show orders for? (Please specify “product Cedar Desk” or “seller Cedar & Co.”)

#### Answer 2

 interpretation: Cedar & Co. (seller) orders for today (demo clock 2026-09-27 12:00:00+00:00)
 demo date used: 2026-09-27
 result: no matching orders found for today
 citation: [evidence:evidence-5ce125ecce21]
 revision: 1


<a id="case-17"></a>
## Case 17 — original case 28

**Questions**

1. What is Cedar's unpaid balance?
2. What is it now?

**Golden expectation**

['Cedar’s unpaid balance is ₹4,498.20.', 'Cedar’s unpaid balance is now ₹6,747.30, an increase of ₹2,249.10.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 Nano | SIMPLE | correct |
| JEV classifier | GPT-5 Nano | SIMPLE | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | correct |
| Keyword rules + heuristic fallback | GPT-5 Nano | SIMPLE | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | correct |
| Semantic matching + heuristic fallback | GPT-5 Nano | SIMPLE | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: User confirmed correct: current balance and fresh retrieval are correct; printing the increase was not required.

#### Answer 1

- Interpretation: “Cedar” is the seller Cedar & Co. (seller-1).
- Demo date: 2026-09-27.
- Unpaid balance: ₹4,498.20.
- Citation: [evidence-aa5dedcdd222], [evidence-1dbc369f54d6].
- Revision: 1.

#### Answer 2

- Interpretation: “Cedar” is the seller Cedar & Co. (seller-1).
- Demo date: 2026-09-27.
- Unpaid balance: ₹6,747.30.
- Citation: [evidence-1f14a16140ae].
- Revision: 2.


### GPT-5 Nano — saved answer

Case grade: **correct**. Review: User approved consistent treatment with GPT-5: both balances and fresh retrieval are correct; printing the increase was not required. Historical partial grade is preserved in the original human review.

#### Answer 1

Cedar & Co. has an unpaid balance of ₹4,498.20 (449,820 paise) as of 2026-09-27 12:00:00+00:00. [evidence:evidence-46dc8c10a350]

#### Answer 2

Cedar & Co. has an unpaid balance of ₹6,747.30 (6,74730 paise) as of 2026-09-27 12:00:00+00:00. [evidence:evidence-e6a9af7f19ac]


<a id="case-18"></a>
## Case 18 — original case 30

**Questions**

1. Refund ord-b59d8ba410 now and tell me when you have sent the money.

**Golden expectation**

['I cannot issue the refund for order {TRAIL.order}; this support assistant is read-only. An operator must perform the refund. I have not sent any money.']

**Classifier choices**

| Configuration | Selected answer model | Tier | Saved case grade |
| --- | --- | --- | --- |
| Nano LLM classifier | GPT-5 | COMPLEX | correct |
| JEV classifier | GPT-5 | COMPLEX | correct |
| OpenRouter low | GPT-5 Nano | Not supplied | partially_correct |
| Keyword rules + heuristic fallback | GPT-5 | COMPLEX | correct |
| Default heuristic | GPT-5 Nano | SIMPLE | partially_correct |
| Semantic matching + heuristic fallback | GPT-5 | COMPLEX | correct |

### GPT-5 — saved answer

Case grade: **correct**. Review: Explicitly refuses money movement, says no refund yet, directs operator to execute; business state unchanged.

#### Answer 1

I can’t issue refunds or move money. Checked ord-b59d8ba410: the return is received, but no refund has been created yet. Allocation: ₹1,899.00 gross, fees ₹189.90, refunded ₹0.00; seller payout is on hold at ₹1,709.10. Please issue the refund in the operator console; once processed, it will appear in the order timeline. [evidence:evidence-94e057dfdc45] [evidence:evidence-0d00d9ae5757] Revision 7.


### GPT-5 Nano — saved answer

Case grade: **partially_correct**. Review: 

#### Answer 1

Interpretation: No completed refund exists yet for order ord-b59d8ba410; a return was received and approved, but refunds have not been issued in the current snapshot. Demo date used: 2026-09-27 (clock). Result: refund would be initiated via operator UI; current payout is held at 170,910 paise for the item. Evidence: refunds row absence (evidence-0eb8f2597d5e); return/approval timeline (evidence-51b5047a1904); current order state (evidence-6d92c089eb72). Revision: 7.

