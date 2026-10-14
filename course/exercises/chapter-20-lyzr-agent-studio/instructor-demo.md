# Instructor demo: a standalone Lyzr support agent

## Workspace and preparation

Use **Lyzr Studio → Support Agent Basics → Playground**. Complete [setup-guide.md](setup-guide.md) once before the demonstration. Confirm the supplied orders-knowledge.txt was uploaded into the separate Knowledge Base, indexed and attached to this agent. Uploading it into chat is not KB setup. This lab does not use marketplace chat, SQL, MCP, a tunnel or the existing Marketplace Support agent. The [prepared Basics agent](https://studio.lyzr.ai/create-new-agent/6acf95f3272a149412fd9e7c?tab=playground) passed bounded API lookup, missing-ID and same-session follow-up checks. Native Cognis is enabled with Cross Session OFF. Native Playground lookup, same-chat follow-up and missing-ID checks passed, with actual KB source chunks visible in Activity; label observed results and failures accurately.

## A. Knowledge retrieval and native execution

1. Open the prepared **Support Agent Basics** agent and select **Playground**. Confirm the configured model is **OpenAI gpt-5.4-mini**, the attached KB is **Support_Agent_Basics_Orders**, and native **Cognis is ON / Cross Session is OFF**. Click **New Chat**. Ask **“What products and quantities are in order-demo-1?”**
2. Expected fixture facts: **Ceramic Mug Set, quantity 2**. Inspect the retrieved source record and dataset/as-of marker.
3. Open **Activity** for this response. Expand **kb_documents_retrieved** and inspect the source **storage/orders-knowledge.txt**, retrieved chunk text and its dataset/as-of marker. Confirm the source contains order-demo-1 and quantity 2. Inspect model input/output and latency where available. A KB search is not a Python function-tool call; its relevance score is not a correctness grade.
4. Record the configured and reported model, session identity, source records, latency and usage when available. Missing cost is not zero.

## B. Same-session context versus a new chat

1. In the same chat ask **“What is its payout status?”** Expected: **held**, for order-demo-1.
2. Inspect retained order context and fresh retrieval if it occurs.
3. Optional boundary check: click **New Chat** and ask only **“What is its payout status?”** Observe whether it requests an order ID. Do not call a guessed order memory recall.

## C. Missing records and evidence limits

1. Click **New Chat** again and ask **“What is the payment status of order-demo-999?”**
2. Expected boundary: the complete fictional catalogue contains only order-demo-1, -2 and -3. No payment status should be invented for -999.
3. Distinguish an absent fixture record from failed KB retrieval. If sources are missing, the answer should state the retrieval limit.
4. Optional evidence-limit check, not a passed core rehearsal: ask **“Is order-demo-1 eligible for payout release now?”** The fixture supplies payout status, not eligibility policy or a live clock; inspect whether the answer respects that limit.

## D. Optional native cross-session memory experiment

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
