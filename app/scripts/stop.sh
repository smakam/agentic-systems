#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ -f compose.google.local.yaml ]; then
  docker compose -f compose.yaml -f compose.memory.yaml -f compose.google.local.yaml stop
else
  docker compose -f compose.yaml -f compose.memory.yaml stop
fi
