#!/usr/bin/env bash
set -euo pipefail
: "${MARKETPLACE_GCP_PROJECT:?Set MARKETPLACE_GCP_PROJECT to the dedicated marketplace project}"
instance="${MARKETPLACE_SQL_INSTANCE:-marketplace-postgres}"
case "${1:-}" in
  start) policy=ALWAYS ;;
  stop) policy=NEVER ;;
  status) exec gcloud sql instances describe "$instance" --project="$MARKETPLACE_GCP_PROJECT" --format='yaml(state,settings.activationPolicy,settings.tier,settings.dataDiskSizeGb)' ;;
  *) printf '%s\n' 'Usage: database.sh start|stop|status' >&2; exit 2 ;;
esac
gcloud sql instances patch "$instance" --project="$MARKETPLACE_GCP_PROJECT" --activation-policy="$policy" --quiet
gcloud sql instances describe "$instance" --project="$MARKETPLACE_GCP_PROJECT" --format='yaml(state,settings.activationPolicy)'
