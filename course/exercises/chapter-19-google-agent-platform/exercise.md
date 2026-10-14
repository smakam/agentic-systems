# Practice: deploy a standalone agent, with an optional cloud integration

The standalone practice uses **Support Agent Basics** in Google Playground. Deploy it with the chapter setup guide, or observe the instructor and label your work observation only. Record the native lookup, same-session follow-up, session/trace and memory behavior. The full cloud chat/MCP/database integration below is an **adventurous optional extension**, not a requirement for the core chapter.

## Standalone Basics deployment

Use the chapter’s [setup-guide.md](setup-guide.md) to create your separately named **Support Agent Basics** deployment. It contains prerequisites once, editable environment values, installation and the two test/deploy commands. Then follow [instructor-demo.md](instructor-demo.md) for questions and observations in native Playground. If you are observing the instructor rather than deploying, label that clearly. This standalone setup needs no marketplace, MCP middleware, database or tunnel.

## Optional full cloud integration

The remainder is an adventurous extension. It connects a cloud chat application and business backend/data to the separate Google-hosted agent. It is not required to understand the standalone Basics lesson.

## Environment and starting point

Use your **own Google Cloud project and separately identified lab resources** for provisioning. Follow [app/CLOUD-SETUP.md](../../../app/CLOUD-SETUP.md) for the Cloud Run marketplace, business MCP and Cloud SQL stack, then [GOOGLE-PLATFORM-PLAN.md](../../GOOGLE-PLATFORM-PLAN.md) for the managed ADK agent, identity and cloud MCP profile. These guides contain the commands; this exercise does not duplicate their deployment sequence.

The current instructor deployment has verified cloud acceptance. The cloud setup sequence has not yet been rehearsed from scratch in a fresh learner project. Treat that as a stated preparation limit and record any adaptation you make. Costs depend on enabled resources, model calls and usage; consult current billing categories. Keep credentials in private environment/Secret Manager configuration and out of screenshots, prompts and submitted work.

Do not update the instructor's Marketplace Support ADK Lab or Support Agent Basics deployment. A `--backend cloud` update intentionally changes the target of a managed agent; choosing Google runtime in the marketplace UI does not switch that deployed target.

## What to do

1. Deploy the optional cloud marketplace stack using the cloud setup guide. Record which service hosts the UI/backend, the authenticated business MCP endpoint, and the database/policy store.
2. Deploy a separately named ADK agent using the Google walkthrough. Bind its runtime identity to your cloud MCP secret and endpoint. Keep model endpoint, runtime/session region and access permissions explicit.
3. Confirm the selected deployed agent's URL/secret profile in deployment metadata. Record the resource names without secret values.
4. Open your marketplace's Support interface, select **Google hosted runtime**, and start a fresh conversation. Ask **“Show the items and quantities for order-2.”** Check the answer against the tool evidence from your own fixture.
5. In the same conversation ask **“What is their total quantity?”** Inspect the preserved order context and any fresh tool calls. Then try the follow-up in a new conversation and record whether it asks which order you mean.
6. Inspect the native Google session, tool events and trace for that run. If your cloud stack has Langfuse enabled, compare the application boundary observation with native platform-internal events. The presence of one does not prove the other is configured.
7. Optionally perform the walkthrough's cross-session memory test using the **same client-supplied user ID** for saving and recall. Record the trigger, stored result and retrieval separately; do not infer long-term memory from an answer that could come from the current transcript.

If you only observe the instructor's full-stack demonstration, label your submission **observation only** rather than claiming you deployed the system.

## What to document

| Observation | What to inspect and record |
|---|---|
| Placement | Browser/UI, application backend, hosted agent, MCP and database/policy locations |
| Tools and evidence | Tool name/arguments, returned order fields and claims supported by those fields |
| Session continuity | Same-chat follow-up versus fresh-chat behavior |
| Identity and access | Trusted client user ID, runtime identity and scoped endpoint/secret references; no values |
| Observability | Native session/trace link; optional application-boundary trace link |
| Memory, if tested | Save/generation trigger, stored content, new-session retrieval and identity |
| Cost categories | Enabled runtime/model/state/retrieval/telemetry/evaluation components; no invented spend |
| Limits | Failed checks, untested steps and adjustments made |

Add a diagram of the actual end-to-end path and five short explanations: what ADK code does; what Google manages; why the business middleware is still needed; which evidence shows session continuity; and what you would need to operate yourself without the managed runtime. Distinguish observed results from documented product capabilities.

## Cleanup

Follow each guide's cleanup section for **only the resources you created**. Remove your own test sessions/memories if the guide supports it, undeploy the optional lab agent, and tear down your own cloud stack when finished. Verify remaining billable resources in your project. Preserve the instructor deployments and business fixtures. Submit the diagram, observation table and explanations, then compare with [solutions/answers.md](solutions/answers.md).
