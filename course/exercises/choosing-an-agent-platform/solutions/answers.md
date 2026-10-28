# Choosing an Agent Platform — reference answers

Read after completing [the exercise](../exercise.md) using the [requirements briefs](../requirements.md). These are illustrative decisions, not unique correct answers, customer case studies or measured vendor rankings. Documentation checked 28 October 2026; recheck the selected edition, region and terms.

## Company D — existing graph-based agent

**Deciding requirements:** retain LangGraph behavior and read-only business tools; gain managed deployment and inspectable stateful runs; keep operating effort manageable for a small engineering team. Region, retention and model compatibility are adoption gates.

**Plausible shortlist:** LangSmith Deployment with the existing LangGraph application, versus Google Agent Platform Runtime hosting compatible agent code. Both are actual product/deployment paths; do not compare a framework library with a whole platform without accounting for the missing hosting and integrations.

**Provisional recommendation:** pilot LangSmith Deployment because it aligns with the existing graph code and developer workflow while supplying deployment infrastructure. This is a fit inference from the stated requirements, not proof that it is cheaper or better than Google. Google remains plausible if its cloud operating model, deployment compatibility and total cost fit better. LangSmith Deployment and LangSmith observability/evaluation are related but distinct services; map their placement and charges separately.

**What the team still owns:** graph logic, tool integration, business authorization, identity/session scope, evidence freshness, configured recovery and acceptance tests. For managed hosting, confirm the eligible plan and approved location/data flows rather than assuming all features are included.

**Trial:** run the same known-order investigation, follow-up, unknown record, denied access and interrupted/resumed run. Compare evidence correctness, graph/checkpoint behavior, trace visibility, response time, cost and integration effort. Do not invent results. Reverse the recommendation if a hard region/retention requirement fails, compatibility requires a major rewrite, or another option meets the same requirements with a better total ownership tradeoff.

Official references:
- [LangSmith Deployment](https://docs.langchain.com/langsmith/deployment): deployment environments, Agent Server and framework support.
- [Google Agent Runtime quickstart](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/quickstart): verify the exact supported code/deployment path.

## Company E — model-provider research assistant

**Deciding requirements:** long-running asynchronous research, a managed harness/runtime, existing Claude relationship, authorized file/web/MCP tools, inspectable sessions and usage controls. The pilot may use beta, but retention, data-processing terms and production approval remain gates.

**Plausible shortlist:** Claude Managed Agents with an approved environment, versus a custom/framework agent using Claude on the team's chosen managed runtime. For the latter, name the specific framework/runtime pair and include the loop, tool execution, persistence and integration work the team must supply.

**Provisional recommendation:** pilot Claude Managed Agents because its documented managed harness and asynchronous-work focus match this team's priorities and existing model-provider relationship. This is not a universal recommendation and does not establish suitability for the company's retention/region requirements. Verify the current beta/service terms before proceeding to production.

**What the team still owns:** research instructions, evidence quality, tool scope and backend authorization, permitted network access, budgets, session ownership, review and operational acceptance. A self-hosted sandbox does not mean the whole provider harness/control plane runs locally; confirm every relevant data path.

**Trial:** use the same bounded research brief, allowed sources and evidence rubric. Inspect permission enforcement, citations, missing/conflicting evidence, interruption/resume, errors, usage and total cost. Compare the custom alternative's quality and operating effort. Reverse the recommendation if beta is unacceptable, required data handling is unsupported, or custom control/model portability becomes a hard requirement.

Official references:
- [Claude Managed Agents overview](https://platform.claude.com/docs/en/managed-agents/overview): managed harness, asynchronous work, environments, tools and beta status.
- [Claude Managed Agents permission policies](https://platform.claude.com/docs/en/managed-agents/permission-policies): verify the exact policy and tool controls for the chosen configuration.

## Cost and ownership rubric for both cases

| Category | Include |
|---|---|
| Models | Inference, embeddings and evaluation model calls |
| Infrastructure | Compute, databases, storage and networking |
| Core agent platform | Execution, orchestration, sessions and memory services |
| Supporting services | Evaluation, guardrails, monitoring, tracing and logging; native or external |
| Team | Development, integration, maintenance and on-call support |

Runtime or storage may be bundled with the platform or billed separately. Count each charge once. Place licenses/subscriptions under the service they pay for. A small inference bill alone does not establish low total cost.

## Review rubric

Accept alternatives that satisfy the hard requirements, name a feasible product/deployment path, use current official evidence and explain the deciding tradeoff. A good submission distinguishes documented capability from observed results, states unknowns, identifies business/operating ownership, includes a reversal condition and proposes a comparable measurable trial. Brand names alone, invented performance scores, or assumptions that managed services eliminate authorization and operations are insufficient.
