# Two company requirements briefs

These are fictional learner cases, separate from the three worked examples in the slides. Requirements below are inputs to a decision, not measured vendor results. Recommend a product and deployment path, not just a provider category.

## Company D — an existing graph-based agent

A software team has a working Python support-investigation agent built with LangGraph. It has explicit workflow branches, checkpoints and read-only business tools. The team wants to retain that code and its business backend while adding managed deployment and an inspection/evaluation workflow. It has two engineers for the application, but no dedicated runtime operations team.

**Required:** preserve the graph behavior and business-tool authorization; support stateful runs and inspect failures; use approved cloud hosting and compatible model access. Customer records may be processed only under an approved region/retention agreement. The team can accept a subscription if it reduces integration and on-call work.

**Preferences:** keep the existing graph code and developer workflow; avoid rewriting into a visual builder. This is a preference unless you identify a genuine compatibility blocker.

**Decision:** Which two products/deployment paths would you shortlist? Which would you try first, and what must be verified before adoption?

## Company E — a model-provider research assistant

A research-services company already uses Claude and has approved that provider for its data. It wants an assistant that can perform long-running, asynchronous research tasks with file/web tools and a read-only MCP connection to internal evidence. A small team prefers a provider-managed harness and runtime to building its own loop. There is no requirement to run the entire agent platform on premises.

**Required:** tool permissions and evidence-supported output; resumable/inspectable work; usage limits; acceptable session/event retention and regional/data-processing terms. A beta offering is acceptable for a limited pilot, but production use needs a separate approval.

**Preferences:** reuse the existing model-provider relationship and minimize custom runtime operations. Model/provider switching is a useful option, not a hard requirement.

**Decision:** Compare a suitable managed-harness product with a plausible framework/runtime alternative. Which would you pilot first, and what result or restriction would change your recommendation?

## Shared boundaries

- The application team owns business permissions, source freshness and acceptance criteria in both cases.
- A managed service still needs configuration, integration and validation.
- Neither case guarantees one correct vendor. A defensible alternative is valid if it meets the requirements and explains its tradeoffs.
- Do not deploy, purchase a plan, submit credentials or use private customer data for this exercise.
