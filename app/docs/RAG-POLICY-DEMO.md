# Test workspace RAG experiments

Select **Workspace options → RAG → RAG experiment** and ask in the main Support composer. Off uses the normal marketplace; either experiment uses isolated synthetic documents and fixed facts. No dialog, terminal commands or file changes are needed. A new conversation is recommended for every comparison; neither settings changes nor Reset to defaults creates one automatically.

## Preparation and costs

Marketplace documents prepare automatically at backend startup, on readiness checks and before normal SDK questions. No Index documents button is exposed. The UI shows Preparing, Ready, or a failure with Retry preparation. Existing compatible embeddings are adopted on upgrade without new provider calls. An unchanged document index does no embedding work.

`document_embedding_cache` persists vectors keyed by exact text, gateway endpoint and embedding-model revision. New chunks alone are embedded; switching back to earlier policy text reuses vectors. Duplicate text in a batch is embedded once. Cache writes are transactional and a database advisory lock prevents duplicate concurrent fills; competing requests retry instead of charging twice. Configuration changes can rebuild cheap chunk metadata while reusing vectors. Top K and new conversations do not re-embed documents. Each question still embeds its query and generates a model answer.

Set `EMBEDDING_MODEL_REVISION` to a new value when changing the gateway embedding mapping; the current baseline is text-embedding-3-small with 1536 dimensions. Model-revision changes invalidate the cache. The cache is internal storage, never a source of user authorization or search scope.

## Experiments and isolation

`rag_policy_demo_state` and `rag_policy_demo_chunks` are owned by the authenticated Support/Operator account in market_test. They never replace marketplace document_chunks or business records. Both roles share normal marketplace indexing. The content-addressed embedding cache can reuse identical public lab text across accounts, while selected settings and searchable chunks remain account scoped. Experiment routes are rejected outside Test and for buyer/seller roles. Existing session, ownership and CSRF checks apply.

Selecting a source/strategy normally prepares it automatically. **Demonstrate source change without reindexing** is the explicit exception: selected V2, indexed V1. **Apply changed source** resolves that state. A failed embedding batch preserves previous indexed chunks; selected settings can remain pending, and the UI blocks the next ask until preparation is retried. Model-revision mismatch also makes an index not ready.

The main chat ask route validates that memory, other experiments, response caching and hosted runtimes are off. It saves a normal conversation Run with a rag_demo result: selected/indexed version, strategy, passage IDs/lines, top K, retrieved characters and answer. These controlled RAG requests use only fixed facts and retrieved passages, independent of chat history or long-term memory. Normal Support agent history is not populated with synthetic evidence. Results remain visible when reopening conversations. These are direct retrieval/generation experiments, not a four-tool MCP investigation.

## Reset

Reset to defaults restores client settings, GPT-5.4 Test mapping and clean security fixture when needed, plus any existing demo baselines. It retains embedding caches and does not create never-used demo indexes. The current conversation remains open; its runtime and memory-provider binding remain because those belong to that conversation. No conversation, memory or business records are removed. Subsequent default questions can continue in the same conversation; a clean comparison still needs New conversation. Shared Test model/fixture restoration affects both authorized accounts, as their original controls do.

## Verification

Focused cache tests cover repeated text, reverse version switching, changed chunks, model revisions, malformed responses and provider failures. API tests cover automatic source preparation, intentional stale mode, account/workspace boundaries and reset preserving conversation storage. Main-chat live checks reproduce V1/stale-V1/V2 and all four chunking settings, then reset and ask a normal marketplace policy question in the same conversation. Order, payout and event fingerprints remain unchanged. See the dated results in the exercise solutions.
