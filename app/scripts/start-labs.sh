#!/bin/sh
# Start existing course lab UIs; initialize missing/empty lab databases only.
set -eu
export COMPOSE_IGNORE_ORPHANS=true
cd "$(dirname "$0")/.."
compose() {
  docker compose -f compose.yaml -f compose.ch11.yaml -f compose.ch12.yaml --profile chapter11 --profile chapter12 "$@"
}
new_backends=""
for pair in ch11_loop_lab:ch11-backend ch12_hosting_lab:ch12-backend; do
  database=${pair%:*}
  backend=${pair#*:}
  exists=$(compose exec -T postgres psql -v ON_ERROR_STOP=1 -U postgres -Atc "SELECT count(*) FROM pg_database WHERE datname='$database'")
  if [ "$exists" = 0 ]; then
    compose exec -T postgres createdb -U postgres -O market "$database"
  fi
  state_table=$(compose exec -T postgres psql -v ON_ERROR_STOP=1 -U postgres -d "$database" -Atc "SELECT to_regclass('public.state')")
  seeded=0
  if [ -n "$state_table" ]; then
    seeded=$(compose exec -T postgres psql -v ON_ERROR_STOP=1 -U postgres -d "$database" -Atc 'SELECT count(*) FROM public.state WHERE id=1')
  fi
  if [ "$seeded" = 0 ]; then
    compose run --rm --no-deps -T "$backend" python -c "from marketplace.db import engine,init_schema,Session; from marketplace.seed import seed; assert engine.url.database == '$database'; init_schema(); db=Session(); seed(db); db.commit(); db.close()"
    new_backends="$new_backends $backend"
  fi
done
# Use the frontend image built by normal startup; no host npm/build step needed.
compose up -d --no-deps --wait --wait-timeout 240 ch11-backend ch11-frontend ch12-backend ch12-frontend
compose restart ch11-frontend ch12-frontend
# Start HTTP MCP only when its existing authentication configuration is ready.
if python3 - <<'CHECK_CONFIG'
from pathlib import Path
p=Path('.ch12.env')
values={}
if p.exists():
    for line in p.read_text().splitlines():
        if '=' in line and not line.lstrip().startswith('#'):
            name,value=line.split('=',1);values[name.strip()]=value.strip().strip('"').strip("'")
raise SystemExit(0 if len(values.get('REMOTE_MCP_API_KEY','')) >= 32 else 1)
CHECK_CONFIG
then
  compose up -d --no-deps ch12-mcp
else
  printf 'Legacy hosting UI is available; the current deployment worksheet uses the standard test marketplace.\n'
fi
for backend in $new_backends; do
  compose exec -T "$backend" python -m marketplace.index || printf 'Lab vector indexing unavailable; configure the gateway and use Index documents in that lab UI.\n'
done
printf 'Agent Loop lab: http://localhost:5181\nRuntime and Hosting lab: http://localhost:5192\nExisting lab data preserved; no seed reset or cloud deployment performed.\n'
