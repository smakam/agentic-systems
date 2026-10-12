#!/usr/bin/env bash
set -euo pipefail
compose=(docker compose -f app/compose.yaml -f app/compose.ch12.yaml --profile chapter12)
for service in ch12-backend ch12-frontend ch12-mcp; do
  if [[ -n "$("${compose[@]}" ps -q --status running "$service")" ]]; then
    echo 'Stop Chapter 12 services before resetting the disposable copy.' >&2
    exit 1
  fi
done
"${compose[@]}" exec -T postgres pg_dump -U postgres -Fc market_eval -f /tmp/ch12-baseline.dump
if ! "${compose[@]}" exec -T postgres psql -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='ch12_hosting_lab'" | grep -q 1; then
  "${compose[@]}" exec -T postgres createdb -U postgres -O market ch12_hosting_lab
fi
"${compose[@]}" exec -T postgres pg_restore -U postgres -d ch12_hosting_lab --clean --if-exists /tmp/ch12-baseline.dump
"${compose[@]}" exec -T postgres rm /tmp/ch12-baseline.dump
echo 'Reset ch12_hosting_lab from market_eval; fixed source unchanged.'
