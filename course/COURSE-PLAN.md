# Inside AI Agent Systems: From Components to Platforms

**Subtitle:** Understand, build and evaluate AI agents through hands-on experiments, and choose the right platform for your needs.

**Reviewer-facing outline:** [Google Doc — course outline for feedback](https://docs.google.com/document/d/1rcXN8C5P0o7AqQWdzh7CVFlvRq1WJRGLUA4o-GSCPZc/edit). This separate outline omits internal delivery status, authoring notes and release-version planning.

**Status:** agreed section/chapter structure and living progress map, updated October 10, 2026; Tracing and Monitoring consolidated (welcome/setup and chapter 3 opening sequence added; guardrails/security consolidated and numbered sections synchronized). Target launch is late November or December 2026.
**Owner:** Sreenivas Makam. This plan was drafted with Claude and is not an implementation spec. The build record stays in [MILESTONE-LOG.md](../MILESTONE-LOG.md) and [SPECIFICATION.md](../SPECIFICATION.md).

## Positioning

**Promise:** build and understand an AI agent system through one realistic marketplace support application. Change its AI components, measure the effects, and learn which responsibilities an AI platform provides. Learners compare design choices with evidence rather than opinion.

**Scope boundary:** this is an AI-system learning course, not a production-readiness course. General infrastructure engineering, identity/authorization implementation and broad security operations are outside the teaching scope. Keep the baseline application’s existing safeguards and explain necessary setup briefly. AI-specific guardrails, tool constraints, prompt injection, context isolation and memory behavior remain relevant learning topics.

**Audience:** developers who have built a first agent, for example after a framework-tour course, and now need it to work reliably on business data. It is the course *after* a learner's first agent course.

**Prerequisites:** Python, basic SQL, Docker, and familiarity with calling an LLM API.

**Current baseline — October 8, 2026:** GPT-5.4 is the default interactive support model. Bounded persistent-memory and multi-agent/reviewer-workflow implementations are available; completed comparisons and their limits are documented in chapters 17 and 16. References to Nano as the default in older experiment notes describe the configuration at that time. Migration away from Nano for remaining comparison aliases and teaching labs is deferred to later model/chapter preparation; preserve historical Nano results.

**What sets it apart**, based on the Udemy scan of 30 Sep 2026:
- **One stateful business system throughout.** Orders, payouts, refunds and versioned policies, not a new toy app every section.
- **Evaluation as the backbone.** A gold set, deterministic checks and an LLM judge calibrated against human grades.
- **Advanced design choices run as experiments.** The course shows what a change did to quality, cost and latency, not what it should do.
- **Honest failure analysis.** Real wrong answers are diagnosed step by step, including a hypothesis that did not explain the observed failure.
- **The same agent on several platforms.** Use shared tasks, tool contracts and evaluation criteria across the OpenAI SDK baseline, Gemini and Lyzr tracks. Distinguish changes in hosting from changes in the model, framework or managed components.

**Framing rule:** teach the decision process and don't crown a winner. Present model-specific numbers as dated case studies.

## How to use and maintain this outline

This is the **current chapter-organized progress map**. Read each chapter's objective
and proposed lab, then its dated **Progress and evidence** block for what exists,
what we learned, supporting tests/reports, hands-on readiness and pending work.
The [milestone log](../MILESTONE-LOG.md) remains chronological and preserves the
learning journey; this document maps that history to the latest course plan.
The Google review outline stays audience-facing and does not receive internal
progress details as part of this update.

After every meaningful milestone, in the same documentation update:

1. Append the dated milestone; preserve earlier results and corrections.
2. Refresh each affected chapter here: learning, implemented/measured state,
   exact evidence links, hands-on readiness, pending items and last update date.
3. If a shared component changes, mark downstream experiments that need reruns.
   Old reports remain valid for their versions, not automatically for current code.
4. Distinguish implementation, tests run, comparisons measured and learner lab
   packaging. Do not mark a proposed experiment complete because nearby tests pass.
5. Record pending work here and remove it only with linked evidence of completion.
   Update the specification only when application requirements change.

### At-a-glance chapter map

**Updated October 10, 2026:** Six sections, twenty-two chapters; Tracing and Monitoring merged into Observability. Chapters may contain multiple short lectures; lecture breakdown is deferred to recording preparation. Detailed evidence and remaining work stay under each chapter below.

| Section | Chapter | Title |
|---|---|---|
| A — Course Introduction | 1 | Welcome and Course Roadmap |
| B — Anatomy | 2 | The Components of an Agent |
| B — Anatomy | 3 | The Marketplace Application |
| B — Anatomy | 4 | Course Setup |
| B — Anatomy | 5 | Your First Agent, End to End |
| C — Core Components | 6 | Model and Gateway |
| C — Core Components | 7 | Prompt and Context |
| C — Core Components | 8 | Tools and MCP |
| C — Core Components | 9 | Knowledge and Retrieval (RAG) |
| C — Core Components | 10 | Session State |
| C — Core Components | 11 | The Agent Loop with OpenAI Agents SDK |
| C — Core Components | 12 | Runtime and Hosting |
| D — Observability, Evaluation and Security | 13 | Observability: Tracing and Monitoring |
| D — Observability, Evaluation and Security | 14 | Evaluation |
| D — Observability, Evaluation and Security | 15 | Guardrails and Agent Security |
| E — Advanced Agent Topics | 16 | Model Routing |
| E — Advanced Agent Topics | 17 | Workflow vs Single Agent vs Multi-Agent |
| E — Advanced Agent Topics | 18 | Short-Term and Long-Term Memory |
| F — Agentic Platforms | 19 | Google Gemini Enterprise Agent Platform |
| F — Agentic Platforms | 20 | Lyzr Agent Studio |
| F — Agentic Platforms | 21 | Other Agent Platforms |
| F — Agentic Platforms | 22 | Choosing an Agent Platform |

## Lesson format

### Required format for every numbered lesson

**Agreed chapter structure — October 8, 2026:** From chapter 5 (the final Anatomy chapter) onward, use overview/explanation slides, a demonstration where appropriate, learner practice, and a closing recap covering what was learned and the next chapter. The Other Agent Platforms overview uses a comparison exercise rather than a deployment lab. Decide each exercise while preparing that chapter; do not freeze all exercises prematurely.

Chapter 1 is welcome and roadmap. Chapter 2 introduces components without a demo. Chapter 3 explains the marketplace and demonstrates the application. Chapter 4 is a Mac-focused setup orientation and verification walkthrough backed by the written guide, with separate Linux and Windows notes. Chapter 5 is demo-led: relevant code, model/tool calls, final answer and a small learner practice task.

**Current preparation scope:** Freeze slides, speaker notes and demo cues for Sections A and B after owner review. [Opening chapter materials](recording/sections-a-b/README.md) track the drafts. The [setup guide](../app/LOCAL-SETUP.md) is Mac-first; rehearse the same guide on a fresh Google Cloud Linux VM and record its actual coverage. A Linux run validates the shared container workflow, not a clean Mac or Windows installation. Learner repository publication remains separate.

For hands-on component and advanced chapters, provide a starting checkpoint, a meaningful change or investigation, observable evidence and an acceptance check. Keep model, fixture and questions fixed when an experiment does not intentionally change them. Introduce small known-answer checks in the first-agent chapter; teach the full evaluation method in Section D.

**Closing slide for every lesson** (agreed October 4, 2026): one slide titled "What you can do now, and what's next". The left side lists three or four things the learner can now do, phrased as abilities ("Follow one question through a trace…"), not topics covered. The right side previews the next chapter in two or three points. This replaces a separate "Up next" slide.

Objectives and “Lab and result” bullets describe the intended learner experience. Each chapter’s **Progress and evidence** block distinguishes completed implementation/experiments from proposed work and learner packaging. “Course-ready” additionally requires a tested learner path, lab instructions, verified result and recording material.

**Material ownership:** This outline is the planning source for each chapter demo and learner exercise. Slide decks contain presentation content only. Keep one separate Markdown speaker-notes file for each chapter. It contains slide-by-slide presentation notes, the demo walkthrough and cues, the learner exercise task, expected learner output and instructor solution/check. Keep distributed learner instructions and reference solutions separately organized under the chapter exercise materials.

### Draft learner exercise and solution organization — October 8, 2026

**For owner review; not finalized.** Chapters 6–22 below now have proposed learner exercises and solution deliverables. These are planning notes, not claims that learner instructions or solutions have been created or verified. Finalize each exercise during chapter preparation; preserve the existing experiment evidence and pending-work boundaries.

Aim for one core exercise per chapter, usually 15–30 minutes after setup, with an optional extension for learners who want to adapt it to their own application. Platform setup may take longer; distinguish setup time from exercise time. Learners may attempt the exercise independently or follow the worked solution.

Keep exercise instructions and solutions together under the relevant chapter, with solutions in a separate folder so learners can choose when to open them. Proposed package:

```text
course/exercises/chapter-06-model-and-gateway/
  exercise.md
  starter/                 # only when the exercise requires starter code/config
  solutions/
    README.md              # worked solution and expected observations
    changes.patch          # only when applicable
    example-results/       # only when useful and verified
```

Use starter files and patches only where there is code/configuration to change; worksheet and diagnosis exercises need a worked example instead. Each exercise and solution must explicitly name the UI URL/workspace, target database and cleanup/restoration steps. The default local learner path is the test UI (`http://127.0.0.1:5179/`) and disposable practice database `market_test`; main `market` and fixed evaluation baseline `market_eval` are separate. Name dedicated CLI/database labs and optional cloud environments explicitly. Code-changing exercises must explain how to restore original code/configuration and restart affected services; database cleanup does not revert source edits. Do not reset a shared practice database while anyone is using it.

Each exercise should state prerequisites, a starting checkpoint, the task, acceptance checks, expected time/cost and cleanup/reset steps where needed. Each solution should explain what changed, why and how to verify it, including expected facts/evidence rather than an identical model-generated answer. Keep credentials out of all distributed files. Use isolated learner/test fixtures for mutations and adversarial inputs; do not change shared demonstration agents or business data without an explicit setup step.

## Promotional preview — separate from course lessons

The promotional video is a separate recording from the welcome and course roadmap lesson, outside the numbered curriculum. The welcome is numbered chapter 1. Reuse suitable welcome footage for the preview, but tailor the welcome to enrolled students and the preview to prospective learners. **Content and script are still to be discussed and agreed before recording.** Record it after the chapter recordings are complete; it can be prepared at the same stage as the welcome video, but remains a separate deliverable.

## Status legend

- **Built** means implemented in the app with evidence in the milestone log.
- **Measured** means dated results exist for the archived configuration; it does not mean results apply to the latest code.
- **Partial** means some pieces exist.
- **To build** means no completed implementation/experiment is recorded.
- **Hands-on readiness** distinguishes an exercised engineering scenario from a learner-ready lab. No chapter is marked course-ready solely because code or results exist.

---

## A. Course Introduction

### 1. Welcome and Course Roadmap

Introduce the intended audience, what learners will be able to build and evaluate, and how the marketplace support assistant connects the course. Explain the roadmap: agent components, the reference application and first agent; component experiments; tracing, monitoring, evaluation and security; routing, multi-agent designs and memory; then platform tracks and the decision lesson. Distinguish required lessons from optional platform material.

Explain the prerequisites: Python, basic SQL, Docker and familiarity with an LLM API. Direct learners to the written setup lesson before attempting hands-on exercises.

**Recording plan:** Record the welcome and course roadmap after the chapter recordings are complete, so the introduction reflects the finished course. It is a course lesson, separate from the promotional preview.

- **Format:** Short orientation video; no technical lab or homework.

## B. Anatomy

The goal of this part is for learners to see the whole system before going deep on any part of it.

### 2. The Components of an Agent
- **Opening sequence:** Introduce the component map and explain how the pieces connect. No application demo or code walkthrough in this chapter.
- **Learning objective:** Explain the AI component boundaries and how a question flows through them.
- **Format:** Conceptual explanation with an architecture diagram; no hands-on lab required.
- **Covers:**
  - model and gateway
  - prompt
  - context
  - tools
  - knowledge (retrieval)
  - session
  - memory
  - orchestration (the agent loop)
  - guardrails (brief component-map mention; detailed teaching is in the combined Guardrails and Agent Security section)
  - runtime and hosting
  - identity as an existing application boundary, not an implementation lesson
  - observability and evaluation
- **Key distinction:** *Context* is what goes into one model call. *Session* is one conversation. *Memory* persists across conversations. (The two meanings of "runtime" moved to chapter 12 on October 4, 2026, where learners first need them.)
- **Ownership map:** who owns each component in our build (we own almost all of them). The same map is reused in Part F to show which components each platform takes over.
- **Status:** material exists in [SPECIFICATION.md §3](../SPECIFICATION.md). The diagram needs to be made course-ready.

#### Progress and evidence — October 1, 2026

- **Current state:** Built foundation; learner presentation pending.
- **What we learned / have available:** Component ownership is split between app, Agents SDK, MCP, gateway and telemetry. Session history, per-question snapshot and deliberate cross-session memory are different responsibilities.
- **Tests and references:** [Architecture and ownership](../SPECIFICATION.md#3-architecture-and-layer-ownership); [actual prompt/input walkthrough](../app/docs/PROMPT-AND-CATALOG.md); M01, M26–M30.
- **Hands-on readiness:** Trace one SQL question and one policy question from UI to model/tool result. Existing traces and walkthrough are available; annotated learner exercise/checkpoint still to prepare.
- **Pending:** Prepare the course diagram and a short guided trace with expected observations. Memory and multi-agent are now implemented as bounded learning experiments; introduce their roles here and explain their detailed architecture, results and limits in chapters 17 and 16. The dated October 1 progress block records the earlier preparation state.

### 3. The Marketplace Application
- **Learning objective:** Connect business-state changes to agent answers.
- **Format and result — agreed October 10:** Overview of the marketplace and its business journeys, with a brief marketplace-only live walkthrough: login, browse/select a product and place a purchase. Do not demonstrate or explain the support agent in this chapter. Learner setup comes next, and the marketplace-plus-agent end-to-end walkthrough belongs to chapter 5.
- **Covers:** buyers, sellers, orders, payments, payouts, refunds and versioned policy documents.
- **Why realistic data matters:** order value, platform fees and seller payable are different metrics with different grains. The double-counting example shows SQL that looks convincing and is wrong.
- **Chapter demo:** Show the simple marketplace flow through login, product selection and purchase. Explain the business entities and purchase/delivery/payout/refund flows using slides/diagrams. Keep support-agent questions, traces and before/after agent answers for chapter 5.
- **Status:** built (M01). Per-answer thumbs-up/down feedback is an application capability added October 8.

#### Progress and evidence — October 1, 2026

- **Current state:** Built; business journeys exercised.
- **What we learned / have available:** Order items, buyer capture, seller allocation, payout and refund are distinct. Manual state changes and the demo clock make before/after agent questions reproducible.
- **Tests and references:** [Buyer/seller/operator/support journeys](../app/USER-JOURNEYS.md); [business integration tests](../app/backend/tests/test_integration.py); [fixtures](../app/backend/marketplace/eval_fixtures.py); M01.
- **Available application evidence:** Happy purchase → dispatch → delivery → hold → payout, then return/refund and failure/retry journeys and checks exist. Chapter 3 uses only a simple marketplace walkthrough; the agent demonstration belongs to chapter 5.
- **Pending:** Align chapter 3 presentation and speaker notes with the marketplace-only scope and rehearse login/product selection/purchase. Prepare the separate agent walkthrough checkpoints under chapter 5.

#### Local and cloud deployment architecture — core paths verified October 8, 2026

The Marketplace lesson explains the shared application architecture and the local/cloud deployment paths. Initial local installation and startup belong to the written Course setup lesson. Shared hosting concepts belong to Runtime and hosting, and platform-specific Google/Lyzr setup stays in the corresponding platform chapters. Use the [architecture review document](MARKETPLACE-DEPLOYMENT-ARCHITECTURE.md) for the diagram, full component placement, identity/memory/telemetry boundaries, Terraform plan, deployment sequence and acceptance checks.

**Delivery choice agreed October 8:** Use the local SDK workspace for the main course demos. Use hosted agents and native telemetry in their platform chapters. Explain the three boundaries—chat application, agent runtime, business/MCP backend—and that placement of each is configurable. Changing runtime starts a fresh conversation, not a mid-session switch; it does not change the hosted middleware target. Local/cloud business baselines were aligned once to revision 24; they do not automatically synchronize. The user validated cloud SDK detailed Langfuse tracing; hosted platforms show a boundary trace there and their detailed calls in native telemetry.

- **Local — available:** cloned repository and Docker Compose, with local PostgreSQL, LiteLLM and Langfuse. A local middleware profile uses a laptop tunnel; Google and Lyzr are now set to the local middleware profile for local-first work.
- **Cloud — core deployment verified:** new GCP project with Cloud Run for the web app, HTTP MCP middleware and LiteLLM; Cloud SQL PostgreSQL and Secret Manager; Langfuse Cloud Japan for managed tracing. This replaces the single-VM proposal. No laptop or tunnel dependency.
- **Automation — deployed; learner rehearsal pending:** Terraform deployed the private foundation, web app, HTTP MCP and LiteLLM. Cloud SQL is now parked with activation policy NEVER; restart it before cloud use. Storage and retained backups remain billable, and public IPv4 remains disabled. Cloud login, SQL/RAG, short/long-term memory, feedback, privacy, injection blocking and Langfuse Cloud trace readback passed. See [deployment checkpoint](../app/cloud/README.md). Fresh-project and clean-machine setup rehearsals remain pending. Hosted ADK/Lyzr cloud connections and shared UI adapters are verified.
- **Shared interface — core paths validated:** runtime selector and backend adapters are implemented in local/cloud. Google question, follow-up and native memory save/fresh-session recall pass; Lyzr cloud order/follow-up and fresh-session memory recall pass; local Lyzr order-2 and same-session follow-up pass. Local Google ADC is configured; local main question/follow-up passed. Changing runtime starts a new conversation; native platform memory/telemetry are distinct, and hosted tool evidence remains in native traces.
- **Scope:** repeatable course hosting, not high availability or a production-readiness claim. Owner approved proceeding after architecture and cost discussion. Durable MCP investigation state and reliable trace export are implementation gates.

### 4. Course Setup — written walkthrough

**Setup ownership:** This initial lesson covers the local laptop installation, configuration, startup and first verification. Learners do not need to complete cloud/platform setup to begin the course. Google and Lyzr account/configuration steps are introduced in their respective platform chapters when needed; shared hosting concepts are explained in Runtime and hosting. The welcome video directs learners to the written instructions.

Use the canonical [local laptop setup guide](../app/LOCAL-SETUP.md) for prerequisites, startup, isolated test fixtures, smoke checks and troubleshooting. The guide is checked against current code; published clone/checkpoint details and clean-machine verification remain learner-release checks.

Provide written setup instructions and a checklist; a separate setup video is not required. Prepare these instructions before recording the hands-on chapters. Learners first watch the components explanation and marketplace demo, then complete setup before the first-agent practice or later exercises. The welcome video points learners to these instructions:

- Install Git, Docker with Compose, a code editor and Python for the course scripts. Node.js is needed only for frontend development outside containers; the marketplace UI is supplied.
- Clone a versioned course checkpoint and copy the environment template. Explain required OpenAI credentials, where to put keys, and which calls incur cost. OpenRouter or another judge provider is optional for the relevant experiments; cloud accounts are needed only for their platform tracks.
- Start the provided containers: marketplace UI/API, PostgreSQL with pgvector, LiteLLM, and Langfuse with its supporting services. Learners do not install each service separately.
- Show the service URLs, demo accounts, gateway aliases/keys, trace viewer, seed/reset commands and a first known-answer check.
- Publish tested machine requirements, dependency versions, setup troubleshooting and estimated per-lab API costs after clean-machine verification. Provide saved traces/results for the learning path without paid reruns.

### 5. First Agent, End to End
- **Reviewed packet — October 12:** Seven slides, a marketplace refresher in speaker notes, first before/after agent questions, code responsibilities, learner-task links, and the shared recap design. [Learner exercise](exercises/chapter-05-first-agent/exercise.md) and [separate worked solution](exercises/chapter-05-first-agent/solutions/README.md) include marketplace journeys. [Validation report](../app/results/chapter-05-validation-2026-10-12/REPORT.md) records six business scenarios and three live MCP questions/traces; UI recording rehearsal and GitHub publication remain pending.
- **Learning objective:** Run the baseline agent and verify its first answers.
- **Lab and result:** Configure the model alias, run a few known-answer questions and locate the corresponding traces.
- **Covers:** every component in its simplest form. OpenAI Agents SDK, one model through LiteLLM, the read-only SQL tool, document search and Langfuse tracing turned on.
- **Teaching format:** Demo-led throughout. Follow one question through the relevant agent code, model calls, tool calls, evidence and final answer; use the environment installed in chapter 4.
- **Chapter demo — agreed October 10:** In the main interactive marketplace, ask a current-state question (for example, a seller's captured amount and unpaid balance), inspect its evidence and Langfuse trace, then make a purchase from that seller through the buyer UI. Ask the same question again in the same conversation and inspect the new trace: confirm the business revision changed, fresh records were queried, and the answer reflects the purchase. Verify the expected change from the purchase amount, fee and allocation records; purchase alone does not imply a completed seller payout. Walk through the relevant agent code and model/tool calls alongside these two answers. Rehearse the exact seller, product and starting balances before recording; this is an agreed sequence, not a completed rehearsal.
- **Database separation — agreed October 10:** Use the main database for interactive purchase/delivery/refund/payout demos. Keep the test database's business fixture fixed for repeatable comparisons; experiments may vary model inputs/catalog responses without changing that business fixture. Record the test revision/clock and expected answers for each comparison. Experiment conversations and run telemetry are separate from business fixture immutability.
- **Learner practice:** Ask a different question, inspect its trace, and explain which components supplied the inputs and produced the answer. Include expected observations and an acceptance checklist.
- **Early evaluation:** introduce the latest nano/GPT-5.4 end-to-end baseline here, before changing individual components. Show two or three representative questions and the saved 18-case summary; learners need not pay to rerun the whole suite initially. Latest assistant review with user-approved cases 23/24: nano **11 correct / 4 partial / 3 incorrect**, GPT-5.4 **17 / 1 / 0**. These are grades across **18 cases**, with **20 generated answers per model** because two cases have follow-up turns; multi-turn cases must satisfy both turns. They are not answer-level counts or a general model ranking. [Answers and comparison](../app/results/core18-history-v3-2026-10-01/comparison.html).
- **Where the same experiment fits later:** chapter 6 discusses the model choice; chapters 7/10 explain the changed context/history; chapter 14 explains gold, deterministic checks, assistant versus human grading and why cases 23/24 were reclassified. This latest run did not use Claude as judge. Repeat small known-answer checks during component labs; keep the detailed evaluation method in Part D.
- **Status:** built (M01).

#### Progress and evidence — October 1, 2026

- **Current state:** Built and exercised; learner setup packaging pending.
- **What we learned / have available:** One read-only agent can combine SQL and policy evidence. Successful execution and a well-written answer do not establish correctness.
- **Tests and references:** [Run/setup instructions](../app/README.md); [latest 18-case paired regression](../app/results/core18-history-v3-2026-10-01/REPORT.md); M01, M30.
- **Hands-on readiness:** Run the stack, ask a known order question and a policy question, inspect evidence and trace. Existing implementation/results available; select a cheap three-question learner smoke test.
- **Pending:** Verify a fresh learner setup and capture expected outputs and costs; keep saved results as an alternative to paid reruns.

---

## C. Core Components

Each lesson explains the component, relevant tools/frameworks, our implementation and the key decision, then makes a small code/configuration change and checks the result. Small evaluation experiments belong inside the component lessons; Part D develops the complete evaluation method.
This part uses the **OpenAI Agents SDK baseline** throughout. That makes OpenAI the reference implementation, so it doesn't need its own track in Part F.

### 6. Model and gateway
- **Reviewed packet — October 12:** Twelve slides and matching HTML/notes. Learner guide has Part 1 (repeat demo) and Part 2 (additional alias/cache challenges), with no submission requirement. A dated [rehearsal report](../app/results/chapter-06-rehearsal-2026-10-12/REPORT.md) records stable-alias switching, Support/Operator attribution, five Langfuse traces, new alias and isolated response-cache checks. The local role-key implementation is applied and main/test state preserved. GitHub publication and instructor recording rehearsal remain pending.

**Draft learner practice — for review, not finalized:**

- **Learning objective:** Explain the model's role in interpreting requests and selecting tools, compare model capability, cost and latency, and understand how a gateway centralizes access while keeping model changes separate from application code.
- **Covers:** Provider translation; scoped keys and workload usage attribution; retries, timeouts, fallbacks and rate limits for reliability; usage estimates, budgets and alerts for spend management; and gateway response caching. Distinguish response caching from provider prompt caching. Introduce gateway guardrails and trace integrations briefly; later chapters develop them.
- **Chapter demo:** (1) Send the same application request through a stable alias, change the model behind that alias, and compare the answer and gateway usage, including estimated cost and latency. (2) Run requests as Support and Operator, using separate gateway identities with the same model aliases, and show usage and estimated spend attributed to each. Briefly tour the LiteLLM UI settings for retries, caching and alerts; this is a capability walkthrough, not a configuration experiment.
- **User exercises:** Repeat the model-alias swap with fixed questions and record answer quality, evidence, tool calls, usage, estimated cost and latency; then verify that Support and Operator usage is attributed separately. Optional developer extension: add a new model alias and call it through the gateway. Optional advanced exercise: enable response caching in a controlled setup, verify a same-model repeat is a cache hit and a model switch is a miss, then clear or expire the entry and verify a fresh model call. Explain when cached responses are useful and when fresh data is required.
- **Solution to prepare:** Configuration and verification steps, example comparison evidence and a worked attribution/cache result. Keep provider billing distinct from gateway usage attribution.
- **Decision:** A gateway versus calling providers directly. Model aliases simplify migration configuration; regression checks establish whether the replacement still works.
- **Status:** Built (M06); draft learner exercise and reference solution are in [course/exercises/chapter-06-model-and-gateway](exercises/chapter-06-model-and-gateway/). Rehearsal, including the Operator identity setup, remains pending.

#### Progress and evidence — October 1, 2026

- **Current state:** Built and measured.
- **What we learned / have available:** One shared LiteLLM gateway uses aliases and separate support/eval/judge virtual keys. Provider access, workload attribution and model quality are separate concerns.
- **Tests and references:** [Gateway setup and credentials configuration](../app/README.md); [M06 verification](../MILESTONE-LOG.md#m06--consolidate-model-access-into-one-gateway); [model comparison](../app/results/core18-history-v3-2026-10-01/comparison.html).
- **Hands-on readiness:** The model-alias comparison and support/evaluation/judge usage attribution have prior implementation evidence in M06. Support-versus-Operator attribution now has a distinct Operator gateway identity and passed the October 12 API/code rehearsal. Verify the installed UI screens for retry, caching and alerts before recording; do not imply those controls are configured in the course setup.
- **Pending:** Prepare and rehearse the fixed-request alias swap, Support/Operator cost attribution and brief settings tour. Verify current teaching models, prices and budgets before recording; avoid turning historical model choices into permanent recommendations.

### 7. Prompt and context

**Reviewed October 12: ten slides, matching HTML and speaker notes complete.**

- **Learning objective:** Separate stable instructions and changing context in the prompt, explain how ontology supplies business context, and understand the effect of missing context.
- **Covers:** Input structure, concise prompting practices with benefits and costs, review when the model changes, static versus dynamic inputs in our application, entity definitions and relationships, separately retrieved policies, and stable-prefix prompt caching. Measure cache reuse rather than assuming savings.
- **Context walkthrough:** Use separate definitions, relationship and policy questions. Inspect the actual catalog, SQL, current records and policy passages in the subsequent model inputs and traces. No combined question is assigned.
- **Comparison demo and learner practice:** In the test marketplace's OpenAI Agents SDK workspace, compare a catalog-dependent balance question and a policy-only question separately. Run normal, successful-empty and restored conditions. The UI controls start a fresh conversation with memory off. `get_catalog` returns success with null catalog data; `search_documents` returns success with empty passages. Tool schemas and other business tools remain available.
- **Observed catalog behavior:** The model inferred SQL from remaining prompt/tool hints. Some queries retrieved records and column names, while others failed. Two empty-catalog runs reached the eight-model-turn limit without a complete balance answer. Empty catalog did not make SQL construction impossible.
- **Observed policy behavior:** Reworded searches and an evidence fetch returned no passages. The model acknowledged that it could not verify the policy rather than inventing one. Normal and restored context returned expected answers. These are observations for the inspected runs, not guarantees.
- **Exercise and solution:** [Learner steps](exercises/chapter-07-prompt-and-context/exercise.md) and [reference solution](exercises/chapter-07-prompt-and-context/solutions/README.md). Repeat the demo and keep observations locally. No submission or advanced challenge is required.
- **Evidence:** Chapter Seven's Drive `_authoring` folder contains the context-comparison report and captured results. Speaker notes link the report and list empty/restored trace IDs. The earlier selected-field ablation differs from successful suppression of an entire source.
- **Validation:** Eight scoped model traces verified with the same business revision and static prompt hash. Successful-empty contracts, evidence retention and flag isolation checked. Business state preserved. The OpenAI route was tested; this sequence was not validated through OpenRouter. Owner recording rehearsal remains separate.

#### Optional optimizations to consider later — deferred

These are useful design questions, **not prerequisites for the sample application
or the core section-5 lab**. Keep the current implementation for now.

- **Catalog tool versus upfront context:** `get_catalog` need not inherently be a
  separate call. Supplying validated catalog definitions upfront could avoid a
  round trip, but also adds catalog tokens to questions that do not need SQL.
  Keep catalog data distinct from behavioral instructions, and preserve schema
  validation and revision/clock separation whichever delivery method is chosen.
- **All entities versus relevant entities:** the current tool returns the full
  catalog. A compact overview plus selected entity definitions could reduce
  context size, but selection must include necessary join paths, metrics, units
  and constraints. Missing context can harm correctness.
- **Prompt size and repeated context:** consider shortening redundant instructions
  or repeated metadata only after checking what the model actually receives.
  Removing useful guidance can trade fewer tokens for more mistakes or tool calls.
- **Cache-aware organization:** keep stable content before changing question
  metadata where practical. Evaluate actual cached tokens, total cost, latency
  and correctness; neither a shorter prompt nor fewer tool calls guarantees a win.

These become more relevant as schemas, traffic and cost grow, but are not limited
to production systems. There is no need to optimize them now for this learning
application. If revisited, compare one change at a time with fixed questions and
fixtures. See [Future Optimizations: selective catalog loading](../SPECIFICATION.md#151-selective-catalog-context-loading).

### 8. Tools and MCP

**Agreed chapter demo and learner exercises — October 10:**

- **Chapter demo:** Discover the business, retrieval and memory tool groups; run representative questions and inspect their MCP calls, arguments and results. Compare one marketplace tool via local stdio and remote HTTP, pairing traces with connection configuration. Show a rejected write in an isolated lab. Keep deeper retrieval/memory behavior for their chapters.
- **Core learner exercise:** Repeat the demo and submit a tool map, local/remote diagram, call/trace references, result comparison and rejected-request evidence.
- **Developer extension 1:** Add `get_seller_balance(seller_id)` to an isolated copy of the existing marketplace server using its read context and parameterized seller-balance view. Verify discovery, known/unknown seller behavior, evidence and reconciliation. Production retains its five-tool contract.
- **Developer extension 2:** Build a separate `get_tracking_status(tracking_id)` MCP server over supplied simulated JSON; connect it alongside the marketplace server. No new database or carrier account required.
- **Exercise package:** [Instructions](exercises/chapter-08-tools-and-mcp/exercise.md), [worked solution](exercises/chapter-08-tools-and-mcp/solutions/README.md), and reference code/fixture in the solutions folder. Scope agreed; owner dry run pending.
- **Learning objective:** Distinguish tool contract, implementation and transport; extend a server and connect a new tool system.
- **Covers:**
  - tool contracts
  - our five read-only tools
  - SQL validation (the query structure is checked before it runs, plus a read-only DB role, a 100-row cap and a 3-second timeout)
  - evidence handles
- **Tool grouping — agreed October 10:** Teach three distinct responsibilities: business definitions/current data/history (`get_catalog`, `query_business_data`, `get_order_history`), document retrieval (`search_documents`), and personal memory (`search_memories`, `save_memory`, `update_memory`, `delete_memory`). Business data and document retrieval share the marketplace MCP server while using separate underlying query/retrieval functions. `fetch_evidence` retrieves retained results from either business or document tools. The local SDK memory tools use a separate owner-scoped MCP server; their writes affect memory, not marketplace business records. Hosted-platform native memory paths are covered separately.
- **Connection diagrams — agreed October 10:** Show SDK runtime/client → stdio tool subprocess → business data; hosted Google/Lyzr runtime → HTTPS tunnel → laptop HTTP MCP → laptop data; and hosted runtime → cloud HTTPS MCP on Cloud Run → cloud data. Locality of stdio is relative to the runtime environment, which can itself be hosted. Endpoint configuration chooses the backend independently of runtime selection. Tie each diagram and tool group to inspectable discovery/configuration/call evidence during demo planning; deeper retrieval and memory behavior belongs to their own chapters.
- **MCP:** expose the same tools as one MCP server. MCP is a transport and does not make tools safe. That server is also what Part F reuses on every platform.
- **Permissions (note added October 1, 2026):** teach agent permissions here, because tools are how the agent acts on the world. Least privilege means the agent gets only the tools it needs (five read-only tools, no business actions), and each tool enforces its own limits regardless of what the model asks for: read-only database role, SQL validation, allowed schemas, and row/time limits. Mention briefly that model access is scoped separately by gateway keys (chapter 6) and that hosted platforms add agent identity and access control (Part F). A short lab moment: show that a write or unsafe query requested by the model is refused at the tool/database layer. Application user identity stays outside the teaching scope.
- **Status — October 10:** Local stdio and authenticated cloud HTTP middleware are verified. Thirteen isolated HTTP protocol/lifecycle tests and Terraform validation passed. Cloud web revision `marketplace-web-00015-8lb` is deployed and ready; a live question and fresh-retrieval follow-up passed with retained evidence and detailed Langfuse tool/model observations. Cloud SQL is confirmed `NEVER`, `STOPPED` after validation. Chapter 8 exercise package is ready for owner dry run. Earlier dated pending lists below are historical checkpoints.
- **Owner validation:** Review slides; execute the chapter demo; execute learner exercises and compare solutions; confirm slide, demo and exercise speaker notes are aligned. Track these four checks separately from implementation tests.
- **Implementation acceptance record:** [October 10 SDK HTTP deployment](../app/cloud/VALIDATION-2026-10-10-SDK-HTTP-MCP.md), including successful question/follow-up, trace verification and stopped SQL readback. Seller-balance and tracking reference tools passed actual stdio discovery/calls; owner rehearsal remains separate.

#### Progress and evidence — October 1, 2026

- **Current state:** Built and transport-tested locally and over remote HTTP; see the October 2 update below.
- **What we learned / have available:** The same five read-only contracts work through direct invocation or MCP. MCP changes transport, not business permissions or answer quality. Evidence handles identify saved results; prior citations need same-conversation provenance.
- **Tests and references:** [MCP comparison](../app/results/mcp-transport-2026-09-30/REPORT.md); [lifecycle/citation follow-up](../app/results/mcp-transport-2026-09-30/FOLLOW-UP-VALIDATION.md); [protocol tests](../app/backend/tests/test_mcp.py); M26–M27.
- **Hands-on readiness:** Already tested: contract parity, rejected SQL, snapshot isolation, cross-run evidence rejection, concurrent processes, interruption/recovery and prior citation links. Package one direct/MCP comparison and one rejected query with expected traces.
- **Pending:** Prepare the tool-description/response-field change lab and cloud-hosted remote endpoint without a tunnel. Remote final-answer citation validation remains a follow-up; prompt wording alone does not guarantee exact handles.

#### Remote MCP progress and evidence — October 2, 2026

- **Current state:** Seven actions (five business tools plus investigation begin/end) served through authenticated Streamable HTTP JSON and used by Lyzr Studio over a temporary tunnel. No A2A required for tool access.
- **What we learned:** A remote runtime needs explicit investigation ownership to retain snapshots and evidence. API-key authentication applies to this exposed demo service; local stdio uses a different process/access boundary. Transport alone does not transfer agent runtime guarantees.
- **Tests and references:** 68 current-source tests passed, including three [HTTP MCP tests](../app/backend/tests/test_remote_mcp.py); public discovery/auth checks and Studio traces in [validation](../app/lyzr/VALIDATION.md); [M36](../MILESTONE-LOG.md#m36--lyzr-agent-studio-with-authenticated-remote-mcp).
- **Hands-on readiness:** [Dashboard steps](../app/lyzr/README.md) and [saved prompt](../app/lyzr/agent-instructions.txt) available. Demonstrate initialize/discovery, begin/read/end, rejected writes and evidence isolation. Package a reproducible learner checkpoint before recording.
- **Pending:** Deploy the middleware and SQL/RAG/embedding dependencies to cloud HTTPS without tunneling, then update Studio and prove operation with local services stopped. Remote citation enforcement and broader platform parity checks remain open.

### 9. Knowledge and retrieval (RAG)

**Slides — agreed October 10:** Include the actual RAG architecture as an editable diagram: versioned policy files → paragraph chunks/source metadata → gateway embeddings → PostgreSQL/pgvector; then agent-selected search query → query embedding → date/scope-filtered cosine ranking → passages/evidence handle → later model input, combined with SQL facts where needed. Explain this reference implementation among alternative designs; no reranker or approximate vector index is claimed. The diagram shows the indexed path; unindexed chunks use a labelled lexical fallback.

**Chapter demo — agreed October 10:**

1. Ask a policy-only payout question; inspect search_documents passages, applicability and citation support.
2. Ask why order-2's payout is held; inspect SQL/current-record evidence and policy together. Use the actual current state.
3. In the isolated ch09_rag_lab vector database, prepare a new supplied policy version, show indexed evidence remains unchanged before reindexing, then reindex and repeat the same eligibility question. Keep supplied business facts fixed.

**User exercises — agreed and reference-tested October 10:** Repeat the two application questions and the policy-version/reindex demo. Developer extension: implement two-paragraph overlapping chunks, index the longer synthetic policy separately from paragraph chunks, and compare passages, source ranges, citations, returned text volume and answers at fixed top_k (1 and 4). Main marketplace and fixed market_eval data remain unchanged. No extra advanced exercise is open.

**Materials:** [Exercise](exercises/chapter-09-knowledge-and-retrieval/exercise.md), [worked solution and runnable reference](exercises/chapter-09-knowledge-and-retrieval/solutions/README.md), [raw measured results](exercises/chapter-09-knowledge-and-retrieval/solutions/results-2026-10-10.json). Separate chapter speaker notes contain slide, demo and exercise guidance.

**Validation:** Real gateway embeddings, pgvector cosine retrieval and six model answers completed against a separate local lab database. Policy v1 (24-hour wait) answered eligible at 30 hours; v2 (48-hour wait) answered not yet eligible. The unreindexed source did not alter indexed evidence. Paragraph and overlap both answered the Amber Review exception correctly; overlap changed text volume but did not improve this final decision. Larger documents alone do not guarantee a chunking effect. These are bounded lab results, not a retrieval benchmark. Instructor application-demo rehearsal and learner walkthrough remain owner checks.

#### Progress and evidence — October 1, 2026

- **Current state:** RAG baseline built and checked; isolated policy refresh and chunking reference comparisons passed October 10 (see materials above).
- **What we learned / have available:** Documents are paragraph chunks with source lines, immutable versions and effective dates. They live in PostgreSQL document_chunks with pgvector embeddings. Search filters effective date/scope and ranks by cosine distance; unindexed data has an explicitly labeled lexical fallback. Ranking is not proof, and SQL facts may need policy evidence to explain them.
- **Tests and references:** [Document ingestion](../app/backend/marketplace/seed.py); [search implementation](../app/backend/marketplace/tools.py); [effective-date and vector-path tests](../app/backend/tests/test_integration.py); [policy/mixed-answer regression](../app/results/core18-history-v3-2026-10-01/REPORT.md).
- **Hands-on readiness:** Existing checks: current/historical policy selection and restricted-reader vector retrieval. The vector integration test uses synthetic embeddings; the live suite also exercises document calls. Package ingestion → inspect chunk/version → retrieve → cite, then a payout SQL-plus-policy question.
- **Pending:** Owner review of slides, full demo rehearsal, learner walkthrough and speaker-note alignment. Older retrieval off/on and date-filter comparisons are not required by the finalized plan. No embedding-model, reranker or broad retrieval-quality benchmark is claimed.

### 10. Session state

**Slides — agreed October 10:** Explain short-term conversational memory: purpose, PostgreSQL storage, user ownership and conversation/session ID, runtime binding, stored full history versus the selected model context, and evidence freshness. Include a block diagram: user → owned conversation → stored history → select up to six prior complete question blocks → next model call, alongside current question and fresh business revision/clock/document revision. The history window is currently hard-coded; it counts question blocks, not individual messages. Mention token budgets, summarization/compaction and selective retrieval as alternative long-conversation strategies, not implemented features. Briefly distinguish later cross-session memory.

**Chapter demo — agreed October 10:**

1. **Follow-up continuity:** In a fresh SDK conversation with long-term memory disabled, ask shipment status for a prepared order, then ask “How many units are in that order?” Inspect retained messages/tool evidence and whether additional retrieval occurs. A follow-up may retrieve again; continuity does not require zero tool calls.
2. **Freshness after marketplace change:** In that same conversation, change the prepared shipment through the marketplace (for example pending → dispatched). Ask its current shipment status again. Verify business revision changed, fresh retrieval occurred, returned evidence uses the new snapshot and the answer reflects the new state. The session retains the order reference; the old status must not become current truth. Refresh is prompt-guided, not deterministic removal of stale history.
3. **Six-block window boundary:** Use a separate SDK conversation. Put a distinctive fictional label in the first question, then add six later question blocks without repeating it. Before the eighth question, inspect DatabaseSession.get_items and the actual generation input to show the first block is absent while the full stored history still contains it. Ask for the initial label; grade input visibility separately from the answer. If the label appears in a later block, reset the fixture rather than claim it was forgotten.

**Preparation status — complete October 10:** The updated eight-slide deck and separate speaker notes are delivered and checked. All three demos passed from the fixed baseline in a disposable lab copy through a temporary OpenRouter GPT-5.4 gateway, authorized after direct OpenAI credits ran out. The fixed evaluation database fingerprint matched before and after. The repeatable reset and actual SDK selector also passed. Neutral arithmetic questions replace the earlier command-like filler. Instructor UI rehearsal remains separate.

**User exercises — agreed and validated October 10:** Repeat the three demos, compare configurable windows of two/six/eight complete question blocks, then compare summarization of older turns plus a small recent window. Preserve full storage, complete tool pairs, and current freshness metadata. Every case needs a fixed starting state, fixed inputs, expected checks and reset steps. Keep the evaluation database unchanged; use a disposable baseline copy for changes. [Exercise instructions](exercises/chapter-10-session-state/exercise.md), executable developer solutions, demo/reset scripts and [measured results](exercises/chapter-10-session-state/solutions/README.md) are present. Three offline contract checks and the actual SDK selector against PostgreSQL pass. The four-strategy live comparison completed through OpenRouter: two/six blocks excluded the early label, while eight blocks and summary plus two correctly recalled it. Current investigation metadata and full stored fixture prefixes were preserved. The short summary example increased supplied input size, so do not claim compression or cost savings. The owner still reviews slides, performs demos/exercises, and checks note alignment.

**Learning objective:** Explain conversation continuity, stored history versus supplied model input, and freshness after a business change. Compare history strategies without mutating full storage or breaking tool pairs. Long-term memory is deferred to Part E. Existing conversation isolation remains part of the implementation; the agreed practice above replaces the older fresh-session draft.

#### Progress and evidence — October 1, 2026

- **Current state:** Built; retention, isolation and freshness checks exercised.
- **What we learned / have available:** Up to six prior question blocks, including tool results, are loaded before the current question. Each question captures its own snapshot. Revision governs current business facts; clock governs time-sensitive interpretation; document revision governs policy reuse. This is not long-term memory.
- **Tests and references:** [Session implementation](../app/backend/marketplace/agent.py); [history/isolation tests](../app/backend/tests/test_catalog.py); [five-turn reuse experiment](../app/results/evidence-reuse-2026-10-01/REPORT.md); [paired reuse checks](../app/results/core18-history-v3-2026-10-01/reuse-summary.json); M27, M29–M30.
- **Hands-on readiness:** Already tested: unchanged facts, changed revision, clock-only boundary, complete tool-pair retention and citation provenance. GPT-5.4 reused evidence in targeted checks; nano sometimes queried again despite receiving prior rows. Build the learner exercise around two questions, a purchase and a clock advance.
- **Pending:** Package a new-conversation reset/isolation demonstration and controlled history-on/off variant. Track truncation/window behavior and optional deterministic freshness enforcement separately from prompt compliance.

#### Memory-suite follow-up — October 3, 2026

GPT-5.4 quantity follow-ups reused the same-conversation structured evidence with zero additional tool calls, including with long-term memory disabled. Sidebar navigation retained completed turns and a draft. [Current short-term conclusions and pending UI checks](../app/docs/MEMORY-STATUS.md#short-term-memory); [repeatable suite](../app/eval/memory-v2/README.md). Pending-request navigation and full-reload restoration are distinct from the verified sidebar case; no automatic compaction is implemented.

### 11. The Agent Loop with OpenAI Agents SDK

**Agreed plan — October 10, 2026; preparation and reference validation complete, owner review/dry run remains.**

- **Slides:** intro; editable model/tool loop diagram; OpenAI Agents SDK capability overview; our Agent, Runner and Hooks implementation; model turns versus tool invocations and enforcement; recovery/stopping; final evidence-based response; demo summary; learner exercise; recap.
- **SDK capability overview:** agent setup, execution and streaming, tools/MCP, conversation state and results, hooks/tracing, guardrails/human review and agent orchestration. SDK guardrails are an application-level capability; our privacy and prompt-injection demos use gateway integrations. The overview does not imply that every SDK feature is enabled in this application.
- **Implementation:** Agent defines instructions/model/MCP tools; Runner.run supplies the question, DatabaseSession, hooks and max_turns. One SDK turn is one model invocation, including any requested tool execution; the final-answer call counts. Model chooses requests; runtime executes them; MCP middleware validates SQL.
- **Chapter demo:** code-to-trace normal execution, one controlled temporary SQL read failure followed by recovery, and one-model-turn stopping. A lab-only selector exposes Normal execution / Tool-error recovery / Turn-limit stop in the disposable ch11_loop_lab UI. Changing mode starts a fresh conversation. Use the same order-2 business-and-policy question for each case. Show counts, returned evidence, citations and stopping reason. The recovery case is a retry, not proof of malformed-query repair.
- **Core learner exercise:** repeat the three demos and annotate a trace with model/tool counts, continuation reasons, evidence and stop condition.
- **Advanced developer exercise:** implement a small agent loop without Agents SDK Runner, using supplied OpenAI/native MCP adapters. Retain assistant tool calls, validate allowed names/JSON, pair returned results by call ID, repeat until final text without tool calls or a turn limit. Pass scripted checks, run one live marketplace question and compare orchestration with the SDK. This replaces earlier proposals about only lowering tool budgets or detecting repeated failures.
- **Files:** [Exercise](exercises/chapter-11-agent-loop/exercise.md), [starter](exercises/chapter-11-agent-loop/starter.py), [worked solution/setup](exercises/chapter-11-agent-loop/solutions/README.md), [validation and measured results](exercises/chapter-11-agent-loop/solutions/VALIDATION.md).
- **Repeatability:** fixed market_eval source is read-only. Stop lab services, reset a disposable copy and use fresh conversations. Experimental modes require an explicit lab flag plus matching lab reader/writer database names; main/cloud defaults remain unchanged. No cloud SQL startup is needed.
- **Limits:** eight SDK model turns (AGENT_MAX_TURNS), 150 seconds per question, 4,096 output tokens per call and estimated cost budget ($1 Compose / $0.05 Python fallback). Cost is checked after a call and can overshoot; embeddings are separate. ReadContext.save limits evidence saves to 24, not exactly 24 invocations; order history can save multiple records. Use hook attempts and trace TOOL observations for actual model-requested tool counts.
- **Validation:** SDK UI normal 4 model calls/3 tools; recovery 5/4; stop 1/1 with MaxTurnsExceeded. Current Langfuse API confirmed matching generation/tool observations. Minimal-loop reference completed a live call in 5/4. Five exercise tests, three backend checks and fifteen frontend checks passed. Business/document fingerprints match fixed baseline. Details in VALIDATION.md; live counts are observations, not guarantees.
- **Status:** slide/notes/demo/exercise preparation complete; owner's review and rehearsal pending. The generic API-key message on MaxTurnsExceeded is fixed. Historical CASE-query recovery questions remain separate implementation research, not a required Chapter 11 activity. Workflow/multi-agent remains deferred to Part E.

### 12. Runtime and hosting

**Agreed revision — October 13, 2026; owner review and recording rehearsal remain.**

- **Opening:** agent model/tool loop; supporting framework/SDK capabilities; runtime and hosting; self-managed deployment versus a managed agent platform. Separate framework and hosting choices and compare control/portability with operational effort and product-specific constraints.
- **Examples:** OpenAI Agents SDK, Google ADK, Claude Agent SDK, LangGraph, CrewAI, Microsoft Agent Framework (AutoGen + Semantic Kernel), and Strands Agents. Name managed offerings separately, including OpenAI Agents API, Gemini Enterprise Agent Platform, Claude Managed Agents, Amazon Bedrock AgentCore Runtime, Foundry Agent Service, LangSmith Deployment and CrewAI AMP. Details belong to Agentic Platforms.
- **Deployment diagrams:** existing local test marketplace and full cloud marketplace. Chat backend and OpenAI Agents SDK share a container; local MCP is a stdio subprocess. Cloud tool transport uses the separate HTTP MCP Cloud Run service. Both full deployments route model calls through LiteLLM. Tool handlers connect to PostgreSQL/Cloud SQL; the application persists history, runs and evidence externally.
- **Runtime capabilities:** distinguish infrastructure (compute, lifecycle/scaling, networking, identity/secrets, deadlines) from optional agent features (loop, context/history, model gateway, retrieval, observability/evaluation and guardrails). Generic Docker/Cloud Run does not automatically provide the latter.
- **Demo:** read-only configuration walkthrough that follows chat-to-agent, agent-to-model gateway/provider, agent-to-MCP, tool-to-data, and history/run persistence. Inspect resources, scaling and secret references; distinguish configured from live-observed settings. No new deployment, reset, tunnel or Cloud SQL startup is required.
- **Exercise:** six local deployment questions using the test UI and market_test practice database, plus six optional full-cloud deployment questions for learners who already deployed it. Each answer cites file/service/trace evidence and includes verification status. Learners without cloud deployment complete only the local section. Submit a local diagram and an optional cloud diagram; a fresh model question is optional.
- **Package:** [exercise](exercises/chapter-12-runtime-and-hosting/exercise.md), [reference answers](exercises/chapter-12-runtime-and-hosting/solutions/README.md), and worksheet preparation checks. The previous agent-only/tunnel experiment is preserved separately as [historical authoring evidence](authoring/chapter-12-hybrid-lab/README.md); it is not the current activity. Its October 10 execution/cleanup records do not establish a live cloud path today.
- **Status:** revised materials are prepared for owner review. Existing local/cloud setup remains the learning reference; no fresh cloud deployment or paid model validation is claimed for this revision.

---

## D. Observability, Evaluation and Security

These are horizontal disciplines: each applies to every component. They answer different questions:
- **Tracing:** what happened in *this* run?
- **Monitoring:** how is the system behaving *over time*?
- **Evaluation:** is it *correct*, and consistently so?
- **Security:** can it be made to misbehave, leak data or overspend? (Added October 5, 2026.)

### 13. Observability: Tracing and Monitoring

**Agreed consolidation — October 10, 2026.** Replaces the former separate Tracing and Monitoring chapters. Earlier chapters already demonstrate individual traces; this chapter teaches capabilities, selection criteria and a comparison of standalone observability platforms.

- **Slides:** tracing versus monitoring; required tracing features (model input/output, tool calls, hierarchy, timing, errors and session links); monitoring features (aggregate latency, failures, token usage, cost, dashboards and alerts); shared requirements (integration coverage, privacy, retention, export and hosting options); documentation-backed comparison of a small selection of standalone platforms; our Langfuse/LiteLLM implementation; recap.
- **Platform boundary:** distinguish standalone observability platforms from platform-native telemetry. Native Google/Lyzr internals stay in their respective platform chapters. Evaluation is an overlapping capability; deeper evaluation methodology stays in the next chapter.
- **Comparison:** research current official documentation before selecting products or asserting features. Compare capabilities and limitations rather than crown a winner. Distinguish built-in features from integrations, paid tiers and proposed functionality.
- **Demo:** six complete recorded investigations: normal payout, controlled read failure/recovery, turn-limit stop, initial shipment status, quantity follow-up and fresh status after dispatch. Inspect question, tools, evidence, answer and timings. Monitoring reviews cost availability, latency and user-feedback scores; the saved local dashboard shows daily support-run counts and daily p99 latency with matching root/name/environment filters. Chart points show tooltips; inspect the corresponding day in Tracing.
- **Learner exercise:** review those six scenarios, inspect cost/latency/scores, and create the same two trend widgets through the UI. Use existing local recordings; instructor IDs are project-specific. No required synthetic upload, code change, reset or new model call. [Exercise](exercises/chapter-13-observability/exercise.md), [separate solution](exercises/chapter-13-observability/solutions/README.md).
- **Validation:** six historical application traces read back in local Langfuse v4.46.0. Root-only daily queries and both rendered charts verified. One authorized live model call verified gateway cost forwarding into one existing generation: 31 tokens and $0.000165. Six offline cost-hook tests passed, including SDK integration and no duplicated usage. Historical cost remains unavailable; v4 observations are immutable and were not rewritten. Alerts and external comparisons remain documentation-backed overviews.
- **Status:** seventeen-slide revision retains the purpose, architectures, requirements/examples, comparison, selection criteria and managed-platform overview; the final demo and task now use recorded investigations and a UI dashboard exercise. Backend cost forwarding is active locally; cloud deployment is separate. Active Drive folders follow the 22-chapter outline. [Historical premerge plan](planning/observability-premerge-2026-10-10.md) and earlier synthetic fixtures are retained as authoring history, not learner prerequisites.

### 14. Evaluation

**Draft learner practice — for review, not finalized:**

- **Exercise:** Add one gold case and deterministic check, run repeated trials, then compare human and judge grades.
- **Solution to prepare:** Case definition, check implementation, repeated-run results and interpretation of judge disagreement and answer variability.
- **Learning objective:** Build and critique an evaluation pipeline.
- **Lab and result:** Add a gold case and deterministic check, run repeated trials and compare provisional judge grades with human review.
- **Covers:**
  - isolated `market_eval` database, versioned fixtures, reset/replay and fixed demo clock
  - gold set design (essential facts vs evidence vs optional detail)
  - deterministic checks
  - LLM-as-judge
  - **calibrating the judge against human grades** (75% → 86% agreement on 36 answers)
  - storing results as Langfuse datasets
  - per-answer user feedback stored by the application and associated with traces; distinguish satisfaction from factual correctness; demonstrate trace scores and Scores → Analytics for rated answers
  - pending online evaluation of sampled actual user answers after response
- **Consistency lesson ("same input, different answer"):** one run isn't a score. Run each case k times and report the pass rate alongside "correct in all k runs". Flag cases that flip between right and wrong.
- **Status:** built and measured (M02, M04, M05). The runner supports repeats; a learner-ready repeated-run workflow and broader consistency summaries remain to prepare. User feedback is implemented and manually validated October 8; asynchronous online evaluation of real usage remains pending.
- **Source:** [Calibration summary](../app/results/calibration-v3-2026-09-29/CALIBRATION-SUMMARY.md)

#### Progress and evidence — October 1, 2026

- **Current state:** Evaluation built and measured; course workflow pending.
- **What we learned / have available:** Separate expected text/records, retrieved records, model text, deterministic checks, judge verdict and human adjudication. Judge agreement is not model accuracy. Correctness can change through rubric clarification without any changed answers.
- **Tests and references:** [Evaluation specification](../EVALUATION-SPEC.md); [judge calibration](../app/results/calibration-v3-2026-09-29/CALIBRATION-SUMMARY.md); [current comparison](../app/results/core18-history-v3-2026-10-01/comparison.html); [approved rubric clarification](../app/results/core18-history-v3-2026-10-01/user-adjudication-v1.json); [runner with repeats](../app/backend/marketplace/eval_compare.py); M02–M05, M14, M30.
- **Hands-on readiness:** Already done: isolated fixtures, structured checks, Claude grading, human review, calibration and Langfuse upload for earlier runs. Current nano/GPT-5.4 run uses assistant grading plus user-approved 23/24, not new Claude grading. Runner supports repeats and payout repeats exist.
- **Pending:** Package add-a-case/check, judge calibration and repeated-run exercises during chapter preparation. Online evaluation is deferred to Evaluation chapter preparation, not an upfront experiment blocker. It is a separate pending capability: sample actual user answers after response, assess evidence support/relevance/citations and inspect quality over time. User thumbs-up/down feedback is an application capability, distinct from judge grades and factual correctness. Preserve original gold and dated adjudications.


#### Why we use `market_eval`

`market_eval` is a separate evaluation database in the same PostgreSQL service.
The interactive marketplace changes through UI actions; evaluations need a known,
repeatable starting state. Before each independent case/trial/model comparison,
the runner resets the evaluation database and loads the case's specified business
records/events, document corpus and demo clock. Both candidates receive the same
fixture version. Scenario-defined follow-ups keep their conversation history and
intentional state changes within that case; do not reset between those turns.

It was created for repeatable evaluation generally, not specifically for the six
routing conversations or the later proposed payout investigation. Different test
sets can reuse it. New experiments can introduce new versioned fixtures without
rewriting earlier results. Database guards reject connections to the interactive
database; independent runners must not concurrently reset this shared evaluation
database.

**Hands-on to package:** change an order through the interactive UI, then load/reset
a known evaluation fixture twice and verify identical starting fingerprints and
expected facts. Compare two models from that same starting state, then demonstrate
an intentional state-changing follow-up within one scenario. Existing fixture and
isolation machinery is implemented; this learner walkthrough remains to prepare.

**Implementation references:** [fixture reset/replay and database guards](../app/backend/marketplace/eval_fixtures.py),
[evaluation runner](../app/backend/marketplace/eval_compare.py), and
[isolation tests](../app/backend/tests/test_evaluation.py).


### 15. Guardrails and Agent Security

**Prepared learner practice — owner rehearsal pending:**

- **Exercise:** Compare the four existing UI cases: built-in input masking, output-only masking, Presidio card blocking and Lakera on retrieved content. Record settings, enforcement points, trace evidence and limitations; review supplied harmless and missed-detection cases. [Exercise](exercises/chapter-15-guardrails-security/exercise.md) · [Worksheet](exercises/chapter-15-guardrails-security/worksheet.md).
- **Separate solutions:** [Recorded observations and grading criteria](exercises/chapter-15-guardrails-security/solutions/README.md); do not assume every fresh attack is blocked. [Instructor walkthrough](exercises/chapter-15-guardrails-security/instructor-demo.md) gives individual numbered cases.

- **Learning objective:** Distinguish model refusal, prompt guidance, gateway screening and enforceable tool boundaries; explain their limits using OWASP.
- **Relationship to other sections:** Monitoring, tracing and evaluation remain separate sections. Chapter 2 briefly identifies guardrails on the component map; there is no separate guardrails lesson in Section C. All detailed guardrail demos live here.
- **Main teaching guide:** [Combined demos and OWASP teaching notes](../app/docs/SECURITY-CHAPTER-DEMO.md).
- **Core teaching walkthrough:** Four existing UI comparisons: built-in input privacy, output-only privacy, Presidio card blocking and Lakera on retrieved content. Forged-policy/source-authority, direct injection and private-context trials remain supporting examples with their existing evidence; the memory-permission demo remains excluded from this chapter.
- **Observed results:** Latest forged-exception answers both retained held/unpaid status; source authority On improved clarity. Lakera blocked instruction attacks, whereas factual poisoning is a separate problem. Post-filter input audit showed synthetic PII masking. Retain misses and false blocks in the historical reports.
- **Marker status:** Earlier visible-marker/private-marker probe completed; the user reports validating the revised same-lantern comparison on October 7. This is user acceptance, not a new independently reviewed trace.
- **OWASP notes for later slides:** Tool misuse and output validation; least privilege and user-bound authority; memory/context poisoning; trust in MCP servers and other agents; human approval for consequential actions; execution budgets; prompts are not secret storage. General cloud/infrastructure security remains outside scope.
- **Removed from this lesson:** The memory-permission walkthrough and any proposed read-by-ID tool. Existing ownership tests remain memory-chapter evidence; no new authorization feature is needed solely for this course lesson.
- **References:** [OWASP course map](../app/docs/OWASP-SECURITY-MAP.md), [support results](../app/results/security-support-ui-2026-10-07/REPORT.md), [gateway input audit](../app/results/gateway-input-audit-2026-10-07/REPORT.md), [historical boundary/marker report](../app/results/security-boundaries-2026-10-07/REPORT.md). These are bounded examples, not full OWASP coverage.
- **Current teaching package:** Sixteen-slide review draft, embedded/exported numbered notes, four-case instructor guide, learner worksheet and separate solutions prepared October 13. Architecture/implementation and prevention/detection/response are each consolidated. Historical security lab acceptance remains user-reported; no new paid security run was made during authoring. Owner rehearsal and recording remain.

#### Supporting experiment evidence and historical results

[Follow-up forged-document trials](../app/results/security-document-injection-v1/VARIANTS.md): the fabricated settlement exception fooled both models, while GPT-5.4 resisted two explicit authority/template variants. Two Nano trials did not receive their payloads and cannot count as resistance. Teach the distinction between rejecting instructions and accepting fabricated facts, and why source governance/status validation complement a gateway content filter. The earlier fixture was restored; filter-on comparison is pending.

[Source-authority prompt comparison](../app/results/security-document-injection-v1/PROMPT-V11.md): adding an explicit distinction between policy rules and actual business status changed GPT-5.4 from accepting EX-204 to flagging the conflict. Nano still accepted it despite receiving the rule. One rerun each; demonstrates model-dependent instruction compliance, not guaranteed prevention. Semantic filtering remains pending.

[Built-in gateway filter lab](../app/results/gateway-guardrails-2026-10-07/REPORT.md): nine paired synthetic cases demonstrate input/output email masking, key-shaped data blocking and explicit injection in tool-result messages. Include the quoted-security false positive and paraphrase miss. Distinguish gateway rejection from model refusal and pre-call protection from post-call redaction. Original API-level verification; subsequent support UI integration and external comparisons are recorded below.

[External Presidio privacy comparison](../app/results/presidio-guardrails-2026-10-07/REPORT.md): local analyzer/anonymizer behind LiteLLM. Teach entity recognition, thresholds, pre/post masking and blocking; .invalid email miss versus example.com success shows recognizer limits. Phone/card and benign controls verified. Separate PII, secret detection and injection detection; do not present Presidio as the semantic injection detector. Optional API lab complete; subsequent support UI integration and injection detector trial are recorded below.

[Manual guardrail cases and Lakera setup](../app/docs/GUARDRAILS-MANUAL.md): compare off/on one case at a time, preserve gateway decisions versus model refusals. Lakera optional overlay activated with default Enforce policy. [Five-case trial](../app/results/guardrails-manual-2026-10-07/LAKERA-REPORT.md): explicit/paraphrased attacks blocked, harmless quotation falsely blocked, legitimate policy and forged exception allowed. Teach detector limits and the separate need for source-authority/business validation. Synthetic Chat Completions tool messages only; subsequent support UI integration is recorded below; unavailable-service testing remains pending.

[Support UI chapter demo catalog](../app/docs/SECURITY-CHAPTER-DEMO.md) now has copy/paste questions and main/test mapping. Hands-on: compare Off/named gateway filter; use test policy fixtures; compare source-authority paragraph off/on with the same forged passage. Main prompt cannot be disabled. [Verified support-flow results](../app/results/security-support-ui-2026-10-07/REPORT.md) include post-RAG blocks, PII masking/blocking and the prompt comparison; clean fixture restored. Explain why factual poisoning, model guidance and gateway screening are separate boundaries. User manual walkthrough and wider repetition remain; original app questions/raw traces are not globally redacted.

---

## E. Advanced Agent Topics

Every lesson in this part is an experiment: a hypothesis, one change, the same evaluation set, and quality, cost and latency compared together.

### 16. Model routing

**Draft learner practice — for review, not finalized:**

- **Exercise:** Compare a fixed-model baseline with one routing policy on a small shared question set.
- **Solution to prepare:** Routing configuration and quality/cost/latency comparison including classifier overhead, available teaching models and experimental limits.
- **Learning objective:** Measure a classifier and routing scope against fixed-model baselines.
- **Lab and result:** Change a routing configuration, run a bounded comparison and explain quality/cost trade-offs and uncertainty.
- **Covers:**
  - choosing a classifier: keyword rules, semantic matching, an LLM classifier, managed routers
  - choosing the scope: route once per session vs per question
- **Results to show:** the LLM classifier gets 88.9% fully correct at about 45% below always-GPT-5. A managed router picked the cheap model every time and got 50%. The live session results are included.
- **Status:** measured and published.
  - [Part 1: Choosing a Classifier](https://sreeni.blog/2026/09/30/model-routing-part-1-choosing-a-classifier/)
  - [Part 2: Choosing the Scope](https://sreeni.blog/2026/09/30/model-routing-part-2-choosing-the-scope/)
- **Before recording:** verify teaching model availability. The owner classified the current routing/cache refresh as low priority on October 8; revisit it during Model Routing chapter preparation, not as a blocker for overall experiment completion. Published numbers remain historical.

#### Progress and evidence — October 1, 2026

- **Current state:** Historical routing experiments complete; current-version rerun pending.
- **What we learned / have available:** Compare fixed-model baselines, classifier decision overhead and chosen-model execution cost. Offline replay applies only to saved same-model trajectories; mixed-model live execution needs fresh runs. Conversation/question scope and classifier type are separate variables. Cache ratios alone do not establish causality.
- **Tests and references:** [Classifier comparison](../app/results/routing-classifiers-2026-09-30/REPORT.md); [semantic scenario audit](../app/results/semantic-scenarios-v2-2026-09-30/REPORT.md); [live granularity/cache report](../app/results/routing-granularity-2026-09-30/REPORT.md); [published series and sources](../blog/model-routing/README.md); M15–M23.
- **Hands-on readiness:** Already measured: LLM/JEV, restricted OpenRouter, keyword/heuristic/semantic classifiers, plus six conversations under four live policies. Published examples use the earlier nano/GPT-5 baseline, not the latest nano/GPT-5.4 run. Learner lab still needs checkpoints and bounded commands.
- **Pending:** Rerun a bounded fixed-model vs conversation/question comparison on the current prompt/catalog/history. Explicitly remeasure cache tokens, input volume, calls, cost and latency, and also regrade quality/tool usage; do not assume only caching changed. Use one declared model pool and identical fixtures. Preserve historical reports; label cold/warm/run-order effects and separate classifier cost. Larger held-out coverage remains future validation.

### 17. Workflow vs single agent vs multi-agent

**Draft learner practice — for review, not finalized:**

- **Exercise:** Run the same investigation through single-agent and coordinator/worker designs with equal total budgets.
- **Solution to prepare:** Configurations, traces and a comparison of correctness, evidence, calls, cost and latency; explain where delegation helped or added overhead.
- **Learning objective:** Compare workflow, single-agent and multi-agent designs on the same task.
- **Lab and result:** Compare single-agent tool scheduling with coordinator/worker delegation, then inspect the nano → GPT-5.4 review → nano correction workflow. Compare correctness, evidence, calls, cost and latency with explicit experimental boundaries.
- **Covers:**
  - a fixed workflow as the comparator
  - a single agent
  - a coordinator with specialist agents on deep investigations
  - equal total budgets and how discoveries are shared between agents
- **Status:** Bounded single-agent serial/parallel, coordinator/worker and evaluator–optimizer comparisons completed; later patterns remain pending. Required for v1.

#### Progress and evidence — October 1, 2026

- **Current state:** Common-policy payout experiment completed with GPT-5.4: three rotated repeats per variant, eleven payouts and three sellers. The initial eight-case reviewer workflow completed (subsequently expanded in M34 below): saved nano draft → GPT-5.4 review → at most one nano correction. Five problem cases plus three controls improved from 3/3/2 correct/partial/incorrect to 5/3/0; saved GPT-5.4 was 7/1/0. Grades are provisional.
- **What we learned / have available:** Two architectures, three variants: serial/parallel are scheduling choices within one agent; workers own separate loops. Catalog precedes SQL, and discovered histories can be independent. This task was handled by a bulk query: workers added overhead without a demonstrated explanation-quality benefit. Eight completed answers had supported explanations; one worker synthesis timed out and two answers had a malformed reference. Sampling, cache and differing queries prevent a pure concurrency claim. Multiple model calls alone are not multi-agent.
- **Tests and references:** [Single-agent runtime](../app/backend/marketplace/agent.py); [current baseline](../app/results/core18-history-v3-2026-10-01/REPORT.md); [payout experiment plan and controls](../app/eval/orchestration-v1/README.md); [comparison and limitations](../app/results/payout-orchestration-v2-2026-10-01/REPORT.md); [run-by-run report](../app/results/payout-orchestration-v2-2026-10-01/comparison.html); [research direction](../RESEARCH-GUIDE.md).
- **Reviewer workflow learning and references:** Detection, correction and final grading are separate. Full catalog metadata matters to the critic; nano may still fail to retrieve missing evidence. Including the saved nano generation cost, the workflow estimate is $0.2575 versus $0.4244 for saved GPT-5.4 alone: approximately 39% lower cost, with 5 versus 7 fully correct answers. Every draft was reviewed; only flagged drafts were corrected. These conservative uncached totals combine historical generation with new review/correction, rather than fresh end-to-end measurements. The user accepted this as a completed learning milestone on October 1. No further runs are required to close it. Assistant grades remain provisional; acceptance of the experiment does not constitute individual grade adjudication or a production-policy decision. [Report](../app/results/reviewer-workflow-v2-2026-10-01/REPORT.md); [comparison](../app/results/reviewer-workflow-v2-2026-10-01/comparison.html); [plan](../app/eval/reviewer-v1/README.md).
- **Hands-on readiness:** Runnable fixture/runner and archived model inputs available for the three tested strategies. Learners can inspect serial tool intervals, concurrent history requests, three overlapping worker model calls, evidence/citation checks and independent client/gateway timeout limits. Reviewer inputs, feedback and corrections are archived; a controlled identical-work scheduling lab and learner packaging remain to prepare.
- **Pending:** Human review of provisional explanation grades if desired; prepare the teaching walkthrough. A pure serial/parallel scheduling comparison needs identical retrieval work after discovery. Add seller-specific policies only if they create meaningful independent investigation branches. Independent-system/A2A remains later work. Optional reviewer variants can enforce evidence acquisition or give the reviewer tools; broader held-out repeats and fresh end-to-end cost/cache/latency measurements are enhancements, not required to close the learning experiment. Memory was the next proposed implementation topic at the time of this October 1 note; its bounded implementation and comparison are now complete in chapter 18. Keep this required course work.


- **Saved diagrams:** [Coordinator with seller workers and evaluator–optimizer](diagrams/AGENT-PATTERNS.md), with editable Mermaid sources and implementation boundaries.

#### Reviewer capability and coverage update — M34, October 1

**Completed:** Nano reviewed the matched eight cases without requesting corrections. Both reviewer variants then covered the eighteen known development cases; review inputs were verified identical. Nano alone and nano-review workflow each graded 11 correct / 4 partial / 3 incorrect; GPT-5.4-review workflow graded 14 / 4 / 0; saved GPT-5.4 alone graded 17 / 1 / 0. Grades are provisional. All 36 workflows completed without business changes.

**Cost/quality lab:** Include generation as well as every review and flagged correction. Assembled uncached totals: nano alone $0.0373; nano review $0.0526; stronger review $0.5817; GPT-5.4 alone $1.2104. Stronger review saves about 52% against stronger generation but has three fewer correct answers. Original generation is reused; this is not a fresh latency/cache comparison. Two follow-ups review/correct the final turn with frozen earlier history, including the planned mutation for case 28.

**What to teach:** Separate the review-stage hypothesis from reviewer-model capability. Stronger feedback can identify scope errors and trigger retrieval; weak review may miss the same mistakes. Do not equate approval/revision with final correctness. Known-case coverage is broader, not held-out validation. The lesson is experimental design and trade-offs, not a universal finding that self-review fails. Preserve M33's evidence-packet mistake as chronological learning; use M34 for the current headline.

**Hands-on:** Replay both critics on identical frozen drafts, inspect case 27's date-filter feedback and corrective SQL, independently grade corrections and controls, then compare total cost. Runnable scripts and raw payloads are available; learner packaging remains pending. [Current report](../app/results/reviewer-ablation-core18-2026-10-01/REPORT.md), [comparison](../app/results/reviewer-ablation-core18-2026-10-01/comparison.html), [matched-input validation](../app/results/reviewer-ablation-core18-2026-10-01/validation.json), [plan](../app/eval/reviewer-v1/README.md). Further repeats, fresh end-to-end runs and human checking remain enhancements.

#### Design discussion and blog handoff — workflow, agents and multi-agent

**Purpose:** Teach how to choose and test a design for a use case, rather than claim that more agents are better. Preserve the rejected alternatives and reasoning as well as successful experiments. The payout comparison and reviewer workflow are separate experiments with different tasks and denominators.

**Who controls the next step?** A workflow uses application-defined stages and transitions; an agent chooses its next tools/actions from results. Both can be combined: our review/correction sequence is fixed, while the generator can investigate using tools. A flowchart alone does not distinguish them: an agent loop can also be drawn. Multiple model calls, different model names, or concurrent tools do not by themselves establish independent agents.

| Pattern | Control and communication | Example / course status |
|---|---|---|
| Prompt chaining | Predetermined stages pass outputs forward. | Produce an outline, validate it, then write; conceptual. |
| Routing | Classify input and select a path. | Our model-routing experiments; selecting a model is distinct from spawning a worker. |
| Parallel sectioning / voting | Independent subtasks, or multiple attempts followed by aggregation. | Parallel checks on a document; conceptual. |
| Single agent with tools | One loop chooses tools and follow-ups; independent tools may overlap. | Implemented SQL/RAG support baseline. |
| Orchestrator with workers | A coordinator delegates bounded tasks and synthesizes worker findings. | Seller investigators implemented in the bounded payout experiment. |
| Handoff | A specialist takes over responsibility; control need not return for manager synthesis. | Conceptual comparison with agents used as tools; not implemented here. |
| Evaluator–optimizer | Generate, critique, conditionally revise under a bounded controller. | Implemented nano → GPT-5.4 review → one nano correction. |
| Independently operated agents | Separate systems exchange tasks/results across an explicit boundary. | A2A discussion; not implemented. |

This taxonomy is a teaching synthesis. Anthropic's [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) supplies the workflow/agent distinction and chaining, routing, parallelization, orchestrator-workers and evaluator-optimizer vocabulary. Framework names and workflow labels are not guarantees of autonomy or quality.

**Why consider multiple agents?** Two main hypotheses from our discussion are independent parallel investigations and focused, separate contexts when one working context becomes overloaded. A worker can retain its own detailed search/tool history and return bounded findings with evidence. This is context isolation and managed transfer, not automatic context preservation: summaries can omit facts, and the coordinator must reconcile shared assumptions and citations. Specialized tools/prompts and independent ownership can also motivate separation, but first ask whether one agent with multiple tools is sufficient.

Costs include repeated instructions/catalog/policy retrieval, more model calls, coordination and synthesis, failure propagation, inconsistent assumptions, citation transfer and additional latency. Parallel tools already provide concurrency without worker loops. Several dependent steps may be easier to reason about together. Measure outcomes, completeness, execution failures, evidence support, cost and latency; record actual overlap rather than assuming concurrency from configuration.

**Examples where workers may make sense:** Anthropic's [multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) uses a lead researcher and subagents exploring different aspects with independent search loops. It describes benefits from parallel exploration and separate context windows, alongside substantial token/coordination costs and poor fit for tightly dependent work. This is vendor-reported evidence, not a benchmark of our support application.

A proposed teaching example is comparing coding tools across programming-language ecosystems: workers investigate Python, JavaScript and Java tooling against the same criteria, then a coordinator reconciles results. Each branch must justify several independent searches and substantial context. This is an illustrative scenario from our discussion, not a claim that Anthropic tested that exact decomposition. Cross-language code changes with shared interfaces may instead be tightly coupled and unsuitable for naive splitting.

Google's [Towards a science of scaling agent systems](https://research.google/blog/towards-a-science-of-scaling-agent-systems-when-and-why-agent-systems-work/) provides supporting and contrary evidence: measured benefits depend on task decomposition, while sequential tasks can suffer coordination overhead. Its benchmark results do not establish our architecture's performance.

**Our reasoning path: SQL/RAG → sellers → measured comparison.**

1. We considered a SQL specialist and a RAG specialist. We did not implement this split: SQL and document search are tools, not necessarily separate responsibilities. One agent can use both and overlap independent searches. Often the business records identify the specific policy, historical date or recovery procedure needed, making retrieval dependent on SQL. A generic returns policy would not resolve every payout question. Separate agents would add handoff overhead without a demonstrated need for separate investigation loops.
2. We then considered investigating unpaid sellers. First discover affected payouts and sellers; diagnose primarily at payout/order-item level, then aggregate by seller. One seller can have several reasons, and a single bulk SQL query may cover all sellers. Neither serialization nor delegation implies one query per seller.
3. We built a separate fixed `market_eval` fixture with three sellers and eleven payouts covering seven outcome classes and controls. Common policy came first; seller-specific policies were deferred. Different policies alone do not prove value: branches need meaningful independent follow-up decisions, conflicting histories, historical policy interpretation or incident research.
4. We compared single-agent serial tools, single-agent parallel tools, and a coordinator with seller workers, all GPT-5.4, with three rotated repeats each. Serial/parallel are scheduling variants of one architecture; workers are another. Catalog precedes SQL. Once discovered, order histories can be independent. The experiment runner supplied the seller-investigation structure; it was not a general coordinator that learned to route every support question.
5. Serial and parallel returned 3/3 answers each; workers returned 2/3. Completed explanations were supported, but one worker synthesis timed out and two raw citation references were malformed. The bulk-query baseline handled the task. Workers added overhead without a demonstrated quality gain. This negative result is useful: the experiment did not show that our task needed workers. Differing retrieval and cache behavior prevent a pure scheduling claim. It does not prove that workers never help.

See [M32 report](../app/results/payout-orchestration-v2-2026-10-01/REPORT.md), [captured runs](../app/results/payout-orchestration-v2-2026-10-01/comparison.html) and [fixture/experiment plan](../app/eval/orchestration-v1/README.md). The [M33 report](../app/results/reviewer-workflow-v2-2026-10-01/REPORT.md), followed by the [M34 reviewer ablation and eighteen-case expansion](../app/results/reviewer-ablation-core18-2026-10-01/REPORT.md), demonstrates a different rationale: a stronger critic improved a weaker generator under a fixed feedback workflow. Keep its independent grading separate from in-workflow review.

**Two separately managed systems and A2A.** An illustrative example is a marketplace support agent requesting a payment-provider agent's investigation. Each organization/team owns its tools, state, permissions and lifecycle; they exchange a bounded task, progress and results rather than merging internal contexts. Separate systems do not automatically require agents—ordinary APIs/MCP may suffice for predefined operations. A2A becomes relevant when delegating work to an independently operating agent and interoperating across frameworks/organizations. It complements our MCP tool boundary and does not replace it or guarantee reasoning quality. The [official A2A overview](https://a2a-protocol.org/latest/topics/what-is-a2a/) explains capabilities, asynchronous collaboration and opaque execution. No A2A implementation or measured benefit is claimed here.

**Reading and source boundaries:** Primary references above were checked October 1, 2026. Also read [Cognition's multi-agent account](https://cognition.com/blog/multi-agents-working) and the counterpoint [Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets](https://arxiv.org/abs/2604.02460), already catalogued with limitations in [research guide chapter 6](../RESEARCH-GUIDE.md#4-orchestration). Those are external evidence, not local test results. For the blog, distinguish published findings, our design hypotheses, implemented architecture and measured outcomes. No new experiments are required to capture this discussion.

### 18. Short-term and long-term memory

**Draft learner practice — for review, not finalized:**

- **Exercise:** Save a synthetic preference, recall it in a new conversation, then update/delete it and repeat; include a memory-off or user-isolation check.
- **Solution to prepare:** Save/recall/update/delete steps, selected memory evidence, expected isolation and a distinction between conversation history and persistent memory.
- **Learning objective:** Distinguish session state from deliberately retained knowledge, and measure when memory helps or misleads a later conversation.
- **Lab and result:** Demonstrate existing short-term state, then compare memory off/on for three explicitly saved long-term examples. Update/delete memories and repeat the later question.
- **Status:** Bounded memory learning lab complete, with a repeatable test suite; required for v1. Lesson recording/packaging and selected manual catalogue cases remain pending. This is not a production-readiness claim.

#### Current progress and conclusions — October 3, 2026

**Current transport:** Memory tools use a separate local stdio MCP server; PostgreSQL is implemented. [Current/provider-planning diagrams](diagrams/MEMORY-ARCHITECTURE.md) and [post-migration 19-question regression](../app/results/memory-repeatable-20261003T112031250654Z/REPORT.md). Teach runtime portability through MCP separately from the planned storage-provider adapter; no external provider is yet integrated behind this service.

- **What we learned:** Short-term structured evidence can be reused without a new tool call even when long-term memory is off. Historical checkpoints support investigation continuity but require fresh current-status checks. Current instructions override preferences; policy overrides checklists. Retrieval selection and correct use are separate model behaviors. Explicit resume wording is a clear checkpoint trigger; vague change questions need a comparison baseline. Nano implicit retrieval remains unreliable in the observed diagnostic.
- **Tests/evidence:** [Eight scenarios / 19 GPT-5.4 questions](../app/results/memory-repeatable-20261003T093153094486Z/REPORT.md): all operation checks passed and assistant-reviewed factual answers correct. [Citation correction and two-question rerun](../app/results/memory-repeatable-20261003T094355178246Z/REPORT.md): existing UI already resolves shortened recorded IDs; all original sources resolve, seven regressions pass. No paid judge. Earlier CRUD/isolation and revision/clock tests remain complementary evidence.
- **Hands-on readiness:** [24-case catalogue, exact prompts and eight-scenario mapping](../app/eval/memory-v2/README.md); choose live `market` or test `market_test`, prepare/reset known fixtures, inspect selection/evidence/cost separately. Automated use fixtures directly seed memories; use the manual save steps to demonstrate chat saving. Preserve original answers and corrected grading when explaining the citation lesson.
- **Pending:** Record/package the lesson; exercise selected remaining UI cases (S03–S06, S08, L09, L14 and vague-change L15). Some boundaries already have prior regressions; do not imply all 24 catalogue cases were run. Repeated/held-out/model-comparison runs are optional. Automatic extraction, compaction, shared procedures and Mem0 are deferred.
- **Blog handoff:** [Consolidated conclusions and evidence](../app/docs/MEMORY-STATUS.md). Focus on how to measure retrieval, memory use, freshness and authority; avoid extrapolating a single successful trial to universal reliability.

#### Scope and evidence — October 2, 2026

**Short-term demonstration:** Show messages, tool calls/results and investigation evidence within one conversation, including revision/clock checks before reusing facts. Explain that persisted history and the bounded history actually sent to the model are different. No automatic compaction or replacement of history is included.

| Long-term type | Marketplace example | What the lab should demonstrate |
|---|---|---|
| Semantic | Explicitly remember that this user means seller Cedar & Co. when they say “Cedar.” | A new conversation uses the preference; an explicit product request overrides it; another user does not inherit it. |
| Episodic | Save a checkpoint of a payout investigation, its evidence sources and unresolved next step. | A new conversation can resume the investigation, but checks current business data before claiming the payout is still failed. |
| Procedural | Explicitly save an accepted investigation checklist: distinguish delivery hold, active return and provider failure. | A later investigation follows the checklist without replacing authoritative policy, permissions or metric definitions. |

**Architecture and production discussion:** [Memory block diagram and integration write-up](diagrams/MEMORY-ARCHITECTURE.md), with editable Mermaid sources for [our function-tool approach](diagrams/memory-architecture.mmd) and [optional Mem0 MCP](diagrams/memory-mem0.mmd). It distinguishes SDK session history from application-owned long-term memory and documents an optional Mem0 adapter.

**Storage and integration:** Implemented a small application-owned memory module and PostgreSQL records for owner/scope, type, content, source conversation/run, timestamps and version. Provide save, retrieve, update and delete operations. As of October 3, the agent calls bounded memory tools through a separate local stdio MCP process; those tools use the backend memory module. Trusted application launch context binds owner, permissions and provenance. Existing marketplace transport remains independent; remote HTTP MCP remains business-only. Existing SDK session storage continues to own conversation history. Direct lookup is enough for preferences; semantic retrieval for episodes is optional if needed, rather than a requirement for every memory type.

**Write policy:** Saving is explicit/user-directed. The model may draft a checkpoint, but automatic extraction or background saving is deferred. Procedural memory is accepted guidance, not autonomous editing of the governing system prompt. Personal records belong to the individual user ID: operator and support are separate users. Any shared procedure requires explicit shared scope.

**Original test plan (followed by current results above):** Across-conversation recall for all three types; memory-off with ordinary history preserved; update/delete; user isolation; current instruction precedence; stale episode/fresh data; conflict with authoritative policy. Reset the memory fixture between independent cases. Record selected memories and their source IDs alongside answer correctness, additional tokens/cost and latency. Basic save/recall, update/delete, isolation and memory-off checks ran initially; stale-policy/revision, policy conflict and retrieved preference override were subsequently exercised in the current results above. See the [M35 report](../app/results/memory-v4-2026-10-02/REPORT.md) for the exact boundary.

**Memory-use diagnostic update — October 2, 2026:** Nine live questions tested stale checkpoints, procedural application and current instruction precedence with memory on/off. The scenarios exposed failed/distorted saves, incorrect delivery reasoning and a business-question/memory-only routing bug; stale handling remains unvalidated because setup failed. These findings do not supersede earlier basic CRUD acceptance. [Exact test cases and results](../app/results/memory-use-v1-2026-10-02/REPORT.md).

**Follow-up application repair and GPT-5.4 verification — October 2, 2026:** Negated memory changes no longer hide business tools; backend assigns save provenance and the save kind is an enum. 74 regression tests passed; three setup saves and six memory-on/off answers passed the GPT-5.4 diagnostic. Stale checkpoint and procedural on variants retrieved actual memories; explicit preference override succeeded without memory retrieval, leaving the preference unchanged. The interactive default was Nano at the time of this diagnostic; the current default is GPT-5.4. This one-trial follow-up changes both model and application, so it is not a controlled model-quality comparison. [Questions, results and limitations](../app/results/memory-use-gpt54-v2-2026-10-02/REPORT.md).

**Lyzr comparison:** Native Cognis recall and its Cross Session off/on control passed in the optional platform lab. Applying a remembered checklist missed a required shipment query, even after a prompt instruction. Teach memory retrieval, correct use and evidence completeness as separate checks. See the [Lyzr platform lab](#20-lyzr-agent-studio) for the concrete gap and acceptance criterion.

**Optional platform discussion:** Explain extraction, retrieval, consolidation, forgetting and compaction as separate capabilities. Mem0 or a similar manager is optional, not a prerequisite for production. A PostgreSQL memory layer can also be engineered for production; this lab does not attempt that assurance. A future Mem0 integration could call its SDK/API in the backend or wrap operations as agent tools; it is not implemented or verified here, and adopting LangChain is not required.

**References:** [LangChain memory overview](https://docs.langchain.com/oss/python/concepts/memory) for short-/long-term scope and semantic/episodic/procedural taxonomy; [OpenAI Agents SDK session-memory guide](https://developers.openai.com/cookbook/examples/agents_sdk/session_memory) for session storage and history management; [Mem0 quickstart](https://docs.mem0.ai/platform/quickstart) for scoped memory add/search and optional tool integration. References checked October 2, 2026. Existing local evidence: [prompt/history walkthrough](../app/docs/PROMPT-AND-CATALOG.md), [specification chapter 9](../SPECIFICATION.md#7-context-and-memory-policy) and M29.

**Implementation update — October 2, 2026:** Added user-scoped PostgreSQL records and direct SDK save/search/update/delete tools, memory on/off and per-question write controls, and a Saved memories panel with Edit/Forget and source inspection. Explicit memory-management requests expose memory tools only; business investigations retain marketplace MCP tools plus memory tools. Search spans all three types using bounded keywords. Updates use version checks; business revision is not changed by memory writes. [Lab walkthrough](../app/eval/memory-v1/README.md). [M35 report](../app/results/memory-v4-2026-10-02/REPORT.md): 65 regression tests passed and thirteen final live memory questions checked. The operation checks are not a general answer-quality benchmark; inspect the report for known limits.

**Manual acceptance — October 2, 2026:** The user reports the memory walkthrough working successfully. Preserve this as user-reported acceptance of the bounded lab, separate from automated checks; no individual-case human-review export is available. The two UI checkboxes now have aligned rows. Teach the difference between enabling retrieval and granting one-question write permission; the latter resets without deleting saved memories.

**Pending now:** Recorded lesson and selected remaining manual catalogue demonstrations. Broader held-out/repeated evaluations are optional; automatic extraction, auto-compaction, shared procedural memory and a memory-platform comparison remain later enhancements.

---

## F. Agentic Platforms

Reuse the marketplace support tasks, MCP tool contracts and evaluation criteria to compare component ownership, quality, costs, engineering effort and control. These tracks change different parts of the stack; disclose model, prompt, context and hosting differences before comparing results.

**Orientation:** Compare four provider categories—cloud platforms, frontier model providers with agent tooling, framework-led independents and platform-led independents—then map them onto models, frameworks, managed infrastructure, builders and governance. Supporting several models or clouds is different from governing agents across runtimes.

**Companion material:** [Platform landscape and customer fit](PLATFORM-GUIDE.md#platform-landscape-positioning-and-customer-fit) · [Component ownership worksheet](PLATFORM-GUIDE.md#common-comparison-agentic-system-components-and-ownership). The guide holds product references, technical boundaries, architecture, dashboard steps, detailed evidence and enhancements.

### 19. Google Gemini Enterprise Agent Platform

**Draft learner practice — for review, not finalized:**

- **Exercise:** Connect a hosted Google agent to the shared business MCP backend, ask a question and follow-up, then inspect its native trace.
- **Solution to prepare:** Setup instructions, configuration template without credentials, successful tool/source checkpoints and an annotated native trace.

Main lesson document: [Google platform walkthrough — architecture, setup steps and checks](GOOGLE-PLATFORM-WALKTHROUGH.md). ADK is deployed. Hosted SQL/RAG and seven memory checks passed, including native Memory Bank recall under the actual Playground user. Deployment Traces → Session view and retrieved memory in model input are verified. Setup, CLI commands, results and trace-viewing steps are all in that same guide.

- **Learning objective:** Identify which responsibilities a native agent platform takes over.
- **Lab:** Build natively with ADK on the managed runtime; reuse business tools and evaluate shared cases, sessions, retrieval and memory.
- **Status:** Bounded experiment phase complete; user manually validated short-term memory, long-term memory and general questions October 8. Hosted checks and native trace inspection passed. Slides, speaker notes, homework and recording preparation remain later work.
- **Details:** [Approach, comparison criteria, evidence and pending work](PLATFORM-GUIDE.md#19-google-gemini-enterprise-agent-platform).

### 20. Lyzr Agent Studio

**Draft learner practice — for review, not finalized:**

- **Exercise:** Connect Lyzr to the same business MCP tools, ask the shared question and inspect its saved sources and native memory behavior.
- **Solution to prepare:** Setup instructions, configuration template without credentials and annotated tool, source and native-memory checkpoints.

- **Learning objective:** Reuse business middleware while moving agent execution and native memory to a managed platform.
- **Lab:** Configure the model/prompt, connect seven remote business MCP actions, test native Cognis memory and call the deployed agent API.
- **Status:** Included hands-on platform chapter. Local/cloud marketplace adapters, hosted business calls, sessions and memory were validated. Learner packaging remains; preserve the historical checklist-use limitation.
- **Details:** [Architecture, component ownership, dashboard steps, tracing, user experience, test evidence and enhancements](PLATFORM-GUIDE.md#21-lyzr-agent-studio).

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

## Scope for v1

**Required v1:** Six sections A–F, twenty-two numbered chapters: welcome; Anatomy with local setup and first-agent practice; Core Components; Observability, Evaluation and Security; Advanced Agent Topics; Google and Lyzr hands-on platform chapters; an Other Agent Platforms overview; and Choosing an Agent Platform. Detailed guardrails and security are combined in chapter 15. Observability covers capability criteria and standalone-platform comparison, with Langfuse/LiteLLM as the implemented example; native telemetry belongs in each platform chapter. Use the local SDK for the main course demos.

**Not required for this release:** Additional deployment labs for AWS, Claude Managed Agents, Microsoft Foundry or OpenAI Agents API. Mention these in chapter 21 through slides. AWS hands-on hosting remains an open future addition if bandwidth permits. Multi-agent and memory remain required.

**Timeline rule:** keep the first multi-agent and memory implementations bounded. If time becomes tight, reduce variants, optional comparisons and recording breadth before removing those two required learning topics. Confirm any further scope change with the course owner.

## Completed experiments — confirmed October 8, 2026

The owner confirmed that the Gemini experiments (19), session-only versus persistent-memory comparison (18), and revised security marker comparison (15) are done. Do not list these as remaining experiments. Preserve their bounded evidence and distinguish completion of the experiment from preparation of the lesson.

- **Gemini:** [Platform walkthrough and verification](GOOGLE-PLATFORM-WALKTHROUGH.md); native SQL/RAG, session/memory checks and trace inspection are recorded in chapter 19.
- **Memory:** [Current conclusions](../app/docs/MEMORY-STATUS.md) and [repeatable comparison report](../app/results/memory-repeatable-20261003T093153094486Z/REPORT.md). Remaining selected manual demonstrations are lesson preparation, not reopening the completed comparison.
- **Security marker:** [Combined teaching guide](../app/docs/SECURITY-CHAPTER-DEMO.md) and chapter 15's recorded user acceptance. No new independent trace review is implied by this completion confirmation; historical reports remain unchanged.

## Experiments and implementation remaining

1. Chapter 7 context omission/restoration comparisons completed October 10; the exercise scope is closed. Use the selected explanation-completeness example for the optional demo comparison. Remaining component preparation includes tool-contract changes (8) and retrieval off/on and policy-date selection (9).
2. Cloud deployment and hosted runtime connections are verified; rehearse setup in a fresh project and on a clean machine for learner release. Resolve any optional Lyzr checklist-use enhancement separately.
3. Complete any remaining fixed-workflow or controlled scheduling variants for chapter 17; retain the completed single-agent/worker and reviewer-workflow results. The chapter 18 memory comparison is complete.
4. Assemble the platform comparison (22) from the SDK baseline and completed Google/Lyzr tracks. Prepare the documentation-based overview (21); AWS deployment is deferred and does not block this release.
5. During the relevant chapter preparation, revisit the low-priority current-version routing/cache refresh (16) and pending online evaluation (14); neither blocks overall experiment completion.
6. Proposed extension: a bounded code-versus-model calculation experiment, such as payout eligibility. Treat the deterministic tool as a variant to measure, not a preselected fix.
7. Deferred model migration: replace remaining Nano comparison aliases/teaching configurations during later model preparation. GPT-5.4 is already the interactive default; this outline update does not migrate model configurations or rerun historical comparisons.

## Lesson preparation and recording remaining

Lecture breakdown and the recording tracker are deferred to delivery/recording preparation. At that stage, split each chapter into suitable explanation, demo and exercise lectures, and track slides, speaker notes, homework, demo verification, recording and editing.

1. Verify the existing written setup guide on a clean machine; publish the repository/checkpoints, costs and start/reset checks. Include saved results for learners who limit paid calls.
2. For each lesson, prepare slides, speaker notes, participant homework, starting checkpoints, expected observations, verification steps and costs; refine the hands-on demo, then record and edit. Feature or experiment completion alone is not course readiness.
3. Package the existing evaluation runner into add-a-case, judge-calibration and repeated-run exercises (15), plus the completed local/remote MCP comparisons (8).
4. Organize monitoring demonstrations from existing Langfuse/LiteLLM dashboards (14); no upfront dashboard build is required.
5. Prepare chapter 15 materials from the existing combined security guide and OWASP map. The marker comparison is complete; broader memory/multi-agent attacks remain optional, and full Top 10 coverage is not claimed.
6. Package the completed memory (19) and Gemini (20) experiments; select any remaining manual demonstrations without treating them as unfinished core comparisons.
7. Record the welcome/roadmap after the chapters. Discuss the separate promotional video's content and script before recording it at the same final stage.

## Risks

- **Model retirement on 11 Dec 2026.** `gpt-5-nano-2025-08-07` and `gpt-5-2025-08-07` both shut down. OpenAI's named replacements are `gpt-5.6-luna` ($0.20 / $1.20 per 1M tokens, vs nano at $0.05 / $0.40) and `gpt-5.6-sol` ($4 / $20, vs GPT-5 at $1.25 / $10). Migration of the remaining historical comparison aliases is deferred to later model/chapter preparation; GPT-5.4 is already the interactive default. Verify availability/prices and the selected teaching pool before recording those labs, and retain Nano/GPT-5 results as dated case studies. [OpenAI deprecations](https://developers.openai.com/api/docs/deprecations)
- **Time.** About 9 weeks for the remaining build plus recording. Multi-agent and memory remain required; budget for their labs and recording before optional platform breadth.
- **Platform change.** Managed agent platforms change quickly. Date the platform lessons and plan updates.
- **Benchmark terms.** Check each cloud provider's terms before publishing comparative numbers.

## Blogs that feed the course

Published: model routing Parts 1 and 2 (feed chapter 16). Candidate next posts, each one a lesson:
- the failure clinic (chapter 13)
- judge calibration (chapter 14)
- the model-retirement rerun (chapters 6 and 14)
- Gemini vs baseline (chapter 19)
- attacking our own agent: the OWASP map and measured attack success (chapter 15)

### Automatic checklist retrieval and sidebar state retention — October 3, 2026

Prompt v10 explicitly instructs investigations to search relevant saved checklists/checkpoints before business analysis, without the user having to name the checklist. The original refunded-order question retrieved the checklist and answered correctly with GPT-5.4; Nano still skipped memory and omitted the full-refund explanation. Retrieval remains model-driven, not guaranteed. The UI default was Nano at the time of this October 3 experiment; the current default is GPT-5.4. Support remains mounted while hidden on other sidebar pages: selected conversation, displayed answers and unsent draft survived browser navigation to settlement and back. Reload/login restore remains distinct. 12 frontend checks passed; frontend/backend built and deployed. [Verification and traces](../app/results/memory-auto-checklist-v10-2026-10-03/REPORT.md).


### Repeatable memory suite and separate test workspace — October 3, 2026

Added a [24-case short-/long-term memory catalogue](../app/eval/memory-v2/README.md), versioned expected outcomes and a runner for eight scenarios/19 questions with memory-off controls. Fixture-only validation prepared each scenario twice and restored the seeded `market_test` baseline; no inference or judge calls were made. Live text-answer grades remain review-required. Basic CRUD/isolation/version boundaries retain the existing regression suite. Optional test UI uses `http://127.0.0.1:5179/`, labelled MEMORY TEST WORKSPACE; normal UI stays on `http://localhost:5178/` and `market`. Both UI instances retain the existing support-model alias; the live runner can explicitly select Nano or GPT-5.4. Stop test services before resets, and do not run concurrent market_test suites. This is baseline reset, not restoration of arbitrary user-modified test data.


### Eight-scenario GPT-5.4 memory verification — October 3, 2026

[Live memory suite report](../app/results/memory-repeatable-20261003T093153094486Z/REPORT.md): eight scenarios/19 questions completed; all six required retrievals and 10 memory-off questions passed. Assistant review found 19 factually correct answers, with one noncanonical citation format in the policy-conflict answer (shortened evidence handles); subsequent UI-backed checking confirmed all source links resolve. Same-conversation quantities reused previous evidence with zero tools, even with long-term memory off. Preference override retrieved the conflicting memory without overwriting it. Seeded test baseline restored; optional test UI restarted. Estimated uncached model cost $1.02, no paid judge. One trial only; remaining manual catalogue cases are not claimed tested.


### Memory citation grading correction — October 3, 2026

[Policy-conflict rerun](../app/results/memory-repeatable-20261003T094355178246Z/REPORT.md): both GPT-5.4 answers correct with full canonical citations; zero unavailable sources; estimated cost $0.31. Seven citation regressions passed. The earlier 19-question report incorrectly treated shortened raw IDs as broken links; existing UI normalization already resolves those recorded IDs. All 19 saved answers passed checking through the actual UI functions. Added a reusable UI-backed citation checker, corrected report/review and documented format-versus-resolution grading. No agent prompt or resolver change needed. Test baseline restored and test services restarted.


## Agreed course preparation sequence — October 7, 2026

Finish the required experiments and update each section’s evidence/pending work, then finalize the course outline. Next work section by section: create slides, speaker notes and participant homework; refine the hands-on demo for recording; then record the section. Slides, notes and homework are deferred from the current experiment/documentation phase. Completion of a bounded lab does not mean the lesson is recording-ready.


### Security lesson closure — October 7, 2026

[OWASP 2026 course map](../app/docs/OWASP-SECURITY-MAP.md) connects the existing injection/privacy trials, read-only SQL/MCP constraints, memory ownership and runner limits. [Two final demonstrations](../app/results/security-boundaries-2026-10-07/REPORT.md) passed: real memory MCP denied cross-owner search/update/delete and disabled writes, with owner access and unchanged-record controls; GPT-5.4 repeated an ordinary visible marker but withheld the private instruction marker. One disclosure prompt only, no real secrets, no paid judge. Test fixtures cleaned up and business revision unchanged. Role-specific SQL/RAG authorization was not added solely for the lesson. The 2025 table remains a historical planning reference; use the linked 2026 map for new materials. Bounded chapter experiments are complete; full OWASP coverage is not claimed. Slides, notes, homework and recording remain later preparation work.

Security lesson revision: detailed guardrails and agent security are combined in chapter 15. The memory-permission demo is removed from the teaching sequence; the combined guide contains the revised marker comparison and OWASP notes. Historical test reports remain unchanged.

### Next course work after security consolidation — October 7, 2026

Guardrails and agent security share chapter 15 and one main guide; monitoring, tracing and evaluation retain their separate sections. No memory-permission demo or new read-by-ID tool is required. The revised marker UI has user-reported validation. Next substantive experiments focus on Google's enterprise agent platform, reusing the application/MCP baseline. Slides, speaker notes, homework and final recording preparation follow experiment completion and outline finalization.

### Marketplace interface runtime selection — implementation follow-up

The common interface can select SDK, Lyzr or Google ADK; a change begins a fresh conversation and history retains its original runtime. Native platform setup stays in the platform chapters. [Configuration and acceptance](../app/RUNTIME-SELECTOR.md) describe verified local/cloud integration and remaining learner rehearsal checks. Cloud Google/Lyzr adapter acceptance is verified; local Google credentials are configured and its local main question/follow-up passed.
