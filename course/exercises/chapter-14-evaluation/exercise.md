# Chapter 14 — Learner exercise

Two tasks: human-grade five supplied answers, then use Langfuse's native code evaluator on three structured answers. All questions, candidate answers and golden references are provided. No model calls are required.

## Before starting

Use the existing local marketplace lab and Langfuse project **marketplace-support**. Run upload commands from the application repository root. The native TypeScript evaluator and local dispatcher must already be configured; reuse **Chapter14 structured order comparison**. Setup instructions are in the package README. Keep solutions closed until you finish.

## Part A — Human evaluation of five answers

### 1. Copy and open the worksheet

Copy `course/exercises/chapter-14-evaluation/fixtures/human-worksheet.json` to `app/results/chapter-14/human-worksheet.json`.

Each case contains the question, golden facts and Nano's saved answer. Edit only **score** and **reason**.

### 2. Grade each model answer

Compare the answer with the golden facts. Assign **0 incorrect**, **1 partially correct**, or **2 correct**, and write a short fact-based reason. Grade the answer, not the question or golden reference. Equivalent wording is acceptable.

### 3. Validate the completed JSON

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation \
  run --rm --no-deps \
  -v "$PWD/course/exercises/chapter-14-evaluation:/exercise:ro" \
  eval-runner python /exercise/publish_human_reviews.py \
  /results/chapter-14/human-worksheet.json
```

**Expected:** five validated reviews and zero model calls. Missing scores, invalid values, blank reasons or changed question/gold/answer fields are rejected.

### 4. Upload your human grades to Langfuse

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation \
  run --rm --no-deps \
  -v "$PWD/course/exercises/chapter-14-evaluation:/exercise:ro" \
  eval-runner python /exercise/publish_human_reviews.py \
  /results/chapter-14/human-worksheet.json \
  --publish --run-name chapter14-my-human-review
```

**Expected:** a printed experiment URL. Open it and check all five answers, scores and comments. Langfuse displays your imported human grades; it does not grade them again. Use a new run name for another submission.

## Part B — Native evaluation of three structured answers

### 1. Inspect the supplied JSON

Open `fixtures/structured-three.json` in this package. Each item has a question, expected shipment status and quantity, and an actual recorded GPT-5.4 answer. Do not generate new model answers.

### 2. Import the three outputs

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation \
  run --rm --no-deps \
  -v "$PWD/course/exercises/chapter-14-evaluation:/exercise:ro" \
  eval-runner python /exercise/upload_structured_answers.py \
  --fixture structured-three.json --publish \
  --run-name chapter14-my-structured-review
```

**Expected:** three imported items, zero model calls and an experiment URL. This script imports answers, not grades.

### 3. Use the native evaluator

In Langfuse, open **Evaluators → Chapter14 structured order comparison**. Inspect the TypeScript source, select one matching imported observation to test the field mapping, and confirm the rule targets `chapter14-structured-answer` at 100% sampling. Reuse the existing rule. If using a shared project, restrict it to your dataset/experiment where appropriate.

The Langfuse worker executes the comparison asynchronously. If the rule was created after import, include past matching observations. Upload completion alone does not mean grading finished.

### 4. Inspect the experiment results

Open the URL printed by the import command. Compare question, golden fields, actual JSON and scores. Record `schema_valid`, `status_matches`, `quantity_matches`, and `structured_grade`. Confirm source **EVAL** for native scoring. Explain what each check proves; these field checks do not establish citation grounding or full semantic correctness.

## Submit

Provide your completed human worksheet, both experiment URLs, one explanation of a human grade, and the three native results with field checks. Keep human grades and native code results distinct. Do not include credentials. Compare with the separate solutions after submission.
