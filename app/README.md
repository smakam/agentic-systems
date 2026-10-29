# Fieldwork — marketplace and support-agent lab

Start with [Local Setup](LOCAL-SETUP.md). The guide covers configuration, service startup, health checks and shutdown. Application commands run from this directory. For optional hosted work, use [Cloud Setup](CLOUD-SETUP.md).

## Learn through controlled experiments

Choose a scenario in the [exercise index](../course/exercises/README.md), record your current settings and run it. Change one capability, repeat the scenario and inspect tool evidence and traces before comparing quality, latency or cost. Keep business fixtures and conversation state consistent when making comparisons.

[Architecture](../SPECIFICATION.md) · [User journeys](USER-JOURNEYS.md) · [Runtime selector](RUNTIME-SELECTOR.md)

## Capability guides

- [Prompt and catalog](docs/PROMPT-AND-CATALOG.md) and [retrieval/policy evidence](docs/RAG-POLICY-DEMO.md)
- [Guardrails and security](docs/GUARDRAILS-MANUAL.md), [security boundaries](docs/SECURITY-BOUNDARY-DEMO.md), and [OWASP mapping](docs/OWASP-SECURITY-MAP.md)
- [Memory status and boundaries](docs/MEMORY-STATUS.md) and [Mem0 integration](docs/MEM0-INTEGRATION.md)
- [Evaluation fixtures and runners](eval/README.md)
- [Google runtime](google/README.md) and [Lyzr paths](lyzr/README.md)
- [Contribution workflow](../course/CONTRIBUTING.md)

## Data and credentials

Use your own private `.env` file and provider credentials. Seed data is synthetic. Interactive, test and evaluation databases have different purposes; follow the specific runner's reset safeguards. Do not run a reset or integration test against a workspace you want to preserve. Generated results are local outputs, not part of the learner checkout.

Runtime availability depends on completed setup, accounts and provider access. Optional integrations and historical demonstration scores have bounded verification; inspect the relevant guide and record any adaptation you make.
