# Clean Linux learner rehearsal

This is an **installation rehearsal**, not the production deployment. Follow
[the learner guide](../../LOCAL-SETUP.md) from an empty Ubuntu VM and record each
check below. The VM runs the local Docker stack; it must not use the existing
Cloud SQL instance or change hosted Google/Lyzr agent settings.

## Host and prerequisites

Use Ubuntu 24.04 LTS x86-64, approximately 2 vCPU / 8 GiB RAM, and 60 GiB boot
disk for this rehearsal. These are the selected test resources, not proven
hardware minima. Keep application ports bound to loopback. Connect using SSH or
an SSH tunnel, not public demo login endpoints. Attach no runtime service
account. Restrict SSH to the operator's source address and use a disposable key.

`bootstrap-ubuntu.sh` installs Git, Python 3, Docker Engine and the Compose plugin
using [Docker's official Ubuntu apt repository](https://docs.docker.com/engine/install/ubuntu/).
It is intended only for a new disposable VM and runs as root. The `learner`
account is granted Docker access, which is effectively administrator access on
that disposable host. Reconnect SSH after bootstrap for that group to apply.

`create-vm.sh create|delete` provides the Cloud Shell/gcloud provisioning path.
Set `REHEARSAL_PROJECT`, `REHEARSAL_SSH_CIDR` and optionally zone/name/network
first. SSH as `learner` so the bootstrap can finish its account setup. Review
the script before creating resources; creation adds VM/disk/IP charges.

## Source checkpoint

Once the repository is published, clone the learner checkpoint exactly as the
guide says. Until then:

```sh
python3 app/scripts/rehearsal/pack-source.py /tmp/marketplace-learner-rehearsal.tar.gz
```

The packer includes the baseline application code, documents, Compose files,
public demo configuration, tests, evaluation inputs and setup scripts. It
excludes `.env`, Google credentials, private overlays, installed dependencies,
compiled files, historic results, Terraform state and access notes. Transfer the
archive over SSH and unpack into an empty directory. Save its SHA-256 receipt.
**This validates source installation, not GitHub clone/checkpoint publication.**

## Credentials and startup

1. Copy `.env.example` to `.env` and set mode 600, as the guide specifies.
2. Enter a learner-owned OpenAI key privately. Do not bake keys into the source
   archive, startup metadata, command arguments, receipts or logs. Reusing a
   developer key on a temporary VM requires explicit authorization first.
3. Leave optional platform keys empty for the baseline.
4. Run `./scripts/start.sh` as the guide instructs. Save the startup exit code and
   readiness checks. The script can finish with lexical fallback if embedding
   credentials fail; that is **not** a successful full RAG validation.
5. Run `python3 scripts/rehearsal/smoke.py` on the VM. This makes three paid
   question executions, checks seeded order details, a short-term follow-up,
   policy evidence and changed/persisted feedback. It writes a local receipt
   containing synthetic demo answers and trace references, without credentials.

The API smoke is a supplement to the guide's browser exercise, not proof of
browser rendering. Inspect one detailed Langfuse trace, feedback score and vector
retrieval separately. Optional memory/test-workspace checks are later learner
capabilities and should be logged individually when exercised.

## Receipt checklist

- [ ] Empty VM, OS/architecture and installed versions recorded.
- [ ] No local credentials, database snapshot or existing Docker volumes inherited.
- [ ] Source origin and hash recorded; published-clone check distinguished.
- [ ] Baseline services healthy and both marketplace/Langfuse pages reachable.
- [ ] Every policy chunk has an embedding; policy run uses vector retrieval.
- [ ] Seeded order question is grounded in SQL evidence.
- [ ] Follow-up returns total quantity 4.
- [ ] Detailed model/tool observations arrive in local Langfuse.
- [ ] Feedback persists and updates its trace score.
- [ ] Optional long-term memory/test workspace checks marked separately.
- [ ] Existing Cloud SQL remains stopped and existing hosted endpoints unchanged.
- [ ] Temporary VM, auto-delete disk, SSH firewall and private key files removed.

If credentials are unavailable, mark inference/vector/trace checks **blocked**;
report only the infrastructure and startup checks actually observed. Do not leave
billable compute running indefinitely while waiting: stop the disposable VM and
resume or delete it after deciding whether to finish the rehearsal. Retained disk
storage is still billable while stopped. Cleanup must be confirmed by cloud API
readback, not merely by submitting a delete command.
