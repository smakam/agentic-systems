# Chapter 13 — Build a token-usage dashboard and investigate a high-average day

## Prerequisites

Complete the common course setup and earlier agent activities. Open [local Langfuse](http://localhost:3000/) and your configured telemetry project (`marketplace-support` in the instructor setup). Use existing recorded SDK support investigations; no new deployment, synthetic upload, paid model call or database reset is needed.

## Learning goal

Build one dashboard, compare **average tokens per investigation** across days, then use original traces to explain a high-average day. Higher daily token totals can simply mean more requests; normalize by investigation count before comparing work per question.

## Part 1 — Build one dashboard

1. Open **Dashboards → New dashboard**. Name it **Support investigation token usage — your name**.
2. Choose a recent range containing your recorded calls. Use the same time range, timezone and daily buckets for both widgets below. Compare complete days, not a partial first or current day.
3. Click **Add Widget → Custom Chart**. Create the first widget:

   | Setting | Value |
   |---|---|
   | View | Observations |
   | Metric | Total Tokens |
   | Aggregation | Sum |
   | Filter | Observation Name = `generation` |
   | Filter | Environment = `default` in the instructor setup |
   | Breakdown | None |
   | Chart | Line Chart or Bar Chart, time series |
   | Name | Daily model tokens |

4. Check the preview contains the intended SDK support model calls, then save. Exclude imported evaluation wrappers, synthetic fixtures, gateway audits and enclosing workflow/turn spans. If your project uses a different observation name/environment, select the corresponding cohort. Do not combine other agents' model calls with Support investigation counts.
5. Create a second widget using **the identical filters, time range and timezone**:

   | Setting | Value |
   |---|---|
   | View | Observations |
   | Metric | Trace Id |
   | Aggregation | Uniq |
   | Chart | Bar Chart or Line Chart, time series |
   | Name | Daily investigations with model calls |

   This counts distinct investigation traces represented by the selected generations, not the number of model calls. An investigation with five model calls counts once. Investigations that have no recorded generation are outside this token-analysis cohort.

6. Hover the same daily points in both charts and record their values. Calculate:

   **Average tokens per investigation = daily model token sum ÷ daily distinct investigation count.**

   Use at least two complete days with nonzero counts. The installed builder supports these two source widgets; compute the ratio in your findings table. **Do not select Average on generation tokens and label it per investigation**: that would calculate tokens per model call. Tokens are usage units, not monetary cost.

7. Keep the dashboard and a small findings table:

   | Day | Total tokens | Distinct investigations | Average tokens per investigation |
   |---|---:|---:|---:|
   | Your first day | | | |
   | Your second day | | | |

Daily model tokens are assigned to the date of each generation. For this simple comparison use runs completed within one day; if an investigation crosses midnight, inspect it and explain the boundary instead of treating its partial-day tokens as a complete run.

## Part 2 — Investigate a high-average day

1. Pick a day with a higher **average**, not merely a higher total. Note the investigation count; a day with one unusual run is different from a broad shift.
2. Open **Tracing** separately. Apply the matching day and environment, and select root investigations named `support-investigation`. Clear unrelated filters. Dashboard points may only show values; they are not automatic trace links.
3. Inspect token usage for the matching investigations. Use the token/usage column if available; otherwise open candidate traces and inspect their generation totals. Find a high-token run and a lower-token comparison from the same day or a comparable day.
4. Read the original question and final answer. In the trace tree inspect the generations, their input/output usage, conversation history and tool inputs/results. Confirm the selected generations belong to that support investigation.
5. Explain a supported contributor: more model/tool rounds, a longer input/history, a large tool response, or a longer model output. Report only what the recorded spans show. More tokens do not by themselves prove waste, bad quality or a model defect; different questions can require different work.
6. State one follow-up check or improvement hypothesis. Explain how you would verify it on comparable runs. You do not need to change the application or rerun models.

## Submit

- Dashboard name/link, filters, date range, timezone and bucket size.
- The daily table with token totals, distinct investigation counts and calculated averages.
- Original trace references for the high-token run and comparison, with one evidence-backed finding.
- Any missing usage, cross-midnight runs or cohort mismatch that limits the conclusion.

Keep your dashboard for review. Do not delete shared dashboards, traces, the telemetry project or business databases. No application settings need restoring.

The instructor's latency investigation, Cedar model comparison and cost-widget construction are demonstrations. This learner task applies the same monitoring-to-tracing method to token usage; it does not require the older six-trace checklist or synthetic fixture scripts.
