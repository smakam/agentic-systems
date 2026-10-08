# Payout fixture version 2

Created 2026-09-29. Targeted seed-only variant; original default fixtures and historical results remain unchanged.

- Case16: unchanged, delivered 2026-09-27 12:00 UTC; snapshot 2026-09-28 11:00 UTC (23h). Expected: not eligible, one hour remains.
- Case17: snapshot becomes 2026-09-28 12:30 UTC (24h30m). Expected: eligible, not yet paid; no active return. Original exactly-24h case remains the v1 boundary test.

`eval_fixtures.py` is a versioned copy of the baseline fixture module with only the case17 clock override and matching validation assertion. The half-hour is applied directly to the isolated seeded evaluation state after the existing clock action; it does not add a production UI action or modify recorded delivery/recording times. It does not change agent-visible policy. `cases.json` versions fixture description and evaluator gold; these do not enter model context.

Run from app (Docker, shared gateway, evaluation key configured):

```sh
docker compose run --rm --no-deps -e PYTHONPATH=/app \
  -v "$PWD/scripts:/scripts:ro" \
  -v "$PWD/eval/payout-v2/eval_fixtures.py:/app/marketplace/eval_fixtures.py:ro" \
  eval-runner python /scripts/payout-v2-eval.py --dry-run
```

Omit `--dry-run` for two repeats per case with GPT-5.4 only, no judge. Script uses fixed versioned output directories and preserves completed results. Evaluation runner retains its estimated $3.50 stopping budget with $2.50 scenario reserve; this is not a provider billing cap. Actual candidate spending is recorded in results.json. Only market_eval is reset.

This is a candidate baseline for these two cases, not a replacement of the full 18-case comparison. Nano and human/judge grading have not been rerun on v2. Do not use the old case17 grade as a v2 result or revise old routing scores retroactively.
