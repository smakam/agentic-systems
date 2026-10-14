# Lyzr Support Agent Basics — native Knowledge Base lab

Separate agent and separate KB; preserve the existing Marketplace Support MCP agent. Uses the exact Google Basics fictional JSON as source, converted deterministically to TXT because Lyzr documents native TXT ingestion. The agent retrieves a managed KB; it does **not** run Google's native Python lookup_order or require marketplace middleware, SQL, MCP or chat UI. KB indexing/model calls may incur plan-dependent charges.

## Use the supplied fictional data

Upload the already supplied `orders-knowledge.txt` directly in Studio. No local script, Python installation or unit test is required for the learner's native Playground exercise. `fixture-manifest.json` identifies the exact shared JSON source and hash.

Developer-only regeneration: from this directory, `python3 prepare.py` regenerates the TXT from the shared Google JSON, and `python3 -m unittest -v test_basics.py` checks the package. These are optional maintenance commands, not lab prerequisites.

## Native Studio setup

1. Knowledge Base → New → Basic. Name `Support_Agent_Basics_Orders`; select the account's authorized embedding model and vector store. Upload `orders-knowledge.txt`, train, and wait for ready. Test retrieval for order-demo-1, order-demo-2 and missing order-demo-999 before attaching it. Record actual retrieved chunks; absence of a search hit is not automatically proof an order is absent. The complete catalogue inside every record supplies the missing-ID boundary.
2. Create a **new** agent named **Support Agent Basics**. Role: read-only fictional order investigator. Goal: answer only from supplied source records. Select the configured OpenAI gpt-5.4-mini model (or record your authorized alternative). Paste `agent-instructions.txt`, attach only the new Knowledge Base. No old MCP tools, browser tools or manager agents. Save/Create and read back name, model and KB attachment.
3. Configure native Cognis explicitly for session continuity and, if testing long-term preferences, Cross Session and extraction guidance. This is a separate setting from KB retrieval. Record actual available account controls; no fabricated CRUD/isolation guarantees.
4. Use native Playground. Inspect Activity/Traces for knowledge retrieval and model inputs/output. Do not call a KB retrieval span a Python function-tool execution.

## Exact bounded walkthrough

Fresh chat: “What products and quantities are in order-demo-1?” Expected: two Ceramic Mug Sets; inspect source record. Same chat: “What is its payout status?” Expected: held, with retained order identity. Fresh chat: “What is the payment status of order-demo-999?” Expected: not in the fictional fixture, no fabricated payment status. Another fresh chat asking only “What is its payout status?” should clarify the order rather than reuse a prior chat's order silently.

## Optional cross-session native-memory exercise — API verified

The settings and prompts below describe the optional Studio observation path; the complete provenance/isolation acceptance was run through the API, not a separate UI long-term-memory rehearsal. Use **this separate Support Agent Basics** agent in Studio, not the marketplace agent. Keep its same KB attached. In Build → Memory → Configure Memory, enable native Cognis **Cross Session ON**. Set extraction instructions to: “Retain explicit durable user presentation preferences faithfully. Do not store fictional business order states, payment/shipment/payout facts, credentials, assistant acknowledgments or one-answer overrides as durable user preferences.” Save/Update and read back the setting. Cross Session OFF still supports the core same-chat exercise.

1. Start a fresh chat under one actual client user identity. Say: **“I have a durable support-answer preference: start each answer with the heading cobalt-sparrow, followed by the headings Finding, Evidence and Next action. Please acknowledge this preference briefly.”** Use your own harmless distinctive marker if repeating the lab.
2. Allow native extraction to complete. This Studio integration automatically generated a native record from the completed exchange; we did **not** invoke Cognis add explicitly. Acknowledgment alone is not persistence proof. Inspect native memory records/search for the actual owner and this agent: content, source session, original user text and timestamps.
3. Start a **new chat with the same actual user identity**, not a continuation. Ask **“What support answer headings do I prefer?”** Record recalled headings and native retrieval/context. The source preference must come from the old session, not a repeated seed in this request.
4. In another fresh chat ask **“What is the payout status of order-demo-2?”** Expect **released** from the fictional KB, with the remembered heading style. Inspect KB chunks independently from personal-memory retrieval; the preference does not establish the payout fact.
5. Optional instructor/API control: use a different synthetic authenticated/client identity with the same agent. Native record listing was empty and **“What support answer headings do I prefer?”** returned no verified preference. A new Playground chat alone is not a different user. Do not claim a user-isolation test if you cannot control/verify the identity.

In the bounded API rehearsal, the owner began with zero records; one extracted preference was found on the first search about **1.01 seconds after the seed response**. Its owner, agent and seed-session fields and original user text matched. Fresh recall, fresh business application and the other-owner negative control passed. This timing is an observation, not a promised extraction SLA. `cross-session-verification.json` preserves the native record/source receipt and four model responses; `verification.json` includes the combined checks. Cross Session was restored OFF and read back after the test. Retention CRUD and broader authorization behavior were not tested.

Optional reproducible instructor/API check, from `app/lyzr/basics`:

```bash
python3 -m unittest -v test_basics.py
python3 verify_cross_session.py --agent-id YOUR_OWN_BASICS_AGENT_ID --wait 35
```

The runner reads `LYZR_API_KEY` privately from the environment or ignored `app/.env`, uses your explicitly supplied own Basics agent ID (or an existing local creation manifest), verifies the separate Basics name/native Cognis configuration and no external tools, generates a unique synthetic owner, enables ON, makes four bounded model calls, polls native scoped records, checks original-text/source-session provenance, and restores the original Cognis configuration in `finally`. It never directly adds memories. It writes `cross-session-latest.json` locally (ignored); the accepted historical receipt is `cross-session-verification.json`. This runnable version was checked with offline failure/restore and provenance tests; the earlier live receipt is from the equivalent bounded flow, and no extra paid rerun was made merely for refactoring. Do not blindly retry a failed paid run.

For read-only record inspection, the official hosted Cognis API supports `GET https://memory.studio.lyzr.ai/v1/memories` with owner_id, agent_id, cross_session=true and limit parameters, and `POST /v1/memories/search` with the same trusted scope plus query. Authenticate privately with the Lyzr API key. Use the **actual** Playground/client owner; do not guess it from a URL or substitute the API test's synthetic identity. The [official search reference](https://docs.lyzr.ai/enterprise/lyzr-blocks/cognis/api/search-memories) explains the scope/source fields. Do not put keys in submitted screenshots or browser query strings.

## Current verified status — October 14, 2026

A separate **Support Agent Basics** agent has been created and configuration read back: [native Playground](https://studio.lyzr.ai/create-new-agent/6acf95f3272a149412fd9e7c?tab=playground). It uses its own trained KB, OpenAI gpt-5.4-mini and native Cognis with Cross Session **OFF**, restored and read back after the optional ON test. This keeps the core same-chat demo reproducible; enable ON explicitly for the optional exercise. No external tools/MCP or manager agents are attached. Existing Marketplace Support agent is unchanged.

Bounded API acceptance: order-demo-1 products/quantity, order-demo-2 released payout and missing order-demo-999 passed. The initial follow-up without Cognis asked for the ID; after enabling session memory, a fresh two-turn products → payout run passed (held). Responses include `module_outputs.documents` containing retrieved chunk text, source metadata and scores. Inspect these actual sources; the returned source-score number is not answer correctness. Native Playground Activity inspection passed for KB chunks, the product lookup, same-session follow-up and missing order. Cross-session extraction, scoped records, fresh recall/application and a different-owner negative control passed through the bounded API test below; a native UI cross-session rehearsal is not claimed by that API receipt. See `verification.json` for bounded evidence.

Earlier raw-text ingestion failed, and TXT API upload returned zero documents; direct retrieval exposed an upstream OpenAI quota error. Native Studio upload/training then succeeded on the same KB, followed by API document readback and successful answers. The change does not isolate the quota error's cause, prove a required top-up, or establish a general API defect.

For your own setup, after valid KB training run `python3 deploy.py --kb-id YOUR_NEW_KB_ID`. Set `LYZR_API_KEY` privately and use authorized `LYZR_LLM_CREDENTIAL_ID`/`LYZR_BASICS_MODEL` values if different from defaults. The script requires nonempty documents and creates only a new agent with session memory; it refuses an existing creation manifest and never updates the marketplace agent. Credentials are not serialized. Unknown creation failures require inspection before retrying.

## Official references

- [Classic Knowledge Base](https://docs.lyzr.ai/enterprise/agent-studio/knowledgebase/studiokb)
- [TXT ingestion API](https://docs.lyzr.ai/agent-apis/knowledgebase/trainragtxt)
- [Create Agent API](https://docs.lyzr.ai/agent-apis/agents/Create%20Agent)
- [Knowledge Base attachment configuration](https://docs.lyzr.ai/api-docs/knowledgebase/Knowledge%20Base)

These documented mechanisms do not establish the new account deployment's acceptance until its live checks pass.
