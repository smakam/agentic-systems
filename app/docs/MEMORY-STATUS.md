# Memory conclusions and remaining work

Current as of October 3, 2026. **The bounded memory learning lab is complete.** This means the implemented scope and controlled demonstrations are sufficient to teach; it does not mean all 24 catalogue cases have passed or that production readiness is established.

## Short-term memory

Conversation history includes user/assistant messages and complete tool-call/result blocks from up to six prior questions. Each new question captures its own snapshot. This is separate from cross-conversation personal memory.

**Verified:** GPT-5.4 correctly reused prior structured quantities in the same conversation with zero new tool calls, both with long-term memory enabled and disabled. The original evidence references resolve through earlier runs in the same conversation. Prior targeted experiments tested revision/clock freshness boundaries. Sidebar navigation retained the selected conversation, displayed answers and unsent draft.

**Conclusions:** Turning off long-term memory does not turn off ordinary conversation history. Business evidence reuse depends on revision, clock for time-sensitive questions, document version/effective scope for policy, and completeness of the earlier result. Reusing prose alone is not equivalent to reusing structured evidence. Stored history is larger than the bounded history actually sent to the model; a session ID is not an unlimited context window. Prompt instructions guide reuse but do not guarantee model compliance.

**Still pending:** A guided new-conversation missing-reference demonstration (S03); dedicated current-suite historical/freshness UI walkthroughs (S04–S06, although earlier targeted tests exist); switching sidebar pages while a request is running (S08); lesson recording and a controlled history-inclusion comparison. Full reload restoration is a distinct feature, not promised by sidebar retention. Automatic compaction remains deferred.

## Long-term memory

Explicit, user-directed semantic preferences, episodic investigation checkpoints and procedural checklists are stored in PostgreSQL through an application-owned module. Four local stdio MCP tools—search_memories, save_memory, update_memory, delete_memory—access it as of October 3; marketplace business transport remains independent and remote HTTP MCP remains business-only. Records are private to user ID, not shared automatically by operator/support role. Provenance and optimistic versions support inspection and safe editing.

**Verified:** Earlier checks covered save/recall of all three types, update/delete, denied writes, user isolation and version/provenance boundaries. The new eight-scenario GPT-5.4 suite completed 19 questions; six required retrieval checks and ten memory-off question checks passed. Assistant review found all 19 answers factually correct. The old checkpoint was retrieved and distinguished from a newly completed payout. A temporary product override actually retrieved the stored seller preference, followed the current instruction, and left the memory unchanged. A saved instruction to ignore the delivery hold did not override policy. The two-question policy-conflict rerun also passed.

**Conclusions:** A checkpoint remembers prior findings and the next unresolved step; it is not the source of current order status. Preferences can clarify user intent, but current instructions take precedence. Checklists guide investigation and cannot override policy, permissions or current business evidence. Saving requires both an explicit request and per-question write permission. That permission resets after a question; stored memory remains. Deletion removes the saved record, not earlier chat messages/traces.

The user observed explicit “where did I leave my investigation” wording retrieve the checkpoint, while a vague “has anything changed” question did not. This is accepted user-reported behavior, not a guarantee of implicit recall. A change comparison needs a stated/retrieved historical baseline. Prompt v10 encourages relevant checklist/checkpoint searches, but Nano still skipped memory in a separate live diagnostic; successful GPT-5.4 trials do not establish Nano reliability or general automatic retrieval reliability.

**Still pending:** Dedicated manual reconfirmation after override (L09); logout/login persistence demonstration (L14); the vague-change branch of L15; a full manual pass through the 24-case catalogue where needed. Many CRUD/isolation/version cases already have earlier regression coverage; they are not unimplemented. Broader repeated/held-out live tests and a controlled current-suite Nano/GPT-5.4 comparison are optional extensions rather than blockers.

## Citation conclusion

The initial review incorrectly called shortened raw evidence IDs broken links. The existing UI already resolves shortened IDs only when matching recorded evidence exists. All 19 original answers passed checking through the actual UI formatter; one answer was noncanonical in raw format. The rerun used full canonical IDs, and all sources resolved. Seven citation regressions passed, including unknown-source rejection and earlier-question/conversation boundaries. No prompt or application-resolver change was required. Evaluate raw formatting and source resolution separately; source resolution alone does not establish factual support for every claim.

## Repeatable test environment and grading

- Live workspace: http://localhost:5178/ → `market`.
- Resettable test workspace: http://127.0.0.1:5179/ → `market_test`. Use this exact host to avoid cookie collision with live localhost. Both UIs use the existing support-model alias, currently Nano; the runner selects Nano or GPT-5.4 explicitly.
- The [24-case catalogue](../eval/memory-v2/README.md) has S01–S08 for short-term behavior and L01–L16 for long-term behavior. Eight automated scenarios cover six complete catalogue cases plus recall portions of four others; 19 counts agent questions including controls, not catalogue cases.
- Automated retrieval/use fixtures seed memories directly, isolating use from chat-saving quality. The runner resets between scenarios, preserves source/spec hashes, answers/evidence/metrics outside the database, and restores the known seeded baseline afterward. It does not restore arbitrary prior user-modified test data.
- Stop test services before reset/runs and avoid concurrent `market_test` runners. Reset deletes test sessions, so sign in again. Never reset live `market` or the separate `market_eval` benchmark as part of this suite.
- Tool/record checks are deterministic. Text correctness here is assistant-reviewed, not independent human adjudication or a paid LLM judge. One sample is not a general reliability percentage. Compare retrieval, correct use, answer correctness, unauthorized writes and citations separately.

## Evidence and hands-on material

- [Initial CRUD/isolation lab](../results/memory-v4-2026-10-02/REPORT.md) and [walkthrough](../eval/memory-v1/README.md).
- [Application fixes and GPT-5.4 stale/checklist checks](../results/memory-use-gpt54-v2-2026-10-02/REPORT.md).
- [Actual-order implicit checklist diagnostic and sidebar retention](../results/memory-auto-checklist-v10-2026-10-03/REPORT.md).
- [Eight-scenario / 19-question report](../results/memory-repeatable-20261003T093153094486Z/REPORT.md), [per-question review](../results/memory-repeatable-20261003T093153094486Z/review.json), and [source-resolution checks](../results/memory-repeatable-20261003T093153094486Z/citation-checks.json). Estimated uncached model cost $1.02.
- [Two-question policy-conflict citation rerun](../results/memory-repeatable-20261003T094355178246Z/REPORT.md). Estimated uncached model cost $0.31. Estimates exclude embeddings and are not invoices.
- [Prompt/history walkthrough](PROMPT-AND-CATALOG.md) and [memory diagrams / optional Mem0 architecture](../../course/diagrams/MEMORY-ARCHITECTURE.md).

## Optional future enhancements

Automatic extraction/background saving; consolidation/conflict handling and expiry; semantic retrieval for larger memory collections; compaction; deliberate shared procedural scope; optional Mem0 integration/comparison; broader held-out/repeated evaluations; full reload conversation restoration. A memory manager is optional, not a requirement for production. None of these capabilities is claimed implemented or tested by this lab.

## Local MCP transport update — October 3, 2026

[Verified change](../results/memory-local-mcp-2026-10-03/REPORT.md): all agent memory calls use local stdio MCP; existing permission/provenance/isolation/version behavior retained. 81 regressions passed without paid model calls. Main and test backends deployed. Earlier live-answer results above predate this transport change.

## Live regression after local MCP change

[October 3 rerun](../results/memory-repeatable-20261003T112031250654Z/REPORT.md): all 19 GPT-5.4 answers passed assistant review; six required retrievals, ten memory-off controls and all source-resolution checks passed. Estimated uncached model cost $0.99, excluding embeddings. This supersedes the lack of paid rerun stated in the transport report. Fixtures preseed memory; chat-save quality is covered separately from these live-use tests.

## Native platform comparison

[Lyzr Cognis report](../lyzr/cognis-memory-2026-10-03/REPORT.md): Cross Session ON; short-term and bounded cross-session recall/control/override/history tests passed. Autonomous checklist use omitted shipment retrieval, so that investigation check failed; explicit follow-up succeeded. Native provider permission/provenance/CRUD/isolation parity is unverified.


### Memory MCP review and provider-portability architecture — October 3, 2026

Reviewed code and the related “Prepare for Lizer CTO discussion” implementation/regression evidence. Agent memory now uses local stdio MCP; PostgreSQL MemoryStore still enforces ownership, explicit mutation permission, provenance and optimistic version checks. Business MCP and short-term conversation history remain independent; remote HTTP MCP exposes only business/lifecycle tools. [Review](../results/memory-local-mcp-2026-10-03/REVIEW.md), [81-regression migration evidence](../results/memory-local-mcp-2026-10-03/REPORT.md), and [19-question post-migration GPT-5.4 report](../results/memory-repeatable-20261003T112031250654Z/REPORT.md): all expected answer/operation/source checks passed, cost about $0.99. This documentation review reused existing evidence and made no paid calls or database resets.

Updated [memory architecture and provider-extension diagrams](../../course/diagrams/MEMORY-ARCHITECTURE.md) and specification overview. **MCP makes operations accessible across runtimes; an adapter interface makes storage replaceable.** The interface and external adapters are planned; current MCP code directly creates PostgreSQL MemoryStore. Future providers must preserve or explicitly adapt permission/isolation, extraction/save fidelity, provenance, update/delete and freshness behavior. Native Lyzr Cognis is a separate test track, not already wired behind our memory MCP. No remote personal-memory endpoint or multi-provider switching is claimed implemented. Existing manual/held-out memory pending work remains; provider adapters/parity testing are optional enhancements.
