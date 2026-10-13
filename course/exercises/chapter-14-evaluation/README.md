# Chapter 14 evaluation package

[Full 18-case human/Claude comparison](../../evaluation/chapter-14-model-comparison/README.md)

This package separates three grading methods and two integration paths:

- **Instructor:** Claude judges five supplied answers externally, then the script publishes the scores to Langfuse. Native Langfuse code evaluation demonstrates three already verified structured answers.
- **Learner:** Human-grade five supplied answers and import their grades. Import five supplied structured outputs and let the native Langfuse worker perform field comparisons.

The learner exercises make no model API calls. Candidate answers and golden references are supplied. Instructor live Claude judging is paid and requires an explicit flag. Preparing the package generated the five structured answers once, outside learner execution.

Read [the exercise](exercise.md) and keep [the solutions](solutions/README.md) separate until the learner finishes.

## Instructor script

From the repository root, inspect the five-case selection without model calls:

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation run --rm --no-deps -v "$PWD/course/exercises/chapter-14-evaluation:/exercise:ro" eval-runner python /exercise/run_claude_demo.py
```

For a recording rehearsal using saved Claude assessments, append `--replay-saved --publish`. This produces no candidate or judge calls. Its grades remain explicitly labelled historical replay.

For a fresh five-case Claude demonstration:

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation run --rm --no-deps -v "$PWD/course/exercises/chapter-14-evaluation:/exercise:ro" eval-runner python /exercise/run_claude_demo.py --live-judge --publish --run-name chapter14-claude-five --output /results/chapter-14/claude-demo.json
```

The existing `eval-runner` reads the restricted judge key from the configured application environment. It makes at most five judge requests, generates no candidate answers and never automatically retries. Results are saved after each call. Invalid or truncated grades stop the run; missing cost reporting stops further paid calls. The default dollar threshold is checked after each completed response, so it can stop subsequent requests but cannot undo or cap the in-flight call. Re-running a stopped live command starts a new paid attempt; inspect the saved file first.

Local Langfuse API keys remain in the application environment and are not part of the fixtures or output package. No new credentials or wider gateway permissions are needed.

## Validation

The fresh five-case Claude workflow, external result publication, human-grade publication using labelled historical judgments, and native structured workflow have been exercised locally. Four offline tests check blind judge payloads, grade validation and the supplied structured records. The historical comparison, fresh five-case teaching run, and native structured results retain separate provenance.

Original model execution traces hold model usage, timing and gateway costs. A saved-answer import's zero model cost means the import made no model call; it is not the cost of producing the original answer.
