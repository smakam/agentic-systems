# Research guide: AI systems decisions, evidence and counterevidence

**Published routing series — September 30, 2026:** [Part 1: classification](https://sreeni.blog/2026/09/30/model-routing-part-1-choosing-a-classifier/) · [Part 2: scope](https://sreeni.blog/2026/09/30/model-routing-part-2-choosing-the-scope/). See the [publication index and synchronized local copies](blog/model-routing/README.md) and [M23 publication milestone](MILESTONE-LOG.md#m23--publish-routing-series-and-synchronize-documentation). Both posts are published; this editorial update changes no application requirements, experiment scores or production routing.

**Framing for the blog/course:** These experiments teach how to evaluate model choice, classification and routing granularity for a use case; they do not prescribe a winning configuration. The 18-case and six-conversation samples are diagnostic demonstrations, not sufficient evidence for general recommendations. Read the [user-confirmed editorial framing and decision process](EVALUATION-SPEC.md#editorial-framing-teach-the-decision-process) before writing about the results.


**Reviewed:** 27 September 2026. **Companion:** [Application and experiment specification](SPECIFICATION.md).

**Selected baseline:** local OpenAI Agents SDK, one fixed API model through LiteLLM Gateway, Langfuse for evaluation/tracing, simple in-application RAG, and a required ontology/static business relationship map. The marketplace UI changes synthetic business state; the assistant reads it. Products below remain comparison options, not a requirement to install them all. See the specification for current scope and unresolved implementation choices.

This guide supports gradual learning around a working simulated marketplace and its internal support/investigation assistant: first a working single-agent implementation, then optional architecture experiments, idiomatic stack comparisons and blogs. A possible Udemy course is a stretch aspiration, not a current deliverable. It is not a leaderboard of vendors. Sources below were opened during preparation. Research-paper notes are based primarily on their abstracts and bibliographic records; this is an annotated starting guide, not a full-methodology replication review. Before quoting numeric findings in a post, inspect the full paper/report, evaluation setup, version, cost accounting and artifacts. No external result has been reproduced in the reference application.

## How to use the evidence

**Primary research** means the authors' own study, not independent replication of that study. **Independent comparative evidence** means a study evaluates systems or architectural claims across teams rather than only promoting its own product; it can still have benchmark limitations and author interests. **First-party engineering report** means a team's account of its system; results remain vendor-reported unless independently checked. **Documentation/protocol** establishes intended interfaces and capabilities, not measured quality. **Product page** is weaker evidence for detailed control, exportability or performance.

Read one recent research or engineering source, the relevant implementation reference and one challenge to the premise for each topic. Convert each reading into a testable hypothesis on the same business assistant. Maintain a claim ledger with claim, source, source type, date/version, observed scope, limitation and local experiment needed. Record publication/submission date and revision date separately from access date.

**Recency policy:** interpret “after 2025” as **1 January 2026 onward**. The research and engineering reading list in the five topic sections uses dated 2026 sources; older papers and archived protocol versions have been removed. A newer crawl, access date or cosmetic edit does not qualify an old study. A recent paper can still evaluate older models: inspect its model versions and workload before transferring a result.

**Implementation-reference boundary:** Appendix A provides the cross-cutting framework/API directory; each topic below also maps research to relevant tools, frameworks and systems. The date cutoff applies to dated evidence, not to the founding date of an actively maintained project. Unless an explicit update date is given, these pages are undated and do **not** qualify as 2026 research evidence. They establish documented interfaces only. Check package versions and release history when selecting the stack. This separates the dated reading list from living technical manuals without falsely assigning publication dates.

The five main sections match the specification exactly: model routing and gateways; context and memory; evaluation; orchestration; reliable tool use. Retrieval is covered within context and memory and revisited in evaluation/tool use. The cross-cutting framework directory is in Appendix A.

The topic sections use the same structure: **recent research and engineering evidence → tools, frameworks and systems → application experiment**. New implementation references below were checked on 27 September 2026; Appendix A retains its recorded access dates. These are documentation-based comparisons, not hands-on evaluations. System lists are representative and can be narrowed when the initial stack is chosen.

## 1. Model routing and gateways

### 1.1 Recent research and engineering evidence

| Reading, type and date | Why read it | Boundary or contrary test |
|---|---|---|
| [R2-Router: A New Paradigm for LLM Routing with Reasoning](https://arxiv.org/abs/2602.02823v2) — primary research, 2 Feb 2026; revised 29 May 2026; record lists ICML 2026 acceptance | Jointly selects a model and output-length budget. Broadens routing beyond a difficulty label mapped to a model. | Author-reported results on its routing benchmark, not this business assistant. Compare against fixed models and bounded reasoning/output budgets; include classification cost and budget adherence. |
| [LiteLLM JEV classifier integration](https://github.com/BerriAI/litellm/pull/41615) — first-party implementation change, merged 18 Sep 2026 | Concrete source history for adding JEV as a complexity classifier. Distinguish the classification decision from the model/pool configured for its tier. | A merged integration establishes availability in source, not classification quality or the first invention of auto-routing. Pin a release and test false-simple decisions, router latency and total cost. |
| [OpenRouter's new Auto router](https://openrouter.ai/blog/announcements/introducing-the-new-auto-router/) — first-party launch/evaluation report, 10 Aug 2026 | Describes task classification and routing informed by aggregate market spend. Useful as a contrasting service design. | Vendor-reported benchmarks; market spend is an indirect quality signal. This is a newer routing description: do not repeat older NotDiamond descriptions as if they establish the current implementation. Dynamic choices complicate reproducibility. |
| [Cognition: Multi-Agents—What's Actually Working](https://cognition.com/blog/multi-agents-working) — first-party engineering report, 22 Apr 2026 | Its “smart friend” discussion makes escalation and context transfer concrete. | The report also describes a weaker primary failing to know when/how to seek help. Test escalation recall and missed hard cases; do not assume a cheap controller can reliably recognize its limits. |

### 1.2 Tools, frameworks and systems

| System and current primary reference | Supported approach and application fit | What to verify locally |
|---|---|---|
| [LiteLLM Auto Routing](https://docs.litellm.ai/docs/proxy/auto_routing) | Complexity classifiers include heuristics, an LLM, JEV and custom plugins; tiers map to configured models or pools. Separate this from deployment load balancing, retries and fallbacks. | Classifier error, selection overhead, pool policy and escalation. Affinity can skip later classification, so test a simple first turn followed by a hard task. |
| [OpenRouter Auto Router](https://openrouter.ai/blog/announcements/introducing-the-new-auto-router/) | Service routing based on task classification and aggregate market spending, subject to constraints. | Log the actual model on every call. Spending is an indirect signal, not a direct quality evaluation; assess repeatability and behavior when the task changes. |
| [Portkey conditional routing](https://portkey.ai/docs/product/ai-gateway/conditional-routing) | Explicit rules over request metadata, parameters and URL paths. Useful for controlled task/stage policies. | Define the rule or upstream classifier ourselves; this page does not establish automatic quality prediction. Test rule precedence and the default route. |
| [Bedrock intelligent prompt routing](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-routing.html) | Managed predictive routing between supported models within a family. | Check currently supported pairs, quality thresholds and regional availability; do not assume our task labels or arbitrary cross-provider models are supported. |
| [Microsoft Foundry model router](https://learn.microsoft.com/en-us/azure/foundry/openai/concepts/model-router-how-it-works) | Managed model selection with quality/cost-oriented routing modes and supported model pools. | Pin router version and pool; inspect control over model exclusions, affinity and model-choice logging. |

These are representative options, not a market-share ranking or industry standard. Compare routing quality, cost of classification, all downstream attempts, latency and traceability. Keep provider prompt caching separate from gateway response caching; test cold and warm prefixes and task changes. Reusing a session or model does not by itself prove a cache hit.

### 1.3 Application experiment

**Hypothesis to test:** explicit stage selection or bounded escalation can reduce total cost while retaining required quality. **Competing hypothesis:** routing errors and overhead erase savings; a fixed model is the better operating point. A gateway's operational value can still be real even if intelligent model routing loses.

## 2. Context and memory

Terminology for this program: memory specifically means deliberate cross-session retention. Current conversation history and task state remain available with memory off, through explicit application/framework storage and context assembly. Read papers that use broader meanings of “memory” with that distinction in mind. User preferences can be remembered; authoritative business metric definitions remain governed corpus/catalog evidence.

### 2.1 Recent research and engineering evidence

| Reading, type and date | Why read it | Boundary or contrary test |
|---|---|---|
| [Lost in Compaction: Evaluating Side-Constraint Loss under Context Compaction](https://arxiv.org/abs/2608.11242v1) — primary comparative preprint, 31 Jul 2026 | COMPINT examines loss of session constraints during compaction across chat, agent trajectories and research. Directly motivates preserving exclusions and corrections. | Its reported retention rates are specific to tested compactors and prompts. Test our own date restrictions, customer exclusions and evidence pointers before and after compaction. |
| [RAGe: A Retrieval-Augmented Generation Evaluation Framework](https://arxiv.org/abs/2605.27445v1) — primary method preprint, 23 May 2026 | Evaluates domain-specific retrieval/generation components alongside resource telemetry. Useful for comparing chunking, embeddings and retrieval choices. | A framework proposal does not establish a winning configuration. Our SQL/document joins, temporal correctness and citation support still require application-specific gold labels. |
| [MemoryArena: Benchmarking Agent Memory in Interdependent Multi-Session Agentic Tasks](https://arxiv.org/abs/2602.16313v2) — primary benchmark research, 18 Feb 2026; revised 17 Sep 2026; record lists ICML 2026 | Couples retained experience with later actions across interdependent sessions, rather than testing recall alone. | Its environments differ from business analytics. Test whether a retained correction changes the next investigation correctly; also test stale or inappropriate carryover. |

### 2.2 Tools, frameworks and systems

| System and current primary reference | Role and application fit | What to verify locally |
|---|---|---|
| [Mem0](https://github.com/mem0ai/mem0) | Add-on memory layer with open-source SDKs and a managed service. Candidate for retained preferences, corrections and investigation context across sessions. | Extraction and retrieval accuracy; user/agent scoping; correction, deletion and retention semantics; hosting and all model/storage costs. Its April 2026 README explicitly distinguishes managed benchmark results from open-source capabilities. |
| [Letta](https://github.com/letta-ai/letta) | Stateful agent platform with memory integrated into the agent's operation, descended from MemGPT. Candidate for a memory-centric agent implementation. | Inspect who owns the loop, memory writes and context assembly. Adoption can change the harness as well as memory, so it may require an end-to-end stack comparison rather than a clean memory-only ablation. |
| [Graphiti / Zep](https://github.com/getzep/graphiti) | Graphiti is the open-source temporal knowledge-graph engine associated with Zep. Candidate for evolving relationships and dated facts. | Entity resolution, temporal conflict handling, provenance, graph operations and maintenance cost. Do not equate Graphiti with the full managed Zep product or presume a graph is needed. |
| [LlamaIndex](https://developers.llamaindex.ai/python/framework/) and [Haystack](https://docs.haystack.deepset.ai/docs/intro) | Frameworks for retrieval and data/pipeline integration. Candidates for the governed business-document retrieval path. | Chunking, metadata/date filters, reranking, evidence identifiers and retrieval quality. Retrieval over the corpus is distinct from personalized cross-session memory. |
| [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) and the chosen framework's state facilities | Conversation and execution state provide the baseline on which optional memory is added. | Preserve ordinary history/checkpoints when cross-session memory is disabled. Record which context behavior is framework-managed and which is application code. |

A simple application-owned store is also a valid baseline; none of these systems is mandatory. Compare what is written, retrieved, corrected and forgotten; access isolation; trace export; deployment dependencies; integration effort; and total operating cost. A memory product must not silently replace authoritative metric definitions with remembered assertions.

### Practical memory lesson references — October 2, 2026

- [LangChain memory overview](https://docs.langchain.com/oss/python/concepts/memory): short-term state and semantic, episodic and procedural long-term memory; used as a conceptual reference, not a framework migration.
- [OpenAI Agents SDK session-memory guide](https://developers.openai.com/cookbook/examples/agents_sdk/session_memory): session adapters and bounded history; compaction is outside our initial lab.
- [Mem0 quickstart](https://docs.mem0.ai/platform/quickstart): scoped add/search operations and supplying memories as context or agent tools. Optional later integration, not a mandatory production dependency or an implemented local adapter.

Implemented evidence: [M35 explicit memory lab](app/results/memory-v4-2026-10-02/REPORT.md), with initial scoped direct SDK tools and cross-conversation checks; the [October 3 migration](app/results/memory-local-mcp-2026-10-03/REPORT.md) now uses local stdio MCP. [Provider portability design](course/diagrams/MEMORY-ARCHITECTURE.md#provider-portability--proposed-extension) distinguishes MCP runtime access from a planned storage adapter. Mem0 remains a documented alternative, not an implemented provider.

Our [initial lesson scope](course/COURSE-PLAN.md#18-short-term-and-long-term-memory) uses explicit saving and PostgreSQL. Automatic extraction is a separate future experiment so writing the wrong memory can be distinguished from misusing a correctly saved memory.

### 2.3 Application experiment

**Hypothesis to test:** selective evidence plus structured run state preserves follow-up accuracy with less context than full history. **Competing hypothesis:** summarization loses a critical correction or negation; persistent memory introduces stale assumptions. Separate history, execution state, compaction, persistent memory and corpus retrieval in every experiment label.

## 3. Evaluation

### 3.1 Recent research and engineering evidence

| Reading, type and date | Why read it | Boundary or contrary test |
|---|---|---|
| [RAGe evaluation framework](https://arxiv.org/abs/2605.27445v1) — primary method preprint, 23 May 2026 | Read the evaluation design alongside section 2: separate retrieval/generation quality from resource use. | Reference or judge scores remain proxies. Preserve deterministic SQL checks, evidence labels and human-audited claims. |
| [When the Judge Changes, So Does the Measurement](https://arxiv.org/abs/2607.08535v1) — primary comparative preprint, 9 Jul 2026 | Examines evaluator replacement, bias and correlated judging errors. Supports freezing judge versions and auditing score changes. | Studied Qwen3 and MiniMax variants do not establish every judge’s behavior. Calibrate on our labeled cases; keep evaluator changes separate from application changes. |
| [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) — first-party engineering guidance, 9 Jan 2026 | Useful vocabulary for tasks, trials, graders, transcripts and outcomes. | Engineering advice rather than independent validation of an evaluator. Verify that local grading captures valid alternative paths and justified abstention. |
| [Time to REFLECT: Can We Trust LLM Judges for Evidence-based Research Agents?](https://arxiv.org/abs/2605.19196v1) — primary meta-evaluation preprint, 18 May 2026 | Uses controlled trace interventions to test detection of reasoning, tool-use and report/evidence failures. Provides current counterevidence to trusting an automated judge alone. | Injected failures are not an estimate of production failure frequency. Adapt fault cases and independently verify that our graders detect them. |

### 3.2 Tools, frameworks and systems

| System and current primary reference | Role and application fit | What to verify locally |
|---|---|---|
| [Langfuse evaluation](https://langfuse.com/docs/evaluation/overview) | Evaluation and observability around traces, datasets and scores. Candidate for relating an answer's grade to the execution that produced it. | Complete trace/usage export, dataset versioning and failed/retried attempts. A tracing platform does not establish grader correctness. |
| [Ragas](https://docs.ragas.io/en/stable/) | Evaluation tooling for LLM applications, including retrieval-oriented evaluation. The current software remains relevant even though its original paper is outside this reading cutoff. | Match metrics to our evidence and answer contracts; inspect required references, judge prompts and disagreement with human labels. |
| [Promptfoo](https://www.promptfoo.dev/docs/intro/) | Configurable evaluation and comparisons across prompts/models with assertions. Candidate for repeatable regression cases. | Capture tool-rich runs through an appropriate adapter, freeze test inputs and distinguish deterministic checks from model-graded assertions. |
| Application-owned gold checks | SQL result reconciliation, numeric tolerances, evidence validity and permitted-tool checks. These provide a small transparent baseline before adopting a platform. | Valid alternate solutions, justified abstention, holdout isolation and false positives. |

Keep evaluator, trace store and experiment runner conceptually separate even if one product supplies all three. Record quality, cost, latency and failures on the same tasks. Compare hosted/self-hosted availability, exports and integration effort when choosing tooling; do not install several overlapping evaluation platforms just to cover the landscape.

### 3.3 Application experiment

**Hypothesis to test:** outcome plus trace grading identifies failures that final-answer fluency hides. **Competing hypothesis:** a large judge suite adds cost and correlated error without improving decisions. Report deterministic checks, human agreement and judge disagreement separately. Evaluation is part of every experiment, not a product added after implementation.

## 4. Orchestration

### 4.1 Recent research and engineering evidence

| Reading, type and date | Why read it | Boundary or contrary test |
|---|---|---|
| [Cognition's updated multi-agent account](https://cognition.com/blog/multi-agents-working) — first-party production report, 22 Apr 2026 | Updates earlier skepticism with bounded reviewer/consultant/manager patterns and continuing communication problems. | Preserve the evolution in their position. Coding with one writer is adjacent to analytical synthesis, not direct proof. The weakest-primary escalation failure is useful contrary evidence. |
| [Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets](https://arxiv.org/abs/2604.02460) — primary comparative preprint, 2 Apr 2026; revised 11 Apr 2026 | Direct counterweight to claims that multiple agents inherently reason better. Authors examine matched budgets and API-budget artifacts. | Based here on abstract-level review; multi-hop benchmarks differ from parallel SQL/document investigations. Read full methods before relying on the theoretical argument or numerical findings. |


**Foundational readings retained for the course (checked October 1, 2026):** [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) for workflow/agent patterns; [Anthropic: How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) for independent research branches and context/cost trade-offs; [Google: Towards a science of scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) for task-dependent scaling evidence; [official A2A overview](https://a2a-protocol.org/latest/topics/what-is-a2a/) for independently operated agent interoperability. These supplement the newer research references above. See the [course design discussion](course/COURSE-PLAN.md#design-discussion-and-blog-handoff--workflow-agents-and-multi-agent) for the SQL/RAG alternative, seller-worker experiment, reviewer workflow and proposed cross-system examples. Vendor/benchmark findings and illustrative examples remain distinct from local measurements.

### 4.2 Tools, frameworks and systems

| Framework/system | Supported architectural role | What to verify locally |
|---|---|---|
| [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) | Explicit stateful graph orchestration, suitable for controlled workflows and agent loops. | Branching, checkpoints, parallel work, cancellation and shared-state ownership. More explicit control also means application design work. |
| [Google ADK](https://adk.dev/) | Agent and workflow composition within Google's framework; hosted deployment is a separate choice. | Chosen-language support for delegation, shared session state and trace export; test revised delegation after a worker discovers new evidence. |
| OpenAI Agents SDK and Claude Agent SDK — see the linked official references in Appendix A | Code-first agent composition versus a more opinionated bundled harness. OpenAI Agents SDK is selected for the baseline; Claude Agent SDK remains an alternative track with different ownership of the loop/context. | Do not assume identical orchestration semantics. Inspect handoffs, agents used as tools, permissions and context behavior for the selected version. |
| [Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-get-started-cli.html), with a selected framework such as Strands | Runtime/harness options and code-based deployments. Hosting an agent and defining its multi-agent topology are separate responsibilities. | Check the selected framework's topology APIs independently; this is not a verified Strands feature comparison. |
| Lyzr Manager Agent / SuperFlow — see Appendix A.1 | Dynamic manager delegation and explicit workflow composition provide another implementation style. | Verify discovery propagation, worker access to both SQL and retrieval, complete traces and aggregate budget controls. |

Choose one initial stack and a competent single-agent baseline. Compare fixed workflow, single-agent and multi-agent variants within that stack first. Changing frameworks may also change prompts, model access and context handling; report those as end-to-end stack differences. No framework listed here has been implemented or benchmarked in our application.

### 4.3 Application experiment

**Hypothesis to test:** independent substantive investigations improve coverage or wall-clock time on broad questions. **Competing hypothesis:** a single agent with equal aggregate budget retains context better and avoids duplicate work. Multi-agent remains a deliberately designed research extension to evaluate when ready, not a prerequisite for initial single-agent success or the presumed winning architecture.

Use the framework documentation in Appendix A to implement the topology. Do not allow convenient SDK examples to shrink the problem to “SQL agent plus search agent.” Specialists must own business subquestions and use both tools where relevant.

## 5. Reliable tool use

### 5.1 Recent research and engineering evidence

| Reading, type and date | Why read it | Boundary or contrary test |
|---|---|---|
| [ASTRA-bench: Evaluating Tool-Use Agent Reasoning and Action Planning with Personal User Context](https://arxiv.org/abs/2603.01357v1) — primary benchmark preprint, 2 Mar 2026 | Combines evolving context, tools and multi-step plans; identifies argument generation as a bottleneck in the tested models. | Personal-assistant scenarios differ from read-only SQL/retrieval. Adapt entity/date resolution and dependent tool-call cases; do not transfer headline performance to newer models. |

### 5.2 Tools, frameworks and systems

| System/mechanism and current primary reference | Role and application fit | What to verify locally |
|---|---|---|
| [Pydantic AI function tools](https://pydantic.dev/docs/ai/tools-toolsets/tools/) | Typed function tools and validation within an agent framework. Candidate for making SQL/retrieval contracts explicit. | Argument validation, error feedback, retry limits and dependency injection. Type correctness is not business authorization or semantic correctness. |
| [MCP server concepts](https://modelcontextprotocol.io/docs/2026-07-28/learn/server-concepts) — July 2026 documentation version | A standard interface for exposing tools and related server capabilities when a reusable external tool boundary is useful. | Pin protocol/client versions and inspect authentication, errors and discovery. MCP does not itself make a tool safe, correct or exactly-once. |
| Chosen agent SDK's tool facilities — see Appendix A | In-process tool registration, interception and execution controls may be sufficient for the initial application. | Verify actual hooks and permissions in the selected SDK; do not presume all frameworks enforce the same controls. |
| [LiteLLM routing/recovery](https://docs.litellm.ai/docs/routing) | Model-call retry and fallback mechanisms, adjacent to but distinct from tool recovery. | Prevent nested retries from exceeding the application deadline/budget; retain every attempt in the trace. |
| Application-owned SQL and retrieval adapters | Enforce read-only database access, allowed query behavior, bounded results and evidence metadata at the execution boundary. | Fault injection, timeouts, invalid arguments, partial results and safe error reporting. Model instructions cannot replace these controls. |

Choose tools to support the reliability contract, not to expand scope. A direct function call is a useful baseline; adding a protocol server or gateway needs a concrete integration benefit. Compare setup effort and operational dependencies as well as success rates.

### 5.3 Application experiment

**Hypothesis to test:** typed errors, bounded repair and explicit partial-result handling improve valid task completion. **Competing hypothesis:** aggressive recovery conceals missing evidence and creates expensive loops. Count correctly reported failure as safer behavior than a fabricated answer, while still distinguishing it from a completed task.

## Reading order and publication discipline

For immediate progress, start with the application specification and the separate live framework/API directory, then read Anthropic’s 2026 evaluation guide to design the first single-agent checks. The full reading list is not a prerequisite.

1. **Routing:** R2-Router and the OpenRouter report; inspect LiteLLM’s dated classifier integration as implementation evidence. Compare selection signals and total cost before adopting a router.
2. **Context and memory:** MemoryArena and Lost in Compaction; derive multi-session correction and compaction tests.
3. **Retrieval and evaluation:** RAGe, REFLECT and the judge-replacement study; define gold evidence and calibrate the evaluator.
4. **Orchestration:** pair Cognition’s production account with the equal-thinking-budget study. Preserve both practical benefits and contrary evidence.
5. **Tools:** ASTRA-bench; adapt context-dependent argument and planning failures to our read-only tools.

Deep-read the relevant full papers before numerical comparisons. These replacements were selected for current relevance, not because a recent date guarantees strong methods or results that transfer to our application.

For every blog draft, record source access date, study/model version, whether evidence is vendor-reported, what was implemented locally and which result was actually measured. A useful sentence has a bounded form: “In our frozen synthetic investigation suite, under these aggregate budgets, variant A changed this outcome relative to B.” Avoid universal claims such as “multi-agent is better,” “memory solves context,” or “a gateway makes agents reliable.”

The guide includes research from different academic/industry teams, multiple open-source stacks, first-party reports and direct counterevidence. Balance means giving the reader enough evidence to challenge a conclusion; it does not mean assigning equal weight to a product page and a controlled comparison. The unanswered question is how these approaches behave in the specified business assistant. That is what the experiments are for.

## Appendix A. Frameworks, harnesses and platforms

A framework is not a hosting decision. A hosted platform may also supply a harness, memory, retrieval, tools and evaluation. Buying a platform can change the architecture when it takes ownership of the loop or state; deploying an unchanged application process to a platform is a narrower hosting change.

The following are **documented roles**, not verified operational comparisons. All rolling documentation and product pages were accessed 26 September 2026. Product availability, language support and interfaces should be pinned and checked again when implementation begins.

| Named option and source | Role and control | Observability and portability implications |
|---|---|---|
| [Google ADK](https://adk.dev/) — open-source framework docs | Code-first agents and workflows; current docs include graph workflows and session/event concepts. It is distinct from Google's hosted agent platform. | Inspect events and evaluation/debugging surfaces for the chosen language/version. Open source helps inspectability; provider and managed-service adapters still need testing. |
| [Gemini Enterprise Agent Platform](https://docs.cloud.google.com/gemini-enterprise-agent-platform/build) — Google documentation, page updated 25 Sep 2026 | Broad managed platform with framework-based development, Agent Runtime, retrieval and managed-agent options. The managed loop and deployment of user-controlled code are different choices. | Docs expose observability/evaluation and state services. Managed identity, sessions and retrieval create service dependencies; verify trace export and state migration. |
| [Amazon Bedrock AgentCore](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/agentcore-get-started-cli.html) — AWS documentation | Distinguishes a managed harness from code-based agents deployed to Runtime. It explicitly lists Google ADK and OpenAI Agents alongside Strands and LangGraph as code-based choices. | A framework can cross cloud-vendor boundaries. Verify telemetry completeness, IAM, state storage and packaging with the exact runtime route. Do not conflate AgentCore with every Bedrock agent feature. |
| [LangChain/LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) — open-source product docs | LangChain supplies model/tool/agent abstractions; LangGraph supplies lower-level orchestration and durable stateful execution. LangGraph can be used standalone. | The docs distinguish LangSmith tracing/evaluation/deployment from the open-source runtime. Check checkpoint formats and exported traces; LangGraph's in-process “runtime” is not itself a cloud-hosting decision. |
| [OpenAI Agents SDK](https://developers.openai.com/api/docs/guides/agents/sdk) — official OpenAI documentation | Code-first agent definitions, run loop, tools, ownership/handoffs, guardrails and state. Distinguish the SDK from a hosted agent API or a raw model API client. | Follow its tracing/integration and model/provider documentation. Verify that non-default provider usage preserves required tool schemas and usage accounting; schema compatibility alone does not prove behavioral portability. |
| [Claude Agent SDK](https://code.claude.com/docs/en/agent-sdk/overview) — Anthropic documentation | Embeds the Claude Code binary, loop, tools and context management in a process the application operates. More opinionated than a raw Claude API client. | Docs expose sessions, hooks, permissions, cost and OpenTelemetry. Harness and model coupling complicate a generic provider comparison; built-in context behavior must be measured or declared fixed. |
| [Lyzr orchestration docs](https://docs.lyzr.ai/enterprise/get-started/concepts/multi-agent-orchestration) — first-party technical docs | Manager Agent provides dynamic delegation; SuperFlow describes explicit workflows. Additional docs cover SQL, retrieval, memory and traces; see Appendix A.1. | A plausible exploratory track, not hands-on verified or committed course inclusion. Exact enforcement, export and revised delegation controls require diligence. |

The comparison deliberately leaves gaps visible. “Supports multi-agent” is not enough: can the coordinator revise a sibling's work, retain evidence handles, cancel tasks and enforce an aggregate budget? “Observability” is not enough: can an exported trace reconstruct all model/tool attempts and the final claim lineage? “Portable” is not enough: which prompts, state, tool adapters, model features and managed services must change?

**Suggested selection exercise:** use a short decision record and, only if necessary, a small capability spike to choose one starting framework/runtime. First verify a single-agent SQL-plus-retrieval trace; inspect support for the intended later coordinator-discovery scenario without requiring its implementation before starting. No spike or selection has occurred.

Candidate tracks are Google ADK/Gemini Enterprise Agent Platform; an AWS stack such as Strands/Bedrock AgentCore; self-hosted/code-first components with OpenAI Agents SDK (selected for the initial local baseline); Claude Agent SDK with its bundled harness; and exploratory Lyzr. The AWS documentation linked above lists Strands as a code-based option; no detailed Strands capability comparison has been performed here. An open-source SDK, a fully open-source stack, open-weight models and self-hosted inference are distinct choices.

Hold one stack steady for architecture ablations. Later, use each ecosystem idiomatically while preserving versioned data/docs, tasks, evidence/output expectations and evaluation contracts. Changes in models, retrieval and harness defaults are confounders in end-to-end stack comparisons, not evidence of pure framework effects. Compare engineering effort, flexibility/control and operational visibility as well as answer quality. No exhaustive implementation of every supporting product is promised.

### A.1 Lyzr feasibility and technical diligence

The user's conversations with Lyzr people motivate an independent feasibility assessment, whether or not a course happens. The first-party technical docs below were opened on 26 September 2026. They make the application plausible and reveal no demonstrated blocker; they do not establish hands-on feasibility or that every required control is available out of the box.

| First-party source | Documented capability and diligence boundary |
|---|---|
| [Data Analyst Agent cookbook](https://docs.lyzr.ai/cookbooks/Data%20Analyst%20Agent) | Text-to-SQL with database connections and semantic models. Verify generated SQL visibility, read-only credentials, allowed query subset and query/result export. |
| [RAG and knowledge](https://docs.lyzr.ai/enterprise/get-started/concepts/rag-knowledge) | Retrieval over supplied knowledge. Verify source revision/span provenance and SQL plus retrieval access within each substantive specialist. |
| [Multi-agent orchestration](https://docs.lyzr.ai/enterprise/get-started/concepts/multi-agent-orchestration) and [Manager Agent](https://docs.lyzr.ai/enterprise/agent-studio/manageragent/studio) | Dynamic Manager Agent delegation and explicit SuperFlow workflows. Manager docs recommend keeping tools/knowledge on workers. This is an idiomatic difference from the generic coordinator design, which permits coordinator tools; preserve required outcomes and disclose that difference. Verify revised delegation when a worker discovers something affecting another worker. |
| [Memory](https://docs.lyzr.ai/enterprise/agent-studio/connections/memory) | Session context and cross-session persistence are both described under “Memory.” Our experiment uses memory only for deliberate cross-session retention: disabling that must preserve ordinary conversation history/task state. Verify retention, correction/deletion, isolation and extraction controls. |
| [Monitoring and tracing](https://docs.lyzr.ai/enterprise/agent-studio/agent%20eval/tracing) | Run records, usage/latency and detailed operation timelines/logs. Verify complete machine-readable trace/query export and whether all retries, subagent calls and evidence lineage are recoverable. Dashboard presence alone does not establish this. |
| [A2A integration](https://docs.lyzr.ai/enterprise/integrations/a2a-protocol) | Documents agent interoperability support. Background only: A2A and cross-system/independently hosted interoperability are excluded from the current implementation scope. |

A concrete diligence demonstration should have two workers each perform SQL and retrieval, then introduce a discovery that requires the manager to revise another worker's task. Inspect resulting evidence, query and trace exports. Check aggregate budgets, timeouts, cancellation, read-only enforcement, model selection/fallback policy and memory controls. Missing built-in controls may require custom tools or orchestration; they do not by themselves prove the application impossible. Do not infer exactly-once guarantees or production reliability from documentation claims without testing their boundaries.

Internal agents communicate within one application, possibly through a coordinator. A2A is not inherently restricted to outside organizations; it is simply unnecessary for this scope. Also, the orchestration page's description of a single agent as limited to one turn is not our definition: our single-agent baseline can take multiple reasoning/tool steps.


**October 1 implementation clarification:** catalog v2 unifies semantic definitions and database metadata; the former sampled-record “context graph” is removed. A richer instance/evidence graph is a future experiment. See [prompt construction examples](app/docs/PROMPT-AND-CATALOG.md).
