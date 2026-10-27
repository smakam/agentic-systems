# Google Agent Platform reference answers

These are interpretation guides, not fixed transcripts or a claim that a learner's fresh deployment will match the instructor's environment.

## Main lesson versus optional extension

Support Agent Basics is the separate small agent with packaged fictional JSON and a native lookup function. Its core Playground demonstration does not require MCP or the marketplace stack. Marketplace Support ADK Lab is the existing full integration: the cloud agent invokes authenticated business MCP backed by business records and policy retrieval. The two deployments serve different teaching purposes.

## Basics practice and the new explicit save path

Basics uses native Python function tools and packaged fictional order JSON, not MCP. The revised `remember_preference` tool sends only a presentation preference explicitly supplied in the current user message to Google Memory Bank, scoped by the ADK context. Its `generation_requested` result is not evidence that extraction has completed. Confirm a stored record and memory preload in a fresh session under the same native user; answer layout alone is insufficient. Current formatting instructions override saved preferences. The new tool's live deployment verification is pending; the prior documented memory results used the separate CLI save path.

The instructor covers both architectures. Core learner practice is Basics: questions, lookup evidence, session/fresh-session contrast, native trace, memory and logs. Full Marketplace provisioning is optional: the chat backend invokes the hosted agent, which calls authenticated business MCP for database and policy evidence. Test its own memory controls rather than assuming it shares the new Basics save tool.

## Architecture and responsibilities

ADK is an open-source framework, analogous in role to OpenAI Agents SDK. It defines instructions, tools and agent execution. The managed Google runtime hosts the application; Sessions, Memory Bank and telemetry are separate services. ADK can run in another suitable environment and can use external models through supported integrations. Deployment flexibility also means owning appropriate operations, dependency management and model/tool access. Selected managed services can be mixed with ADK; it is not an all-or-nothing choice.

In the optional full integration, marketplace UI/backend placement and the hosted agent's MCP target are independent. A UI runtime selection invokes the configured deployed agent; it does not deploy it or rewrite its MCP profile. Business middleware authenticates calls and exposes the database/policy tools. Current instructor acceptance used the cloud profile. Original local acceptance predates the migration; a later local switch-back has not been retested.

## Evidence, session and memory

For order-2, report what your fixture/tool actually returned. A same-session follow-up may resolve “their” through retained context. A fresh conversation should not be credited with session continuity merely because it guessed the same order. Inspect the current session events and tool result.

A saved preference across distinct sessions needs evidence of memory formation and later retrieval under the same client identity. History within one session is a different mechanism. A memory-assisted formatting choice does not establish a business fact or replace order/policy evidence.

## Tracing, evaluation and cost

Native traces/session events expose hosted internal calls. The optional marketplace Langfuse observation records the application boundary. Logs/monitoring describe operation; evaluation assesses quality. Model-based evaluation may consume judge/autorater inference tokens, and computation-based metrics have a separate charge category. Candidate response generation may add model inference. Record actual enabled categories; don't invent dollar amounts or assume every available service was used.

## What a good submission shows

A clear placement diagram, actual tool evidence, observed same/fresh-session behavior, explicit identities/resource boundaries, useful trace links and honest limits. The optional cloud guide has a verified existing deployment but no complete fresh-project learner rehearsal; describe adaptation and failures honestly. Cleanup must affect only learner-created resources. An observation-only submission should not claim provisioning or isolation tests it did not perform.

## Basics fixture reference

The packaged JSON is a fictional snapshot, not live commerce. `lookup_order(order_id)` supplies record fields and source metadata; unknown IDs return `found=false`.

| Record | Source facts |
|---|---|
| order-demo-1 | 2 Ceramic Mug Sets; payment received; shipment not dispatched; payout held |
| order-demo-2 | 1 Canvas Weekender; payment received; delivered; payout released |
| order-demo-3 | 1 Desk Lamp; cancelled; payment refunded; shipment cancelled; payout not applicable |
| order-demo-999 | No packaged record; do not invent a status |

A held status does not establish its reason or policy eligibility: Basics has no policy tool. The fixture unit-level facts above are source references; hosted product lookup, same-session payout follow-up, missing-record response and native traces have been checked. Memory generation and scoped stored-preference search passed; another test user returned no matching record. A completed native trace subsequently verified preference preload and a fresh order-demo-2 answer using the saved three-column layout. Full instructions: [instructions.txt](../../../../app/google/basics/support_agent_basics/instructions.txt). Native memory generation is an explicit platform operation using the saved session and verified owner; it is not automatic Mem0 conversation-end extraction.

## Standalone setup and walkthrough

The chapter setup guide owns prerequisites, editable environment values, installation and the test/deploy commands. The instructor guide owns the questions and observations after deployment. A new Basics runtime must be distinct from the existing marketplace agent. It uses no MCP secret, SQL database or marketplace UI. A fresh-project installation is not yet an independently completed learner rehearsal.

## Bounded hosted memory result

Native trace 565cdc596fb140716fb98df5cb2afea0 subsequently completed and verifies the saved preference in PAST_CONVERSATIONS, a successful lookup_order span and an order-demo-2 answer with Finding, Evidence and Next action columns. Memory formation, scoped retrieval, other-user-empty search and fresh-session application are therefore observed separately. The first run reported Google 500 INTERNAL; the CLI retry timed out at 90 seconds before the native run completed in about 106 seconds. This does not mean the CLI verification suite passed or establish the internal cause. One model answer called the packaged fixture a “database record”; the source is fictional JSON, not a live database.
