# Chapter 6 exercise: Model and gateway

## Learning goal

Keep an application's model alias stable while changing the model behind it, then compare answers, traces and usage attributed to separate gateway identities.

## Your tasks

**Part 1:** Repeat the instructor's model-swap demo in the normal Test workspace and compare Support-versus-Operator usage.

**Part 2:** Use the isolated command-line lab to add a new alias and, optionally, test response caching.

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

## Part 2 — Additional challenges (isolated CLI lab)

These tasks use a separate disposable gateway and database, not the normal Test workspace. From the application's `app` folder, run:

```sh
python3 scripts/chapter-06-lab.py setup
```

The lab backend is `http://127.0.0.1:58006`; its gateway is `http://localhost:4006`. It creates its own `market_test` in `course-ch6-db`, separate from the normal Test database. Results are under `app/test-output/chapter-06-lab`. This lab's rehearsed provider path uses the OpenAI API key in your existing `.env`; provider calls incur charges. Keep normal main/test services running. If setup is interrupted, run the cleanup command at the end before retrying.

### 1. Add a new alias

```sh
python3 scripts/chapter-06-lab.py new
```

The lab adds `learner-model` mapped to GPT-5.4 and sends a small “READY” request through the same gateway API. Inspect `new-alias.json` and the generated lab config. Identify the alias, configured provider model and successful returned content; a returned alias alone is not independent proof of the provider mapping.

### 2. Test gateway response caching (optional advanced challenge)

**Before you finish: disable response caching and confirm that the next request makes a fresh model call. Do not leave caching enabled after this exercise.**

Use only the isolated lab; do not enable caching on the normal course gateway.

```sh
python3 scripts/chapter-06-lab.py cache
```

The script keeps the synthetic request fixed and records A miss/repeat hit, B miss/repeat hit, then a fresh B call after clearing. Check `cache-checks.json`: repeated cached responses retain the same response ID and carry the cache-key header. Cross-model requests have distinct identities. The final cleared response has a new ID and no cache-key header.

In the installed gateway, Redis clearing and `/cache/delete` alone left an in-process copy. The verified lab therefore deletes the entry, clears only its disposable Redis, and restarts only its disposable gateway to clear both layers. It then proves a new model response. Never clear the shared Langfuse Redis. Explain why reusing stored answers for mutable business data requires a freshness policy; this challenge uses a static prompt, not a changing order.

### What to check and record

Include the request sequence and gateway evidence for hit, cross-model miss, second-model hit and fresh call after clearing/expiry. Explain the difference between provider prompt caching (the model is still called) and gateway response caching (a matching stored answer can be returned without a new inference).

## Cleanup

```sh
python3 scripts/chapter-06-lab.py cleanup
```

This stops only the named Chapter Six lab services and removes its temporary credential files. It leaves your normal gateway, main/test workspaces and local Langfuse traces untouched. Keep the answer/usage/cache receipts for self-checking; do not publish credentials. No main or test reset is needed.

## Reference solution

See [`solutions/answers.md`](solutions/answers.md). The solution describes the expected checks; model-generated wording and measured cost/latency can vary, so use the supplied facts and captured telemetry rather than a memorized answer.
