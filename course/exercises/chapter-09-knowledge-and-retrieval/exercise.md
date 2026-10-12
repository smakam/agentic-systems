# Chapter 9 — Knowledge and Retrieval

## Goals and prerequisites

Inspect what retrieval contributes to an answer, update an indexed policy, and compare chunking strategies. Use the course's running local Docker backend, gateway and pgvector PostgreSQL services. Embedding/model calls use your configured gateway and incur normal provider usage.

Use a dedicated **ch09_rag_lab** database and the supplied lab documents. Keep the main marketplace and fixed market_eval database unchanged. The lab contains only synthetic document chunks, not marketplace business records. The reference script refuses another database name and has no lexical fallback. Its isolated table is intentionally simpler than production's immutable versions and effective-date filters.

## Part 1 — repeat the chapter demo

1. In the test marketplace Support workspace, select OpenAI Agents SDK and ask a policy-only question: “What conditions must be met before releasing a seller payout?” Inspect search_documents inputs, passages, policy version, scope, dates, and citation support.
2. Ask “Why is the payout for order-2 held?” Inspect the business evidence as well as the applicable policy. Record which claim comes from SQL and which comes from documents; use the actual current records, not an assumed status.
3. Save both traces or screenshots and write a short source map. A policy passage cannot prove a payout was executed.

### Update a policy and refresh the index

Use [payout-v1.md](fixtures/payout-v1.md) and [payout-v2.md](fixtures/payout-v2.md). These are simulated lab policies; they do not replace the marketplace policy. Version 1 requires 24 hours after delivery; version 2 requires 48 hours.

Use fixed supplied facts: payment captured, delivery 30 hours ago, no open return. Ask whether the seller payout is eligible, requesting the waiting period and citation.

1. Index v1 with paragraph chunks; retrieve passages and save the answer.
2. Prepare v2 on disk but do not index it. Ask again against the v1 corpus. Explain why the indexed evidence remains v1 even though a new document exists on disk.
3. Rebuild the isolated policy corpus from v2 and generate its embeddings. Ask the identical question again. Verify passage version, source, waiting period, citation and answer.
4. Restore v1 if repeating the experiment. In the real application's ingestion path, add a new version and correctly set applicability dates; never mutate an existing immutable version.

Keep before/stale/after passages, two answers, and an explanation locally of why reindexing was necessary. Expected eligibility changes because only the supplied policy changed; the fixed business facts do not change. Do not treat eligibility as executed payment.

## Part 2 — additional challenge: compare overlapping chunks

Use the longer [expanded-policy.md](fixtures/expanded-policy.md). The standard payout rule and the lab-only Amber Review exception are adjacent paragraphs. The normal waiting period is 24 hours. Amber Review is a fictional review status, not a product name or a field queried from marketplace records. The question supplies that status as a simulated fact. When the flag is present, the exception requires 72 hours after delivery instead of 24 hours. The fixture intentionally includes unrelated material; it is not an operational policy.

1. Implement a paragraph chunker that retains source line ranges.
2. Implement two-paragraph windows with stride one, preserving source ranges. Compare your implementation with the reference only after trying it.
3. Reindex each strategy into a separate corpus using the same embedding model, cosine ranking and supplied facts. Ask: “Payment captured, confirmed delivery 30 hours ago, no open return, Amber Review flag present. Is seller payout eligible? Explain the standard rule and exception with citations.”
4. Compare paragraph versus overlap at top_k=1, then at top_k=4. Hold top_k fixed within each comparison.
5. Inspect chunk boundaries, retrieved passages, whether the rule and exception are present, returned text length, citations, and the answer. Explain the storage/context cost of overlap. A larger document alone does not guarantee an effect; boundaries and retrieval settings matter.

Keep your chunking code, source ranges, comparison table and recommendation locally to compare with the solution. There is no submission destination. Correct answers under both strategies are a valid result. Do not claim overlap always improves correctness or use similarity scores as confidence.

## Running the reference after attempting the exercises

From the repository root, create the disposable local lab database once:

```sh
docker compose -f app/compose.yaml exec -T postgres psql -U postgres -d postgres -c 'CREATE DATABASE ch09_rag_lab'
docker cp course/exercises/chapter-09-knowledge-and-retrieval marketplace-lab-backend-1:/tmp/ch9-lab
docker compose -f app/compose.yaml exec -T backend env CH9_DATABASE_URL=postgresql://postgres:local-bootstrap-only@postgres:5432/ch09_rag_lab python /tmp/ch9-lab/solutions/rag_lab.py --answers --output /tmp/ch9-lab/results.json
docker cp marketplace-lab-backend-1:/tmp/ch9-lab/results.json /tmp/ch9-results.json
```

If the lab database already exists, skip CREATE DATABASE. The local bootstrap credential is only for this supplied Docker lab. Never use cloud or business credentials for this task. If the gateway key cannot access the embedding/support-model aliases, fix lab access before continuing; do not substitute a lexical result and call it vector retrieval.

The script rebuilds only its own lab corpora. It compares two sequential indexed versions, not automatic historical policy selection. Effective-date filtering is inspected in the application demo; an effective-date extension is optional, not required here.

After saving outputs and completing the lab, remove the disposable database:

```sh
docker compose -f app/compose.yaml exec -T postgres psql -U postgres -d postgres -c 'DROP DATABASE ch09_rag_lab'
```

## Solution and status

See [worked solution](solutions/README.md) and [measured results](solutions/results-2026-10-10.json). Reference execution was validated October 10, 2026. Instructor's full application-demo rehearsal and learner walkthrough remain separate checks.
