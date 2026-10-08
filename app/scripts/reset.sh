#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ "${1:-}" != '--confirm-demo-reset' ]; then
  printf 'This removes marketplace changes, logins, documents, and conversations. Langfuse traces remain.\nRun with --confirm-demo-reset to continue.\n'
  exit 1
fi
docker compose stop backend
docker compose run --rm --no-deps backend python -m marketplace.reset --confirm-demo-reset
docker compose start backend
printf 'Demo reset. Sign in again and reindex documents.\n'
