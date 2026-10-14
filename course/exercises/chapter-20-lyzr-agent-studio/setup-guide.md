# Setup: Support Agent Basics in Lyzr

## Workspace and prerequisites

Use your authorized **Lyzr Studio account**, its model connection and available credits. The core setup needs no marketplace UI, SQL database, MCP server, tunnel or full Cloud Setup. Create a separate agent and separate KB; preserve the existing Marketplace Support MCP agent and its connections.

The instructor's separate [Basics agent](https://studio.lyzr.ai/create-new-agent/6acf95f3272a149412fd9e7c?tab=playground) has passed bounded API lookup, missing-ID and same-session follow-up checks. Native Playground lookup, same-chat follow-up and missing-ID checks passed, with actual KB source chunks visible in Activity; cross-session memory is untested. Account controls and model availability vary; record what you actually configure. Model calls, ingestion and indexing may incur charges.

## Prepare the shared fictional data

From the repository root:

```sh
cd app/lyzr/basics
python3 prepare.py
python3 -m unittest -v test_basics.py
```

Upload only `orders-knowledge.txt`. Its source is `app/google/basics/support_agent_basics/orders.json`; `fixture-manifest.json` records the source hash. There are exactly three fictional orders, with a dataset/as-of marker. This is native KB retrieval, not a live order system or Python `lookup_order` execution.

## Create the native Knowledge Base

1. In Knowledge Base select New and the **Basic/Classic** option available in your account.
2. Name it **Support_Agent_Basics_Orders**. Select your authorized embedding model and vector store; record those choices.
3. Upload `orders-knowledge.txt`, train/index it, and wait until the native status says ready.
4. Test retrieval for `order-demo-1`, `order-demo-2`, and `order-demo-999`. Inspect chunks and the complete catalogue included in each record. A missing search hit alone is not proof that an order is absent.

## Create the separate agent

1. Select Agents → New Agent. Use **Support Agent Basics** as its name.
2. Role: **Read-only fictional order investigator**. Goal: **Answer order questions using only the attached fictional source records**.
3. Choose the configured **OpenAI GPT-5.4 Mini**, or record your authorized alternative.
4. Paste `app/lyzr/basics/agent-instructions.txt` into Instructions.
5. Attach only **Support_Agent_Basics_Orders**. Do not attach old marketplace MCP tools, browser tools, manager agents or unrelated knowledge.
6. Save/Create. Read back the name, model, instructions and KB attachment.
7. Enable native Cognis for session continuity and keep **Cross Session OFF** for the core demo. The first API follow-up failed without session memory; a fresh two-turn run passed after enabling it. Cross-session preferences are a separate optional experiment: configure extraction separately and verify actual stored/retrieved context before claiming persistence.
8. Open Playground and follow [instructor-demo.md](instructor-demo.md). Inspect native Activity/Traces and actual knowledge retrieval.

## Cleanup and evidence

Record your new agent and KB identities, model, source hash and acceptance results without credentials. Remove only your own lab agent/KB and lab memories when finished. Preserve the original integration agent. Deleting a KB or agent is not evidence that all telemetry or historical sessions were erased.

Official references: [Studio Builder](https://docs.lyzr.ai/enterprise/agent-studio/agents/studio), [Classic Knowledge Base](https://docs.lyzr.ai/enterprise/agent-studio/knowledgebase/studiokb), [model connections](https://docs.lyzr.ai/enterprise/agent-studio/connections/models).
