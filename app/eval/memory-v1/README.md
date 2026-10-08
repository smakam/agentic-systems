# Explicit long-term memory lab

The support agent uses four local stdio MCP tools (updated October 3): `search_memories`, `save_memory`, `update_memory`, `delete_memory`. Business tools retain their existing MCP transport. Explicit personal-memory management questions expose only memory tools; normal business investigations keep both. This is a bounded application tool-scope rule, not another agent or a general-purpose intent classifier. Records live in `agent_memories` in the same PostgreSQL database, outside analytics views and business revision changes.

## Try it

1. Sign in as support or operator and open Support workspace.
2. Keep **Use long-term memory** enabled. Check **Allow memory changes for this question**.
3. Ask: “Remember this semantic preference: When I say Cedar, I mean seller Cedar & Co.”
4. Open **Saved memories** and inspect the record and source metadata.
5. Start a **New conversation** and ask: “What do I mean when I say Cedar?” No write permission is needed to search.
6. Compare in another new conversation with long-term memory off. Ordinary session history is unchanged; memory-off is not an erase-history switch.
7. To update through chat, enable changes and explicitly ask to update; to forget, explicitly ask to forget. Alternatively use the Saved memories Edit/Forget buttons. Version checks reject stale edits. The write permission resets after each question.

Episodic example: “Save an episodic checkpoint: I investigated order-1; next step is to inspect payout attempt history. This is historical.” In a new conversation ask to resume; the agent must query current facts before claiming current status.

Procedural example: “Remember this procedural checklist: check delivery hold, active returns, then payout failure events; use current policy and records.” In a new conversation ask which checklist was saved, then apply it to an investigation. Guidance never replaces governed policy.

All initial memories are private to the authenticated individual user, including procedural guidance. Shared memory is not implemented. No automatic extraction, background saving, compaction, embeddings or Mem0 dependency is added. Retrieval is bounded lexical keyword search (up to ten matches); larger memory libraries may need better retrieval.

## Boundaries and verification

The backend requires an owned operator/support conversation and separate write permission. Current-request operation matching conservatively restricts mutations to save, update or delete; ambiguous wording can require rephrasing. An update cannot create a conflicting replacement. The agent is additionally instructed to save only on an explicit current-user request. The checkbox authorizes memory changes only; SQL/RAG tools remain read-only.

Stored source conversation/run, creation/update times, version and snapshot metadata support inspection. A memory's snapshot is provenance, not an assertion of present validity. Source runs must belong to the same user. Deletion removes the long-term record, not original chat messages, traces or exported test artifacts. Test forgetting in a fresh conversation.

Database tests run through `scripts/test.sh`, only on disposable `market_test`. Live checks use `scripts/memory-smoke.py` in the same isolated database with marketplace tools through MCP and memory tools through a separate local stdio MCP server. The script resets test memories, preserves each run's answer/tool attempts/operation log/cost, and requires a fresh results path. Do not run it against `market` or concurrently with a resetting test suite. No paid LLM judge is used.

Memory operations are logged in run metrics as `memory_tool_attempts`, `memory_operations`, `memory_tool_calls` and `memory_write_allowed`. Total displayed tool calls include business and memory calls. SDK instrumentation provides tracing; no Langfuse dataset upload is claimed.


## Expanded repeatable suite

See [memory-v2](../memory-v2/README.md) for the 24-case catalogue, eight automated scenarios, reset commands, and separate live/test UI addresses.


Current conclusions and pending short-/long-term work: [memory status — October 3, 2026](../../docs/MEMORY-STATUS.md). The bounded lab is complete; full catalogue coverage and production readiness are not claimed.
