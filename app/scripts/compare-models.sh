#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
docker compose exec -T postgres psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='market_eval'" | grep -q 1 || docker compose exec -T postgres psql -U postgres -c 'CREATE DATABASE market_eval OWNER market'
docker compose exec -T postgres psql -U postgres -d market_eval -c 'CREATE EXTENSION IF NOT EXISTS vector'
mkdir -p results
docker compose run --rm --no-deps eval-runner python -m marketplace.eval_compare "$@"
