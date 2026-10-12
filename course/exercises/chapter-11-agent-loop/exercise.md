# Chapter 11 — The Agent Loop

## Goal and starting point

Understand how the runtime alternates model calls and tool execution. Repeat the three UI demos, then implement the orchestration yourself without the Agents SDK runner. Use the supplied OpenAI client and native MCP adapters; the marketplace server continues to enforce read-only SQL.

Prerequisites: repository checkout, local Docker stack, indexed documents in the Agent Loop lab, working `support-model` and `embedding` gateway aliases with provider credit. Use the dedicated `ch11_loop_lab` database; leave fixed `market_eval` unchanged. Course Setup already starts this dedicated lab UI; no extra startup or database reset is required for the three read-only demos. Allow about 20 minutes for the UI tasks and 60–90 minutes for the developer extension. Scripted checks cost nothing; live runs consume model and embedding tokens. Gateway estimates are not invoices.

## Core — repeat and explain the three demos

Open http://localhost:5181, sign in as operator, open Support workspace, select the SDK runtime, disable long-term memory, keep guardrail Off and source authority on. Use a fresh conversation for each mode; changing the mode does this automatically.

Use exactly this question:

> For order-2, query its current shipment and payout status using query_business_data, then retrieve settlement policy with search_documents and explain why payout is held. Include evidence citations.

1. **Normal execution:** follow the code and trace from model request to tools to final answer. Read the model-call and tool-invocation counters beneath the answer and compare them with the trace. Identify catalog, business records and policy passage. Verify pending shipment and held payout against returned records, not prose alone.
2. **Tool-error recovery:** find the first `query_business_data` attempt returning `LAB_TEMPORARY_READ_FAILURE`. It is simulated before SQL execution. Verify a later real read succeeds and supports the final answer. An error must never become “no matching records.”
3. **Turn-limit stop:** verify one model invocation, `MaxTurnsExceeded`, retained evidence and an explicit incomplete result. Select Normal afterward to restore the mode. The ordinary eight-turn setting was not globally modified.

Keep a table locally with mode, run ID, trace ID, actual model/tool counts, evidence and stopping reason. Counts can vary between live runs; verify the behavior, rather than requiring the saved exact count.

## Developer extension — implement a minimal loop

Complete `starter.py` using its existing `run_loop` signature. Do not call `agents.Runner` or delegate orchestration to an agent framework.

1. Build the message list from instructions and question.
2. Call the supplied model adapter; count that invocation as one turn.
3. If the response includes tool calls, retain the assistant message, validate the allowed name and JSON-object arguments, execute each permitted call, and append each result with its original `tool_call_id`.
4. Pass those messages to the next model call. Return an answer only when no tool calls remain. Text alongside tool calls is not the final result.
5. Keep errors as structured errors so the model can repair a request. Stop after `max_turns` without another model invocation; report incomplete instead of inventing a business answer.
6. Record model responses, tool requests and results in a transcript. Do not print credentials.

The UI continues to use its SDK loop. Your implementation runs only in the separate developer command; it does not replace or stop the SDK path. Run the five scripted checks with `LOOP_IMPLEMENTATION=starter`; then use `live_adapters.py --implementation starter`. Compare one live marketplace investigation with the SDK trace. Tool order and answer wording need not be identical. Explain which responsibilities you implemented and which remain in the adapters/server/SDK.

Expected outputs: completed `starter.py`, five passing scripted checks, one live transcript with cited evidence, and a short SDK comparison. This small loop has no handoffs, streaming, durable sessions or full production guardrails. You are learning orchestration, not recreating all SDK features.

## Cleanup

Select Normal after the comparison. Use a fresh conversation for each read-only repetition; no database reset is required. Stop all local workspaces through the normal Course Setup instructions when finished. Do not run Compose `down --volumes`, reset the fixed source or modify the main marketplace. Keep your transcripts outside the disposable database.

Try first; the worked implementation and measured results are in `solutions/`.
