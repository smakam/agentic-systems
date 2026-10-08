#!/bin/sh
# Run from Cloud Shell or a gcloud-equipped operator machine. Creates billable resources.
set -eu
: "${REHEARSAL_PROJECT:?Set the dedicated authorized GCP project}"
: "${REHEARSAL_SSH_CIDR:?Set your current public address with /32}"
REHEARSAL_ZONE=${REHEARSAL_ZONE:-asia-south1-a}
REHEARSAL_NAME=${REHEARSAL_NAME:-marketplace-learner-rehearsal}
REHEARSAL_NETWORK=${REHEARSAL_NETWORK:-default}
case "${1:-}" in
  create)
    gcloud compute firewall-rules create "${REHEARSAL_NAME}-ssh" \
      --project="$REHEARSAL_PROJECT" --network="$REHEARSAL_NETWORK" \
      --priority=900 --allow=tcp:22 --source-ranges="$REHEARSAL_SSH_CIDR" --target-tags="$REHEARSAL_NAME"
    gcloud compute firewall-rules create "${REHEARSAL_NAME}-deny-other-ssh" \
      --project="$REHEARSAL_PROJECT" --network="$REHEARSAL_NETWORK" \
      --priority=901 --deny=tcp:22 --source-ranges=0.0.0.0/0 --target-tags="$REHEARSAL_NAME"
    gcloud compute instances create "$REHEARSAL_NAME" \
      --project="$REHEARSAL_PROJECT" --zone="$REHEARSAL_ZONE" \
      --machine-type=e2-standard-2 --image-family=ubuntu-2404-lts-amd64 --image-project=ubuntu-os-cloud \
      --boot-disk-size=60GB --boot-disk-type=pd-standard --boot-disk-auto-delete \
      --network="$REHEARSAL_NETWORK" --tags="$REHEARSAL_NAME" \
      --no-service-account --no-scopes --no-restart-on-failure \
      --metadata=enable-oslogin=FALSE,block-project-ssh-keys=TRUE \
      --metadata-from-file="startup-script=$(dirname "$0")/bootstrap-ubuntu.sh"
    printf 'SSH as learner so the bootstrap can grant its disposable Docker group access.\n'
    ;;
  delete)
    gcloud compute instances delete "$REHEARSAL_NAME" --project="$REHEARSAL_PROJECT" --zone="$REHEARSAL_ZONE" --quiet
    gcloud compute firewall-rules delete "${REHEARSAL_NAME}-ssh" --project="$REHEARSAL_PROJECT" --quiet
    gcloud compute firewall-rules delete "${REHEARSAL_NAME}-deny-other-ssh" --project="$REHEARSAL_PROJECT" --quiet
    ;;
  *) printf 'Usage: create-vm.sh create|delete\n' >&2; exit 2 ;;
esac
