# Detailed answers and golden references

Display numbers 1–18 follow this comparison. Original source case identifiers are retained. Golden references specify required business facts; equivalent wording is acceptable. Human labels and Claude v3 judgments are separate.

<a id="case-1"></a>
## Case 1 — source case 02

**Question sequence**

1. What products and quantities are in order-1, and who sells them?

**Expected answer / original golden facts**

Canvas Weekender ×2, Cedar; Desk Lamp ×2, Northstar. Item, listing/product and seller joins.

<a id="case-1-nano-human"></a>
<a id="case-1-nano-claude"></a>
### GPT-5 nano

**Model answer**

Interpretation: Order-1 contains two items: Canvas Weekender by Cedar & Co. and Desk Lamp by Northstar Goods, each with quantity 2.
Demo date used: 2026-09-27 12:00:00+00:00 (demo clock).
Result: 
- Canvas Weekender — Cedar & Co. — quantity 2
- Desk Lamp — Northstar Goods — quantity 2
[Citation: evidence-7d04a8b7e233]
Revision: 1

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer lists both products, their quantities and their sellers, and all three match the fixture. The cited query performs the required item, listing, product and seller joins for order-1. The snapshot revision and demo clock are stated. The answer is concise and clear.

<a id="case-1-gpt54-human"></a>
<a id="case-1-gpt54-claude"></a>
### GPT-5.4

**Model answer**

| Product | Qty | Seller |
|---|---:|---|
| Canvas Weekender | 2 | Cedar & Co. |
| Desk Lamp | 2 | Northstar Goods |

[evidence:evidence-1eb3549a9a22] Revision 1

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer names both order-1 products with correct quantities and sellers, and matches the fixture truth. It cites a query that performs the required order_items, listings, products and sellers joins, and it states the snapshot revision. The presentation is a clear table.

<a id="case-2"></a>
## Case 2 — source case 04

**Question sequence**

1. Show orders placed today for Cedar & Co. that are not yet delivered.

**Expected answer / original golden facts**

Exactly the new Cedar order; exclude Northstar and the pre-midnight control. UTC day boundary and current shipment state.

<a id="case-2-nano-human"></a>
<a id="case-2-nano-claude"></a>
### GPT-5 nano

**Model answer**

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

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer returns exactly the one correct Cedar & Co. order placed on 2026-09-27 UTC that is not yet delivered. It correctly excludes the Northstar order and the pre-midnight control order. The cited query uses correct seller filtering, UTC day boundaries from the demo clock and current shipment status, at snapshot revision 4. The presentation is concise and clear.

<a id="case-2-gpt54-human"></a>
<a id="case-2-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Interpretation: Cedar & Co. = seller Cedar & Co. Demo date used: 2026-09-27.

| order | placed_at | item | qty | item price | shipment |
|---|---|---:|---:|---:|---|
| ord-eefcffe1c2 | 2026-09-27 12:00 UTC | Canvas Weekender | 1 | ₹2499.00 | pending |

Citation: [evidence-edab00c508f0] Revision: 4

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer lists exactly the one qualifying Cedar & Co. order. It correctly excludes the Northstar order and the order placed one second before midnight UTC. The item, quantity, price and pending shipment status all match the fixture. The retrieved SQL uses the correct seller filter, UTC day window and not-delivered condition. The answer cites the evidence handle and snapshot revision, and the table is clear.

<a id="case-3"></a>
## Case 3 — source case 08

**Question sequence**

1. Show orders for Acme.

**Expected answer / original golden facts**

No matching seller/product in this fixture; request the intended name or identifier. Do not invent an entity or report all orders.

<a id="case-3-nano-human"></a>
<a id="case-3-nano-claude"></a>
### GPT-5 nano

**Model answer**

Acme does not match any seller or product name in the catalog. Did you mean the seller Cedar & Co. or one of these products: Canvas Weekender, Desk Lamp, Ceramic Mug Set, Trail Backpack, Wireless Keyboard, Linen Notebook? (Demo clock: 2026-09-27 12:00:00+00:00)

**Human:** correct — 2/2

Correctly identified no match and requested clarification. Avoid suggesting Cedar without evidence, listing every product, and showing the demo clock. The response could be shorter.

**Claude v3:** correct — 2/2

The candidate correctly found no match for 'Acme', supported by an empty name search and the complete catalog. It asked for clarification without dumping orders or inventing an entity. One minor oddity: it suggests only Cedar & Co. among sellers and omits Northstar Goods and Everyday Studio, with no stated basis for that choice. Because this is phrased as a question rather than an attribution, it does not materially mislead, and the clarification goal is still met.

<a id="case-3-gpt54-human"></a>
<a id="case-3-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Did you mean seller **Cedar & Co.**?

**Human:** partially_correct — 1/2

Asked for clarification, but guessed Cedar & Co. without evidence and did not say Acme was not found. Better: ‘I couldn’t find a seller or product named Acme. Are you referring to a seller or a product? Please provide the correct name or identifier.

**Claude v3:** partially_correct — 1/2

The candidate retrieved the full, untruncated catalog of business names, which is enough to see that no Acme entity exists. It correctly avoided reporting orders and asked for clarification. However, it did not state that no match was found. It also steered the user toward one arbitrary seller, Cedar & Co., without justification and without listing the alternatives or asking for an identifier. The core clarification behavior is present but materially incomplete and somewhat leading, so it is partial rather than fully correct.

<a id="case-4"></a>
## Case 4 — source case 09

**Question sequence**

1. Has the payment gone through for order-1?

**Expected answer / original golden facts**

{
  "essential_facts": [
    "Distinguish captured buyer payment from seller payout. Accept either a clarification question or an explicitly qualified answer distinguishing both meanings.",
    "Buyer payment captured; seller payout has a failure. Do not imply seller settlement completed."
  ],
  "evidence_requirements": [
    "Any factual payment/payout statements must match retrieved records. Clarification alone needs no citation."
  ],
  "optional_details": [
    "Enumerating every held or failed seller payout, amount and date."
  ]
}

<a id="case-4-nano-human"></a>
<a id="case-4-nano-claude"></a>
### GPT-5 nano

**Model answer**

Interpretation: The payment has gone through (captured) for order-1.
Demo date used: 2026-09-27 12:00:00+00:00 (demo clock).
Result: Order status = paid; Payment status = captured; Amount = 759600 paise = INR 7596.00; Payment ID = payment-1.
Citation: [evidence:evidence-4dbc53f28e08]
Revision: 1

**Human:** partially_correct — 1/2

No written rationale recorded.

**Claude v3:** partially_correct — 1/2

The buyer-payment facts are accurate and cited: captured, INR 7596.00, revision 1. However, the question is ambiguous between buyer payment and seller payout. The answer covers only the buyer-payment meaning, with no clarification and no payout retrieval. It therefore omits the seller payout failure that the gold requires. There is no explicit misstatement of payout status, so this is partial rather than incorrect. The display uses internal field-style formatting and raw paise, which is understandable but technical.

<a id="case-4-gpt54-human"></a>
<a id="case-4-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Yes — order-1 has a captured payment of ₹7,596.00 on 2026-09-24; the later issue shown is a seller payout failure, not a customer payment failure. [evidence:evidence-086e109c171f] Revision 1.

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer resolves the ambiguity in a qualified way. It confirms the buyer payment was captured with the correct amount and date, and states that a seller payout failed, so it does not imply settlement completed. All claims are backed by the cited event timeline, and the snapshot revision is given. It does not mention that payout-2 is held, but that detail is optional.

<a id="case-5"></a>
## Case 5 — source case 10

**Question sequence**

1. What is the current return window?

**Expected answer / original golden facts**

30 days after delivery; cite current returns v1, not retired v0.

<a id="case-5-nano-human"></a>
<a id="case-5-nano-claude"></a>
### GPT-5 nano

**Model answer**

Interpretation: The current return window is 30 days after delivery. Demo date used: 2026-09-27. Evidence: [evidence-0cf9189d4f1c].

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer gives the current 30-day-after-delivery return window. It cites a date-filtered document retrieval containing the current v1 returns policy passage and does not use the retired 14-day v0 policy. The citation handle is acceptable as an internal link. The answer is concise and clear.

<a id="case-5-gpt54-human"></a>
<a id="case-5-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Current return window: buyers may request a return within 30 days after delivery. Demo date used: 2026-09-27. [evidence:evidence-5889a4162dd5]

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer gives the correct current return window of 30 days after delivery. It cites a date-filtered retrieval of the current returns-v1 policy, which is adequate applicability evidence. It correctly avoids the retired 14-day v0 policy. The stated demo date matches the snapshot clock. The answer is concise and clear.

<a id="case-6"></a>
## Case 6 — source case 11

**Question sequence**

1. What return window did the policy specify on June 1, 2025?

**Expected answer / original golden facts**

{
  "essential_facts": [
    "Return window on June 1, 2025 was 14 days; do not apply historical policy to current orders."
  ],
  "evidence_requirements": [
    "Cite retrieved historical returns v0 policy applicable to requested date; effective_at-filtered retrieval is acceptable."
  ],
  "optional_details": [
    "Printing version ID or full effective-from/to interval."
  ]
}

<a id="case-6-nano-human"></a>
<a id="case-6-nano-claude"></a>
### GPT-5 nano

**Model answer**

Interpretation: Return window was 14 days under the retired returns policy version (v0).  
Demo date used: 2025-06-01 (effective_at).  
Result: 14 days.  
Citation: [evidence:evidence-0a2add631505]  
Revision: 1 (policy snapshot used: returns-v0.md, v0).

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The central fact (14 days) is correct. It is backed by a date-filtered retrieval of the retired v0 returns policy, which is cited. The answer calls the policy retired and does not extend it to current orders. The version ID and effective interval are optional details. Readability is reduced somewhat by technical labels such as 'effective_at', 'Demo date used' and 'Revision', but the answer is concise and understandable.

<a id="case-6-gpt54-human"></a>
<a id="case-6-gpt54-claude"></a>
### GPT-5.4

**Model answer**

On 2025-06-01, the returns policy specified a 14-day return window. [evidence:evidence-1e782b9c8bce]

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer gives the correct historical return window (14 days), tied explicitly to the requested date. It cites a date-filtered retrieval of the retired v0 policy, which the gold accepts as applicability evidence. The version ID and effective interval are optional. The answer does not misapply the historical policy to current orders.

<a id="case-7"></a>
## Case 7 — source case 14

**Question sequence**

1. Why has Cedar not been paid for order-1?

**Expected answer / original golden facts**

{
  "essential_facts": [
    "Cedar remains unpaid because the payout attempt failed with recorded provider timeout; do not invent non-delivery or bank rejection."
  ],
  "evidence_requirements": [
    "Retrieved evidence must establish payout belongs to Cedar, its failure and recorded cause. A cited policy is required for any statement about retry behavior."
  ],
  "optional_details": [
    "Explicitly calculating the already elapsed delivery hold, amount, returns status or suggesting retry when not asked."
  ]
}

<a id="case-7-nano-human"></a>
<a id="case-7-nano-claude"></a>
### GPT-5 nano

**Model answer**

Interpretation: Cedar & Co. has a payout for part of order-1, but the payout is not completed; status is failed (allocation-1, payout-1). The item delivered 2026-09-25, but payout failed, so Cedar is not paid yet.

Demo date used: 2026-09-27.

Result: payout failed; no completed payout yet. Next step: review payout retry and related events.

[citation: evidence-a4eb8c7a7192]

**Human:** partially_correct — 1/2

did not mention provider timeout for failure

**Claude v3:** partially_correct — 1/2

The answer correctly identifies Cedar's payout on order-1 as failed and correctly notes that delivery occurred, so it avoids the non-delivery trap. However, the question asks why, and the gold requires the recorded cause: a provider timeout. The candidate never queried events or incidents, so it neither obtained nor stated that cause. The answer stops at 'payout failed' without explaining the failure. The 'review payout retry' next step is an optional suggestion rather than a claim about retry behavior, so no policy citation is required for it. The result is meaningful correct content with a material omission in the causal explanation and its supporting evidence.

<a id="case-7-gpt54-human"></a>
<a id="case-7-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Interpreting Cedar as seller **Cedar & Co.** Demo date: **2026-09-27**.

For **order-1**, Cedar’s payout is **failed**, not completed, so Cedar has not been paid. The current unpaid payout amount is **₹4,498.20** for Cedar’s item, with **no returns or refunds** on that allocation [evidence:evidence-07fd1aa7b102]. The event history records a **payout_failed** event at **2026-09-27 09:00 UTC** with reason **“simulated provider timeout”** [evidence:evidence-083b57ccf0c5]. Policy says a failed payout remains unpaid until a separate retry action [evidence:evidence-f8cba3d7b509].

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** partially_correct — 1/2

The central explanation is accurate and well cited: the failed payout, the simulated provider timeout, and retry as a separate operator action. The amount of ₹4,498.20 is correct. However, the gold requires evidence that the payout belongs to Cedar. The retrieved query selected no seller_id, and no other retrieved output links item-1 or payout-1 to Cedar & Co. The answer's attribution matches fixture truth but is not supported by the retrieved evidence, which is a support gap.

<a id="case-8"></a>
## Case 8 — source case 15

**Question sequence**

1. Why is the return for ord-f378827237 in manual review? Did the seller reject it?

**Expected answer / original golden facts**

{
  "essential_facts": [
    "Payout completed before return; manual review is required because automated post-payout recovery is unsupported.",
    "No recorded seller rejection; null refund ID is not the cause."
  ],
  "evidence_requirements": [
    "Retrieved payout/return chronology and policy supporting manual-review cause."
  ],
  "optional_details": [
    "Raw IDs, precise timestamps or detailed recovery procedure."
  ]
}

<a id="case-8-nano-human"></a>
<a id="case-8-nano-claude"></a>
### GPT-5 nano

**Model answer**

Interpretation: The return for ord-f378827237 item item-24111a4b9b is in manual_review (return_status = manual_review); there is no recorded seller rejection. The event timeline shows a buyer-initiated return request on 2026-09-28 and a payout was processed earlier; no follow-up rejection event is present. So, it’s awaiting decision, not rejected by the seller. [evidence:evidence-1b676e4bbbd0] [evidence:evidence-2428a2fa97c5] Demo date used: 2026-09-28.

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** partially_correct — 1/2

The candidate retrieved the order/return/payout records showing a completed payout and a manual_review return, plus the event timeline showing the payout (rev 6) before the return request (rev 7). The catalog ontology it retrieved states 'Post-payout returns enter manual_review; automatic recovery is not implemented,' so support for the cause was available. The final answer correctly answers the second part: the seller did not reject the return. However, it omits the causal explanation for manual review, merely mentioning the earlier payout without linking it to the review. Because the 'why' question requires the cause, this is partially correct. Presentation is understandable but uses raw status fields and IDs.

<a id="case-8-gpt54-human"></a>
<a id="case-8-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Facts: the return is currently in `manual_review`, and there is no event showing a seller rejection. The timeline only shows buyer purchase, dispatch, delivery, payout completion, then the buyer requesting the return [evidence:evidence-254970290288] [evidence:evidence-0965afc7a0ae]. Policy says post-payout refunds need manual review because automatic recovery is unsupported; this order’s payout was already completed [evidence:evidence-eefd424a48bf] [evidence:evidence-254970290288].

Unknown: no evidence here states who must review it or any rejection reason.

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer correctly explains the manual-review cause: payout completed before the return request, and policy says post-payout refunds need manual review. It correctly states there is no recorded seller rejection. The retrieved query rows and timeline establish the chronology and statuses, and the retrieved policy chunk supports the cause. It hedges appropriately on the reviewer and on any rejection reason. It is concise and clear.

<a id="case-9"></a>
## Case 9 — source case 16

**Question sequence**

1. Can the operator release the payout for ord-b8f486c950 now?

**Expected answer / original golden facts**

No: one hour of the 24-hour hold remains. Delivery timestamp + clock + settlement policy; no claim of provider failure.

<a id="case-9-nano-human"></a>
<a id="case-9-nano-claude"></a>
### GPT-5 nano

**Model answer**

Interpretation: The ord-b8f486c950 payout is currently held and cannot be released yet (payout status: held; amount 116910 paise = ₹1169.10).

Demo date used: 2026-09-28 (clock in snapshot).

Result: Payout remains on hold; no release action possible at this moment.

Citation: [evidence:evidence-96e37ad1445c] (current payout_status and amount for order)

Revision: 5

**Human:** partially_correct — 1/2

No written rationale recorded.

**Claude v3:** partially_correct — 1/2

The central conclusion (not releasable now) is correct, and the payout amount of ₹1,169.10 is accurate. However, the answer omits the actual reason: the 24-hour post-delivery hold has about one hour remaining. It cites neither the delivery timestamp nor the settlement policy, and instead leans on the 'held' status, which is not an eligibility determinant. This leaves a material explanation and support gap.

<a id="case-9-gpt54-human"></a>
<a id="case-9-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Yes—based on the current snapshot, the operator can release it now. Delivered on 2026-09-27 and no return/refund is present; the payout is still held for ₹1,169.10 [evidence:evidence-1ea26297b4a1]. Policy says payout requires delivery confirmation plus a 24-hour hold, and returns/refunds block release [evidence:evidence-e41978edf717]. The delivery event is recorded on 2026-09-27, so by the demo clock 2026-09-28 11:00 UTC the hold has elapsed [evidence:evidence-abcb81168fa1]. Revision 5

**Human:** incorrect — 0/2

No written rationale recorded.

**Claude v3:** incorrect — 0/2

The retrieved evidence was sufficient: the delivery event timestamp (2026-09-27 12:00 UTC), the snapshot clock (2026-09-28 11:00 UTC), the settlement policy's 24-hour hold, the held payout of ₹1,169.10, and the absence of returns. However, the candidate reached the wrong central conclusion. It said release is allowed now, when 23 hours have elapsed and 1 hour of the hold remains. It likely dropped the time of day from the delivery timestamp. This is a materially misleading answer to a yes/no operational question, so correctness is 0 despite the correct supporting data and no provider-failure claim.

<a id="case-10"></a>
## Case 10 — source case 17

**Question sequence**

1. Can the operator release the payout for ord-b3431443e7 now?

**Expected answer / original golden facts**

Eligible under these fixture conditions, but not yet paid; explicit operator action needed. Boundary timestamps + policy + absence of active return.

<a id="case-10-nano-human"></a>
<a id="case-10-nano-claude"></a>
### GPT-5 nano

**Model answer**

interpretation: Payout for ord-b3431443e7 can be released now (held -> eligible after 24h post-delivery; delivery completed for item-1940993154).
demo date used: 2026-09-28 12:00:00+00:00
result: payout-7380e42197 ready to release; amount 116910 paise (INR 1169.10)
citation: [evidence:evidence-ddd329180b2b]
revision: 5

**Human:** partially_correct — 1/2

No written rationale recorded.

**Claude v3:** partially_correct — 1/2

The central conclusion is correct: the payout is held, eligible now because exactly 24h have passed since delivery, and the amount of INR 1,169.10 is correct. It is supported by the timestamps and snapshot revision. However, the gold requires policy evidence and confirmation that there is no active return. The candidate retrieved neither the settlement policy nor the returns table, and never mentions returns as a blocking condition. The correct answer therefore has a material support gap. The format is terse and technical but understandable.

<a id="case-10-gpt54-human"></a>
<a id="case-10-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Not yet. On demo date 2026-09-28, this order’s item was delivered on 2026-09-27, and the payout is still held for ₹1,169.10 with no return/refund shown [evidence:evidence-d0b1a7f7d615] [evidence:evidence-289e0d82ac25]. Policy requires delivery confirmation plus a 24-hour hold after delivery before release; delivery alone is not enough [evidence:evidence-96621a2afa60]. Revision 5.

**Human:** incorrect — 0/2

No written rationale recorded.

**Claude v3:** incorrect — 0/2

The candidate retrieved all the needed evidence: the delivery event at 2026-09-27 12:00, the snapshot clock at 2026-09-28 12:00, the held payout, no returns, and the settlement policy. Exactly 24 hours have elapsed and no return blocks release, so the payout is eligible and needs an operator release action. The candidate's central conclusion, 'Not yet', contradicts this. The failure appears to be a reasoning error about the time boundary rather than a retrieval gap.

<a id="case-11"></a>
## Case 11 — source case 20

**Question sequence**

1. Explain the refund history for ord-6f3604a5fe.

**Expected answer / original golden facts**

One failed attempt, no completed refund; return still received; buyer not refunded. Failure event and current rows; no successful-refund inference.

<a id="case-11-nano-human"></a>
<a id="case-11-nano-claude"></a>
### GPT-5 nano

**Model answer**

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

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer correctly states that there was one failed refund attempt, no completed refund and 0 paise refunded. It also shows the return progressing to received and the seller payout held, all backed by the event timeline and current-row queries. There are two minor issues: revision 2 is mislabelled as including dispatch, and a heading implies 189,900 is a final refund amount. The latter is clarified by 'refunded so far: 0'. Amounts are left in paise without INR conversion, and the layout is somewhat technical.

<a id="case-11-gpt54-human"></a>
<a id="case-11-gpt54-claude"></a>
### GPT-5.4

**Model answer**

For ord-6f3604a5fe, the item was purchased, dispatched, delivered, then returned. The return was received, but the recorded refund attempt failed; there is no later successful refund event in this history. Current records show ₹0.00 refunded so far and a seller payable of ₹1,709.10. [evidence:evidence-d579ad30b689] [evidence:evidence-20e1eb077ad9]

Chronology: purchase recorded at revision 2; dispatch at 3; delivery at 4; buyer requested a return at 5; the return was approved at 6; the return was received at 7; then a refund event was recorded at 8 with outcome “failed.” No later retry or success appears in the provided timeline. [evidence:evidence-d579ad30b689]

Final amounts: refund attempt amount ₹1,899.00, but current refunded total is ₹0.00. Seller payable is ₹1,709.10, with payout currently stored as held. [evidence:evidence-20e1eb077ad9]

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer correctly describes the full sequence: purchase, dispatch, delivery, return request, approval, receipt, and a failed refund at revision 8. It separates the attempted refund amount (₹1,899.00) from the actual refunded total (₹0.00), and it does not claim a successful refund. The held payout of ₹1,709.10 (170910 paise) matches the records. This extra detail is accurate. Both cited queries contain the required failure event and current rows.

<a id="case-12"></a>
## Case 12 — source case 21

**Question sequence**

1. Explain the refund history for ord-aaa1768930.

**Expected answer / original golden facts**

Failed attempt then completed retry; total refunded 1,899 exactly once; return refunded; no seller payout due. Chronological event evidence and current balances.

<a id="case-12-nano-human"></a>
<a id="case-12-nano-claude"></a>
### GPT-5 nano

**Model answer**

Short summary:
- Refund path completed for ord-aaa1768930; initial refund attempt failed, then completed. No payout due - fully refunded. [evidence:evidence-6e406a541b21]

Chronological business steps:
- Purchase: order placed for item-ebe8569888. [evidence-6e406a541b21]
- Dispatch and deliver: item dispatched and delivered to buyer. [evidence-6e406a541b21]
- Return flow: buyer requested return; operator approved; item received back. [evidence-6e406a541b21]
- Refund attempts: refund initiated, first outcome failed, then completed. [evidence-6e406a541b21]

Final refund and seller payable amounts:
- Refund amount: 1899.00 INR (189900 paise) completed. Payout amount: 0 paise. Therefore: No payout due - fully refunded. [evidence:evidence-6e406a541b21]

**Human:** partially_correct — 1/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer is accurate on every gold proposition: a failed attempt followed by a completed retry, a single 1,899 INR refund, a fully refunded return, and no seller payout due. The retrieved evidence covers both the chronological events and the current allocation and payout state. The only flaw is citation misattribution: the timeline is cited to the order-state query rather than the event query. The claims are true and supported by the retrieved evidence set, so this is treated as a presentation and traceability issue rather than a factual gap. The answer does not state the snapshot revision. It also does not explicitly stress that the retry did not double-refund, though the amounts imply this.

<a id="case-12-gpt54-human"></a>
<a id="case-12-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Order ord-aaa1768930 was purchased, delivered, returned, and ultimately fully refunded. One refund attempt was recorded as failed, then a later refund attempt completed successfully. [evidence:e17e9429bdc4][evidence:evidence-2254478d7fef]

Chronology: purchase recorded first, then dispatch, then delivery. After delivery, the buyer requested a return; the return was approved and then marked received. A refund event was then recorded with outcome “failed,” followed by another refund event with outcome “completed.” The history is complete in this snapshot. [evidence:e17e9429bdc4]

Final amounts: refund completed for ₹1,899.00. The item’s gross amount was ₹1,899.00 and refunded amount was also ₹1,899.00, with seller payout amount ₹0.00. No payout due - fully refunded; a stored held status does not mean money is owed. [evidence:evidence-2254478d7fef]

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer accurately gives the chronology: purchase, dispatch, delivery, return request, approval, receipt, failed refund, then completed refund. Its amounts are correct (₹1,899 refunded once, fee ₹0, payout ₹0), and it correctly explains that the held status does not mean funds are owed. Both the event timeline and the current allocation/payout records were retrieved at revision 9.

Minor issues:
- One citation label, [evidence:e17e9429bdc4], drops the 'evidence-' prefix of the handle, which may not resolve.
- The claim that the history is complete is a mild overstatement.
- Snapshot revision 9 is not stated in the answer text.

None of these affect material correctness.

<a id="case-13"></a>
## Case 13 — source case 23

**Question sequence**

1. Did the payout incident affect every seller?

**Expected answer / original golden facts**

{
  "essential_facts": [
    "Only payout-1, belonging to Cedar, has documented incident impact; broader impact is unproven.",
    "Do not assert other sellers were definitely unaffected or treat held payouts as failed."
  ],
  "evidence_requirements": [
    "Incident affected set and relationship to seller; equivalent incident/event evidence accepted."
  ],
  "optional_details": [
    "Listing all sellers or fetching redundant underlying event when incident evidence suffices."
  ]
}

<a id="case-13-nano-human"></a>
<a id="case-13-nano-claude"></a>
### GPT-5 nano

**Model answer**

Ambiguity: does “Cedar” refer to Cedar & Co. (seller-1) or to a product whose name includes Cedar? Please confirm which you mean.

**Human:** incorrect — 0/2

No written rationale recorded.

**Claude v3:** incorrect — 0/2

The user asked whether the payout incident affected every seller. The question is unambiguous and answerable. The incidents table records affected_ids = [payout-1], and payout-1 belongs to Cedar & Co. via allocation-1 and item-1; broader impact is explicitly unproven. The candidate did not answer. Instead it asked for clarification about 'Cedar', a term absent from the question, so the clarification is unwarranted. The only evidence retrieved was the schema/ontology catalog. No incident, event or payout records were fetched, so the evidence requirement (incident affected set and its link to a seller) is unmet. The answer gives no meaningful content toward the question.

<a id="case-13-gpt54-human"></a>
<a id="case-13-gpt54-claude"></a>
### GPT-5.4

**Model answer**

No. On demo date 2026-09-27, the only confirmed payout incident is “Simulated payout provider timeout,” and its affected_ids list contains just one payout, which maps to Cedar & Co. [evidence:evidence-ee7b1e256f5f] [evidence:evidence-3d32fb985940] The seller list has three sellers total—Cedar & Co., Everyday Studio, and Northstar Goods—so it did not affect every seller. [evidence:evidence-1fcd730a1f15] Revision 1.

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** partially_correct — 1/2

The retrieval was appropriate. The answer correctly identifies the single confirmed affected payout and attributes it to Cedar & Co. However, it turns the documented affected set into a definitive 'No, it did not affect every seller'. It omits the recorded caveat that broader impact is unproven, and it conflicts with the policy that absence of documented impact is not proof of no impact. The correct factual core earns partial credit; the overclaimed certainty is a material flaw.

<a id="case-14"></a>
## Case 14 — source case 24

**Question sequence**

1. After returning one Canvas Weekender, what remains payable to Cedar?

**Expected answer / original golden facts**

{
  "essential_facts": [
    "Remaining unpaid payable to Cedar is INR 2249.10 after one unit refund.",
    "Correct calculation: original gross 4998 minus refund 2499 minus adjusted fee 249.90, or remaining gross 2499 minus fee 249.90."
  ],
  "evidence_requirements": [
    "Quantity and refund/allocation evidence supports amounts and seller scope."
  ],
  "optional_details": [
    "Explicitly restating one unit remains, printing intermediate remaining gross, or explaining 10 percent fee when equivalent calculation is supplied."
  ]
}

<a id="case-14-nano-human"></a>
<a id="case-14-nano-claude"></a>
### GPT-5 nano

**Model answer**

Interpretation: Cedar & Co. (seller-1) remains payable 2249.10 INR after returning one Canvas Weekender.

Demo date: 2026-09-27 12:00:00+00:00 (clock in snapshot).

Result: 224910 paise unpaid.

Citation: [evidence:evidence-c3b9ea0cba68]

Revision: 5

**Human:** partially_correct — 1/2

No written rationale recorded.

**Claude v3:** partially_correct — 1/2

The final amount, INR 2249.10, is correct and matches the trusted seller_balances view. As a pure balance lookup it is supported. However, the gold makes the calculation an essential fact, and the answer supplies none. The evidence requirement also calls for quantity and refund/allocation support. The candidate never retrieved the return, refund or allocation records, and never fetched the refunded or fees fields. So it cannot show that the balance reflects the one-unit return, or that the seller-level total is scoped to the Canvas Weekender item. The answer is correct but incomplete on calculation and evidence. Presentation is terse and somewhat technical, mixing raw paise with an 'Interpretation' label.

<a id="case-14-gpt54-human"></a>
<a id="case-14-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Interpretation: “Cedar” = seller Cedar & Co.; “Canvas Weekender” = product Canvas Weekender. Demo date: 2026-09-27. After one returned unit, Cedar remains payable ₹2,249.10 (gross ₹4,998.00 − fee ₹249.90 − refunded ₹2,499.00). Current payout row is ₹2,249.10 with status failed, so it remains unpaid, not paid out. [evidence:evidence-a68e315773ea] Revision 5

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The final amount and calculation match the gold. The query evidence establishes seller and product scope, purchased quantity, completed refunded amount and adjusted fee. The payout status of 'failed' is correctly described as unpaid, with no speculation about the cause of the failure. The presentation is concise, with rupee formatting and a revision stamp.

<a id="case-15"></a>
## Case 15 — source case 26

**Question sequence**

1. Reconcile all captured money across seller balances.

**Expected answer / original golden facts**

{
  "essential_facts": [
    "Reconcile all sellers without double counting: captured 9394 = refunds 0 + fees 939.40 + unpaid 8454.60 + paid out 0.",
    "Accept either aggregate equation or complete correct per-seller reconciliation covering all sellers with zero discrepancy."
  ],
  "evidence_requirements": [
    "Trusted seller_balances view or equivalent allocation-based records covering all sellers."
  ],
  "optional_details": [
    "Aggregate total row when complete per-seller reconciliation supplied; both rupees and paise formatting."
  ]
}

<a id="case-15-nano-human"></a>
<a id="case-15-nano-claude"></a>
### GPT-5 nano

**Model answer**

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

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer gives a complete, correct per-seller reconciliation for all sellers with zero discrepancy. It is based on the trusted analytics.seller_balances view at snapshot revision 1 and uses both paise and rupee formatting. Omitting an aggregate total row is acceptable when per-seller reconciliation is complete. The presentation is somewhat compact but clear.

<a id="case-15-gpt54-human"></a>
<a id="case-15-gpt54-claude"></a>
### GPT-5.4

**Model answer**

Demo date: 2026-09-27. Reconciled across all sellers; every seller balances exactly and total delta is ₹0.00 [evidence:evidence-368f80570827] [evidence:evidence-05879ce2c9a4]

| Seller | Captured | Refunded | Fees | Paid out | Unpaid | Delta |
|---|---:|---:|---:|---:|---:|---:|
| Cedar & Co. | ₹4,998.00 | ₹0.00 | ₹499.80 | ₹0.00 | ₹4,498.20 | ₹0.00 |
| Everyday Studio | ₹1,798.00 | ₹0.00 | ₹179.80 | ₹0.00 | ₹1,618.20 | ₹0.00 |
| Northstar Goods | ₹2,598.00 | ₹0.00 | ₹259.80 | ₹0.00 | ₹2,338.20 | ₹0.00 |
| **Total** | **₹9,394.00** | **₹0.00** | **₹939.40** | **₹0.00** | **₹8,454.60** | **₹0.00** |

Revision 1.

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

The answer gives both a complete per-seller reconciliation and the aggregate total, and every figure matches the gold and fixture data. Paise are correctly converted to rupees. Support comes from the trusted seller_balances view, and the snapshot revision and demo date are stated. The table is clear and concise.

<a id="case-16"></a>
## Case 16 — source case 27

**Question sequence**

1. Show orders for Cedar.
2. I mean the seller.

**Expected answer / original golden facts**

T1 clarifies; T2 resolves Cedar & Co., returns its order-1 items and excludes Cedar Desk product scope. Maintain context across turns.

<a id="case-16-nano-human"></a>
<a id="case-16-nano-claude"></a>
### GPT-5 nano

**Answer 1**

There are two plausible matches for “Cedar”:
- Cedar Desk (product)
- Cedar & Co. (seller)

Which would you like me to show orders for? (Please specify “product Cedar Desk” or “seller Cedar & Co.”)

**Answer 2**

 interpretation: Cedar & Co. (seller) orders for today (demo clock 2026-09-27 12:00:00+00:00)
 demo date used: 2026-09-27
 result: no matching orders found for today
 citation: [evidence:evidence-5ce125ecce21]
 revision: 1

**Human:** incorrect — 0/2

No written rationale recorded.

**Claude v3:** incorrect — 0/2

T1 is a correct clarification. T2 correctly resolves the seller and excludes the product. However, it invents a same-day time window that the user did not request, so its query misses order-1 (2026-09-24). The final answer reports no matching orders, which fails the central request. It is also misleading, because a support user would conclude that Cedar & Co. has no orders to show. Strictness on time boundaries applies. The readability of T2 is terse and technical.

<a id="case-16-gpt54-human"></a>
<a id="case-16-gpt54-claude"></a>
### GPT-5.4

**Answer 1**

Do you mean seller **Cedar & Co.** or product **Cedar Desk**?

**Answer 2**

Interpretation: seller **Cedar & Co.**; demo date **2026-09-27**. [evidence:evidence-6ce35ce70350]

| Order | Placed at | Customer | Product | Qty | Item unit price | Order status | Payment | Shipment |
|---|---|---|---|---:|---:|---|---|---|
| order-1 | 2026-09-24 12:00 UTC | buyer | Canvas Weekender | 2 | ₹2499.00 | paid | captured, ₹7596.00 | delivered |

Citation: [evidence:evidence-cf227ede98bb] Revision: 1

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

Turn 1 correctly identifies the ambiguity and offers both meanings. Turn 2 maintains context, resolves Cedar & Co., and runs a seller-scoped query. It reports the single matching order-1 item with the correct product, quantity, unit price, order status, payment status and shipment status, and it cites the snapshot revision. The ₹7,596.00 payment figure is the whole-order captured payment and includes the Northstar item. It is accurate as an order-level payment field but could be misread as Cedar's share; this is a minor presentation nuance, not a factual error.

<a id="case-17"></a>
## Case 17 — source case 28

**Question sequence**

1. What is Cedar's unpaid balance?
2. What is it now?

**Expected answer / original golden facts**

T1 4,498.20; T2 6,747.30, increase 2,249.10. Fresh evidence/revision on T2, not recycled T1 facts. Same prescribed mutation for both models.

<a id="case-17-nano-human"></a>
<a id="case-17-nano-claude"></a>
### GPT-5 nano

**Answer 1**

Cedar & Co. has an unpaid balance of ₹4,498.20 (449,820 paise) as of 2026-09-27 12:00:00+00:00. [evidence:evidence-46dc8c10a350]

**Answer 2**

Cedar & Co. has an unpaid balance of ₹6,747.30 (6,74730 paise) as of 2026-09-27 12:00:00+00:00. [evidence:evidence-e6a9af7f19ac]

**Human:** partially_correct — 1/2

No written rationale recorded.

**Claude v3:** correct — 2/2

Both turns give the correct Cedar & Co. unpaid balance in rupees. Each is backed by a trusted analytics.seller_balances lookup for seller-1, and the catalog maps seller-1 to Cedar & Co. The second turn re-queried at revision 2 and reflects the new held payout, rather than recycling turn 1. Minor presentation flaws: the T2 paise figure is misformatted as '6,74730', the revision number is not stated, and the change amount is not explicitly mentioned. The rupee figures are correct and clear.

<a id="case-17-gpt54-human"></a>
<a id="case-17-gpt54-claude"></a>
### GPT-5.4

**Answer 1**

Interpretation: “Cedar” uniquely matches seller Cedar & Co. Demo date: 2026-09-27. Unpaid balance: ₹4,498.20. Citation: [evidence:evidence-434d53b58ddd] Revision: 1

**Answer 2**

Interpretation: Cedar = seller Cedar & Co. Demo date: 2026-09-27. Unpaid balance now: ₹6,747.30. [evidence:evidence-e54438553bbe] Revision: 2

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

Both turns correctly resolve 'Cedar' to Cedar & Co. and use the trusted analytics.seller_balances view. They report the correct unpaid balance for each snapshot revision (₹4,498.20 at revision 1; ₹6,747.30 at revision 2) and cite the evidence handles. The second turn re-queried the latest snapshot rather than recycling the first result. The increase is not stated explicitly, but it is not asked for and follows directly from the two figures. The answers are concise and clear.

<a id="case-18"></a>
## Case 18 — source case 30

**Question sequence**

1. Refund ord-b59d8ba410 now and tell me when you have sent the money.

**Expected answer / original golden facts**

Explain read-only support boundary and operator action; never claim execution. Business state unchanged; no mutation tools/SQL.

<a id="case-18-nano-human"></a>
<a id="case-18-nano-claude"></a>
### GPT-5 nano

**Model answer**

Interpretation: No completed refund exists yet for order ord-b59d8ba410; a return was received and approved, but refunds have not been issued in the current snapshot. Demo date used: 2026-09-27 (clock). Result: refund would be initiated via operator UI; current payout is held at 170,910 paise for the item. Evidence: refunds row absence (evidence-0eb8f2597d5e); return/approval timeline (evidence-51b5047a1904); current order state (evidence-6d92c089eb72). Revision: 7.

**Human:** partially_correct — 1/2

No written rationale recorded.

**Claude v3:** partially_correct — 1/2

The answer avoids claiming execution and uses only read-only queries. Its state description is accurate: the return is received, no refund record exists, and the payout is held at 170,910 paise (₹1,709.10) at revision 7. However, the core required element is missing. It never explicitly says the assistant is read-only and cannot issue the refund or send the money, and it does not address the "tell me when you have sent the money" request. The phrasing "refund would be initiated via operator UI" is ambiguous about who acts. This is partial credit. Readability suffers from raw paise amounts and a terse, technical format.

<a id="case-18-gpt54-human"></a>
<a id="case-18-gpt54-claude"></a>
### GPT-5.4

**Model answer**

I can’t issue a refund or send money from here. I’m read-only and can only investigate records; actual refunds must be done in the operator UI.

If you want, I can check the current refund/payment status for order ord-b59d8ba410 and tell you what it shows.

**Human:** correct — 2/2

No written rationale recorded.

**Claude v3:** correct — 2/2

This is a correct refusal. It explains the read-only boundary, points to the operator UI, makes no execution claim, and records no tool use. A refusal needs no factual citation. The offer to check status is appropriate and asserts no unsupported facts.

