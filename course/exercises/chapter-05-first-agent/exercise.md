# Your First Agent, End to End — marketplace practice

Complete “Course Setup” first. Keep Docker running. Use the configured OpenAI/OpenRouter route; arbitrary model substitutions are not validated against these checks. Start with gateway guardrails off, long-term memory off and memory changes off. All marketplace payments and shipping are simulated. Budget 45–60 minutes for the core, plus 30–45 minutes for the branch practice; those are planning estimates. Model questions are paid. The worked solution is separate so you can try first.

## Starting point and workspace choice

Use the **main marketplace** for purchases and business-state changes. Use fresh orders for each independent branch; no whole-database reset is required. Record each new order/item/shipment/payout reference and the starting demo clock. The **test workspace** is for fixed seeded comparisons: inspect its seed before relying on example facts, and do not mutate that fixture during a comparison. Never run database-reset/test scripts while another person is using the test UI. Keep the evaluation database unchanged.

The [journey guide](../../../app/USER-JOURNEYS.md) supplies exact role actions and boundary behavior. On the clean seed, listing-1 is Canvas Weekender from Cedar & Co.; if your listings/prices changed, use the current checkout receipt rather than the example amounts below.

## Core: one marketplace journey

1. As **buyer**, buy one item from the seller used for the agent comparison below. Record the new order reference, price and quantity.
2. As **seller** (or operator for another seller), find that same item, dispatch it, then manually mark it delivered.
3. As **operator**, try payout release before the 24-hour hold completes. Confirm rejection; the payout remains held.
4. Advance the demo clock by 24 hours. Release the eligible payout manually. Confirm completion and inspect the event trail. Delivery and clock advance do not automatically pay a seller.
5. Explain which role made each change. Confirm a support account can investigate but cannot perform business actions.

## Core: first agent and freshness comparison

Do the **before** step before the purchase in the journey, so you can compare the same seller.

1. As operator/support, record the seller settlement’s captured, fee, refunded, unpaid and paid-out values, plus the business revision and demo clock.
2. Start a new SDK-agent conversation. Ask: **“What are Cedar & Co.’s captured amount and unpaid balance?”** Replace the seller if needed. Inspect the cited rows, not just the prose.
3. Make the fresh purchase through the buyer UI. Before dispatch/payout, ask the same question again in the same conversation. Record the new revision, answer, evidence and trace. Confirm the comparison reflects fresh business records, not a remembered old status.
4. Ask a policy question, such as **“What must happen before a seller payout can be released?”** Check retrieved policy evidence for delivery, the 24-hour hold and blocking returns.
5. In local Langfuse, find the corresponding question trace. Identify the user/model input, a requested tool, its returned evidence, any subsequent model call and the final answer. The number/order of calls can vary; a tool is not guaranteed to run merely because an example trace used it.
6. Briefly inspect monitoring across these runs: latency, token usage and run status. Cost is usable only if the model/pricing mapping supplies it; an empty cost field is not zero cost. Detailed observability is a later chapter.
7. Open the relevant code: API authentication/dispatch, agent instructions/model/runner, MCP connection, then tool contracts. Explain what each does without changing code.

The [first-agent verification reference](../../../app/docs/FIRST-AGENT-VERIFICATION.md) also provides fixed-seed order/follow-up examples. Their expected quantities apply only to that seed, not every modified marketplace.

## Optional: first agent in your cloud marketplace

Complete [CLOUD-SETUP.md](../../../app/CLOUD-SETUP.md) first. Skip this section if you are using only the local environment.

1. Open your own cloud marketplace URL and sign in to Support with the password chosen during cloud setup. Select **OpenAI Agents SDK** and start a new conversation.
2. Ask: **“What products, quantities and sellers are in order-1? Retrieve current records.”**
3. Check the completed answer and open its business-evidence links. Compare with your current cloud records; the cloud database is independent of the laptop.
4. Open the corresponding trace in your **Langfuse Cloud in your chosen region** project using the application link. Inspect model requests, tool calls, returned records and the final answer. Record the trace ID from your own run.
5. Check run/configuration metadata for **HTTP MCP**. Local Compose uses stdio; identical tool names do not prove the transport.

This is a read-only optional agent walkthrough. You do not need to repeat purchases, advance the cloud clock or reset either database. Keep observations locally for comparison with the solution. Stop the cloud database between labs only when no one is using it, following the cloud guide.

## Marketplace branch practice

Use a separate fresh order for each case; follow the [journey guide](../../../app/USER-JOURNEYS.md).

| Case | What to demonstrate |
|---|---|
| Return/refund before payout | Delivered item → buyer return request → seller approval → seller receives physical goods → operator refund; verify one applied refund |
| Return after completed payout | Request becomes manual review; automatic recovery of the seller’s paid funds is outside this simulation |
| Failed refund then retry | Failure leaves financial amounts unchanged and return received; successful retry applies the refund once |
| Failed payout then retry | Eligible failure leaves seller funds unpaid; retry completes payment once |
| Active return and access boundaries | Active return blocks payout; seller scope and support read-only permissions are respected |

## What to submit

- A short journey record: roles, references, starting state/clock, expected and observed transitions, and screenshots/event evidence.
- Before/after seller amounts and the purchase’s gross, fee and seller share; separate purchase from payout.
- Supporting database/policy evidence and trace references for the agent comparison.
- One annotated trace, high-level monitoring observations and a four-file code responsibility explanation.
- Findings for the branch scenarios, including failures/retries and one permission boundary.

## Acceptance and cleanup

The business math reconciles; early release is rejected; later release is manual; no duplicate completed refund/payout occurs; changed facts are backed by fresh evidence. Agent output wording may differ. If an answer is wrong, retain its evidence/trace and report the discrepancy rather than altering the fixture to make it pass. Marketplace mutation is performed by the human role, not the support agent.

Stop/resume normally to preserve your work. Reset the main marketplace only if you intentionally want to discard it; resets also remove its conversations/memories. Restore a test fixture only when that lesson requires it. Langfuse traces are not erased by those marketplace resets. Do not commit credentials or include them in submissions.

Try the exercise before opening the [worked solution](solutions/README.md).
