# Practice: Basics, with optional full cloud Marketplace integration

## Core practice: Basics in Playground

Complete the [Basics setup guide](../../setup/lyzr-agent-platform/setup-guide.md), or observe the instructor and label your observations accordingly. The supplied fictional orders become an indexed Knowledge Base attached to your **Support Agent Basics** agent. Role, goal, instructions and model are part of creating that agent; native memory and guardrails are optional features configured separately. The setup guide provides the UI steps; the practice questions follow below.

1. Start a new Playground chat and ask **“What is the status of order-demo-2?”** Compare the returned payment, shipment and payout facts with the retrieved source.
2. Ask **“What is the payout status for this order?”** in the same chat. Inspect retained order identity and the evidence used.
3. Try another supplied fictional order or **order-demo-999** in a new chat. Check source grounding and the missing-record boundary.
4. Inspect **Activity / Traces**, the retrieved `orders-knowledge.txt` chunk, model input/output, latency and usage where visible. An answer or a tool list alone does not prove which evidence was used.

Keep a few notes on the question, retrieved facts, final answer, follow-up behavior and any failed checks. This is practice with the demonstrated flow, not a new platform benchmark.

## Optional practice: full cloud Marketplace integration

### Setup and starting point

Use your own resources. First complete [Cloud application setup](../../../app/CLOUD-SETUP.md), then [Lyzr integration setup](../../LYZR-PLATFORM-PLAN.md). **Google Cloud supplies the marketplace frontend/application backend, the authenticated MCP backend, and Cloud SQL business/policy data. The agent runs on Lyzr, not Google ADK.** The shared application setup includes the SDK baseline and supporting services; the Lyzr guide adds the hosted-agent connection. Reuse an existing working stack rather than deploying it again.

Confirm Cloud SQL is running and the web/MCP services work. Create or use your own separate Marketplace integration agent, connect its cloud business MCP tools, and configure the application backend to invoke it. The inference API key and MCP credential have different destinations. Never use the instructor’s resources as your provisioning target. This path does not depend on a laptop tunnel.

### Practice

1. Open your cloud marketplace Support interface and select **Lyzr**. Start a fresh conversation.
2. Ask **“What is the status of order-1?”**, substituting a confirmed order ID from your own backend if needed.
3. Ask **“What is the payout status for this order?”** in the same conversation. Compare the answer with the actual returned business records.
4. Open the corresponding native Lyzr session/trace. Inspect the MCP connection, investigation and tool results, final response and evidence. Check logs, latency and usage where available. If configured, compare with the application-boundary Langfuse trace.

### What to document

Record the application, hosted agent, MCP and database locations; your questions and supported answers; same-chat context; relevant tool arguments/results; trace links; observed cost categories; and failed or untested checks. Keep credentials out of your notes. If you only watched the instructor, label the result **observation only** rather than claiming you deployed it. The existing integration has been exercised, but a full fresh learner-project installation remains unverified.

## Cleanup and reference

Follow the linked guides to remove only resources you created. Preserve instructor/shared agents, connections and business data. Review [reference answers](solutions/answers.md). Optional native memory reference material stays in the chapter speaker notes, outside this practice.
