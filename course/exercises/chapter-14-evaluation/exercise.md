# Chapter 14: Evaluation

Use five supplied model answers for human grading and five supplied structured answers for native Langfuse grading. Both exercises make **no model API calls**. The provided outputs are real saved marketplace answers. Local Langfuse runs at http://localhost:3000 in the `marketplace-support` project.

Run commands from the repository root. The app's existing Docker image includes the required Python packages. Its `eval-runner` service mounts `app/results` as `/results`. These activities do not reset or modify marketplace business records. Keep your reviews and imports under `app/results/chapter-14`.

## Part 1: Human evaluation

1. Read `fixtures/human-five.json`. For each case, inspect the question, supplied answer, independent golden requirements, and evidence. The golden reference is for evaluation only and was not supplied to the answering model.
2. Copy `fixtures/human-review-template.json` to `app/results/chapter-14/human-reviews.json`.
3. Assign a correctness score: **0 incorrect**, **1 partially correct**, or **2 correct**. Add a specific reason using the golden requirements and evidence. Equivalent wording is acceptable. Do not penalize an omitted optional detail or assume a valid citation proves the claim.
4. Validate your completed file without contacting Langfuse or a model:

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation run --rm --no-deps -v "$PWD/course/exercises/chapter-14-evaluation:/exercise:ro" eval-runner python /exercise/publish_human_reviews.py /results/chapter-14/human-reviews.json
```

5. Add `--publish --run-name chapter14-my-human-review` to the command to import your grades. Open the returned URL, or find that run in Langfuse **Datasets → chapter14-human-v1 → Experiments**. Check that there are five answers and a `human_correctness` score plus your reason for each.
6. Compare your decisions with the separate solution after completing your review. A disagreement needs analysis of facts and the rubric. It does not automatically mean either reviewer is wrong.

Do not use the historical human solution file as your own review. It is retained to discuss reference/rubric differences and missing reasons.

## Part 2: Native structured comparison

### One-time local setup

Enable the trusted local TypeScript evaluator runtime. This restarts only Langfuse's web and worker services and preserves their volumes:

```sh
docker compose -p marketplace-lab -f app/compose.yaml -f course/exercises/chapter-14-evaluation/compose.code-eval.yaml up -d --no-deps langfuse-worker langfuse-web
```

The local dispatcher executes trusted evaluator code inside the worker. Use the supplied evaluator for this course lab. This setup is not a sandbox for arbitrary code or a production deployment pattern.

### Import and grade

1. Read `fixtures/structured-five.json`. It contains five questions, independently recorded expected fields, actual saved JSON answers, and original trace references. Three questions concern an individual order item; two concern the total quantity across an order.
2. Import the supplied answers. This does not call the agent or any model:

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation run --rm --no-deps -v "$PWD/course/exercises/chapter-14-evaluation:/exercise:ro" eval-runner python /exercise/upload_structured_answers.py --publish --run-name chapter14-my-structured-review
```

3. In Langfuse, open **Evaluators → New evaluator → New code evaluator**. Choose **TypeScript** and replace the template with `structured-evaluator.ts`. Name it **Chapter14 structured order comparison**. If your project already has that evaluator and its matching rule, inspect and reuse it instead of making a duplicate.
4. In the test panel, filter by observation name `chapter14-structured-answer`, select one imported answer, and run the test. Verify that reference and actual status/quantity are visible and the code emits the four scores below.
5. Save the evaluator. Reuse that name filter as a rule with 100% sampling. Enable scoring of past matching observations for the imported cases. The native worker computes the grades asynchronously; the upload script does not grade them. In a shared project, use your experiment or dataset filter too to isolate your own five cases.
6. Open the imported run in **Experiments**. Select only your run as baseline. Confirm five rows and examine:
   - `schema_valid`
   - `status_matches`
   - `quantity_matches`
   - `structured_grade`
7. Explain why all five supplied answers are correct under this narrow contract. Use the separately labelled evaluator controls to see partial and incorrect outcomes; do not describe those authored controls as real model failures.
8. Inspect one answer observation and its `original_trace_id` metadata. Open that original trace to see the agent's question, model/tool sequence, evidence, latency and token usage. The imported task's duration and model cost describe import work, not the original agent execution.

## Completion

Retain your five human grades with reasons, the two Langfuse result links or screenshots, and a short explanation of what exact field checks prove and what they leave untested. This evaluator does not establish semantic correctness of a policy explanation or citation grounding. No new candidate or Claude calls are required for either exercise.
