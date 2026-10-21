# Evaluation — Learner exercise

## Workspace for this activity

Use [local Langfuse](http://localhost:3000), project **marketplace-support**, and the supplied saved answers. No marketplace UI or business database is required for this activity. Run the documented import commands from the application repository root; keep the configured Langfuse worker and dispatcher running.

Two tasks: human-grade five supplied answers, then use Langfuse's native code evaluator on three structured answers. All questions, candidate answers and golden references are provided. No model calls are required.

## Before starting

Use the existing local marketplace lab and Langfuse project **marketplace-support**. Run upload commands from the application repository root. The native TypeScript evaluator and local dispatcher must already be configured; reuse **Chapter14 structured order comparison**. Complete the [learner setup in the package README](README.md#learner-setup--complete-once-before-the-exercise) to enable the local dispatcher and create your own evaluator/rule. Keep solutions closed until you finish.

## Part A — Human evaluation of five answers

### 1. Open the worksheet in this exercise folder

Open [human-worksheet.json](human-worksheet.json) directly in `course/exercises/evaluation/`. It contains five questions, golden references and actual saved Nano answers. Edit this file in place; there is no copy step. If you already completed an older copy under `app/results/chapter-14/`, keep it and use its `/results/chapter-14/human-worksheet.json` path with the same validation/upload commands instead.

The worksheet is a human-grading submission, not a database fixture. Keep the [solutions](solutions/answers.md) closed until you finish.

### 2. Grade each model answer

In `course/exercises/evaluation/human-worksheet.json`, update each object in the `cases` array: replace `score: null` with **0 incorrect**, **1 partially correct**, or **2 correct**, and fill `reason` with a short fact-based explanation. Compare `model_answers` with `golden_facts`; leave `questions`, `golden_facts`, `model_answers` and `case_id` unchanged. Repeat for all five cases. Equivalent wording is acceptable. Use **2** when all required facts are correct and supported, **1** when the answer is useful but incomplete without a wrong central conclusion, and **0** when the central conclusion is wrong, unsupported, or does not answer the question. Judge citation/evidence requirements against the supplied reference; do not award full credit merely for fluent wording.

For example, a completed case contains these two fields (choose your own grade and reason):

```json
"score": 2,
"reason": "The answer includes all required facts and matches the golden reference."
```

### 3. Validate the completed JSON

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation \
  run --rm --no-deps \
  -v "$PWD/course/exercises/evaluation:/exercise:ro" \
  eval-runner python /exercise/publish_human_reviews.py \
  /exercise/human-worksheet.json
```

**Expected:** five validated reviews and zero model calls. Missing scores, invalid values, blank reasons or changed question/gold/answer fields are rejected.

### 4. Upload your human grades to Langfuse

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation \
  run --rm --no-deps \
  -v "$PWD/course/exercises/evaluation:/exercise:ro" \
  eval-runner python /exercise/publish_human_reviews.py \
  /exercise/human-worksheet.json \
  --publish --run-name chapter14-my-human-review
```

**Expected:** a printed experiment URL. Open it and check all five answers, scores and comments. In **Experiments**, filter to `chapter14-human-v1` and open your run name. Select one answer, choose **evaluator** in the middle trace tree, then scroll the right panel to **Output**. `human_correctness` is your score and its comment is your reason. The source is **API** because the script uploaded the grades; the metadata records human grading. An error count of zero means the publication task had no execution error, not that all answers are correct. Langfuse displays your imported human grades; it does not grade them again. Use a new run name for another submission.

## Part B — Native evaluation of three structured answers

### 1. Inspect the supplied JSON

Open [structured-three.json](structured-three.json) in this package. Each item has a question, expected shipment status and quantity, and an actual recorded GPT-5.4 answer. Do not generate new model answers.

### 2. Import the three outputs

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation \
  run --rm --no-deps \
  -v "$PWD/course/exercises/evaluation:/exercise:ro" \
  eval-runner python /exercise/upload_structured_answers.py \
  --fixture structured-three.json --publish \
  --run-name chapter14-my-structured-review
```

**Expected:** three imported items, zero model calls and an experiment URL. This script imports answers, not grades.

### 3. Use the native evaluator

In Langfuse, open **Evaluators → Chapter14 structured order comparison**. On the right, use **Test with sample observations**. Select the radio button for one of your imported `chapter14-structured-answer` rows, then click **Run test on this sample**. Inspect the returned checks. This reruns code grading of a saved answer; it makes no new agent answer and does not create an experiment. Inspect the TypeScript source and confirm the rule targets `chapter14-structured-answer` at 100% sampling. Reuse the existing rule. If using a shared project, restrict it to your dataset/experiment where appropriate.

The import creates a named experiment and links each saved answer to a dataset item. The enabled observation rule triggers grading automatically; you do not need the UI **Run experiment** button for this supplied-answer workflow. The Langfuse worker executes the comparison asynchronously. If the rule was created after import, include past matching observations. Upload completion alone does not mean grading finished.

### 4. Inspect the experiment results

Open the URL printed by the import command. Compare question, golden fields, actual JSON and scores. Record `schema_valid`, `status_matches`, `quantity_matches`, and `structured_grade`. Confirm source **EVAL** for native scoring. The three supplied outputs match their references, so expect three `correct` grades and true schema/status/quantity checks. The overall grade is categorical; it does not use the human 0–2 scale. Explain what each check proves; these field checks do not establish citation grounding or full semantic correctness.

### If the sample test cannot run

If it reports **code eval dispatcher is not configured**, repeat the dispatcher setup in the [package README](README.md#learner-setup--complete-once-before-the-exercise) for both Langfuse web and worker, preserving any additional local Compose overlays. Refresh and repeat the sample test. A passing sample test confirms that one code execution works; separately check the scores on all three experiment items. If scores remain absent, check the enabled rule, matching observation name, 100% sampling and worker queue before importing another run.

## Submit

Provide your completed human worksheet, both experiment URLs, one explanation of a human grade, and the three native results with field checks. Keep human grades and native code results distinct. Do not include credentials. Compare with the separate solutions after submission.
