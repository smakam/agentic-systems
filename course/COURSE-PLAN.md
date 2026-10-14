# Inside AI Agent Systems: From Components to Platforms

**Subtitle:** Understand, build and evaluate AI agents through hands-on experiments, and choose the right platform for your needs.

**Reviewer-facing outline:** [Course outline for feedback](https://docs.google.com/document/d/1UFUyWdsYq-mIXusY0pakXXvWOXQOmBry/edit).

**Owner:** Sreenivas Makam. Chapters 1–18 contain the current reviewed lesson decisions. Chapters 19–22 retain their planning detail until review. Implementation history belongs in [MILESTONE-LOG.md](../MILESTONE-LOG.md); application requirements belong in [SPECIFICATION.md](../SPECIFICATION.md).

## Positioning

Build and understand an AI agent system through one stateful marketplace support application. Change AI components, inspect evidence, and evaluate quality, cost and latency to choose a design or platform for your needs. Model-specific numbers are dated case studies, not general rankings.

The code-based path assumes Python, basic SQL, Docker and familiarity with LLM APIs. Guided demonstrations and saved results also support learners focused on concepts and platform choices. The course covers AI-system engineering, including constrained tools, evaluation, tracing, guardrails and context isolation; general infrastructure administration and identity implementation are outside its focus.

The interactive support default is GPT-5.4. Historical Nano/GPT-5 comparisons keep their original models and evidence. Changing current aliases does not retroactively change those results.

## Lesson format and material conventions

From Chapter 5 onward, provide explanation, an instructor demonstration where appropriate, learner practice, separate reference answers and a closing recap of abilities and the next chapter. Chapter 4 uses the Mac-first written setup guide with Linux/Windows notes. The final platform overview uses a comparison worksheet, not new deployments.

Each activity states its workspace URL, database or supplied-data source, exact settings, task, observations and cleanup. The Test workspace is not universal: gateway CLI, Agent Loop, retrieval/session developer labs and Langfuse-only activities use the environments named below. Do not reset a shared practice database while another learner is using it.

Use `exercise.md` for learner instructions, `instructor-demo.md` where a separate walkthrough exists, and `solutions/answers.md` for worked answers. A `README.md` is navigation only. Keep scripts, fixtures and evidence only when required by the activity or a current reference; identify optional developer material explicitly. [Exercise starting index](exercises/README.md).

Speaker notes contain presentation cues, demo steps and exercise instructions. Keep distributed exercises and answers separate so learners can attempt the task before opening the solution. Restore code/configuration separately from database resets. Never distribute credentials.

## Chapter map

Six sections and twenty-two chapters. Chapters may contain several short lectures.

| Section | Chapters | Focus |
|---|---|---|
| A | 1 | Course Introduction |
| B | 2–5 | Anatomy |
| C | 6–12 | Core Components |
| D | 13–15 | Observability, Evaluation and Security |
| E | 16–18 | Advanced Agent Topics |
| F | 19–22 | Agentic Platforms |

## A. Course Introduction

### 1. Welcome and Course Roadmap

**Learning objective:** Explain the audience, prerequisites, learning paths and six-section course sequence. Introduce the marketplace as the shared teaching example.

**Demo and learner practice:** Welcome and roadmap; no hands-on lab. Record the welcome after the chapter recordings.

**Workspace:** No workspace required.

## B. Anatomy

### 2. The Components of an Agent

**Learning objective:** Trace a question through models, instructions and context, tools and retrieval, sessions and memory, orchestration, runtime and observability.

**Demo and learner practice:** Use the component diagram to explain responsibilities and boundaries. Application and support-agent demonstrations follow in Chapters 3 and 5.

**Workspace:** Conceptual chapter; no workspace required.

### 3. The Marketplace Application

**Learning objective:** Connect buyers, sellers, orders, payments, payouts, refunds and versioned policies to the questions support must investigate.

**Demo and learner practice:** Demonstrate login, product listings and a purchase. Explain business journeys and local/cloud architecture. The support-agent walkthrough belongs in Chapter 5.

**Workspace:** Main marketplace UI: http://localhost:5178/; database market. Use the interactive business data for the application demonstration.

### 4. Course Setup

**Learning objective:** Start the local reference application and verify services, credentials and model access.

**Demo and learner practice:** Follow the Mac-first written setup guide for Git, Docker Compose, editor/Python, provider keys, demo accounts, costs, seeded data and reset checks. Linux and Windows notes are separate. Native platform setup belongs in later chapters.

**Workspace:** Use app/LOCAL-SETUP.md. It identifies the main UI, Test workspace, dedicated Agent Loop lab and Langfuse; verify each service before its activity.

**Guide:** [Local setup](../app/LOCAL-SETUP.md).

### 5. Your First Agent, End to End

**Learning objective:** Follow one OpenAI Agents SDK investigation through code, model/tool calls, evidence, final answer and Langfuse.

**Demo and learner practice:** Instructor: ask a current-state question, make a purchase, ask again and inspect fresh evidence and the business revision. Learner: practice marketplace journeys and a known-answer investigation in disposable data. Saved 18-case results introduce correctness checking; full evaluation is Chapter 14.

**Workspace:** Instructor: main UI http://localhost:5178/, database market. Learner: Test workspace http://127.0.0.1:5179/, database market_test. Trace inspection: http://localhost:3000, project marketplace-support.

**Materials:** [Exercise](exercises/chapter-05-first-agent/exercise.md) · [Answers](exercises/chapter-05-first-agent/solutions/answers.md)

**Result boundary:** The saved 18-case comparison graded Nano 11 correct / 4 partial / 3 incorrect and GPT-5.4 17 / 1 / 0. Two follow-up cases generated 20 answers per model; the counts are case grades. [Saved comparison](../app/results/core18-history-v3-2026-10-01/comparison.html).

## C. Core Components

### 6. Model and Gateway

**Learning objective:** Explain model capability, cost and latency, and how a gateway centralizes access through aliases, scoped keys and workload attribution.

**Demo and learner practice:** Swap a model behind an alias while holding questions and fixtures fixed. Inspect correctness, tool calls, usage, estimated cost and latency. Explain retries, fallbacks, budgets and caching as capabilities; distinguish gateway response caching from provider prompt caching.

**Workspace:** Dedicated CLI/API lab: backend http://127.0.0.1:58006/, gateway http://localhost:4006/, market_test in the separate course-ch6-db container. Use app/scripts/chapter-06-lab.py; this is not the normal Test workspace. Langfuse: http://localhost:3000.

**Materials:** [Exercise](exercises/chapter-06-model-and-gateway/exercise.md) · [Answers](exercises/chapter-06-model-and-gateway/solutions/answers.md)

### 7. Prompt and Context

**Learning objective:** Identify which instructions, business definitions, schema/catalog context, metadata and evidence a question needs.

**Demo and learner practice:** Map context and compare catalog suppression/restoration on business questions and policy suppression/restoration on policy questions. Keep the fixture, revision and clock fixed; use fresh conversations. Record missing explanations, qualified answers, guessed queries and failures rather than assume all context removal must fail.

**Workspace:** Test workspace http://127.0.0.1:5179/, database market_test; Support with OpenAI Agents SDK and memory off. Inspect marketplace-support traces in local Langfuse.

**Materials:** [Exercise](exercises/chapter-07-prompt-and-context/exercise.md) · [Answers](exercises/chapter-07-prompt-and-context/solutions/answers.md)

**Takeaway:** Missing catalog or policy context can change completeness, uncertainty or execution; a successful query alone does not show that all necessary context was supplied.

### 8. Tools and MCP

**Learning objective:** Distinguish tool contract, implementation and transport, including SQL validation, read-only permissions, evidence references and limits.

**Demo and learner practice:** Inspect business, retrieval and memory tools; compare stdio and remote HTTP MCP, and examine a rejected request. Core learners repeat the tool investigation. Developer extensions add a seller-balance tool and a separate tracking MCP server using supplied JSON fixtures.

**Workspace:** Test workspace http://127.0.0.1:5179/, database market_test. Code extensions use an isolated application copy/disposable database; tracking uses its own JSON fixtures. Optional cloud work requires the learner’s own deployment and database.

**Materials:** [Exercise](exercises/chapter-08-tools-and-mcp/exercise.md) · [Answers](exercises/chapter-08-tools-and-mcp/solutions/answers.md)

### 9. Knowledge and Retrieval (RAG)

**Learning objective:** Separate retrieval correctness from answer correctness when combining business records with versioned policy evidence.

**Demo and learner practice:** Explain ingestion, paragraph chunks, gateway embeddings, PostgreSQL/pgvector, effective dates and ranking. Ask policy-only and mixed questions. Reindex supplied policy versions, then compare overlapping chunks and retrieval settings without assuming better final answers.

**Workspace:** UI: Test workspace http://127.0.0.1:5179/, market_test. Developer reindex/chunk work: dedicated ch09_rag_lab synthetic corpus through the documented CLI; the normal UI does not query that corpus.

**Materials:** [Exercise](exercises/chapter-09-knowledge-and-retrieval/exercise.md) · [Answers](exercises/chapter-09-knowledge-and-retrieval/solutions/answers.md)

**Takeaway:** New policy text requires reindexing in the isolated lab. Chunk overlap and more retrieved text did not establish a general answer-quality improvement.

### 10. Session State

**Learning objective:** Distinguish retained conversation history, per-run state and persistent memory, including isolation and evidence freshness.

**Demo and learner practice:** Show a follow-up, fresh evidence after a business-state change, and an early detail leaving the model input after six later question blocks while remaining stored. Core learners repeat the observations. Developers compare window sizes and summarization plus a recent window.

**Workspace:** Core: Test workspace http://127.0.0.1:5179/, market_test. Developer comparison: temporary backend copy and ch10_session_lab. Restore original code/settings separately from database cleanup.

**Materials:** [Exercise](exercises/chapter-10-session-state/exercise.md) · [Answers](exercises/chapter-10-session-state/solutions/answers.md)

**Takeaway:** Stored history and model-visible history differ. Summary strategies are alternatives to measure, not guaranteed token savings.

### 11. The Agent Loop with OpenAI Agents SDK

**Learning objective:** Explain the model/tool loop and SDK capabilities: agent setup, execution and streaming, tools/MCP, state/results, hooks/tracing, guardrails, human review and orchestration.

**Demo and learner practice:** Map Agent, Runner and Hooks to normal execution, a controlled temporary tool-error recovery, and a turn-limit stop. Core learners annotate model/tool counts, evidence and stopping. Developers implement a minimal loop with supplied adapters and compare it with the SDK. SDK guardrails are a separate integration point from our gateway privacy/injection checks.

**Workspace:** Dedicated Agent Loop UI http://localhost:5181/, database ch11_loop_lab. Use fresh conversations and lab-only execution modes. The normal Test workspace is not this lab.

**Materials:** [Exercise](exercises/chapter-11-agent-loop/exercise.md) · [Answers](exercises/chapter-11-agent-loop/solutions/answers.md)

### 12. Runtime and Hosting

**Learning objective:** Separate framework choice from hosting, and distinguish infrastructure responsibilities from agent-system capabilities.

**Demo and learner practice:** Inspect existing local Docker and full-cloud marketplace configurations: chat/agent, gateway, MCP, databases and external history. Complete six local architecture questions and six optional cloud questions, citing configuration/service/trace evidence. No new deployment or tunnel is required.

**Workspace:** Local worksheet: Test workspace http://127.0.0.1:5179/, market_test. Optional cloud section: learner’s already deployed full marketplace and its own database. The historical agent-only hosting lab is not this activity.

**Materials:** [Exercise](exercises/chapter-12-runtime-and-hosting/exercise.md) · [Answers](exercises/chapter-12-runtime-and-hosting/solutions/answers.md)

## D. Observability, Evaluation and Security

### 13. Observability: Tracing and Monitoring

**Learning objective:** Explain one run through tracing and behavior over time through monitoring; assess observability platforms by practical capabilities and boundaries.

**Demo and learner practice:** Investigate six supplied recorded runs and two dashboard widgets for daily count and daily p99. Inspect tool timing, recovered errors versus failed roots, feedback, available cost and conversation links. Native platform telemetry is covered in platform chapters.

**Workspace:** Local Langfuse http://localhost:3000, project marketplace-support. This is a recorded-evidence investigation; no business database changes, uploads or new model calls are required. The Agent Loop UI is optional for locating existing runs.

**Materials:** [Exercise](exercises/chapter-13-observability/exercise.md) · [Answers](exercises/chapter-13-observability/solutions/answers.md)

### 14. Evaluation

**Learning objective:** Distinguish golden references, deterministic checks, provisional LLM judgments, human review and calibrated judge agreement.

**Demo and learner practice:** Instructor: inspect five saved answers and human/judge grades, then three structured answers with native TypeScript evaluation. Learners human-grade the five supplied answers and import their grades, then import and inspect the three structured outputs using the configured native evaluator. No paid model calls are needed. Repeated trials and online evaluation are concepts, not additional required implementation exercises.

**Workspace:** Local Langfuse http://localhost:3000, project marketplace-support; supplied answer fixtures and repository-root import commands. Reuse Chapter14 structured order comparison with its worker/dispatcher. No marketplace UI or business database is required.

**Materials:** [Exercise](exercises/chapter-14-evaluation/exercise.md) · [Answers](exercises/chapter-14-evaluation/solutions/answers.md) · [Instructor demo](exercises/chapter-14-evaluation/instructor-demo.md)

**Takeaway:** Judge agreement is not model accuracy, and feedback is not factual correctness. Human review and deterministic checks have different roles; a single trial does not establish consistency. [Calibration evidence](../app/results/calibration-v3-2026-09-29/CALIBRATION-SUMMARY.md).

### 15. Guardrails and Agent Security

**Learning objective:** Explain privacy, prompt injection, source authority, tool enforcement and protection boundaries through bounded examples.

**Demo and learner practice:** Run input/output masking, a sensitive-card blocking case and a retrieved instruction-attack case. Distinguish detector decisions, model behavior, source-authority guidance and enforced read-only tools. Teach prevention, detection and response without claiming complete OWASP coverage.

**Workspace:** Test Support http://127.0.0.1:5179/, market_test; OpenAI Agents SDK, memory off and prescribed guardrail/source-authority settings. Local Langfuse marketplace-support. Use isolated policy fixtures and cleanup instructions.

**Materials:** [Exercise](exercises/chapter-15-guardrails-security/exercise.md) · [Answers](exercises/chapter-15-guardrails-security/solutions/answers.md) · [Instructor demo](exercises/chapter-15-guardrails-security/instructor-demo.md)

## E. Advanced Agent Topics

### 16. Model Routing

**Learning objective:** Define routing, model pool, selection policy and scope before applying them to experiments.

**Demo and learner practice:** Explain conversation, question, model-call and named-stage scope, caching as a design consideration, and application versus gateway routing. Present the historical 18-case classifier and six-conversation studies with small-sample limits. Live demo compares native LiteLLM keyword and LLM policies, then LLM conversation/question scope; learner lab adds trained heuristic v2 and documents gateway decisions in Langfuse.

**Workspace:** Test workspace http://127.0.0.1:5179/, market_test; Support with OpenAI Agents SDK, routing controls, memory/guardrails off and source authority on. Keyword and heuristic use per-question scope; LLM uses either scope.

**Materials:** [Exercise](exercises/chapter-16-model-routing/exercise.md) · [Answers](exercises/chapter-16-model-routing/solutions/answers.md) · [Instructor demo](exercises/chapter-16-model-routing/instructor-demo.md)

**Historical conclusion:** Business-context classifier configurations did better on these tested cases. Both scope policies reduced cost but lowered fully correct conversations versus always GPT-5 (4/6 versus 6/6); neither improved this pilot’s quality/cost tradeoff. Larger samples and repeated trials are needed. Cache reuse can affect cost/latency, especially across a conversation; no isolated cache benefit is claimed.

### 17. Agent Design Patterns

**Learning objective:** Choose workflow, single-agent or hybrid control, then justify additional roles through independent work, distinct evidence/capability or system boundaries.

**Demo and learner practice:** Teach workflow patterns before multi-agent roles, concrete examples, four linked use cases and A2A across systems. Present the untested serial records/policy split separately from the measured seller-worker and reviewer studies. Demo a hybrid multi-agent workflow: generation, evidence/context handoff, structured review, code-controlled branch and one optional correction. Learners inspect baseline/hybrid runs and a conversation follow-up.

**Workspace:** Test workspace http://127.0.0.1:5179/, market_test; Support with OpenAI Agents SDK and Agent design demo controls. Routing and memory off. Follow Generate draft, Review draft, Workflow decision and optional Correct draft in local Langfuse.

**Materials:** [Exercise](exercises/chapter-17-agent-design-patterns/exercise.md) · [Answers](exercises/chapter-17-agent-design-patterns/solutions/answers.md) · [Instructor demo](exercises/chapter-17-agent-design-patterns/instructor-demo.md)

**Historical conclusion:** The serial business-records/policy split was not tested because no clear benefit justified the handoffs. Seller workers added coordination overhead and one run failed to complete; parallel tool calls can sometimes supply the needed concurrency. Stronger review improved Nano’s fully correct count from 11/18 to 14/18, below GPT-5.4 alone at 17/18. These bounded findings justify checking reviewer capability and coordination cost. [Live controller](../app/backend/marketplace/agent_design_demo.py) · [Seller experiment](../app/scripts/payout-orchestration.py) · [Reviewer experiment](../app/scripts/reviewer-workflow-core18.py).

### 18. Short-term and long-term memory

**Learning objective:** Distinguish conversation context from retained knowledge, explain what memory should preserve and when it should be used, and inspect formation, retrieval and lifecycle across conversations.

**Lesson scope:** Explain short-term context and three long-term purposes with marketplace examples: semantic preferences, episodic investigation checkpoints and procedural checklists. Design memory by storage, trusted user scope, save trigger, retained content, retrieval, update/retention and deletion. Choose foreground or background memory writes; our integration retrieves during the answer and extracts completed conversations in the background. Trace the loop from conversation content through formation, later retrieval, answer use, update and forgetting. Stored history and the bounded context sent to the model are different; deleting a memory does not delete historical chat.

**Demo and learner practice:** Follow same-conversation context and a fresh conversation, then explicit internal saving and automatic Mem0 extraction without a save request. Inspect actual saved entries, cross-conversation recall, a paraphrased query, edit/forget, current-instruction precedence, fresh business evidence and user isolation. Learners document settings, stored entries, retrieved evidence, final answers and the question/extraction trace links. Finish by draining pending lab jobs and deleting only named lab records, without submitting another conversation that restates the deleted memory.

**Workspace:** Test workspace http://127.0.0.1:5179/, database market_test; Support with OpenAI Agents SDK. Use the Internal memory/Mem0 selector. Normal support model, routing and Agent design demo off, clean policy and source-authority context on; the main marketplace on 5178 and Agent Loop lab on 5181 do not enable this Mem0 lab. Trace inspection: local Langfuse http://localhost:3000/, project marketplace-support.

**Materials:** [Exercise](exercises/chapter-18-short-and-long-term-memory/exercise.md) · [Answers](exercises/chapter-18-short-and-long-term-memory/solutions/answers.md) · [Instructor demo](exercises/chapter-18-short-and-long-term-memory/instructor-demo.md)

**Implemented comparison:** Internal memory uses application-owned PostgreSQL records, trusted owner/provenance, bounded keyword search and version-checked edits through local stdio MCP tools. Saving requires explicit user intent and per-question write permission. The deployed hosted Mem0 integration queues completed turns at New conversation or the configured idle trigger. A conservative user-authored durable-intent gate skips routine business/recall-only turns as `noop`. Eligible full user/assistant context goes to REST V3 add with per-request `marketplace-durable-context-v2` retention guidelines; shared project settings are unchanged. Hosted HTTPS MCP supplies search/list/edit/delete and extraction status polling. Retrieval is a separate agent read operation. Turning retrieval off does not disable extraction while Mem0 is selected. Provider categories are preserved rather than forced into our three-purpose taxonomy; external records do not inherit internal version semantics.

**Retrieval design:** Both enabled providers are instructed to search presentation preferences plus topic/checklist/checkpoint before every business question. A retrieved user layout overrides default Field/Details formatting; a current explicit user request overrides that preference. The agent still selects tools; no forced application preload is used. Current [Mem0 Platform graph documentation](https://docs.mem0.ai/platform/features/graph-memory) describes always-on entity extraction/linking and a retrieval boost combined with semantic and keyword scores. Internal memory has no custom graph implementation. The lab compares the observed provider behavior; it does not isolate the graph contribution, rank providers generally or inspect their physical storage.

**Verified boundary and takeaway:** Core internal save/recall/lifecycle checks and deployed Mem0 formation, business-question preference use, paraphrased retrieval, edit/delete, trusted user isolation and trace handoffs were verified. Isolated Internal/Mem0 status runs both retrieved and applied a saved preference; the user confirmed the deployed retrieval fix. A provider intermittently recreated a deleted preference from business-only input; audited payloads contained no such preference and the provider-internal cause remains unknown. The gate prevents that business-only submission path, without guaranteeing perfect grounding or cross-batch deduplication for eligible chats. The default 900-second idle trigger has automated coverage; the live rehearsal used New conversation. Formation, retrieval and correct use are separate checks: an acknowledgement is not proof of storage, a queued operation is not a confirmed save, and retrieved memory is not authoritative current business evidence. Current instructions override preferences; live records and applicable policy override historical checkpoints/checklists. Broader repeated and held-out evaluation, automatic history compaction, shared procedures and automatic expiry/consolidation remain outside this lab.

**Code and evidence:** [Internal memory](../app/backend/marketplace/memory.py) · [Mem0 adapter and background jobs](../app/backend/marketplace/mem0_provider.py) · [Integration and verification boundaries](../app/docs/MEM0-INTEGRATION.md) · [Memory status and historical evidence](../app/docs/MEMORY-STATUS.md). Historical [eight-scenario / 19-question results](../app/results/memory-repeatable-20261003T093153094486Z/REPORT.md) complement the current lab; the [24-case catalogue](../app/eval/memory-v2/README.md) is a catalogue, not a claim that every case ran.

---

## F. Agentic Platforms

Reuse the marketplace support tasks, MCP tool contracts and evaluation criteria to compare component ownership, quality, costs, engineering effort and control. These tracks change different parts of the stack; disclose model, prompt, context and hosting differences before comparing results.

**Orientation:** Compare four provider categories—cloud platforms, frontier model providers with agent tooling, framework-led independents and platform-led independents—then map them onto models, frameworks, managed infrastructure, builders and governance. Supporting several models or clouds is different from governing agents across runtimes.

**Companion material:** [Platform landscape and customer fit](PLATFORM-GUIDE.md#platform-landscape-positioning-and-customer-fit) · [Component ownership worksheet](PLATFORM-GUIDE.md#common-comparison-agentic-system-components-and-ownership). The guide holds product references, technical boundaries, architecture, dashboard steps, detailed evidence and enhancements.

### 19. Google Gemini Enterprise Agent Platform

**Reviewed lesson scope:** Introduce the managed platform's purpose, benefits and tradeoffs; map familiar agent components in one architecture diagram; distinguish self-managed open-source ADK from Managed Agent Platform; explain component cost drivers, including evaluation separately from observability. Selected services can be combined; avoid blanket model, external-memory or data-location restrictions.

- **Core lesson and demonstration:** Deploy the separate **Support Agent Basics** agent, with packaged fictional orders and native `lookup_order`. Use native Google Playground to inspect record evidence, a same-session follow-up, an unknown order, native session/trace events and separately triggered Memory Bank generation/recall. No marketplace UI, SQL, MCP middleware, tunnel or Cloud SQL is required for Basics.
- **Standalone practice:** Follow the chapter's concise setup guide for prerequisites, editable environment settings, installation and test/deploy commands. The instructor guide starts after deployment and supplies the exact questions and observations. Reference answers separate fictional source facts from model behavior.
- **Optional adventurous exercise:** Build the full cloud integration connecting the chat application/backend and business data/MCP to a Google-hosted agent, using the linked cloud instructions. This is separate from standalone Basics and preserves the existing Marketplace Support ADK Lab.
- **Current verification:** Basics has been created. Native Playground product lookup, same-session held-payout follow-up, missing-record result and model/tool traces have been checked. Cross-session memory verification remains pending. The existing cloud integration has its own historical evidence; it is not a fresh learner-project installation rehearsal.

**Materials:** [Setup guide](exercises/chapter-19-google-agent-platform/setup-guide.md) · [Instructor walkthrough](exercises/chapter-19-google-agent-platform/instructor-demo.md) · [Exercise](exercises/chapter-19-google-agent-platform/exercise.md) · [Separate answers](exercises/chapter-19-google-agent-platform/solutions/answers.md) · [Basics code and instructions](../app/google/basics/README.md) · [Optional integration walkthrough](GOOGLE-PLATFORM-WALKTHROUGH.md).

### 20. Lyzr Agent Studio

**Draft learner practice — for review, not finalized:**

- **Core lesson:** A standalone Lyzr support-agent activity in native Studio/Playground, with native session, memory and observability inspection. Keep the required lesson independent of the marketplace chat application; determine its precise fictional-data/tool setup during Chapter 20 review.
- **Exercise to prepare:** Ask a known question and follow-up, inspect native sources/trace and distinguish session context from persistent memory.
- **Solution to prepare:** Native setup, exact fixture/prompts, expected tool/source checkpoints and annotated memory/trace observations. The standalone lesson is not yet implemented or verified.

- **Learning objective:** Understand the agent execution, tools, sessions, memory and tracing supplied by Lyzr's managed platform.
- **Optional integration extension:** Connect the hosted Lyzr agent to the existing GCP marketplace chat and authenticated MCP/Cloud SQL business backend, with explicit credential/target instructions from the [Lyzr integration guide](../app/lyzr/README.md), [runtime selector/configuration](../app/RUNTIME-SELECTOR.md) and [cloud setup](../app/CLOUD-SETUP.md).
- **Historical evidence:** Existing local/cloud marketplace adapters, hosted business calls, sessions and native Cognis were validated. Keep the earlier checklist-use limitation visible; those integration results do not establish a future standalone lesson's acceptance.
- **Details:** [Platform component ownership and historical results](PLATFORM-GUIDE.md#21-lyzr-agent-studio).

### 21. Other Agent Platforms

**Draft learner practice — for review, not finalized:**

- **Exercise:** Complete a component-ownership worksheet for two offerings: agent execution, tools, sessions, memory, tracing, deployment and access.
- **Solution to prepare:** A worked comparison with dated official sources and clearly identified unknowns; this is a documentation exercise, not a deployment lab.

- **Learning objective:** Compare managed agent offerings with the SDK baseline by component ownership and operational responsibility.
- **Format:** Slides only, about one or two slides per offering; no new deployment labs.
- **Covers:** AWS Bedrock AgentCore; Claude Managed Agents; Microsoft Foundry; OpenAI Agents API managed runtime.
- **Comparison lens:** Who runs the agent, manages sessions/context, connects tools, supplies memory and tracing, and controls deployment and access. Distinguish frameworks, models and hosted runtimes.
- **Evidence boundary:** These are documentation-based overviews, not marketplace integrations validated in this course. OpenAI Agents SDK remains the baseline throughout the application; its managed Agents API is a distinct offering. See [official Agents API documentation](https://developers.openai.com/api/docs/guides/agents-api/overview). Recheck product capabilities when preparing slides.
- **Deferred:** A hands-on AWS hosting chapter may be added later if bandwidth permits; it is outside the current release scope.

### 22. Choosing an AI platform

**Draft learner practice — for review, not finalized:**

- **Exercise:** Write a short decision report using results collected throughout the course: chosen design/platform, evidence, trade-offs, limitations and next steps.
- **Solution to prepare:** An example decision report and rubric; explain the reasoning and distinguish measured integrations from documentation-only comparisons.

- **Learning objective:** Choose a stack using customer needs, measured results and ownership requirements.
- **Lab:** Generate a decision report from available tracks; compare quality, cost, latency, integration effort and control, with confounders disclosed.
- **Closing lesson — prepare with this chapter:** Use the existing decision-report lab to conclude the course. Learners summarize their chosen design/platform, supporting evidence, quality/cost/latency trade-offs and limitations, then identify sensible next steps. Prepare this during chapter 22 delivery work; no additional chapter or implementation project is required. End with a thank-you slide; no separate conclusion chapter.
- **Status:** Method available; prepare the decision lesson from the SDK baseline and completed Google/Lyzr tracks, with documentation-only offerings clearly identified.
- **Details:** [Decision criteria, evidence and pending work](PLATFORM-GUIDE.md#22-choosing-an-ai-platform).

---

## Delivery and release checks

The required release retains all six sections and twenty-two chapters, including multi-agent design and memory. Google and Lyzr remain the hands-on platform tracks; the other-platform chapter is documentation-based. Additional AWS/Claude/Microsoft/OpenAI managed-runtime deployment labs are outside this release.

Before recording and release, rehearse the written setup on a clean machine, verify current model availability and lab costs, and provide saved evidence for learners limiting paid calls. Record and edit chapter lectures after their materials and learner paths are reviewed. Record the welcome last; agree the separate promotional video’s content before recording it. Managed-platform lessons need dated sources and current setup checks.

Future model migration or broader experiments must preserve dated reports and state which configuration changed. Chapters 19–22 retain their detailed planning until review; refine those chapters without reopening completed earlier activities.
