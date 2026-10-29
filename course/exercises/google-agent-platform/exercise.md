# Practice: deploy a standalone agent, with an optional cloud integration

The standalone practice uses **Support Agent Basics** in Google Playground. Deploy it with the chapter setup guide, or observe the instructor and label your work observation only. Record the native lookup, same-session follow-up, sessions, traces and logs. The full cloud chat/MCP/database integration below is an **adventurous optional extension**, not a requirement for the core chapter.

## Standalone Basics deployment

Use the chapter’s [setup-guide.md](../../setup/google-agent-platform/setup-guide.md) to create your separately named **Support Agent Basics** deployment. It contains prerequisites once, editable environment values, installation and the two test/deploy commands. Then follow [instructor-demo.md](instructor-demo.md) for questions and observations in native Playground. If you are observing the instructor rather than deploying, label that clearly. This standalone setup needs no marketplace, MCP middleware, database or tunnel.

## Core practice: Basic support agent

Complete [setup-guide.md](../../setup/google-agent-platform/setup-guide.md) first, then use [instructor-demo.md](instructor-demo.md). The setup guide validates deployment; the steps here are what to explore afterward. [Basic agent code](../../../app/google/basics/support_agent_basics/agent.py).

1. In a fresh session ask **“What products and quantities are in order-demo-2?”** Compare the answer with the actual native lookup result and packaged fixture.
2. Ask **“What is its payout status?”** in the same session. Inspect retained context; a new tool call is not required if the earlier fixture evidence is already available.
3. In a new session ask about **order-demo-999**. Inspect the not-found result and check that no order status is invented.
4. Open the completed session/trace. Follow model input → tool arguments → result → answer. Then inspect available runtime logs/monitoring and distinguish them from quality evaluation.

## Optional practice: Marketplace support agent

### Setup and starting point

Use the **full cloud Marketplace application** for this extension. Complete [Cloud Setup](../../../app/CLOUD-SETUP.md) steps 1–4: deploy the Marketplace project, deploy the Marketplace-compatible Google agent in the agent project, connect the web backend to that runtime, and verify it end to end. The frontend/backend, business MCP service and database stay in Google Cloud; the Google agent runs in its managed runtime. This course path does not use a local caller or laptop tunnel.

The standalone Basics deployment has no business MCP tools and is not the deployment to update. Selecting Google in chat calls a configured runtime; it does not deploy one or repoint its business endpoint. Use your own separately identified resources and preserve instructor deployments. The setup guide contains the commands; this exercise covers behavior and evidence afterward.

The instructor completed one uninterrupted clean reinstall on 29 October 2026 after removing course resources in two existing test projects. Enabled APIs and default networking were retained; this does not verify a brand-new account, every operating system or every provider path. Record any adaptation you make. Costs depend on enabled resources, model calls and usage; consult current billing categories. Keep credentials in private environment/Secret Manager configuration and out of screenshots, prompts and submitted work.

Do not update the instructor's Marketplace Support ADK Lab or Support Agent Basics deployment. A `--backend cloud` update intentionally changes the target of a managed agent; choosing Google runtime in the marketplace UI does not switch that deployed target.

### Practice

1. Open your cloud marketplace Support interface and select **Google ADK**. Use your own hosted Marketplace agent connected to the business MCP backend. [Marketplace agent code](../../../app/google/marketplace_google/agent.py).
2. Start a fresh conversation and ask **“What is the status of order-1?”**, substituting a confirmed order ID from your backend if needed. Compare the answer with the actual tool evidence.
3. In the same conversation ask **“What is the payout status for this order?”** Inspect the retained order context and supporting evidence.
4. Open the corresponding Marketplace agent session in your Google console. Inspect the native model/tool trace and runtime logs. If Langfuse is configured, optionally compare the application trace with Google's internal execution trace.

If you observe the instructor rather than deploying your own system, label your observations **observation only**.

### What to document

| Observation | What to inspect and record |
|---|---|
| Placement | Browser/UI, application backend, hosted agent, MCP and database/policy locations |
| Tools and evidence | Tool name/arguments, returned order fields and claims supported by those fields |
| Session continuity | Same-chat follow-up versus fresh-chat behavior |
| Identity and access | Trusted client user ID, runtime identity and scoped endpoint/secret references; no values |
| Observability | Native session/trace link; optional application-boundary trace link |
| Cost categories | Enabled runtime/model/state/retrieval/telemetry/evaluation components; no invented spend |
| Limits | Failed checks, untested steps and adjustments made |

Add a diagram of the actual end-to-end path and five short explanations: what ADK code does; what Google manages; why the business middleware is still needed; which evidence shows session continuity; and what you would need to operate yourself without the managed runtime. Distinguish observed results from documented product capabilities.

## Cleanup

Follow each guide's cleanup section for **only the resources you created**. Remove your own test sessions/memories if the guide supports it, undeploy the optional lab agent, and tear down your own cloud stack when finished. Verify remaining billable resources in your project. Preserve the instructor deployments and business fixtures. Review your diagram, observations and explanations for yourself, then compare with [solutions/answers.md](solutions/answers.md).
