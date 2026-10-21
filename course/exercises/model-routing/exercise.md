# Model routing learner exercise

## Workspace for this activity

Use the [Test workspace](http://127.0.0.1:5179), **Support workspace**, with the disposable **market_test** database. Inspect routing evidence in [local Langfuse](http://localhost:3000), project **marketplace-support**. The normal marketplace on port 5178 does not provide these prepared lab controls.

Use the test UI to understand how classifiers select a model and how scope controls when that choice is made. Ask the supplied questions, inspect Langfuse, and document what actually happened. A route selection and a correct answer are separate observations.

## Before you begin

1. Open the [Test workspace](http://127.0.0.1:5179/) and sign in as the demo operator. Open **Support workspace**.
2. Select **OpenAI Agents SDK**. Keep **Use long-term memory** and **Allow memory changes** off.
3. Set **Test policy document → Clean policy** and wait for preparation to finish. Set **Gateway guardrail → Off**, **Source-authority prompt → On**, and the private-instruction example to **Off**.
4. Record the test database revision and demo clock. Do not reset the shared database or run another fixture-changing exercise concurrently.
5. Confirm the routing panel offers **Keyword rules**, **Built-in heuristic v2**, and **LLM · GPT-5 Nano**. These are the three live choices in this exercise. The historical six-classifier study is separate.

These runs make paid provider calls. This is an understanding and documentation exercise, not a statistically meaningful benchmark. The prepared answer pool is Nano/GPT-5. The LLM classifier itself uses Nano. The heuristic v2 choice uses LiteLLM's bundled trained classifier, not the older default heuristic from the historical study.

## Part A — Compare three classifiers

Use these exact questions:

- **Q1:** `Show the purchased product and quantity for order-2.`
- **Q2:** `Investigate whether order-2 is ready for seller payout. Explain the shipment evidence and settlement conditions.`

Run the six cases below. **Start a fresh conversation before every case**, even if you did not change a setting. Keep all preparation settings unchanged.

| Case | Mode | Classifier | Scope | Question |
|---|---|---|---|---|
| A1 | Native LiteLLM routing | Keyword rules | Per question | Q1 |
| A2 | Native LiteLLM routing | Keyword rules | Per question | Q2 |
| A3 | Native LiteLLM routing | Built-in heuristic v2 | Per question | Q1 |
| A4 | Native LiteLLM routing | Built-in heuristic v2 | Per question | Q2 |
| A5 | Native LiteLLM routing | LLM · GPT-5 Nano | Per question | Q1 |
| A6 | Native LiteLLM routing | LLM · GPT-5 Nano | Per question | Q2 |

For each case:

1. Select the row's mode, classifier and scope. Start the fresh conversation and submit its exact question.
2. Copy the final answer into your report. Open its cited evidence and note whether it supports the answer.
3. Click **Routing trace ↗**. Select the first **Gateway routing decision → Model input** observation for the answer call. Switch **Detail view: Preview → Attributes** and read **Metadata**.
4. Fill one row in Table A using the exact fields listed below. If a field is absent, write **not present**; do not infer it from the answer.
5. Open the corresponding **generation** observation and record its model. Keep the classifier model separate from the answer model.
6. Inspect the later calls in that question. Note whether they retained the selected model and whether the cause indicates continuation.

### Table A — Your classifier observations

| Case | Policy | Tier | Decision cause | Classifier model, if present | Routed alias | Actual answer model | Answer and evidence check | Trace link |
|---|---|---|---|---|---|---|---|---|
| A1 | | | | | | | | |
| A2 | | | | | | | | |
| A3 | | | | | | | | |
| A4 | | | | | | | | |
| A5 | | | | | | | | |
| A6 | | | | | | | | |

Use these metadata fields:

| Field | What to record |
|---|---|
| `routing_policy` | Requested prepared policy |
| `routing_classifier` and `routing_scope` | Classifier and decision scope |
| `routing_decision.tier` | Assigned complexity tier |
| `routing_decision.cause` | What produced or reused the decision |
| `routing_decision.classifier_model` | Model used for LLM classification, when present |
| `routing_decision.routed_model` | Selected answer-model alias |
| `model` | Model version recorded by the gateway audit; cross-check the generation model |

**Write three short observations:** Did the classifiers agree on Q1? Did they agree on Q2? Did selecting a stronger model guarantee a correct answer? Support each statement with your table and evidence.

## Part B — Compare scope with one classifier

Keep **Mode → Native LiteLLM routing** and **Classifier → LLM · GPT-5 Nano** for both cases. Change only the scope.

Use this exact question sequence:

1. `Hi.`
2. `Investigate whether order-2 is ready for seller payout. Explain the shipment evidence and settlement conditions.`
3. `For order-2, calculate the seller's net payout after fees.`

### Case B1 — Per conversation

1. Select **Scope → Per conversation** and start a fresh conversation.
2. Ask all three questions in sequence in that same conversation. Do not click New conversation between questions.
3. For each answer, open the trace and inspect the first gateway routing decision in **Attributes → Metadata**.
4. Record the tier, cause, classifier model if present, and actual answer model in Table B. Also copy each answer and check its evidence.
5. Identify whether later questions reused the first selection. Look for `session_affinity_pin`. Complete this sequence without a gateway restart or a long pause; a pin can expire.

### Case B2 — Per question

1. Change **Scope → Per question**. Confirm a fresh conversation starts.
2. Ask the identical three-question sequence in that same new conversation.
3. Fill the remaining Table B rows. Inspect the first gateway routing decision for each user question, then the later model calls within that question.
4. Look for a fresh `llm_classifier` decision on each user question and `user_turn_continuation` on calls after tools. A fresh decision may still choose the same model.

### Table B — Your scope observations

| Case | Question number | Tier | Decision cause | Classifier model, if present | Actual answer model | Fresh decision or reuse? | Answer and evidence check | Trace link |
|---|---|---|---|---|---|---|---|---|
| B1 | 1 | | | | | | | |
| B1 | 2 | | | | | | | |
| B1 | 3 | | | | | | | |
| B2 | 1 | | | | | | | |
| B2 | 2 | | | | | | | |
| B2 | 3 | | | | | | | |

**Write two short observations:** Which policy reused its first selection? Which policy made new decisions, and did its model change? Explain why three model calls within one question do not mean three separate per-question decisions.

## What to hand in

One Markdown document containing:

1. Workspace revision/clock and the selected preparation settings.
2. Completed Tables A and B, final answers, evidence checks and trace links.
3. The five short observations requested above.

No code changes, JSON upload, or new evaluation dataset are required. Record allowed failures or unexpected choices honestly. A missing gateway decision is **inconclusive**, not proof that routing worked. Do not include API keys.

## Cleanup

Select **Mode → Normal support model** to start a fresh ordinary conversation. Leave the policy document clean, guardrail off, source authority on, and private-instruction example off. Keep your recorded runs; do not delete other learners' records or reset shared data.

## References

- [Instructor demo and setup](instructor-demo.md)
- [Separate reference answers](solutions/answers.md) — read after completing the exercise
- Optional historical context: [18 classifier cases](evidence/eighteen-classifier-cases.md) and [six scope conversations](evidence/six-scope-conversations.md). These are dated studies, not expected outputs for this live exercise.
