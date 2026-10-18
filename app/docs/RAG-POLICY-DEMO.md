# Test workspace RAG experiments

The Test Support UI exposes **RAG → Open RAG experiments**. The dialog contains policy-version and chunking experiments; it does not redirect ordinary Support chat or modify marketplace `document_chunks` and business tables. Each request is authenticated through the existing session/CSRF checks. Only Support and Operator can use the demo, and the server rejects it outside `market_test`.

## Data and requests

`rag_policy_demo_state` stores selected source/strategy separately from the indexed source/strategy. `rag_policy_demo_chunks` holds the synthetic text, source-line ranges and pgvector embeddings. Rows are scoped to the authenticated owner and experiment so simultaneous learners cannot replace each other’s demo index. This is demo isolation, not enterprise document access-control trimming. A single-owner installation could instead share one demo corpus, but it is not necessary to change the marketplace retrieval path.

Selecting a source or strategy changes only the selection. Indexing first obtains embeddings, then replaces the demo chunks and indexed state in one database transaction. Failure preserves the previous index. Restore reselects/reindexes V1 or the paragraph baseline. Each question embeds the fixed scenario plus question, runs exact cosine retrieval against that experiment’s indexed chunks, and generates an answer using only returned passages and synthetic facts. No conversation history or long-term memory is included. Queries use the configured `embedding` and `support-model-test` aliases.

The policy-version question uses captured payment, confirmed delivery 30 hours ago and no return. Indexed V1 requires 24 hours; indexed V2 requires 48. Selecting V2 without indexing keeps V1 evidence. The chunking fixture separates a 24-hour base wait and cumulative 48-hour Amber Review extension across adjacent blank-line paragraphs. Paragraph versus two-paragraph overlap and top K 1/4 can therefore produce different evidence coverage. More context is not universally better.

## Validation on October 18, 2026

- Twelve focused tests cover actual paragraph/window boundaries, invalid combinations, non-Test rejection, role checks and preserving an existing index after embedding failure. Three existing model-directed-history checks and all twenty-three frontend checks also pass.
- The live Test endpoints completed V1 → selected V2 with stale V1 → indexed V2, with the expected eligibility change, then restored V1.
- The final fixed chunking question returned only the standard rule at paragraph/top-one, and both required rules at paragraph/top-four and overlap/top-one/top-four. The three complete-evidence answers calculated 72 hours and rejected eligibility at 30 hours. The incomplete run acknowledged the missing hold/total. See the retained UI endpoint [results](../../course/exercises/knowledge-and-retrieval/solutions/ui-results-2026-10-18.json).
- Browser checks verified the stale notice, result/index labels, chunking and top-K controls, an overlap/top-one answer and its source lines. The final interface opens in a wide native dialog for recording readability; keyboard focus is contained by the browser dialog.
- Read-only before/after checksums match for marketplace state, sellers, products, listings, orders/items, payments, shipments, allocations, payouts, returns, refunds, events and marketplace document chunks. Main and Test health checks pass. The main application and cloud deployment were not restarted.
- The twelve-slide deck passed package, geometry, font and reimport checks; modified slides were visually reviewed. HTML contains all twelve exact rendered images, and browser navigation confirmed the inserted mechanics slide and final slide.

The earlier CLI lab and dated result file remain historical evidence, using `expanded-policy-legacy.md`. They are not learner prerequisites or evidence of the revised UI fixture. The current exercise and answers use the browser only.
