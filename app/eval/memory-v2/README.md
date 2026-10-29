# Repeatable short-term and long-term memory lab

This versioned suite uses disposable **market_test**, never the interactive **market** database or the historical **market_eval** benchmark database. Each independent scenario starts from seeded business revision 1, demo clock September 27, 2026 at 12:00 UTC, and no saved memories or conversations. Order-1 has Canvas Weekender (2, Cedar & Co.) and Desk Lamp (2, Northstar Goods); payout-1 failed after a provider timeout. Order-2 has Ceramic Mug Set (2, Everyday Studio), shipment-3 pending and payout-3 held. These are fixture facts, not assertions about the live UI.

## Choose the workspace

- Live: http://localhost:5178/ — existing `market` data.
- Test: http://127.0.0.1:5179/ — `market_test`, visibly labelled MEMORY TEST WORKSPACE. Use **127.0.0.1**, rather than localhost, so browser login cookies do not collide with the live localhost workspace. Sign in with the existing demo users/password. Both UIs use the existing `support-model` gateway alias (currently Nano); the automated runner separately selects Nano or GPT-5.4.

From the app directory, prepare a fixture then start only the optional test services:

```sh
sh scripts/memory-repeatable.sh --prepare checkpoint
docker compose -f compose.yaml -f compose.memory.yaml up -d --no-deps --build memory-backend memory-frontend
```

The postgres and gateway services must already be running. Test requests use the existing gateway and incur normal inference costs. This adds an isolated application instance, not another gateway. Memory is private per user even in the test workspace. Fixture memories are saved for **support**, so sign in as support for prepared recall scenarios.

Before resetting/preparing another scenario, let investigations finish, stop the test backend, and close or reload the test page afterward. Resets remove sessions/conversations; sign in again. Never run this suite alongside `scripts/test.sh` or another runner using `market_test`.

```sh
docker compose -f compose.yaml -f compose.memory.yaml stop memory-frontend memory-backend
sh scripts/memory-repeatable.sh --reset
```

## Automated modes

```sh
# No model calls: prepare every scenario twice, compare fixtures, restore baseline.
sh scripts/memory-repeatable.sh
# Run a selected scenario and its memory-off control, then restore baseline.
sh scripts/memory-repeatable.sh --live --model 54 --scenario checkpoint
# Optional full eight-scenario run (19 questions); normal provider charges apply.
sh scripts/memory-repeatable.sh --live --model 54
# Same suite with Nano; failures are recorded rather than assumed fixed.
sh scripts/memory-repeatable.sh --live --model nano
```

Each invocation creates a fresh `results/memory-repeatable-<UTC timestamp>/` containing the case specification and manifest. Live mode also saves full answers, evidence, metrics, conversation IDs and deterministic operation checks in results.json. No paid LLM judge is used. Review text correctness against each expected answer; a successful tool call is not proof of a correct answer. The runner seeds memories directly to isolate retrieval/use from model-dependent saving. Chat saving is tested separately below and in the existing CRUD suite.

Live runs restore the seeded baseline in `finally`, including after a normal Python/model error. A killed container cannot execute cleanup: run `--reset` afterward. This restores the **known seeded baseline**, not an arbitrary prior test-session snapshot. Generated IDs and password hashes can differ; semantic fixture facts must match. Both read/write URLs are checked before any reset. Source/spec hashes and prompt version are recorded. Artifacts outside the database survive reset.

## Detailed test catalogue

**Settings:** R = Use long-term memory; W = Allow memory changes. W resets after each question. Unless stated, answer questions use W off. A new conversation is mandatory for cross-conversation tests; sidebar navigation alone is not a new conversation.

| ID | Test and exact steps | Expected / trace inspection | Coverage |
|---|---|---|---|
| S01 | Prepare `short-history`. Ask “What products, quantities and sellers are in order-1?” then “What is the total quantity of those items?” in the same conversation. | Two products, 2 each; total 4. Grounded evidence and resolvable citations. | Live runner |
| S02 | Prepare `short-history-memory-off`. R off; repeat S01 in one conversation. | Same history continuity; no memory operations. | Live runner |
| S03 | After S01, new conversation: “Total the quantities you just showed me.” | Clarify missing reference; do not treat another conversation as current history. | Manual |
| S04 | After S01, same conversation: “Total the quantities you showed me earlier.” | May reuse complete prior records with original evidence references. Inspect reference resolution, not merely total. | Manual |
| S05 | Ask order-2 payout status; as operator dispatch/deliver shipment-3, then ask “What is its status now?” in the original conversation. | Refresh current records because revision changed; delivered, held within 24 hours. | Manual |
| S06 | Deliver order-2; ask payout eligibility, advance demo clock 24 hours as operator, ask again. | Clock/revision change triggers fresh time-dependent reasoning; eligible if no other blocker. Held row alone does not imply ineligible. | Manual |
| S07 | Type a draft in Support, visit settlement and return. Repeat with a completed answer. | Draft, selected conversation and answers survive navigation; no unnecessary model call. | Manual, previously verified |
| S08 | Start an investigation, switch sidebar page, return while it is running. | Pending request/result remains associated with the same conversation. | Manual, not yet live-verified |
| L01 | Clean baseline; R/W on: “Remember this semantic preference: when I say Cedar, I mean seller Cedar & Co.” New conversation, R on/W off: “What do I mean by Cedar?” | Faithful semantic save and recall; `save_memory`, then `search_memories`. | Existing CRUD + manual |
| L02 | Prepare `semantic-recall`; ask its question, then memory-off control in a fresh conversation. | Recall only when enabled; no invented preference when off. | Live runner |
| L03 | R/W on: “Save an episodic checkpoint: I investigated order-1; next step is payout attempt history. This is historical.” New conversation: “Where did I leave my investigation for order-1?” | Faithful checkpoint/next-step recall, no claim of current status. | Existing CRUD + manual |
| L04 | Prepare `checkpoint`; ask its question. Fixture saved failure at revision 1, then completed payout through an operator retry at revision 2. | Old failure remembered; current completion verified. Business evidence supersedes memory. | Live runner |
| L05 | R/W on: “Remember my payout checklist: check delivery and the 24-hour hold, active returns, payout attempt history and applicable policy.” New conversation: “What payout checklist did I save?” | Faithful procedural save/recall. | Existing CRUD + manual |
| L06 | Prepare `procedural-recall`; recall checklist, then investigate payout-1 without explicitly saying “use checklist.” | Inspect whether memory was actually retrieved; explain provider timeout, not unelapsed hold. Automatic retrieval is model-dependent. | Recall in runner; implicit application manual |
| L07 | Prepare `policy-conflict`; use the provided investigation prompt. | Saved “ignore hold” instruction rejected in favour of 24-hour policy; current delivered time checked. No payout mutation. | Live runner |
| L08 | Prepare `preference-override`; first recall Cedar, then ask the override question **in that same conversation**. | First search must retrieve saved preference; second answer Desk Lamp, 2, Northstar Goods; saved preference unchanged. | Live runner |
| L09 | After L08, new conversation: “What do I mean by Cedar?” | Still seller Cedar & Co.; temporary override did not persist. | Manual |
| L10 | R/W on: “Update my saved Cedar preference: Cedar now means the Desk Lamp product.” New conversation: “What do I mean by Cedar?” | Same memory updated/version advanced; no conflicting new copy. | Existing CRUD + manual |
| L11 | R/W on: “Forget my saved Cedar preference.” New conversation: “What do I mean by Cedar according to saved memory?” | No matching saved record. Old chat may still contain the earlier preference; deletion does not erase transcripts. | Existing CRUD + manual |
| L12 | R on/W off: “Remember that Cedar means Desk Lamp.” | No stored change; explain write permission requirement. | Existing CRUD + manual |
| L13 | Save Cedar as support. Sign out, sign in as operator, new conversation: “What saved preference do I have about Cedar?” | Operator cannot retrieve/edit support's record. | Existing isolation checks + manual |
| L14 | After a save, sign out/in as support and open a new conversation; recall. | Long-term record persists across login; this does not promise automatic conversation restoration. | Manual |
| L15 | Prepare `episodic-recall`; ask “Has anything changed for order-1?” without a stated baseline. | May check current records; cannot assert a comparison without historical baseline. Explicit resume must retrieve checkpoint. | Explicit recall in runner; ambiguity manual |
| L16 | Open two editors on one saved record; save one edit, submit stale edit from the other. | Version conflict; stale edit cannot overwrite. | Existing deterministic regression |

## Automated scenario-to-case mapping

S means **short-term**; L means **long-term**. A catalogue case describes a behavior; a scenario contains fixture setup plus questions; a question is one agent request. Fixture memory is seeded directly, so these automated scenarios do not test the chat save step.

| Automated scenario | Catalogue coverage | Questions including control |
|---|---|---:|
| `checkpoint` | L04 | 2 |
| `policy-conflict` | L07 | 2 |
| `preference-override` | L08 | 3 |
| `short-history` | S01 | 3 |
| `semantic-recall` | L02 | 2 |
| `episodic-recall` | Recall portion of L03; explicit recall portion of L15 | 2 |
| `procedural-recall` | Recall portion of L05/L06; not implicit application | 2 |
| `short-history-memory-off` | S02 | 3 |
| **Total** | **6 fully automated catalogue cases, plus recall portions of 4 others** | **19** |

## What counts as a pass

Record memory selection, current evidence acquisition, final answer correctness, unintended writes, citation resolution, model, prompt version, tokens/cost and latency separately. For policy conflict, passing retrieval while following the bad checklist is an answer failure. For an implicit checkpoint question, skipping memory is distinct from producing a wrong business answer. Required explicit retrieval failures should be flagged, not hidden by a plausible answer.

The full catalogue is 24 cases; the live runner currently automates eight scenarios/19 questions, including controls. Existing database regressions cover CRUD/permissions/provenance/version boundaries. Navigation, sign-in persistence and selected history-change sequences remain manual UI cases. These modes complement each other; the catalogue is not a claim that all 24 have passed.

The test backend explicitly permits login Origin `http://127.0.0.1:5179`. Login/session/market access through that origin was verified October 3, 2026; unrelated origins remain rejected.

## Latest live verification

October 3 GPT-5.4 run (historical instructor evidence; retained separately): 19 questions completed; all memory operation checks passed. Assistant-reviewed answers were factually correct, with one noncanonical citation format; subsequent checking with the actual UI resolver confirmed all source links resolve. This does not mark the full 24-case catalogue complete.

After any live run, check source resolution with the actual UI formatter:

```sh
node scripts/check-memory-citations.mjs results/<run-directory>
```

This writes citation-checks.json and exits nonzero for unavailable sources. Raw shortened formatting is recorded separately; it is not automatically a broken link. Only evidence from the same conversation/current or earlier answers can resolve.


Current conclusions and pending short-/long-term work: [memory status — October 3, 2026](../../docs/MEMORY-STATUS.md). The bounded lab is complete; full catalogue coverage and production readiness are not claimed.


### Memory MCP review and provider-portability architecture — October 3, 2026

Reviewed code and the related “Prepare for Lizer CTO discussion” implementation/regression evidence. Agent memory now uses local stdio MCP; PostgreSQL MemoryStore still enforces ownership, explicit mutation permission, provenance and optimistic version checks. Business MCP and short-term conversation history remain independent; remote HTTP MCP exposes only business/lifecycle tools. Review (historical instructor evidence; retained separately), 81-regression migration evidence (historical instructor evidence; retained separately), and 19-question post-migration GPT-5.4 report (historical instructor evidence; retained separately): all expected answer/operation/source checks passed, cost about $0.99. This documentation review reused existing evidence and made no paid calls or database resets.

Updated [memory architecture and provider-extension diagrams](../../../course/diagrams/MEMORY-ARCHITECTURE.md) and specification overview. **MCP makes operations accessible across runtimes; an adapter interface makes storage replaceable.** The interface and external adapters are planned; current MCP code directly creates PostgreSQL MemoryStore. Future providers must preserve or explicitly adapt permission/isolation, extraction/save fidelity, provenance, update/delete and freshness behavior. Native Lyzr Cognis is a separate test track, not already wired behind our memory MCP. No remote personal-memory endpoint or multi-provider switching is claimed implemented. Existing manual/held-out memory pending work remains; provider adapters/parity testing are optional enhancements.
