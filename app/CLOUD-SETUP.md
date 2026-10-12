# Optional Google Cloud setup

Use this guide if you want to run the course marketplace and OpenAI Agents SDK in Google Cloud. Local setup remains sufficient for the required course path. This deployment is independent of your laptop: data, conversations, memories and credentials are not automatically synchronized.

**Status:** the existing course deployment, agent answers, retained evidence and HTTP MCP traces have been verified. The following installation sequence has not yet been rehearsed end to end in a fresh learner project. That rehearsal is deferred; do not treat this as a validated one-command installer.

## 1. Prepare accounts and tools

- Use your own billed Google Cloud project and an identity authorized to provision its resources.
- Install Git, Python 3, Docker, the Google Cloud CLI and Terraform (the repository requires Terraform 1.7 or newer, below 2.0).
- Have a funded **OpenAI API key**. The current cloud helper and gateway use OpenAI; the local OpenRouter selector does not configure cloud inference.
- Create a **Langfuse Cloud project in the Japan region** and obtain its matching public/secret key pair. The current deployment configuration uses that region. Using a different Langfuse region requires changing both runtime configuration and the frontend build URL.
- Use the [same repository](https://github.com/smakam/agentic-systems) as the local setup. Commands below start from the repository root unless a directory is specified.

Authenticate the deployment identity and Application Default Credentials with Google Cloud CLI. Select your own project. Do not use another learner's project or the instructor's service URLs as your deployment.

```sh
gcloud auth login
gcloud auth application-default login
export MARKETPLACE_GCP_PROJECT=YOUR_PROJECT_ID
export MARKETPLACE_GCP_REGION=asia-south1
gcloud config set project "$MARKETPLACE_GCP_PROJECT"
```

Cloud infrastructure, retained database storage and model requests can incur charges. Review the cloud provider's current billing information and the [deployment cost guidance](cloud/README.md#cost-boundary) before creating resources. Optional platform credits have eligibility and usage limits.

## 2. Create the infrastructure

The foundation creates private networking, PostgreSQL, databases, runtime identities, an image repository and scoped Secret Manager containers. It does not store secret payloads in Terraform variables.

First create the protected state bucket:

```sh
cd app/cloud/bootstrap
terraform init
terraform plan -var="project_id=$MARKETPLACE_GCP_PROJECT" -var="region=$MARKETPLACE_GCP_REGION" -out=bootstrap.tfplan
terraform apply bootstrap.tfplan
terraform output -raw state_bucket
```

Preserve the bootstrap state. From the repository root, initialize the main configuration using the bucket name printed above:

```sh
cd app/cloud/terraform
terraform init -backend-config="bucket=${MARKETPLACE_GCP_PROJECT}-tfstate" -backend-config='prefix=marketplace'
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`: set your project and region, and set `database_active = true` for initial creation. Leave image variables empty and optional hosted agents disabled. New instance creation in the tested deployment required the database to be active; stopping is for after setup.

```sh
terraform plan -out=foundation.tfplan
terraform apply foundation.tfplan
```

## 3. Configure private credentials

Return to the repository root. The credential helper configures database users and stores generated secrets in your project. It prompts privately for a new demo login password and the OpenAI key. Lakera is optional; leave it blank for this setup.

```sh
python3 app/cloud/scripts/configure-cloud.py --project "$MARKETPLACE_GCP_PROJECT" --region "$MARKETPLACE_GCP_REGION"
app/cloud/scripts/configure-langfuse.sh
```

The Langfuse helper requests the matching Japan-region project keys. It stores the secret key in the two runtime-scoped secrets and writes the public key/host to `langfuse-public.env`. Set the non-secret `langfuse_public_key` Terraform variable to that public key. Keep secret values out of source control, Terraform variables, command arguments and recordings.

## 4. Build the images and initialize the database

The [deployment reference](cloud/README.md#build-the-web-image-with-the-cloud-trace-link) explains the image build configuration. Use your own registry:

```sh
export MARKETPLACE_IMAGE_REPOSITORY="${MARKETPLACE_GCP_REGION}-docker.pkg.dev/${MARKETPLACE_GCP_PROJECT}/marketplace"
gcloud auth configure-docker "${MARKETPLACE_GCP_REGION}-docker.pkg.dev"
docker build --platform linux/amd64 -f app/cloud/Dockerfile.web --build-arg VITE_LANGFUSE_URL=https://jp.cloud.langfuse.com -t "$MARKETPLACE_IMAGE_REPOSITORY/web:course-setup" app
docker build --platform linux/amd64 -f app/cloud/Dockerfile.gateway -t "$MARKETPLACE_IMAGE_REPOSITORY/gateway:course-setup" app
docker push "$MARKETPLACE_IMAGE_REPOSITORY/web:course-setup"
docker push "$MARKETPLACE_IMAGE_REPOSITORY/gateway:course-setup"
```

In `app/cloud/terraform/terraform.tfvars`, set `web_image` and `gateway_image` to those pushed image references, `application_enabled = false`, and your Langfuse public key. Keep `database_active = true`. Apply a reviewed Terraform plan to create the private gateway and initialization job before enabling the application services.

From the repository root, run the explicit initialization job:

```sh
gcloud run jobs execute marketplace-initialize --project "$MARKETPLACE_GCP_PROJECT" --region "$MARKETPLACE_GCP_REGION" --wait
```

Initialization seeds the cloud databases and configures their read-only roles. It is a setup operation, not a reset to perform whenever you revisit the app. Inspect the job status before continuing.

Read the gateway URL from Terraform's `service_urls` output. Provision its scoped model keys without printing credentials:

```sh
python3 app/cloud/scripts/configure-gateway-keys.py --project "$MARKETPLACE_GCP_PROJECT" --gateway YOUR_GATEWAY_HTTPS_URL
```

## 5. Enable the application and HTTP MCP service

Set these non-secret values in `terraform.tfvars`:

- `application_enabled = true`
- `app_origin` to the intended web service origin for your project and region
- `public_web = true` for the browser-accessible course app
- `public_mcp = true` for an externally reachable MCP service **with its application API-key authentication still enforced**

The gateway remains private. Keep the optional Lyzr and Google ADK runtimes disabled for this initial SDK setup. The [Terraform service configuration](cloud/terraform/services.tf) supplies `AGENT_TOOL_TRANSPORT=mcp_http`, the project-specific MCP endpoint and its secret reference to the web runtime. Do not copy local `.env` values into the cloud application.

Apply a reviewed plan. Record the `web` and `mcp` URLs from `terraform output service_urls`; the MCP endpoint is the MCP service URL followed by `/mcp`. Record your Langfuse Cloud project URL too. These are the URLs to use in Chapters Five and Eight.

## 6. Verify access and one agent request

1. Open **your cloud marketplace web URL** and sign in as `support` or `operator` with the demo password you chose during credential setup.
2. Open the Support workspace and select **OpenAI Agents SDK**.
3. Ask: **“What products, quantities and sellers are in order-1? Retrieve current records.”**
4. Confirm that the answer completes and its evidence links open the retained records. Expect facts from your cloud data, which may differ from the laptop's modified data.
5. Use the application's Langfuse link to open **your Japan-region cloud project**, then inspect the trace associated with that question. Check model-generation and business-tool observations. Run metadata should identify HTTP MCP; a tool name alone does not establish transport.

The private LiteLLM service is accessed by authenticated runtimes; it is not a public dashboard login checkpoint. Langfuse Cloud is a hosted account, not the laptop's seeded Langfuse login. A first request after idle time may take longer while services start.

Chapter Five optionally repeats this first-agent walkthrough in the cloud. Chapter Eight compares the local stdio connection with this cloud HTTP connection. If you skip cloud setup, you can still inspect supplied remote trace evidence in Chapter Eight.

## 7. Stop and resume between labs

From the repository root:

```sh
app/cloud/scripts/database.sh status
app/cloud/scripts/database.sh stop
# Before the next cloud lab:
app/cloud/scripts/database.sh start
```

Wait until the database is ready before asking questions. Stop it only when no one is using the deployment. Set Terraform's `database_active` variable to the same intended state before your next apply so Terraform does not reverse your choice. Cloud Run minimum instances are zero in this course configuration; database storage and retained resources remain billable while stopped.

## Troubleshooting and reference

Use the [cloud setup troubleshooting](cloud/README.md#learner-setup-and-troubleshooting-requirements) for initialization, secret formats, read-only role configuration, gateway authentication and frontend trace URLs. Do not publish credentials or raw connection errors that contain them.

The [existing HTTP MCP acceptance record](cloud/VALIDATION-2026-10-10-SDK-HTTP-MCP.md) documents the tested deployed behavior. It is supporting evidence, not a substitute for the pending fresh-project installation rehearsal.
