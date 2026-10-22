# Chapter 16 — Native model routing instructor demo

## Workspace for this activity

Use the [Test workspace](http://127.0.0.1:5179), **Support workspace**, with the disposable **market_test** database. Inspect routing evidence in [local Langfuse](http://localhost:3000), project **marketplace-support**. The normal marketplace on port 5178 does not provide these prepared lab controls.

Use the **test workspace**, [127.0.0.1:5179](http://127.0.0.1:5179/), database `market_test`. The normal workspace at port 5178 is a separate application. These cases use freshly generated answers and incur provider charges. They are a routing demonstration, not a new benchmark.

## Preparation

1. Start the existing app stack from `app/` using `scripts/start.sh`; it generates the provider configuration and retains the existing security filters. For this lab, build and start `memory-backend` and `memory-frontend` with `compose.memory.yaml`. Keep `LITELLM_CONFIG_PATH=./infra/litellm.provider.generated.yaml` when restarting the gateway.
2. Run `python3 scripts/provision-gateway-keys.py` after the gateway is ready. It adds the prepared route aliases to the existing evaluation key. The key remains on the server, never in the browser.
3. Open the test UI, sign in as **operator**, and open **Support workspace**. Select **OpenAI Agents SDK**.
4. Set **Test policy document → Clean policy**. Wait for indexing to finish. This changes only the test document corpus; it does not reset business records. Do not run other fixture-changing labs concurrently.
5. Use **Gateway guardrail → Off**, keep **Source-authority prompt** enabled, and leave private-instruction mode off. Keep long-term memory off. Record the database revision and demo clock.
6. Confirm that **Model routing demo** offers fixed Nano, fixed GPT-5 and native LiteLLM routing, with Keyword rules, Built-in heuristic v2 and LLM classifier choices. A missing panel means the test backend or its evaluation key is not configured; it is not a classification outcome.

The prepared configuration is [routing-demo.models.yaml](../../../app/infra/routing-demo.models.yaml). Pool: `eval-nano` → GPT-5 Nano; `eval-5` → GPT-5. Native tiers map SIMPLE to Nano and MEDIUM / COMPLEX / REASONING to GPT-5. These labels describe request complexity, not model quality.

The installed LiteLLM 1.102.1 license limits customized heuristic routers and custom classifier prompts. This lab has **one keyword profile at question scope**, **one native heuristic-v2 profile at question scope**, and **two LLM profiles using the same shipped classifier prompt**. The heuristic-v2 profile uses the bundled trained artifact and is included in the learner exercise; it differs from the older default heuristic in the historical study. The historical business rubric in our results is different; it is linked below. No license state or vendor code is modified.

## Part A — Compare classification policies

### Case A1 — Explicit lookup

1. Set **Mode → Native LiteLLM routing**, **Classifier → Keyword rules**, **Scope → Per question**. A routing-setting change creates a fresh conversation.
2. Ask: `List the products and quantities in order-2.`
3. Check the answer and expand its evidence. On the seeded baseline, the order contains two Ceramic Mug Sets from Everyday Studio. Verify against the current records if the test database was changed.
4. Read the routing badge: requested profile and actual answer model. This keyword rule should select Nano; confirm the native tier and cause in the trace rather than infer it from the wording of the answer.
5. Change **Classifier → LLM · GPT-5 Nano**. Repeat the exact question in the new conversation.
6. Compare the two decisions and answers. The LLM may classify this as MEDIUM and choose GPT-5; a lookup requiring database/tool work is not guaranteed SIMPLE under its shipped rubric. This is a result to inspect, not a required switch.

### Case A2 — Causal payout question

1. Choose **Keyword rules / Per question** and start a fresh conversation.
2. Ask: `Why has the seller not been paid for order-2, and what must happen before payout is eligible?`
3. Inspect the returned status and policy evidence. In the seeded baseline, payout is held, shipment is pending, delivery has not been recorded, and the delivery wait condition has not been satisfied. Never accept a claim that an execution has occurred just because the policy permits it.
4. Inspect the routing decision: the explicit `why` rule escalates to COMPLEX → GPT-5.
5. Switch to **LLM / Per question** and repeat. Compare tier, actual model and answer quality. Do not compare cost from isolated spans while omitting classifier calls.

### Optional fixed-model control

1. Select **Fixed GPT-5**, which starts a new conversation, and repeat one question.
2. Optionally repeat with **Fixed GPT-5 Nano**.
3. Compare correctness and elapsed time. These fixed modes do not classify. The app's cost cap uses a conservative stronger-model rate; it is not a complete routing bill.

## Part B — Hold the classifier fixed; change scope

Use the same LLM classifier, answer pool, security settings and question sequence in both conversations. Ask follow-ups in the **same** conversation; do not click New conversation between questions.

### Case B1 — Per conversation

1. Set **Mode → Native LiteLLM routing**, **Classifier → LLM · GPT-5 Nano**, and **Scope → Per conversation**.
2. Ask `Hello.` This makes the first selection easy to inspect. Record the tier, actual model and cause. In verification, this selected Nano.
3. Ask `Why has the seller not been paid for order-2, and what must happen before payout is eligible?`
4. Ask `What exact amount would the seller receive after fees for order-2?`
5. Confirm that the same candidate remains selected across all three user questions and tool continuations. In Langfuse, later calls should show `session_affinity_pin`. The native pin lasts up to 3,600 seconds; expiry or a gateway restart starts a new selection.
6. Compare each answer with the current records. The seeded expected net is ₹1,618.20. A pinned model is not proof of a correct answer.

### Case B2 — Per question

1. Change **Scope → Per question**. Confirm that the UI starts a fresh conversation.
2. Repeat the exact three questions, in the same order, without changing the other settings.
3. Inspect the first model call of each new user question. It should contain a new LLM classification decision. The selected model may stay the same or change.
4. Inspect subsequent model calls after tools. They should reuse the user-turn decision, rather than classify each tool continuation anew.
5. Compare all three answers, not just the last one. This case demonstrates decision timing; a model switch or a quality improvement is not guaranteed.

## Part C — Read the routing decision in Langfuse

1. Click the answer's trace link. Open **support-investigation** to see the requested policy, classifier, scope and backend-owned session identity.
2. Open **Gateway routing decision → Model input**. Under **Metadata**, inspect `routing_decision.router_model_name`, `tier`, `routed_model`, `cause`, `conversation_continuing`, `classifier_model` and `classifier_cost` when present. Depending on the Langfuse view, nested fields appear flattened with dots.
3. Open the corresponding **generation** observation. Its model name is the actual provider answer model, also shown in `actual_answer_model`. It is separate from the classifier model.
4. Interpret `llm_classifier` as a new LLM decision; `session_affinity_pin` as reuse of the conversation selection. `user_turn_continuation` means reuse within the current question after a tool call. Missing classifier cost is not zero.
5. A classifier's own gateway input audit may have no routing decision yet. It is a separate call, not an answer-model generation. The audit span is an observation of input and routing metadata, not a second charged generation.
6. Check failures before claiming a route worked. If the run failed, the UI shows no completed answer model or only completed calls before failure. A selected profile alone does not prove dispatch.

The gateway audit uses OpenTelemetry. The installed Langfuse v4 deployment uses `/api/public/v2/observations` for readback; legacy trace/observation API 404s do not mean ingestion failed. See [Langfuse Public API](https://langfuse.com/docs/api-and-data-platform/features/public-api).

For the learner exercise, use the separate [numbered instructions and observation tables](exercise.md). The learner questions differ from these demo questions.

## Cleanup

1. Set **Mode → Normal support model** to create a fresh ordinary conversation.
2. Leave **Clean policy**, guardrail Off, source authority on, and private-instruction mode off. Restore memory preferences only for subsequent ordinary use.
3. Retain the saved demo runs for review. Do not reset the shared test database or delete unrelated conversations.
4. Routing profiles remain available only in the configured test SDK workspace. Main workspace model settings and business tool permissions remain separate.

## Historical results and teaching boundaries

- [Classifier study](https://sreeni.blog/2026/09/30/model-routing-part-1-choosing-a-classifier/): 18 known cases; six configurations selected previously saved candidate trajectories. Cost is a replay estimate including classifier overhead.
- [Scope study](https://sreeni.blog/2026/09/30/model-routing-part-2-choosing-the-scope/): six scenarios × three questions × four policies = 72 freshly generated answers. Whole-conversation pass counts were 4/6 for Nano and both routing policies, 6/6 for GPT-5.
- [Historical business rubric](../../../app/eval/routing-v2-prompt.txt) and [classifier definitions](../../../app/eval/routing-final-v1/classifiers.json): bounded lookups are simple; causal reconstruction, policy applied to live data, time eligibility and reconciliation are complex. Buyer payment, seller payout and buyer refund are distinct; current state can hide failed prior attempts; any complex required part escalates the request.
- The small one-pass known-case studies illustrate methodology, not a general ranking. Business-context setups did better on those cases, but no matched ablation proves that context alone caused the improvement.
- The fresh native demo verifies implementation mechanics; it does not replace or reproduce the historical benchmark. Per-call and named-stage routing are explained conceptually, not presented as tested results.

[Verified rehearsal and checks](verification.md)
