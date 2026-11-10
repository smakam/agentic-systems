# A2A support and simulated delivery

This optional lab adds two working A2A flows to the existing marketplace. It uses **a2a-sdk 1.3.0**, implementing **A2A protocol 1.0**. The SDK version and protocol version are different numbers. The implementation uses the installed SDK's JSON-RPC dispatcher, request handler, executor, task store and protobuf types, rather than the older `A2AStarletteApplication` examples.

## What runs

1. The browser can call the existing support agent through either the existing API or A2A. Both paths call `run_support_question` and the existing `answer`, SDK Runner and DatabaseSession. They share identity, owner checks, execution limits, tool preparation, history and settings validation. The A2A executor is a protocol adapter; it is not another reasoning agent.
2. A separate **simulated delivery service** owns durable shipment records, tracking events and problem reasons. Seller-authorized marketplace commands book and update these records through A2A. A small delivery agent uses the configured model gateway and two read tools to investigate shipment questions delegated by support.

No real carriers, payments or payouts are invoked. Shipping writes are deterministic backend operations, never support-agent tools.

## Start the optional lab

Use this branch and the existing [local setup](../LOCAL-SETUP.md). Add two different, independently generated random secrets to the private `app/.env`:

```dotenv
DELIVERY_READ_TOKEN=<random read credential>
DELIVERY_WRITE_TOKEN=<different random write credential>
DELIVERY_MODEL_ALIAS=support-model
```

Keep these values out of Git, screenshots and the browser. The delivery service rejects missing or equal credentials. The read credential can investigate; only the write credential can book, change a scenario or mark delivery. The support browser continues using its existing marketplace session and CSRF token.

From `app/`, start the branch's backend and frontend with the optional service:

```sh
docker compose -f compose.yaml -f compose.a2a.yaml up -d --build backend frontend delivery
```

This is a local branch setup command, not an instruction to deploy or merge it. Stop other processes that occupy the baseline ports before using the standard stack. The optional delivery service has no published host port and is reachable from the marketplace backend on the Compose network. Its SQLite records live in the separate `delivery-state` volume. The marketplace schema adds separate association and A2A metadata tables; existing shipment columns and old orders do not need a blanket migration.

For host development, run Python from `app/backend` so the existing MCP subprocesses can import `marketplace`. Set `DATABASE_URL`, `READ_DATABASE_URL`, `DATA_DIR`, existing gateway credentials, `DELIVERY_A2A_URL` and the two delivery credentials. The Vite proxy target can be set with `MARKETPLACE_API_PROXY`. Do not point automated reset tests at an interactive database.

## Browser walkthrough

### 1. Standard API and A2A Support

- Sign in as support or operator and open **Support workspace**.
- Select **Standard API**, ask an order question and inspect the normal run evidence.
- Select **A2A Support**. Changing the mode starts a fresh conversation.
- Inspect the fetched **actual Agent Card**: business skills, JSON-RPC interface, protocol version, capabilities and security declarations. Expand the raw JSON if useful. A failed card request is shown as an error, not replaced with invented metadata.
- Ask another order question. The browser itself posts an A2A `SendMessage`; it does not call a Python demonstration client.
- Ask a follow-up. Each accepted question invokes a new SDK run and creates a **new completed Task**, using the **same A2A context, owned marketplace conversation and stored session history**. Failed questions produce failed tasks. A completed task cannot reopen.

The card is served at `/api/a2a/support/.well-known/agent-card.json` and JSON-RPC at `/api/a2a/support`. POST requests explicitly enforce the existing session, CSRF and support/operator checks before SDK dispatch. Task retrieval checks the owning conversation. The browser sends `A2A-Version: 1.0`. Replaying the same message ID and payload returns its stored task instead of charging for another run; changing the payload under that ID is rejected.

### 2. A2A Support + Delivery

- As a buyer, purchase an item. It initially has the existing local `pending` shipment.
- As that item's seller (or operator), open **Orders & fulfillment** and select **A2A delivery** for new dispatches. Choose normal transit or the depot exception, then **Dispatch**.
- The authenticated marketplace backend verifies the seller, shipment state and command key before requesting a booking from the delivery service. It saves the external reference and applies the existing `pending → dispatched` business transition only after a valid receipt.
- While dispatched, use **Apply delivery scenario** to switch the linked simulation between normal transit and an exception. The exception records a specific depot scanner failure and missing departure scan. It is not a fabricated explanation.
- Return to support, choose **A2A Support + Delivery**, and ask about the order or shipment. Support locates the shipment and calls a read-only client-helper tool. That helper resolves the persisted association and delegates through A2A. The delivery agent calls status first and reads recorded problem details when an exception, lateness or explanation needs them.
- Back in the seller UI, **Simulate delivery** updates the delivery service first and then applies the marketplace's existing delivered transition and demo-clock `delivered_at`. Return and 24-hour payout-hold rules continue using that timestamp.

The three demo modes guide the walkthrough. **Support transport and shipment enrollment are distinct.** Choosing a support mode does not rewrite old shipments or change a seller's enrollment control. Existing links remain authoritative even after defaults or conversation modes change. An unlinked shipment continues using local marketplace status and legacy delivery controls. A linked shipment continues using its delivery service. Saved link metadata is labeled as such; it is not presented as a fresh remote observation.

## Failure and retry behavior

The marketplace and delivery service do not share one atomic database transaction. External booking is unique per marketplace shipment and writes are repeat-safe. If a remote operation succeeds but the local transaction fails, retrying can recover without creating a duplicate shipment. A remote outage or invalid receipt does not advance local shipping state. The UI reports failure; support evidence explicitly says when fresh remote status or a reason could not be verified.

The marketplace's existing command serialization and actor-scoped idempotency keys remain in use. Blocking database locks and commits run off the async event loop so another command cannot deadlock an in-flight remote call. The service owns richer states such as `in_transit` and `exception`; both map to marketplace `dispatched`. Scenario changes are rejected for delivered or unlinked shipments.

Support A2A contexts, task records and replay receipts are stored in PostgreSQL. Delivery shipment records and scenario receipts are stored in the delivery service's SQLite volume. Delivery protocol task lookup is process-local; it does not claim durable task history across delivery-service restarts. Neither adapter advertises streaming, webhooks, cancellation, task continuation or a registry.

## Checks and evidence

The validation report records the exact executed checks, live model traces and browser results: [A2A validation](A2A-VALIDATION.md). New tests cover protocol validation, authorization, owner isolation, task replay, follow-ups, failed tasks, conditional tool use, seller commands, legacy routing, outage behavior, invalid receipts and distributed retry recovery. The complete existing backend suite and frontend production build are also checked.

Official references: [A2A specification](https://a2a-protocol.org/latest/specification/), [Python SDK](https://github.com/a2aproject/a2a-python), [Agent discovery](https://a2a-protocol.org/latest/topics/agent-discovery/). A known card address is sufficient for this lab; it does not scan cloud accounts or require a registry. Advertised skills describe business behavior, not automatically callable internal function signatures.
