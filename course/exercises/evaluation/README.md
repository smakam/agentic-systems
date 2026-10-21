# Evaluation

Start with [exercise.md](exercise.md). It contains both the [instructor demo](exercise.md#instructor-demo) and the [learner exercise](exercise.md#learner-exercise), including creating the evaluator in your own Langfuse project.

## Files to open

| File | What you do with it |
| --- | --- |
| [exercise.md](exercise.md) | Follow the instructor walkthrough or learner steps |
| [human-worksheet.json](human-worksheet.json) | Enter five scores and reasons |
| [structured-evaluator.ts](structured-evaluator.ts) | Copy the supplied grading code into Langfuse |
| [structured-three.json](structured-three.json) | Inspect the three supplied structured answers |
| [solutions/answers.md](solutions/answers.md) | Compare after completing the exercise |

Only edit the worksheet's score and reason fields. No new model calls are required.

## Supporting folders

- `scripts/`: validation and upload commands used by the guide; no learner code edits.
- `setup/`: the Compose overlay enabling the local code evaluator; the guide gives the command.
- `preparation/`: optional instructor/developer material and script reference data; skip for the learner activity.
- `tests/`: developer checks; skip for the learner activity.
- `solutions/`: separate worked answers and supporting saved results.

[Full 18-case human/Claude comparison](../../evaluation/chapter-14-model-comparison/README.md)
