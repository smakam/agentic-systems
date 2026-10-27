# Instructor demo: Basic and Marketplace support agents on Google

**New Playground save revision:** deployed-code update and fresh-session verification are in progress. Historical memory results below used the prior explicit CLI-save path; they do not validate the new tool.

**Readiness:** Support Agent Basics is deployed. The native Playground product lookup, same-session payout follow-up, missing-order result and tool/model traces have been checked. Memory Bank generation and scoped search of the stored preference passed, including an empty search for another test user. A recovered completed native trace verifies the saved preference in the model input and an order-demo-2 answer using Finding, Evidence and Next action columns. The first run had a Google service error; the CLI retry timed out before native completion, so this is not a passed CLI suite. Fixture references below remain distinct from each future model response.

## Start in the right environment

Use **Google Cloud console → Agent Platform → Agents → Scale → Deployments → Support Agent Basics → Playground** in the authorized course project. This is a **new, separate managed deployment**. Preserve the earlier **Marketplace Support ADK Lab**. No marketplace browser, SQL database, MCP server or tunnel is required for the core demonstration.

The model/runtime/memory/telemetry settings come from the Basics deployment manifest and configuration, not a marketplace UI checkbox. Read the current [Basics guide](../../../app/google/basics/README.md) for deployment and CLI commands. Confirm the deployment's native session owner rather than assuming the browser URL or a marketplace login supplies its memory identity.

## Brief code walkthrough before Playground

Spend about one minute on the code: agent.py attaches the native lookup and explicit preference-save tools plus optional memory preload; tools.py reads orders.json; instructions.txt defines the behavior. The fixture has fictional business data only, not policy documents. There is no MCP or separate business backend in Basics. Then return to Google Cloud for the live demonstration. The Tools list describes capabilities; a completed session/trace shows actual calls, results and answers.

## Show the instructions before running

Open the [full instruction file](../../../app/google/basics/support_agent_basics/instructions.txt) and [fictional dataset](../../../app/google/basics/support_agent_basics/orders.json).

Explain the agent's boundaries:

- It answers order questions using the native `lookup_order(order_id)` function before stating record facts.
- It uses an exact supplied order ID or same-session context; if unclear, it asks for an ID.
- It reports packaged fictional snapshot fields and missing records faithfully. Payment and seller payout are separate.
- It cannot mutate orders, move money, query SQL/MCP or invent policy eligibility. There is no policy tool.
- A relevant retrieved presentation preference can affect layout; current explicit instructions and fixture facts retain authority.
- Session context and persisted Memory Bank are different. Saying “remember” does not itself prove persistence; memory generation is a separate operation, now requested through the explicit remember_preference tool.

## Deployment is separate from this walkthrough

Use [setup-guide.md](setup-guide.md) for prerequisites, environment substitutions, installation, the tests/deploy commands and opening Playground. The instructor walkthrough below starts after deployment; do not redeploy during every question or memory demonstration. The existing full-stack lab remains separate.

## A: tool evidence and same-session follow-up

1. Start a fresh Playground session. Ask **“What products and quantities are in order-demo-1?”**
2. Inspect native session/trace events: `lookup_order` should use `order-demo-1`; compare returned fields with the packaged JSON. Record the actual answer.
3. The fixture contains **2 × Ceramic Mug Set**. The tool source identifies dataset `support-agent-basics-fictional-v1`, its as-of marker and `fictional: true`.
4. In the same session ask **“What is its payout status?”** Inspect the retained order context and lookup evidence; the follow-up may reuse the prior tool result rather than issue a new lookup. The fixture says **payout held** and **buyer payment received**; held alone does not establish the policy reason or eligibility.
5. Start a new session and ask **“What is its payout status?”** without naming an order. Inspect whether it asks for an ID; an unsupported guess is a behavior to record.

## B: missing data and instruction boundaries

1. In a fresh session ask **“What is the payout status for order-demo-999?”**
2. Inspect the lookup result: the fixture has no such order, so `found=false` should not become an invented status.
3. Optionally ask **“Can you release the payout for order-demo-1?”** The tool is read-only and there is no mutation/policy tool. Record whether the response explains that boundary without claiming a real action.

## C: native long-term memory from Playground

**Deployment requirement:** use the Basics revision that exposes `remember_preference`. Older deployments only preload memory and still require the CLI save operation. The new save tool is a native ADK function, not MCP. It saves only an explicitly requested presentation preference through the current session's trusted user scope; no identity argument is accepted.

1. In a fresh Playground session say **“Remember: I prefer answers in a compact table with Finding, Evidence and Next action columns.”**
2. Inspect the session/tool trace. Confirm a `remember_preference` call with the actual requested preference. Its result must say `generation_requested`. This requests Google Memory Bank extraction; it is not proof that storage has finished. A response saying “I will remember” without the tool call is insufficient.
3. Inspect the deployment's Memory Bank records for the same native user and confirm the stored preference is available. If the record has not appeared, allow processing time and check again; do not immediately claim failure or readiness. Use only synthetic preferences.
4. Start a **new Playground session under the same verified native user** and ask **“What are the payment, shipment and payout statuses for order-demo-2?”** Do not repeat the preference or request a table.
5. Inspect the actual model input/native trace for memory preload and the answer's format, alongside the order-lookup evidence. The fixture says payment received, shipment delivered and payout released. Format alone does not establish memory retrieval, and same-session context is not long-term recall.
6. Ask **“For this answer use one short paragraph. What is the payout status for order-demo-3?”** Current explicit formatting should override the remembered preference. The fixture payout is not applicable; the order is cancelled and payment refunded.

When memory is disabled or generation cannot be confirmed, the tool reports that status and the agent must not claim a save. This path does not automatically save every conversation. The CLI session/save/memory commands remain optional diagnostics or a fallback for older revisions; they are not required for the revised Playground walkthrough. Provider errors are distinct from retrieval misses. Preserve the existing Marketplace Support ADK Lab.

## D: native tracing, monitoring and evaluation concepts

Open the actual native session/tool events and Cloud Trace for a completed run. Show what input the tool received, what it returned and what the final answer claimed. Inspect logs/monitoring where configured. Keep operational telemetry separate from quality scoring.

Use one fixture question as a simple evaluation example: compare its answer with the known JSON fields and identify missing or invented claims. Explain documented Agent Evaluation/Gen AI evaluation capabilities without claiming a native evaluation job ran unless you show its receipt. Judge-model inference and computation-based metric charges are separate evaluation cost categories; no dollar rate is required.

## E: Marketplace support agent — instructor walkthrough

After Basics, show **Marketplace Support ADK Lab** as the full business integration. Its code is [marketplace_google/agent.py](../../../app/google/marketplace_google/agent.py). [Open the existing authorized deployment](https://console.cloud.google.com/agent-platform/runtimes/locations/us-central1/agent-engines/1966208540318105600/playground?project=customer-support-agent-510915). This resource is different from [Support Agent Basics](https://console.cloud.google.com/agent-platform/runtimes/locations/us-central1/agent-engines/2782635506360385536/playground?project=customer-support-agent-510915).

1. Confirm the cloud chat/backend, authenticated business MCP and database are available. Follow the setup guide for readiness; do not redeploy during the walkthrough.
2. Show the architecture: chat UI and trusted application backend → hosted ADK agent → business MCP backend → database and policy retrieval. The UI's Google runtime option invokes its configured deployment; it does not deploy or retarget it. Verify the binding before claiming which instance was called.
3. Select a known order from the current backend. Ask **“List the products and quantities for order [known ID].”** Then ask **“What is its buyer payment status and seller payout status?”**
4. Ask **“Why is that payout held, and what does the applicable policy require?”** if the selected order has a held payout. Otherwise choose a question supported by its actual state. Do not invent a failure reason or promise a specific answer.
5. Inspect the actual business-tool inputs/results, retrieved policy and citations in the native trace. Contrast with Basics: remote MCP and database/policy evidence replace the packaged JSON function.
6. Show native session history, logs and monitoring where configured. Operational signals are not correctness scores. For memory, inspect only a supported verified save/retrieval path for this separate deployment; the new Basics save tool does not automatically exist here. Keep user identities, deployment settings and data distinct.

Learners repeat the Basics flow as core practice. Deploying and connecting their own full marketplace cloud integration remains optional; the instructor demonstrates the existing integration without making it a required learner setup.

## What to record and cleanup

Record the deployment, model and memory settings; actual question/answer; lookup input/result/source; same/fresh-session behavior; generation and retrieval evidence; native trace links; and failures or missing telemetry. This is a framework/managed-service walkthrough, not a comparative platform benchmark.

Leave the instructor deployments in place for review. Use only synthetic data/preferences and remove only owned rehearsal artifacts through documented platform controls if available. Do not delete the earlier deployment or learner-created resources. Learners attempting the optional extension use [exercise.md](exercise.md), with [separate reference answers](solutions/answers.md).
