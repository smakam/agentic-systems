# Your First Agent, End to End

## Prerequisites

Complete **Chapter Four — Course Setup** using the [local setup guide](../../../app/LOCAL-SETUP.md). Keep Docker and the application running.

Open the **[regular marketplace](http://localhost:5178/)**. This exercise uses its existing local data. Use the demo accounts from the setup guide, choose **OpenAI Agents SDK** in Support, and keep long-term memory, routing demos and guardrails off for this introductory exercise. All purchases, shipping and payouts are simulated. Agent questions use paid model API calls.

Use a fresh order and record its reference. Current balances may differ from examples because you have already used the application.

## 1. Get familiar with the marketplace

Walk through one complete purchase-to-payout journey before using the support agent. Use a fresh order and follow the same order/item across account changes.

1. As **buyer**, review the catalog and buy one **Canvas Weekender from Cedar & Co.** Record the order reference and checkout amount.
2. As **seller**, find that item, dispatch it and mark it delivered. Record its item reference and delivery time.
3. As **operator**, try to release that item’s payout before the 24-hour hold ends. Expect rejection and a held payout.
4. Advance the demo clock to at least 24 hours after delivery. Release that exact payout manually, provided no active return blocks it and its payable amount is positive.
5. Confirm completion and inspect the event history. The completed payout moves the seller share from unpaid to paid. Advancing time alone does not pay the seller.

The [marketplace journey guide](../../../app/USER-JOURNEYS.md) explains the role actions. Returns, failure/retry branches and a code tour are not required here.

## 2. Get familiar with the support agent

### Ask questions and inspect traces

As operator or support:

1. Start a new conversation. Ask **“What is the payout policy?”** Open its policy evidence.
2. Start another conversation. Ask **“How many sellers are there?”** Follow with **“What are the names of the sellers?”** in that same conversation.
3. Start a third conversation. Ask **“What are Cedar & Co.’s paid and unpaid balances?”** Record both values and inspect the supporting business records. Keep this conversation for the comparison below.
4. Open the corresponding traces in **[local Langfuse](http://localhost:3000/)** through the application. Identify model calls, requested tools, returned evidence and final answers. Compare the policy and business-data questions. For the follow-up, inspect how the earlier conversation enters the model input. Total token usage includes input and output. Missing usage or cost does not mean zero.

### Make a new purchase and compare the balances

Use a **second fresh order**, separate from the completed journey above. Record the balance baseline after finishing section one. Keep this second purchase unpaid while comparing balances.

1. Sign in as **buyer** in the same regular marketplace. Buy one **Canvas Weekender from Cedar & Co.** Record the new order reference and checkout amount.
2. Return to operator/support and reopen the third conversation. Ask **“What are Cedar & Co.’s paid and unpaid balances?”** again.
3. Compare the new answer and fresh SQL evidence with your baseline. The purchase increases unpaid by the seller share after the marketplace fee. Paid remains unchanged at this stage.
4. At the unchanged sample price of ₹2,499 for one item, the fee is ₹249.90 and the unpaid increase is ₹2,249.10. Use your actual price and quantity if different.

## Optional: try your cloud application

**Prerequisite:** complete the separate [cloud setup guide](../../../app/CLOUD-SETUP.md) and keep its Cloud SQL database running.

1. Open **your cloud marketplace URL** from that setup. Sign in to Support and choose **OpenAI Agents SDK**.
2. Start a new conversation and ask **“What products, quantities and sellers are in order-1?”** Check the current cloud records and evidence.
3. Open that question’s trace in **your Langfuse Cloud project**. The instructor uses [Langfuse Japan](https://jp.cloud.langfuse.com/); use the region chosen during your own setup. Sign in with your hosted account, rather than the local demo credentials.
4. Inspect model calls, HTTP MCP tool calls, returned business evidence and the final answer.

Cloud data is independent of your local application. This optional step requires no cloud purchase or reset. Stop your cloud database after the demo when nobody is using it, following the cloud guide.

## What to keep

Keep the first journey’s order reference and payout result, the policy answer, the seller-name follow-up, one explained trace, and the balances before and after the second purchase. Report discrepancies using the actual evidence.

No reset is needed to finish. Preserve your local data and record any demo clock change. Do not run fixture-reset scripts for this exercise.

Try the exercise before opening the [worked answers](solutions/answers.md).
