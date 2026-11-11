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
DELIVERY_MODEL_ALIAS=support-model-test
```

Keep these values out of Git, screenshots and the browser. The delivery service rejects missing or equal credentials. The read credential can investigate; only the write credential can book, change a scenario or mark delivery. The support browser continues using its existing marketplace session and CSRF token.

From `app/`, start the branch in the existing Test workspace on `http://127.0.0.1:5179`:

```sh
docker compose -f compose.yaml -f compose.memory.yaml -f compose.a2a-test.yaml up -d --build memory-backend memory-frontend delivery
```

This is a local branch setup command, not an instruction to deploy or merge it. This command targets the Test services; do not rebuild the production backend/frontend for this experiment. Preserve any existing identity or cloud-runtime overlays required by your installation. The optional delivery service has no published host port and is reachable from the marketplace backend on the Compose network. Its SQLite records live in the separate `delivery-state` volume. The marketplace schema adds separate association and A2A metadata tables; existing shipment columns and old orders do not need a blanket migration.

For host development, run Python from `app/backend` so the existing MCP subprocesses can import `marketplace`. Set `DATABASE_URL`, `READ_DATABASE_URL`, `DATA_DIR`, existing gateway credentials, `DELIVERY_A2A_URL` and the two delivery credentials. The Vite proxy target can be set with `MARKETPLACE_API_PROXY`. Do not point automated reset tests at an interactive database.

The repeatable sequence and execution record are in [A2A demo walkthrough](A2A-DEMO-WALKTHROUGH.md).

## Browser walkthrough

### 1. Standard API and A2A Support

- Sign in as support or operator and open **Support workspace**.
- Use **Reset to defaults** at the top of Workspace options for the ordinary API, then ask an order question and inspect the Standard API request span in Langfuse.
- Expand **Workspace options → A2A** and select **Marketplace A2A**. Changing the mode starts a fresh conversation.
- Inspect the fetched **actual Agent Card**: business skills, JSON-RPC interface, protocol version, capabilities and security declarations. Expand the raw JSON if useful. A failed card request is shown as an error, not replaced with invented metadata.
- Ask another order question. The browser itself posts an A2A `SendMessage`; it does not call a Python demonstration client.
- Ask a follow-up. Each accepted question invokes a new SDK run and creates a **new completed Task**, using the **same A2A context, owned marketplace conversation and stored session history**. Failed questions produce failed tasks. A completed task cannot reopen.

The card is served at `/api/a2a/support/.well-known/agent-card.json` and JSON-RPC at `/api/a2a/support`. POST requests explicitly enforce the existing session, CSRF and support/operator checks before SDK dispatch. Task retrieval checks the owning conversation. The browser sends `A2A-Version: 1.0`. Replaying the same message ID and payload returns its stored task instead of charging for another run; changing the payload under that ID is rejected.

### 2. Multi-agent A2A

- In **Workspace options → A2A**, select **Multi-agent A2A** and **Normal transit** or **Depot exception** before purchasing. Settings are saved in the test database and survive account switching.
- **View Agent Card** fetches the marketplace card and, in multi-agent mode, the delivery card on demand. The pop-up viewer shows description, endpoints, skills, capabilities and expandable raw JSON; Close or Escape dismisses it.
- Switch to buyer and purchase an item. Each new shipment captures its delivery enrollment and fixture at purchase. Later option changes do not rewrite it. Existing shipments without an intent stay local.
- Switch to the item's seller (or operator) and use ordinary **Dispatch**. The backend follows the saved intent, books remotely when enrolled, saves the reference, and transitions to dispatched after validating the receipt. Seller route and fixture selectors are removed.
- For the same linked shipment, ask **“What is my order status?”** in each mode. Basic status uses marketplace records: pending, dispatched or delivered.
- Ask **“Track my delivery and give me the details.”** In Standard API and Marketplace A2A, support reports the marketplace status and explains that detailed tracking is unavailable; it makes no delivery-agent call. In Multi-agent A2A, support can delegate for a linked shipment. The remote agent checks status and conditionally checks problem details. Delegation follows the meaning of the question, not a required trigger phrase.
- Langfuse shows **A2A marketplace request → support investigation → delivery outbound → delivery inbound → delivery task → remote model/tools**. Trace context is propagated across the authenticated HTTP boundary. Standard API has its own request span. Metadata records protocol operation, task/context, outcome and timing without credentials. No separate request/response viewer is needed.
- Use ordinary **Simulate delivery** for a linked shipment. This updates the delivery service, then synchronizes the marketplace transition and demo-clock delivered timestamp. Switching support modes does not discard the saved association needed for seller lifecycle synchronization.

Keep order status and remote tracking distinct. A delivery exception does not automatically mean overdue. Normal transit and a depot exception are controlled simulation fixtures, not real carrier data. Simple status retrieval could also be implemented as a deterministic workflow; this lab demonstrates a separately exposed agent and its evidence boundary.

## Failure and retry behavior

The marketplace and delivery service do not share one atomic database transaction. External booking is unique per marketplace shipment and writes are repeat-safe. If a remote operation succeeds but the local transaction fails, retrying can recover without creating a duplicate shipment. A remote outage or invalid receipt does not advance local shipping state. The UI reports failure; support evidence explicitly says when fresh remote status or a reason could not be verified.

The marketplace's existing command serialization and actor-scoped idempotency keys remain in use. Blocking database locks and commits run off the async event loop so another command cannot deadlock an in-flight remote call. The service owns richer states such as `in_transit` and `exception`; both map to marketplace `dispatched`. Scenario changes are rejected for delivered or unlinked shipments.

Support A2A contexts, task records and replay receipts are stored in PostgreSQL. Delivery shipment records and scenario receipts are stored in the delivery service's SQLite volume. Delivery protocol task lookup is process-local; it does not claim durable task history across delivery-service restarts. Neither adapter advertises streaming, webhooks, cancellation, task continuation or a registry.

## Checks and evidence

The validation report records the exact executed checks, live model traces and browser results: [A2A validation](A2A-VALIDATION.md). New tests cover protocol validation, authorization, owner isolation, task replay, follow-ups, failed tasks, conditional tool use, seller commands, legacy routing, outage behavior, invalid receipts and distributed retry recovery. The complete existing backend suite and frontend production build are also checked.

Official references: [A2A specification](https://a2a-protocol.org/latest/specification/), [Python SDK](https://github.com/a2aproject/a2a-python), [Agent discovery](https://a2a-protocol.org/latest/topics/agent-discovery/). A known card address is sufficient for this lab; it does not scan cloud accounts or require a registry. Advertised skills describe business behavior, not automatically callable internal function signatures.
