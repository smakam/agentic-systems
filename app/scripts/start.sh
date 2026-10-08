#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; fi
# Keep the existing local Google credentials and optional test workspace when
# restarting this configured laptop. All services here still use local data.
compose() {
  if [ -f compose.google.local.yaml ]; then
    docker compose -f compose.yaml -f compose.memory.yaml -f compose.google.local.yaml "$@"
  else
    docker compose "$@"
  fi
}
compose up -d --wait postgres
compose exec -T postgres psql -v ON_ERROR_STOP=1 -U postgres < infra/ensure-litellm.sql
compose up -d --wait gateway
python3 scripts/provision-gateway-keys.py
compose up -d --build --wait --wait-timeout 240
# Nginx resolves backend container addresses at startup; refresh after rebuild.
compose restart frontend
if [ -f compose.google.local.yaml ]; then compose restart memory-frontend; fi
compose exec -T backend python -m marketplace.index || printf 'Vector indexing unavailable; configure the API key and use Index documents in the operator UI.\n'
printf '\nMarketplace: http://localhost:5178\nLangfuse: http://localhost:3000\nDemo password: demo-marketplace\n'
