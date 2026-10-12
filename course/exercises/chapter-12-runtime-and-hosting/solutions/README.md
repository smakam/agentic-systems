# Worked solution

Use the commands in ../exercise.md with your own Cloud project and credentials. The reference implementation is `app/backend/marketplace/hosting_worker.py`, `hosting_client.py`, `app/cloud/Dockerfile.hosting-lab`, `app/compose.ch12.yaml` and the scripts here.

The worker owns the Agents SDK loop and calls OpenAI directly; HTTP MCP owns tool execution, snapshot and evidence contracts. The local authenticated backend owns history and saved runs. Its opt-in adapter refuses any database other than `ch12_hosting_lab`. The worker exposes no database credentials or connections. The cloud host provides one CPU, 1 GiB memory, 180-second request deadline, concurrency one and zero-to-one instances; the inner loop has eight turns and a 150-second deadline. A completed answer must cite retained current evidence and confirm investigation cleanup. Hosting does not imply durable execution.

Expected business result: order-2 has a held payout with an unresolved delivery condition. The follow-up retains the order reference while obtaining current order/policy evidence. Exact prose, model calls and tool sequences may vary. Check actual saved evidence rather than matching a sentence. The validation report records the observed outcome and any limits.

Direct GPT-5.4 reasoning/tool requests use OpenAIResponsesModel (Responses API). Chat Completions rejects this model with reasoning-enabled function tools; the full gateway baseline is a separate route. Five contract checks cover direct Responses selection, bounded history, unknown-citation rejection, cleanup on interruption, auth/instruction boundaries and fixed-database isolation.
