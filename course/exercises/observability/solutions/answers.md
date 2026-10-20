# Chapter 13 — Token dashboard reference solution

The exercise builds one dashboard and explains a day with high **average tokens per investigation** using recorded execution evidence. Daily values depend on each learner's recordings; no fixed token total or model ranking is required.

## Dashboard configuration

Create two time-series widgets in the same dashboard, using the same date range, timezone and cohort. In the instructor installation, local SDK calls use **Observation Name = generation**, **Environment = default**. Confirm the corresponding original traces are Support investigations; exclude unrelated agents, imported experiments and synthetic fixtures.

| Widget | View | Metric | Aggregation |
|---|---|---|---|
| Daily model tokens | Observations | Total Tokens | Sum |
| Daily investigations with model calls | Observations | Trace Id | Uniq |

The denominator is distinct investigation traces represented by those same generations. Count on Trace Id counts model observations; **Uniq** counts investigations. Average on Total Tokens is per generation, not per investigation. Root spans, workflow wrappers and gateway audits must not be added to generation usage.

The installed builder exposes one metric per custom widget. Use the two widgets as numerator and denominator and calculate the ratio in the submission table:

**Average tokens per investigation = total tokens for the day ÷ distinct investigations with recorded model calls that day.**

For illustration only, 120,000 tokens across 20 investigations gives 6,000 tokens per investigation. Another day with 180,000 tokens across 60 investigations gives 3,000. The second day consumes more in total, while the first uses more per investigation. These numbers are arithmetic examples, not recorded measurements.

Use complete days with nonzero counts. A zero-count day has no defined average. Investigations without recorded generations are outside this cohort. Generations are bucketed by their own timestamps: inspect cross-midnight runs separately or choose within-day runs for the simple comparison. Missing telemetry is not evidence of zero usage.

## Trace investigation

1. Note a high-average day's total tokens and distinct investigation count.
2. Open Tracing with that day and environment, select root `support-investigation` runs, and inspect high-token original executions. A trace must belong to the dashboard's generation cohort.
3. Read the question and final answer before inspecting the tree.
4. Sum usage from the actual model generations only. Compare input tokens, output tokens, number of rounds, conversation history and tool-result sizes with another run.
5. Tie the finding to observed evidence. For example: “This investigation contains more sequential model calls, each carrying the accumulated history; the database calls themselves are brief.” State the actual counts/values from the chosen traces before making that claim.
6. Consider question mix, model and settings. A single expensive question is not proof of a system regression. Propose a bounded check and say what evidence would confirm an improvement.

## What a good submission establishes

The dashboard selects a coherent population; numerator and denominator match; the calculation distinguishes request volume from work per investigation; and the trace explanation cites the question, usage and execution evidence. Tokens are not currency. A cost comparison additionally needs the model's applicable input/output pricing and available cost reporting.

## Connection to the instructor demonstrations

- **Monitoring → tracing:** daily run count and P99 investigation latency identify a period to inspect. The October 18 historical example has 35 investigations and P99 about 33.74 s. Its inspected 35.37-second run spends about 35.20 s across eight model generations; tool calls are brief. This supports investigating sequential model rounds, not claiming the database is slow.
- **Evaluation → tracing:** the Cedar clarification case has human and provisional judge correctness 2 for GPT-5.4 and 0 for Nano. Both first clarify seller versus product. The follow-up “I mean the seller” is available in the original generation input alongside the initial question. Nano's query adds an unrequested September 27–28 date window and returns no rows; GPT-5.4 returns the seller's September 24 order. A successful tool call can still answer the wrong scope. This is a dated case, not proof of general model accuracy.
- **Dashboard construction:** the instructor creates a daily **Total Cost / Sum** chart over recorded generations. Earlier runs predate cost reporting; do not interpret their missing cost as free generation. The learning goal is selecting a metric, aggregation, filters and visualization, then saving the widget.

The old six-scenario walkthrough and synthetic loader are not required exercise steps. No deployment, paid model request or business-data mutation is needed.
