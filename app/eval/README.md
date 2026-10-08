# Running the 30-case comparison

## Latest routing results

The diagnostic routing phase is complete. See the [current findings and optional future work](../../SPECIFICATION.md#model-routing-diagnostic-phase--closed-september-30-2026), [classifier comparison](../../app/results/routing-classifiers-2026-09-30/comparison.html), and [live granularity report](../../app/results/routing-granularity-2026-09-30/comparison.html). The live report leads with six-conversation success, with 18-answer scores and cache breakdowns below. These experiments do not enable production routing.


The case contract is [EVALUATION-SPEC.md](../../EVALUATION-SPEC.md). `cases.json` is evaluator-only input and gold; it is not mounted into the interactive backend or indexed as RAG content.

From `app`, with Docker services running:

```sh
./scripts/compare-models.sh --output /results/fixture-validation --dry-run
./scripts/compare-models.sh --output /results/comparison-01 --budget 15
python3 scripts/render-eval-report.py results/comparison-01/results.json
```

The first command validates all 30 fixtures twice, checking deterministic resets, without model calls. The second runs one paired pass (60 scenarios, 64 answer turns), plus a Claude Opus 5.5 judge on every scenario. It uses the shared LiteLLM gateway with separate candidate and judge virtual keys, without changing the interactive model. All business writes target `market_eval`; reset guards reject interactive/test database targets and different read/write hosts. An advisory lock prevents two comparison runners from resetting the evaluation database concurrently.

The budget is an **estimated usage stopping threshold**, not a provider billing cap. The runner reserves room before a scenario and applies model-specific per-answer soft limits; a completed call can overshoot a soft limit. Estimates use uncached list rates and exclude embeddings and failed API attempts with no reported usage. A stalled/failed provider response must be checked before assuming it cost nothing. Default first-pass budget is $15. No repeat pass is automatic; `--repeats 3` explicitly requests it.

`results.json` preserves every completed turn, evidence, attempted tools, rejected queries, typed checks, provisional judge grades, cost and latency. Exact source files are archived alongside it. An interrupted partial scenario is not silently restarted; preserve that result and create a new experiment directory for any rerun. Completed experiments can be resumed only if source hashes match. Do not change prompts during a paired baseline.

`review.html` is a local, self-contained human review page. It shows required facts, answers, evidence and separate automated checks, with expandable judge decisions. Grade each answer, record agreement/disagreement with checks and judge, add notes, and download `human-review.json`. Browser-local storage is only a convenience; download the file to preserve decisions. Human decisions are not filled by the LLM and are not automatically imported into Langfuse yet.

Langfuse receives the `marketplace-30-v1` dataset, model/trial/turn run associations and separate structured/provisional-judge scores. Local JSON remains the durable evidence record. Judge grades are advisory until human review; this first batch is also calibration material, not a validated judge benchmark. Claude Opus 5.5 (`claude-opus-5-5`) is the fixed judge from a separate provider; human review is still required for both candidates. The earlier GPT-5.4 judge run was stopped and retained as exploratory history. Human review of all 60 answers remains the agreed next step.

Structured checks currently cover read-only state, citation resolution, query-record fidelity, selected named monetary fields and current/historical return policy versions. Query replay is **not** proof that the model selected the right query. Unsupported field shapes are marked not mechanically assessable, never an automatic pass. The semantic judge checks relevance, explanation and final numbers against independent gold and fixture records.

Validation status and results belong in dated result directories. Do not treat a successful syntax check or fixture setup as a successful live model comparison.

To reuse saved candidate answers after changing only the judge, pass `--reuse-from /results/<prior-run>/results.json`. Candidate and fixture source hashes and fixture state must match. Old grades remain in `previous_judge`; Claude grades are new. Previously recorded cost is carried forward rather than charging reused candidates twice.

If judge billing or availability blocks progress, use `--collect-only` to save candidate answers without judge calls. Later use `--grade-only --reuse-from /results/<collection>/results.json` in a new output directory to grade those exact answers. Existing successful Claude grades are reused when the configured model and rubric match. The reduced cost-conscious run retains both direct-Anthropic and OpenRouter grades, labeling route provenance; it is not a controlled route comparison. Missing grades remain explicitly pending. Neither mode silently reruns failed candidate answers to improve their score.

### Judge access

The shared gateway uses `ANTHROPIC_API_KEY` in `app/.env` and calls `anthropic/claude-opus-5-5`. OpenRouter remains an optional route (`openrouter/anthropic/claude-opus-5.5` with `OPENROUTER_API_KEY`) but is not used for the remaining grades in this iteration. Candidate and embedding calls still use the OpenAI key. The reduced batch preserves matching earlier Claude grades, including direct-Anthropic grades, to avoid unnecessary spend. At the user's request, remaining grades now use the refilled direct Anthropic account; route provenance is recorded. Cheaper judges are deferred to a later comparison.

### Active reduced scope

Use the 18-case selection in `core-18.json`: 36 scenario answers / 40 agent turns. Pass `--cases 02,04,08,09,10,11,14,15,16,17,20,21,23,24,26,27,28,30` with the usual reuse options. The full `cases.json` remains the 30-case regression pool; no candidate questions or gold requirements were changed. The reduced scope preserves capability families with fewer edge variants.

### September 29 gateway consolidation

Run `./scripts/start.sh` from the `app` directory to provision scoped keys before evaluation. The `eval-runner` Compose service is only an on-demand job, not a second LiteLLM service. It uses `http://gateway:4000/v1`. Model aliases and all provider routes live in `infra/litellm.yaml`; candidate and judge keys are distinct. Existing saved results/source snapshots document the historical two-gateway setup and are deliberately preserved. The v3 calibration plus unchanged human scores are published to `marketplace-core18-gold-v3`; use the verified `complete-import` runs.

## Offline routing replay

First experiment: [routing-offline-v1 findings](../results/routing-offline-v1-2026-09-29/FINDINGS.md). `scripts/offline-routing.py` classifies only each saved case's opening question through the evaluation virtual key, pins that selection for the whole case and reuses saved human grades/candidate costs. It does not connect to the business database or execute the support agent. This is a custom rubric, not native LiteLLM AutoRouter behavior.

From `app`, inspect/rebuild the existing summary without API calls:

```sh
backend/.venv/bin/python scripts/offline-routing.py --output results/routing-offline-v1-2026-09-29 --summarize-only
```

Omitting `--summarize-only` fills missing classifier decisions with paid calls (estimated $0.10 stopping budget). Existing decisions are reused and changed source/prompt hashes require a new output directory. Retain every version; do not overwrite prior experiments to tune the rubric. Unknown usage after a failed API call is not automatically counted and must be checked before retrying.

V2 routing adds the full generic application ontology and explicit task interpretation rules. Its [comparison with v1](../results/routing-offline-v2-2026-09-29/COMPARISON.md) preserves original human grades and candidate answers. The prompt is `eval/routing-v2-prompt.txt`; the runner is `scripts/offline-routing-v2.py`. Use `--summarize-only` with `results/routing-offline-v2-2026-09-29` to regenerate its report without API calls. `python3 scripts/compare-routing.py` rebuilds the v1/v2 comparison locally. Changing the prompt requires a new experiment directory. V1's original script and prompt remain unchanged.


### Nano/GPT-5 offline routing comparison (2026-09-29)

Saved experiment: `results/routing-gpt5-llm-jev-2026-09-29/`. Scripts: `scripts/routing-gpt5-comparison.py` (nano classifier and JEV via existing OpenRouter key), `scripts/routing-openrouter-gpt5.py` (restricted Auto Router selection probes), `scripts/render-routing-gpt5.py` (no-API report regeneration). First opening question pins a model for the entire saved case. Candidate grade source is the adjudicated core18 GPT-5 v2 comparison; manifests preserve its hash. Auto uses `plugins: [{id: "auto-router", allowed_models: ["openai/gpt-5-nano", "openai/gpt-5"], cost_tier: "low"}]`. No support-app routing changes. See report for cost accounting and the distinction between cached answer replay, custom classifiers, native crowd routing and live agent testing.
