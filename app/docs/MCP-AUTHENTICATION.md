# MCP authentication — ordered local walkthrough

Use this guide for the marketplace's three access patterns: shared support access, delegated buyer/seller access, and a service identity for **simulated** payouts. All code is in `main`. The shared-key wrapper is a custom integration, not MCP's standard OAuth flow. Keycloak supplies identity; the marketplace backend enforces ownership and business permissions.

## 1. Start The Marketplace Baseline

Complete [Local Setup](../LOCAL-SETUP.md), including gateway/provider configuration and health/login checks. Start it from `app/` with `./scripts/start.sh`. The identity Compose file expects the default `marketplace-lab_default` network. Shared support reads and delegated order reads use the main `market` database; payout automation uses the separate synthetic `market_test` database. They do not all share one workspace.

Commands below run from `app/` unless marked otherwise. Docker/Compose and Python 3 are required. The host provisioning and OAuth checks use `httpx`; use a private virtual environment rather than a global install:

```sh
python3 -m venv /tmp/marketplace-mcp-venv
. /tmp/marketplace-mcp-venv/bin/activate
python -m pip install httpx==0.28.1
# Identity and payout services reuse this baseline image tag:
docker build -t marketplace-lab-backend backend
```

Keep the baseline running. Do not run fixture resets against either interactive workspace while someone is using it. No new model provider key is needed for the OAuth checks; asking support questions still uses your existing inference provider.

## 2. Check Shared-Key Support Access

The baseline support UI normally calls MCP over a local subprocess. This separate HTTP endpoint demonstrates fixed application-level support access; it is not a buyer/seller identity.

Create `app/.remote-mcp.env` in your editor if it does not already exist. Give `REMOTE_MCP_API_KEY` an independently generated random value of at least 32 characters. Keep the existing value when resuming an already configured environment. Store it only in this gitignored file and set `chmod 600 .remote-mcp.env`. Do not paste it into screenshots, source code or this guide.

```sh
docker compose -f compose.yaml -f compose.remote-mcp.yaml up -d --no-deps remote-mcp
# No credential: expected HTTP 401, not a successful tool call.
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:58001/mcp
```

For an authenticated tools/list check without printing the key or putting it on a shell command line:

```sh
python - <<'CHECK'
from pathlib import Path
import httpx
values = dict(line.split('=', 1) for line in Path('.remote-mcp.env').read_text().splitlines()
              if line and not line.lstrip().startswith('#') and '=' in line)
response = httpx.post('http://127.0.0.1:58001/mcp',
    headers={'x-api-key': values['REMOTE_MCP_API_KEY'], 'Accept': 'application/json, text/event-stream'},
    json={'jsonrpc': '2.0', 'id': 1, 'method': 'tools/list', 'params': {}})
response.raise_for_status()
result = response.json()
assert 'error' not in result, result
print('Tools:', ', '.join(tool['name'] for tool in result['result']['tools']))
CHECK
```

This verifies the HTTP boundary and tool surface, not a full investigation. The read-only support tools use investigation-scoped evidence. A shared key is not a per-person identity. Use a local MCP client that supports the API-key header; this path is not the ChatGPT OAuth connector example.

## 3. Prepare The HTTPS Origin And Exact OAuth Callback

Delegated access uses a reachable HTTPS origin forwarding to the local proxy on port **58002**. Supply your own tunnel/reverse-proxy configuration and any required account. Keep the local service bound to loopback. This guide does not create a tunnel, weaken TLS verification or reuse an instructor-owned domain.

Before provisioning, obtain the **exact callback URL** shown by the ChatGPT MCP connection flow and the stable public HTTPS origin you will use. Do not guess a callback or use a wildcard. The setup helper accepts an HTTPS origin with no path, query or fragment and a callback on `chatgpt.com` with no query/fragment. Availability of custom MCP connections depends on your account.

```sh
python user-mcp/setup.py \
  --base-url https://YOUR-HTTPS-ORIGIN \
  --chatgpt-callback https://chatgpt.com/YOUR-EXACT-CALLBACK-PATH
```

Replace both placeholders before running. The helper creates `.env.user-mcp` and private `.user-mcp/` files: realm/client configuration, identity links, proxy configuration and `Access.md`. It generates distinct credentials and maps the four demo buyers/sellers to explicit subjects. These files are gitignored and contain secrets; view access details privately in your editor, not in public terminal output. Repeating setup preserves matching settings and refuses a different origin/callback. Changing an existing realm requires an explicit migration, not deleting identity data to make startup pass.

## 4. Start Identity, Delegated Orders And The Proxy

```sh
docker compose --env-file .env.user-mcp -f compose.user-mcp.yaml up -d identity orders proxy
docker compose --env-file .env.user-mcp -f compose.user-mcp.yaml ps
```

Wait for Keycloak realm import before checking:

```sh
curl --fail http://127.0.0.1:58501/identity/realms/marketplace/.well-known/openid-configuration
```

Start your HTTPS route to `127.0.0.1:58002`, then check public issuer discovery at `https://YOUR-HTTPS-ORIGIN/identity/realms/marketplace/.well-known/openid-configuration`. Its issuer must match the configured public origin. The proxy routes `/identity/realms/marketplace/` and identity assets, not the Keycloak admin API. Keep administration on loopback port 58501.

In the ChatGPT connection, use the endpoint `https://YOUR-HTTPS-ORIGIN/orders/mcp` and the client details from the private `Access.md`. Sign in as one of `buyer`, `buyer2`, `seller`, or `seller2` with the generated identity password. This password differs from the baseline marketplace password. The service grants scoped order reads, not arbitrary marketplace support tools.

## 5. Verify Delegated Access And Denials

```sh
python user-mcp/verify_oauth.py
```

The check uses the configured public HTTPS route, real Keycloak code/PKCE and the four linked demo accounts. It checks discovery, profile, owned orders/seller lines, cross-buyer denial, refresh identity and authorization-code replay rejection. Its receipt is `.user-mcp/oauth-verification.json`; tokens remain in memory. This is a local synthetic-account verification, not a general security certification. Changed demo fixtures may invalidate the script's expected `order-1`/`order-2` ownership; inspect failures rather than resetting shared data automatically.

## 6. Configure Service Access For Simulated Payouts

Keep Keycloak running. Register the service client and private Test-only policy, then start only the payout endpoint:

```sh
python user-mcp/configure_payout.py
python user-mcp/payout_control.py service
python user-mcp/payout_control.py status
```

The configurator registers client-credentials access and writes private credential, policy and worker files. The endpoint listens on loopback **58503** and connects to `market_test`. Policy requires the exact service identity, scopes, simulation flag, eligibility and amount/run limits. No real payment provider is called. The scheduler is not started by either setup command.

To demonstrate a release, use the **Test** UI as operator: deliberately enable automatic payouts in Admin, prepare a delivered synthetic order, and advance the demo clock past the required hold according to the lesson. Keep main-workspace manual payout behavior separate.

First run one explicit iteration and inspect its result:

```sh
python user-mcp/payout_control.py once
python user-mcp/payout_control.py status
```

No eligible candidates or disabled automation can correctly produce no releases. Check both successful and denied cases. Repeating a release uses its stable idempotency key rather than paying twice. The sanitized run log lives in `.user-mcp/payout-runs/runs.jsonl`.

Only if you deliberately want recurring simulated runs:

```sh
python user-mcp/payout_control.py start --interval 60
# Stop the scheduler after the demonstration:
python user-mcp/payout_control.py stop
```

The minimum interval is 10 seconds. Stopping the worker does not change the Test UI's automatic-mode flag; turn that off separately when you finish.

## 7. Marketplace Keycloak Sign-In — Separate UI Exercise

Delegated MCP works without changing marketplace web login. If you also want to compare username/password and Keycloak login in both local UIs:

```sh
python user-mcp/configure_ui_login.py
python user-mcp/switch_runtime.py branch
python user-mcp/verify_ui_login.py
```

Here `branch` means **this checkout**, including a checkout of `main`; it does not require a feature branch. The switch helper recreates the four main/Test application services using the current checkout, preserves their active Compose environment and database state, and mounts the generated private UI identity files. Wait until no investigations are active and retain any cloud/runtime overlays your installation needs. The verifier checks both authentication methods, account scoping and logout for six synthetic roles on both ports. This registers the separate `marketplace-web` client; it does not expand the MCP tool permissions.

## 8. Stop And Resume Without Losing Identity Or Marketplace Data

```sh
python user-mcp/payout_control.py stop
docker compose --env-file .env.user-mcp \
  -f compose.user-mcp.yaml -f compose.payout-mcp.yaml stop
docker compose -f compose.yaml -f compose.remote-mcp.yaml stop remote-mcp
```

Stop your tunnel separately. Do not use `down -v` or delete `.user-mcp/` as a normal shutdown: the identity volume, subject mappings and credentials must remain consistent. These commands do not stop the baseline marketplace. If web Keycloak login was enabled, it is unavailable while identity/proxy are stopped; the normal password path remains separate. Resume the baseline first, then identity/orders/proxy, then the payout endpoint if needed. Keep the scheduler opt-in. Reuse the same public origin/callback and private files.

## Scope And Troubleshooting

- Missing Docker image/network: complete baseline startup and the image build in section 1. Confirm you are using the default project names expected by these Compose files.
- Unauthorized shared support call: check the private API key and which endpoint the client calls. Buyer OAuth tokens are not shared support keys.
- OAuth issuer/callback mismatch: compare public discovery with `settings.json` privately; preserve exact origin and callback. Do not disable signature/TLS checks.
- Old Keycloak realm: realm import initializes a new identity volume; it is not an automatic update mechanism for an existing realm. Apply explicit administrative changes when changing registered clients.
- Payouts do nothing: inspect automatic-mode opt-in, delivery/hold eligibility, service identity/scopes and policy budgets before assuming authentication failed.
- Cloud: this guide configures a local identity lab behind your own HTTPS route. It does not install these services in the baseline cloud deployment or certify any third-party host. See [Cloud Setup](../CLOUD-SETUP.md) for that separate boundary.

See also [Agentic UI setup](AGENTIC-UI-DEMO.md), [A2A setup](A2A-MARKETPLACE.md) and the [exercise index](../../course/exercises/README.md). Backend regressions for these boundaries live in `tests/test_remote_mcp.py`, `tests/test_user_mcp.py`, `tests/test_payout_mcp.py` and `tests/test_oidc_login.py` under `app/backend`; use a dedicated disposable database as described in the Agentic UI guide, not the interactive Test database.

## Documentation Verification — 16 November 2026

The ordered commands were checked against their current scripts and Compose definitions. Eleven existing setup/runtime unit tests passed, including repeatable identity provisioning and preservation of active UI-login mounts during runtime switching. Backend authentication/payout regressions were included in the 375-test run on a fresh dedicated database described in the Agentic UI guide. This documentation pass did not reprovision the running Keycloak realm, connect a new third-party host, start the payout scheduler or repeat the public HTTPS OAuth flow.
