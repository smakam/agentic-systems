#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
# This suite exclusively owns disposable market_test while it is running.
# Do not run concurrently with scripts/test.sh or other market_test experiments.
docker compose exec -T postgres psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='market_test'" | grep -q 1 || docker compose exec -T postgres psql -U postgres -c 'CREATE DATABASE market_test OWNER market'
docker compose exec -T postgres psql -U postgres -d market_test -c 'CREATE EXTENSION IF NOT EXISTS vector'
docker compose run --rm --no-deps -e PYTHONPATH=/app \
  -e DATABASE_URL=postgresql+psycopg://market:market-local@postgres:5432/market_test \
  -e READ_DATABASE_URL=postgresql://agent_reader:reader-local@postgres:5432/market_test \
  -v "$PWD/scripts:/scripts:ro" eval-runner python /scripts/memory-repeatable.py "$@"
