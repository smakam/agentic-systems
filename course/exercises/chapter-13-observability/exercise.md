# Chapter 13 — Inspect recorded traces and build a monitoring dashboard

Review six complete recorded investigations, inspect cost, latency and feedback, then create two monitoring charts. Use the same workflow as the instructor demo. No synthetic upload, new deployment, database reset or code change is required.

## Exercise environment

| Item | Use for this exercise |
|---|---|
| Observability UI | Local Langfuse at `http://localhost:3000` |
| Telemetry store | Your configured local Langfuse project; the instructor project is `marketplace-support` |
| Trace input | The six recorded scenarios listed below, or corresponding recordings from your earlier labs |
| Marketplace UI | Agent Loop lab at `http://localhost:5181` if you need to locate your existing question runs |
| Business database | Existing disposable practice/lab database associated with the earlier run; inspection does not modify it |

Instructor IDs identify recordings in the instructor's project, not records automatically present in every learner's project. Use your corresponding Chapter 11 and Chapter 10 recordings when available. The separate solution includes the instructor's reference inventory and saved evidence sources. If a scenario is absent, state that gap rather than substitute an unrelated trace. You can still build the dashboard from your available recorded support investigations; one day of traffic is a valid small sample.

## Part 1 — Review the six recorded scenarios

| Scenario | Instructor trace ID | What to explain |
|---|---|---|
| Normal payout investigation | `ff9cfc4226ca599acefdd696843d1ae1` | Question → catalog → business data → settlement policy → cited answer |
| Read failure and recovery | `b7d2f229e68a46e53428c689e5c9518c` | Controlled failed read → model-requested retry → successful evidence → answer |
| Turn-limit stop | `4a0c39e87ecb4b137f5bbd902655c9b6` | One generation and catalog call, then stop before a second generation |
| Initial shipment status | `0e1638805b5bf0af2ed7b5d719d51d32` | Fresh evidence establishes pending status |
| Quantity follow-up | `81a6601ef96763ce592a9414e00731cd` | Same conversation; history supplies two units without a new tool call |
| Fresh status after dispatch | `cd16ec570ade71d09c563112ff8c5682` | Changed order state → fresh business query → dispatched answer |

In **Tracing**, select a date range containing the recording, search its trace ID, and open the matching table row. Most recorded roots have the generic name `support-investigation`, so scenario labels alone do not uniquely select a run. For each trace, inspect the question and answer, then model outputs/tool requests, tool arguments/results, evidence citations, timings and final status. Keep the last three traces together as one conversation. The recovery failure and one-turn cap were deliberate lab conditions; the subsequent model/tool behavior was actually recorded.

Record model invocations and tool attempts separately. A recovered tool error does not make the final investigation unsuccessful. The turn-limit response comes from the application; the blocked second model call does not occur. Enclosing workflow, agent and turn spans overlap with their children: do not add all span durations together.

## Part 2 — Inspect monitoring

1. Open **Home**, choose a range containing your recordings, and select only the recorded environment (`default` in the instructor setup). Exclude `ch13-synthetic`.
2. **Cost and tokens:** inspect Model costs and Model Usage. Identify the model aliases, token totals and any available costs. New SDK calls forward LiteLLM's per-call pricing estimate to their existing generation observation. Older observations may have no cost; a displayed zero is not proof that those calls were free. Report cost coverage and its pricing basis; these values are not invoices. Do not alter old observations or repeat uploads to fill missing costs.
3. **Latency:** compare whole-investigation percentiles with individual model/tool latency. In the observation table, `generation` is the model call; `turn` is a chain wrapper; `Marketplace support` and `Agent workflow` enclose larger execution. A panel title is not a substitute for checking observation type and name. Use a trace to verify any proposed time breakdown.
4. **Scores:** find `user_feedback`, where recorded thumbs-up/down responses are represented as 1/0. Note the number of rated answers and average. Missing feedback is not a negative rating. Other score names may represent different assessments; scores do not automatically prove correctness. Open a rated run to inspect its question, answer and evidence.

The total Home trace count includes multiple application boundaries and tool-service roots. Use `support-investigation` roots for SDK question-run volume, rather than treating every listed root as a user question. The gateway audit span is not another paid model generation.

## Part 3 — Create your dashboard

1. Select **Dashboards → New dashboard** and give it a clear name.
2. Add a **run count** time-series widget: view **Observations**, metric **Count**, aggregation **Count**, chart **Bar time series**.
3. Apply filters to that widget: **Name = support-investigation**, **Is Root Observation = true**, **Environment = default**. If the editor exposes Type, also restrict to the span root used by your SDK path. Use the actual environment/name of your deployment if different.
4. Add a **latency** time-series widget: view **Observations**, metric **Latency**, aggregation **99th percentile**, chart **Line time series**. Use exactly the same filters as the count widget.
5. Select the same seven-day range for both charts. On the instructor's v4.46.0 installation these charts use daily buckets. Check the displayed bucket interval/timezone in your version. A rolling seven-day range can include partial first and last days; use complete calendar-day boundaries for a strict day-by-day comparison.
6. Compare daily run count with daily p99 latency. State the sample size; one run makes its percentile that run's duration. A no-run day has no latency value, not zero latency. A relationship in these charts does not establish that volume caused the delay: question mix, model, tools, retries and configuration can change too.
7. Hover or click a point to read its date and value. In the installed version this does not navigate to a trace. Go to **Tracing**, select that day's range, apply the same root/name/environment filters, sort latency descending and inspect one or more slow investigations.

No script or API key is needed for this UI exercise. The instructor's two widgets are saved in **Chapter 13 — Recorded investigation trends**; create your own rather than change the shared demonstration.

## Submit and cleanup

Submit your dashboard name/link, time range, filters, bucket interval, supporting trace IDs and a short findings table covering the six scenarios, cost availability, latency and feedback. Include a count-versus-latency observation and the trace evidence used to investigate it. State any missing scenarios or telemetry.

Keep the dashboard and recordings for review. No business-data or code restoration is needed because this exercise only inspects telemetry and creates a dashboard. Remove only your own dashboard if desired; preserve the shared project, instructor dashboard and existing traces. The previous synthetic fixture scripts remain historical authoring material, not required learner steps.
