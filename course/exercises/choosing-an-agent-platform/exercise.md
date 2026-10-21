# Choosing an Agent Platform — learner exercise

## Workspace and goal

Use the chapter slides, your browser and this worksheet. No new cloud account, deployment, programming or paid model calls are required. Allow about 30–45 minutes. Keep [reference answers](solutions/answers.md) closed until you finish.

Recommend a platform approach for an enterprise agent by comparing **two plausible options** against the same requirements. Choose a task from your work, or use this fictional scenario:

> An internal support team needs explanations of order and payout status, grounded in current business records and policy evidence. Business tools must enforce read-only access and user permissions. The team wants follow-up questions, observable failures and manageable maintenance. It already operates a cloud application. You decide the remaining constraints and success targets; do not invent measured platform results.

## 1. State the requirements

Copy the template below into your submission. Make assumptions explicit.

| Requirement | Your answer |
|---|---|
| Users, task and successful outcome | |
| Business records/policy evidence and freshness | |
| Unacceptable failures and backend access controls | |
| Quality and latency targets; how you would measure them | |
| Deployment, processing locations and retention constraints | |
| Model/framework requirements and existing cloud/tooling | |
| Team skills, maintenance capacity and spending limits | |

Separate hard constraints from preferences. “We need private deployment” must identify which components and processing must stay private, including external model calls and telemetry.

## 2. Shortlist two options

Use the chapter's flowchart to identify the relevant provider type: **cloud-provider platform**, **model-provider platform**, **framework-associated platform**, or **integrated builder**. A self-managed SDK/framework is also a valid baseline.

Name the actual product/deployment path for each option, not just its parent company. Explain why each meets the hard constraints and deserves comparison. Different options can belong to the same provider type. Use the two official product pages most relevant to your choices for a brief documentation check; this is not a broad market-research assignment. Record the access date and any edition/region restrictions.

## 3. Compare the responsibilities and costs

Fill one row per area; use short phrases. “Unknown” is acceptable when followed by a way to resolve it. A feature you have not tested is not necessarily unavailable.

| Area | Option A: supplier, our work and limits | Option B: supplier, our work and limits |
|---|---|---|
| Agent loop/instructions/code and model access | | |
| Runtime hosting, scaling and recovery | | |
| Sessions, context and long-term memory | | |
| Business tools/MCP, authorization and data access | | |
| Knowledge ingestion/retrieval and cited evidence | | |
| Traces, monitoring, evaluations and guardrails | | |
| Deployment, data processing and retention | | |
| Usage charges, licenses and team cost | | |

Keep the application-to-runtime interface stable through an adapter where practical. Consider MCP at the business-tool boundary, while preserving backend authorization; a common protocol does not make identity or session semantics identical across products.

Include model inference, runtime, storage/memory, tools/networking, observability/evaluation and subscriptions where applicable. Explicitly include development, integration, **maintenance** and on-call work. Exact prices are optional; list the billing drivers and cost assumptions.

For the claims that determine your choice, record a source/date and whether the claim is documented, observed in a bounded course lab, your assumption, or still unknown. Do not rank providers using different models, prompts, datasets or memory policies as if those were controlled benchmarks.

## 4. Recommend and define the smallest useful trial

Write a short recommendation: pick one option, explain the deciding tradeoff and name one condition that would change your choice.

Design (do not execute) a small comparison using the same questions, business facts, tool permissions and quality rubric. Include:
- A known-record question and a same-session follow-up.
- A missing-record question and an unauthorized-access attempt.
- Evidence/citation checks, trace visibility, latency and total cost.
- Fresh-session memory checks only if your requirements need durable memory; verify stored/retrieved evidence rather than answer style alone.
- Explicit acceptance criteria, remaining unknowns and the next validation step.

If a model or tool cannot be held constant, record the difference and limit your conclusion. Optional replay of an earlier course lab must use that chapter's setup, workspace and cleanup instructions.

## Submit

Submit a one- or two-page decision (compact tables are fine): requirements, two named options, responsibility/cost comparison, two dated official references, recommendation and trial plan. No deployment, credentials, customer data or screenshots of private account settings are required.

## Self-check

Can another team member explain why you chose this option, what your team must still build/operate, what remains uncertain, and what evidence could change the decision? There is no universal winning platform.
