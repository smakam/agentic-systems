#!/usr/bin/env bash
set -euo pipefail
: "${MARKETPLACE_GCP_PROJECT:?Set the intended marketplace Google project first}"
command -v gcloud >/dev/null
printf 'Destination project: %s\n' "$MARKETPLACE_GCP_PROJECT"
printf 'Paste the Marketplace support PUBLIC key: '
IFS= read -r MARKETPLACE_LF_PUBLIC_KEY
printf 'Paste the matching SECRET key (hidden): '
IFS= read -rs MARKETPLACE_LF_SECRET_KEY
printf '\n'
[[ "$MARKETPLACE_LF_PUBLIC_KEY" == pk-lf-* && "$MARKETPLACE_LF_SECRET_KEY" == sk-lf-* ]] || {
  printf 'Expected a matching Langfuse public/secret key pair; nothing stored.\n' >&2
  exit 1
}
# Values travel via stdin, not command history, argv, Terraform or source files.
for secret_name in marketplace-web-langfuse-secret marketplace-gateway-langfuse-secret; do
  printf '%s' "$MARKETPLACE_LF_SECRET_KEY" | gcloud secrets versions add "$secret_name" \
    --project="$MARKETPLACE_GCP_PROJECT" --data-file=- --quiet >/dev/null
done
unset MARKETPLACE_LF_SECRET_KEY
# The public key identifies the project; it cannot authenticate without the secret.
umask 077
printf 'LANGFUSE_HOST=https://jp.cloud.langfuse.com\nLANGFUSE_PUBLIC_KEY=%s\n' "$MARKETPLACE_LF_PUBLIC_KEY" > langfuse-public.env
printf 'Langfuse secrets stored in the two runtime-scoped secrets. Public configuration saved in langfuse-public.env.\n'
