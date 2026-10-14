# Support Agent Basics

A separate standalone Chapter 19 lab: Google-managed ADK agent, packaged fictional order records and a native Python `lookup_order(order_id)` tool. No marketplace UI, SQL, MCP server, tunnel or business database is required. Native Sessions supply conversation context; optional `PreloadMemoryTool` uses managed Memory Bank after deployment. Local execution is not proof of managed memory or tracing.

## Fixture and native tools

Use `order-demo-1` (two Ceramic Mug Sets, payment received, not dispatched, payout held), `order-demo-2` (one Canvas Weekender, delivered, payout released), or `order-demo-3` (one Desk Lamp, cancelled/refunded). The fictional snapshot has its own dataset ID/as-of marker. Unknown IDs return `found=false`; there is no policy or mutation tool. Records are shared fictional lesson data; private memory identity is provided by native session context, not tool arguments.

## Create a separate managed deployment

Use the existing project, runtime service identity and staging bucket only when authorized. Activate the prepared Cloud Shell Python 3.12 environment, copy this directory separately and run from it. Install its pinned requirements in that environment. Set non-secret `GOOGLE_CLOUD_PROJECT`, `GOOGLE_CLOUD_LOCATION`, `GOOGLE_STAGING_BUCKET`, `GOOGLE_RUNTIME_SERVICE_ACCOUNT`, `GOOGLE_AGENT_MODEL` and `GOOGLE_MODEL_LOCATION` as in the existing Google walkthrough. No MCP secret is needed. Existing identity permissions are reusable; this script does not add roles.

```bash
cd ~/support-agent-basics
source ~/marketplace-google-venv/bin/activate
python -m unittest -v test_basics.py
python deploy.py
```

`deploy.py` calls create only, always names the NEW deployment **Support Agent Basics**, ignores the existing lab's `GOOGLE_RUNTIME_RESOURCE`, and writes `support-basics-deployment.json`. It refuses to create again when that manifest exists. Do not rerun after an uncertain create response until checking the console. No existing managed runtime is updated or deleted. Preserve the original Marketplace Support ADK Lab and its deployment manifest.

## Native demo and memory controls

Open the NEW Support Agent Basics deployment in Google Playground. Ask: **What products and quantities are in order-demo-1?** Then in the same session: **What is its payout status?** Inspect the native tool input/output and retained session context. A new session cannot infer which order you mean solely from the prior session.

State a synthetic preference in Playground: **I prefer answers in a compact table with Finding, Evidence and Next action.** Copy that native session ID. The native user ID must match the stored session owner; the existing Playground commonly uses `vais-query-reasoning-engine`, but confirm it in this new runtime's session rather than assuming a browser URL identifies the owner.

```bash
python demo.py session --user NATIVE_USER_ID --session SESSION_ID
python demo.py save --user NATIVE_USER_ID --session SESSION_ID
python demo.py memory --user NATIVE_USER_ID --question 'preferred answer format'
```

Wait for actual memory to appear, then start a fresh native session and ask another known order question. Generation and correct answer use are distinct checks. The CLI defaults to `basics-course-user`; that label is a lab client control, not an authenticated marketplace identity. No model argument can override the framework's memory user. Native memory is enabled by the deployment setting `GOOGLE_MEMORY_ENABLED`; this demo does not present a chat checkbox as a working override.

Inspect Google-native Sessions, Memory Bank, Cloud Trace/Logging/Monitoring. Telemetry is configured in the create script; verify actual traces after deployment. Model/runtime/memory charges depend on the account and calls. No paid inference is needed for the fixture/unit tests.
