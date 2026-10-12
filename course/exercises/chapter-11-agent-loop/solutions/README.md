# Chapter 11 — Worked solution and demo setup

Run all shell commands from `/Users/srmakam/mycode/agentic-systems` unless a different directory is shown. The existing local stack supplies PostgreSQL, gateway and Langfuse. These commands create separate UI/API services; no cloud SQL startup is required.

## Prepare a repeatable baseline

```bash
docker compose -f app/compose.yaml -f app/compose.ch11.yaml --profile chapter11 stop ch11-frontend ch11-backend
bash course/exercises/chapter-11-agent-loop/solutions/reset_lab.sh
cd app/frontend
npm run build
cd ../..
docker compose -f app/compose.yaml -f app/compose.ch11.yaml --profile chapter11 up -d --no-deps ch11-backend ch11-frontend
```

First start the ordinary local dependencies if they are not running, using the normal repository setup guide. `--no-deps` prevents the lab launch from recreating those shared services. Both reader and writer connection strings must point to `ch11_loop_lab`, with `CH11_LOOP_LAB=true`. The backend hides/rejects experimental modes otherwise; local/cloud normal defaults remain unchanged. Reset refuses while the lab services run. `market_eval` is the read-only baseline source.

Open http://localhost:5181. Follow the exercise's three modes and exact question. Each mode starts a fresh conversation. A run's metrics include the active mode, max turns, model request count, actual model-requested tool invocations, attempted-tool results, injected-error marker and trace ID. `tool_calls` is the legacy evidence-save counter; it can differ from actual invocations.

## Scripted solution checks

```bash
python3 -m unittest discover -s course/exercises/chapter-11-agent-loop/solutions -p test_loop.py
LOOP_IMPLEMENTATION=starter python3 -m unittest discover -s course/exercises/chapter-11-agent-loop/solutions -p test_loop.py
```

The first command tests `solutions/minimal_loop.py`. The second intentionally fails until the learner implements `starter.py`. Checks cover model/tool pairing, multiple tools in one turn, invalid/unknown requests without execution, error repair and stopping before another model call. Five deterministic tests do not require API credit.

## Run the live loop

```bash
docker compose -f app/compose.yaml -f app/compose.ch11.yaml --profile chapter11 exec -T ch11-backend python /exercise/solutions/live_adapters.py --implementation minimal_loop --output /tmp/ch11-minimal-loop.json
docker compose -f app/compose.yaml -f app/compose.ch11.yaml --profile chapter11 cp ch11-backend:/tmp/ch11-minimal-loop.json /tmp/ch11-minimal-loop.json
```

Replace `minimal_loop` with `starter` to test your implementation. The adapter uses the OpenAI client through `support-model`, native `mcp.ClientSession` over stdio, and the supplied marketplace tools. It does not import the Agents SDK runner. The live question is policy plus business/event evidence for order-2. The minimal loop has its own transcript; do not imply it produces the SDK's Langfuse span tree. Compare its JSON model/tool events with the SDK trace.

The example solution returns a final response only when tool calls are absent, appends paired result IDs, validates names/JSON, and gives an incomplete result on the limit. It deliberately lets operational adapter failures propagate rather than disguising outages as empty results. In a production implementation, add explicit schemas, time/cost budgets, cancellation, observability, persistent sessions and failure handling.

## Expected results and cleanup

See [VALIDATION.md](VALIDATION.md), [demo-results.json](demo-results.json) and [minimal-loop-live.json](minimal-loop-live.json). Exact live counts/wording may change. The stopping test must report one completed model invocation and `MaxTurnsExceeded`; recovery must show the one injected error and a later successful read. Normal/recovery answers should be checked against retained evidence.

```bash
docker compose -f app/compose.yaml -f app/compose.ch11.yaml --profile chapter11 stop ch11-frontend ch11-backend
bash course/exercises/chapter-11-agent-loop/solutions/reset_lab.sh
```

Saved JSON files are outside the reset database. Restart the two lab services when ready to rehearse. The fixed baseline and main marketplace stay unchanged.
