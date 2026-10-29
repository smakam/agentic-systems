# Evaluation contract

Expected answers and fixtures are evaluator-only inputs. Do not mount them into the interactive backend or index them as retrieval content. The full fixture pool is [app/eval/cases.json](app/eval/cases.json); smaller suites have their own manifests and expected results.

For each comparison, preserve the question, fixture version, source/configuration, model, prompt, tool policy and conversation boundary. Record completed and failed attempts. Keep candidate answers, structured checks, provisional judge grades and human decisions separate. A query replay proves execution fidelity, not that the agent chose the correct query.

Use isolated evaluation data and the runner's reset guards. Do not reset interactive data. Cost budgets are estimated usage stopping thresholds, not provider billing caps. Interrupted runs and unknown usage need explicit accounting before retrying.

Compare quality, cost and latency together, stating the sample size, grading provenance and caching basis. Saved-answer routing replay is distinct from a live agent conversation. Demonstration results do not establish a production model or routing policy.

[Runner instructions](app/eval/README.md) · [Course evaluation exercise](course/exercises/evaluation/exercise.md) · [Model comparison data](course/evaluation/chapter-14-model-comparison/README.md)
