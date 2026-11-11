# A2A implementation validation

## Test workspace refinement, 11 November 2026

Follow-up UI refinement: Reset is above the collapsed A2A section; only Marketplace A2A and Multi-agent A2A are selectable experiments. Agent Cards open in a native modal. All 43 frontend tests and the production build passed again; browser checks verified one/two cards, Close/Escape, focus restoration and reset to the unselected/off state with the A2A section collapsed.

The separate review branch now runs on the existing test UI at port 5179 with market_test. Production container IDs/start times and main were preserved. Original test containers are retained stopped for rollback; no database was reset during deployment.

- Full backend suite: **356 passed, 10 optional skipped, 20 subtests passed**.
- Frontend: **43 passed**; production build passed. Both Docker images built; the test-only Compose overlay passed configuration validation.
- Browser checks: centralized settings; one/two on-demand cards with raw details and correct endpoint; purchase and ordinary seller dispatch; persistence across accounts; reset defaults; explicit history-only guard for conversations from another mode.
- Nine live API comparisons were independently checked against Langfuse observations. Standard API has its own request span. Marketplace A2A has an actual protocol span. Detailed multi-agent tracking links outbound and inbound delivery spans to the remote model/tool loop in the same trace. Marketplace modes and basic-status questions made no delivery call.
- Remote records verified: normal in_transit with status tool; exception with status plus problem-detail tools; then delivered after ordinary seller action. A live follow-up created a new task in the same context.
- Controlled service outage: dispatch returned 503 and left marketplace pending; recovery retry succeeded. Automated checks cover concurrent shipping/reset, saved intent, direct-dispatch bypass prevention and no remote calls enabled merely by configured credentials.
- Standards review found enrollment guard and reset gaps; both fixed. Its follow-up caught a reset lock wait on the event loop; fixed with worker execution and a concurrent test. Requirements review found silent context loss across modes; fixed with explicit read-only history and New conversation. Both reviewers cleared the fixes.

The full sequence was exercised through a combination of browser actions and live API calls, not exclusively browser clicks. Initial live attempts exposed an incorrect Langfuse hostname and an unauthorized delivery model alias; these were corrected before the successful rerun. This is a local simulation, not a real-carrier or model-quality benchmark. User retest and approval remain pending.

See [the repeatable demo sequence](A2A-DEMO-WALKTHROUGH.md) for expected outcomes, ready records and trace links.


Validated on 10 November 2026 against base commit `49fcf34`, on `codex/marketplace-a2a-support-delivery`. The original checkout and its two running workspaces were preserved. No merge or production deployment was performed.

## Automated checks

| Check | Executed result |
|---|---|
| Complete backend suite | **348 passed, 10 skipped, 20 subtests passed** |
| Final focused A2A, delivery and conversation checks | **49 passed** |
| Frontend Node tests | **43 passed** |
| Frontend production build | Passed; 296 modules |
| Backend and frontend Docker image builds | Both passed, using unique local review tags |
| Container import smoke | SDK 1.3.0; support and delivery apps import successfully |
| Nginx configuration test | Passed |
| Optional A2A Compose configuration | Passed `config --quiet`; no services started by that check |
| Whitespace/diff validation | Passed |

The 10 skipped tests are the existing optional cloud-registry PostgreSQL tests and dedicated Mem0 database integration tests. They were not reported as passing. The A2A, shipping, ownership, legacy shipment, return and payout tests ran.

The full suite ran from `app/backend` with a dedicated PostgreSQL container, an isolated database named `market_test`, and a placeholder gateway key. It did not use interactive marketplace records or real model credentials:

```sh
DATABASE_URL=postgresql+psycopg://market:market-local@127.0.0.1:55434/market_test \
READ_DATABASE_URL=postgresql://agent_reader:reader-local@127.0.0.1:55434/market_test \
DATA_DIR=/absolute/path/to/agentic-systems/app/data \
LITELLM_API_KEY=test-no-live-network \
LITELLM_URL=http://127.0.0.1:1/v1 \
python -m pytest tests -q -rs
```

Port 55434 was used only for this disposable regression container. Learners can use their own isolated test container and port. The test safety assertions require the database name `market_test`; do not substitute an interactive workspace.

Frontend checks from the repository root:

```sh
node --test app/frontend/src/*.test.js
npm --prefix app/frontend run build
git diff --check
```

Focused backend test files:

- `tests/test_support_a2a.py`: actual SDK JSON-RPC, session/CSRF/roles, context and task ownership, new-task follow-ups, shared API validation, failed tasks, unsupported features, durable message replay, version checks, alias rejection and concurrent questions.
- `tests/test_delivery_service.py`: separate credentials, deterministic A2A writes, durable/restarted and concurrent fixture storage, scenario replay protection, conditional model tools, overdue transit, failed tasks and malformed receipts.
- `tests/test_delivery_shipping.py`: seller authorization before remote writes, link-based routing, legacy behavior, idempotency, remote-success/local-rollback recovery, outages, post-dispatch scenario controls, delivery timestamps, return/payout dependencies and concurrent shipping/non-shipping commands.
- `tests/test_conversation_order.py`: existing history ordering, owner isolation and runtime/provider metadata with additive A2A metadata.

## Live model and browser checks

The review environment ran a separate backend on port 58600 and browser UI on port 5184, using a dedicated `market_a2a_demo` database. A separate delivery service ran on port 58604 with a private SQLite file and separate generated read/write tokens. Existing configured scoped model-gateway credentials were used privately. No provider/service keys were exposed in the UI, cards, screenshots or committed files.

The actual configured delivery model called:

| Fixture | Observed read tools | Completed delivery model responses |
|---|---|---|
| Normal transit, on schedule | Status only | 2 |
| Depot exception | Status, then recorded problem details | 3 |

These are measured traces from real model requests, not canned responses or merely a count of available tools. The controlled tests additionally check that overdue `in_transit` cannot be treated as on schedule and that missing required evidence fails the investigation.

Executed browser journey:

1. Signed in as support and fetched the actual Agent Card. It showed protocol 1.0, the same-origin JSON-RPC interface, business skills, false streaming/push capabilities, and session/CSRF security declarations.
2. Submitted an order question using **A2A Support** and received a completed task with a normal marketplace run.
3. Submitted a follow-up. Stored metadata confirmed a different task ID with the same context and marketplace conversation; the agent retained the order reference from history.
4. Signed in as buyer and purchased Canvas Weekender and Trail Backpack in one new order.
5. Signed in as the owning seller and dispatched both through A2A. Both saved external references and became marketplace `dispatched`.
6. Changed Canvas Weekender to the depot exception **after dispatch** using the seller UI. The external record retained the specific scanner failure and tracking evidence.
7. Asked support about Canvas Weekender using **A2A Support + Delivery**. The completed answer quoted the recorded reason. Its evidence panel displayed actual remote status, observation/simulation times, status and problem-detail tool calls, and tracking evidence.
8. Changed the conversation mode to **Standard API** and asked about the linked Trail Backpack. It still delegated using the persisted shipment link and returned `in_transit`, `on_schedule=true` with a status-only delivery trace.
9. Changed the seller's new-dispatch default back to local. Existing enrolled shipments retained their references and delivery controls.
10. Stopped the isolated delivery service and attempted **Simulate delivery** in the seller UI. The command returned HTTP 503, the UI displayed an honest error, and the shipment remained dispatched.
11. Restarted the service and completed **Simulate delivery** while the default remained local. The linked shipment became delivered, the action button disappeared, and PostgreSQL confirmed `delivered_at` equals the marketplace demo clock.

## Evidence and limits

Sanitized local traces and screenshots are in the course workspace's `A2A Research/implementation-evidence/2026-11-10` folder. They include `live-integration.json`, `live-delivery.json`, backend/frontend logs, `actual-agent-card.png`, `seller-linked-scenarios.png`, `support-delivery-evidence.png`, and `delivered-with-local-default.png`. These generated files and private runtime settings are not part of the code commit.

The live UI checks used local Python/Vite processes and the existing gateway, with isolated marketplace data. Both Docker images were built and smoke-tested; a complete new Compose deployment was not started. Cross-system shipping is retry-safe coordination, not an atomic distributed transaction. Delivery task lookup remains process-local; delivery shipment/scenario records and support tasks/contexts/replay receipts are durable. Streaming, webhooks, cancellation, pending-task continuation, registry scanning and real carrier integrations are outside this implementation.
