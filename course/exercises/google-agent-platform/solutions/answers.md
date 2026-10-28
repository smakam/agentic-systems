# Google Agent Platform reference answers

Use these notes to interpret your own results; live responses can vary.

## Core practice: Basic support agent

Basics runs in Google Playground. The hosted ADK agent uses a native `lookup_order` function to read packaged fictional order JSON. It does not call MCP, a business database or a policy service.

| Record | Expected fixture facts |
|---|---|
| order-demo-1 | 2 Ceramic Mug Sets; payment received; shipment not dispatched; payout held |
| order-demo-2 | 1 Canvas Weekender; payment received; shipment delivered; payout released |
| order-demo-3 | 1 Desk Lamp; cancelled; payment refunded; shipment cancelled; payout not applicable |
| order-demo-999 | No packaged record; no invented order status |

The payout follow-up can reuse the order ID and evidence from the same session. A new session has no demonstrated continuity with the earlier one. A held payout does not establish its reason or policy eligibility: Basics has no policy tool.

Inspect the native trace for the actual lookup arguments, returned fields and final answer. The tool list shows availability; the execution trace shows what ran. Logs and monitoring describe operation and do not by themselves assess answer correctness. Memory is outside this exercise.

## Optional practice: Marketplace support agent

This path is chat application → hosted Google ADK agent → authenticated business MCP → business records and policy retrieval. The application backend handles the runtime connection and trusted user/session context; business middleware enforces access to the tools and evidence.

Selecting Google ADK in the chat application invokes the configured deployment. It does not deploy the agent or change that agent's backend connection. Complete the linked setup guides first using your own resources.

For the order-status question and payout follow-up, report the actual backend results for the chosen order. Keep buyer payment, seller payout status and policy eligibility distinct. Use authoritative policy and relevant business evidence before explaining eligibility or a hold reason.

Open the corresponding Google session and trace to inspect the hosted execution. An optional Langfuse trace can show the application boundary; it does not replace Google's internal trace. Same-session follow-ups should retain the relevant order context. Workspace Internal/Mem0 controls do not configure hosted Google or Lyzr memory.

## What to document

Record the actual application, hosted agent and backend locations; tool arguments and results; supported answer claims; session continuity; identity and access boundaries without secret values; trace links; enabled cost categories; and any failed or untested checks. Do not invent spending or claim deployment work you only observed.

A simple diagram should identify what the ADK code defines, what Google hosts, and why the separate business backend is needed. Distinguish observed behavior from documented capabilities. The existing instructor integration has been exercised, but a complete fresh learner-project setup has not been rehearsed independently.

Use the shared [Basics setup guide](../../../setup/google-agent-platform/setup-guide.md), [Marketplace cloud setup](../../../../app/CLOUD-SETUP.md), and [instructor walkthrough](../instructor-demo.md) for the corresponding steps. Cleanup applies only to resources you created; preserve instructor deployments and business data.
