# Setup: Support Agent Basics in Lyzr

## Workspace and prerequisites

Use your authorized **Lyzr Studio account**, its model connection and available credits. The core setup needs no marketplace UI, SQL database, MCP server, tunnel or full Cloud Setup. Create a separate agent and separate KB; preserve the existing Marketplace Support MCP agent and its connections.

The instructor's separate [Basics agent](https://studio.lyzr.ai/create-new-agent/6acf95f3272a149412fd9e7c?tab=playground) has passed bounded API lookup, missing-ID and same-session follow-up checks. Native Playground lookup, same-chat follow-up and missing-ID checks passed, with actual KB source chunks visible in Activity; the optional cross-session API experiment also passed; native UI cross-session record inspection is not claimed. Account controls and model availability vary; record what you actually configure. Model calls, ingestion and indexing may incur charges.

## Use the supplied fictional data

Download the already prepared [orders-knowledge.txt](https://github.com/smakam/agentic-systems/blob/main/app/lyzr/basics/orders-knowledge.txt) from GitHub using its Download raw file option. No Python setup or regeneration is required for this lab.

This TXT comes from the same three-order fictional JSON used by Google Basics. Each record includes the dataset/as-of marker and complete catalogue. Upload it into **Lyzr Knowledge Base**, not the agent chat. Lyzr retrieves indexed source chunks; it does not execute Google's Python lookup function or query live marketplace records.

## Create the native Knowledge Base

1. In Knowledge Base select New and the **Basic/Classic** option available in your account.
2. Name it **Support_Agent_Basics_Orders**. Select your authorized embedding model and vector store; record those choices.
3. In this Knowledge Base, choose **Add Source → Add File**, select the downloaded `orders-knowledge.txt`, then **Review Upload**. Complete upload/indexing and confirm the document is available before attaching this KB to the agent.
4. Test retrieval for `order-demo-1`, `order-demo-2`, and `order-demo-999`. Inspect chunks and the complete catalogue included in each record. A missing search hit alone is not proof that an order is absent.

## Create the separate agent

1. Select Agents → New Agent. Use **Support Agent Basics** as its name.
2. Role: **Read-only fictional order investigator**. Goal: **Answer order questions using only the attached fictional source records**.
3. Choose the configured **OpenAI GPT-5.4 Mini**, or record your authorized alternative.
4. Open the supplied [agent-instructions.txt](../../../app/lyzr/basics/agent-instructions.txt), copy its contents and paste them into Instructions.
5. Attach only **Support_Agent_Basics_Orders**. Do not attach old marketplace MCP tools, browser tools, manager agents or unrelated knowledge.
6. Save/Create. Read back the name, model, instructions and KB attachment.
7. Enable native Cognis for session continuity and keep **Cross Session OFF** for the core demo. The first API follow-up failed without session memory; a fresh two-turn run passed after enabling it. Cross-session preferences are a separate optional experiment: use the exact ON settings, synthetic owner/session checks and restoration steps in [instructor-demo.md, Part D](../../exercises/lyzr-agent-studio/instructor-demo.md#optional-native-memory-reference). The bounded API experiment passed; the core default remains OFF.
8. Open Playground and follow [instructor-demo.md](../../exercises/lyzr-agent-studio/instructor-demo.md). Inspect native Activity/Traces and actual knowledge retrieval.

## Cleanup and evidence

Record your new agent and KB identities, model, source hash and acceptance results without credentials. Remove only your own lab agent/KB and lab memories when finished. Preserve the original integration agent. Deleting a KB or agent is not evidence that all telemetry or historical sessions were erased.

Official references: [Studio Builder](https://docs.lyzr.ai/enterprise/agent-studio/agents/studio), [Classic Knowledge Base](https://docs.lyzr.ai/enterprise/agent-studio/knowledgebase/studiokb), [model connections](https://docs.lyzr.ai/enterprise/agent-studio/connections/models).

## Optional cloud extension

The full cloud architecture and integration steps are in [LYZR-PLATFORM-PLAN.md](../../LYZR-PLATFORM-PLAN.md) and [the optional exercise](../../exercises/lyzr-agent-studio/exercise.md). They are separate from this core TXT → native KB → Basics agent → Playground setup and require completed Cloud Setup.
