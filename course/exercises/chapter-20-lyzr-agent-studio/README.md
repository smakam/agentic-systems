# Chapter 20: Lyzr Agent Studio

The core lesson uses **Support Agent Basics** in native Lyzr Studio and Playground, with a separate Knowledge Base containing fictional orders. It uses the same JSON source as the Google Basics lab, converted to TXT for native Lyzr ingestion. It does not run Google's Python lookup tool or connect to the marketplace database.

1. Download the supplied TXT and configure the native KB/agent once with [setup-guide.md](setup-guide.md).
2. Walk through native behavior with [instructor-demo.md](instructor-demo.md).
3. Optionally connect your full cloud marketplace using [exercise.md](exercise.md).
4. Compare your observations with [solutions/answers.md](solutions/answers.md).

**Readiness:** the separate [Support Agent Basics Playground](https://studio.lyzr.ai/create-new-agent/6acf95f3272a149412fd9e7c?tab=playground) is created with OpenAI GPT-5.4 Mini and its own trained Knowledge Base. Bounded API checks passed for order-demo-1 products/quantity, order-demo-2 released payout, missing order-demo-999 and a fresh two-turn products → payout follow-up (held). Native Cognis is enabled with Cross Session OFF. Responses contain retrieved source chunks in `module_outputs.documents`; scores are retrieval relevance, not answer correctness. Native Playground lookup, same-chat follow-up and missing-ID checks passed, with actual KB source chunks visible in Activity; the optional owner-scoped cross-session API experiment also passed; the core setting remains OFF. Native cross-session Playground UI behavior is a separate observation. See [the verification record](../../../app/lyzr/basics/verification.json). Preserve the existing Marketplace Support MCP agent.

## Optional developer regeneration

The TXT is already prepared and committed. Only if you change the source JSON, run `python3 prepare.py` and `python3 -m unittest -v test_basics.py` from `app/lyzr/basics`; the technical package README explains source hashes and deployment checks. These commands are not learner prerequisites.
