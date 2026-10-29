# Two-project cloud setup validation

**Result: the corrected installer passed a clean reinstall on October 29, 2026 in one uninterrupted invocation.** Both SDK and Google agents then passed live acceptance and database restart checks. Use the [Cloud Setup guide](../CLOUD-SETUP.md) for learner instructions.

## Clean reinstall

The course resources were removed from `marketplace-test-513014` (asia-south1) and `agent-test-513015` (us-central1), keeping their project IDs and billing. Before setup, API inventories confirmed no Cloud Run services, Cloud SQL instances, secrets, Artifact Registry repositories or managed agents remained. A fresh GitHub clone at revision `62d88654edab35a567a1240ba27ac37ab1aee9b9` was used without old setup checkpoints.

The published `python3 app/cloud/scripts/setup.py --deploy` command completed all **13 phases in one invocation**, taking approximately 16 minutes. Normal configuration and credential prompts were answered; no code edits, checkpoint skips, manual deployment repairs or installer restarts were needed. Live acceptance was a separate step, as the guide requires. The first Google question allowed the documented IAM propagation interval.

The first rehearsal on October 28 used fresh projects and passed after corrections and resumptions. Those fixes were published before this clean repeat; this result does not rewrite the first attempt as an unchanged success.

## Verified behavior

- cloud web and database health.
- all six demo accounts authenticate.
- all cloud documents indexed.
- SDK answer matches seeded records and uses HTTP MCP.
- SDK conversation follow-up.
- SDK policy answer has vector evidence.
- cloud feedback persists.
- Langfuse Cloud retains SDK model and tool observations.
- Google runtime discovered by Marketplace.
- Google agent retrieves real Marketplace evidence over MCP.
- Google native session retained across follow-up.
- Google conversation and runs persist in Marketplace.
- Google Cloud Trace retains native model and Marketplace business-tool spans.
- saved SDK and Google conversations survive database stop and resume.
- saved feedback survives database stop and resume.
- live data-backed answer works after database restart.
- Google managed agent remains data-backed after database restart.

## Corrections from the first rehearsal

| Gap found | Published correction |
|---|---|
| Frontend used the local tracing project identifier | Discover the authenticated Langfuse Cloud project during credential setup and include its ID in the frontend build. |
| Unconfigured external gateway guardrails blocked startup | Omit only optional hooks whose dependencies are absent; keep built-in hooks and fail closed for partially configured required integrations. |
| Computed service URLs remained empty after failed resource creation | Refresh Terraform outputs without changing resources, then fail closed if a URL is still missing. |
| Restricted runtime user could not initialize the embedding cache | Create it under the initializer identity and grant only runtime DML access. |
| Cloud IAM auth used an incompatible HTTP client family | Match the pinned OpenAI SDK HTTP transport. Local Compose does not exercise Cloud Run IAM authentication. |
| gcloud beta installation prompt was hidden by captured output | Generate the service identity through the official REST API and poll completion. |
| Google rejected a cross-project injected secret | Privately provision a versioned agent-project secret with scoped runtime access; no secret values in Terraform state or command arguments. |
| Secret version listing used an unsupported CLI option | Pass the secret name positionally. |
| First query preceded IAM propagation | Document the brief propagation delay; subsequent real tool calls and follow-up succeeded without broadening the scoped query role. |
| Native traces lacked the required ingestion API | Enable Telemetry API as part of agent foundation, in addition to Cloud Trace. |

## Evidence and limits

The [machine-readable receipt](setup-validation.json) records the source revision, installer phases and retained trace/session references. Secrets, private credential files, Terraform state and raw trace payloads are excluded. Answers were compared with seeded Marketplace facts and actual HTTP MCP evidence. Native Google model/tool spans and the managed session were read back from Google APIs. The read-only trace verifier was corrected to follow pagination, including empty pages with continuation tokens; this required no installer or application change. Saved conversations and feedback survived Cloud SQL stop/resume; new data-backed SDK and Google questions also passed afterward.

This was a clean reinstall in reused projects, not another brand-new project pair: enabled APIs, Google-managed service identities and the default project network remained. Deployment tooling ran on macOS. Cloud Shell, Windows and organization policy variants were not rehearsed; optional external guardrails were not enabled. Application APIs and frontend HTTP availability were checked; independent browser interaction was not part of this repeat. The [Linux local validation](../LINUX-SETUP-VALIDATION.md) is a separate acceptance record.

## Final environment state

After acceptance, test Cloud SQL was confirmed **STOPPED/NEVER**. Test data and both deployments remain for review; storage and other retained resources can still incur charges. Start the test database before using that application.

The original course deployment was excluded from test teardown. Its Cloud SQL is **RUNNABLE/ALWAYS**, started at the instructor's request, and its web health is healthy. The existing local Docker application was also restored after Docker Desktop's upgrade, preserving its data.
