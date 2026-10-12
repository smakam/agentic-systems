# Cloud SDK HTTP MCP update — October 10, 2026

## Implemented and verified

- Local Compose retains marketplace stdio MCP. Cloud web selects `mcp_http` and the separate authenticated Cloud Run `/mcp` service. SDK memory remains a separate user-bound stdio server.
- The HTTP client binds investigation identity outside the model schema, exposes five business tools, retains nested evidence before cleanup, and fails closed on authentication, expired ownership and snapshot mismatch.
- Thirteen isolated HTTP protocol/lifecycle tests passed with synthetic records, no model calls and no database reset. They cover discovery, hidden ownership arguments, retained evidence, rejected writes, cross-investigation isolation, expiry, authentication failure, snapshot mismatch, cleanup/cancellation and unsafe endpoint rejection.
- Terraform configuration validates. The web identity was granted access to the existing MCP API-key secret; unrelated service settings were preserved.
- Cloud Build `1260dcea-8c38-4b9a-ab0b-259d4449653a` succeeded in `asia-south1`.
- Image: `asia-south1-docker.pkg.dev/marketplace-app-511005/marketplace/web@sha256:75bc70256c987cbb6eec6fb33be93605a2a3d9f8784e18b523c4feb06386355e`.
- Cloud web revision `marketplace-web-00015-8lb` is ready. Readback confirms `AGENT_TOOL_TRANSPORT=mcp_http`; the SDK URL points to `https://marketplace-mcp-327903210973.asia-south1.run.app/mcp`, and the API key is a Secret Manager reference.

Use this immutable image as the `web_image` input on the next Terraform deployment. The service rollout used a targeted Cloud Run update; a full Terraform apply was not performed.

## Live acceptance passed — October 10

The initial deployed run failed because MCP serialized the initial clock with ISO `T`, while retained evidence used the persisted datetime string with a space. The client now compares timezone-aware clock instants while still rejecting clock/revision/document drift. Regression tests cover equivalent serialization and real drift. Evidence accounting now counts unique retained envelopes; the `attempt` field is a retry ordinal, not a cumulative call counter.

A subsequent ordinary follow-up reused prior conversation evidence without a fresh tool call. This was not a transport failure. The final acceptance explicitly requested freshly retrieved data in the follow-up so it exercised a second HTTP investigation.

| Run | Status | Retained envelopes | Model requests | Trace |
|---|---|---:|---:|---|
| run-3833d7a0af | completed | 5 | 4 | a77bb8845f0a5f206e488a62df783c18 |
| run-5125281875 | completed | 1 | 2 | 83f35257e01c32b222d848787f424a22 |

Both used `mcp_transport=http` and `marketplace-mcp-327903210973.asia-south1.run.app`, at business revision 24. Readback verified the saved evidence after the questions ended, and every answer citation refers to retained evidence. Langfuse API readback found 23 and 12 observations respectively, with model generations and actual TOOL observations. The first trace contains get_catalog, get_order_history and query_business_data; the second contains query_business_data. All reported tool levels were DEFAULT, with no tool ERROR.

[Saved application runs and sanitized trace summaries](SDK-HTTP-ACCEPTANCE-2026-10-10.json). No secret values or raw model reasoning are exported. These are bounded live connectivity/evidence checks, not broader platform parity or a production-readiness claim.

SQL shutdown was submitted after successful validation: operation `2f7dcbef-34e3-4ef4-9558-d06f0000002f`. Operation is DONE; instance readback confirms activation policy `NEVER` and state `STOPPED`. Business data was only read during the live questions.

## Chapter 8 materials

The internal course plan, implementation guide, architecture document and standalone HTML diagram reflect the new path and this acceptance boundary. Slides/notes describe the three tool responsibilities and local/remote connections.

The exercise package includes core demo repetition, the seller-balance extension and a separate simulated tracking MCP server. Both reference implementations passed actual stdio discovery/calls. Seller balance used the fixed `market_eval` database with read-only credentials, verified reconciliation and an unknown/malicious-looking bound ID, and did not change its records. Tracking verified known-ID and not-found behavior against the supplied JSON.

Owner checks remain separate: review slides, execute demos, execute exercises against solutions, and check notes alignment.
