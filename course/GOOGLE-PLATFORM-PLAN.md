# Optional Google full-cloud marketplace integration

**Complete [app/CLOUD-SETUP.md](../app/CLOUD-SETUP.md) first.** This extension is for learners who already have their own working cloud marketplace chat/backend, authenticated business MCP service and database/policy store. This guide connects that stack to a Google-hosted marketplace agent; it does not repeat cloud provisioning.

The required Chapter 19 lesson is the separate [Support Agent Basics setup](exercises/chapter-19-google-agent-platform/setup-guide.md), using fictional JSON and native tools in Google Playground. Basics has no business MCP tools: pointing its configuration at an MCP URL does not turn it into the marketplace agent. For this optional extension, deploy the **marketplace ADK code in `app/google`**, or use your own existing compatible marketplace ADK deployment. Preserve both instructor deployments.

## Before you start

Confirm these three prerequisites:

1. Your cloud marketplace is working under the completed Cloud Setup guide, and you know its Cloud Run MCP URL and its Secret Manager MCP-key reference. Do not copy the key into source, prompts or screenshots.
2. You have a billing-enabled Google agent project, an authorized Cloud Shell session, a runtime service account and private staging bucket. Enable Agent Platform, Resource Manager, Secret Manager and required telemetry APIs in that project. The runtime identity needs Vertex AI User and telemetry writer permissions, Storage Object Viewer on its staging bucket, and Secret Accessor on its one MCP secret. Provisioning permissions belong to your authenticated deployer.
3. Decide whether you will **create your own marketplace ADK runtime** or **update your own already compatible marketplace ADK runtime**. A Basics runtime is not compatible. Use your own project and resource names; instructor resources are not values to copy.

## 1. Prepare the agent code and your configuration

In Cloud Shell, clone your course repository or upload its `app/google` directory. Work in that directory, not `app/google/basics`:

```bash
cd YOUR_COURSE_REPOSITORY/app/google
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m unittest test_agent -v

export GOOGLE_GENAI_USE_ENTERPRISE=TRUE
export GOOGLE_CLOUD_PROJECT=YOUR_AGENT_PROJECT_ID
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_STAGING_BUCKET=gs://YOUR_PRIVATE_AGENT_STAGING_BUCKET
export GOOGLE_RUNTIME_SERVICE_ACCOUNT=YOUR_AGENT_RUNTIME_SERVICE_ACCOUNT_EMAIL
export GOOGLE_AGENT_MODEL=gemini-3.5-flash
export GOOGLE_MODEL_LOCATION=us
export GOOGLE_MEMORY_ENABLED=true
export REMOTE_MCP_URL=https://YOUR_CLOUD_MCP_HOST/mcp
export GOOGLE_MCP_SECRET=projects/YOUR_AGENT_PROJECT_ID/secrets/YOUR_AGENT_MCP_SECRET
export GOOGLE_MCP_SECRET_VERSION=YOUR_NUMERIC_SECRET_VERSION
```

Use a model and endpoint available to your project. Runtime/session region and model endpoint are separate settings. These values are references, not secret payloads. The deployed agent reads the MCP key from Secret Manager at runtime. Its URL must address your working business service.

## 2. Make the MCP credential available to the runtime

Use your Cloud Setup MCP key, not a newly generated unrelated key. If the agent shares the business project's secret, point `GOOGLE_MCP_SECRET` at that existing secret and grant the agent runtime identity access to that secret only. If you use a separate agent-project secret, copy the existing key directly between Secret Manager services with an authorized deployer; do not print it:

```bash
# Only for a separate secret you create in your agent project:
gcloud secrets create YOUR_AGENT_MCP_SECRET --project "$GOOGLE_CLOUD_PROJECT" --replication-policy=automatic
gcloud secrets versions access YOUR_BUSINESS_MCP_SECRET_VERSION --secret=YOUR_BUSINESS_MCP_SECRET --project=YOUR_BUSINESS_PROJECT_ID | gcloud secrets versions add YOUR_AGENT_MCP_SECRET --project "$GOOGLE_CLOUD_PROJECT" --data-file=-
```

Record the new numeric version and set `GOOGLE_MCP_SECRET_VERSION` accordingly. Grant `roles/secretmanager.secretAccessor` on the chosen secret to the runtime service account. Do not replace a shared key or grant access to all project secrets. The business MCP enforces its application key; verify any additional Cloud Run access policy against Cloud Setup before continuing.

## 3. Create or update your marketplace ADK runtime

**New runtime:** remove any inherited runtime target and create without a profile flag. Your direct URL/secret settings from steps 1–2 supply the cloud business connection:

```bash
unset GOOGLE_RUNTIME_RESOURCE
python deploy.py
```

`deploy.py` creates a new marketplace ADK deployment and writes its resource name, URL and secret reference to `deployment.json`. The code's display name is Marketplace Support ADK Lab; distinguish your resource by project and returned resource ID. If creation fails or times out, inspect your project's runtime list before retrying; do not blindly create duplicates.

**Existing compatible runtime you own:** use its resource ID to update with the same direct settings:

```bash
export GOOGLE_RUNTIME_RESOURCE=projects/YOUR_AGENT_PROJECT_NUMBER/locations/YOUR_RUNTIME_REGION/reasoningEngines/YOUR_RUNTIME_ID
python deploy.py
```

The optional `--backend cloud|local` flag is **update only** and requires `GOOGLE_RUNTIME_RESOURCE`. It reads saved `backend_profiles.json`, whose checked-in values identify instructor endpoints/secrets. Do not use those profiles for your own project unless you first replace them with your own non-secret references. A marketplace UI runtime selection never changes an agent's MCP target.

## 4. Verify the agent before connecting chat

Read `deployment.json`; confirm its resource belongs to your project and its MCP URL/secret reference match your cloud stack. Open that deployment in Google Playground, start a fresh session and ask “Show the items and quantities for order-2.” Inspect actual business tool calls and returned evidence. Then ask “What is their total quantity?” in the same session and inspect retained context. Use your own fixture's expected values.

If startup or tools fail, inspect the deployment logs, runtime identity, secret version and endpoint before proceeding. A displayed deployment is not proof that authenticated tools work. Native Sessions and Traces are separate surfaces; allow trace ingestion time.

## 5. Connect your cloud marketplace backend

After the hosted marketplace agent works, edit the existing `app/cloud/terraform/terraform.tfvars` from your completed Cloud Setup:

```hcl
google_runtime_project_id = "YOUR_AGENT_PROJECT_ID"
google_runtime_resource   = "projects/YOUR_AGENT_PROJECT_NUMBER/locations/YOUR_RUNTIME_REGION/reasoningEngines/YOUR_RUNTIME_ID"
```

Preserve your other cloud settings and image references. From `app/cloud/terraform`, review and apply the connection change:

```bash
terraform plan -out=google-integration.tfplan
terraform apply google-integration.tfplan
```

The existing Terraform code injects `GOOGLE_RUNTIME_RESOURCE` into the **web backend** and grants its Cloud Run service identity the custom `aiplatform.reasoningEngines.query` permission in the agent project. This project-level query permission is not a per-user session boundary; the backend binds authenticated users to platform identities. It grants no deployment/admin permission. All credentials stay in the backend; no frontend API key or ADC file is required. The existing UI discovers available runtimes from the backend, so no frontend build variable selects the Google resource. See [runtime configuration](../app/RUNTIME-SELECTOR.md#configuration).

## 6. Verify end to end and record what you observed

Open **your cloud marketplace URL**, select **Google hosted runtime**, and start a fresh conversation. Repeat the order-2 question and same-chat quantity follow-up. Check your business tool evidence, native session/trace and application-boundary trace if Langfuse is configured. The managed agent, cloud business tools and chat backend are distinct components; choosing Google in chat changes the execution adapter, not the database or MCP endpoint.

Record the project/resource references, tool results, session continuity, trace links, failures and actual costs you inspect. Do not submit secrets. Complete the [optional exercise observation table](exercises/chapter-19-google-agent-platform/exercise.md#what-to-document). The instructor's historical integration passed, but these instructions have not been rehearsed from scratch in a fresh learner project.

For cleanup, remove only resources you created and verify remaining billable services. Keep the standalone Basics and instructor resources intact. The laptop/tunnel configuration is an optional historical alternative, not required for this full-cloud path.
