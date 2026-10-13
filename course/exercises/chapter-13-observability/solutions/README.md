# Reference findings

Use the local Langfuse UI and telemetry project identified in the exercise. This solution concerns the synthetic six-case batch. It does not require the marketplace UI, a business database change, or new model calls.

Run the supplied upload and verification commands. IDs change per cohort; use your generated manifest. Do not expect the instructor's IDs to exist in your project.

| Case | Duration | Tokens | Supplied cost USD | Outcome |
|---|---:|---:|---:|---|
| normal | 1.2 s | 1,040 | 0.00118 | Completed |
| slow-tool | 6.2 s | 1,040 | 0.00118 | Completed; SQL tool occupies 5 s |
| recovered-error | 2.4 s | 1,920 | 0.00219 | One failed tool attempt, then successful retry |
| failed-run | 0.9 s | 480 | 0.00056 | Root failed |
| conversation-first | 1.8 s | 1,180 | 0.00136 | Completed |
| conversation-followup | 1.5 s | 3,180 | 0.00336 | Completed; same session as first question |

Batch totals: six runs, one failed run (16.67%), 8,840 generation tokens, $0.00983 supplied cost. The slow SQL tool accounts for 5/6.2 = 80.65% of the slow run. Seven tool attempts include two errors; that tool-error fraction differs from the failed-run fraction. Mean root duration is 14/6 = 2.333 seconds. This tiny fictional cohort does not establish a production latency distribution.

The follow-up session combines 4,360 tokens and $0.00472. The second question has more input tokens but less latency in this supplied example; token count alone does not determine elapsed time.

Dashboard recipe: filter each widget to metadata batch_id from the manifest and a time range around the upload. Volume uses root count; latency uses root duration; usage/cost uses generation fields. For final failures filter root metadata run_status=failed. Drill into the manifest's slow-tool and recovered-error traces. Verify session linking using the manifest's shared followup session ID.

Supported ingestion source: https://langfuse.com/docs/api-and-data-platform/features/public-api . Dashboard guidance: https://langfuse.com/docs/metrics/features/custom-dashboards . The upload uses OTLP/HTTP JSON with the v4 ingestion header; the legacy ingestion endpoint is not used.

The installed-version dashboard recipe and verified local IDs are in [validation](../validation.md). In v4.46.0 use Home Cards, save the batch filter, and use Tracing for the final failure count. Avoid the structured-generation tool-call counter for this tool-observation fixture.

## How the findings connect monitoring and tracing

Monitoring summarizes the batch: six runs, one failed root, total usage and supplied cost. Tracing explains individual cases: the slow run is dominated by SQL time; the recovered error has a failed attempt followed by successful execution; the incomplete run has a failed root. Count model generations once for cost, and do not confuse a gateway input-audit span with a second paid model call.

The instructor can contrast the recorded Agent Loop recovery trace using the speaker readout. Its historical model/tool execution is real, but its empty monetary fields must not be filled with fictional prices. Learners' trace references come from their own manifest.

A successful run is not proof of answer correctness. Evaluation can flag an incorrect answer, after which the associated trace helps investigate retrieval, tool inputs/results or final interpretation. After a targeted change, rerun evaluation. Evaluation methodology belongs in the next chapter; this exercise teaches telemetry diagnosis.
