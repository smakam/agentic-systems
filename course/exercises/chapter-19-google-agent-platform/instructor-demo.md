# Instructor demo: Support Agent Basics on Google

**Readiness:** Support Agent Basics is deployed. The native Playground product lookup, same-session payout follow-up, missing-order result and tool/model traces have been checked. Memory Bank generation and scoped search of the stored preference passed, including an empty search for another test user. A recovered completed native trace verifies the saved preference in the model input and an order-demo-2 answer using Finding, Evidence and Next action columns. The first run had a Google service error; the CLI retry timed out before native completion, so this is not a passed CLI suite. Fixture references below remain distinct from each future model response.

## Start in the right environment

Use **Google Cloud console → Agent Platform → Agents → Scale → Deployments → Support Agent Basics → Playground** in the authorized course project. This is a **new, separate managed deployment**. Preserve the earlier **Marketplace Support ADK Lab**. No marketplace browser, SQL database, MCP server or tunnel is required for the core demonstration.

The model/runtime/memory/telemetry settings come from the Basics deployment manifest and configuration, not a marketplace UI checkbox. Read the current [Basics guide](../../../app/google/basics/README.md) for deployment and CLI commands. Confirm the deployment's native session owner rather than assuming the browser URL or a marketplace login supplies its memory identity.

## Show the instructions before running

Open the [full instruction file](../../../app/google/basics/support_agent_basics/instructions.txt) and [fictional dataset](../../../app/google/basics/support_agent_basics/orders.json).

Explain the agent's boundaries:

- It answers order questions using the native `lookup_order(order_id)` function before stating record facts.
- It uses an exact supplied order ID or same-session context; if unclear, it asks for an ID.
- It reports packaged fictional snapshot fields and missing records faithfully. Payment and seller payout are separate.
- It cannot mutate orders, move money, query SQL/MCP or invent policy eligibility. There is no policy tool.
- A relevant retrieved presentation preference can affect layout; current explicit instructions and fixture facts retain authority.
- Session context and persisted Memory Bank are different. Saying “remember” does not itself prove persistence; memory generation is a separate operation.

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

## C: native long-term memory across sessions

**Verified boundary:** formation and scoped retrieval were checked. The fresh-session answer-use steps below remain a demonstration to inspect, not a guaranteed verified outcome. Record provider/connection errors separately from a memory retrieval miss.

1. In a fresh native session state **“I prefer answers in a compact table with Finding, Evidence and Next action.”** This is a synthetic presentation preference.
2. Copy that native session ID. From the prepared Basics CLI directory inspect its stored owner:

   ```bash
   python demo.py session --user NATIVE_USER_ID --session SESSION_ID
   ```

   Supply the verified owner consistently. Playground's earlier lab commonly used `vais-query-reasoning-engine`; that is not a guarantee for this deployment. The CLI default `basics-course-user` is a different lab client label.

3. Trigger platform memory generation separately:

   ```bash
   python demo.py save --user NATIVE_USER_ID --session SESSION_ID
   python demo.py memory --user NATIVE_USER_ID --question 'preferred answer format'
   ```

4. Wait for an actual stored/retrieved preference before claiming readiness. A generation request or a nicely formatted answer alone is insufficient.
5. Start a **new Playground session** under the same verified native user and ask **“What are the payment, shipment and payout statuses for order-demo-2?”** Do not mention memory or ask for a table.
6. Inspect native retrieval and actual answer layout alongside lookup evidence. The fixture says **payment received, shipment delivered, payout released**. Record a format miss honestly; memory formation and correct use are separate checks.
7. In that session ask **“For this answer use one short paragraph. What is the payout status for order-demo-3?”** Current explicit layout should override a saved preference; the fixture payout is **not applicable**, with order cancelled and payment refunded.

Memory requires the deployment's native memory setting. No marketplace checkbox controls this agent. Do not imply automatic conversation-end extraction was implemented merely because Chapter 18 demonstrated it for Mem0.

## D: native tracing, monitoring and evaluation concepts

Open the actual native session/tool events and Cloud Trace for a completed run. Show what input the tool received, what it returned and what the final answer claimed. Inspect logs/monitoring where configured. Keep operational telemetry separate from quality scoring.

Use one fixture question as a simple evaluation example: compare its answer with the known JSON fields and identify missing or invented claims. Explain documented Agent Evaluation/Gen AI evaluation capabilities without claiming a native evaluation job ran unless you show its receipt. Judge-model inference and computation-based metric charges are separate evaluation cost categories; no dollar rate is required.

## Optional reference: full cloud integration

The [optional exercise](exercise.md) connects a cloud chat application/backend and business MCP/data to a Google-hosted agent using the linked deployment guides. The existing Marketplace Support ADK Lab supplies historical integration evidence; it is not an additional required instructor demonstration. Keep its deployment, tools, business fixtures and memory identities distinct from Basics. The core walkthrough above remains entirely in native Google Playground.

## What to record and cleanup

Record the deployment, model and memory settings; actual question/answer; lookup input/result/source; same/fresh-session behavior; generation and retrieval evidence; native trace links; and failures or missing telemetry. This is a framework/managed-service walkthrough, not a comparative platform benchmark.

Leave the instructor deployments in place for review. Use only synthetic data/preferences and remove only owned rehearsal artifacts through documented platform controls if available. Do not delete the earlier deployment or learner-created resources. Learners attempting the optional extension use [exercise.md](exercise.md), with [separate reference answers](solutions/answers.md).
