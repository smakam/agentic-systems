# The Agent Loop with OpenAI Agents SDK — worked solution

Run all shell commands from your repository root unless a different directory is shown. Course Setup supplies the already-running local interfaces, PostgreSQL, gateway and Langfuse. This README primarily explains the optional developer loop implementation and its checks. The UI always uses the SDK loop. Developer commands run a separate selected implementation in a one-off process; they do not replace the UI loop or start two loops for the same question.

## Part 1 — repeat the three UI demos

Follow the exact question and three demonstration sequences in [exercise.md](../exercise.md). Open [the Agent Loop lab](http://localhost:5181/), which normal Course Setup already starts. Its database is `ch11_loop_lab`, separate from the standard test UI's `market_test`. These are read-only scenarios; no extra launch or database reset is required. Use a fresh conversation for each condition and restore Normal afterward.

Compare your observed model/tool counts, recovery and stopping behavior with [the saved validation](VALIDATION.md). Hooks supply model-call/token counters and tool-attempt records. Elapsed time and evidence-save counts come from other application layers. Exact live counts and wording may vary.

## Part 2 — optional developer extension: implement and test your loop

Implement [starter.py](../starter.py) using the exercise requirements, or inspect [the reference implementation](minimal_loop.py) after attempting it. These checks are only for this developer extension, not prerequisites for UI practice. They use scripted model/tool responses and make no API calls.

### Check the supplied reference solution

```bash
python3 -m unittest discover -s course/exercises/agent-loop/solutions -p test_loop.py
```

This checks `solutions/minimal_loop.py` and should pass.

### Check your implementation after completing starter.py

```bash
LOOP_IMPLEMENTATION=starter python3 -m unittest discover -s course/exercises/agent-loop/solutions -p test_loop.py
```

This runs the same checks against your implementation. The distributed starter is an unfinished template, so complete it before using this command to verify your work; demonstrating an expected failure is not a separate exercise.

The five checks cover model/tool result pairing, multiple tools in one turn, invalid/unknown requests without execution, error repair, and stopping before another model call. They require no API credit.

## Run your loop with a real model and MCP tools

After your offline checks pass, run your `starter.py` implementation on the supplied order-2 question using the real configured gateway and the lab's real read-only MCP tools. Unlike the scripted checks, this makes paid model calls and reads `ch11_loop_lab`. It runs as a separate command-line process inside the existing lab backend; it does not use or replace the Agents SDK Runner behind the UI.

### Execute your implementation

```bash
docker compose -f app/compose.yaml -f app/compose.ch11.yaml --profile chapter11 exec -T ch11-backend python /exercise/solutions/live_adapters.py --implementation starter --output /tmp/ch11-starter-loop.json
```

The adapter supplies the question, model client and MCP connection. Your loop decides when to request the model, execute tools, return tool results and stop. The output contains the final answer, model/tool events, usage and retained evidence. The `--output` location is inside the `ch11-backend` container, not yet on your laptop.

### Copy the transcript to your laptop

```bash
docker compose -f app/compose.yaml -f app/compose.ch11.yaml --profile chapter11 cp ch11-backend:/tmp/ch11-starter-loop.json /tmp/ch11-starter-loop.json
```

After the copy succeeds, open `/tmp/ch11-starter-loop.json` on your laptop in VS Code or another JSON viewer. It is a different file from the container path, even though both paths have the same spelling. Save a lasting copy in your chosen results folder before deleting temporary files.

To run the supplied reference implementation instead, choose `--implementation minimal_loop` and a different output filename. You are choosing one implementation per command, not running both. Compare your transcript with an SDK run of the same question in the UI; conduct the runs sequentially. The minimal loop has its own JSON transcript, not the SDK's Langfuse trace tree. No source edit to `marketplace/agent.py` is required.

The example solution returns a final response only when tool calls are absent, appends paired result IDs, validates names/JSON, and gives an incomplete result on the limit. It deliberately lets operational adapter failures propagate rather than disguising outages as empty results. In a production implementation, add explicit schemas, time/cost budgets, cancellation, observability, persistent sessions and failure handling.

## Saved examples and comparison

These are recorded reference examples, not the outputs of your fresh run:

| File | What it contains | How to use it |
|---|---|---|
| [demo-results.json](demo-results.json) | Three SDK UI investigations: Normal, Recovery and Turn-limit stop; answers, retained evidence, hook metrics, tool-attempt outcomes and Langfuse trace references | Reference for the instructor/UI demos |
| [minimal-loop-live.json](minimal-loop-live.json) | One live run of the supplied manual loop: messages, ordered model/tool events, final answer, status, turns, usage and evidence | Example of the manual loop transcript format; not an SDK Langfuse trace |
| [VALIDATION.md](VALIDATION.md) | Checks performed, observed behavior, limitations and recorded environment | Understand what was actually verified |

Your own transcript is `/tmp/ch11-starter-loop.json` after the live run and copy steps above. Compare it with an SDK UI run using the same question and lab records:

| Compare | SDK UI / Langfuse | Your saved JSON |
|---|---|---|
| Model requests and tool decisions | Model observations in the trace | `events` entries with `kind: model` |
| Tool arguments, results and errors | Tool observations and saved run metrics | `events` entries with `kind: tool` |
| Counts | UI model-call/tool-invocation counters | `turns` and the number of tool events |
| Completion or stopping | Run status, stopping message and error type | `status` and `answer` |
| Answer support | Answer citations and retained UI evidence | `answer` and `evidence` |
| Usage | Saved usage metrics/model observations | Per-response `usage` entries |

Offline checks produce no Langfuse trace. The manual live adapter saves this JSON transcript and does not install the SDK tracing integration. Gateway model calls may be recorded separately, but real MCP calls do not automatically create a complete Langfuse loop trace. Compare functional behavior across the two recording formats; do not expect identical tool order, prose or trace layout. The short manual prompt is not identical to the full SDK prompt, so this is an orchestration exercise rather than a fair quality/cost benchmark.

The SDK one-turn demonstration should stop with an explicit incomplete result. Recovery should show the injected failure and a later successful read; check actual evidence rather than requiring the historical exact counts.

## Cleanup

After the UI comparison, restore Normal and keep the recorded results. Read-only repetitions do not require a database reset. When finished using the application, stop the workspaces together using the normal Course Setup stop instructions. If you edited application source or configuration for your own implementation, undo those edits and restart the affected service before returning to the normal course flow. The fixed evaluation baseline remains unchanged.
