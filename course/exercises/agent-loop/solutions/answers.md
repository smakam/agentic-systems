# The Agent Loop with OpenAI Agents SDK — worked solution

Run all shell commands from your repository root unless a different directory is shown. Course Setup supplies the already-running local interfaces, PostgreSQL, gateway and Langfuse. This file explains the supplied runnable loop and its optional checks. The UI always uses the SDK loop. Developer commands run a separate selected implementation in a one-off process; they do not replace the UI loop or start two loops for the same question.

## Part 1 — repeat the three UI checks

Use “What is the status of order-2?” and follow the three UI sequences in [exercise.md](../exercise.md). Use [Test workspace](http://127.0.0.1:5179/) → Support → OpenAI Agents SDK → Workspace options → Agent loop. No separate UI launch, code edit, service restart or database reset is required.

- **Normal:** the model-response and tool-attempt counts under the answer should match the corresponding completed generations and tool invocations in Langfuse. A cache statistic is a different measurement; an evidence save is not necessarily one tool call.
- **Fail first business query:** the first query_business_data attempt fails before SQL execution. A subsequent model-selected retry should succeed and support the answer. Only that tool’s first attempt is injected, and a fresh question gets its own injection. Record what the model actually does; instructions do not guarantee recovery.
- **Stop after one model step:** one model response may request tools that return valid evidence. When another model response is needed, max_turns prevents it and the application reports incomplete. A successful tool is not the failed operation. No second model request was sent, so no second provider-generation span is expected.

The settings apply per question and persist until changed/reset. A new question starts a new run with its own allowance. Normal restores the usual eight model steps; Reset to defaults also restores Normal without replacing the current conversation. Original answers and evidence remain available.

The responsibilities are separate: gateway/client retries (when configured) repeat failed model requests; the SDK runs the loop and enforces the turn limit; the model chooses tool retry/argument repair; application/tool code returns errors, enforces permissions/time/cost/evidence budgets and reports incomplete. The model-finish hook checks accumulated estimated cost after a response, not before charging for it. Tool hooks duplicate some Langfuse measurements for local UI use; they are not required for tracing.



## Run and explain — supplied real-model loop

Use the single command in [exercise.md](../exercise.md). The supplied files are complete; no coding is required. This is a separate process, not a replacement for the marketplace UI's SDK runner.

### File roles

- **starter.py:** defines the local sample quantity tool and its schema. Its model function sends the messages and tool schema to the real model through the configured Test gateway. It calls the imported `run_loop` and prints the result.
- **solutions/minimal_loop.py:** owns orchestration. It retains the model response, validates and executes requested tools, pairs each result with its tool-call ID and supplies the updated conversation to the next model call. It returns the final answer or an incomplete result at the step limit.
- **exercise.md:** gives the command and observation task.
- **solutions/answers.md:** provides these explanations.

### Expected observations

The first model response requests `lookup_quantity`. The local function returns the sample quantity, two. The loop appends that result to the messages. The next model call reads it and answers. The validated live run completed with two model calls and one tool invocation; model behavior can vary, so inspect the actual events.

The quantity is fixed sample data, but neither the model's tool request nor its final answer is scripted. No MCP server or marketplace database is accessed by this sample tool. The real model calls consume API credit. JSON is printed output, not an additional source file learners must manage. The browser activity already demonstrates stopping; this activity focuses on how the custom loop works.
