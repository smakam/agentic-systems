# Shared marketplace cloud deployment

Learners: start with the ordered [optional cloud setup guide](../CLOUD-SETUP.md). This file contains deployment references and validation history.

[Access reference: local/cloud URLs, users and credential locations](../.access-reference.md).
Core cloud deployment verified October 8, 2026. The marketplace web application, authenticated HTTP MCP middleware and private LiteLLM gateway run in `marketplace-app-511005`, backed by private Cloud SQL PostgreSQL and Secret Manager. Langfuse Cloud Japan receives traces and feedback. No laptop or tunnel is required for these services. Cloud SQL is now parked with activation policy NEVER; restart it before cloud use. Storage and retained backups remain billable, and public IPv4 remains disabled. A fresh-project learner rehearsal remains separate work; hosted-platform connections are verified.

See the [reviewed architecture](../../course/MARKETPLACE-DEPLOYMENT-ARCHITECTURE.md). This directory preserves the local Compose setup.

## Verified deployment checkpoint — October 8, 2026

**SDK HTTP update — October 10:** Source/configuration now selects `AGENT_TOOL_TRANSPORT=mcp_http` for web, with `SDK_MCP_URL` targeting the separate Cloud Run `/mcp` endpoint and `SDK_MCP_API_KEY` referencing the existing MCP secret. Web receives access to that secret; local Compose remains stdio. Thirteen isolated HTTP protocol/lifecycle tests and Terraform validation passed. Cloud web revision `marketplace-web-00015-8lb` is deployed and ready; a live question and fresh-retrieval follow-up passed with retained evidence and detailed Langfuse tool/model observations. Cloud SQL is confirmed `NEVER`, `STOPPED` after validation. See [the acceptance record](VALIDATION-2026-10-10-SDK-HTTP-MCP.md). Use its immutable web image on the next Terraform deployment; the October 8 image below is historical.

- **Foundation created:** protected Terraform state bucket, private networking, image repository, runtime identities and scoped secret containers. Cloud SQL `marketplace-postgres` contains `market`, `market_test`, `market_eval` and `litellm`; it was stopped between setup phases, then started successfully for initialization (`RUNNABLE`, `activationPolicy=ALWAYS`), with public IPv4 disabled.
- **Langfuse credentials verified:** the Marketplace support project in Japan has matching keys stored in `marketplace-web-langfuse-secret` and `marketplace-gateway-langfuse-secret`, version 1 enabled for each. API authentication against the intended project passed; no secret values are recorded here.
- **Images published:** web `course-20261008-r4` (digest `sha256:cf464b7994351c8ed6a40c7fc7f86736aceaebcaa9bdb9685a1cb52250a66363`) and the pinned gateway r2 image. Terraform deployed all three services with no deletions.
- **Cloud acceptance passed:** initialization rerun, operator/support login, 20-document vector indexing, correct held payout answer with SQL/RAG evidence, short-term history, explicit memory save and fresh-conversation recall, feedback persistence/export, built-in email masking and Lakera blocking. The separate HTTP MCP service passed begin/read/end across separate requests. Langfuse readback found model/tool spans and gateway input observations; the privacy observation contained the redaction marker and no original synthetic email. See [verification record](VALIDATION-2026-10-08.md).
- **Learner setup:** [Local laptop guide](../LOCAL-SETUP.md) is written and configuration checks passed. A clean-machine install and publication of the learner repository remain unverified. Shared-interface adapters are implemented; see the runtime selector validation below.

## Foundation

`terraform/` creates service APIs, an image repository, runtime identities including a dedicated initializer, private network/subnet/Private Services Access, private-only PostgreSQL, separate databases and scoped secret access. It deliberately has no secret payloads or database passwords. `database_active` defaults to false. Cloud Run deployments follow only after image packaging and the persistence/telemetry gates in the architecture are implemented.

Use a separately bootstrapped private GCS state bucket, authenticate as the deployment operator, and initialize:

```sh
cd app/cloud/terraform
terraform init -backend-config='bucket=YOUR_PRIVATE_STATE_BUCKET' -backend-config='prefix=marketplace'
cp terraform.tfvars.example terraform.tfvars
# Edit project and region; keep secrets out of this file.
terraform plan -out=foundation.tfplan
# Review resources, IAM grants and costs before applying.
terraform apply foundation.tfplan
```

Service identities have Cloud SQL connector access only where needed; secret access is per secret. Database roles and fresh credential initialization are separate work. No app service gets project Owner or Editor. Do not put secret values in Terraform variables or state. Deployment uses the protected GCS backend. Preserve the bootstrap directory's state separately: the bucket must exist before the main backend can initialize.

On a fresh project, run `bootstrap/` first to enable Storage and Cloud Resource Manager and create the protected bucket. Create PostgreSQL with `database_active=true`, then stop it after initialization/verification and set the desired Terraform input back to false. The stopped activation policy works for an existing instance; it was rejected by Google during creation in this deployment.

## Application adaptations verified locally

- `Dockerfile.web` builds the frontend and backend together. Static-page and API-route/auth smoke checks passed with the database dependency mocked; this is not a cloud end-to-end check.
- `INITIALIZE_ON_STARTUP=false` leaves schema/seed work to the explicit initialization job and prevents a new replica from failing another replica's running questions.
- `GATEWAY_IAM_AUDIENCE` adds Cloud Run IAM identity authentication without replacing the model-scoped gateway key; metadata failure prevents forwarding. Two mocked transport tests passed.
- `MCP_REGISTRY_DATABASE_URL` selects durable HTTP MCP evidence/budget storage. A separate disposable PostgreSQL test verified evidence recovery across two registry instances, persisted call counts, hashed investigation tokens, expiry and revision drift rejection. This URL needs a narrowly scoped registry database role; business-query credentials stay read-only.
- Cloud HTTP MCP uses **revision-guarded reads**, rather than claiming a transaction held by another replica. Business revision/demo clock and policy hashes must match on each call; any change requires a fresh investigation. Local MCP retains its original held repeatable-read snapshot.
- The web request drains application traces before returning. Gateway post-filter audit timing still requires cloud verification.

These checks made no paid model calls and did not reset marketplace data. Frontend lockfile patched `source-map-js` to its compatible fixed release after the build reported an advisory; the subsequent dependency audit reported zero vulnerabilities.

## Build the web image with the cloud trace link

The support workspace's Langfuse link is set at frontend build time. Local builds default to `http://localhost:3000`. For this Japan-region cloud deployment, build from the repository root with:

```sh
docker build -f app/cloud/Dockerfile.web \
  --build-arg VITE_LANGFUSE_URL=https://jp.cloud.langfuse.com \
  -t asia-south1-docker.pkg.dev/marketplace-app-511005/marketplace/web:course-20261008 app
```

Set this URL to the intended Langfuse UI host (or project URL) for other deployments. Rebuild the web image when it changes; setting a Cloud Run runtime environment variable does not update the bundled frontend. This public navigation URL contains no keys and is separate from backend/gateway trace-export credentials.

## Configure Langfuse Cloud credentials

For learner deployments, set `MARKETPLACE_LF_HOST` to the regional HTTPS host where your Langfuse project exists. Pass that same host as Terraform `langfuse_host` and the frontend build argument `VITE_LANGFUSE_URL`. The default Terraform host preserves the existing instructor deployment; the learner guide explains explicit region selection.

The operator completed key entry on October 8. Both secret versions are enabled and API authentication passed. The steps below remain the repeatable setup procedure for a new learner project; trace delivery still needs a deployed-service check.

Create a matching public/secret key pair in your Langfuse project in the selected region. In Cloud Shell, run `scripts/configure-langfuse.sh` with `MARKETPLACE_GCP_PROJECT` set to the intended project. The October 8 operator copy is at `~/marketplace-cloud-review/configure-langfuse.sh`. The script accepts the secret through a hidden prompt and stdin, populates only the backend/gateway Langfuse secret versions, and writes the non-authenticating public key/host to a protected local configuration file. Never paste secrets into chat or Terraform. Key creation/entry is performed by the account owner.

## Pause the database between labs

```sh
export MARKETPLACE_GCP_PROJECT=marketplace-app-511005
app/cloud/scripts/database.sh status
app/cloud/scripts/database.sh start
# Use the application only after PostgreSQL is ready.
app/cloud/scripts/database.sh stop
```

These commands require gcloud and an authorized deployment identity. Start/stop changes activation policy: set the Terraform `database_active` input to the same desired value before a subsequent apply so Terraform does not undo the change. Stopping makes database-backed application calls unavailable; saved data remains. Cloud Run must keep minimum instances at zero for the intended idle-cost behavior.

## Cost boundary

> **Stop Cloud SQL between cloud lab sessions and start it only when you need the cloud application.** For this small lab, Cloud SQL left running is usually the largest continuing infrastructure cost. Stopping preserves data and suspends instance compute charges; storage and retained backups still incur a smaller ongoing charge. Follow the [stop/start instructions](../CLOUD-SETUP.md#7-stop-and-resume-between-labs) and verify the instance reaches **Stopped**.

Small shared-core PostgreSQL kept running: planning allowance about US$30–40/month including modest retained resources, subject to final regional price and capacity checks. Model/API calls are extra. Stopped PostgreSQL still incurs storage/backup charges. Public idle IPv4 can add $0.01/hour, around $7.30/month; the foundation uses private-only IP instead. Small stopped-lab retained resources should be a few dollars monthly, not a guaranteed bill. Langfuse Hobby is free within limits.

## Using the deployed application

[Open cloud marketplace](https://marketplace-web-327903210973.asia-south1.run.app/). Select operator or support and enter the demo password chosen during setup. Langfuse Cloud is in the Japan region. The local application remains available independently; data is not synchronized between the two.

## Remaining follow-up

1. Rehearse the corrected setup scripts in a fresh project; publish the learner repository and validate a clean local installation.
2. Hosted Google ADK reconnection passed October 8: the existing runtime uses the cloud MCP profile, deployed metadata matches the URL/secret pair, and a fresh cited payout investigation completed. See the [Google walkthrough](../../course/GOOGLE-PLATFORM-PLAN.md#switch-between-local-and-cloud-mcp-backends) for local/cloud switching. Lyzr reconnection remains to verify separately. Shared UI adapters remain a separate feature.
3. Forced replica/restart persistence checks and a broader Presidio cloud test remain additional acceptance work. The verified HTTP MCP check used separate requests, without forcing an instance change.
4. Keep database start/stop and cleanup instructions aligned with Terraform. Do not stop PostgreSQL while the owner is testing the app.

Sources: [Cloud SQL billing](https://cloud.google.com/sql/pricing), [stopped instance charges](https://docs.cloud.google.com/sql/docs/postgres/start-stop-restart-instance), [Cloud Run billing](https://docs.cloud.google.com/run/docs/configuring/billing-settings).

## Learner setup and troubleshooting requirements

The final learner path must use the corrected scripts and container images, rather than require learners to repeat this deployment's manual debugging. Keep one ordered checklist for project/region configuration, Terraform, private credential entry, image builds, database initialization, service deployment, acceptance checks and start/stop/cleanup. Mark it validated only after the cloud checks and a fresh-project rehearsal pass.

Known setup issues and the fixes included in that path:

- **Database startup appears quiet:** the credential script waits for an existing startup operation, reports progress and waits for `RUNNABLE` before configuring accounts. Do not submit a second startup while the first is pending. Errors identify the setup phase without exposing secret values.
- **Initialization encounters LiteLLM-owned migration tables:** the initializer handles bootstrap-owned objects separately from LiteLLM-owned objects. It validates unexpected owners and grants instead of attempting a blanket permission change as a non-superuser. The fix passed disposable PostgreSQL tests, and the rebuilt cloud initialization job completed successfully.
- **Cloud trace link points to localhost:** pass the Langfuse UI URL during the frontend image build. A runtime-only setting does not change the compiled link.
- **Private gateway needs two authentication layers:** the application supplies its runtime identity for Cloud Run and a scoped LiteLLM key for model access. The setup helper configures separate support and embedding keys; both were configured successfully in this project.

Troubleshooting entries should show the symptom, safe check, retry command and expected result. Keep credentials out of commands, logs and the guide. Infrastructure creation, successful initialization and a working user question are separate checkpoints.

- **Cloud SQL catalog reports view-lineage drift:** configure `agent_reader` with `search_path=analytics`, read-only transactions and the same statement timeout as local setup. The corrected initializer and cloud rerun passed.
- **HTTP MCP registry rejects a database URL:** this connection uses psycopg directly, so its secret must use `postgresql://`, not SQLAlchemy's `postgresql+psycopg://`. The credential helper now validates/migrates the original format. Ten offline credential checks passed. The affected cloud credential was rotated, its older secret version disabled, and MCP begin/read/end passed afterward. Avoid printing raw database exceptions: they can contain connection credentials.

### Gateway cold starts

The cloud gateway scales to zero. A first request after inactivity can spend longer than 40 seconds starting LiteLLM and its dependencies. The model client uses a 120-second timeout when Cloud Run IAM is configured, with the overall investigation still bounded to 150 seconds. `GATEWAY_REQUEST_TIMEOUT_SECONDS` can override the client timeout; local requests retain 40 seconds. This keeps minimum instances at zero rather than adding idle compute. A warm request succeeding does not by itself validate a cold start.

## Runtime selector follow-up — October 8, 2026

[Marketplace runtime selector](../RUNTIME-SELECTOR.md) documents conversation binding, native memory controls, configuration and remaining live validation. Changing runtime opens a fresh conversation; history preserves the original platform. The selector is deployed locally and in cloud. Google question/follow-up and native cross-session memory save/recall are verified. Google and Lyzr cloud order questions, same-session follow-ups and fresh-session native memory recall are verified. Local Lyzr credentials are configured in ignored `app/.env`, both local backends restarted, and the local order-2 question and same-session follow-up passed. Local Google ADC is configured; local main question and follow-up passed.


## Verified marketplace checkpoint — October 8, 2026

The local and cloud reference application paths are working. The shared UI selects OpenAI Agents SDK, Google ADK or Lyzr; switching opens a fresh conversation, and history retains its original runtime/session. Google and Lyzr remain hosted when selected locally, and currently use the local MCP tunnel profile. The SDK uses the selected application's local/cloud database. Endpoint/key profiles are independent of the runtime selector.

Cloud `market` was aligned once to local revision 24, including clock, business history and indexed policies, with a retained rollback snapshot. User accounts, conversations, ratings and personal/native memories remain independent; test/evaluation databases were not copied. Local order summaries and daily counts now use readable business labels and formatting. The user approved the new local output and confirmed the cloud SDK detailed trace in Langfuse. Google/Lyzr wrapper traces record the marketplace question/answer/timing/feedback; internal calls remain in native platform tracing.

Course plan: local SDK for main demonstrations; hosted agents and native platform monitoring in platform chapters. Online evaluation remains Evaluation chapter preparation. Clean-machine/fresh-project learner rehearsals, publication checkpoints, slides, notes, homework and recording preparation remain separate work. See the [architecture and delivery boundaries](../../course/MARKETPLACE-DEPLOYMENT-ARCHITECTURE.md).

## Separate Chapter 12 learner deployment

[Chapter 12](../../course/exercises/runtime-and-hosting/exercise.md) deploys only the stateless agent worker using Dockerfile.hosting-lab. Laptop chat owns history; HTTPS MCP reaches local middleware; the agent calls OpenAI Responses directly. It uses dedicated application keys and an existing learner-provisioned provider secret. This is a compact hosting lab, separate from the full application services described above. The deploy and cleanup helper records exact created resources; do not reuse instructor URLs, which were removed after validation.
