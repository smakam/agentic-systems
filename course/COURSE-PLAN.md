# Inside AI Agent Systems: From Components to Platforms

**Subtitle:** Understand, build and evaluate AI agents through hands-on experiments, and choose the right platform for your needs.

**Reviewer-facing outline:** [Course outline for feedback](https://docs.google.com/document/d/1UFUyWdsYq-mIXusY0pakXXvWOXQOmBry/edit).

**Owner:** Sreenivas Makam. Chapters 1–21 contain the current reviewed lesson decisions. Each platform lesson states its verified behavior and remaining preparation limits. Implementation history belongs in [MILESTONE-LOG.md](../MILESTONE-LOG.md); application requirements belong in [SPECIFICATION.md](../SPECIFICATION.md).

## Positioning

This course is for developers, technical leaders, product managers and business stakeholders who need to understand, build, evaluate or choose AI agent systems for enterprise workflows. A stateful marketplace support application provides a practical business example throughout the course.

Learners study the components, design patterns and production considerations behind an agent system, including observability, evaluation, security, memory and deployment. They compare models and platform choices, understand what frameworks and managed services provide, and decide what their own team must build, integrate and operate. The emphasis is on building from components and making evidence-based engineering and product decisions.

## Practical learning and prerequisites

Activities include configuring models and tools, trying changes in a working system, inspecting traces, examining monitoring signals, evaluating answers, checking guardrails and memory behavior, and comparing designs and platforms. Some exercises involve code or configuration; others involve investigation, observation and a documented recommendation. Demonstrations and experiments teach production concerns without claiming that every lab is a complete production deployment.

Code-based labs assume Python basics, basic SQL, Docker and familiarity with LLM APIs. Beginners and learners without programming experience can understand most explanations, guided demonstrations and platform comparisons through an observation-focused path. Experienced developers can go deeper through configuration work, code-based labs and optional extensions. Product and business learners can use guided demonstrations, saved results and comparison activities to understand behavior and tradeoffs. Detailed environment preparation and exact workspace addresses belong in Course Setup and the relevant activity guide, rather than the reviewer-facing overview.

The interactive support default is GPT-5.4. Historical Nano/GPT-5 comparisons keep their original models and evidence. Model-specific numbers are dated case studies, not general rankings; changing current aliases does not retroactively change those results.

## Lesson format and material conventions

The reviewer-facing overview uses four consistent headings where content exists: Learning objective, Core topics, Instructor demo and User exercises. Omit a demo or exercise subsection when no such activity exists; do not add an absence note or invent an activity. Describe orientation and decision activities accurately. Chapter cross-references include the chapter title, such as Chapter 4: Course Setup. From Chapter 5: Your First Agent, End to End onward, provide explanation, an instructor demonstration where appropriate, learner practice, separate reference answers and a closing recap. Introduce the next chapter except in the final lesson. Chapter 4: Course Setup uses the Mac-first written setup guide with Linux/Windows notes. The final platform overview uses a comparison worksheet, not new deployments.

Each detailed activity guide states its workspace URL, database or supplied-data source, exact settings, task, observations and cleanup. The Test workspace is not universal: gateway CLI, Agent Loop, retrieval/session developer labs and Langfuse-only activities use the environments named below. Do not reset a shared practice database while another learner is using it.

Use `exercise.md` for learner instructions, `instructor-demo.md` where a separate walkthrough exists, and `solutions/answers.md` for worked answers. A `README.md` is navigation only. Keep scripts, fixtures and evidence only when required by the activity or a current reference; identify optional developer material explicitly. [Exercise starting index](exercises/README.md).

Speaker notes contain presentation cues, demo steps and exercise instructions. Keep distributed exercises and answers separate so learners can attempt the task before opening the solution. Restore code/configuration separately from database resets. Never distribute credentials.

## Chapter quizzes

**Draft bank prepared (15 October 2026):** Five single-answer multiple-choice questions for each of Chapters 1–21, 105 questions overall, alongside the existing demonstrations and hands-on exercises. The bank has 98 course-based questions and seven brief official-documentation research checks. The research questions are a small minority and require no paid service access.

- Mix foundational checks, applied decisions and more challenging scenarios. Difficulty labels are author estimates in the instructor key, not calibrated pass rates.
- Tie course-based questions to actual lesson topics; mark research extensions and provide the official source and relevant section.
- Use four answer options with one correct answer. Explain each correct answer and distractor.
- Keep learner questions separate from instructor keys. Each chapter pack also has structured authoring data and a related lecture topic for later mapping.
- Review the complete bank against final recordings before entry as Udemy curriculum **Quizzes**. The ZIP/JSON are authoring formats, not claimed native quiz-import templates. Follow the supported editor workflow and preview before publishing.

**Preparation status:** The [Chapter Quizzes folder](https://drive.google.com/drive/folders/1NE5Q2WM2RGIHutk70-HlOX-Ouj66thbu) holds the combined questions, separate instructor key, entry guide and a ZIP with 21 chapter packs. Nothing has been entered or published in Udemy. Remaining review and release tasks stay in the launch checklist in Udemy Resources.

## Udemy publishing resources

The production and launch checklist now lives in the internal [Udemy Resources folder](https://drive.google.com/drive/folders/1kNw1Vh0mxAy7aphHHxtbbTxuM9sKNBVa), alongside the landing-page draft, pricing research, learner messages, course-image draft, expanded instructor profile and complete chapter quiz draft bank with a separate instructor key. Use the [launch checklist](https://drive.google.com/file/d/1kersEhUOZULX-TtSYBnR3tHZm1EjN5s2/view) to track readiness rather than duplicate it in this course plan.

Sreenivas owns all video work. Non-video preparation is in draft review; account/private-information steps and final publication remain owner decisions. Review outreach and promotion-code planning are deferred. [Udemy landing-page guidance](https://teach.udemy.com/publishing/create-your-course-landing-page/).

## Chapter map

Six sections and twenty-one chapters. Chapters may contain several short lectures.

| Section | Chapters | Focus |
|---|---|---|
| A | 1 | Course Introduction |
| B | 2–5 | Anatomy |
| C | 6–12 | Core Components |
| D | 13–15 | Observability, Evaluation and Security |
| E | 16–18 | Advanced Agent Topics |
| F | 19–21 | Agentic Platforms |

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

**Demo and learner practice:** Demonstrate the marketplace journey from purchase through delivery, an early payout-hold rejection and a manually eligible payout. Explain business journeys and local/cloud architecture. The support-agent walkthrough belongs in Chapter 5: Your First Agent, End to End.

**Workspace:** Main marketplace UI: http://localhost:5178/; database market. Use the interactive business data for the application demonstration.

### 4. Course Setup

**Learning objective:** Start the local reference application and verify services, credentials and model access.

**Demo and learner practice:** Follow the Mac-first written setup guide for Git, Docker Compose, editor/Python, provider keys, demo accounts, costs, seeded data and reset checks. Linux and Windows notes are separate. Native platform setup belongs in later chapters.

**Workspace:** Use app/LOCAL-SETUP.md. It identifies the main UI, Test workspace and shared services. Show the five-group container map and local CPU/memory snapshot alongside the setup walkthrough; verify each service before its activity.

**Guide:** [Local setup](../app/LOCAL-SETUP.md).

### 5. Your First Agent, End to End

**Learning objective:** Follow one OpenAI Agents SDK investigation through code, model/tool calls, evidence, final answer and Langfuse.

**Demo and learner practice:** Instructor: ask a current-state question, make a purchase, ask again and inspect fresh evidence and the business revision. Learner: first complete one purchase, delivery and payout journey in the regular marketplace. Then ask support questions, inspect traces and compare balances around a second fresh purchase. Saved 18-case results introduce correctness checking; full evaluation is Chapter 14: Evaluation.

**Workspace:** Instructor: main UI http://localhost:5178/, database market. Learner: regular marketplace http://localhost:5178/, database market. Trace inspection: http://localhost:3000, project marketplace-support.

**Materials:** [Exercise](exercises/first-agent/exercise.md) · [Answers](exercises/first-agent/solutions/answers.md)

**Result boundary:** The saved 18-case comparison graded Nano 11 correct / 4 partial / 3 incorrect and GPT-5.4 17 / 1 / 0. Two follow-up cases generated 20 answers per model; the counts are case grades. [Saved comparison](../app/results/core18-history-v3-2026-10-01/comparison.html).

## C. Core Components

### 6. Model and Gateway

**Learning objective:** Explain model capability, cost and latency, and how a gateway centralizes access through aliases, scoped keys and workload attribution.

**Demo and learner practice:** Swap a model behind an alias while holding questions and fixtures fixed. The instructor can now use the Test workspace Support model mapping selector: it changes the actual database-managed `support-model-test` definition while fixed Test Support/Operator keys retain only that alias plus embedding. Main support remains separate. Tour virtual keys, models, guardrails and observability before the before/after question; restore GPT-5.4 afterward. Learner practice uses the same Test UI; the additional alias task uses LiteLLM Playground and the optional response-cache task uses the Test checkbox. Cache controls are only toured during the instructor demo, not exercised hands-on. Inspect correctness, tool calls, usage, estimated cost and latency. Explain retries, fallbacks, budgets and caching as capabilities; distinguish gateway response caching from provider prompt caching.

**Workspace:** Normal Test UI http://127.0.0.1:5179/, database market_test; LiteLLM http://localhost:4000/ui/ for alias creation and Playground; Langfuse http://localhost:3000. No additional application or database is required. Record the slide walkthrough and instructor demo separately; leave response caching Off outside the optional learner comparison.

**Materials:** [Exercise](exercises/model-and-gateway/exercise.md) · [Answers](exercises/model-and-gateway/solutions/answers.md)

### 7. Prompt and Context

**Learning objective:** Identify which instructions, business definitions, schema/catalog context, metadata and evidence a question needs.

**Demo and learner practice:** Map context and compare catalog suppression/restoration on business questions and policy suppression/restoration on policy questions. Keep the fixture, revision and clock fixed; use fresh conversations. Record missing explanations, qualified answers, guessed queries and failures rather than assume all context removal must fail.

**Workspace:** Test workspace http://127.0.0.1:5179/, database market_test; Support with OpenAI Agents SDK and memory off. Inspect marketplace-support traces in local Langfuse.

**Materials:** [Exercise](exercises/prompt-and-context/exercise.md) · [Answers](exercises/prompt-and-context/solutions/answers.md)

**Takeaway:** Missing catalog or policy context can change completeness, uncertainty or execution; a successful query alone does not show that all necessary context was supplied.

### 8. Tools and MCP

**Learning objective:** Distinguish tool contract, implementation and transport, including SQL validation, read-only permissions, evidence references and limits.

**Demo and learner practice:** Inspect business, retrieval and memory tools; compare stdio and remote HTTP MCP. Core learners repeat the tool investigation. The optional developer extension adds a seller-balance tool to an isolated copy of the existing MCP server, using two templates and a terminal test.

**Workspace:** Test workspace http://127.0.0.1:5179/, database market_test. The code extension uses a temporary backend-package copy and the read-only Test database connection, without editing or restarting either running application. Optional cloud work requires the learner’s own deployment and database.

**Materials:** [Exercise](exercises/tools-and-mcp/exercise.md) · [Answers](exercises/tools-and-mcp/solutions/answers.md)

### 9. Knowledge and Retrieval (RAG)

**Learning objective:** Separate retrieval correctness from answer correctness when combining business records with versioned policy evidence.

**Demo and learner practice:** Explain ingestion, embeddings, vector retrieval and optional reranking, then inspect marketplace evidence. Use isolated Test workspace RAG controls and the main question box, with automatic cached indexing, to compare V1, stale indexed V1 and reindexed V2. Compare paragraph/overlap at top K one/four using adjacent policy facts; learners use the UI without editing files or running commands.

**Workspace:** Test workspace http://127.0.0.1:5179/, market_test. Policy-version comparisons apply isolated lab policies to a prepared recorded Test order. Chunking compares policy-only Amber product questions across paragraph/overlap and one/four passages. All learner steps run in the main Support UI; the learner folder contains only the exercise and worked answers.

**Materials:** [Exercise](exercises/knowledge-and-retrieval/exercise.md) · [Answers](exercises/knowledge-and-retrieval/solutions/answers.md)

**Takeaway:** Source changes require reindexing. Chunk boundaries and passage limits affect evidence coverage; overlap and more context are not universally better.

### 10. Session State

**Learning objective:** Distinguish retained conversation history, per-run state and persistent memory, including isolation and evidence freshness.

**Demo and learner practice:** Show a follow-up, reuse of complete evidence at an unchanged revision, fresh evidence after a business-state change, and compare two-, six- and eight-block windows using the same label-recall question. Learners repeat those four checks, then keep the two-block conversation open, show the label is absent from its input, manually compact full stored history, and ask again to compare recall from the summary.

**Workspace:** Test workspace http://127.0.0.1:5179/, market_test. Session history controls apply to the owned local SDK conversation. Reset to defaults restores the six-block baseline without opening a new conversation.

**Materials:** [Exercise](exercises/session-state/exercise.md) · [Answers](exercises/session-state/solutions/answers.md)

**Takeaway:** Stored history and model-visible history differ. Summary strategies are alternatives to measure, not guaranteed token savings.

### 11. The Agent Loop with OpenAI Agents SDK

**Learning objective:** Explain the model/tool loop and SDK capabilities: agent setup, execution and streaming, tools/MCP, state/results, hooks/tracing, guardrails, human review and orchestration.

**Demo and learner practice:** Map Agent, Runner and Hooks to normal execution, a controlled temporary tool-error recovery, and a turn-limit stop. Core learners annotate model/tool counts, evidence and stopping. Learners run and explain a supplied custom runner loop with a real model and a local sample tool; no file edits are required. SDK guardrails are a separate integration point from our gateway privacy/injection checks.

**Workspace:** Standard Test workspace http://127.0.0.1:5179/, database market_test → Support → Workspace options → Agent loop. Normal, Fail first business query and Stop after one model step apply per question. Use fresh conversations when changing modes; reset restores Normal. The custom-loop command runs in a temporary Test backend container; the legacy lab is not required.

**Materials:** [Exercise](exercises/agent-loop/exercise.md) · [Answers](exercises/agent-loop/solutions/answers.md)

### 12. Runtime and Hosting

**Learning objective:** Separate Agent SDK choice from hosting, and distinguish infrastructure responsibilities from agent-system capabilities.

**Core topics:** Agent SDK, runtime and hosting definitions; self-managed and managed options; infrastructure and agent capabilities; representative SDKs and managed offerings; local Docker and full-cloud architecture differences.

## D. Observability, Evaluation and Security

### 13. Observability: Tracing and Monitoring

**Learning objective:** Explain one run through tracing and behavior over time through monitoring; assess observability platforms by practical capabilities and boundaries.

**Instructor demo:** Investigate a high-P99 day through original traces; compare the Cedar clarification case where Nano scores 0 and GPT-5.4 scores 2, following the evaluation result to original queries; create a daily estimated-model-cost widget. Briefly orient learners to Home monitoring views. Native platform telemetry is covered in platform chapters.

**User exercise:** Create one token-usage dashboard, calculate average daily tokens per investigation from matching token sums and distinct investigation counts, then explain a high-average day using original trace evidence.

**Workspace:** Local Langfuse http://localhost:3000, project marketplace-support. This is a recorded-evidence investigation; no business database changes, uploads or new model calls are required. Use existing support recordings and the historical model-comparison results.

**Materials:** [Exercise](exercises/observability/exercise.md) · [Answers](exercises/observability/solutions/answers.md)

### 14. Evaluation

**Learning objective:** Distinguish golden references, deterministic checks, provisional LLM judgments, human review and calibrated judge agreement.

**Demo and learner practice:** Instructor: inspect five saved answers and human/judge grades, then three structured answers with native TypeScript evaluation. Learners human-grade the five supplied answers and import their grades, then import and inspect the three structured outputs using the configured native evaluator. No paid model calls are needed. Repeated trials and online evaluation are concepts, not additional required implementation exercises.

**Workspace:** Local Langfuse http://localhost:3000, project marketplace-support; supplied answer fixtures and repository-root import commands. Reuse Chapter14 structured order comparison with its worker/dispatcher. No marketplace UI or business database is required.

**Materials:** [Exercise](exercises/evaluation/exercise.md) · [Answers](exercises/evaluation/solutions/answers.md) · [Instructor demo](exercises/evaluation/exercise.md#instructor-demo)

**Takeaway:** Judge agreement is not model accuracy, and feedback is not factual correctness. Human review and deterministic checks have different roles; a single trial does not establish consistency. [Calibration evidence](../app/results/calibration-v3-2026-09-29/CALIBRATION-SUMMARY.md).

### 15. Guardrails and Agent Security

**Learning objective:** Explain privacy, prompt injection, source authority, tool enforcement and protection boundaries through bounded examples.

**Demo and learner practice:** Run input/output masking, a sensitive-card blocking case, a retrieved instruction-attack case and a source-authority Off/On comparison with a forged policy exception. Distinguish detector decisions, model behavior, source-authority guidance and enforced read-only tools. Teach prevention, detection and response without claiming complete OWASP coverage.

**Workspace:** Test Support http://127.0.0.1:5179/, market_test; OpenAI Agents SDK, memory off and prescribed guardrail/source-authority settings. Local Langfuse marketplace-support. Use isolated policy fixtures and cleanup instructions.

**Materials:** [Exercise](exercises/guardrails-security/exercise.md) · [Answers](exercises/guardrails-security/solutions/answers.md) · [Instructor demo](exercises/guardrails-security/exercise.md#instructor-demo)

## E. Advanced Agent Topics

### 16. Model Routing

**Learning objective:** Define routing, model pool, selection policy and scope before applying them to experiments.

**Demo and learner practice:** Explain conversation, question, model-call and named-stage scope, caching as a design consideration, and application versus gateway routing. Present the historical 18-case classifier and six-conversation studies with small-sample limits. Live demo compares native LiteLLM keyword and LLM policies, then LLM conversation/question scope; learner lab adds trained heuristic v2 and documents gateway decisions in Langfuse.

**Workspace:** Test workspace http://127.0.0.1:5179/, market_test; Support with OpenAI Agents SDK, routing controls, memory/guardrails off and source authority on. Keyword and heuristic use per-question scope; LLM uses either scope.

**Materials:** [Exercise](exercises/model-routing/exercise.md) · [Answers](exercises/model-routing/solutions/answers.md) · [Instructor demo](exercises/model-routing/instructor-demo.md)

**Historical conclusion:** Business-context classifier configurations did better on these tested cases. Both scope policies reduced cost but lowered fully correct conversations versus always GPT-5 (4/6 versus 6/6); neither improved this pilot’s quality/cost tradeoff. Larger samples and repeated trials are needed. Cache reuse can affect cost/latency, especially across a conversation; no isolated cache benefit is claimed.

### 17. Agent Design Patterns

**Learning objective:** Choose workflow, single-agent or hybrid control, then justify additional roles through independent work, distinct evidence/capability or system boundaries.

**Demo and learner practice:** Teach workflow patterns before multi-agent roles, concrete examples, four linked use cases and A2A across systems. Present the untested serial records/policy split separately from the measured seller-worker and reviewer studies. Demo a hybrid multi-agent workflow: generation, evidence/context handoff, structured review, code-controlled branch and one optional correction. Learners repeat the demo with another question and compare Nano alone, Nano review and GPT-5.4 review. An optional follow-up checks context handoff to the reviewer.

**Workspace:** Test workspace http://127.0.0.1:5179/, market_test; Support with OpenAI Agents SDK and Agent design demo controls. Routing and memory off. Follow Generate draft, Review draft, Workflow decision and optional Correct draft in local Langfuse.

**Materials:** [Exercise](exercises/agent-design-patterns/exercise.md) · [Answers](exercises/agent-design-patterns/solutions/answers.md) · [Instructor demo](exercises/agent-design-patterns/instructor-demo.md)

**Historical conclusion:** The serial business-records/policy split was not tested because no clear benefit justified the handoffs. Seller workers added coordination overhead and one run failed to complete; parallel tool calls can sometimes supply the needed concurrency. Stronger review improved Nano’s fully correct count from 11/18 to 14/18, below GPT-5.4 alone at 17/18. These bounded findings justify checking reviewer capability and coordination cost. [Live controller](../app/backend/marketplace/agent_design_demo.py) · [Seller experiment](../app/scripts/payout-orchestration.py) · [Reviewer experiment](../app/scripts/reviewer-workflow-core18.py).

### 18. Short-term and long-term memory

**Learning objective:** Distinguish conversation context from retained knowledge, explain what memory should preserve and when it should be used, and inspect formation, retrieval and lifecycle across conversations.

**Lesson scope:** Explain short-term context and three long-term purposes with marketplace examples: semantic preferences, episodic investigation checkpoints and procedural checklists. Design memory by storage, trusted user scope, save trigger, retained content, retrieval, update/retention and deletion. Choose foreground or background memory writes; our integration retrieves during the answer and extracts completed conversations in the background. Trace the loop from conversation content through formation, later retrieval, answer use, update and forgetting. Stored history and the bounded context sent to the model are different; deleting a memory does not delete historical chat.

**Demo and learner practice:** Follow same-conversation context and a fresh conversation, then explicit internal saving and automatic Mem0 extraction without a save request. Inspect actual saved entries, cross-conversation recall, a paraphrased query, edit/forget, current-instruction precedence, fresh business evidence and user isolation. Learners document settings, stored entries, retrieved evidence, final answers and the question/extraction trace links. Finish by draining pending lab jobs and deleting only named lab records, without submitting another conversation that restates the deleted memory.

**Workspace:** Test workspace http://127.0.0.1:5179/, database market_test; Support with OpenAI Agents SDK. Use the Internal memory/Mem0 selector. Normal support model, routing and Agent design demo off, clean policy and source-authority context on; the main marketplace on 5178 and Agent Loop lab on 5181 do not enable this Mem0 lab. Trace inspection: local Langfuse http://localhost:3000/, project marketplace-support.

**Materials:** [Exercise](exercises/short-and-long-term-memory/exercise.md) · [Answers](exercises/short-and-long-term-memory/solutions/answers.md) · [Instructor demo](exercises/short-and-long-term-memory/instructor-demo.md)

**Implemented comparison:** Internal memory uses application-owned PostgreSQL records, trusted owner/provenance, bounded keyword search and version-checked edits through local stdio MCP tools. Saving requires explicit user intent and per-question write permission. The deployed hosted Mem0 integration queues completed turns at New conversation or the configured idle trigger. A conservative user-authored durable-intent gate skips routine business/recall-only turns as `noop`. Eligible full user/assistant context goes to REST V3 add with per-request `marketplace-durable-context-v2` retention guidelines; shared project settings are unchanged. Hosted HTTPS MCP supplies search/list/edit/delete and extraction status polling. Retrieval is a separate agent read operation. Turning retrieval off does not disable extraction while Mem0 is selected. Provider categories are preserved rather than forced into our three-purpose taxonomy; external records do not inherit internal version semantics.

**Retrieval design:** Both enabled providers are instructed to search presentation preferences plus topic/checklist/checkpoint before every business question. A retrieved user layout overrides default Field/Details formatting; a current explicit user request overrides that preference. The agent still selects tools; no forced application preload is used. Current [Mem0 Platform graph documentation](https://docs.mem0.ai/platform/features/graph-memory) describes always-on entity extraction/linking and a retrieval boost combined with semantic and keyword scores. Internal memory has no custom graph implementation. The lab compares the observed provider behavior; it does not isolate the graph contribution, rank providers generally or inspect their physical storage.

**Verified boundary and takeaway:** Core internal save/recall/lifecycle checks and deployed Mem0 formation, business-question preference use, paraphrased retrieval, edit/delete, trusted user isolation and trace handoffs were verified. Isolated Internal/Mem0 status runs both retrieved and applied a saved preference; the user confirmed the deployed retrieval fix. A provider intermittently recreated a deleted preference from business-only input; audited payloads contained no such preference and the provider-internal cause remains unknown. The gate prevents that business-only submission path, without guaranteeing perfect grounding or cross-batch deduplication for eligible chats. The default 900-second idle trigger has automated coverage; the live rehearsal used New conversation. Formation, retrieval and correct use are separate checks: an acknowledgement is not proof of storage, a queued operation is not a confirmed save, and retrieved memory is not authoritative current business evidence. Current instructions override preferences; live records and applicable policy override historical checkpoints/checklists. Broader repeated and held-out evaluation, automatic history compaction, shared procedures and automatic expiry/consolidation remain outside this lab.

**Code and evidence:** [Internal memory](../app/backend/marketplace/memory.py) · [Mem0 adapter and background jobs](../app/backend/marketplace/mem0_provider.py) · [Integration and verification boundaries](../app/docs/MEM0-INTEGRATION.md) · [Memory status and historical evidence](../app/docs/MEMORY-STATUS.md). Historical [eight-scenario / 19-question results](../app/results/memory-repeatable-20261003T093153094486Z/REPORT.md) complement the current lab; the [24-case catalogue](../app/eval/memory-v2/README.md) is a catalogue, not a claim that every case ran.

---

## F. Agentic Platforms

Use familiar support tasks to compare component ownership, capabilities, costs, engineering effort and control. The standalone Google and Lyzr Basics agents use the same fictional order source through different native mechanisms. Their optional cloud integrations use business MCP/data boundaries. Disclose model, prompt, context, tool, fixture and hosting differences before comparing outcomes.

**Orientation:** Recap the SDK, Google and Lyzr approaches, then compare cloud providers, model-provider platforms, framework-associated platforms and integrated builders. Map their capabilities onto models, execution frameworks, managed runtime/services, builders and governance. These categories overlap; model choice, deployment choice and governance over existing agents are separate decisions.

**Teaching material:** The combined Chapter 21: Choosing an Agent Platform deck and speaker notes hold platform landscape/customer fit, component ownership and decision criteria. Historical implementation evidence remains in [MILESTONE-LOG.md](../MILESTONE-LOG.md); platform-specific setup remains in the relevant chapter materials.

### 19. Google Gemini Enterprise Agent Platform

**Reviewed lesson scope:** Introduce the managed platform's purpose, benefits and tradeoffs; map familiar agent components in one architecture diagram; distinguish self-managed open-source ADK from Managed Agent Platform; explain component cost drivers, including evaluation separately from observability. Selected services can be combined; avoid blanket model, external-memory or data-location restrictions.

- **Core lesson and demonstration:** Deploy the separate **Support Agent Basics** agent, with packaged fictional orders and native `lookup_order`. Use native Google Playground to inspect record evidence, a same-session follow-up, an unknown order, native session/trace events and separately triggered Memory Bank generation/recall. No marketplace UI, SQL, MCP middleware, tunnel or Cloud SQL is required for Basics.
- **Standalone practice:** Follow the chapter's concise setup guide for prerequisites, editable environment settings, installation and test/deploy commands. The instructor guide starts after deployment and supplies the exact questions and observations. Reference answers separate fictional source facts from model behavior.
- **Optional adventurous exercise:** Build the full cloud integration connecting the chat application/backend and business data/MCP to a Google-hosted agent, using the linked cloud instructions. This is separate from standalone Basics and preserves the existing Marketplace Support ADK Lab.
- **Current verification:** Basics has been created. Native Playground product lookup, same-session held-payout follow-up, missing-record result and model/tool traces have been checked. Memory Bank generation and scoped stored-preference retrieval passed, including an empty result for another test user. Fresh-session preference preload and answer use were subsequently verified in a recovered native trace after the CLI retry timed out; this is not a passed CLI verification suite. The existing cloud integration has its own historical evidence; it is not a fresh learner-project installation rehearsal.

**Materials:** [Setup guide](exercises/google-agent-platform/setup-guide.md) · [Instructor walkthrough](exercises/google-agent-platform/instructor-demo.md) · [Exercise](exercises/google-agent-platform/exercise.md) · [Separate answers](exercises/google-agent-platform/solutions/answers.md) · [Basics code and instructions](../app/google/basics/README.md) · [Optional integration walkthrough](GOOGLE-PLATFORM-PLAN.md).

### 20. Lyzr Agent Studio

- **Lesson:** Purpose and customer fit, product stack (Framework, Studio, ADK/REST, Architect, Cognis and separate Opencontroller governance), deployment/model/data boundaries, benefits/tradeoffs and cost drivers. Documented enterprise choices are distinct from the hosted configuration rehearsed here.
- **Core demo:** A separate **Support Agent Basics** in native Studio/Playground, using the same fictional JSON source as Google Basics converted deterministically to a native TXT Knowledge Base. Inspect retrieval, a same-session follow-up, missing records and native execution evidence; distinguish KB retrieval from Google's Python lookup tool. Native memory inspection is optional and evidence-bounded.
- **Setup:** [Separate setup guide](exercises/lyzr-agent-studio/setup-guide.md), followed by [instructor demo](exercises/lyzr-agent-studio/instructor-demo.md). No marketplace, SQL, MCP or tunnel is needed for Basics. Local package checks and bounded hosted API known-order, missing-ID and same-session follow-up checks pass. Native Cognis is enabled with Cross Session OFF; native Playground known-order, same-chat and missing-ID checks passed with actual KB source chunks visible in Activity. Optional owner-scoped native Cognis cross-session API checks verified automatic extraction, record provenance, fresh recall and answer use, plus one other-owner negative check. Cross Session OFF was restored after the experiment. Cross-session Playground behavior and general isolation/CRUD guarantees are not established.
- **Optional exercise:** One [full cloud integration exercise](exercises/lyzr-agent-studio/exercise.md), following [the Lyzr platform setup plan](LYZR-PLATFORM-PLAN.md) after completed Cloud Setup: cloud chat/backend calls a separate Lyzr marketplace agent, which calls the GCP MCP/data backend. Preserve the standalone Basics and existing instructor agents. [Separate answers](exercises/lyzr-agent-studio/solutions/answers.md).
- **Reference:** [Existing Lyzr integration](../app/lyzr/README.md) preserves historical configurations and bounded results. Earlier local-tunnel results do not prove a fresh learner cloud deployment.

### 21. Choosing an Agent Platform

**Reviewed closing lesson:** A 13-slide synthesis of the approaches used in the course, current platform capabilities and a practical selection method. This is a documentation-based comparison and decision exercise, without another deployment lab.

- **Learning objective:** Match application needs to platform capabilities, component ownership, operating responsibility and cost. Distinguish an agent framework from an integrated agent platform and a provider-managed harness.
- **Provider types and fit:** Cloud platforms (Google Agent Platform, AWS Bedrock AgentCore, Microsoft Foundry Agent Service); model-provider platforms (OpenAI Agents API, Claude Managed Agents); framework-associated platforms (LangGraph/LangSmith Deployment, CrewAI); integrated builders (Lyzr Agent Studio, Dify). Prior cloud/model/framework commitments and reduced assembly needs guide a shortlist; private/self-hosted choices depend on the actual product edition.
- **Capability comparisons:** Review familiar layers, then concrete AWS/Microsoft, OpenAI/Claude and LangSmith/CrewAI/Dify features. Include execution, model/framework access, tools, state/memory, identity and observability/evaluation where documented. Sources and material limits are in speaker notes; no untested feature parity or quality ranking is implied.
- **Integration and costs:** Use a stable application contract with provider-specific runtime adapters; reuse MCP at the business-tool boundary while retaining backend permissions. Compare inference, execution, persistence, tools/networking, observability/evaluation, subscriptions/licenses and explicit team costs for development, integration, maintenance and on-call support.
- **Selection process:** State the task, acceptable failures and hard constraints; shortlist two options; compare responsibilities, data paths and total cost; run the same useful trial; decide and record unknowns. A separate conditional flowchart maps those requirements and prior-stack preferences to provider types and named product candidates.
- **Learner exercise:** Write a short decision using requirements, a two-option component-ownership comparison and a recommendation supported by sources, tradeoffs and remaining validation. The [learner worksheet](exercises/choosing-an-agent-platform/exercise.md) and [separate reference answers](exercises/choosing-an-agent-platform/solutions/answers.md) are in the exercise package; speaker notes retain the instructor walkthrough. No new cloud account or deployment is required.
- **Closing:** A concise Recap, with the optional action to apply the decision method to the learner's own agent. There is no following chapter.
- **Evidence boundary:** SDK/Google/Lyzr results are bounded integration evidence; the other offerings use dated official documentation. Recheck account/region/deployment options and commercial terms. Different models, prompts, contexts, tools, fixtures and memory policies prevent a universal winner claim.
- **Materials:** [Chapter 21 deck](https://docs.google.com/presentation/d/17AXM8BjDRNuc53p1NGmcE9Mh8lK7cMfF/edit) · [Speaker notes](https://drive.google.com/file/d/1Jbn7KL5nADFuwEbXiMqPhlfZqcT1pTC_/view) · [HTML review](https://drive.google.com/file/d/1ebBuCxTN_8j5pXhOikqODQebKyM3jmxc/view). Historical platform experiments remain in [MILESTONE-LOG.md](../MILESTONE-LOG.md).

---

## Delivery and release checks

The required release retains all six sections and twenty-one chapters, including multi-agent design and memory. Google and Lyzr are the hands-on platform tracks; the closing lesson uses documentation, course evidence and a platform-decision exercise. Additional AWS/Claude/Microsoft/OpenAI managed-runtime deployment labs are outside this release.

Before recording and release, rehearse the written setup on a clean machine, verify current model availability and lab costs, and provide saved evidence for learners limiting paid calls. Record and edit chapter lectures after their materials and learner paths are reviewed. Record the welcome last; agree the separate promotional video’s content before recording it. Managed-platform lessons need dated sources and current setup checks.

Future model migration or broader experiments must preserve dated reports and state which configuration changed. Keep the reviewed lesson scope and explicit verification limits current without restoring superseded planning discussions.
