# Native routing verification — 13 October 2026

LiteLLM 1.102.1, local test UI at port 5179, `market_test` revision 1, clean policy fixture, SDK runtime, memory off and guardrail off. The demo pool is GPT-5 Nano / GPT-5. This verifies routing mechanics; these fresh runs do not establish comparative answer quality.

## Rehearsal

| Scope | Greeting | Payout explanation | Net amount |
| --- | --- | --- | --- |
| Conversation | Nano; new LLM decision | Nano; session pin | Nano; session pin |
| Question | Nano; new LLM decision | GPT-5; new LLM decision | GPT-5; new LLM decision |

All six runs completed. Net amount returned in both conversations was ₹1,618.20. The explanation answers retained held status; these were inspected, not scored by a blinded judge. Native metadata showed `llm_classifier`, `session_affinity_pin` and `user_turn_continuation`. Requested policy/classifier/scope and actual generation models were read back from the same Langfuse traces through its v4 observations API.

Keyword question-scope checks selected Nano for the explicit lookup and GPT-5 for the causal payout question. A browser-run LLM question-scope greeting also completed; its routing badge and trace link were verified in the UI.

## Checks

- Routing boundary / concurrent telemetry tests: 4 passed.
- Gateway identity / cost instrumentation regression tests: 9 passed.
- Provider-switch configuration preservation: 1 passed; native routes, Lakera and existing filters retained.
- Final frontend production build passed.
- API rejected switching a used conversation to a different routing policy before a provider call (400).
- All 16 presentation slides rendered and were visually reviewed; package/layout/font checks passed, including native editable chart data and tables.

The installed license limits customization, so only one keyword profile is registered. Both LLM scope profiles use the same shipped classifier rubric. No license state or vendor code was modified. Existing historical saved-answer studies remain separate.

[Routing metadata readback](verification/native-routing-traces-2026-10-13.json)
