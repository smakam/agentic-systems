# Chapter 7 exercise: Prompt and context

## UI, database and cleanup

**UI:** [test marketplace](http://127.0.0.1:5179/) from Course Setup; use the role/workspace named in each task. **Database:** disposable practice database `market_test`, separate from main `market` and the fixed evaluation baseline `market_eval`. Test UI changes do not update the main marketplace. Save your questions, results and traces locally.

Use Support with OpenAI Agents SDK and a fresh conversation for each condition. Business questions are read-only; the context controls change returned tool data, not stored catalog, documents or business records.

**Cleanup:** restore both suppression controls to off and the original workspace options. No business database reset is required; saved conversations and traces remain.


## Your tasks

Repeat the questions and context comparison covered in the demo. There is no additional challenge and nothing to submit. Keep your observations locally and compare them with the reference solution.

## Before you start

Complete local setup and start the normal stack with `scripts/start.sh`. Use the support workspace and local Langfuse. Use the course model configuration and a fresh conversation for each question. Note the business revision and demo clock. Use the separate questions below. The questions investigate records and policies without changing marketplace business data. Conversations and traces are saved as usual.

## Part 1: Repeat the context queries

### 1. Entity definitions

Ask: “For Cedar & Co., show captured, refunded, fees, paid out, and unpaid in rupees. Explain what unpaid includes.”

### 2. Relationships

Ask: “What products and quantities are in order-1, and who sells them?”

### 3. Policies

Ask: “What is the payout hold after an item is marked delivered, and what can block release?”

For each question, open its Langfuse trace and inspect the model calls and tool results. Locate:

- Stable instructions and tool schemas, where the trace exposes them.
- The question, revision, clock and any retained history.
- Catalog definitions or relationships returned before SQL.
- Current records and policy passages actually retrieved.
- The later model input that receives each tool result and the final citations.

A query can use several kinds of context. Label only sources visible in your trace. Tool schemas may be recorded separately from the input-message array.

## Part 2: Repeat the UI context comparison

Use the **test marketplace** at `http://127.0.0.1:5179`, sign in as support, and select OpenAI Agents SDK. Under Workspace options, expand **Context comparison**. Keep the model, business revision and demo time fixed.

1. Clear both suppression options, turn long-term memory off, and ask the definitions and policy questions in separate fresh conversations.
2. Enable **Suppress catalog context** and repeat the definitions question. Changing the setting starts a fresh conversation and turns memory off. Inspect the tool result and answer.
3. Clear catalog suppression, enable **Suppress policy retrieval**, and repeat the policy question in the new conversation. Inspect whether the agent makes a policy claim without passages.
4. Clear both options and repeat the same definitions and policy questions separately in a fresh conversation. Verify that catalog and policy evidence return.

Both tool calls return success. Catalog suppression returns null catalog data and retrieval suppression returns an empty passage list. No tool error or stop instruction is injected. These are valid tool responses, not malformed null responses. Tool names and schemas remain visible. Current business records remain available through other tools, so this experiment suppresses two specific context sources rather than every possible source of information.

Compare final answers and the actual tool outputs in evidence and Langfuse. Check whether the model stops before SQL without catalog definitions and whether it avoids policy assertions without passages. These are expectations to test, not enforced outcomes. Record the behavior you observe rather than assuming the model must fail. The controls apply only to the local SDK in the test workspace and do not change stored ontology or documents. Restore both settings when finished. No business-data reset is required.

The earlier saved full/reduced/restored catalog experiment removed selected fields through a standalone runner. It is background evidence for a different experiment, not the procedure for this UI comparison.

## What to check and record

| Question or condition | Model call | Context item | Static configuration or dynamic input | Source | How it supports the answer |
|---|---|---|---|---|---|
| | | | | | |

Record missing context, actual tool calls, SQL, answer differences and citations. Report observed results without requiring removal to cause a wrong answer. For a fresh run, amounts and eligibility depend on current records and demo time.

See [the reference solution](solutions/answers.md). The [historical comparison note](supplied-trace.md) describes a different earlier experiment and is not a prerequisite for the current UI exercise.

Observed rehearsal outcome: empty-success catalog data led to attempted SQL and a turn-limit stop. Empty-success policy passages led to a qualified answer declining to confirm the policy. Treat your own run as an observation, not a guaranteed repeat.
