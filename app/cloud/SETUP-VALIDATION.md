# Two-project cloud setup validation

Validated on October 28, 2026 in fresh, billing-enabled projects `marketplace-test-513014` (asia-south1) and `agent-test-513015` (us-central1).

**Result: the baseline deployment and live acceptance passed after corrections and resumptions.** This was a fresh-project rehearsal, not a claim that the original installer passed unchanged on its first attempt. The original course deployment was not modified. Use the [Cloud Setup guide](../CLOUD-SETUP.md) for learner instructions.

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
- saved SDK and Google conversations survive database stop and resume.
- saved feedback survives database stop and resume.
- live data-backed answer works after database restart.
- Google managed agent remains data-backed after database restart.
- Google Cloud Trace retains native model and Marketplace business-tool spans.

## Corrections made during the rehearsal

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

The [machine-readable receipt](setup-validation.json) records checks and trace/session references. Secrets, private credential files, Terraform state and raw trace payloads are excluded. SDK and Google answers were checked against seeded Marketplace records, with actual HTTP MCP evidence and retained traces. Database stop/resume was verified with saved conversations, feedback and new data-backed questions.

This run used the published wrapper with reviewed maintainer recoveries after failures. It did not repeat the entire corrected installer in a second new project pair. It used macOS deployment tooling; Cloud Shell and organization policy variations were not rehearsed. Optional external guardrails were not enabled. The [Linux local validation](../LINUX-SETUP-VALIDATION.md) is a separate acceptance record.
