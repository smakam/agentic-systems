# Lyzr marketplace support lab

The application supplies read-only business tools; Lyzr owns the model and agent loop. Long-term memory is off. Seven MCP tools are exposed: begin/end investigation plus catalog, SQL, document retrieval, evidence fetch and order history.

## Run the temporary endpoint

With the existing marketplace stack running, from `app`:

```sh
./scripts/remote-mcp.sh start
./scripts/remote-mcp.sh status
./scripts/remote-mcp.sh stop
```

The launcher downloads cloudflared from Cloudflare's official GitHub release and verifies its SHA256. It starts only the remote-mcp service and an outbound HTTPS tunnel; no router port forwarding is needed. Keep the Mac awake, Docker running and the tunnel process alive. Restarting the tunnel changes its URL; update the Studio MCP connection accordingly. The key is in `.remote-mcp.env` (mode 600, ignored by Git); do not put it into prompts or source control. Studio uses the `x-api-key` header with no prefix. Stopping the tunnel and MCP service removes external reachability. Delete the saved Studio connection when the demo ends if desired.

Cloudflare Quick Tunnels do not support SSE. This adapter uses stateless Streamable HTTP with JSON responses. A client that requires legacy SSE will need another tunnel/hosting arrangement.

## Isolation and scope

One `begin_investigation` creates an opaque investigation ID, a repeatable-read database snapshot, and an evidence store. All five business tools require that ID. Evidence handles cannot be fetched across investigations. A per-investigation lock serializes tool access. Investigations expire after 180 seconds; at most eight can be open. `end_investigation` releases the snapshot early. Expiry, capacity, authentication and SQL failures produce explicit errors. Database analytics access uses the existing agent_reader role; business mutations and memory are unavailable.

This is a single-principal synthetic-data lab. A shared API key authorizes the lab's full read-only analytics scope; it does not implement production end-user or tenant permissions. Remote calls do not pass through the OpenAI agent runtime, its citation validator, history injection or Langfuse run bookkeeping. The Studio prompt instructs those behaviors; smoke tests must verify them. SQL validation, retrieval, budgets and evidence contracts still run in the application.

## Dashboard steps performed

These steps describe the saved configuration created on 2026-10-02. Before dashboard setup, the local authenticated MCP service and temporary tunnel were started and tested.

1. Open the signed-in Lyzr Agent Studio organization.
2. Go to **Tools → New → MCP Server**. Enter:
   - **Name:** Marketplace Support MCP Lab
   - **Description:** Read-only synthetic marketplace tools; per-question snapshots and evidence; no memory or business writes.
   - **Server URL:** the current HTTPS tunnel endpoint ending in `/mcp` (read `.remote-mcp/endpoint.txt`; it changes when the tunnel restarts).
   - **Auth Type:** API Key
   - **API Key:** the demo key from `.remote-mcp.env` (never copy the value into documentation).
   - **Header Name:** `x-api-key`
   - **Header Prefix:** leave blank.
3. Click **Add Server**. Close the success dialog, open the **MCP** tab and select **Marketplace Support MCP Lab**. Confirm Lyzr discovers all seven actions: `begin_investigation`, `end_investigation`, `get_catalog`, `query_business_data`, `search_documents`, `fetch_evidence`, `get_order_history`. In this API-key setup, discovery worked without a separate Connect step.
4. Select **Create Agent → Agent**. Set **Name** to Marketplace Support — MCP Lab and **Description** to Read-only investigation of the synthetic marketplace through authenticated remote MCP. No long-term memory.
5. Fill **Role** with Internal marketplace support investigator and **Goal** with Answer questions about synthetic marketplace orders, refunds, payouts and policies using verified read-only MCP evidence.
6. Paste the adapted prompt from `lyzr/agent-instructions.txt` into **Instructions**. It directs the agent to begin/end each investigation, use the same investigation ID throughout the question, retrieve evidence, preserve exact citations and distinguish unknown facts from absent records.
7. Remove the default **Memory** feature using **Remove feature**. Leave Knowledge Base, Data Query, Skills, managerial agents, A2A and automation unconfigured for this initial test; the application supplies SQL and document retrieval through MCP.
8. Select the model under **Model → OpenAI**. The final saved model is **gpt-5.4-mini**. We initially tried gpt-5-nano and gpt-5.4-nano, then switched after observing answer-fidelity issues. During setup we enabled advanced model parameters and selected low reasoning effort; the final saved model is confirmed, but its reasoning setting was not re-read after the model changes.
9. Under **Tools → Add tool**, choose **Marketplace Support MCP Lab**. Keep all **7 actions** selected, leave **Use creator's credentials** selected for the private lab agent, and click **Add Tool**. Leave dynamic parameters such as investigation ID and SQL to the agent's tool calls. The builder showed a cached tool list during setup; reloading it and restoring the draft made the new connection available.
10. Click **Create** once the prompt, model, memory setting and MCP attachment are ready. Subsequent prompt/model changes were saved with **Update**. The initial setup stopped at Playground. On opening Deploy later, Lyzr confirmed the agent was already live behind its authenticated API; no separate API deployment action was required. App Store publishing and sharing were not performed.
11. Open **Playground** and submit a test question. Use the **Activity** panel to inspect tool calls, inputs, outputs and returned evidence. Use **New Chat** to test without earlier conversation history.
12. Refine the prompt based on observed failures and click **Update**. The final successful test was: “For order-1, what are the current order and payment statuses, and what happened to its seller payouts? Explain any earlier failed attempt and the applicable settlement policy.” It completed in 13.39 seconds; all three citation handles matched returned evidence and `end_investigation` closed the snapshot.

Saved agent: [Marketplace Support — MCP Lab](https://studio.lyzr.ai/create-new-agent/6abfbf34013b6eb4db9ff6f0?tab=playground). See `VALIDATION.md` for model-trial findings and verification limits.

## Studio configuration

Agent: Marketplace Support — MCP Lab. Model: OpenAI gpt-5.4-mini. Role: internal marketplace support investigator. Current memory: native Cognis enabled with Cross Session ON (October 3). Prompt: `lyzr/agent-instructions.txt`. Connect all seven tools from Marketplace Support MCP Lab. Do not add an unrelated built-in knowledge base or data query feature.

Suggested smoke tests:
- What is the current status of order-1?
- What happened to the payouts for order-1? Explain current state and previous failures using event history and policy.
- Show Cedar orders. Expected: resolve seller/product ambiguity before querying orders.

## Validation

The adapter integration tests use the disposable market_test database, never the interactive market database. They verify authenticated MCP discovery, blocked hosts/origins, fixed snapshots, evidence isolation, write rejection, expiry, capacity and cleanup. Public-tunnel SDK checks verify initialize, tool discovery, catalog, history and policy retrieval; requests without the key return HTTP 401. Studio end-to-end observations are recorded in VALIDATION.md. Nano models reached the tools but showed answer-fidelity issues, so the saved agent uses the mini model.

The remote order-history response adds an `order_summary` evidence envelope with order and payment statuses. It uses the same snapshot and a bound read-only query, so those statuses do not have to be inferred from payout records.

## API deployment confirmed

On 2026-10-02, the **Deploy → Agent API** page displayed **Agent deployed** and **Your Agent is Deployed and Ready to Use**. Saving the agent had already made it available through Lyzr's authenticated inference API.

- Endpoint: `POST https://agent-prod.studio.lyzr.ai/v3/inference/chat/`
- Agent ID: `6abfbf34013b6eb4db9ff6f0`
- Headers: `Content-Type: application/json` and `x-api-key` containing the Lyzr API credential shown in the dashboard. This credential is separate from the application's remote MCP key.
- Request fields: `user_id`, `agent_id`, `session_id`, `message`. Start a distinct session ID for a new conversation.
- Keep API credentials on a trusted backend, outside public browser code and this guide.

The deployment status was verified in the dashboard. The agent's tool workflow was tested through Playground; a separate external inference-API request has not been executed. The local MCP service and temporary tunnel were still running at deployment verification. The tunnel remains required for business-tool calls; restarting it requires updating its URL in Studio.

App Store publishing is a separate option and has not been performed.


## Next deployment task: cloud middleware without a tunnel

The agent API is deployed, but the business middleware still depends on local Docker and a temporary tunnel. The next task is to deploy the remote MCP service together with cloud-reachable SQL/RAG data and embedding/gateway dependencies behind a stable authenticated HTTPS endpoint. Provider/target selection and implementation are pending. Account for process-local investigation snapshots/evidence before scaling. Update Studio and verify retrieval with the local tunnel and middleware stopped. Full scope and acceptance criteria are in [specification section 3.4](../../SPECIFICATION.md#34-lyzr-remote-mcp-implementation-and-cloud-follow-up--october-2-2026), with progress in [M36](../../MILESTONE-LOG.md#m36--lyzr-agent-studio-with-authenticated-remote-mcp) and the [course outline](../../course/COURSE-PLAN.md).

## Current configuration update — October 3, 2026

After reboot, the agent was reattached to Marketplace Support MCP Lab — Reconnected using the same demo key and seven read-only actions. The current quick-tunnel URL is in `.remote-mcp/endpoint.txt`. The launcher now waits for authenticated MCP initialization before declaring readiness.

Dashboard follow-up: Build → Memory Add → Lyzr Cognis → leave Cross Session OFF → Save → Update → Playground in a fresh session. Model and prompt unchanged. [Two-turn off/on test and screenshots](memory-session-2026-10-03/REPORT.md) verify within-session order reference resolution and fresh evidence retrieval. Cognis internal persistence behavior was not exhaustively verified; application long-term-memory tools remain unexposed. Earlier October 2 Memory-off steps above are historical.

For a stable URL while retaining local hosting, use a named Cloudflare tunnel with an account/domain or an account-assigned ngrok dev domain. User deferred selecting these; no stable tunnel has been provisioned. Full cloud middleware deployment remains the separate task above.

## Active stable tunnel — October 3, 2026

[ngrok setup, verification and reboot runbook](ngrok-2026-10-03/REPORT.md). Current agent attaches **Marketplace Support MCP Lab — Stable**, endpoint `https://clamor-grumpily-directed.ngrok-free.dev/mcp`. All seven actions verified; old Cloudflare process stopped. This supersedes the earlier quick-tunnel instructions and deferred-choice notes. Use `bash scripts/remote-mcp-ngrok.sh start|status|stop` from app. Ngrok starts after macOS login; ensure Docker Desktop is running. Actual reboot not tested; same-URL service restart and Lyzr lookup passed. Cross Session is now ON; see the subsequent native-memory test report.

## Native Cognis long-term test — October 3

Cross Session is ON, with extraction guidance for preferences, accepted checklists and historical checkpoints. Prompt now permits native memory, distinguishes remembered history from current business evidence, and protects temporary overrides. Description updated; gpt-5.4-mini and the Stable business MCP connection retained. [Results and dashboard steps](cognis-memory-2026-10-03/REPORT.md).

Short-term continuity, fresh-chat semantic/procedural/checkpoint recall, override reconfirmation and the Cross Session off/on control passed. Autonomous checklist application missed actual shipment retrieval, including after an added instruction: record this separately from successful checklist recall. Native write permissions, provenance, verified deletion and multi-user isolation do not inherit our backend contracts and remain unverified.

### External curl smoke test — October 3, 2026

[Result and reusable curl](api-smoke-2026-10-03/REPORT.md): HTTP 200 in 17.23 s; latest deployed agent returned correct order-2 paid/captured status and evidence references in a fresh API session. First masked-key attempt returned 403; existing unmasked key succeeded. Credential absent from saved request/report and temporary credential files removed. User reviewed tracing/monitoring UI and accepted it. Checklist-use gap, native memory identity/provenance/CRUD checks, cloud hosting/reboot verification and deeper observability are tracked as enhancements in course section 21.
