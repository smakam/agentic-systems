# Chapter 11 validation — October 10, 2026

Preparation and reference validation complete; owner's slide review and full rehearsal remain.

## Environment

Normal recharged OpenAI route through `support-model`, configured GPT-5.4 dated model; existing local gateway and Langfuse. SDK demos ran through the actual UI at localhost:5181 with the disposable `ch11_loop_lab` database. Long-term memory off, guardrail Off, source authority on. Model-requested business tools used stdio MCP. Cloud SQL was not started.

All cases started in fresh conversations over the same fixed business snapshot. No marketplace commands or policy edits were made. Public business/document tables in `ch11_loop_lab` and `market_eval` had identical SHA-256 fingerprints after the runs:

`8abb40ef4ae5337848e2784935d14f1f28682dee1328ef685fe00b4255044db0`

See `business-fingerprint.json`. Conversation/run/authentication rows are intentionally outside that business-data comparison.

## Three UI demos

| Mode | Run | Model calls | Tool invocations | Verified result |
|---|---|---:|---:|---|
| Normal | run-98efffd4ac | 4 | 3 | Completed: catalog → SQL → applicable policy → cited answer |
| Recovery | run-e0520a2b8e | 5 | 4 | One simulated SQL read error before execution, followed by successful real SQL and policy retrieval |
| Turn-limit stop | run-a89015716b | 1 | 1 | Catalog returned, then MaxTurnsExceeded before a second model call; clear incomplete result |

The completed answers match returned order-2 records: shipment pending, no delivered timestamp, payout held for 161,820 paise / ₹1,618.20. Policy requires delivery confirmation and a 24-hour hold after delivery. Citation handles were checked against the evidence actually returned. Exact wording and counts can vary on rerun; these are measured observations, not guaranteed fixed model behavior.

Recovery demonstrates retry after a deliberately simulated temporary read failure. It does not demonstrate repairing malformed SQL or recovering from every kind of outage. The wrapper returns `LAB_TEMPORARY_READ_FAILURE` once per investigation and executes no SQL for that failed attempt. The next permitted call uses the real MCP server.

An initial recovery run completed, but the hook labeled an MCP text-wrapped error as completed. The hook was corrected and the recovery demo rerun; the final JSON now records that attempt as `error`. `initial-recovery-before-metric-fix.json` preserves the earlier diagnostic run; it is superseded for metric verification. The UI labels legacy `tool_calls` as evidence saves in this lab, separately from actual model-requested invocations.

The UI selector starts a new conversation when mode changes. Selecting Normal was verified after the experiments. Non-normal modes are rejected unless both database connections target the explicitly enabled Chapter 11 lab and the runtime is SDK. Backend checks cover fail-closed behavior, one-shot failure before execution and wrapped-error classification.

## Trace inspection

`trace-checks.json` records observation IDs/names/types read from local Langfuse v4 through `/api/public/v2/observations`. Generation/tool observation counts match application hook counts for all three final cases. The older trace/observation API returned 404 because this deployment uses v4 events mode; this was an API compatibility issue, not evidence that traces were absent. See the [official public API documentation](https://langfuse.com/docs/api-and-data-platform/features/public-api).

## Developer exercise

Five scripted checks passed: paired results return to the next model input; two requested tools still belong to one model turn; unknown/malformed requests never execute; the turn limit prevents another invocation; an invalid request can be repaired.

The reference loop's live run used the OpenAI client and native MCP client, without Agents SDK Runner. It completed in five model invocations and four tool invocations, obtaining order history, policy, catalog and SQL evidence. Its answer cited valid returned handles and explained the pending shipment / held payout with the applicable policy. See `minimal-loop-live.json`. The exact documented mounted-container command was subsequently rerun successfully (also five model calls/four tools); `documented-command-live.json` records that check. It is a separate prompt/teaching loop; this is not a fair quality or performance benchmark against the application SDK prompt.

The reference implementation lacks full SDK feature parity. Its saved transcript, not an SDK trace tree, is the expected developer output. The unimplemented starter intentionally requires learner work.

## Checks and readiness

- Five deterministic exercise tests, three backend lab tests and fifteen existing frontend tests passed.
- Frontend production build passed; all three modes exercised through real UI controls.
- Deck updated to nine editable slides with the loop diagram and SDK implementation slide; package/layout/font/import validation and visual inspection completed.
- Separate speaker notes include slide guidance, exact demo process and exercise guidance; course plan indexes the agreed demos/exercises.
- Exported run/transcript evidence is outside the disposable database. Lab services are stopped and the disposable copy reset after validation; the owner can restart them with the README instructions.

Your four review steps remain: inspect slides, rehearse demos, execute learner exercises and check speaker-note alignment. No external reviewer Word outline was changed.
