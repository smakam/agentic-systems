# Setup guide: deploy Support Agent Basics

This guide creates a **separate Google-managed agent** using the course's fictional JSON orders and native `lookup_order` tool. No marketplace UI, MCP server, SQL database or tunnel is needed. Use your own authorized Google Cloud project, or the instructor's already-created deployment for observation only.

The instructor deployment has been created and its Playground lookup, follow-up, missing-record behavior and native traces checked. Memory generation and scoped stored-preference search have also passed. Fresh-session preference preload and answer use were subsequently verified in a completed native trace after the CLI retry timed out. The sequence below is not a claim that a fresh learner project has already been rehearsed end to end.

## Prerequisites — prepare once

- A Google Cloud project with billing enabled and access to the configured model. Use Cloud Shell, authorize its project access, and have Python 3.12 available.
- Permission to enable APIs, create/deploy an agent, upload staging objects and attach the runtime service account. The deployer needs Service Account User on that runtime identity; do not grant broad project Owner merely to follow the lesson.
- Enabled APIs: Agent Platform/AI Platform (`aiplatform.googleapis.com`), Resource Manager, Telemetry, Cloud Trace, Logging and Monitoring.
- A dedicated runtime service account with model/runtime access (Vertex AI User), Logs Writer, Cloud Trace Agent and Monitoring Metric Writer for this lab, plus Storage Object Viewer scoped to the staging bucket.
- A private staging bucket, and permission for the deployer to write its staging objects. Ask your administrator to prepare these resources if you cannot create/grant them yourself.

The deployment script does **not** enable APIs, create the bucket/identity or grant IAM roles. These are actual prerequisites, not hidden work. No MCP secret or external memory-provider key is required for Basics. Native model/runtime/state/telemetry usage can incur charges; exact rates and quotas vary.

### Edit these values for your environment

In Cloud Shell, replace the project, bucket and service-account examples. Keep the tested model/runtime locations unless intentionally investigating another supported configuration: the model endpoint is distinct from the runtime/session region.

```bash
export GOOGLE_CLOUD_PROJECT='YOUR_PROJECT_ID'
export GOOGLE_CLOUD_LOCATION='us-central1'
export GOOGLE_STAGING_BUCKET='gs://YOUR_UNIQUE_STAGING_BUCKET'
export GOOGLE_RUNTIME_SERVICE_ACCOUNT='support-basics-runtime@YOUR_PROJECT_ID.iam.gserviceaccount.com'
export GOOGLE_AGENT_MODEL='gemini-3.5-flash'
export GOOGLE_MODEL_LOCATION='us'
export GOOGLE_MEMORY_ENABLED='true'

gcloud config set project "$GOOGLE_CLOUD_PROJECT"
```

These are configuration values, not API secrets. Do not copy the instructor's resource names into your own project. Confirm billing and the permissions above before deployment.

### If the project has not been prepared

An authorized administrator can enable the required APIs:

```bash
gcloud services enable \
  aiplatform.googleapis.com cloudresourcemanager.googleapis.com \
  telemetry.googleapis.com cloudtrace.googleapis.com \
  logging.googleapis.com monitoring.googleapis.com
```

Create the dedicated service account and private staging bucket if they do not exist, then grant the scoped permissions listed above. The account name in `GOOGLE_RUNTIME_SERVICE_ACCOUNT` must match the identity actually created. Use the current [runtime permission documentation](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/use-terraform) and [telemetry setup documentation](https://docs.cloud.google.com/stackdriver/docs/instrumentation/setup/go) to review the exact access needed in your organization. Do not rerun resource creation blindly in an already prepared course project.

## Get the code and install

Use your existing course checkout, or clone the public repository into a fresh directory:

```bash
git clone https://github.com/smakam/agentic-systems.git
cd agentic-systems/app/google/basics
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

If the checkout or virtual environment already exists, enter/activate it rather than cloning or creating it again. The [technical README](../../../app/google/basics/README.md), [full agent instructions](../../../app/google/basics/support_agent_basics/instructions.txt) and [fictional fixture](../../../app/google/basics/support_agent_basics/orders.json) are adjacent to the code.

## Two main commands after setup

From `app/google/basics` with the environment above active:

```bash
python -m unittest -v test_basics.py
python deploy.py
```

The tests do not require paid model calls. Deployment creates **Support Agent Basics** and writes **support-basics-deployment.json**. The script does not update/delete the existing Marketplace Support ADK Lab and ignores its old runtime resource variable. It refuses a second creation when the Basics manifest exists. If a create response is uncertain, inspect the console and resources before retrying; do not remove the guard file to force another deployment.

## Open Playground and verify

1. In your selected project open **Agent Platform → Agents → Scale → Deployments → Support Agent Basics → Playground**. Use your new deployment's resource, not an older lab with a similar name.
2. Start a fresh session and ask **“What products and quantities are in order-demo-1?”** The fictional source has **2 × Ceramic Mug Set**; inspect the `lookup_order` input/result and native trace.
3. In the same session ask **“What is its payout status?”** The source says **held**, while buyer payment is **received**. Check the retained order context and lookup evidence.
4. Ask about **order-demo-999** and verify that a missing fixture record is not invented.
5. Follow [instructor-demo.md](instructor-demo.md) for the walkthrough and separate Memory Bank generation/recall checks. A correct answer or current-session preference is not proof of persisted memory.

For the instructor's authorized observation environment, the verified [Support Agent Basics Playground](https://console.cloud.google.com/agent-platform/runtimes/locations/us-central1/agent-engines/2782635506360385536/playground?project=customer-support-agent-510915) opens the existing resource. This link does not grant access and is not a resource to modify for learner deployment.

## Cleanup

Keep the instructor resources intact. When your own lab is no longer needed, remove only its runtime, synthetic session/memory artifacts, dedicated identity and unused staging objects using the current platform controls. Do not delete a shared project, identity or bucket. Confirm remaining billable resources. The course deployment script intentionally contains no deletion operation.
