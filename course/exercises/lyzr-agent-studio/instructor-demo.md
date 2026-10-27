# Instructor demo: Basics and Marketplace support agents on Lyzr

## 1. Basics in Lyzr Playground

Complete the [Basics setup guide](setup-guide.md) first. Use the separate **Support Agent Basics** agent with its fictional-order Knowledge Base attached. It is a Lyzr-hosted agent, even though this path requires no cloud marketplace deployment. Leave Marketplace MCP tools unattached.

1. Open **Support Agent Basics → Playground**, then start a new chat.
2. Ask **“What is the status of order-demo-1?”** Check the answer against the retrieved fictional source: payment received, shipment not dispatched, payout held. The agent should distinguish those fields rather than invent an overall status absent from the source.
3. In the same chat ask **“What is the payout status for this order?”** Check the retained order identity and the held payout in the source.
4. Open **Activity / Traces**. Inspect the actual Knowledge Base chunk from `orders-knowledge.txt`, its dataset/as-of information, model input/output, latency and usage where available. Retrieval relevance is not an answer-correctness score.
5. If useful, ask about **order-demo-999** in a new chat to show the missing-record boundary. No record should be invented; distinguish a failed retrieval from a successfully established absence.

The current core configuration uses native Cognis with Cross Session OFF for session continuity. That is distinct from cross-session memory. Memory is not required to demonstrate this question → retrieval → response path.

## 2. Full cloud Marketplace integration

Prepare the application using [Cloud application setup](../../../app/CLOUD-SETUP.md), then follow [Lyzr integration setup](../../LYZR-PLATFORM-PLAN.md). Google Cloud hosts the marketplace frontend/application backend, authenticated business MCP service, and Cloud SQL business/policy data. **Lyzr hosts the agent. No Google ADK agent deployment is required.** The shared cloud guide includes an SDK baseline; selecting Lyzr routes this investigation to Lyzr’s hosted agent instead. Existing working infrastructure should be reused rather than provisioned again.

Before the demo, confirm Cloud SQL is running, the cloud web/backend and MCP services are healthy, and the separate Lyzr Marketplace agent has the cloud MCP connection attached. A tool appearing in a registry or being attached does not prove successful runtime access. Verify its endpoint and an authenticated read. A laptop tunnel is a different configuration and should not be used for this cloud walkthrough.

1. Open the **cloud marketplace application → Support**, select **Lyzr**, and start a fresh conversation.
2. Ask **“What is the status of order-1?”**, using a confirmed current order ID if your fixture differs.
3. Follow with **“What is the payout status for this order?”** Compare the answer with current business-tool evidence. Buyer payment and seller payout are separate facts.
4. Open the **Marketplace agent’s native Lyzr trace** for the matching run. Show the investigation, MCP tool arguments/results, final response and evidence. Confirm the business tool calls use the cloud connection.
5. Inspect available execution latency and usage. If Langfuse is configured, it can show the application boundary; Lyzr’s native trace shows the hosted internal execution. Logs and traces are not proof of answer quality by themselves.

The application backend holds the Lyzr inference credential. The MCP connection holds a different credential for the business backend. Keep secrets out of prompts, recordings and frontend code. Preserve instructor/shared resources when learners provision their own.

## Optional native memory reference

The following is a separate reference experiment, not a required step of either walkthrough.


The core demo keeps **Cognis ON / Cross Session OFF**. This optional experiment temporarily turns Cross Session ON for a separate Basics agent **you own**, then restores its original setting. It uses four model calls and synthetic preferences only. Do not target the instructor's agent. The current Studio UI may show an enabled Memory card without exposing Cross Session configuration or owner-scoped record inspection; the parameterized runner is the verified API path.

1. Complete the Basics setup for your own agent. Confirm it is named **Support Agent Basics**, has native Cognis and the fictional KB, and has no external tools. Copy its own 24-character agent ID. Keep `LYZR_API_KEY` private in your environment or ignored `app/.env`; never put the value in source, prompts, shell arguments or screenshots.
2. From the repository root run:

   ```bash
   cd app/lyzr/basics
   python3 verify_cross_session.py --agent-id YOUR_OWN_BASICS_AGENT_ID --wait 35
   ```

   Studio-created agents do not need a local deployment manifest. The script reads your agent, temporarily enables native Cognis Cross Session with preference-only retention guidance, and attempts restoration in `finally`. It refuses a Basics target with external tools.
3. Read the output receipt path, `passed`, `inference_requests` and restoration result. Inspect the JSON rather than treating an acknowledgement as evidence. The runner creates fresh synthetic owner/session IDs and a unique **cobalt-sparrow-...** marker, checks a zero-record baseline, and sends a user preference for that heading plus **Finding, Evidence and Next action**. No direct memory-add call seeds the result.
4. Inspect `native_records`: match content and `original_content` to the seed question, and match `owner_id`, `agent_id` and source `session_id`. Then inspect the fresh same-owner question **“What support answer headings do I prefer?”** Expected: the generated marker and three headings. Formation, provenance and fresh-session recall are separate checks.
5. Inspect another fresh same-owner question **“What is the payout status of order-demo-2?”** Expected fixture fact: **released**, grounded in the KB, with the saved heading format. Preference memory and business evidence are different sources. For the different synthetic owner, inspect zero records and **“What support answer headings do I prefer?”** returning no verified preference.
6. Confirm `restored_original_memory_configuration` is true. For the course Basics default this means Cross Session OFF again. If restoration failed, restore the recorded original configuration before another run. Remove only your own synthetic lab memories using supported native record controls; the runner's restoration does not itself delete those records.

**Bounded reference result:** four native API calls verified automatic extraction, a saved record with matching original user text and owner/agent/source-session provenance, fresh recall, answer use and one other-owner negative check. The saved rehearsal used marker cobalt-sparrow; repeat runs generate a fresh suffix. See `app/lyzr/basics/cross-session-verification.json`. This is not a universal isolation, timing or deletion guarantee. A separate native Playground New Chat smoke check can be documented, but API evidence does not establish an unperformed cross-session UI rehearsal.

The verified main demonstration is the order-demo-1 lookup, its same-chat payout follow-up, and the fresh-chat unknown-order check. Native UI rehearsal returned quantity 2, held and no such order respectively, with actual KB source chunks visible in Activity. The ambiguous fresh-chat and eligibility questions are optional observations; they have not been included in that acceptance claim. The main demonstration is complete after A–C. Do not repeat deployment steps during every query. Use actual results rather than guaranteed model wording.
