# Your First Agent, End to End — worked answers

Use the **[regular marketplace](http://localhost:5178/)** from **Chapter Four — Course Setup**. The local database retains earlier activity, so compare changes against your recorded baseline.

## Questions and evidence

- The payout policy should describe delivery plus a 24-hour hold, no blocking active return, positive payable amount and manual operator release. Inspect retrieved policy evidence.
- The seeded marketplace has three sellers: Cedar & Co., Everyday Studio and Northstar Goods. Confirm the current records. The second question stays in the seller-count conversation.
- Cedar & Co.’s paid and unpaid balances must match the current settlement records. Do not expect a fixed starting balance.

In Langfuse, follow the question through model calls, tool arguments, returned evidence and the final answer. The policy question uses document evidence; balance questions use current business records. Exact wording and tool-call counts can vary. Total tokens includes input and output. An empty cost field cannot establish that a call was free.

## Purchase and balance comparison

Buying one Canvas Weekender at the unchanged seeded price gives:

| Amount | Value |
|---|---:|
| Captured buyer payment | ₹2,499 |
| Marketplace fee | ₹249.90 |
| Seller share | ₹2,249.10 |

Immediately after purchase, Cedar & Co.’s unpaid balance increases by ₹2,249.10 while paid remains unchanged. Use actual receipt amounts if price or quantity differs. A fresh tool query must support the second answer.

## Completed marketplace journey

Purchase creates a paid order, captured payment, pending shipment and held payout. Seller dispatches and marks delivered. Early payout release is rejected and remains held.

After delivery plus 24 hours, the operator manually releases the eligible payout. A successful payout moves the seller share from unpaid to paid, without creating another buyer payment. The order remains paid in this simulation. Advancing the clock alone does not release funds.

Follow the same new order/item across account changes. Do not require returns, refunds, simulated failures or retry branches for this exercise.

## Optional cloud observations

Complete [cloud setup](../../../../app/CLOUD-SETUP.md) first. The cloud order question should return current cloud records and retained business evidence. Inspect the corresponding trace in the hosted Langfuse project chosen during setup. The instructor uses Japan; other learners may choose another region.

This path uses OpenAI Agents SDK with authenticated HTTP MCP tools. Cloud and local databases are independent, so their answers need not match. No cloud purchase is required.

## Completion

A useful result shows the policy evidence, seller follow-up context, fresh before/after balances, one explained trace and the new order’s completed payout. Retain any unsupported/stale answer as a finding. Preserve the existing marketplace data; no reset is required.
