#!/usr/bin/env bash
# Run from repository root. Touch only the disposable Chapter 10 destination.
set -euo pipefail
compose=(docker compose -f app/compose.yaml)
"${compose[@]}" exec -T postgres pg_dump -U postgres -Fc market_eval -f /tmp/ch10-fixed-baseline.dump
if ! "${compose[@]}" exec -T postgres psql -U postgres -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname='ch10_session_lab'" | grep -q 1; then
  "${compose[@]}" exec -T postgres createdb -U postgres -O market ch10_session_lab
fi
"${compose[@]}" exec -T postgres pg_restore -U postgres -d ch10_session_lab --clean --if-exists /tmp/ch10-fixed-baseline.dump
"${compose[@]}" exec -T postgres rm /tmp/ch10-fixed-baseline.dump
echo 'Reset ch10_session_lab from fixed market_eval; source database unchanged.'
