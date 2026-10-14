# Chapter 18 reference answers

These are reference explanations, not a transcript learners must reproduce. Judge the recorded settings, storage, retrieval and use evidence. Neither an acknowledgement nor a plausible answer alone proves long-term memory.

## A: conversation history

The same-chat follow-up can resolve “those items” using the earlier order question and answer. The fresh chat lacks those prior messages. It should seek clarification when it cannot identify the order. An unsupported guess is a model behavior to document. Both runs have long-term memory off, so this comparison demonstrates short-term conversation context.

## B: formation and retrieval

Internal saving requires the explicit current request and the per-question write permission. The agent chooses semantic for the preference and supplies the content; the backend stores a user-owned record with kind, source and version. The trace should show the successful save operation and the listing should contain the record. Recall requires an actual search result, not just a matching answer.

Mem0 saving differs in two decisions. The application starts extraction when the conversation ends or reaches the configured idle timeout. Mem0 selects what to retain from submitted user/assistant messages. The learner did not request a save. A provider-pending operation is not yet a completed save. The UI groups it with queued work as “Memory save queued.” “Memory save complete” confirms completion; the extraction trace distinguishes the underlying phases. Completion may yield zero or several entries, including an assistant statement; record the actual text and provider categories. Do not assign our internal three labels to every Mem0 record.

The paraphrase compares observed retrieval. Internal search uses literal keyword substrings; the agent may nevertheless choose overlapping words. Mem0 uses the provider retrieval service. A successful semantic match in this case is evidence for this query and namespace, not a general accuracy ranking. Formation and retrieval both changed, so the complete experiment does not isolate the search algorithm.

## C: edit, instruction precedence and forgetting

Edit changes the identified record. Internal versions advance and stale-version writes are rejected. Mem0 does not acquire that same version contract merely because the UI uses the same Edit label. Confirm the operation and listing before testing fresh-chat recall.

A current instruction to use a numbered list should override the usual remembered paragraph format. The policy answer still needs applicable policy evidence. The preference governs presentation, not the truth of refund eligibility.

Forget removes the selected stored entry. Related duplicates may remain. The old conversation can still contain the preference, and a later completed conversation that restates it may extract it again. Wait for pending extraction, inspect related records and test in a new conversation. If no matching saved memory exists, the agent should say so rather than invent a remembered preference. The trace should support the conclusion.

## D: types and authority

The checkpoint is episodic because it refers to a previous investigation. The checklist is procedural because it supplies a reusable method. The formatting preference is semantic. These categories describe purpose rather than storage topology: the internal implementation stores them in one table with a kind field.

A valid resumed investigation uses the historical checkpoint to orient the work, then obtains current payout records. A valid checklist-assisted answer applies relevant checks while using current policy and records. Neither a remembered status nor a checklist overrides current evidence, source-authority instructions or tool permissions. Report missing evidence explicitly; don't score invented details as successful memory use.

## Trace and scope interpretation

The question trace shows the selected provider, actual search query/results and how the agent used them. Mem0 background extraction has a separate observation and trace link. Read submitted content, status and extracted IDs/content separately from later retrieval. A correct answer with no retrieved record may be supported by session history or another source.

An optional second-user test should show a different trusted scope and absence of the first user's named records. An empty result alone is not a comprehensive isolation proof. This lab implements personal user scope; it does not demonstrate shared team memory.

## Acceptable failures and limits

A retrieval miss, no useful extracted fact, delay or provider error can be a valid observation if documented honestly. Do not substitute the internal provider silently. Do not claim provider-internal token costs or latency breakdowns from local elapsed time. Automatic consolidation, expiration and learned procedures remain conceptual extensions. Current [Mem0 Platform documentation](https://docs.mem0.ai/platform/features/graph-memory) describes its native entity graph alongside semantic/keyword retrieval; this lab does not separately measure the graph contribution. PostgreSQL can support other indexes and relational structures, while our internal baseline implements keyword search.

The exercise is complete when the learner documents each mechanism, separates observed evidence from interpretation, and removes only their lab records after the final completed Mem0 conversation is queued and pending jobs finish. An empty new chat prevents a further completed conversation from recreating the deleted entries during cleanup.
