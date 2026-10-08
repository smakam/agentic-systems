# OWASP security lesson: protections beyond model behavior

Updated October 7, 2026. **Bounded chapter experiments complete; slides, speaker notes, homework and recording packaging deferred.** Teach the difference between model guidance, gateway detection and enforceable tool/application boundaries. A relevant example is not complete coverage of a risk category.

## Two additional demonstrations

[Step-by-step guide for your own run](SECURITY-BOUNDARY-DEMO.md).

[Completed results and repeatable command](../results/security-boundaries-2026-10-07/REPORT.md): real memory MCP operator/support ownership checks (including known-ID update/delete rejection, allowed owner control and disabled-write rejection), plus two synthetic marker probes through GPT-5.4. The model repeated visible user text and withheld the private marker. Only the permission test demonstrates deterministic middleware enforcement; the marker outcome is model behavior for one prompt. No real secrets were used, and temporary test rows were cleaned up.

## LLM risk map — 2026 edition

Use the [official published 2026 list](https://github.com/GenAI-Security-Project/GenAI-LLM-Top10/blob/main/2026/README.md). Its numbering differs from the historical 2025 table in the course plan. This map supersedes that table for new teaching materials.

| Category | Marketplace evidence / teaching scope |
|---|---|
| LLM01 Prompt Injection | [Direct and RAG Lakera comparisons](SECURITY-CHAPTER-DEMO.md); model refusal differs from gateway blocking. Bounded cases only. |
| LLM02 Sensitive Information Disclosure | Built-in/Presidio input/output masking and blocking; [post-filter input audit](../results/gateway-input-audit-2026-10-07/REPORT.md). Original app history/logs remain unsanitized. |
| LLM03 Excessive Agency | Read-only business tools and SQL/database restrictions; denied payout-action request. Personal memory writes require permission. |
| LLM04 Supply Chain | Explain trusted model/MCP/provider dependencies, pinning and secret handling. No dedicated compromise experiment. |
| LLM05 Data and Model Poisoning | Forged RAG policy/source-authority trials demonstrate document contamination and false factual claims, not training-data/model poisoning. |
| LLM06 Unbounded Consumption | Existing [cost-budget test](../backend/tests/test_integration.py) and [MCP tool-call budget test](../backend/tests/test_mcp.py); distinguish model-turn, time/cost and tool-call limits. No extra paid loop demo required. |
| LLM07 Misinformation | Reuse gold-answer evaluation and evidence/citation checks. Source-authority guides conflict interpretation; it does not validate every fact. |
| LLM08 Hidden Context Exposure | [Synthetic marker control/disclosure test](../results/security-boundaries-2026-10-07/REPORT.md). One model refusal is not guaranteed confidentiality. |
| LLM09 Vector and Embedding Weaknesses | [Effective-date and restricted-reader retrieval tests](../backend/tests/test_integration.py); poisoned corpus overlap. Role-specific document access is not implemented, so do not claim a retrieval authorization demo. |
| LLM10 Improper Output Handling | Unsafe model-generated SQL is validated; database permissions provide another boundary. Reuse [SQL rejection tests](../backend/tests/test_integration.py) and [MCP checks](../backend/tests/test_mcp.py). Not a claim covering all output/rendering sinks. |

## Agentic risks and scope

Use [OWASP Agentic Applications Top 10 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/) as a separate lens: goal hijacking relates to our injection cases; tool misuse relates to read-only/SQL constraints; identity and privilege abuse relates to owner-bound memory MCP; memory contamination relates to explicit-save permissions and provenance. Existing memory tests verify ownership/write controls, not all automatic-extraction poisoning attacks.

Explain inter-agent trust, supply-chain compromise, cascading failures, human over-trust and rogue-agent behavior using the worker/reviewer architectures. These are discussion topics, not newly tested attacks or a completed Agentic Top 10 benchmark. No need to invent operator-only RAG documents just for the demo: current business SQL/RAG access is intentionally shared and read-only.

## Recording structure

Brief OWASP map → direct memory tool permission demo with allowed/denied controls → synthetic hidden-context demonstration → existing runner limits and residual risks. Refer back to the guardrail lesson for injection and privacy experiments rather than repeating them. Finish required course experiments and finalize the outline before section-by-section slides, notes, homework, demo refinement and recording.
