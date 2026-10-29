# Evidence reviewer and one correction: diagnostic v1

October 1, 2026. Experimental workflow only; the support application remains unchanged.

## Design

Reuse frozen nano drafts and GPT-5.4 answers from the current history-v3 baseline. GPT-5.4 reviews each nano question, answer and retrieved evidence without golden answers, prior grades or the stronger model's baseline answer. It has no tools. It can identify contradictions, missing evidence, unsupported causes and necessary additional retrieval. The controller passes its feedback to nano only if revision is requested. Nano gets one correction stage, may use the same five read-only MCP tools, and must treat reviewer feedback as a hypothesis. There is no repeated review loop.

Eight cases: 09, 10, 14, 15, 16, 17, 20, 23. Five previously problematic nano answers (three partial, two incorrect) and three correct controls. This selection is diagnostic and enriched for known issues, not representative accuracy measurement or held-out validation. The reviewer prompt includes general policy/time and ambiguity guidance informed by earlier diagnosis; it is not a blind measure of an untuned reviewer.

Each correction resets the matching market_eval fixture and verifies source hashes, fixture fingerprint, saved evidence snapshot and document revision. Draft evidence is supplied explicitly; existing handles can be fetched from the saved same-snapshot evidence, while new retrieval goes through MCP. No gold enters either stage. No interactive data is changed.

## Evaluation

Independent assistant review compares final text to the existing gold/reference. Keep initial grade, reviewer feedback, final grade, retrieved records and citation validity separate. Check corrected errors, missed problems, unnecessary revisions and introduced regressions. GPT-5.4's reviewer verdict is part of the system, not the grading oracle. Retain failed stages as execution failures.

Reuse is intentional: report review/correction spend separately from historical generation cost. A simulated total combines saved nano generation cost with new incremental cost; latency is likewise assembled, not freshly measured end to end. All rates are estimates, not invoices, and exclude embeddings/unreturned timeout usage. Incremental conservative budget $5; stage limit eight model calls and $0.50 between-call estimate; one nano correction, bounded retrieval and time. Client request limit 120 seconds; gateway independently limits requests to 60 seconds.

## Artifacts

- [Runner](../../scripts/reviewer-workflow.py)
- Saved baseline (historical instructor evidence; retained separately)
- Results (historical instructor evidence; retained separately)

Reproduce from app with `docker compose run --rm --no-deps -v "$PWD/scripts:/scripts:ro" -e PYTHONPATH=/app eval-runner python /results/reviewer-workflow-v2-2026-10-01/reviewer-workflow.py`. Completed cases resume; changing runner source requires a new output path. This is an evaluator–optimizer workflow with model-controlled investigation inside its stages. It is not autonomous seller delegation or an independent paid grading experiment.

## Completed evidence-packet correction

V1 excluded catalog definitions; the reviewer questioned a valid unit conversion and missed a catalog rule. V2 supplies the full original evidence with identical prompts. Both runs are preserved. Final report (historical instructor evidence; retained separately): nano 3 correct / 3 partial / 2 incorrect; workflow 5 / 3 / 0; GPT-5.4 baseline 7 / 1 / 0 on these eight diagnostic cases. No fresh end-to-end baseline rerun.


## Accepted milestone and publishing takeaway

The user accepted this as a completed learning milestone on October 1. No further runs are required to close it. Assistant grades remain provisional; acceptance of the experiment does not constitute individual grade adjudication or a production-policy decision.

Including the saved nano generation cost, the workflow estimate is $0.2575 versus $0.4244 for saved GPT-5.4 alone: approximately 39% lower cost, with 5 versus 7 fully correct answers. Every draft was reviewed; only flagged drafts were corrected. These conservative uncached totals combine historical generation with new review/correction, rather than fresh end-to-end measurements.

The workflow preserved all three correct controls. One incorrect answer became correct and one became partial; one partial became correct and two remained partial. Describe this as a bounded evaluator–optimizer workflow with two agents, demonstrating how to measure improvement and overhead. Do not imply that review verdicts are ground truth or that this small selected set establishes a general winner. Further validation is optional future work; teaching packaging and memory are the next proposed activities.


## Reviewer-model ablation and core18 expansion — October 1

The user requested a same-model critic to separate the review-stage effect from stronger reviewer capability, then coverage of all eighteen cases. Compare nano generation alone, nano reviewer plus at most one nano correction, GPT-5.4 reviewer plus at most one nano correction, and saved GPT-5.4 alone. Keep reviewer prompt, full evidence, generator, model settings and correction limit fixed. Reviewer-model change includes its documented model price; no golden answer enters either stage.

Eight-case Nano review requested no corrections; final answers stayed 3 correct / 3 partial / 2 incorrect, versus 5 / 3 / 0 after stronger review. Incremental Nano review estimate $0.00497. This supports reviewer-capability dependence on these drafts, not proof that a weak model never benefits from review.

Expand both variants to the full eighteen-case suite, reusing the eight completed rows per variant. Cases 27 and 28 preserve original prior conversation; review/correct only the final turn. Case 28 reproduces its prescribed purchase mutation before matching final evidence revision. Earlier turns are frozen; this is not a freshly generated conversational trajectory. Both earlier first-turn nano answers were correct under the saved grades. Independently grade the resulting conversation against the same accepted gold, keeping correct/partial/incorrect separate from reviewer approval.

Runner: [core18 replay](../../scripts/reviewer-workflow-core18.py). Outputs: Nano reviewer (historical instructor evidence; retained separately) and GPT-5.4 reviewer (historical instructor evidence; retained separately). Preserve original eight-case reports as historical; eighteen-case reports supersede their coverage conclusions. Compare assembled full-generation-plus-review/correction estimates as well as incremental costs. Fresh end-to-end repeat trials remain future validation.


**Core18 complete:** Current ablation report (historical instructor evidence; retained separately) and comparison (historical instructor evidence; retained separately). Nano alone and Nano-review workflow: 11/4/3; stronger-review workflow: 14/4/0; GPT-5.4 alone: 17/1/0. Counts are correct/partial/incorrect. All 36 executions completed; all eighteen review inputs matched between variants. This supersedes the original eight-case coverage headline; historical artifacts remain unchanged.

For a fresh full-suite rerun, mount `scripts` as above and run `/scripts/reviewer-workflow-core18.py` with `REVIEWER_ALIAS=eval-nano` or `eval-54` and a new `REVIEWER_OUT=/results/<new-run-directory>` environment value. Existing completed directories resume without redoing cases; changing runner source requires a new directory. A new directory without seeded reused rows runs all eighteen reviews.
