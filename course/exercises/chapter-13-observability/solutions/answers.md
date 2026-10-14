# Chapter 13 — Reference findings and dashboard recipe

This solution follows the exercise: inspect six recorded investigations, review cost/latency/feedback, and build matching count and latency charts in local Langfuse. It requires no synthetic upload, database mutation or new model call.

## Part 1 — Six recorded traces

The instructor project is `marketplace-support` at `http://localhost:3000`. Instructor references will not automatically exist in a learner's local project; use corresponding earlier-lab recordings, or the saved source records below, and report unavailable examples explicitly.

| Scenario | Trace ID | Recorded duration | Model calls | Tokens | Finding |
|---|---|---:|---:|---:|---|
| Normal payout investigation | `ff9cfc4226ca599acefdd696843d1ae1` | 17.63 s | 4 | 39,515 | Catalog, business query and policy support the cited payout answer |
| Recovery | `b7d2f229e68a46e53428c689e5c9518c` | 21.26 s | 5 | 52,008 | Four tool attempts include a controlled failed read and a successful retry; final run completes |
| Turn limit | `4a0c39e87ecb4b137f5bbd902655c9b6` | 2.99 s | 1 | 2,081 | Catalog executes, then Runner refuses a second model invocation; application returns incomplete status |
| Initial shipment status | `0e1638805b5bf0af2ed7b5d719d51d32` | 9.70 s | 3 | 25,612 | Shipment pending; two units in order ord-500d17bb22 |
| Quantity follow-up | `81a6601ef96763ce592a9414e00731cd` | 2.03 s | 1 | 12,214 | Same conversation, two units from history, no new tool call |
| Fresh status after dispatch | `cd16ec570ade71d09c563112ff8c5682` | 7.29 s | 3 | 56,394 | Fresh business lookup reflects dispatched status after the earlier practice change |

The last three recordings belong to `chat-ch10-follow-ec25467cea`; inspect conversation metadata, not an assumed native Langfuse Session. The separate history-window example is excluded because its earlier eight-question conversation is not part of this walkthrough.

Saved source records: [Agent Loop results](../../chapter-11-agent-loop/solutions/demo-results.json) and [Session State results](../../chapter-10-session-state/solutions/demo-results-2026-10-10.json). The current reference inventory is [recorded-investigations.json](recorded-investigations.json). The timings above are whole root durations; the app's elapsed values can differ slightly. A single normal/recovery pair is a teaching comparison, not a production benchmark.

## Part 2 — Monitoring interpretation

**Cost:** historical generations report aliases without matched pricing or supplied cost. Missing cost must remain unavailable. Future backend chat-completion calls attach LiteLLM's reported pricing estimate before export to the existing SDK generation. This does not add another generation or duplicate usage. The one authorized live verification recorded one generation, 31 tokens and $0.000165. Older observations are immutable in Langfuse v4: re-sending them can duplicate records and inflate metrics. No historical observations were rewritten.

**Latency:** enclosing spans overlap. In the normal recording, four generations total 16.637 s, tools total 0.958 s and the root is 17.628 s. Model calls account for most of this sequential run. The workflow/agent durations include that work and must not be added again. Per-call percentiles across a cohort cannot be subtracted from whole-run percentiles to obtain overhead. The Home latency panels may show several observation types despite their titles; check type and name.

**Scores:** `user_feedback` represents recorded thumbs up (1) or down (0). Its count is rated answers, not all questions; an average is calculated over available ratings. It is human feedback, not a correctness guarantee. Missing ratings are not zero. Other score names can have different meanings.

Home's total root count mixes SDK question runs, hosted-agent request boundaries and separately marked MCP application roots. `marketplace-hosted-answer` records our backend request/response boundary to Google/Lyzr, not all their internal model execution. For SDK question volume, select roots named `support-investigation`.

## Part 3 — Dashboard recipe and reference

Saved instructor dashboard: **Chapter 13 — Recorded investigation trends** (`cmv6ctgsl000dp907f3gqw0t5`). It contains two widgets, verified in local v4.46.0:

| Setting | Run count | Latency |
|---|---|---|
| View | Observations | Observations |
| Metric / aggregation | Count / Count | Latency / p99 |
| Chart | Bar time series | Line time series |
| Name filter | support-investigation | support-investigation |
| Root filter | Is Root Observation = true | Is Root Observation = true |
| Environment | default | default |
| Period / buckets | Same selected range / daily | Same selected range / daily |

The installed line widget displays one metric series; p99 was selected explicitly. Use a separate widget if you also want p50. No-run days have no latency point. A rolling seven-day range may cover eight calendar labels due to partial boundary days. Keep the bucket interval and timezone aligned before comparing days.

At the readback, October 7 had 51 support runs and p99 approximately 33.56 s. This identifies a period to inspect; it does not prove that volume caused latency. Open Tracing, filter the date/name/root/environment, sort by latency and inspect the actual model/tool operations. Clicking a chart point shows a tooltip, not automatic trace navigation. Counts change as more runs are added, so do not require learners to reproduce the instructor's exact totals.

## Evidence boundaries

No synthetic fixtures are used in the main demo or required exercise. Learners use their existing local recordings. No live alerts, platform comparison benchmarks or production-performance claims are made. Evaluation still checks answer quality; monitoring finds patterns and traces help explain individual executions.

References: [Langfuse custom dashboards](https://langfuse.com/docs/metrics/features/custom-dashboards), [token and cost tracking](https://langfuse.com/docs/observability/features/token-and-cost-tracking), [immutable observations and supported annotations](https://langfuse.com/faq/all/tracing-data-updates).
