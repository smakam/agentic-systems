# Historical tracing and monitoring plan

Superseded October 10, 2026. Original chapter numbers retained here for source provenance.

### 13. Tracing, with the failure clinic as the example

**Draft learner practice — for review, not finalized:**

- **Exercise:** Diagnose a supplied incorrect payout answer from its saved trace; check the expected answer, retrieved facts and exact model input.
- **Solution to prepare:** Worked diagnosis separating facts, model input and answer error, with evidence-backed conclusions and remaining uncertainty.
- **Learning objective:** Diagnose a wrong answer using captured evidence.
- **Lab and result:** Capture and replay a request with a diagnostic script; compare correct/incorrect inputs and document what the evidence does not establish.
- **Covers:** Langfuse traces of model calls, tool calls, the exact model inputs and cost per step.
- **Worked example:** payout eligibility failures (M03, M09–M13). GPT-5.4 treated 23 hours as past the 24-hour hold and exactly 24 hours as not past it. The investigation:
  1. Check whether the gold answer is wrong (it isn't).
  2. Check whether the evidence reached the model (traces show it did).
  3. Rerun unchanged (3 of 4 runs correct).
  4. Test a timestamp-ambiguity hypothesis by widening the gap to 24h30m (failures remain, so boundary ambiguity is not a sufficient explanation).
  5. Compare right and wrong runs side by side (same facts).
  6. Replay the identical request (wrong, correct, wrong).
  7. Swap in GPT-5 (6 of 6 correct).
- **Lesson:** check the gold answer, then the evidence, then the model input, then variance, and only then blame the model.
- **Status:** diagnosed and documented.
- **Sources:**
  - [Diagnosis](../app/results/diagnosis-2026-09-29/DIAGNOSIS.md)
  - [Input comparison](../app/results/payout-input-comparison-2026-09-29/FINDINGS.md)

#### Progress and evidence — October 1, 2026

- **Current state:** Failure diagnosis measured and documented.
- **What we learned / have available:** Trace the first wrong decision: missing retrieval, lost transport, misread evidence, arithmetic, scope or citation. Same evidence can produce different answers; SDK input capture is not proof of exact provider HTTP payload.
- **Tests and references:** [Original diagnosis](../app/results/diagnosis-2026-09-29/DIAGNOSIS.md); [input comparison](../app/results/payout-input-comparison-2026-09-29/FINDINGS.md); [catalog-v2 diagnosis](../app/results/catalog-v2-2026-10-01/DIAGNOSIS.md); [current captures/walkthrough](../app/docs/PROMPT-AND-CATALOG.md); M09–M13, M28–M30.
- **Hands-on readiness:** Captured/replayed correct and incorrect payout responses exist. Package one guided investigation from answer → evidence → input → repeated sample, preserving wrong answers.
- **Pending:** Select a compact example and checkpoints; document capture boundaries and do not expose credentials. Provider-wire capture is a separate optional diagnostic.

### 14. Monitoring

**Draft learner practice — for review, not finalized:**

- **Exercise:** Run a small batch of fixed questions and identify expensive, slow or failed runs using Langfuse and LiteLLM.
- **Solution to prepare:** Annotated telemetry views, calculations from the same batch and an explanation of what the metrics establish.
- **Learning objective:** Use AI telemetry to spot regressions.
- **Lab and result:** Add a cost/latency/error view and generate controlled traffic or a simulated error to verify the displayed change.
- **Covers:**
  - cost per question by model
  - latency spread
  - tool and model error rates
  - usage per virtual key
  - simple thresholds for spotting AI cost, latency and error regressions; no general on-call/operations curriculum
- **Status:** Existing telemetry available. Owner deferred monitoring demo organization to chapter preparation on October 8; no new dashboard is required upfront. The Monitoring chapter covers only Langfuse/LiteLLM; native Google/Lyzr monitoring is covered in the respective platform chapters.

#### Progress and evidence — October 1, 2026

- **Current state:** Telemetry exists; teaching dashboard pending.
- **What we learned / have available:** Langfuse traces and LiteLLM virtual-key usage provide different views. Locally estimated costs, provider billing, cached tokens and model latency must be labeled distinctly.
- **Tests and references:** [Telemetry/services guide](../app/README.md); [cost/cache report](../app/results/routing-granularity-2026-09-30/REPORT.md); [current estimated costs](../app/results/core18-history-v3-2026-10-01/REPORT.md); M05–M06, M18.
- **Hands-on readiness:** Existing usage/cost/latency data can be inspected. The small regression dashboard and controlled traffic/error exercise are not yet packaged.
- **Pending:** During chapter preparation, organize cost/latency/error demonstrations from existing dashboards. Keep this chapter limited to Langfuse/LiteLLM. Cover Google/Lyzr native monitoring only in their respective platform chapters; label available metrics and their limits. Add a small comparison view only if essential information is missing. This does not block overall experiment completion.

