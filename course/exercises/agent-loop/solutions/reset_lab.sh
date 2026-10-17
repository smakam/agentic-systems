#!/usr/bin/env bash
# Run from repository root, after stopping both Chapter 11 lab services.
set -euo pipefail
compose=(docker compose -f app/compose.yaml -f app/compose.ch11.yaml --profile chapter11)
for service in ch11-backend ch11-frontend; do
  if [[ -n "$("${compose[@]}" ps -q --status running "$service")" ]]; then
    echo "Stop Chapter 11 lab services before reset." >&2
    exit 1
  fi
done
"${compose[@]}" exec -T postgres pg_dump -U postgres -Fc market_eval -f /tmp/ch11-baseline.dump
if ! "${compose[@]}" exec -T postgres psql -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='ch11_loop_lab'" | grep -q 1; then
  "${compose[@]}" exec -T postgres createdb -U postgres -O market ch11_loop_lab
fi
"${compose[@]}" exec -T postgres pg_restore -U postgres -d ch11_loop_lab --clean --if-exists /tmp/ch11-baseline.dump
"${compose[@]}" exec -T postgres rm /tmp/ch11-baseline.dump
echo 'Reset ch11_loop_lab; fixed market_eval source unchanged.'
