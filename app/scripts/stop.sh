#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ -f compose.google.local.yaml ]; then
  docker compose -f compose.yaml -f compose.memory.yaml -f compose.google.local.yaml -f compose.ch11.yaml -f compose.ch12.yaml --profile chapter11 --profile chapter12 stop
else
  docker compose -f compose.yaml -f compose.memory.yaml -f compose.ch11.yaml -f compose.ch12.yaml --profile chapter11 --profile chapter12 stop
fi
