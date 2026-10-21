# Optional instructor and developer preparation

Learners can ignore this folder. Follow [the main activity guide](../exercise.md) for the instructor demo and learner exercise. Run these commands from the repository root. Do not run paid judging merely to inspect saved results.

## Optional preparation scripts

From the repository root, inspect the five-case selection without model calls:

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation run --rm --no-deps -v "$PWD/course/exercises/evaluation:/exercise:ro" eval-runner python /exercise/scripts/run_claude_demo.py
```

To import the verified teaching grades with model metadata, append `--import-verified --publish` and a unique `--run-name`. This makes no candidate or judge calls. `--replay-saved` separately preserves older historical Claude v3 judgments; those differ from the teaching run.

For a fresh five-case Claude demonstration:

```sh
docker compose -p marketplace-lab -f app/compose.yaml --profile evaluation run --rm --no-deps -v "$PWD/course/exercises/evaluation:/exercise:ro" eval-runner python /exercise/scripts/run_claude_demo.py --live-judge --publish --run-name chapter14-claude-five --output /results/chapter-14/claude-demo.json
```

The existing `eval-runner` reads the restricted judge key from the configured application environment. It makes at most five judge requests, generates no candidate answers and never automatically retries. Results are saved after each call. Invalid or truncated grades stop the run; missing cost reporting stops further paid calls. The default dollar threshold is checked after each completed response, so it can stop subsequent requests but cannot undo or cap the in-flight call. Re-running a stopped live command starts a new paid attempt; inspect the saved file first.

Local Langfuse API keys remain in the application environment and are not part of the fixtures or output package. No new credentials or wider gateway permissions are needed.

## Validation

The fresh five-case Claude workflow, external result publication, human-grade publication using labelled historical judgments, and native structured workflow have been exercised locally. Four offline tests check blind judge payloads, grade validation and the supplied structured records. The historical comparison, fresh five-case teaching run, and native structured results retain separate provenance.

Original model execution traces hold model usage, timing and gateway costs. A saved-answer import's zero model cost means the import made no model call; it is not the cost of producing the original answer.
