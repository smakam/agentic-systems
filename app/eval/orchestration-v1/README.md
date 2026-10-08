# Payout orchestration experiment v1

Approved October 1, 2026. Fixed model: GPT-5.4 (`eval-54`, configured snapshot `gpt-5.4-2026-03-05`). Compare execution structure, not model choice. The interactive support application is unchanged.

## Question and controls

Investigate all sellers' payouts, explain supported reasons, include paid and zero-due controls, and summarize unpaid totals by seller. An evaluator-only fixture resets **market_eval**, never the interactive marketplace. Two identical builds produced the same fingerprint before live calls. Three sellers and eleven payouts cover seven outcome classes: not delivered, less than 24 hours since delivery, active return, eligible but no release requested, failed provider attempt, fully refunded/no payout due, and paid. Active returns include requested and received/refund-pending examples; a failed-then-successful control tests chronology. These are synthetic scenarios with a common settlement policy; unknown real-world causes must remain unknown.

## Variants

1. One agent, serial tools: one tool call at a time.
2. One agent, parallel tools: independent tool calls can run together; dependent retrieval remains sequential.
3. Coordinator plus seller workers: discover sellers, delegate one investigation per seller (at most three), then synthesize. Each worker owns a separate loop and MCP evidence store, using the same model and five read-only tools. Worker findings and source envelopes return to the coordinator.

All variants share static business instructions, output format, data and documents. Workers verify the same revision/clock/document revision before reading. This is not a fixed workflow comparison, reviewer–optimizer loop, or A2A test. No reason to assume multi-agent will win: this task may be handled by one broad SQL query and one policy lookup.

## Measurement and evaluation

Start with one smoke trial per variant, then extend to three trials if execution is valid. Rotate order across trials. Per-run aggregate ceiling: 32 model calls, 300 seconds and $2.50 estimated uncached model spend; batch ceiling $15. Cost checks occur between model calls and are estimates, not provider billing enforcement. No paid LLM judge. Embedding spend is separate from these model estimates.

Deterministic checks compare payout coverage, seller/order identity, amounts, seller totals, known citation handles, and unchanged business state. They do **not** establish explanation correctness. Assistant review separately checks supported reasons, latest attempts, hold timing, zero/paid controls, and claim/source support. Record disagreements and unresolved output errors rather than treating missing answers as correct.

Compare semantic quality first, then total latency, cost, model/tool calls, cached input and observed overlap. Client tool intervals establish overlapping requests, not parallel execution inside PostgreSQL. Three repeats on one fixed task are descriptive evidence, not a general recommendation. Cache/run order can confound latency and cost.

## Artifacts and reproduction

- [Fixture/oracle](../../scripts/payout-orchestration-fixture.py)
- [Runner](../../scripts/payout-orchestration.py)
- [Results directory](../../results/payout-orchestration-v2-2026-10-01/)

From `app`: `docker compose run --rm --no-deps -v "$PWD/scripts:/scripts:ro" -e PYTHONPATH=/app -e ORCHESTRATION_TRIALS=3 eval-runner python /scripts/payout-orchestration.py`. Add `-e ORCHESTRATION_DRY=1` for fixture validation without inference. The runner resumes saved trials and archives its source; changing source requires a new experiment directory.

## Smoke-run correction

The first v1 serial and parallel attempts hit the existing 40-second per-request client timeout after retrieval. They are retained in `results/payout-orchestration-v1-2026-10-01`. V2 changes only the experiment client request timeout to 120 seconds for every variant, retaining the 300-second aggregate run ceiling. Do not count a missing answer as a semantic failure of GPT-5.4 or infer architectural superiority from timeout differences.

## Grading boundary for eligible-but-unreleased payouts

The fixture builder knows no release command was executed. The source policy says delivery alone does not imply completed payout, but does not explicitly document the initial manual release step. An answer that correctly identifies eligibility, no recorded payout attempt, and an unknown operational reason is acceptable; do not penalize the model for refusing to invent an operator motive. Explicit “release not requested” is acceptable only as an inference from complete event history. Record this source gap when reviewing the oracle.

Order-history responses contain nested evidence envelopes. Offline checker registration traverses those envelopes; otherwise valid citations would falsely fail. Original checks are retained as `initial_checks`. The correction does not edit model answers or rerun inference. The checker has one positive and four negative controls (missing payout, duplicate payout, wrong amount, unknown citation).

## Interpretation limits

Agents may choose different valid query shapes. This compares complete controller strategies; it does not isolate scheduling while holding SQL identical. Three rotated repeats help expose variability but do not remove cache warming, provider load or sampling effects. Saved token usage supports a cache-adjusted estimate ($2.50 input, $0.25 cached input, $15 output per million); retain the conservative uncached estimate used by the guards. Timed-out requests with no returned usage may still be billable and are not fully captured.

## What “serial” and “parallel” mean here

Serial/parallel describes tool execution, not seller ordering. One SQL query can return all sellers. A model request first chooses a tool and its arguments; MCP executes that tool; a later model request receives its returned records and chooses another step or writes the final answer. The worker variant adds independent seller-scoped model/tool loops.

The v1 serial timeout was model request 9, after successful payout, return/refund and payout-event queries (started at 49.9 seconds; run ended at 90.2). The parallel timeout was request 5, after payout/accounting and payout-event queries (34.4 to 74.7 seconds). Both exceeded the 40-second client request limit. Tool results had already arrived. Larger input/output and provider delay are plausible contributors, not established causes; no response was returned to show what the model would have done next.

## Two architectures, three experiment variants

Serial and parallel are scheduling variants of the same single-agent architecture. They do not prescribe one seller per SQL call. Catalog discovery precedes SQL construction. Once order IDs are known, independent histories can be requested together: trial 2 parallel issued ten order-history requests after catalog and payout discovery. Single-agent serial may choose a bulk query instead. Thus permitted concurrency and realized overlap must be reported separately. Workers introduce independent seller-scoped agent loops and final synthesis. The experiment tests two architectural choices and three complete strategies, not three distinct architectures or identical query plans.
