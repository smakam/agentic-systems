# Responsible AI evaluation resources

Companion catalog for **Evaluating Responsible AI**, in the Responsible AI and AI Governance for Agents series. Use it to choose resources by the behavior you want to evaluate.

## Benchmarks and guidance by lens

| Lens | Resource | What it helps you evaluate |
| --- | --- | --- |
| Safety | [XSTest](https://ukgovernmentbeis.github.io/inspect_evals/evals/xstest/) | Whether a model declines harmful requests and answers harmless ones. |
| Safety | [Stanford HELM Safety](https://crfm.stanford.edu/helm/safety/latest/) | Published model comparisons across selected safety risks. |
| Safety | [MLCommons AILuminate Safety](https://mlcommons.org/ailuminate/safety/results/) | Published model safety results across hazard categories. |
| Security | [OWASP GenAI Top 10](https://genai.owasp.org/llm-top-10/) | Application risks to consider when defining controls and expected behaviors. |
| Security | [AgentDojo research overview](https://arxiv.org/abs/2406.13352) | How a fixed simulated harness measures task completion and agent behavior under untrusted inputs. |
| Values | [MASK](https://github.com/centerforaisafety/mask) and [Scale’s MASK leaderboard](https://labs.scale.com/leaderboard/mask) | Honesty under pressure. Check the evaluation split and setup before comparing scores. |
| Values | [AA-Omniscience](https://artificialanalysis.ai/evaluations/omniscience) | Factual reliability and abstention. |
| Values | [BBQ](https://github.com/nyu-mll/BBQ) | Bias in question answering when the evidence is ambiguous or informative. |

## Frameworks, runners and published results

- [NIST AI Risk Management Framework](https://www.nist.gov/itl/ai-risk-management-framework) for organizing risk management.
- [Inspect AI](https://inspect.aisi.org.uk/) for structuring an evaluation and recording its evidence.
- [COMPL-AI](https://github.com/compl-ai/compl-ai) for examples of mapping governance requirements to technical measures.
- [CAIS Risk Index](https://dashboard.safe.ai/#safety) for comparing selected risk measures. Check which components were scored for each model.

## From the lesson pilot

| Setup | Saved evidence |
| --- | --- |
| Direct model calls | [Direct-model runner](https://github.com/smakam/agentic-systems/blob/2c224e9e1a15a64816b1cebc48ec28d34da44b1f/evaluations/responsible-ai-pilot/run_model_cases.py) and [results and rubric decisions](https://github.com/smakam/agentic-systems/blob/2c224e9e1a15a64816b1cebc48ec28d34da44b1f/evaluations/responsible-ai-pilot/model-summary.md) |
| Fixed agent harness | [AgentDojo pilot results](https://github.com/smakam/agentic-systems/blob/2c224e9e1a15a64816b1cebc48ec28d34da44b1f/evaluations/responsible-ai-pilot/agentdojo-summary.md) |
| Marketplace support agent | [Marketplace pilot results](https://github.com/smakam/agentic-systems/blob/2c224e9e1a15a64816b1cebc48ec28d34da44b1f/evaluations/responsible-ai-pilot/marketplace-summary.md) |

Published results can help shortlist models. For deployment, test the behaviors that matter in your application and inspect both the answer and evidence from the run. The pilot illustrates the evaluation method with a small set of cases.
