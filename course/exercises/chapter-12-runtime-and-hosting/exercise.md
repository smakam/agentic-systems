# Chapter 12 — Host only the agent in Cloud Run

The local Docker setup is already complete. Move the agent process to your own Google Cloud project while chat, history, middleware and business data remain on your laptop.

Path: local chat → Cloud Run agent → authenticated HTTPS tunnel → local HTTP MCP → disposable PostgreSQL copy. The agent calls OpenAI directly. LiteLLM still supplies the local middleware embedding dependency; it is not the agent model route in this exercise.

## Prerequisites

Use the existing app setup, Docker, a running local gateway and PostgreSQL, and the unchanged `market_eval` baseline. Install cloudflared at `app/.remote-mcp/cloudflared` using the existing tunnel setup. You need Google Cloud billing, Cloud Run, Artifact Registry and Secret Manager enabled, an Artifact Registry Docker repository, deployment permissions, and a service account. Provision your own OpenAI key as a Secret Manager secret in your chosen project and give that service account Secret Accessor permission on it. The helper deliberately does not upload provider keys from the laptop. Do not use instructor credentials. Configure gcloud authentication; this machine also supports the existing local ADC Docker CLI fallback.

## Run from the repository root

```sh
python3 course/exercises/chapter-12-runtime-and-hosting/solutions/cloud_lab.py prepare
bash course/exercises/chapter-12-runtime-and-hosting/solutions/reset_lab.sh
docker compose -f app/compose.yaml -f app/compose.ch12.yaml --profile chapter12 up -d --no-deps ch12-mcp
python3 course/exercises/chapter-12-runtime-and-hosting/solutions/tunnel.py start
```

Keep the returned tunnel URL. Deploy with your actual project, region, repository, service account, provider secret name and HTTPS tunnel URL ending `/mcp`:

```sh
python3 course/exercises/chapter-12-runtime-and-hosting/solutions/cloud_lab.py deploy --project YOUR_PROJECT --region YOUR_REGION --repository YOUR_REPOSITORY --service-account YOUR_SERVICE_ACCOUNT --openai-secret YOUR_PROVIDER_SECRET --mcp-url YOUR_TUNNEL_MCP_URL
docker compose -f app/compose.yaml -f app/compose.ch12.yaml --profile chapter12 up -d --no-deps --force-recreate ch12-mcp
docker compose -f app/compose.yaml -f app/compose.ch12.yaml --profile chapter12 up -d --no-deps ch12-backend ch12-frontend
```

Deployment supplies an application API key through Secret Manager. The public HTTPS endpoint rejects unauthenticated investigation calls; its health endpoint contains no secrets. `.ch12.env` is private and ignored by Git. Recreating MCP is necessary because deployment records the allowed tunnel hostname. Keep laptop and tunnel running throughout. If a deployment fails after creating resources, inspect the recorded state and use `deploy --resume` with the same arguments rather than generating another deployment.

Open http://localhost:5192, sign in as the supplied support demo user, select Support, SDK runtime, memory off, and create a new conversation. Ask “Why is the payout for order-2 held?” then “What delivery condition must change before that payout can be released?” Inspect the evidence and metrics: `direct_openai`, `remote_agent`, `mcp_http`, model/tool counts and confirmed investigation cleanup. The lab uses a compact dedicated prompt; it is a hosting exercise, not a quality benchmark against the full baseline.

```sh
python3 course/exercises/chapter-12-runtime-and-hosting/solutions/validate_path.py --output /tmp/ch12-results.json
```

The validator asks those two questions, checks current evidence/citations and the route, and confirms both saved runs. History remains in laptop Postgres; the cloud worker receives a bounded transcript and has no database connection. Failed requests do not append a partial turn. No mid-question checkpoint resume is implemented.

## Submit and clean up

Submit the three-component placement diagram, resource/timeout/concurrency settings, question results and route metrics. Include the cleanup confirmation; exclude keys and complete environment dumps.

```sh
python3 course/exercises/chapter-12-runtime-and-hosting/solutions/cloud_lab.py cleanup
python3 course/exercises/chapter-12-runtime-and-hosting/solutions/tunnel.py stop
docker compose -f app/compose.yaml -f app/compose.ch12.yaml --profile chapter12 stop ch12-backend ch12-frontend ch12-mcp
bash course/exercises/chapter-12-runtime-and-hosting/solutions/reset_lab.sh
```

Cleanup targets only the recorded lab service, lab secrets and image. It preserves the provider secret, shared services and fixed `market_eval`. Save your results before resetting. Never use `docker compose down -v` for this exercise.
