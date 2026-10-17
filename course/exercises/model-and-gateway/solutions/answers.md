# Chapter 6 reference solution: Model and gateway

The core exercise repeats the instructor demo in the normal Test UI. Only the advanced new-alias and response-cache tasks use the isolated command-line lab. Exact answer wording, cost and latency vary.

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

Use the separate CLI lab setup and cleanup in the exercise for these advanced tasks. They do not use or reset the normal Test database.

### 1. New alias

The solution adds a distinct alias with a compatible model mapping, calls it through the same gateway request format, and captures a successful response/trace. It leaves the shared starting configuration restored after the test.

### 2. Gateway response cache

With all messages and request parameters fixed:

1. The first model A request is a miss and calls the provider; its repeat is a hit.
2. Switching to model B is a miss because the model is part of the cache identity; the repeat on model B is a hit.
3. Clearing or expiring the B entry makes the next identical request a miss and triggers a fresh provider call.

Accept gateway cache status/logs or equivalent request evidence that demonstrates whether inference occurred; speed alone is not proof of a hit. Provider prompt caching is distinct: the model still generates a new answer, though cached input processing may have different pricing. A response-cache hit reuses a prior answer, so learners must discuss whether the data can become stale and how invalidation is handled. Remove test entries and restore the isolated configuration.

## Review checklist

- [ ] Same question, policy evidence, data and controls used for both model mappings
- [ ] Only the alias mapping changed, then was restored
- [ ] Correctness checked against policy sources and trace evidence
- [ ] Support and Operator are distinct identities with separate usage attribution
- [ ] Gateway estimates are labeled as estimates, not provider invoices
- [ ] Optional cache claims are backed by hit/miss/provider-call evidence
- [ ] No credentials are present in the saved notes


## Dated rehearsal evidence

Recorded validation (instructor-local evidence; not distributed) contains five completed MCP questions with correct expected facts, five local Langfuse traces, distinct Support/Operator gateway usage, the new-alias response and the passing cache sequence. Three request-identity tests cover concurrency, cleanup and MCP key propagation. The instructor's Drive chapter notes link the same report under the chapter's `_authoring/rehearsal-2026-10-12` evidence folder.

The sample 18-case model-selection counts shown in the slides are historical and separate from these focused rehearsal questions. Both models answered the two rehearsal questions correctly; do not turn those checks into a new full-suite score.

### Cache clearing in the installed version

Delete the recorded entry, clear only the lab Redis, and restart only the lab gateway. Clearing Redis or using `/cache/delete` alone did not clear its in-process copy in this installation. The successful sequence proved a new provider response after both layers were cleared. A header, response ID and call record are stronger evidence than speed alone.

### UI capability tour

In the installed LiteLLM UI, inspect Router Settings → Loadbalancing → Reliability & Retries; Response Cache → Cache Settings; and Settings → Logging & Alerts → Alerting Types. These pages were inspected without saving settings or sending alerts. Availability is distinct from enabling a feature.
