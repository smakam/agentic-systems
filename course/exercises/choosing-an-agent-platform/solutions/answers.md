# Chapter 21: Choosing an Agent Platform — reference answers

Read after completing [the exercise](../exercise.md). This is an illustrative decision and review rubric, not a universal provider ranking or a new benchmark.

## Example requirements and shortlist

Assume an internal support agent with read-only order/payout tools, current policy citations and same-session follow-ups. The application and business data already run in Google Cloud; a small team prioritizes reduced hosting work. There is no on-premises-only requirement. Durable personal memory is optional and is excluded from the initial acceptance trial. The team must set a latency target and spending ceiling based on its actual workload.

Two plausible options:
- **OpenAI Agents SDK on the team's own cloud application hosting:** retain the framework's loop/session capabilities and operate the hosting and surrounding integrations.
- **Google-managed Agent Runtime hosting the team's agent:** use managed hosting and selected platform services while retaining the team's instructions/code, business tools and backend permissions.

These are candidate paths from the course, not claims that either automatically satisfies every account, model, residency or retention requirement. Check the selected path in current official documentation: [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/) and [Google Agent Runtime](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build/runtime/quickstart). Record your own access date and any restrictions; course observations are not a substitute for current product checks.

## Example comparison

| Area | Self-hosted SDK approach | Managed runtime approach |
|---|---|---|
| Agent behavior | Team owns instructions, code, business tools and testing; SDK supplies framework capabilities | Team still owns instructions/code, business tools and testing |
| Hosting and operations | Team provisions/operates hosting, scaling and recovery | Managed hosting reduces that infrastructure work; team still configures IAM, deployment and limits |
| State and memory | Configure session persistence and integrate durable memory if required | Select/configure platform state/memory services; verify scope, retention and any explicit generation step |
| Business data and security | Existing backend enforces read-only permissions; runtime adapter calls business tools | Same backend responsibility; secure the hosted agent's tool connection |
| Observability/evaluation | Connect instrumentation and evaluation workflow; team maintains integrations | Configure available platform telemetry/evaluation and business-level acceptance checks |
| Cost | Inference, hosting, persistence, other services and engineering/on-call work | Inference, managed runtime/state/other configured services and engineering/operations work |
| Open questions | Hosting overhead and integration maintenance at the team's workload | Account/model/location eligibility, permissions, processing/retention and total usage charges |

Either can use a consistent application contract and business MCP tools. Backend authorization remains necessary. Avoid claiming that self-hosting the agent automatically keeps external inference/telemetry local, or that managed services remove all integration work.

## Example recommendation and trial

Provisionally choose the managed runtime because the assumed team already uses Google Cloud and values reduced hosting work. Reconsider if a hard model/location requirement is unsupported or the measured operating/cost tradeoff favors the existing SDK deployment. A team with established hosting and custom integrations could reasonably choose the SDK instead.

Use the same order/payout facts and tool authorization in both candidates. Inspect correct-record answers, a follow-up, missing records and access denial; require evidence-supported answers and no unauthorized business read. Verify that traces identify the model/tool/error path. Compare measured response times and cost per accepted task against the team's declared targets. Include integration and maintenance effort. Do not invent trial measurements. Hold model/prompt/context constant where possible and disclose differences.

The next step is a bounded trial using fictional data in authorized environments, after resolving model/location/retention and IAM uncertainties. No new deployment is required for this worksheet submission.

## What a good submission shows

- Concrete requirements, hard constraints and a feasible two-product shortlist.
- Clear ownership of application behavior, tools, data access and platform operations.
- Dated official sources for decisive claims, with assumptions and unknowns visible.
- Total costs including development, integration, maintenance and on-call duties.
- A recommendation tied to the stated priorities and a condition that would change it.
- A comparable, measurable trial plan with quality, security and operational checks.

Alternative choices—AWS/Microsoft, model-provider platforms, LangSmith/CrewAI, Lyzr/Dify or another supported framework—are valid when justified against the same requirements. “Integrated platform” does not establish feature parity. Different course fixtures/models are bounded learning evidence, not a controlled quality leaderboard.
