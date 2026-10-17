# Chapter 14 evaluation package

[Full 18-case human/Claude comparison](../../evaluation/chapter-14-model-comparison/README.md)

This package separates three grading methods and two integration paths:

- **Instructor:** Walk through five golden cases, saved Nano answers and imported Claude grades; then three golden cases, the native TypeScript evaluator and its recorded results. No scripts or model calls during the demo.
- **Learner:** Human-grade five supplied answers and import their grades. Import three supplied structured outputs and let the native Langfuse worker perform field comparisons.

The learner exercises make no model API calls. Candidate answers and golden references are supplied. Instructor live Claude judging is paid and requires an explicit flag. Preparing the package generated the five structured answers once, outside learner execution.

The learner `fixtures/` folder contains only `human-worksheet.json` and `structured-three.json`. Script reference data is kept in `preparation/fixtures/`. Earlier unneeded import records and the unused review template are preserved separately in `course/evaluation/chapter-14-preparation-history/`.

Read [the exercise](exercise.md) and keep [the solutions](solutions/answers.md) separate until the learner finishes.

## Learner setup — complete once before the exercise

Start with **Chapter 4: Course Setup**, using [Local laptop setup](../../../app/LOCAL-SETUP.md). The standard local Langfuse services and the application backend image must already be available. This chapter imports supplied answers; it does not require a new model answer, a funded judge model, a cloud account or a marketplace database reset.

Run the shell commands below from the **repository root** (the directory containing `app/` and `course/`). Keep your own Langfuse project credentials configured for the import container. The standard local Compose configuration already supplies its demo project credentials; do not copy the instructor's hosted-project keys.

### 1. Enable the local TypeScript dispatcher

The supplied [Compose overlay](compose.code-eval.yaml) enables code evaluators on the web service and worker, including the worker execution queue:

```sh
docker compose -p marketplace-lab \
  -f app/compose.yaml \
  -f course/exercises/evaluation/compose.code-eval.yaml \
  up -d --no-deps langfuse-web langfuse-worker

docker compose -p marketplace-lab \
  -f app/compose.yaml \
  -f course/exercises/evaluation/compose.code-eval.yaml \
  ps langfuse-web langfuse-worker
```

Both services must be running before proceeding. This recreates only these two services if configuration changed, preserving their volumes and existing records. It does not restart marketplace services or reset business data. Dependencies must already be running from Course Setup. If you use custom Langfuse overlays, include those too rather than discarding your configuration.

This overlay selects `insecure-local`: it executes trusted TypeScript in the worker process, **not an isolation boundary for untrusted code**. Use only the supplied reviewed evaluator on your local lab. Python evaluation and production isolation are separate deployment choices. The overlay must be included whenever you later recreate these services for this lab; the general startup command does not automatically include it.

### 2. Create the evaluator in your own project

1. Open local Langfuse and select your course project (`marketplace-support` in standard setup).
2. Open **Evaluators → New evaluator → Code evaluator → TypeScript**.
3. Name it **Chapter14 structured order comparison**. If your project already has this evaluator, inspect/reuse it instead of creating a duplicate.
4. Paste the complete supplied [structured-evaluator.ts](structured-evaluator.ts) into the code editor and save. Do not paste the JSON fixture as evaluator code. UI labels may vary with version.
5. Create or attach an observation rule with **Name equals `chapter14-structured-answer`**, sampling **100%**, and this evaluator. Enable it before the structured import in the exercise. Use your own local project; in a shared project add filters supported by that installation to limit the rule to your lab data, or ask the project owner to provide an isolated project.

The code reads the answer from `ctx.observation.output`. Its reference comes from the experiment expected output, falling back to the observation metadata's `expected_output`. The supplied importer records both source facts and provenance. There is no separate LLM judge or prompt-variable mapping to configure.

### 3. Prepare the human worksheet and check the import path

```sh
mkdir -p app/results/chapter-14
cp -n course/exercises/evaluation/fixtures/human-worksheet.json \
  app/results/chapter-14/human-worksheet.json

docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation \
  run --rm --no-deps \
  -v "$PWD/course/exercises/evaluation:/exercise:ro" \
  eval-runner python /exercise/upload_structured_answers.py
```

Keep your existing worksheet if it is already present. The dry run lists three case IDs with `model_calls: 0` and `published: false`; it does not create an experiment. If the backend image is absent, build it once using `docker compose -p marketplace-lab -f app/compose.yaml build backend`, then retry. Do not add a live-judge flag.

### 4. Complete and verify the exercise

Follow [exercise.md](exercise.md): grade/import the five human answers, then import the three supplied structured answers. Open the printed experiment URL. In the evaluator editor, select a newly imported `chapter14-structured-answer` observation and run its test; inspect the actual answer/reference and returned field checks.

Verify that each of the three items subsequently has native scores with source **EVAL**. An imported experiment or a successful editor test alone is not proof that the asynchronous rule scored every item. If you created the rule after importing, use batch evaluation on only your matching imported observations, or import a new uniquely named run after enabling the rule. Avoid duplicate rules and repeated imports while merely waiting for a queued job.

### Troubleshooting and cleanup

- **Code evaluator absent:** confirm the overlay was applied to both web and worker; refresh Langfuse. Keep the pinned course images unless deliberately testing an upgrade.
- **No native scores:** check the rule is enabled, name filter and sampling, then worker status. Inspect evaluator execution errors (the `langfuse-code-eval` environment) before rerunning imports.
- **Not assessable:** inspect expected-output context/metadata and confirm you imported the supplied fixture with the chapter script.
- **Authentication failure:** the import container's project keys must belong to the selected local project. Do not put keys into the worksheet, evaluator source or submissions.
- To disable local execution after finishing, disable only your own rule and recreate the two Langfuse services with your normal Compose files, omitting this chapter overlay. Retain your datasets/results for review. Never use `down -v` or reset the marketplace to clean up this exercise.

**Verification boundary:** the instructor's native workflow passed previously. These written setup steps have been checked against the tracked overlay, importer, evaluator and current official documentation; they are not yet a fresh-project UI/installation rehearsal.

References: [Langfuse self-hosted dispatcher setup](https://langfuse.com/self-hosting/configuration/code-evaluators), [creating and testing code evaluators](https://langfuse.com/docs/evaluation/evaluation-methods/code-evaluators) (checked 15 October 2026).

## Optional preparation scripts

From the repository root, inspect the five-case selection without model calls:

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation run --rm --no-deps -v "$PWD/course/exercises/evaluation:/exercise:ro" eval-runner python /exercise/run_claude_demo.py
```

To import the verified teaching grades with model metadata, append `--import-verified --publish` and a unique `--run-name`. This makes no candidate or judge calls. `--replay-saved` separately preserves older historical Claude v3 judgments; those differ from the teaching run.

For a fresh five-case Claude demonstration:

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation run --rm --no-deps -v "$PWD/course/exercises/evaluation:/exercise:ro" eval-runner python /exercise/run_claude_demo.py --live-judge --publish --run-name chapter14-claude-five --output /results/chapter-14/claude-demo.json
```

The existing `eval-runner` reads the restricted judge key from the configured application environment. It makes at most five judge requests, generates no candidate answers and never automatically retries. Results are saved after each call. Invalid or truncated grades stop the run; missing cost reporting stops further paid calls. The default dollar threshold is checked after each completed response, so it can stop subsequent requests but cannot undo or cap the in-flight call. Re-running a stopped live command starts a new paid attempt; inspect the saved file first.

Local Langfuse API keys remain in the application environment and are not part of the fixtures or output package. No new credentials or wider gateway permissions are needed.

## Validation

The fresh five-case Claude workflow, external result publication, human-grade publication using labelled historical judgments, and native structured workflow have been exercised locally. Four offline tests check blind judge payloads, grade validation and the supplied structured records. The historical comparison, fresh five-case teaching run, and native structured results retain separate provenance.

Original model execution traces hold model usage, timing and gateway costs. A saved-answer import's zero model cost means the import made no model call; it is not the cost of producing the original answer.
