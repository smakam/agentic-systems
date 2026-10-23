# Chapter 17: Agent Design Patterns — instructor demo

## Workspace for this activity

Use the [Test workspace](http://127.0.0.1:5179), **Support workspace**, with the disposable **market_test** database. Inspect agent-role handoffs in [local Langfuse](http://localhost:3000), project **marketplace-support**. Select **Agent design demo** in this workspace, rather than the normal marketplace on port 5178.

## Goal

Show how a hybrid multi-agent workflow passes information between generator, reviewer and correction roles, and how to debug those stages in Langfuse. This is an interaction walkthrough, not a benchmark or proof that review improves every answer.

## Setup

1. Open the [Test workspace](http://127.0.0.1:5179). Sign in as `support` with the public demo password `demo-marketplace`.
2. Open **Support workspace**. Refresh the page if **Agent design demo** is missing.
3. Check that documents are indexed. Use a clean policy corpus. If the Security demo shows a forged/paraphrase document, ask the operator to select **Clean policy**, then return to Support. Do not reset business data merely to run this demo.
4. Note the current data revision and demo clock. Expected business facts below assume the seeded revision-one workspace; changed data must be checked against its current evidence.
5. In **Agent design demo**, select **Hybrid · generate, review, correct**, **Generator: GPT-5 Nano**, **Reviewer: GPT-5.4**. The app starts a fresh conversation, turns memory off and keeps routing off. Models are fixed for this workflow; changing any demo setting starts a fresh conversation.

### What the three modes mean

| Mode | Behavior |
|---|---|
| Off · normal support | Ordinary support agent using the configured default model (currently GPT-5.4). |
| Generator only | Single support-agent loop with the chosen generator model; no reviewer. A baseline for inspecting the additional workflow stages. |
| Hybrid · generate, review, correct | Generate a draft, evaluate it, then accept it or run one correction with the generator model. |

All roles use the OpenAI Agents SDK. The generator and correction roles can use the existing read-only business tools. The reviewer has its own instructions and model but no tools: one structured evaluation call, without a golden answer. Code controls the sequence and the correction limit.

## Case A — follow the accept path

1. Use the setup settings above in a fresh conversation.
2. Enter exactly: **List the products and quantities in order-2.**
3. Click **Investigate** and wait for completion.
4. Inspect the final answer and click its evidence. The seeded facts are **Ceramic Mug Set, 2 units**.
5. Expand **Hybrid workflow** beneath the answer. Inspect **Generate draft** and **Review draft**. Open each **Stage input** to see the handoff: the generator receives the question and snapshot; the reviewer receives the question, draft and original evidence (plus retained prior context when relevant).
6. Find **Revision requested** and **Evidence sufficient**. In the saved rehearsal the reviewer accepted the draft, so no correction stage ran. A fresh run can differ; record what happened rather than assuming acceptance.
7. Open **Workflow trace**. Follow the Langfuse instructions below.

## Case B — explain a return after the seller was paid

This is the main correction example. A fresh rehearsal on 23 October 2026 showed Nano repeating the return status without explaining its cause; GPT-5.4 identified the missing post-payout rule, and Nano added the supported reason. A fresh run may already answer correctly or produce different feedback. Do not rerun until a desired mistake appears.

### Prepare the business scenario once

Use a new order in **Test workspace**. This setup deliberately creates simulated business events and advances the shared Test demo clock; it is not a support-agent action. Keep existing investigations and records; do not reset the workspace.

1. As **buyer**, purchase one Desk Lamp. Note the new order ID.
2. In **Orders & fulfillment**, use an authorized operator/seller account to dispatch and deliver that item's shipment.
3. As **operator**, open **Seller settlement** and use **Advance demo clock 24h**. Confirm delivery occurred at least 24 hours before the new clock.
4. For the new order's item, choose **Release payout** and confirm its status is **completed**. Do not use Simulate failure.
5. Switch to **buyer** and request a return for that delivered item. Confirm the return is **manual_review**. The completed payout must precede the return request.
6. Return to **Support workspace** as support. Use the actual new order ID in the question below; historical experiment order IDs are not guaranteed to exist here.

### Run and inspect

1. Select **Generator only**, **Generator: GPT-5 Nano**, in a fresh conversation.
2. Ask: **Why is the return for <prepared order ID> in manual review? Did the seller reject it?** Replace the placeholder with the new order ID.
3. Inspect whether the answer explains the cause rather than merely repeating the status. Keep this baseline; do not assume it must be wrong.
4. Select **Hybrid · generate, review, correct**, **Generator: GPT-5 Nano**, **Reviewer: GPT-5.4**. Repeat exactly the same question in the fresh conversation created by the setting change.
5. Inspect **Generate draft**, **Review draft**, **Workflow decision**, and any **Correct draft**. The hybrid generates a new draft; compare its own draft with its final answer to identify a correction. Comparing separate generator-only and hybrid runs does not isolate reviewer effects.
6. In the verified rehearsal, the draft said the return was in manual review but omitted why. Review pointed to the completed payout before the return and the policy that post-payout returns require manual review because automatic recovery is not implemented. The correction added that explanation and stated that no seller rejection was recorded.
7. Verify the final explanation against payout and return records, event chronology, and the policy note. Neither an accepted draft nor a completed correction independently proves correctness.
8. If the fresh draft is already complete, explain the accept path and show the recorded successful correction below rather than manufacturing an error.

[Recorded successful return correction](http://localhost:3000/project/marketplace-support/traces/e4f50865dc8ad540661f4670538d7d24).

[Rehearsal setup, before/after summary and limits](../../authoring/chapter-17-agent-design/success-rehearsal.md).

### Optional limitation example

The earlier order-1 question, **For order-1, which items can have their seller payout released at the current demo clock? Separate policy eligibility from current payout status**, exposed missing delivery evidence. Review withdrew unsupported eligibility claims, but correction did not retrieve the missing records. Keep this only as an explicitly incomplete correction, not the main success demonstration.

## Case C — optional controlled model change

1. Select **Generator only**, **Generator: GPT-5 Nano**, and repeat the prepared return question in a fresh conversation. Document its answer and evidence.
2. Select **Hybrid · generate, review, correct**, keeping **Generator: GPT-5 Nano**. Choose **Reviewer: GPT-5 Nano** and repeat the same question.
3. Change only **Reviewer** to **GPT-5.4** and repeat in the fresh conversation created by that change.
4. Inspect role inputs, feedback and any correction. Changing reviewer settings also generates a fresh draft, so these live runs are not a matched-draft reviewer ablation. Explain the interactions; do not infer a quality ranking from one run.
5. Learners may choose GPT-5.4 as generator too. The correction role always uses the selected generator model.

## Read the workflow in Langfuse

1. Use the answer’s **Workflow trace** link, rather than trying to identify a run by model name alone.
2. Under **support-investigation**, find **Generate draft**, **Review draft**, **Workflow decision** and, when selected, **Correct draft**. They share one trace and have the support investigation as their parent.
3. Expand the generator’s SDK agent/turn/generation and tool observations. Identify its question, tool arguments, evidence and draft. A single role can contain several model calls.
4. Select **Review draft** and use **Preview** to read its input and structured output. The reviewer has one generation and no tool observations. Its input is the handoff contract.
5. Select **Workflow decision**. Its output records `accept_draft` or `correct_once`. That branch is executed by application code, not by an extra coordinator model.
6. If present, inspect **Correct draft** in the same way. Trace the review feedback into the correction input; note whether it requested any new tool evidence.
7. In **Attributes → Metadata**, read the role and requested model alias (`eval-nano` or `eval-54`). Generation/gateway observations may show a provider model/version or a gateway alias. An alias is a configuration name, not a separate model or a virtual key.
8. Debug in this order: evidence gathering → draft claims → reviewer feedback → controller branch → correction → final answer. A missing stage can mean the accept branch was chosen; a failed stage does not mean the whole workflow succeeded.

The local Langfuse v4 deployment uses the [Observations API v2](https://langfuse.com/docs/api-and-data-platform/features/public-api) for readback; legacy API 404s do not imply tracing failed.

## Failure and cleanup

- If a stage fails or times out, inspect the failed stage and trace. The run is marked failed; the app does not save an unreviewed draft as a completed conversation answer. Evidence collected so far remains in the run.
- The workflow shares a deadline and model-cost budget across stages. The displayed app cost uses conservative GPT-5.4 uncached rates for all stages; it is not a model-specific bill or a performance comparison.
- Finish by selecting **Off · normal support** and starting a new conversation. Keep business data unchanged.

Code: [workflow controller](https://github.com/smakam/agentic-systems/blob/main/app/backend/marketplace/agent_design_demo.py). Historical experiments remain separate: [seller agents](https://github.com/smakam/agentic-systems/blob/main/app/scripts/payout-orchestration.py), [saved-draft reviewer ablation](https://github.com/smakam/agentic-systems/blob/main/app/scripts/reviewer-workflow-core18.py).
