# The Agent Loop with OpenAI Agents SDK — worked solution

Run all shell commands from your repository root unless a different directory is shown. Course Setup supplies the already-running local interfaces, PostgreSQL, gateway and Langfuse. This file explains the supplied runnable loop and its optional checks. The UI always uses the SDK loop. Developer commands run a separate selected implementation in a one-off process; they do not replace the UI loop or start two loops for the same question.

## Part 1 — repeat the three UI checks

Follow the exact question and three UI sequences in [exercise.md](../exercise.md). Use [Test workspace](http://127.0.0.1:5179/) → Support → OpenAI Agents SDK → Workspace options → Agent loop. No separate UI launch, code edit, service restart or database reset is required.

- **Normal:** the model-response and tool-attempt counts under the answer should match the corresponding completed generations and tool invocations in Langfuse. A cache statistic is a different measurement; an evidence save is not necessarily one tool call.
- **Fail first business query:** the first query_business_data attempt fails before SQL execution. A subsequent model-selected retry should succeed and support the answer. Only that tool’s first attempt is injected, and a fresh question gets its own injection. Record what the model actually does; instructions do not guarantee recovery.
- **Stop after one model step:** one model response may request tools that return valid evidence. When another model response is needed, max_turns prevents it and the application reports incomplete. A successful tool is not the failed operation. No second model request was sent, so no second provider-generation span is expected.

The settings apply per question and persist until changed/reset. A new question starts a new run with its own allowance. Normal restores the usual eight model steps; Reset to defaults also restores Normal without replacing the current conversation. Original answers and evidence remain available.

The responsibilities are separate: gateway/client retries (when configured) repeat failed model requests; the SDK runs the loop and enforces the turn limit; the model chooses tool retry/argument repair; application/tool code returns errors, enforces permissions/time/cost/evidence budgets and reports incomplete. The model-finish hook checks accumulated estimated cost after a response, not before charging for it. Tool hooks duplicate some Langfuse measurements for local UI use; they are not required for tracing.

[Earlier saved validation](VALIDATION.md) describes historical runs in the legacy lab. Do not treat those dates, exact counts or order statuses as current Test facts.

## Run and explain — supplied loop example

The [complete starter](../starter.py) already implements the small model–tool loop; no TODOs or coding are required. The default offline example returns two model steps, one tool invocation and a completed answer. These runs are free and do not access the marketplace database.

The live-adapter file is reference material for this activity: it shows how real model calls and read-only MCP tools connect to the same loop. Its backend setup is separate and is not required for the learner run. The UI remains on the SDK runner.

### File roles — expected write-up

- **starter.py:** the ready-to-run offline entry point. It defines a scripted model, a sample tool and its schema, then calls the imported `run_loop`. No edits are required.
- **solutions/minimal_loop.py:** the reusable orchestration function. This is where the repeated model → requested tools → tool feedback sequence lives.
- **solutions/live_adapters.py:** connects the same loop to real model requests and read-only MCP tools. It discovers available tool schemas and passes the model/tool functions into the loop. There is no SDK Agent registration or Runner in this example.
- **solutions/test_loop.py:** verifies the loop with scripted model/tool functions. Tests check behavior rather than provide the live connections.
- **Results JSON:** generated observations, not source code. It records messages, events, the answer and the stopping status. Older saved results describe their own run, not necessarily today’s records.

The offline run requests a tool in its first model step, appends the tool result to the messages, then supplies those messages to the second model step to produce the final answer. The browser demo already covers the turn-limit comparison; learners do not repeat it here.

### What the supplied loop does

1. Starts with instructions and the question.
2. Requests a model response and retains it.
3. Executes only allowed tool requests, pairing results with their call IDs.
4. Supplies results/errors to the next model step.
5. Returns a final answer when no tool calls remain, or stops incomplete at the selected limit.

This illustrates orchestration rather than production feature parity. Network connections, provider API calls and real MCP execution belong to the adapters. Validation and read-only SQL permissions remain in the tool server. Changing the separate example does not change the UI agent or business records.

### Optional scripted checks

These five checks verify tool-result pairing, multiple tool calls in one model step, rejected malformed requests, repair feedback and the step boundary. They make no API calls:

```bash
LOOP_IMPLEMENTATION=starter python3 -m unittest discover -s course/exercises/agent-loop/solutions -p test_loop.py
```

The reference implementation remains available in [minimal_loop.py](minimal_loop.py), and the earlier [validation record](VALIDATION.md) is historical. No database reset is required after these read-only examples. Do not run the legacy reset scripts against the shared Test workspace.
