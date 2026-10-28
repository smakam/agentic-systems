# Local setup validation

**Validated on a fresh Ubuntu VM on October 28, 2026.** Installation, live OpenAI-backed investigations, vector retrieval, emitted model/tool observations, feedback and stop/resume persistence passed. This validates the shared Docker application path, with the source-access and platform limits stated below.

## Environment

| Item | Observed value |
|---|---|
| Host | Ubuntu 24.04.5 LTS, x86-64, fresh boot disk and empty Docker volumes |
| Capacity | 4 vCPUs, 16 GiB RAM, 60 GB boot disk |
| Tools | Docker 29.9.2, Compose 5.6.1, Python 3.12.3 |
| Application | Published source revision `480812eb6f309b6e12089861665d9ab22c1b1aa7` |
| Source transfer | Archive of that exact Git revision; no developer `.env`, credentials, overlays, build caches or Terraform state included |
| Provider | Direct OpenAI using the configured course model and embeddings; key use explicitly authorized for this disposable VM |

The application used the documented `./scripts/start.sh`, `./scripts/stop.sh` and restart commands. Git, Python and Docker Engine were installed using the Linux prerequisite instructions and Docker's official Ubuntu repository. Docker ran as the trusted lab user. Application ports remained bound to loopback; SSH was restricted to Google's IAP proxy for this VM only. No laptop tunnel was used for the application or its tools.

## Acceptance results

All **13 acceptance checks passed**:

| Check | Result |
|---|---|
| Main API health | Healthy |
| Service access | Main/test frontends, gateway dashboard and local Langfuse returned HTTP 200 |
| Demo accounts | All six accounts logged in to both workspaces |
| Retrieval readiness | 20 of 20 documents indexed |
| Order investigation | Live answer matched the seeded products and sellers, with business evidence |
| Conversation continuity | Follow-up returned the expected total quantity |
| Policy investigation | Live answer included the required policy condition and `pgvector_cosine` document evidence |
| Feedback | Down/up changes persisted in application records |
| Workspace isolation | Main conversation was absent from the Test workspace |
| Trace ingestion | Actual model generations and business-tool observations were retained in Langfuse |
| Stop/resume persistence | Conversation, feedback and all indexed documents survived `stop.sh` followed by `start.sh` |
| Post-restart inference | Another live data-backed question completed correctly |
| Feedback telemetry | The corresponding positive `user_feedback` score remained in Langfuse after restart |

Four paid agent questions were exercised. No claim is made that finishing a run alone proves quality: the checks compared seeded facts, follow-up arithmetic, policy conditions and retrieved evidence. The retained trace contained 18 observations, including `generation`, `get_catalog` and `query_business_data`.

The non-secret [machine-readable receipt](docs/local-setup-validation.json) records the checks, revision, run references and cleanup state. Detailed synthetic run outputs and startup logs are retained in the course authoring workspace.

## Findings and limits

- **GitHub authentication/clone was not exercised.** The repository was private and the remote environment had no GitHub login. An archive of the exact published revision was used rather than exporting a GitHub credential. This limitation concerns source download; the application installation and live acceptance checks passed.
- **Full browser interaction was not independently exercised.** Frontend HTTP availability and authenticated application APIs were checked. The existing laptop stack was left running and untouched.
- **Mac fresh installation and Windows/WSL2 remain untested.** This Linux result does not establish platform-specific installer compatibility. The configured OpenAI path passed; fresh OpenRouter acceptance remains untested.
- The acceptance runner initially reached the API before the frontend was ready. Its readiness wait was corrected; no application change was required.
- Trace/score verification used current Langfuse APIs: Observations v2 and Scores v3 with score `subject` fields. Legacy observation reads returned 404 for this deployment. See [Langfuse API compatibility](https://langfuse.com/docs/api-and-data-platform/features/public-api) and [Scores v3](https://langfuse.com/changelog/2026-06-10-scores-v3-api). These were validation-runner corrections, not application deployment changes.

## Cleanup

The temporary VM, its boot disk and the two test-specific SSH firewall rules were removed after retaining the results. Deleting the disk removed the temporary provider-key copy, generated gateway credentials and synthetic test data. The pre-existing Marketplace application and managed agent were not changed. Existing Cloud SQL remained `STOPPED` with activation policy `NEVER`.

The older stopped rehearsal VM was not reused or modified. This report replaces the earlier partial-installation report; its history remains in Git.
