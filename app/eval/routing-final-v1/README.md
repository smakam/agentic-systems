# Routing completion experiments, version 1

Approved scope, September 30, 2026: add keyword, default heuristic, semantic and OpenRouter medium comparisons; then run a six-conversation live pilot comparing fixed nano, fixed GPT-5, conversation pinning and per-question selection. High-tier OpenRouter, Not Diamond, per-internal-call routing and staged nano-tools/GPT-5-final orchestration are deferred.

## Classification replay

`classifiers.json` was hashed before execution. It uses specification journey categories, not gold answers. This is still a known development set, not leak-free held-out evaluation. Freeze means an artifact SHA256, not a git commit. No rule or threshold was tuned after observing these results.

The native methods run with the installed LiteLLM 1.102.1 image in an isolated container, without changing the active gateway configuration. SIMPLE maps to nano, all higher tiers to GPT-5. Keyword and semantic no-match cases use native heuristic fallback. The semantic threshold is 0.5 and index aggregation is max; API failures are surfaced by the harness rather than counted as semantic decisions. Model selection reuses the accepted payout-v2 core18 saved answers. No new candidate or judge calls.

Scripts: `../../scripts/routing-native-final.py`, `../../scripts/routing-openrouter-medium.py`, `../../scripts/render-routing-final.py`. Results: `../../results/routing-classifiers-2026-09-30/`. Native code and effective configs are archived with the result. Semantic embeddings use the evaluation virtual key through the shared LiteLLM gateway. OpenRouter probes use the existing funded OpenRouter key directly; generated probe text is not graded.

## Live granularity pilot

`conversations.json` is evaluator-only expected text and records, frozen before live execution. Six new three-turn scripts cover increasing complexity, decreasing complexity, clarification, purchase mutation, clock mutation, and stable simple lookups. They reuse known business fixtures and are not the unseen validation set.

The classifier sees the current question plus actual prior conversation, with the unchanged routing-v2 prompt. It does not see future turns, expected answers, grades, or fixture oracle snapshots. Each policy generates its own conversation history. All tool/model steps within one user question use one model; only the question-level policy may switch between questions. App-level mapping implements this experiment; production routing is unchanged.

Run from `app/`:

```sh
docker compose run --rm --no-deps -e PYTHONPATH=/app \
  -v './scripts:/scripts:ro' \
  -v './eval/payout-v2/eval_fixtures.py:/app/marketplace/eval_fixtures.py:ro' \
  eval-runner python /scripts/routing-granularity.py --dry-run

docker compose run --rm --no-deps -e PYTHONPATH=/app \
  -v './scripts:/scripts:ro' \
  -v './eval/payout-v2/eval_fixtures.py:/app/marketplace/eval_fixtures.py:ro' \
  eval-runner python /scripts/routing-granularity.py
```

The runner requires both database connections to resolve to `market_eval`, holds an evaluation lock, verifies identical fixture hashes between policies and verifies that agent runs do not change business state. It retains conversations across turns and resets between policies. Read-only expected snapshots are saved before calls. Embeddings are restored from the versioned document cache. Existing completed results are not rerun; interrupted scenarios cannot silently overwrite paid attempts.

A $3 full-price estimated-spend guard includes candidate/classifier calls and reserves for unknown usage. All per-call request/response bodies and reported cached tokens are retained without auth headers. Retrieval embeddings are separately accounted for. No paid Claude judge runs; assistant review and flagged uncertainties are recorded in `assistant-review.json`.

Natural provider cache is shared: randomized policy order reduces a fixed ordering effect but does not establish cold-cache control. Report cached-input fraction, reconstructed cache-adjusted cost, full-price cost, per-turn end-to-end p50/p95 and model switches. Do not infer a causal switch penalty. Six conversation clusters and one pass give diagnostic evidence, not statistical proof.

Validation/rendering: `python3 scripts/render-routing-granularity.py` checks each turn's internal model pin, SDK/captured token totals, unchanged business state and fixture equivalence, then renders expected text/records separately from actual model text and retrieved evidence.

## Future work

- Run a second pass only for specific unstable findings, preserving first-pass results.
- Validate a frozen chosen policy on 10–12 new scenario combinations before general quantitative recommendations; no publication claim from these development cases alone.
- Per-call routing, explicit escalation and stage-based orchestration remain distinct deferred experiments.
- Embedding example/threshold calibration on a separate development set, custom-trained routers, and a third candidate model need separately versioned studies.

## September 30 execution and resumption

OpenAI credit exhaustion interrupted S2/conversation turn 2 after 22 successful turns. `credit-interruption-results.json` preserves that state; `interrupted-session.json` preserves prior history. After funding, `scripts/resume-routing-granularity.py` restored that session, removed only the failed question's duplicate user entry and retried that question. Completed answers were retained. The rejected request remains in the call ledger without invented usage or charges. The $0.20 unknown-usage reserve is a guard allowance, not measured spend.

An OpenRouter GPT-5 availability probe cost $0.00063125. A replacement experiment was considered but not run: temporary aliases were never activated, and the gateway configuration was restored. The live comparison stayed on the original direct OpenAI route. Funding downtime is excluded from turn latency; resulting cache warmth is not controlled.

`validate-routing-gold.py` independently checks the frozen expected facts against scenario snapshots. This checks the gold, not the answer's correctness. The separate assistant review compares each generated answer with those facts; it is not a new Claude assessment or user review.
