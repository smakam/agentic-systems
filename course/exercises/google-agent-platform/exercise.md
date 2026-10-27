# Practice: deploy a standalone agent, with an optional cloud integration

The standalone practice uses **Support Agent Basics** in Google Playground. Deploy it with the chapter setup guide, or observe the instructor and label your work observation only. Record the native lookup, same-session follow-up, sessions, traces and logs. The full cloud chat/MCP/database integration below is an **adventurous optional extension**, not a requirement for the core chapter.

## Standalone Basics deployment

Use the chapter’s [setup-guide.md](setup-guide.md) to create your separately named **Support Agent Basics** deployment. It contains prerequisites once, editable environment values, installation and the two test/deploy commands. Then follow [instructor-demo.md](instructor-demo.md) for questions and observations in native Playground. If you are observing the instructor rather than deploying, label that clearly. This standalone setup needs no marketplace, MCP middleware, database or tunnel.

## Core practice: Basic support agent

Complete [setup-guide.md](setup-guide.md) first, then use [instructor-demo.md](instructor-demo.md). The setup guide validates deployment; the steps here are what to explore afterward. [Basic agent code](../../../app/google/basics/support_agent_basics/agent.py).

1. In a fresh session ask **“What products and quantities are in order-demo-2?”** Compare the answer with the actual native lookup result and packaged fixture.
2. Ask **“What is its payout status?”** in the same session. Inspect retained context; a new tool call is not required if the earlier fixture evidence is already available.
3. In a new session ask about **order-demo-999**. Inspect the not-found result and check that no order status is invented.
4. Open the completed session/trace. Follow model input → tool arguments → result → answer. Then inspect available runtime logs/monitoring and distinguish them from quality evaluation.

## Optional practice: Marketplace support agent

Follow the linked full cloud setup below for your own resources, then:

1. Open your chat application connected to your hosted ADK deployment and business MCP backend. [Marketplace agent code](../../../app/google/marketplace_google/agent.py).
2. Choose a confirmed order in your backend. Ask for products, payment and payout status, then a follow-up policy/why question that matches its actual state.
3. Inspect business and policy tool results, final evidence, session continuity, native trace and logs. Explain what the separate backend provides that the Basics fixture does not.

## Optional full cloud integration

The remainder is an adventurous extension. It connects a cloud chat application and business backend/data to the separate Google-hosted agent. It is not required to understand the standalone Basics lesson.

## Environment and starting point

Use your **own Google Cloud project and separately identified lab resources** for provisioning. Complete [app/CLOUD-SETUP.md](../../../app/CLOUD-SETUP.md) first: your cloud chat/backend, business MCP and database must already work. Then follow [Google Platform Plan](../../GOOGLE-PLATFORM-PLAN.md) steps 1–6: configure your marketplace ADK agent and MCP secret, create or update your own compatible runtime, verify it in Playground, connect the cloud chat backend, and verify end to end. The standalone Basics agent has no business MCP tools and is not the deployment to update. These guides contain the commands; this exercise does not duplicate their deployment sequence.

The current instructor deployment has verified cloud acceptance. The cloud setup sequence has not yet been rehearsed from scratch in a fresh learner project. Treat that as a stated preparation limit and record any adaptation you make. Costs depend on enabled resources, model calls and usage; consult current billing categories. Keep credentials in private environment/Secret Manager configuration and out of screenshots, prompts and submitted work.

Do not update the instructor's Marketplace Support ADK Lab or Support Agent Basics deployment. A `--backend cloud` update intentionally changes the target of a managed agent; choosing Google runtime in the marketplace UI does not switch that deployed target.

## What to do

1. Verify your already completed Cloud Setup: the cloud marketplace UI/backend, authenticated business MCP endpoint and database/policy store must be working. Record their locations; do not redeploy the stack for this exercise.
2. Follow [Google Platform Plan](../../GOOGLE-PLATFORM-PLAN.md) to create your own marketplace ADK deployment or update an existing compatible deployment you own. Bind its runtime identity to your cloud MCP secret and endpoint. Keep model endpoint, runtime/session region and access permissions explicit.
3. Confirm the selected deployed agent's URL/secret profile in deployment metadata. Record the resource names without secret values.
4. Open your marketplace's Support interface, select **Google hosted runtime**, and start a fresh conversation. Ask **“Show the items and quantities for order-2.”** Check the answer against the tool evidence from your own fixture.
5. In the same conversation ask **“What is their total quantity?”** Inspect the preserved order context and any fresh tool calls. Then try the follow-up in a new conversation and record whether it asks which order you mean.
6. Inspect the native Google session, tool events and trace for that run. If your cloud stack has Langfuse enabled, compare the application boundary observation with native platform-internal events. The presence of one does not prove the other is configured.

If you only observe the instructor's full-stack demonstration, label your submission **observation only** rather than claiming you deployed the system.

## What to document

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
