# Chapter 6 exercise: Model and gateway

## Learning goal

Keep an application's model alias stable while changing the model behind it, then compare answers, traces and usage attributed to separate gateway identities.

## Your tasks

**Part 1:** Repeat the instructor's model-swap demo in the normal Test workspace and compare Support-versus-Operator usage.

**Part 2:** Add a new alias in LiteLLM and call it from Playground, then optionally try response caching in the Test workspace.

Keep your results locally and compare them with the reference solution. Nothing needs to be submitted. Allow about 25–35 minutes for Part 1 once your environment is ready; the advanced tasks take additional time.

## Before you begin

- Complete the environment setup and run the current course application with the Test model-mapping control available.
- Open the [Test workspace](http://127.0.0.1:5179/), [LiteLLM](http://localhost:4000/ui/) and [Langfuse](http://localhost:3000/).
- Use Support with the OpenAI Agents SDK runtime. Keep memory Off, gateway guardrails Off, clean policy documents and the same other controls throughout. Do not enable a routing or agent-design experiment.
- Do not make purchases, advance the clock, reset data or edit policies during the comparison. Use the policy evidence returned by your own environment to judge the answers.
- Model requests incur provider charges. Gateway spend is an estimate, not a provider invoice.

## Part 1 — Repeat the demo in the Test UI

### 1. Change the model behind a stable alias

1. In **Support model mapping**, click **Restore default** and confirm GPT-5.4.
2. In LiteLLM **Models + Endpoints**, find `support-model-test`. Record its mapped model. Also confirm the main `support-model` remains mapped to GPT-5.4.
3. Start a fresh Support conversation and ask: **What is the current returns policy?** Save the answer, cited policy evidence and trace reference.
4. In that new Langfuse trace, inspect **Gateway output → Model input → Attributes → metadata → model**. Record the actual provider model for each model call. The generation's alias alone does not prove the resolved model.
5. Choose **GPT-5 Nano** in the Test mapping control. The control starts a fresh conversation. Refresh LiteLLM and confirm the same Test alias now maps to Nano.
6. Ask the identical question with unchanged data and controls. Compare the new answer and evidence, and verify Nano in this new trace. Model-chosen tools and the number of calls may differ.
7. Optionally repeat with GPT-5. Use a new conversation for every mapping and check the newest trace rather than an earlier test.
8. Finish with **Restore default** and verify `support-model-test` is back on GPT-5.4. Confirm the main alias is unchanged.

The selector changes the Test alias's actual model definition. It does not change key permissions or redirect a key to an evaluation alias. Both Test keys continue to allow only `support-model-test` and `embedding`. This mapping applies to normal SDK Support and Operator requests throughout Test; specialized routing, evaluation, judge and hosted-runtime paths are separate.

### What to record

| Model | Alias / resolved model | Correctness and policy evidence | Tool behavior | Tokens / estimated spend | Latency | Trace |
|---|---|---|---|---|---|---|
| GPT-5.4 | | | | | | |
| GPT-5 Nano | | | | | | |
| GPT-5 (optional) | | | | | | |

Explain which mapping you would choose for this workload and why. One policy question does not establish a general model-quality ranking. Include evidence that the Test default was restored and the main mapping stayed unchanged.

### 2. Compare Support and Operator usage

With GPT-5.4 restored, ask the same policy question in a fresh Operator conversation in Test. In LiteLLM Usage, compare `marketplace-test-support` and `marketplace-test-operator` for the relevant time range. Both allow the same two aliases but have separate usage attribution. Save request counts, tokens and estimated spend, noting any prior activity included in the totals. Do not expect the cumulative totals to match.

The gateway identities identify application workloads; they do not grant marketplace business permissions. No database cleanup or service shutdown is needed for Part 1—just restore the mapping and keep your evidence.

## Part 2 — Additional challenges

These tasks use the existing LiteLLM gateway and Test workspace. No new application, database or lab environment is needed.

### 1. Add and call a new model alias in Playground

1. Open LiteLLM as the local administrator. Go to **Models + Endpoints → Add Model**.
2. Choose **OpenAI** as Provider and select **gpt-5.4-2026-03-05** under **LiteLLM Model Name(s)**. This is the verified OpenAI example; use a model and provider available in your configured account.
3. In the **Model Mappings** table, change **Public Model Name** to a unique name such as `learner-model`. Keep the underlying model unchanged. Do not reuse an existing course alias.
4. Use existing provider credentials if available. For the course's OpenAI environment, the **OpenAI API Key** field can contain `os.environ/OPENAI_API_KEY`; this references the key already configured inside the gateway. Leave **API Base** blank for this OpenAI example, including clearing any browser-autofilled text. Do not put a provider secret into your exercise notes.
5. Click **Add Model**. Confirm the success message and the new alias's mapping in **All Models**.
6. Open **Playground → Chat**. Use **Current UI Session** as **Virtual Key Source**, keep the endpoint `/v1/chat/completions`, and select the new alias. Ask: **Reply with the single word READY.**
7. Save the alias, configured provider/model and successful response. The response name alone is not proof of the provider mapping; use the model definition too.

The administrator's UI session can call the new alias. If you instead choose a restricted virtual key, use a separate practice key that permits this alias; do not expand the normal Test Support/Operator keys or alter their existing mappings. No application-code change is required. You may remove only your newly created practice alias and practice key after saving your evidence.

### 2. Test gateway response caching in the Test workspace

1. Return to the [Test workspace](http://127.0.0.1:5179/) as Support, using the normal SDK runtime with memory and guardrails Off. Keep the same model, data, policy documents and other settings throughout this comparison.
2. Under **Response caching**, select **Enable response cache**. Changing this setting starts a fresh conversation.
3. Ask **What is the current returns policy?** Wait for the answer, then proceed immediately to the next step; leave trace inspection until after both requests. The first matching request normally has no stored response yet.
4. Start another **New conversation**, leave caching enabled, and immediately ask the identical question within two minutes. Now inspect both Langfuse traces: select each generation → Attributes → Metadata → `gateway_response_cache_hit`. A value of `true` means LiteLLM returned a stored response for that model call. The answer also shows how many model responses came from cache. If you spend more than two minutes examining the first trace before repeating, the entry can expire and the repeat will correctly miss.
5. Clear **Enable response cache**. Ask the same question in the fresh conversation created by the change. Confirm `gateway_response_cache_hit` is `false` for every model call and that the recorded response IDs differ from the cached response.

**Before you finish: leave Enable response cache unchecked. Do not leave caching enabled after this exercise.**

An agent answer can contain several model calls; some may hit while others miss because their full model inputs differ. A generation still appears in the SDK trace on a gateway cache hit. Use the explicit cache-hit metadata and response IDs, not missing spans or speed alone, as evidence. Repeating a question later in the same conversation adds history and may miss; use fresh conversations for the controlled comparison.

The course uses a short-lived, local, exact-match response cache with ordinary requests uncached by default. The Test checkbox opts only eligible requests in. Cache identities distinguish users, selected models, business revisions and policy versions. Entries expire after two minutes. A different prompt, changed context or expired entry can require a new model call. Do not enable caching globally in LiteLLM's Redis settings for this exercise, and do not flush the shared Redis used by Langfuse.

Gateway response caching reuses a completed response without a new model generation on a hit. Provider prompt caching still calls the model to generate a new response. App list-rate cost estimates are not a measurement of charges saved by response caching or a provider invoice.

### What to record

Save the three trace references (first request, repeated request with caching On, request with caching Off), the per-call hit/miss fields and response IDs. Explain why cached answers can become stale, and show that the checkbox is Off at the end. No database cleanup or additional service shutdown is needed.

## Reference solution

See [`solutions/answers.md`](solutions/answers.md). Model wording and measured latency vary; assess policy correctness using retrieved sources and assess cache behavior using gateway evidence.
