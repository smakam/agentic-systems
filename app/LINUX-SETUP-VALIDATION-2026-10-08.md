# Fresh Linux setup rehearsal — October 8, 2026

**Partial validation.** A fresh Ubuntu VM installed and started the learner stack.
Provider-backed questions, vector retrieval, emitted agent traces and feedback
scores remain blocked on explicit approval to use an inference key on this VM.
No provider credentials were copied to it.

## Verified installation checks

| Check | Actual result |
|---|---|
| Fresh host | Ubuntu 24.04.5 LTS, x86-64; new boot disk and empty Docker volumes |
| Host size | E2 standard 2: 2 vCPU, 8 GiB memory, 60 GiB boot disk |
| Tool versions | Git 2.43.0; Python 3.12.3; Docker 29.8.2; Compose 5.6.0 |
| Source | Sanitized unpublished archive; no Git remote/clone validation |
| Startup | `./scripts/start.sh` exited successfully; nine baseline containers running |
| Health checks | Postgres, backend, Redis, ClickHouse and MinIO passed configured checks |
| API/database | Health OK; operator login succeeded; 2 seeded orders and 3 sellers |
| Persistence | Newly created SDK conversation appeared in API list and PostgreSQL |
| Frontend | HTTP 200 with root application element; no browser interaction claimed |
| Local Langfuse | Public health HTTP 200 after initial migrations |
| Provider configuration | Empty baseline `.env`; no paid model questions executed |
| RAG readiness | 20 documents, 0 indexed; explicitly lexical fallback |

Source SHA-256:
`827938fb968e3a28e257ccdc168096fe5416fbc0e1d24a57dac58169ba5ac02b`.
The included source reflects the guide available when staging occurred; later
wording changes can be staged on resume. Local secrets, ADC, hosted platform
keys, private overlays, historical result files and Terraform state were excluded.

Saved non-secret receipts: [host](results/learner-linux-2026-10-08/host.txt),
[infrastructure](results/learner-linux-2026-10-08/infrastructure.json), and
[source](results/learner-linux-2026-10-08/source.json).

## Findings for the guide

- The shared Compose startup builds both application images on a fresh Linux
  host and provisions its virtual gateway keys without any laptop-installed
  Node/Python dependencies beyond the documented small provisioning script.
- Initial Langfuse migrations continue after Compose reports running containers.
  Its first health request timed out; a subsequent request returned HTTP 200.
  Learners must wait for health/readiness, not just container existence.
- Startup's indexing fallback was observed. A zero exit from `start.sh` is not
  proof of complete inference or vector RAG readiness. Inspect `/api/readiness`.
- Observed idle/light-use service memory was approximately 3.2 GiB after startup;
  the selected 8 GiB VM had about 4 GiB available. This is not a peak or minimum.
- GCP's E2 instance requires the supported maintenance migration setting for a
  standard VM. SSH needs explicit priority rules to override inherited default
  network SSH rules; only the new VM's tag was targeted.

## Pending paid acceptance and approval boundary

The automatic approval reviewer rejected copying the developer's existing
OpenAI key to this VM because the rehearsal authorization did not explicitly
approve exporting that credential to that destination. The parent task asked
for explicit authorization or a separate lab key. No indirect transfer was used.

After authorization, resume the VM, enter only that key in its private `.env`,
rerun startup/indexing and follow sections 1–4 of
[the learner guide](LOCAL-SETUP.md). The supplemental
[smoke script](scripts/rehearsal/smoke.py) checks seeded order details,
short-term follow-up, policy evidence and persisted/changed ratings. Then verify
vector retrieval and detailed Langfuse observations/scores. Optional long-term
memory and isolated test-workspace checks are separate receipt items.

## Temporary resource status

Project: `marketplace-app-511005`. Zone: `asia-south1-a`.
VM and auto-delete boot disk: `marketplace-learner-rehearsal-20261008`.
Temporary tagged firewall rules: `marketplace-learner-rehearsal-20261008-ssh`
and `marketplace-learner-rehearsal-20261008-deny-other-ssh`.

**Stopped and verified:** cloud API readback reports `TERMINATED`, the ephemeral
external address is released, and existing Cloud SQL activation remains `NEVER`.
See the [stop receipt](results/learner-linux-2026-10-08/stop.json).
The disk is temporarily retained for resuming paid checks; storage remains
billable while compute is stopped. Delete the VM/disk and both temporary firewall
rules after acceptance, then remove the disposable SSH key files. Existing Cloud
SQL and hosted agent configurations were not changed by this rehearsal.
