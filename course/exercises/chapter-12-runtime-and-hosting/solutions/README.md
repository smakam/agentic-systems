# Runtime and Hosting — reference answers

This solution mirrors the deployment walkthrough: six local questions followed by six cloud questions. It describes the **standard local test marketplace** and the **full Google Cloud marketplace**. Verify your actual configuration; the table’s source values are not fresh live-service observations.

## Part 1 — local deployment

| Question | Reference answer | Evidence to inspect |
|---|---|---|
| 1. Component placement | Test frontend and test backend are separate Docker services. The chat API and OpenAI Agents SDK execute in the backend process. Standard stdio MCP runs as a child process inside that backend container. LiteLLM and PostgreSQL run in separate containers. | `app/compose.yaml`, `compose.memory.yaml`; SDK creation in `agent.py`; `MCPServerStdio` in `mcp_client.py` |
| 2. Chat → agent | The browser calls the marketplace API via the frontend route. The backend ask handler invokes the SDK agent in-process; it does not call a separate local agent HTTP service. | Frontend `src/main.jsx` ask handler; backend `api.py` conversation ask handler; `agent.py` `Runner.run` |
| 3. Agent → model | The SDK’s model client points to the LiteLLM gateway (`LITELLM_URL`). LiteLLM routes the model alias using the selected gateway configuration. The model provider is an external service; a locally hosted agent does not mean locally hosted model inference. | `compose.yaml`, `tools.py` model client, gateway config selected by Local Setup |
| 4. Agent → tools | The standard local setting is MCP over stdio. `MCPServerStdio` launches the marketplace MCP server as a subprocess with selected environment settings. Tool handlers execute SQL using their scoped database connection. A direct-tools override is a different configuration: check the selected setting and observed trace before drawing the route. | `AGENT_TOOL_TRANSPORT` in Compose; `agent.py`, `mcp_client.py`, `mcp_server.py`, `tools.py` |
| 5. Persistence | The test UI uses `market_test`. Tool reads use `READ_DATABASE_URL`; the application uses its database connection to persist conversations, runs and evidence. PostgreSQL’s persistent volume survives backend container recreation. Process-local SDK state alone is not durable storage. Do not confuse this practice database with fixed `market_eval`. | `compose.memory.yaml`, `db.py`, model definitions and final run persistence in `agent.py` |
| 6. Controls | Docker supplies the container environment and lifecycle. The SDK handles the loop and its normal eight-model-turn limit. The app supplies elapsed-time/cost controls and stored history selection. LiteLLM supplies configured model routing/gateway controls; Langfuse receives traces through instrumentation. These are integrations, not automatically supplied by Docker. | `compose.yaml`; `agent.py` limits and `BudgetHooks`; database session code; gateway/tracing configuration |

Local diagram: browser/test frontend → chat API + OpenAI Agents SDK in test backend → stdio MCP subprocess/tool handlers → `market_test`; the SDK separately calls LiteLLM → configured external model. Add an application persistence connection to PostgreSQL for history, runs and evidence.

## Part 2 — full cloud deployment

| Question | Reference answer | Evidence to inspect |
|---|---|---|
| 1. Services and placement | The intended full deployment has `marketplace-web`, `marketplace-mcp` and `marketplace-gateway` Cloud Run services. The web container hosts the chat backend and OpenAI Agents SDK. Your project, region, image and revision are deployment-specific. | `app/cloud/terraform/services.tf`; your Cloud Run service/revision pages; `outputs.tf` |
| 2. Chat → agent | Browser HTTPS traffic reaches the web service. Its backend invokes the SDK in-process. These logical components share the web container; they are not three independently deployed agent/chat containers. | Web service container entry point; `api.py`, `agent.py`, web routing configuration |
| 3. Agent → model | The full cloud marketplace uses LiteLLM, not the direct OpenAI route of the retired hybrid lab. Terraform supplies the gateway’s `/v1` URL as `LITELLM_URL` and its service URI as IAM audience. Runtime service identities have gateway invocation permission. LiteLLM forwards the configured provider/model request. | Web environment names and Secret Manager references; gateway configuration; `gateway_identity.py`; gateway IAM bindings in `services.tf` |
| 4. Agent → tools | Web is configured with `AGENT_TOOL_TRANSPORT=mcp_http` and `SDK_MCP_URL` pointing to the cloud MCP service’s `/mcp` endpoint. HTTP MCP carries tool requests; MCP handlers then use the database driver to query Cloud SQL. MCP API-key and allowed-host checks and scoped read credentials are separate controls. | `services.tf`, `http_mcp_client.py`, `remote_mcp.py`; secret **references**, not values |
| 5. Persistence | Cloud SQL is outside the Cloud Run services. MCP reads business/policy data through its scoped database connection. Web also uses Cloud SQL for application history, saved investigations and evidence. Gateway has its own database configuration. The database name and roles must be read from your deployment/source; do not infer them from local `market_test`. | Cloud SQL configuration in Terraform; service Cloud SQL mounts and database secret bindings; application models |
| 6. Resources and responsibilities | Current web/MCP source configuration specifies 1 CPU, 1 GiB, 180-second request timeout, concurrency 2, minimum 0 and maximum 2 instances. Those are intended configuration values; read actual deployed settings separately. Secret Manager and service identity support infrastructure access controls. The SDK/app/gateway/Langfuse still supply agent loop, history, model routing, evidence handling and tracing. Cloud Run does not automatically implement RAG, model guardrails, evaluations or resumable agent execution. | `services.tf`, `agent.py`, gateway configuration and tracing code; Cloud Run revision settings |

Cloud diagram: browser → web service (chat backend + SDK) → HTTP MCP service/tool handlers → Cloud SQL; SDK → LiteLLM gateway service → external model. Add web → Cloud SQL application persistence. Hosting the agent in the cloud changes location and operational controls, not the basic model/tool/data responsibilities.

## Interpreting your evidence

- **Observed:** checked in the current Docker/service configuration or an actual recorded execution.
- **Configured:** specified by source or example configuration, without checking a running deployment.
- **Unavailable:** you have no deployment or access to the particular live setting. State that limitation explicitly.

No cloud deployment is required to complete the source-based cloud comparison. The worksheet does not require a tunnel, the historical port-5192 UI, a fresh model call or a database reset. Live diagrams should match the learner’s selected configuration, not blindly copy these source defaults.

For infrastructure behavior, see [Cloud Run configuration](https://docs.cloud.google.com/run/docs/configuring) and [container runtime contract](https://docs.cloud.google.com/run/docs/container-contract). Compare optional agent-platform features in the later **Agentic Platforms** section.

The earlier agent-only/tunnel experiment and its October 10 validation are retained as a separate historical authoring record. They are not the current learner exercise or evidence that a cloud service is running today.
