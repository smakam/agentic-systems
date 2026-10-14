# Lyzr Support Agent Basics — native Knowledge Base lab

Separate agent and separate KB; preserve the existing Marketplace Support MCP agent. Uses the exact Google Basics fictional JSON as source, converted deterministically to TXT because Lyzr documents native TXT ingestion. The agent retrieves a managed KB; it does **not** run Google's native Python lookup_order or require marketplace middleware, SQL, MCP or chat UI. KB indexing/model calls may incur plan-dependent charges.

## Prepare

From this directory run `python3 prepare.py` and `python3 -m unittest -v test_basics.py`. Upload only `orders-knowledge.txt`; `fixture-manifest.json` records the shared source hash.

## Native Studio setup

1. Knowledge Base → New → Basic. Name `Support_Agent_Basics_Orders`; select the account's authorized embedding model and vector store. Upload `orders-knowledge.txt`, train, and wait for ready. Test retrieval for order-demo-1, order-demo-2 and missing order-demo-999 before attaching it. Record actual retrieved chunks; absence of a search hit is not automatically proof an order is absent. The complete catalogue inside every record supplies the missing-ID boundary.
2. Create a **new** agent named **Support Agent Basics**. Role: read-only fictional order investigator. Goal: answer only from supplied source records. Select the configured OpenAI gpt-5.4-mini model (or record your authorized alternative). Paste `agent-instructions.txt`, attach only the new Knowledge Base. No old MCP tools, browser tools or manager agents. Save/Create and read back name, model and KB attachment.
3. Configure native Cognis explicitly for session continuity and, if testing long-term preferences, Cross Session and extraction guidance. This is a separate setting from KB retrieval. Record actual available account controls; no fabricated CRUD/isolation guarantees.
4. Use native Playground. Inspect Activity/Traces for knowledge retrieval and model inputs/output. Do not call a KB retrieval span a Python function-tool execution.

## Exact bounded walkthrough

Fresh chat: “What products and quantities are in order-demo-1?” Expected: two Ceramic Mug Sets; inspect source record. Same chat: “What is its payout status?” Expected: held, with retained order identity. Fresh chat: “What is the payment status of order-demo-999?” Expected: not in the fictional fixture, no fabricated payment status. Another fresh chat asking only “What is its payout status?” should clarify the order rather than reuse a prior chat's order silently.

Optional native memory: state “I prefer support answers in a compact table with Finding, Evidence and Next action.” Inspect generation/configuration separately; in a fresh chat ask order-demo-2 payout status (released) and check actual retrieval/context before claiming memory use. Native extraction timing, record audit, and cross-user identity isolation require actual verification; do not infer them from answer formatting alone.

## Current verified status — October 14, 2026

A separate **Support Agent Basics** agent has been created and configuration read back: [native Playground](https://studio.lyzr.ai/create-new-agent/6acf95f3272a149412fd9e7c?tab=playground). It uses its own trained KB, OpenAI gpt-5.4-mini and native Cognis with Cross Session **OFF**. No external tools/MCP or manager agents are attached. Existing Marketplace Support agent is unchanged.

Bounded API acceptance: order-demo-1 products/quantity, order-demo-2 released payout and missing order-demo-999 passed. The initial follow-up without Cognis asked for the ID; after enabling session memory, a fresh two-turn products → payout run passed (held). Responses include `module_outputs.documents` containing retrieved chunk text, source metadata and scores. Inspect these actual sources; the returned source-score number is not answer correctness. Native UI trace inspection and cross-session memory are separate checks and are not claimed complete by these answers. See `verification.json` for bounded evidence.

Earlier raw-text ingestion failed, and TXT API upload returned zero documents; direct retrieval exposed an upstream OpenAI quota error. Native Studio upload/training then succeeded on the same KB, followed by API document readback and successful answers. The change does not isolate the quota error's cause, prove a required top-up, or establish a general API defect.

For your own setup, after valid KB training run `python3 deploy.py --kb-id YOUR_NEW_KB_ID`. Set `LYZR_API_KEY` privately and use authorized `LYZR_LLM_CREDENTIAL_ID`/`LYZR_BASICS_MODEL` values if different from defaults. The script requires nonempty documents and creates only a new agent with session memory; it refuses an existing creation manifest and never updates the marketplace agent. Credentials are not serialized. Unknown creation failures require inspection before retrying.

## Official references

- [Classic Knowledge Base](https://docs.lyzr.ai/enterprise/agent-studio/knowledgebase/studiokb)
- [TXT ingestion API](https://docs.lyzr.ai/agent-apis/knowledgebase/trainragtxt)
- [Create Agent API](https://docs.lyzr.ai/agent-apis/agents/Create%20Agent)
- [Knowledge Base attachment configuration](https://docs.lyzr.ai/api-docs/knowledgebase/Knowledge%20Base)

These documented mechanisms do not establish the new account deployment's acceptance until its live checks pass.
