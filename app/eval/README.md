# Evaluation fixtures and runners

For the current course lab, begin with the [evaluation exercise](../../course/exercises/evaluation/exercise.md). Saved course comparison data is in [the model comparison package](../../course/evaluation/chapter-14-model-comparison/README.md). The commands below describe the larger optional 30-case runner; they do not reproduce every course comparison automatically.

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

Langfuse receives the `marketplace-30-v1` dataset, model/trial/turn run associations and separate structured/provisional-judge scores. Local JSON remains the durable evidence record. Judge grades are advisory until human review; this first batch is also calibration material, not a validated judge benchmark. Claude Opus 5.5 (`claude-opus-5-5`) is the fixed judge from a separate provider; human review is still required for both candidates. The earlier GPT-5.4 judge run was stopped and retained as exploratory history. Treat judge grades as provisional until a human has reviewed the corresponding answers.

Structured checks currently cover read-only state, citation resolution, query-record fidelity, selected named monetary fields and current/historical return policy versions. Query replay is **not** proof that the model selected the right query. Unsupported field shapes are marked not mechanically assessable, never an automatic pass. The semantic judge checks relevance, explanation and final numbers against independent gold and fixture records.

Validation status and results belong in dated result directories. Do not treat a successful syntax check or fixture setup as a successful live model comparison.

To reuse saved candidate answers after changing only the judge, pass `--reuse-from /results/<prior-run>/results.json`. Candidate and fixture source hashes and fixture state must match. Old grades remain in `previous_judge`; Claude grades are new. Previously recorded cost is carried forward rather than charging reused candidates twice.

If judge billing or availability blocks progress, use `--collect-only` to save candidate answers without judge calls. Later use `--grade-only --reuse-from /results/<collection>/results.json` in a new output directory to grade those exact answers. Existing successful Claude grades are reused when the configured model and rubric match. The reduced cost-conscious run retains both direct-Anthropic and OpenRouter grades, labeling route provenance; it is not a controlled route comparison. Missing grades remain explicitly pending. Neither mode silently reruns failed candidate answers to improve their score.


Provider/model configuration must match your own available accounts. Inspect the runner options before making paid calls. Historical local outputs and authoring receipts are not distributed in this checkout.
