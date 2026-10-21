# Validation — 10 October 2026

Local Langfuse v4.46.0 OSS, project marketplace-support. The supplied upload script ingested six synthetic roots and 25 observations; API readback verified every case, duration, token count and supplied dollar total. The stored manifest and readback are in validated-manifest.json and upload-readback.json. No model requests or business mutations were used.

Batch: `ch13-58634577764b`. Dashboard: `cmv2ohrtp0005p907lx49at4d`.

Live UI verified: dashboard has six traces, 8.84K tokens, rounded $0.01 supplied cost; filter persisted after navigation/reload. Slow trace shows 6.20 seconds and SQL 5.00 seconds. Recovery shows one error followed by a successful retry; failed trace shows ERROR on its root. Shared session displays both questions and $0.00472 total. Stored API readback supplies precise cost $0.00983 rather than the dashboard's rounded display.

## Reproduce the dashboard

Open Dashboards → create dashboard → name it. Add Widget → Home Cards: select “Total traces with the top trace names”, “Cost and token usage per model”, and “p50–p99 latencies per observation type and name”. Apply metadata batch_id equal to the manifest batch; save filters, choose a time range containing upload, and reload to verify.

For final failures inspect the root's run_status=failed metadata using Tracing or the direct failed trace ID. Do not count a recovered tool error as a failed run. The built-in Agent Dashboard's “Total Tool Calls” uses structured generation call data; this fixture provides tool observations and does not populate that separate field. Use tool-observation counts or the trace tree (seven attempts), not that widget's zero. Latency percentiles aggregate observations; the SQL p95 is 4.76 seconds in this tiny fixture, whereas the individual slow SQL step is 5.00 seconds. This is a teaching cohort, not production evidence.

## Instructor links

- Dashboard: http://localhost:3000/project/marketplace-support/dashboards/cmv2ohrtp0005p907lx49at4d
- Slow tool: http://localhost:3000/project/marketplace-support/traces/3aa05eb93d9b48d4aca9500c169a11bd
- Recovered error: http://localhost:3000/project/marketplace-support/traces/fce7498a66e341ea9f4101822fa856e6
- Failed run: http://localhost:3000/project/marketplace-support/traces/b63894e9aeb74282a38b2c02d2463a3d
- Follow-up session: http://localhost:3000/project/marketplace-support/sessions/ch13-58634577764b-followup

Learner installations generate their own IDs. Dashboard setup was performed in the UI; it is not created automatically by upload. Alerts and platform comparisons are described from official documentation; no alert delivery or external-platform benchmark is claimed.
