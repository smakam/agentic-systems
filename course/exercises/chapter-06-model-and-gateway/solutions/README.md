# Chapter 6 reference solution: Model and gateway

**Status:** API/code checks passed for the recorded OpenAI lab. Recording rehearsal remains separate. Do not distribute credentials.

The exercise guide is shared by the instructor demo and learner practice. Keep dated rehearsal results linked here, separate from the learner instructions. Speaker notes provide recording cues and reference that same guide.

## Part 1 — Repeat the demo

### 1. Model alias comparison

A correct run changes only the model mapping behind the supplied existing alias. The application request, prompt, fixed lookup/policy questions and data revision stay the same. The learner records the original mapping, captures both answers/traces for each model, compares each answer with the supplied expected facts and evidence, and restores the original mapping.

Expected observations:

- The application continues to call the same alias; the gateway routes it to the newly mapped model without an application-code change.
- Model outputs and tool behavior may differ. Judge correctness and evidence against the supplied answer key; do not score by stylistic preference.
- Usage, estimated cost and latency are recorded from the available telemetry. Exact values depend on the model, provider pricing and runtime, so use the values from the learner's run or the instructor's dated saved results.
- The final mapping matches the recorded original mapping.

A strong recommendation ties the selected model to the workload's quality needs and measured cost/latency trade-offs, and identifies uncertainty or any failed answer. There is no universal winner implied by this exercise.

### 2. Support and Operator attribution

A correct run uses two separately provisioned gateway identities while keeping the model aliases/mappings common. The gateway usage view or export groups the requests and estimated spend under the expected Support and Operator identities. The learner reports the observed totals and identifies the evidence used for attribution. If the identities are not distinct or the dashboard cannot separate them, mark the exercise blocked and fix the setup before claiming a result.

The gateway's attributed cost is an estimate; the provider invoices its account. It is not an individual provider bill or a marketplace authorization boundary.

## Part 2 — Additional challenges

### 1. New alias

The solution adds a distinct alias with a compatible model mapping, calls it through the same gateway request format, and captures a successful response/trace. It leaves the shared starting configuration restored after the test.

### 2. Gateway response cache

With all messages and request parameters fixed:

1. The first model A request is a miss and calls the provider; its repeat is a hit.
2. Switching to model B is a miss because the model is part of the cache identity; the repeat on model B is a hit.
3. Clearing or expiring the B entry makes the next identical request a miss and triggers a fresh provider call.

Accept gateway cache status/logs or equivalent request evidence that demonstrates whether inference occurred; speed alone is not proof of a hit. Provider prompt caching is distinct: the model still generates a new answer, though cached input processing may have different pricing. A response-cache hit reuses a prior answer, so learners must discuss whether the data can become stale and how invalidation is handled. Remove test entries and restore the isolated configuration.

## Review checklist

- [ ] Fixed questions and data revision used for both model mappings
- [ ] Only the alias mapping changed, then was restored
- [ ] Correctness checked against supplied expected facts and trace evidence
- [ ] Support and Operator are distinct identities with separate usage attribution
- [ ] Gateway estimates are labeled as estimates, not provider invoices
- [ ] Optional cache claims are backed by hit/miss/provider-call evidence
- [ ] No credentials are present in the saved notes


## Dated rehearsal evidence

[Recorded validation](../../../../app/results/chapter-06-rehearsal-2026-10-12/REPORT.md) contains five completed MCP questions with correct expected facts, five local Langfuse traces, distinct Support/Operator gateway usage, the new-alias response and the passing cache sequence. Three request-identity tests cover concurrency, cleanup and MCP key propagation. The instructor's Drive chapter notes link the same report under the chapter's `_authoring/rehearsal-2026-10-12` evidence folder.

The sample 18-case model-selection counts shown in the slides are historical and separate from these focused rehearsal questions. Both models answered the two rehearsal questions correctly; do not turn those checks into a new full-suite score.

### Cache clearing in the installed version

Delete the recorded entry, clear only the lab Redis, and restart only the lab gateway. Clearing Redis or using `/cache/delete` alone did not clear its in-process copy in this installation. The successful sequence proved a new provider response after both layers were cleared. A header, response ID and call record are stronger evidence than speed alone.

### UI capability tour

In the installed LiteLLM UI, inspect Router Settings → Loadbalancing → Reliability & Retries; Response Cache → Cache Settings; and Settings → Logging & Alerts → Alerting Types. These pages were inspected without saving settings or sending alerts. Availability is distinct from enabling a feature.
