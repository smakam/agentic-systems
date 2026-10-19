#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ ! -f .env ]; then cp .env.example .env; fi
python3 scripts/configure-inference.py
export LITELLM_CONFIG_PATH=./infra/litellm.provider.generated.yaml
# Keep the existing local Google credentials and optional test workspace when
# restarting this configured laptop. All services here still use local data.
compose() {
  if [ -f compose.google.local.yaml ]; then
    docker compose -f compose.yaml -f compose.memory.yaml -f compose.google.local.yaml "$@"
  else
    docker compose -f compose.yaml -f compose.memory.yaml "$@"
  fi
}
compose up -d --wait postgres
# Bootstrap the test database without resetting an existing workspace.
if [ "$(compose exec -T postgres psql -v ON_ERROR_STOP=1 -U postgres -Atc "SELECT count(*) FROM pg_database WHERE datname='market_test'")" = "0" ]; then
  compose exec -T postgres psql -v ON_ERROR_STOP=1 -U postgres -c 'CREATE DATABASE market_test OWNER market'
fi
compose exec -T postgres psql -v ON_ERROR_STOP=1 -U postgres -d market_test -c 'CREATE EXTENSION IF NOT EXISTS vector'
compose exec -T postgres psql -v ON_ERROR_STOP=1 -U postgres < infra/ensure-litellm.sql
compose up -d --wait --force-recreate gateway
python3 scripts/provision-gateway-keys.py
compose up -d --build --wait --wait-timeout 240
# Nginx resolves backend container addresses at startup; refresh after rebuild.
compose restart frontend
compose restart memory-frontend
./scripts/start-labs.sh
printf '\nMarketplace: http://localhost:5178\nTest workspace: http://127.0.0.1:5179\nLangfuse: http://localhost:3000\nDemo password: demo-marketplace\n'
