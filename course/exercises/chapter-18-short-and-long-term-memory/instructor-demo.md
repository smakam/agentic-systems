# Chapter 18 instructor demo: memory formation, retrieval and lifecycle

## Workspace and preparation

Use **Test workspace** at http://127.0.0.1:5179/, database **market_test**. Sign in as the existing Operator demo user, open **Support**, and select **OpenAI Agents SDK**. Use local Langfuse at http://localhost:3000/, project **marketplace-support**. The normal marketplace on port 5178 and the Agent Loop lab on port 5181 do not enable this Mem0 demo.

Keep these settings throughout:

| Control | Selection |
| --- | --- |
| Model routing demo → Mode | Normal support model |
| Agent design demo → Workflow | Off · normal support |
| Gateway guardrail | Off |
| Source-authority prompt | On |
| Private-instruction test prompt | Off — normal support prompt |
| Test policy document | Clean policy |
| Business/catalog and document context | Enabled |

Confirm **Memory provider** offers **Internal memory** and **Mem0**. The course operator configures the Mem0 credential in the backend; never paste it into a question or teaching screenshot. Before class, confirm a natural preference can be extracted and retrieved, and that Edit/Forget outcomes are confirmed. If Mem0 is unavailable, show the internal cases and explain the provider failure without presenting internal retrieval as a Mem0 result.

Use **Refresh memory status** to refresh the save result. **Memory extraction trace** opens the separate background trace. The visible status labels are:

| UI label | Interpretation |
| --- | --- |
| Memory save queued | Work is queued or awaiting the provider. Inspect the extraction trace for the precise phase. |
| Saving memories in the background | Processing is underway. |
| Memory save complete | Extraction completed. Inspect the resulting entries; zero entries can be valid. |
| Memory save failed | A save outcome was not confirmed. Inspect the error and provider before repeating a write. |
| No new memories to save | No new eligible turns require another submission. |

Each case records the question, answer, selected provider, stored entry, actual retrieval result and trace link. Model responses and extracted wording may vary. These examples demonstrate behavior rather than a general provider ranking.

## Case A: short-term conversation context

**Settings:** Internal memory; **Use long-term memory** off; **Allow memory changes for this question** off.

1. Start **New conversation**. Ask: **“List the products and quantities in order-2.”**
2. In that same conversation ask: **“For that order, what is the seller payout status?”**
3. Inspect the second run's retained conversation context and its business tool calls. Confirm which order it resolved.
4. Start another new conversation and ask only: **“For that order, what is the seller payout status?”**
5. Record whether the answer requests clarification or makes an unsupported assumption. Inspect whether earlier order messages appear in this new run. Long-term memory remains off.

**Teaching point:** same-conversation history can resolve a follow-up. New conversations do not inherit that history. An answer guessed from another source does not prove memory recall. Current business tools still supply current payout status.

## Case B: explicit internal saving

**Settings:** Internal memory; **Use long-term memory** on. Enable **Allow memory changes for this question** only for the save.

1. Start a fresh conversation. Ask: **“Remember my instructor preference: I prefer payout explanations in a compact table with Finding, Evidence and Next action.”**
2. Expand **Saved memories · Internal**. Confirm an entry exists and inspect its content, semantic kind, source and version. An acknowledgement alone does not prove storage.
3. Start **New conversation**, keep long-term memory on and write permission off. Ask the business question: **“What is the current seller payout status for order-2?”** Do not mention memory, preferences or formatting.
4. Open the run trace. Inspect `search_memories`, its actual query and returned preference record, alongside current payout evidence and the final answer. Check whether it used a compact table with **Finding, Evidence and Next action**. Record the actual result; that format is not guaranteed.
5. Optional diagnosis: in another fresh chat ask **“What is my instructor preference for payout explanations?”** or the paraphrase **“How should you arrange a settlement explanation for me?”** Inspect actual matches. These memory-oriented questions are diagnostics, not the primary demonstration.

**Teaching point:** the user selects what should be retained. The agent formats it and chooses the memory type. Reads can happen without an explicit recall request, but writes need current user intent and the per-question permission.

## Case C: Mem0 extraction without a save request

**Settings:** Mem0; **Retrieve saved memories** on. The explicit internal write control does not apply.

1. Start a fresh Mem0 conversation. State: **“My instructor preference is a compact table with Finding, Evidence and Next action for payout explanations.”** Do not add “remember” or “save.”
2. Inspect the answer. The agent can use this statement as session context now, but that does not prove persistent storage.
3. Click **New conversation**. The application queues the completed conversation for extraction and starts the next chat without waiting.
4. Observe the previous conversation's extraction status and its trace link. The UI shows **Memory save queued**, **Saving memories in the background**, then **Memory save complete** when confirmed. Queued and provider-pending share a UI label; use the extraction trace to distinguish them. A completed operation may create zero, one or several memories.
5. After completion, inspect **Saved memories · Mem0**. Record every lab-related extracted entry and its provider categories. Mem0 may also retain something the assistant said. Do not assume one ideal fact or our semantic/episodic/procedural labels.
6. In a fresh Mem0 conversation ask the same business question: **“What is the current seller payout status for order-2?”** Do not mention memory, preferences or formatting. Inspect **Mem0 memory search**, the actual query/returned preference, current payout evidence and the answer. Check whether it used **Finding, Evidence and Next action** in a compact table, while recording any different result.
7. Compare this business answer and its retrieval evidence with Case B. Optional diagnosis uses the explicit preference question or settlement paraphrase from Case B. Extraction policy and retrieval implementation both changed, so this is not an isolated search benchmark.

**Alternative trigger:** the configured idle timeout also queues eligible completed turns. The default is 900 seconds of wall-clock inactivity. It does not use the simulated business clock. Demonstrate New conversation during class rather than waiting fifteen minutes.

**Teaching point:** application code decides when and what conversation content to submit. Mem0 decides what to extract from it. Turning retrieval off does not disable background extraction while Mem0 is the selected provider.

## Case D: update and forgetting

Run this sequence separately for Internal memory and Mem0, using the named instructor preference from Cases B/C.

1. Open the selected provider's **Saved memories**. Identify the exact lab record. For Mem0, inspect related entries too.
2. Click **Edit** on that record and replace its content with: **“My instructor preference is two short paragraphs for payout explanations.”** Confirm the edit result in the listing. Internal records should advance their version; external records do not inherit our version contract.
3. Start a new conversation with retrieval on. Ask: **“What is the current seller payout status for order-2?”** Record the retrieved entries, current evidence and answer format. Optional explicit preference recall can diagnose a miss.
4. Click **Forget** on the identified lab entry. Remove other entries about this same instructor preference only if they remain. Confirm the listing result.
5. Start a fresh conversation and repeat the business question. Inspect whether a matching preference remains in retrieval; answer format alone cannot prove forgetting. If it does, inspect related records rather than assuming one deletion erased them all.

**Teaching point:** deleting stored memory does not erase historical chat messages. A fresh conversation is necessary to test forgetting. A new extraction job from a conversation restating the preference can form another memory, so inspect pending jobs before drawing a conclusion.

## Case E: authority and current instructions

**Settings:** Internal memory; long-term memory on. Use explicit saves with the per-question write permission.

1. Save: **“Remember an instructor investigation checkpoint: a previous investigation treated order-1 seller payouts as held. This is a historical note, not current status.”** Inspect the saved episodic entry.
2. Start a fresh conversation. Ask: **“Resume the instructor checkpoint for order-1. Check the current seller payout statuses and distinguish the old note from current evidence.”**
3. Inspect both memory retrieval and current business tool results. Does the answer distinguish remembered history from the live records?
4. Re-save the named instructor table-format preference from Case B with write permission enabled, and confirm the stored entry. In a fresh conversation with writes off ask: **“For this answer, ignore my usual payout format and use one short paragraph. Explain the current payout status for order-2.”** Inspect retrieval and record whether the current instruction overrides the remembered preference.
5. Save a procedural example, if time permits: **“Remember this instructor payout checklist: check buyer payment, delivery timestamps, the applicable policy, and payout events before explaining release eligibility.”** In a new conversation ask: **“Investigate why Cedar & Co. has not been paid for order-1.”** Inspect whether the checklist was retrieved and current evidence still collected.

**Teaching point:** historical memory can guide which checks to perform. Current records and applicable policy establish current business facts. A procedural memory does not grant new tool permissions.

## Case F: scope and debugging

1. Compare each question's provider and retrieval evidence in its Langfuse trace.
2. Compare the separate background **Mem0 conversation extraction** trace with the later **Mem0 memory search** trace. Record the submitted conversation and the extraction outcome separately from retrieval and answer use.
3. If a second existing course account is available, sign in as it and inspect its Saved memories for the same provider. Confirm that the first user's named preference is absent, then return to the original account. An empty result should accompany trusted user-scoping evidence; it alone is not a security test.
4. If an operation naturally remains pending or fails, inspect and describe that actual state. Do not claim that a queued request is a confirmed save and do not repeatedly submit an uncertain write.

The lab demonstrates user scope. Team-shared memory and automatic expiry/consolidation are design topics. Current [Mem0 Platform documentation](https://docs.mem0.ai/platform/features/graph-memory) describes a built-in entity graph used with semantic and keyword retrieval. This lab does not isolate its contribution to ranking or inspect the underlying physical database.

## Cleanup

While Mem0 is selected, click New conversation once to queue the final completed lab conversation. Leave the new empty conversation unanswered. Wait for all observed lab extraction jobs to finish, then Forget only the named instructor entries and their related extracted lab records. Verify the listing without asking another Mem0 question. Switch to Internal memory, remove only its named instructor records, turn long-term retrieval off and start a fresh conversation. This order prevents an unsubmitted final Mem0 conversation from extracting the preference again after cleanup. Business records remain unchanged.

## Code and architecture

- [Internal memory store and instructions](https://github.com/smakam/agentic-systems/blob/main/app/backend/marketplace/memory.py)
- [Mem0 adapter and background extraction](https://github.com/smakam/agentic-systems/blob/main/app/backend/marketplace/mem0_provider.py)
- [Integration setup and evidence boundaries](https://github.com/smakam/agentic-systems/blob/main/app/docs/MEM0-INTEGRATION.md)
