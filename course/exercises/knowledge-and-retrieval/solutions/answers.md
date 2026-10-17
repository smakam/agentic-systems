# Chapter 9 worked solution and measured result

## UI, database and cleanup

**UI:** [test marketplace](http://127.0.0.1:5179/) from Course Setup; use the role/workspace named in each task. **Database:** disposable practice database `market_test`, separate from main `market` and the fixed evaluation baseline `market_eval`. Test UI changes do not update the main marketplace. Save your questions, results and traces locally.

Core policy and SQL-plus-policy questions use Support with OpenAI Agents SDK in the test UI.

**Developer lab:** reindexing and chunking comparisons run through the supplied CLI against `ch09_rag_lab`, containing only synthetic lab documents. The normal test UI does not automatically query this separate corpus. Its policy changes do not replace the marketplace policies.

**Cleanup:** save outputs and, when no lab runner is active, remove only `ch09_rag_lab` using the supplied command. Read-only UI practice needs no reset. Restore source/configuration changes if you used your own implementation.


[rag_lab.py](rag_lab.py) implements the isolated lab using the actual gateway embedding alias and PostgreSQL pgvector cosine operator. No main/evaluation records, production ingestion or policy files are changed. The database-name guard permits only ch09_rag_lab. Three lab corpora retain source/version/line ranges, hashes and 1536-dimensional vectors. The indexed policy corpus is intentionally replaced sequentially; production retains immutable versions with effective-date filtering.

## Policy refresh

The reference indexes v1, retrieves twice before reindexing, asserts the evidence is unchanged, then indexes v2 and verifies v2 passages and the 48-hour rule. It creates separate model answers before and after. A v2 source existing on disk does not refresh the vector table automatically.

On October 10, the model answered **eligible** with the 24-hour rule under v1, then **not yet eligible** with the 48-hour rule under v2, using identical supplied 30-hour delivery facts. Both answers cited returned evidence and distinguished eligibility from execution. Corpus-local citation IDs repeat across rebuilds; preserve each saved result's version/source metadata alongside its citations. They are not production evidence handles.

## Chunking

The paragraph implementation tracks nonblank paragraphs and one-based source ranges. The overlap implementation makes two-paragraph windows with stride one; the final window may contain one paragraph. Both strategies embed the same synthetic longer policy using the same model and query and compare cosine retrieval at fixed top_k. There is no reranker, semantic chunking, or approximate vector index.

| Strategy | top_k | Complete standard-rule paragraph returned | Exception returned | Returned characters |
|---|---:|---|---|---:|
| Paragraph | 1 | No | Yes | 296 |
| Overlap | 1 | No | Yes | 488 |
| Paragraph | 4 | Yes | Yes | 755 |
| Overlap | 4 | Yes | Yes | 1667 |

All four answers correctly said the Amber Review payout is not yet eligible at 30 hours because the exception requires 72 hours. At top_k=1 the exception itself states “rather than 24,” so the model can recover the standard timing without retrieving the complete standard-rule paragraph. Overlap's top-ranked window paired the exception with the following paragraph, not the preceding rule. Do not present this as an answer-quality improvement or hide the result because it differs from the hypothesis.

For this particular question, paragraph chunks with top_k=1 were the most efficient observed option by retrieved-text volume: they returned 296 characters and still produced the correct answer. The other three settings returned more text without improving the final decision. This is not a measured total-cost or latency win, and it does not establish paragraph/top-one as the best configuration for other questions; use a broader representative question set before selecting a default.

The lesson is to inspect actual retrieved context: overlap changed boundaries and text volume, but increased context cost without improving this final decision. A broader question set is needed before adopting it. Document size alone does not determine whether chunking matters.

## Evidence and limits

[Raw results](results-2026-10-10.json) contain passages, versions, source ranges, cosine scores, and all six generated answers. Validation used real gateway embeddings and six answer calls against a separate local vector database. No synthetic embeddings or lexical fallback were used. These are one-run teaching comparisons, not a general retrieval benchmark. SQL-plus-RAG application traces and the instructor's full demo rehearsal are not claimed by this lab validation.

For cleanup, export results, close the script connection, then drop only ch09_rag_lab following exercise.md. Reference script reruns rebuild its own corpora so the experiments are repeatable.
