# Model and gateway — reference solution

The core exercise repeats the instructor demo in the normal Test UI. The additional tasks use LiteLLM Playground and the existing Test workspace; no separate environment is required. Exact answer wording, cost and latency vary.

A successful core run keeps `support-model-test` fixed while its actual model definition changes from GPT-5.4 to Nano (optionally GPT-5), then returns to GPT-5.4. The main `support-model` remains unchanged. Both Test keys retain exactly `support-model-test` and `embedding`, without per-key alias redirects. Normal Test SDK Support and Operator requests use these Test identities; specialized evaluation, routing, judge and hosted-runtime paths are separate.

For each fresh question, inspect the newest matching Langfuse trace. **Gateway output → Model input → Attributes → metadata → model** identifies the provider model for that call. Check each call, since a single answer can need several model calls. Do not mistake an older Nano trace for the new GPT-5.4 request.

For usage attribution, compare `marketplace-test-support` and `marketplace-test-operator` over the chosen time range. Earlier requests and indexing can affect cumulative totals. Restoring the Test mapping completes core cleanup; no database reset or service shutdown is required.

## Part 1 — Repeat the demo

### 1. Model alias comparison

A correct run changes only the model mapping behind the supplied existing alias. The requested Test alias, prompt, returns-policy question, data and other controls stay the same. The learner records the original mapping, captures both answers/traces for each model, compares each answer with the retrieved policy evidence in their environment, and restores the original mapping.

Expected observations:

- The application continues to call the same alias; the gateway routes it to the newly mapped model without an application-code change.
- Model outputs and tool behavior may differ. Judge correctness and evidence against the retrieved policy evidence in the learner's environment; do not score by stylistic preference.
- Usage, estimated cost and latency are recorded from the available telemetry. Exact values depend on the model, provider pricing and runtime, so use the values from the learner's run or the instructor's dated saved results.
- The final mapping matches the recorded original mapping.

A strong recommendation ties the selected model to the workload's quality needs and measured cost/latency trade-offs, and identifies uncertainty or any failed answer. There is no universal winner implied by this exercise.

### 2. Support and Operator attribution

A correct run uses two separately provisioned gateway identities while keeping the model aliases/mappings common. The gateway usage view or export groups the requests and estimated spend under the expected Support and Operator identities. The learner reports the observed totals and identifies the evidence used for attribution. If the identities are not distinct or the dashboard cannot separate them, mark the exercise blocked and fix the setup before claiming a result.

The gateway's attributed cost is an estimate; the provider invoices its account. It is not an individual provider bill or a marketplace authorization boundary.

## Part 2 — Additional challenges

### 1. New alias in LiteLLM Playground

A correct run creates a unique public model name in **Models + Endpoints → Add Model**, preserves all existing course mappings, and calls that new name through **Playground → Chat**. In the verified OpenAI example, the underlying model is `gpt-5.4-2026-03-05`, credentials reference the gateway's existing environment and API Base is blank. The administrator's **Current UI Session** can call the alias; restricted keys require their own explicit permission. Normal Test keys remain unchanged.

Expected evidence is the model definition plus a successful Playground response to **Reply with the single word READY.** A successful local UI rehearsal returned READY. This exercises gateway alias creation without changing the application or creating another database.

### 2. Response cache On/Off in Test

The learner enables **Response caching → Enable response cache** for normal Test SDK support with memory and guardrails Off. They ask the policy question in one fresh conversation and repeat it in another fresh conversation before the two-minute expiry, with unchanged controls and data. The first request fills the cache; the repeat should demonstrate at least one cached model response. Make the two requests back-to-back and inspect the traces afterward. Pausing to inspect the first trace can exceed the two-minute expiry and make the repeat correctly miss. Later model calls can miss if tool results or other full inputs differ.

In each generation's Langfuse metadata, inspect `gateway_response_cache_hit`, backed by LiteLLM's cache-key response header, and `gateway_response_id`. The repeated hit reuses the response ID. The SDK can still emit a generation observation for that call: absence of a generation is not the cache test.

After the learner switches caching Off, a new conversation starts. The identical question produces fresh model responses: all per-call cache-hit fields are false and cached response IDs are not reused. The app's answer receipt reports the number of model responses served from cache. Faster responses alone, matching text alone, or provider cached-input-token counts do not establish gateway response-cache hits.

**Required final step: leave Enable response cache unchecked. Confirm a fresh model call with caching Off before finishing.**

This is request-level opt-in on the existing gateway. Ordinary Main requests remain uncached; no global Redis configuration, database reset or new application is needed. Cache namespaces separate users, selected models, business revisions and policy versions. Cache entries expire after two minutes. Gateway response caching and provider prompt caching are different; app list-rate cost estimates do not measure the actual cache savings.

## Review checklist

- [ ] Same policy question, data and other controls used for each comparison
- [ ] Test model alias stays stable; main mapping and Test key permissions stay unchanged
- [ ] Test model mapping restored to GPT-5.4 after Part 1
- [ ] Answers checked against retrieved policy evidence
- [ ] Support and Operator usage attributed to distinct Test keys
- [ ] New practice alias called successfully from Playground
- [ ] Cache evidence checked per model call in the newest matching trace
- [ ] Response cache disabled and a fresh call confirmed at the end
- [ ] No credentials included in saved evidence

## Verification boundary

The simplified new-alias flow was rehearsed through the installed LiteLLM UI and Playground. The Test SDK cache comparison was also exercised live: the first question had no response-cache hits, the repeated question had a hit on its first model call, and the cache-Off question had fresh responses on both calls. The cache-hit field was read back from Langfuse. These checks demonstrate the workflow, not a general model-quality benchmark or production cache design.

The historical 18-case model-selection report linked from the slides is a separate study. Do not turn this one-question caching demonstration into another full-suite quality score.
