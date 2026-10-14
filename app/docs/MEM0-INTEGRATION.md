# Mem0 memory integration — Test workspace

This learning integration compares application-owned PostgreSQL memory with Mem0's hosted memory service. It is separate from Google Memory Bank and Lyzr Cognis. Mem0's current behavior must be checked directly; the 2025 paper is an architecture reference, not a guarantee about today's API.

## Workspace and setup

Use the Test workspace at http://127.0.0.1:5179/, its disposable `market_test` database, **Support workspace**, and **OpenAI Agents SDK**. The normal marketplace on port 5178 does not enable this provider. Keep Model routing and Agent design demos off, the gateway guardrail off, and Source authority on.

Configure `MEM0_API_KEY` in `app/.env`. Never put the key in frontend code, committed files, screenshots or teaching examples. The Test backend receives it through `compose.memory.yaml`.

The default idle interval is 900 seconds. `MEM0_IDLE_TIMEOUT_SECONDS` changes it. It measures wall-clock inactivity after the latest answer, independently of the marketplace's simulated business clock.

## Two architectures

- **Internal:** agent → local memory MCP → application MemoryStore → PostgreSQL. Explicit requests plus per-question write permission authorize saves. Records have semantic/episodic/procedural labels, provenance and optimistic versions. Search uses literal keywords.
- **Mem0:** agent → user-scoped retrieval wrapper → hosted Mem0 MCP → provider memories. Application conversation-end/idle jobs submit user/assistant messages for automatic extraction. Search uses the provider's retrieval service. Provider categories and identifiers are retained; our three type labels and optimistic version guarantees are not invented for external records.

The provider is fixed for a conversation. Selecting another provider starts a fresh conversation. Stored memories in one provider are not silently copied to the other.

## Observation walkthrough

1. Choose **Internal memory**, enable long-term retrieval and the per-question write control. In a fresh conversation ask: “Remember that I prefer payout explanations in a compact table with Finding, Evidence, Next action.” Confirm a saved record exists; acknowledgement alone is insufficient.
2. In another Internal conversation, ask: “How do I prefer payout explanations arranged?” Inspect the actual search operation and answer.
3. Choose **Mem0**. In a fresh conversation state: “For payout explanations, I prefer a compact table with Finding, Evidence, Next action.” Do not say remember or save. The current conversation can still use ordinary session history.
4. Choose **New conversation**. This queues extraction of the completed conversation and allows the new conversation to proceed without waiting for Mem0. Observe its background status; idle timeout is the alternative trigger.
5. After extraction completes, inspect **Saved memories · Mem0**. Record the extracted text and provider categories. The service may extract more or less than the expected preference; document the actual result.
6. In a fresh Mem0 conversation ask: “How should you structure a settlement explanation for me?” Inspect retrieval evidence and the answer. A successful answer is not by itself proof that memory was searched.
7. Edit one identified lab memory, then check fresh-conversation recall. Forget that memory and inspect fresh-conversation recall again. Other related extracted entries may still exist; list them before concluding that forgetting failed. Deleting a saved entry does not erase old chat history.
8. Switch to another demo account and check that the first account's lab memories are absent. Return to the original account to inspect its own memories. Do not delete unrelated provider records.

These are controlled observations, not a general claim that Mem0 is more accurate. The save policy and search mechanism change together, so the full comparison is not an isolated search benchmark.

## Lifecycle and debugging

Check four stages separately: which conversation was submitted, whether extraction completed, what memories were retrieved, and how the answer used them. Question traces record the provider and retrieval evidence. Background extraction has a separate Langfuse observation and status link.

Extraction statuses distinguish queued, submitting, provider-pending, complete, failed and no new turns. Completed extraction can legitimately produce zero memories. A restart or network interruption during submission can leave an uncertain outcome; inspect the provider before repeating a write. The application avoids blindly resubmitting such jobs.

Save retries and returning to an old conversation do not resubmit already-processed turns. New completed turns can form a later batch. Only completed answers are submitted; failed investigations are not represented as successful experiences.

Memory remains personal historical context. Current business records, applicable policy and current user instructions retain their existing authority. Neither provider may turn a historical payout observation into proof of current payment.

## Costs and evidence boundaries

Application-model usage remains visible in its existing traces. Mem0's internal extraction/embedding calls are provider operations; their token or monetary costs are not claimed as measured unless the provider supplies them. The locally observed elapsed time is not a breakdown of provider-internal computation. Free-plan limits are account-specific.

The current integration uses hosted MCP with authenticated add, search, list, update, delete and event-status operations. It does not implement a custom graph memory, automatic model training or the survey's advanced latent/parametric memory systems.

## Verified rehearsal (14 October 2026)

The deployed Test workspace completed natural-preference extraction without a save request, then retrieved the extracted preference for a paraphrased question in a fresh conversation. The question recorded an actual hosted-MCP search with one matching memory. Background submission and a new conversation returned immediately; extraction completion was checked independently. The UI showed the saved entry, native category and extraction trace link.

Internal-memory rehearsal also confirmed same-conversation follow-up, clarification in a fresh conversation, explicit semantic saving and recall, and an episodic checkpoint checked against current business records. Scoped external listing, editing and deletion were verified with readback using an isolated synthetic fixture, which was then removed. Separate-user isolation and CSRF checks passed. Langfuse readback confirmed the submitted message pair and pending/completed outcomes on the extraction trace.

Automated coverage includes durable-job behavior, idle triggers, user isolation, the preserved internal-memory path, real local MCP transport, routing/workflow compatibility and frontend provider handling. The default fifteen-minute idle trigger was checked by automated tests rather than waiting for it in the live walkthrough. Optional procedural/checklist, changed-format and additional paraphrase cases remain learner observations; model responses are not prescribed.
