# Chapter 6 exercise: Model and gateway

**Status:** API/code rehearsal complete for the OpenAI path; recording rehearsal remains separate.  
**Estimated time:** 25–35 minutes for the core tasks after the environment is ready. Optional extensions take additional time.

## Your tasks

Keep your results locally and compare them with the reference solution. Nothing needs to be submitted.

**Part 1:** Repeat the model-alias comparison and Support-versus-Operator usage checks covered in the demo. Follow the steps below and save your answers, evidence and Langfuse traces.

**Part 2:** Add and call a new model alias. If you want a further challenge, test response caching in an isolated setup.

## Learning goal

Observe how a gateway lets an application keep a stable model alias while the mapped model changes, and how gateway identities support workload-level usage and estimated-cost attribution.

## Prerequisites and lab setup

- Complete Chapter Four and keep the normal main/test workspaces running.
- Run the commands below from the application's `app` folder. Python 3, Git, Docker and the current course checkout are required.
- This rehearsed isolated lab uses an OpenAI API key from your existing `.env`. The main application also supports OpenRouter, but this specific lab's business-path rehearsal used OpenAI only.
- The lab runs its own gateway, backend, synthetic database and response cache. It preserves your normal gateway and both marketplace workspaces. API calls incur provider charges; exact amounts vary.

```sh
python3 scripts/chapter-06-lab.py setup
```

The script builds the current backend and creates the lab services and scoped Support/Operator identities without printing credentials. Results are saved under `app/test-output/chapter-06-lab`. If setup is interrupted, run the cleanup command below before retrying. The lab gateway is at `http://localhost:4006`; its backend is at `http://127.0.0.1:58006`. Use the regular local Langfuse instance to inspect the generated traces.

The fixed questions are:

1. “What are Cedar & Co.'s captured amount and unpaid balance?”
2. “What must happen before a seller payout can be released?”

With the supplied clean seed, captured is ₹4,998.00 and unpaid is ₹4,498.20 at revision 1. Policy requires delivery, the 24-hour hold, and no blocking requested/approved/received return. Keep this data fixed during the comparison.

## Part 1 — Repeat what was covered in the demo

### 1. Change the model behind an existing alias

The application always requests `support-model`. Start with GPT-5.4:

```sh
python3 scripts/chapter-06-lab.py questions gpt54
```

Open `gpt54-1.json` and `gpt54-2.json` in the results folder. Inspect each answer, evidence, tool calls and latency; open its `metrics.trace_id` in local Langfuse. Record correctness against the expected facts above.

Change only the isolated gateway's model behind that alias, then repeat the same questions in fresh conversations:

```sh
python3 scripts/chapter-06-lab.py model nano
python3 scripts/chapter-06-lab.py questions nano
```

Compare the `nano-1.json` and `nano-2.json` receipts with the GPT-5.4 receipts. The prompt, fixed questions and business revision remain the same; model-chosen tools may differ. Use gateway usage records for the mapped-model cost estimate. The application's static model label/rate estimate can lag an alias remapping, so do not use that field as proof of the provider model or invoice.

The original GPT-5 nano snapshot retires December 11, 2026; this is the recorded comparison route, not a perpetual model-availability guarantee. Future route replacements need their own validation.

Restore the original mapping before continuing:

```sh
python3 scripts/chapter-06-lab.py model gpt54
```

### What to check and record

Complete one row per question and model in a comparison table:

| Question | Alias and mapped model | Correctness/evidence | Tool behavior | Usage/tokens | Estimated cost | Latency | Langfuse trace |
|---|---|---|---|---|---|---|---|
| Lookup |  |  |  |  |  |  |  |
| Policy |  |  |  |  |  |  |  |

Add a short recommendation explaining which mapping you would use for this workload and why. Include the before/after mapping and evidence that you restored the original mapping.

### 2. Attribute usage to Support and Operator

Keep the restored GPT-5.4 mapping. The previous questions used the authenticated Support account. Send the same lookup through the Operator account and inspect the two scoped identities:

```sh
python3 scripts/chapter-06-lab.py operator
python3 scripts/chapter-06-lab.py usage
```

Open `operator.json` and its Langfuse trace. Gateway usage is grouped under `chapter6-support` and `chapter6-operator`, though both permit `support-model` and `embedding`. Support totals include both model comparisons and setup indexing, so the totals need not be equal. In the regular gateway UI, the equivalent course identities are `marketplace-support` and `marketplace-operator`; rerun normal startup after updating the course checkout to load that implementation.

### What to check and record

Provide the gateway view/export reference and a small Support-versus-Operator table with request count, usage/tokens and estimated spend. State that the gateway estimate is for attribution and is not the provider invoice.

## Part 2 — Additional challenges

### 1. Add a new alias

```sh
python3 scripts/chapter-06-lab.py new
```

The lab adds `learner-model` mapped to GPT-5.4 and sends a small “READY” request through the same gateway API. Inspect `new-alias.json` and the generated lab config. Identify the alias, configured provider model and successful returned content; a returned alias alone is not independent proof of the provider mapping.

### 2. Test gateway response caching (optional advanced challenge)

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

See [`solutions/README.md`](solutions/README.md). The solution describes the expected checks; model-generated wording and measured cost/latency can vary, so use the supplied facts and captured telemetry rather than a memorized answer.
