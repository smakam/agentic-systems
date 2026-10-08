# Scenario-only semantic iteration

# Semantic routing: scenario coverage v2

September 30, 2026. Add missing business scenarios, not copies of evaluation questions. Keep embedding model, max aggregation, threshold 0.5, heuristic fallback and candidate pool unchanged. The original v1 configuration and nine-policy comparison are preserved.

## Scenario audit

| Cases | Missing scenario | Tier |
|---|---|---|
| 09 | No explicit distinction between buyer collection and seller settlement. | COMPLEX |
| 10 | Existing policy scenario covers applicability reasoning, not a direct current policy lookup. | SIMPLE |
| 11 | Existing applicability scenario does not explicitly represent effective-date lookup. | COMPLEX |
| 15 | No return exception or manual-review workflow scenario. | COMPLEX |
| 20, 21 | Existing payment retry scenario does not explicitly cover refund attempts versus final refund state. | COMPLEX |
| 24 | No partial-quantity return and remaining seller allocation scenario. | COMPLEX |

Cases 14 (buyer paid/seller unpaid), 27 (ambiguous business name) and 28 (seller balances) already had coverage, so no new scenario was added for them. Six scenario categories contributed twelve descriptions, increasing the index from 14 to 26 utterances. Native matching still embeds text; scenario descriptions are not executable routing rules.

## Results

| Metric | Original semantic v1 | Scenario-expanded v2 |
|---|---:|---:|
| Correct / partial / incorrect | 13 / 4 / 1 | 13 / 4 / 1 |
| Fully correct | 72.2% | 72.2% |
| Heuristic fallbacks | 10 | 6 |
| Nano / GPT-5 selections | 13 / 5 | 9 / 9 |
| Full-price replay cost including embeddings | $0.137874 | $0.196334 |

New embedding spend: $0.00001226. No candidate answers or judge calls were regenerated. This development iteration reuses saved accepted grades; it is not held-out evidence.

## What changed and why it matters

Four prior no-matches crossed the threshold: 10, 11, 15 and 20. Case 15 already selected GPT-5 through heuristic fallback. Case 26 changed from a simple semantic match to a complex one. All four actual model switches selected GPT-5 where the saved nano answer was already correct, explaining unchanged quality and higher cost.

The current-policy lookup (10) matched the historical-policy scenario, even though we added a simple current-policy category. Text similarity captures shared subject matter but does not necessarily separate reasoning demands.

Refund-history questions 20 and 21 differ only in their order identifier. The nearest v2 scenario scored approximately 0.529 and 0.493 respectively, on opposite sides of 0.5. This shows sensitivity to incidental identifiers in this pair; we have not yet tested normalization or established a general causal effect.

Cases 14, 27 and 28 still missed despite existing scenario coverage. Cases 09, 21 and 24 missed despite added scenarios. Lower fallback count is not itself better routing quality.

## Case-level diagnostics

The cosine scores below are independently computed from captured query/index embeddings. Native LiteLLM decisions remain authoritative. Original-index scores use the captured vectors restricted to original utterances, not previously saved v1 scores.

| Case | Best original-index score | Best expanded-index score | v2 outcome |
|---|---:|---:|---|
| 09 | 0.406 | 0.462 | no_match_heuristic; eval-nano |
| 10 | 0.404 | 0.564 | semantic_match; eval-5 |
| 11 | 0.438 | 0.539 | semantic_match; eval-5 |
| 14 | 0.415 | 0.415 | no_match_heuristic; eval-nano |
| 15 | 0.393 | 0.586 | semantic_match; eval-5 |
| 20 | 0.482 | 0.529 | semantic_match; eval-5 |
| 21 | 0.486 | 0.493 | no_match_heuristic; eval-nano |
| 24 | 0.289 | 0.370 | no_match_heuristic; eval-nano |
| 26 | 0.544 | 0.677 | semantic_match; eval-5 |
| 27 | 0.485 | 0.485 | no_match_heuristic; eval-nano |
| 28 | 0.387 | 0.387 | no_match_heuristic; eval-nano |

## Decision and next option

Preserve v2 as an experiment; do not promote it as an improvement over v1. A separately versioned identifier-normalization diagnostic would be more informative than adding further scenario text blindly. Do not lower the threshold or alter fallback in this run. Fresh validation would be required before generalizing any tuned result.

Artifacts: frozen-config.json, manifest.json, native.json (decisions, usage and embeddings), analysis.json (all nearest matches and grades). Scripts: scripts/routing-semantic-scenarios.py and scripts/analyze-semantic-scenarios.py. Gateway and production routing unchanged.
