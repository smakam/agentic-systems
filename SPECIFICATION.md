# Marketplace support lab architecture

The application uses synthetic marketplace data to make agent behavior inspectable. A learner changes a component or setting, repeats a scenario and compares answers, tool evidence, traces, quality, latency and cost.

## Runtime responsibilities

- The browser provides marketplace views, a Support workspace and experiment controls.
- The application backend authenticates requests, preserves conversation state, selects the configured runtime and returns answers with evidence.
- The OpenAI Agents SDK path runs the agent loop; a shared LiteLLM gateway handles configured provider/model access. Optional Google and Lyzr runtimes have separate setup and execution boundaries.
- Read-only business tools expose catalog/schema, bounded SQL, document retrieval, evidence and order history through MCP. An investigation groups business reads and evidence; model text is not an authorization source.
- PostgreSQL owns synthetic business records and application state. Retrieved policy/document evidence is distinct from current transactional truth.
- Optional memory, routing, guardrails and orchestration labs change specific behavior. They do not convert remembered facts or model claims into trusted identity or current business evidence.
- Langfuse provides tracing and evaluation telemetry when configured. Local experiment outputs retain their own source, fixture and grading provenance.

## New capability boundaries

- [MCP authentication](app/docs/MCP-AUTHENTICATION.md): shared-key support access, delegated buyer/seller order access, and service-authenticated simulated Test payouts. Identity providers issue credentials; backend ownership, scope and business rules decide permitted actions. Marketplace web sign-in is a separate integration.
- [A2A](app/docs/A2A-MARKETPLACE.md): protocol adapters expose the support agent and a separately managed simulated delivery agent. The existing marketplace session/CSRF rules and conversation ownership remain in force; a common interface does not remove the access boundary.
- [Agentic UI](app/docs/AGENTIC-UI-DEMO.md): a presentation stage reuses a completed investigation for controlled, declarative or generated views. MCP Apps supplies the local host/provider boundary for the declarative example. Requesting history starts new backend work; changing only presentation does not rerun the business investigation. AG-UI is explained, not integrated.

These capabilities are in `main`, but enabling local/Test services is separate from deployment. The baseline cloud path does not automatically configure the identity lab, isolated UI teaching host or delivery experiment. Follow each guide's workspace and configuration requirements.

## Learning paths and contracts

[Local Setup](app/LOCAL-SETUP.md) is the primary lab path; [Cloud Setup](app/CLOUD-SETUP.md) describes the optional deployment. [Runtime selection](app/RUNTIME-SELECTOR.md) explains the boundary between application hosting and agent execution. [User journeys](app/USER-JOURNEYS.md) describe business behavior.

[Exercises](course/exercises/README.md) cover first-agent behavior, models/gateways, tools/MCP, prompt/context, retrieval, sessions, loops, observability, evaluation, security, routing, design patterns, memory and platforms. Each experiment should preserve the scenario and fixture, record the changed setting, inspect evidence and state its limits.

[Evaluation contracts](EVALUATION-SPEC.md) keep expected answers outside the interactive agent. Scores are sample-specific observations; historical classifier replay and live agent tests are different experiments. There is no universally recommended production model or routing policy.

The detailed chronological development plans are retained in the instructor archive, outside the learner repository. This page describes the current teaching architecture rather than that history.
