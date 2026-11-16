# Agentic UI Marketplace Demo

The Agentic UI comparison and direct controlled renderer are included in `main`. AG-UI is explained only; there is no AG-UI runtime integration.

## Start The Isolated Review

Prerequisites: complete [Local Setup](../LOCAL-SETUP.md) first and confirm the existing Test workspace is healthy. This guide uses the default `marketplace-lab` Compose project and its `marketplace-lab-test-backend-1` and `marketplace-lab-postgres-1` containers. Install Node 22/npm on the host for the teaching host; unlike baseline Docker startup, this path runs Vite on the host. Keep ports 58010 and 5181 free and use the Test gateway's valid model credentials. No provider credentials are stored in the repository.

From the repository root, build the image that the helper expects, then start the review backend:

```sh
docker build -t marketplace-a2ui-common-backend:local app/backend
python3 app/scripts/start-agentic-ui-review.py
curl --fail http://127.0.0.1:58010/api/health
```

The helper does not build this image itself. Rebuild it after dependency changes. It bind-mounts the current checkout's marketplace code, and copies the existing Test configuration and read-only mounts. If your baseline uses another Compose project/container naming scheme, adapt the helper deliberately; it is not an auto-discovery tool for arbitrary installations.

The script creates a separate PostgreSQL container from a snapshot of Test on its first run. It restores the reader's read-only role settings and starts only `marketplace-agentic-ui-backend` on loopback port 58010. Subsequent runs retain that copied database and restart only this review backend. The ordinary Test/production databases and containers are not reset or restarted. Mounts for existing configuration and course data remain read-only. Do not use this script as a production deployment procedure.

Then, in `app/frontend`:

```sh
npm ci
MARKETPLACE_API_PROXY=http://127.0.0.1:58010 npm run demo
```

Open `http://127.0.0.1:5181`. `npm run demo` builds the self-contained MCP UI resource and starts the Vite teaching host/MCP endpoint. `npm run preview` is not an MCP host. Use a separate browser profile or a different loopback hostname if you need to keep another local marketplace session signed in; cookies are not scoped by port.

The MCP middleware is local-only and uses the existing authenticated session and CSRF token. It exposes only the two read-only presentation tools, not arbitrary marketplace commands. A valid owned source investigation is required.

## Run Regressions Without Resetting The Interactive Test Workspace

The regression runner is separate from the review backend. It expects a dedicated container named `marketplace-a2a-test-db` on Docker's default `bridge` network. It must never use `marketplace-lab-postgres-1`, `market_test` in that shared container, or `marketplace-agentic-ui-db`.

From the repository root, check whether the dedicated container already exists:

```sh
docker ps -a --filter name=marketplace-a2a-test-db --format 'table {{.Names}}\t{{.Status}}'
```

If it exists, start it with `docker start marketplace-a2a-test-db` if needed. Do not reinitialize it while a regression run is active. For a **first run only**, create the dedicated database with the same pinned pgvector image used by the baseline:

```sh
docker run -d --name marketplace-a2a-test-db --network bridge \
  -e POSTGRES_PASSWORD=regression-local-only \
  --mount "type=bind,source=$PWD/app/infra/init.sql,target=/docker-entrypoint-initdb.d/10-marketplace.sql,readonly" \
  pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f
```

This database has no published host port. The public local-demo passwords in `init.sql` are for this disposable lab, not production credentials. Wait until readiness succeeds **and** the `market` role exists (initialization may still be running after the server first accepts connections):

```sh
docker exec marketplace-a2a-test-db pg_isready -U postgres
docker exec marketplace-a2a-test-db psql -U postgres -Atc "SELECT rolname FROM pg_roles WHERE rolname='market'"
```

Only after those checks succeed, create the regression database and enable pgvector:

```sh
docker exec marketplace-a2a-test-db createdb -U postgres -O market market_test
docker exec marketplace-a2a-test-db psql -U postgres -d market_test -v ON_ERROR_STOP=1 -c 'CREATE EXTENSION IF NOT EXISTS vector'
```

Initialize the new regression database's marketplace schema, seed and auxiliary tables before the first suite run. This command shares only the dedicated database container's network namespace; it does not connect to the normal Test database or call a model provider:

```sh
docker run --rm -i --network container:marketplace-a2a-test-db \
  -e DATABASE_URL=postgresql+psycopg://market:market-local@127.0.0.1:5432/market_test \
  -e READ_DATABASE_URL=postgresql://agent_reader:reader-local@127.0.0.1:5432/market_test \
  -e DATA_DIR=/data \
  --mount "type=bind,source=$PWD/app/backend/marketplace,target=/app/marketplace,readonly" \
  --mount "type=bind,source=$PWD/app/data,target=/data,readonly" \
  marketplace-a2ui-common-backend:local python - <<'INIT'
from marketplace.db import init_schema, Session
from marketplace.seed import seed
from marketplace.rag_policy_demo import initialize as initialize_rag_demo
from marketplace.embedding_cache import initialize as initialize_embedding_cache
init_schema()
with Session.begin() as db:
    seed(db)
initialize_rag_demo()
initialize_embedding_cache()
INIT
python3 app/scripts/test-a2ui-preview.py
```

The `createdb` command is first-run-only. Later runs reuse this dedicated database; the tests may replace its fixtures. The runner checks the container name, network and default-bridge address before using it. If Docker uses a different bridge subnet, stop and adapt that guard to your dedicated test environment; do not redirect it to the interactive database just to pass the check.

Frontend checks run from `app/frontend` after `npm ci`:

```sh
node --test src/*.test.js mcp-app-server.test.mjs
npm run build
```

These regressions use synthetic data and test doubles for model calls. They do not establish live model quality or third-party assistant compatibility. Historical counts are in [Validation](AGENTIC-UI-VALIDATION.md); report the results of your own run.

On 16 November 2026, the documented first-run database creation and explicit initialization were exercised in a new disposable container using the existing local backend image and current mounted source. The complete backend suite passed: 375 tests and 30 subtests, with 10 optional skips. The temporary validation database was removed afterward; normal Test and main databases were not reset. This does not claim a fresh image/package download or a new live-model/OAuth verification.

## Stop And Resume

Stop the host `npm run demo` process with Ctrl-C. Stop only these dedicated containers when they are idle:

```sh
docker stop marketplace-agentic-ui-backend marketplace-agentic-ui-db
# Only if you created/used the separate regression container:
docker stop marketplace-a2a-test-db
```

To resume, start `marketplace-agentic-ui-db`, then rerun the review helper and the host frontend command above. Start the regression container separately if needed. Keep the normal Test baseline running while creating/restarting the review backend. Stopping these containers retains their data; no reset or volume-deletion command is needed. The first review database is a snapshot, so later changes in normal Test do not automatically appear there.

## Local And Cloud Scope

This is a local/Test teaching path on code included in `main`. It does not install MCP Apps in ChatGPT/Claude, configure cloud networking, deploy the review backend, or implement AG-UI. The baseline cloud setup does not automatically enable these experiments. See [MCP authentication](MCP-AUTHENTICATION.md) for the separate identity/payout lab and [A2A](A2A-MARKETPLACE.md) for agent communication.

## Demonstration Sequence

1. Sign in as operator or support. Open Support workspace and enable **Visual answers** under Agentic UI. Use standard API/SDK mode with other experiments and memory off.
2. Start a new investigation: `What is the current status of order order-1? Include items and delivery status.` The initial presentation is declarative.
3. Open Text answer and sources. Establish the facts before comparing the UI.
4. Select **Controlled** on that result. Inspect Model view selection. A checked result was `{"view":"table","reference":"d0"}`. The application renders the fixed arrangement directly through `ControlledAnswer`, using the selected data. No A2UI messages or model-generated component tree are used in controlled mode.
5. Select **Declarative**. Inspect Presentation instructions, Model layout output, and A2UI messages received by the renderer. Follow the dataset reference into the supplied data. A checked status output used Text, RecordTable, a button label/Button, and Column. Model choices can vary.
6. Select **Open-ended**. Inspect generated UI code. This demo supports static HTML/CSS only: markup is sanitized and CSP blocks model scripts and network access. The model generates a history button using a supplied action identifier. Only a nonce-authorized application script handles its click, forwarding an allowlisted action to the parent. The parent verifies the frame source and action before using the existing owned/CSRF-protected backend request. Compare displayed facts with the same source evidence.
7. Select **Declarative → Display: MCP Apps**. Inspect Delivery and interaction events plus Inspect MCP protocol evidence. The tool declares a `ui://` resource; the host reads HTML containing the renderer/widgets. Initialization and tool input/result delivery use the official MCP Apps bridge.
8. Open browser DevTools → Network, filter `mcp-ui`, and inspect JSON-RPC `initialize`, `tools/list`, `resources/read`, and `tools/call`. The optional GET event stream is unsupported by this stateless demo and returns 405; POST tool/resource calls are the relevant path.
9. Click Show order history inside the iframe. Observe iframe → host → MCP tool → result → iframe. Checked output: EventTimeline plus RecordTable for returns/refunds/payouts. The tool calls the existing support API internally; MCP is the host/provider boundary.
10. Back in Direct view, request/choose the recorded history investigation. Compare its controlled timeline selection with the declarative composition and generated HTML. UI mode buttons re-present one completed investigation; a history click creates a new business investigation.

## Under-The-Hood Evidence

| Claim | Evidence |
| --- | --- |
| Controlled selects rather than composes | Model view-selection JSON; `controlled_view` in `marketplace/agentic_ui_demo.py` resolves its data; `ControlledAnswer` renders a prebuilt React view directly, without A2UI messages |
| Declarative composes components | Model layout output, catalog/signatures in instructions, resulting A2UI payload, client registry in `A2UIMarketplace.jsx` |
| Open-ended produces code | Generated HTML/CSS output, sanitized frame document, sandbox without same-origin permission, nonce-only script policy, source-bound approved history messages |
| The support facts are held constant | Same source run/evidence handles shown in Inspect delivery and rendering; comparison endpoint does not rerun business tools |
| MCP Apps is a protocol integration | Tool metadata, resource receipt, AppBridge/App implementation, Network JSON-RPC and actual frame tool round trip |
| The presentation model was called | Inspector trace identifier; Langfuse `Agentic UI presentation comparison` root and mode-specific generation child |

The original support investigation retains its normal trace. Alternative presentations have separate traces linked by `source_run_id` and `conversation_id` metadata. Look at the generation input/output to distinguish selection, composition and code. Local Langfuse v4 uses Observations API v2 for API reads; legacy trace endpoints return 404 in events-only mode.

## Observed Lessons

- Controlled and declarative status views can look similar: both selected a table in the checked run. Inspect the model output and application-owned arrangement to establish the distinction.
- For history, checked controlled output selected one timeline; checked declarative output combined timeline and records table.
- Open-ended rendered the order facts correctly in the inspected status sample, but this is not a repeated-run quality benchmark. One attempt exceeded its output limit and fell back to text; the compact prompt and retry affordance address the demo flow without claiming perfect generation.
- The MCP App reused the same declarative widgets. Protocol events, the iframe boundary and the history tool call establish what changed.
- Isolation does not establish factual correctness. Keep answer/source evidence available and inspect provenance and truncation notices.

## Limits

- MCP Apps is implemented only for the declarative example in the local teaching host. No ChatGPT/Claude installation or compatibility certification is claimed.
- The MCP provider lives in the local dev host process; it is a real SDK-backed server, not a full assistant/model router. The generation comparison reuses already-completed investigations.
- Open-ended here means model-generated HTML/CSS and button markup. Only the application-authored history bridge executes; arbitrary model-generated JavaScript remains disabled.
- All experiments retain the existing Test-only A2UI gate. No AG-UI implementation, production deployment, or publication is included.
- The existing A2UI/Zod dependency chain retains an upstream audit finding. Model payloads are bounded and validated before rendering; this guide does not claim the dependency issue is fixed. Do not use a forced dependency downgrade as a substitute for a compatible upstream patch.
