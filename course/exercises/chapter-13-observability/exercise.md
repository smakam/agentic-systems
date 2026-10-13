# Chapter 13 — Investigate a repeatable observability batch

Use your local Langfuse. The supplied fixture contains fictional traces with fixed symptoms, timings, usage and dollar values. No model calls, marketplace purchases or database edits are required. These costs demonstrate analytics; they are not provider charges or performance measurements.

## Exercise environment

| Item | Use for this exercise |
|---|---|
| UI | Local Langfuse at `http://localhost:3000` |
| Telemetry store | The local Langfuse project selected by your API keys |
| Input data | The supplied six-case fictional trace fixture |
| Marketplace UI / business database | Not used; leave marketplace and evaluation data unchanged |

The instructor dashboard uses a saved synthetic cohort, followed by an optional contrast with a recorded Agent Loop recovery trace. Your exercise creates its own batch, trace and session identifiers; do not depend on the instructor's references. Instrumentation and real model/tool calls are illustrated by the recorded run, while the fictional batch provides repeatable monitoring values.

## Prepare and verify

Start the existing local Langfuse services using the application setup guide. Obtain this project's public and secret API keys from Settings. In your terminal set `LANGFUSE_BASE_URL=http://localhost:3000`, `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY`. Keep credentials out of submitted files.

From the code repository root:

```sh
python3 course/exercises/chapter-13-observability/upload_traces.py --output /tmp/ch13-manifest.json
python3 course/exercises/chapter-13-observability/verify_upload.py /tmp/ch13-manifest.json --output /tmp/ch13-verification.json
```

The script refuses to overwrite an existing manifest. On a new run choose a new filename and use its new batch ID. After an upload timeout, keep the prepared manifest and check its trace IDs before deciding what to do; do not blindly resend. Readback can briefly lag ingestion: retry verification, not upload, if observations are still missing.

## Investigate

1. In Tracing, set a time range including the upload, and filter metadata `batch_id` to the exact manifest value. Confirm there are six root traces. Alternatively open the six manifest trace IDs directly.
2. Find the slowest trace. Use Tree or Timeline to identify the step responsible and quantify its share of total latency.
3. Find the recovered-error and failed-run examples. Explain why an error on a tool does not necessarily mean the final run failed. Use root `run_status` metadata for final status.
4. Open the shared follow-up session. Compare its two traces' token usage, latency and supplied costs.
5. In Dashboards, create a named dashboard for your batch. Add volume, latency and token/cost widgets using the same batch filter and time range. Use root observations for run volume and duration; use generation observations for tokens/cost. Include an unsuccessful-run count using root `run_status=failed`. If the installed widget editor does not support that exact metadata predicate, use the filtered tracing view as the documented failure count instead of counting every error observation as a failed run.
6. Compare findings with the separate solution only after completing your investigation.

## Submit

Submit the manifest batch ID, dashboard ID/link and filters, supporting trace IDs, and a short findings table. Include total run count, failed-run count, slowest step, and follow-up comparison. Clearly label synthetic costs. Do not submit API keys.

## Cleanup

Keep your manifest for review. Filter the exact batch before deleting any teaching traces in the UI; never delete the whole project or unrelated traces. Stop local services using the normal setup instructions when finished. Deletion is optional and is not performed by the upload script.
