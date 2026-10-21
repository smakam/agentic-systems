# Agent Design Patterns — learner exercise

## Workspace for this activity

Use the [Test workspace](http://127.0.0.1:5179), **Support workspace**, with the disposable **market_test** database. Inspect agent-role handoffs in [local Langfuse](http://localhost:3000), project **marketplace-support**. Select **Agent design demo** in this workspace, rather than the normal marketplace on port 5178.

## What you will do and submit

Run a small observation lab in the Test workspace. Select the supplied settings, enter the exact questions, inspect the agent-role handoffs in the UI and Langfuse, and fill in the tables below. Submit the tables and four short observations. No code, JSON upload or benchmark report is required.

## Prepare

1. Open [Test workspace](http://127.0.0.1:5179), sign in as `support` (`demo-marketplace`) and open **Support workspace**.
2. Check documents are indexed and the installed policy is clean; ask the operator to restore Clean policy if needed. Record the revision and demo clock; do not change business state.
3. Use **Agent design demo**, not the Model routing demo. Changing its settings starts a fresh conversation. Memory and routing remain off in this lab.

## Part A — baseline and role handoffs

Use this exact question for A1–A3: **For order-2, explain why the seller payout is held. Distinguish buyer payment, delivery status and seller payout, and cite the policy and business evidence.**

| Run | Workflow | Generator | Reviewer | Action |
|---|---|---|---|---|
| A1 | Generator only | GPT-5 Nano | Not used | Investigate the question once. |
| A2 | Hybrid · generate, review, correct | GPT-5 Nano | GPT-5 Nano | Repeat the same question in a fresh conversation. |
| A3 | Hybrid · generate, review, correct | GPT-5 Nano | GPT-5.4 | Change only the reviewer setting; repeat in the fresh conversation. |

For each run:

1. Read the final answer and click its evidence.
2. Expand the workflow stages beneath the answer. For A2/A3, read the draft, the reviewer’s issues and the decision. If correction ran, compare its output with the draft.
3. Open **Workflow trace**. Under **support-investigation**, inspect each stage’s Preview input/output and Attributes metadata. Expand agent/turn/generation and tools as needed.
4. Fill in one row per run. If a field does not apply, write “not run”. If a stage failed, write “failed” and name it; do not label an incomplete run as accepted.

| Run | Revision / clock | Final answer in 1–2 sentences | Draft’s main claim | Reviewer: revision requested / evidence sufficient | Issues and correction instructions (brief) | Decision: accept / correct / failed | Stages and requested model aliases | Trace link |
|---|---|---|---|---|---|---|---|---|
| A1 | | | | Not run | Not run | Generator only | | |
| A2 | | | | | | | | |
| A3 | | | | | | | | |

## Part B — inspect a follow-up and retained context

1. Start fresh. Select **Hybrid · generate, review, correct**, **Generator: GPT-5 Nano**, **Reviewer: GPT-5.4**.
2. Ask: **What products and quantities are in order-1?**
3. In the same conversation, ask: **For that order, explain the failed seller payout attempt and separate it from the other item’s held payout.**
4. Inspect both traces. In the second reviewer input, find the original evidence and any retained prior conversation context. Confirm the correction limit is still one, even when the question is a follow-up.
5. Record both runs in the table. If your current revision differs from the seeded workspace, report the current evidence rather than copying baseline facts.

| Question | Generator model | Reviewer model | Evidence passed to review | Did prior context appear? | Revision requested? | Correction ran? Any new tools? | Final answer / remaining uncertainty | Trace link |
|---|---|---|---|---|---|---|---|---|
| Products and quantities | | | | | | | | |
| Failed versus held payout follow-up | | | | | | | | |

## Part C — document your understanding

Write one or two sentences for each:

1. What information passed from generator to reviewer, and from reviewer to correction?
2. Which component chose the accept/correct branch, and which roles could call tools?
3. Identify one claim in a draft, review or final answer and the evidence supporting it. If evidence is missing, explain what should be retrieved.
4. Did adding review change the answer in your runs? Describe the observation without claiming that one model or architecture is generally better. Fresh drafts can differ, even with the same model.

A correction is not mandatory for completing this exercise. If every draft was accepted, inspect the recorded correction example in the instructor guide and clearly label that row as recorded. A completed correction may still leave missing facts or incorrect reasoning.

Finish by selecting **Off · normal support** and starting a fresh conversation. Compare your explanations with the separate [reference answers](solutions/answers.md) after completing the lab.
