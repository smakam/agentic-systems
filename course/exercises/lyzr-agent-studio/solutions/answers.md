# Lyzr Agent Platform — reference answers

These checkpoints help interpret your own run; model outputs can vary.

## Core: Basics in Playground

The hosted Basics agent uses native Knowledge Base retrieval from the supplied fictional order file. Google Basics uses a Python lookup function over the same source; here Lyzr retrieves indexed chunks. The agent must ground order claims in the retrieved record.

| Order | Fictional source facts |
|---|---|
| order-demo-1 | 2 Ceramic Mug Sets; payment received; shipment not dispatched; payout held |
| order-demo-2 | 1 Canvas Weekender; payment received; shipment delivered; payout released |
| order-demo-3 | 1 Desk Lamp; cancelled; payment refunded; shipment cancelled; payout not applicable |
| order-demo-999 | No record in the supplied complete fictional catalogue |

A same-chat payout follow-up can use the retained order identity. A new chat should not be credited with continuity merely because it guessed an order. A held payout does not establish eligibility or a hold reason: this fixture supplies no eligibility policy or live clock. Inspect the actual source chunk and distinguish missing source evidence from a confirmed missing record.

## Optional: full cloud Marketplace integration

The path is **marketplace chat application and backend in Google Cloud → Lyzr-hosted agent → authenticated MCP service in Google Cloud → Cloud SQL business records and policy evidence**. No Google ADK deployment is used for this path. The shared cloud guide prepares the application infrastructure; the Lyzr guide connects its hosted agent. Cloud SQL must be running for business reads.

The marketplace application selects the configured hosted agent; it does not change that agent’s MCP endpoint. The backend uses a Lyzr inference credential, while the agent’s MCP connection uses a separate business-service credential. A listed tool or discovered schema proves neither successful runtime authentication nor a correct answer. Inspect a matching authenticated tool result and native trace.

For order status and the payout follow-up, use your own current records. Separate buyer payment, seller payout status and policy eligibility. A policy explanation requires relevant business and policy evidence. The workspace Internal/Mem0 options do not configure native Lyzr memory.

## Monitoring, cost and ownership

Activity and traces expose execution, source retrieval, tool arguments/results and failures. Analytics shows operational usage, latency and credits; evaluation assesses answer quality. Application Langfuse can show a different boundary from Lyzr’s internal trace.

Use three cost categories: model inference paid to the model provider under current public Lyzr pricing; customer-operated infrastructure/runtime paid to the infrastructure provider; and platform capabilities paid to Lyzr under the plan. Hosted infrastructure may be bundled; external tools and memory can add charges. Check [current pricing](https://www.lyzr.ai/pricing/) and contract terms instead of combining old credit schedules with new plans.

Google Cloud operates the deployed application infrastructure and database services; Lyzr runs the hosted agent. You retain source quality, business authorization, identity and integration responsibilities. Record what you actually observed and any limits; the fresh-project learner setup has not been rehearsed end to end. Cleanup applies only to your own resources.

Use the [Basics setup guide](../../../setup/lyzr-agent-platform/setup-guide.md), [Lyzr cloud integration guide](../../../LYZR-PLATFORM-PLAN.md) for the detailed steps. The presenter walkthrough remains in the chapter speaker notes.
