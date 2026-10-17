# Marketplace runtime selector

Start with [Local and cloud deployment with multiple agent runtimes](DEPLOYMENT-AND-RUNTIME-PATHS.md) for the architecture, coordinated backend switch command and local-to-cloud acceptance process. This companion guide covers selector behavior, credentials and detailed validation.

Historical baseline, October 8, 2026, before the coordinated local switch and memory-control change: selector and adapters implemented; local main and test containers updated; cloud selector and Google query grant deployed; hosted adapters pass mocked contract tests. Google question, follow-up, explicit Memory Bank save and fresh-conversation recall pass. Google and Lyzr cloud order questions, same-session follow-ups and fresh-session native memory recall are verified. Local Lyzr credentials are configured in ignored `app/.env`, both local backends restarted, and the local order-2 question and same-session follow-up passed. Local Google ADC is configured; local main question and follow-up passed.

## Conversation behavior

Choose **Agent runtime** in the support workspace options: OpenAI Agents SDK, Lyzr, or Google ADK. A runtime change opens a blank conversation automatically. The first question creates its record. The previous conversation remains in history with its original runtime and session. Reopening it restores that runtime. A running question disables switching.

The server stores the runtime, agent target, platform user and external session. Question requests cannot override these values. Legacy conversations remain SDK conversations. Platform users derive from the authenticated marketplace account and a stable environment namespace; users cannot choose an operator identity in their question.

## Platform differences

| Runtime | Conversation history | Long-term memory | Marketplace guardrails |
| --- | --- | --- | --- |
| OpenAI Agents SDK | Existing local SDK session | Existing user-owned memory service; read/write controls | Existing gateway and prompt demos |
| Lyzr | Stable native session per marketplace conversation | Deployed agent's native settings; marketplace per-question switches are hidden | Configured on the hosted agent |
| Google ADK | Native session created once and persisted before asking | Deployed agent settings control retrieval; marketplace per-question switches are hidden | Configured on the hosted agent |

Each platform retains its own memory. Memory is not copied between runtimes or between environment namespaces. Configure Google retrieval with `GOOGLE_MEMORY_ENABLED` on the deployed agent. Memory Bank generation/save belongs to the hosted platform workflow; marketplace questions no longer send memory overrides or request session saves.

Hosted agents use their configured MCP endpoint. Choosing Google or Lyzr from a local interface does not repoint that agent to local data. Business revision and tool/token metrics from our SDK are not shown as if they describe a hosted run. New hosted responses retain structured business evidence from Google tool-response events and the matching Lyzr inference trace. Citations open the same saved database records, event timeline or policy passages as SDK answers. Unavailable sources are labelled instead of inventing records; older answers may lack a stored evidence bundle. Native traces remain useful for platform-level debugging. The app records the returned answer and supports normal answer feedback. A Langfuse wrapper records the hosted request/answer when configured; native internal tool/model spans remain in each platform's telemetry.

## Optional Google marketplace integration

This guide describes the existing verified marketplace integration, not a required setup for every Google lesson. The separate [standalone Chapter 19 Basics lab](../course/exercises/google-agent-platform/setup-guide.md) uses native Playground with packaged fictional data/function tools and has been deployed. It does not contain marketplace MCP tools; use the [optional marketplace integration sequence](../course/GOOGLE-PLATFORM-PLAN.md) to connect a compatible marketplace ADK agent. In the existing integration, the managed agent stays hosted whether its marketplace caller is local or cloud. Local ADC authenticates that caller; the agent's MCP profile independently selects its business endpoint and matching secret. `python deploy.py --backend local|cloud` updates a managed deployment, not a UI runtime choice. Preserve dated acceptance below and read back the actual deployed endpoint before a current demo.

## Configuration

All configuration and credentials belong to the **backend**, never the frontend bundle.

- Lyzr: `LYZR_AGENT_ID`, `LYZR_API_KEY`. The inference credential is distinct from the `x-api-key` supplied by Lyzr to our MCP service.
- Google: `GOOGLE_RUNTIME_RESOURCE`, Application Default Credentials (ADC), and permission to query that runtime. Cloud Run uses its service account; local Docker needs a read-only mounted ADC file and `GOOGLE_APPLICATION_CREDENTIALS` pointing to it inside the container.
- `MARKETPLACE_IDENTITY_NAMESPACE`: keep stable within an environment; test and main should differ.
- Missing configuration disables the option and the API rejects new conversations for it.

Local Compose passes these optional environment variables. For ADC, add a private Compose override mounting only the credential file read-only; do not mount the whole home directory or check credentials into Git.

Cloud Terraform supports `lyzr_agent_id`, `lyzr_enabled`, `google_runtime_resource`, and `google_runtime_project_id`. Use `lyzr_secret_enabled=true` to provision the approved secret before entry. Run `python3 cloud/scripts/configure-lyzr.py --project YOUR_PROJECT` in Cloud Shell to enter the key privately. Enable Lyzr only after the dedicated `marketplace-web-lyzr-api-key` Secret Manager secret has a version. The optional Google grant contains only `aiplatform.reasoningEngines.query`, in the agent project; it grants access to runtime query operations in that project, including session/memory methods exposed by the deployed agent. It is not limited to one user's native session. Backend identity binding supplies the app-level user boundary. No deployment/admin role is granted.

## Remaining setup and acceptance

1. Lyzr inference credentials are configured in cloud Secret Manager and the ignored local `.env`; temporary transfer files were removed. Both main/test local backends have loaded the settings.
2. The approved Google query grant is applied to the marketplace web service identity; local ADC is now configured separately. Live Google deployment metadata confirms the hosted GCP marketplace MCP target.
3. Test each runtime from the UI: order-2, a follow-up in the same conversation, reopening history, and switching to a fresh runtime conversation.
4. Verify native long-term memory save/recall with one synthetic preference and a fresh session under the same marketplace user. Verify another marketplace user cannot retrieve it.
5. Verify feedback on the marketplace wrapper trace, and native Google/Lyzr tracing separately.

## Validation so far

Eight adapter/API contract checks pass: immutable stored target; isolated users; session reuse; rejected client identity/runtime overrides; unsupported controls rejected; Google final-text filtering and absence of chat memory overrides; authorization failures saved as failures without exposing provider error bodies. The targeted feedback/gateway-auth suite brings the total to **13 passing checks**. Frontend production build and local container builds pass. Cloud selector is deployed with Google and Lyzr enabled. Browser switching from SDK to Google opens a blank conversation. Google and Lyzr cloud session/save/recall checks passed. Local Lyzr order-2 and same-session follow-up passed; local Google ADC is configured and local main question/follow-up passed. Thirteen frontend API/evidence checks and the production build also pass.

API references: [Lyzr inference chat](https://docs.lyzr.ai/agent-apis/agents/Chat), [Google custom-runtime query methods](https://docs.cloud.google.com/gemini-enterprise-agent-platform/scale/runtime/use-a-custom-agent).

## Historical validation before the memory-control change, October 8

The Google adapter completed a synthetic request, an order-2 question and a same-session follow-up from the marketplace. The follow-up recalled order-2. The order response reported revision 24 although the cloud marketplace database is revision 1. Live deployment metadata independently confirms `REMOTE_MCP_URL` points to the GCP marketplace MCP endpoint. The answer revision discrepancy is not evidence of a local connection. Fresh cloud memory-off and local/cloud memory-on reruns returned the correct September 27, revision 1; the earlier mismatch did not reproduce and its cause remains unconfirmed. The verifier now compares answer metadata with the actual tool snapshot.

Local main/test containers are deployed and Lyzr is configured. Google local credentials are now configured. Local ADC is now stored privately and mounted read-only through the ignored Compose override; the official CLI runs in Docker, so no host gcloud installation is needed.

Google native long-term memory passed: saved a synthetic payout-answer preference as a short table (Status, Reason, Next step), requested Memory Bank generation, then recalled those columns in a fresh marketplace conversation. Switching to SDK cleared the current conversation; reopening the Google conversation restored Google and its answer history. This does not copy memory between platforms.

Lyzr cloud validation: order-2 returned held payout ₹1,618.20, the follow-up recalled order-2, and a fresh conversation recalled the saved table columns Status, Reason, Next step. The memory-save acknowledgement itself was unhelpful; fresh-session recall supplied the evidence. Thumbs-up feedback survived reload. The final r8 deployment preserves hosted citations as returned text and avoids SDK snapshot labels for hosted calls. Native tool evidence remains in the platform trace. Local Lyzr also answered order-2 through the same hosted agent, which retains its cloud MCP target.

## Local Google activation and snapshot recheck — October 8

Local Google ADC was created with Google's official CLI container after the owner completed OAuth sign-in. The ignored `.google-auth/` directory holds the credential; ignored `compose.google.local.yaml` mounts that one file read-only into main/test backends. Both were restarted. Local main Google order-2 and its follow-up passed with memory enabled. The hosted agent still reads cloud data: September 27, revision 1; the local marketplace header is September 28, revision 24 and describes the local database only.

Keep the private override when recreating these backends:

```sh
cd app
docker compose -f compose.yaml -f compose.memory.yaml -f compose.google.local.yaml up -d --no-deps backend memory-backend
```

Do not share the private credential directory or override. Local authentication uses the owner's existing Google permissions; it does not grant new IAM roles. Revoke it with `gcloud auth application-default revoke` using the same credential configuration if no longer needed.

The fresh memory-disabled cloud investigation returned snapshot `2026-09-27T12:00:00Z`, revision 1, and its answer matched. The earlier revision-24 claim has not reproduced so far; its precise cause is unconfirmed. `google/verify_backend.py` now compares the final answer's date/revision to the actual begin-investigation result and fails on a mismatch instead of merely checking that an answer exists.

## Current repair and acceptance — October 8

The first coordinated switch read back the correct local URL and secret, but actual Google tools failed: the serialized MCP client retained the build-time cloud URL while authentication used the runtime local secret. `RuntimeBusinessTools` now creates its MCP client inside the deployed process. The repaired local deployment completed successfully and carries `BACKEND_PROFILE_CONFIG_VERSION=runtime-url-v1`; the switch script rejects older deployments on apply. All six local/cloud runtime questions have passed with the matching backend snapshot; see [acceptance record](BACKEND-SWITCH-VALIDATION-2026-10-08.md). Hosted agents are now set to local; cloud SQL is parked until a cloud walkthrough.

Chat memory controls are now SDK-only. Google and Lyzr follow hosted configuration; the Google adapter neither sends memory state overrides nor requests a session save. Four Google packaging/policy regression checks, eight updated adapter/API contract checks and ten switch-script checks pass. The cloud r9 image has been published and applied through the existing Terraform state; the refreshed cloud UI also hides hosted memory switches. Earlier save/recall results above describe the previous interface and remain historical evidence, not current chat controls.


## Shared answer presentation — October 8, 2026

The shared renderer supports Markdown tables and safe line breaks for all three runtimes. Google tool-response envelopes and Lyzr MCP trace results are saved as business source records, with provider trace metadata excluded. Lyzr validation binds the inference span to the stored agent/session and exact returned answer; its trace-listing agent field can be null. Source retrieval is optional and bounded to 20 seconds so an unavailable trace does not discard an otherwise successful answer.

Sixteen hosted adapter/evidence checks and fifteen frontend checks pass; production builds pass. Local Google and Lyzr smoke-test answers have been restored from their actual tool records, and their database source buttons open revision-24 rows. This was a targeted restoration of the two test conversations, not a backfill of all historical answers. The final cloud r15 image is deployed, reports ready and receives all traffic. A fresh Google cloud answer retained five source records; clicked database evidence displays revision-1 rows. Lyzr delayed source recovery retained four records for the cloud test answer; a fresh status rerun passed in 24.56 seconds with four automatic source records and clickable revision-1 rows. The empty legacy memory footer label is removed.

Delayed Lyzr trace recovery also retries a missing source bundle when reading the newest completed answer (within 15 minutes). Existing source bundles remain immutable. The retry uses the stored agent/session and exact answer, makes no inference or business tool calls, and remains optional if telemetry is unavailable. Five answer-history/feedback and cloud-auth checks also pass.


Cloud MCP concurrency repair: durable investigation row locks now use asynchronous PostgreSQL waits. A synchronous waiter previously blocked the event loop while another tool held the row lock across awaited policy retrieval. The original failure was reproduced in a disposable database; two durable-registry tests pass. The previously timed-out Lyzr payout question passed after deployment in 80.29 seconds, with clickable saved database and policy sources. Latency remains variable (latest Google status 102.67 seconds; Lyzr status 24.56 seconds). This validates the observed examples, not an availability or latency guarantee.

Final web and MCP image/traffic readback confirms ready status and 100% latest-revision routing. Local main/test proxies are healthy. Catalog definitions are retained in source envelopes as well. Full results and screenshots are in [the switch validation record](BACKEND-SWITCH-VALIDATION-2026-10-08.md).


### Aligned comparison baseline and local answer formatting

The cloud business snapshot was aligned with local `market` on 8 October: revision 24, 28 September simulation clock, all business records/events/commands and 20 indexed policy chunks. Cloud accounts, conversations and native/personal memories remain independent. Local/cloud data can diverge again after business actions. Existing conversation answers are historical; use a fresh conversation when comparing runtimes. The test and evaluation databases remain separate.

Local SDK answers now use `ANSWER_STYLE=readable` in Compose (main and test workspaces). Order lookups show an order title and Field/Details table with the actual placement date, order status, payment and shipment, plus other retrieved relevant fields. Counts state their date windows plainly. Citations remain inspectable; internal snapshot revision stays in UI metadata instead of being repeated in answer prose. Hosted Google/Lyzr and deployed cloud SDK formatting were not changed. Live local checks passed for order-2 status and yesterday/today order counts (2 and 1 respectively). When recreating backends, restart local frontend proxies so they resolve the new container addresses; retain the Google ADC overlay.

### User acceptance and teaching boundary

The user accepted the local readable output and confirmed detailed cloud SDK tracing in Langfuse. Hosted Google/Lyzr wrapper observations record the application boundary; inspect native platforms for internal model/tool spans. Main course demos will use the local SDK; hosted runtimes/native telemetry belong to platform chapters. See the [current architecture checkpoint](../course/MARKETPLACE-DEPLOYMENT-ARCHITECTURE.md#current-course-delivery-and-component-boundaries).


### Local-first pause acceptance — October 8

Both Google and Lyzr local profile settings were read back as verified by the switching script. Fresh direct local marketplace API questions completed through each hosted runtime while Cloud SQL was stopped. Google reported paid/captured/pending; Lyzr reported paid/captured/held and no return/refund. Saved source evidence was present for both. The first smoke predicate incorrectly required an unrequested payout amount in every answer; the saved responses were regraded for the requested order/payment status and evidence instead, without another inference run. Both passed. Cloud database activation policy is NEVER; restart before using cloud chat/SDK/MCP. Local UI remains on the SDK for the user's recording work.
