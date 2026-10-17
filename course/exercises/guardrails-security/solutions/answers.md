# Chapter 15 — Separate solutions

Review after completing the worksheet. These are recorded observations and grading criteria, not promises that a fresh model run reproduces every response.

| Case | Expected evidence | What the evidence establishes |
|---|---|---|
| Input privacy | Forwarded gateway input shows `[EMAIL_REDACTED]` | The configured pre-call filter transformed that input before the answer model; original app history may remain raw. |
| Output-only privacy | Original input retained; emitted output email replaced | Response redaction occurred after generation; input was not protected by this post-only profile. If no email was emitted, the run does not prove output masking. |
| Presidio card | Named CREDIT_CARD rejection; app BLOCKED; model-call error | The configured detector blocked that request before answer generation. It is different from a model refusal or service failure. |
| Lakera retrieved attack | Test passage retrieved; subsequent model request rejected | Indirect content was screened before the next model call, after retrieval. Earlier successful calls are possible. Without retrieved payload evidence, the trial is inconclusive. |

## Saved controls

The harmless security quotation was blocked: a false positive for the intended allow policy. Review the actual context, detector verdict and policy; changes should be regression-tested against malicious and harmless cases.

The forged factual payout exception was allowed by Lakera. An injection detector does not verify transaction truth; compare actual database records, source provenance and policy applicability before acting. Do not blindly trust retrieved claims or the detector’s allow decision.

## Grading the worksheet

Accept a factually supported report of an unexpected fresh result. Require profile/fixture settings, a trace or raw saved result, the correct enforcement stage, and a specific limitation. Do not award proof of input masking from output alone, proof of blocking from generic errors, or proof of resistance when the test content was not retrieved.

A block or denied call can create a review signal. A confirmed false positive may require policy correction; a true violation may require restricting capability; a service failure requires separate operational investigation. Automated alerts are a general design capability, not a completed setup in this exercise.

## Sources

- [Support UI results](https://github.com/smakam/agentic-systems/blob/main/course/exercises/guardrails-security/recorded-evidence.md#support-ui-results)
- [Gateway input audit](https://github.com/smakam/agentic-systems/blob/main/course/exercises/guardrails-security/recorded-evidence.md#gateway-input-audit)
- [Built-in filters](https://github.com/smakam/agentic-systems/blob/main/course/exercises/guardrails-security/recorded-evidence.md#built-in-filters)
- [Presidio](https://github.com/smakam/agentic-systems/blob/main/course/exercises/guardrails-security/recorded-evidence.md#presidio)
- [Lakera](https://github.com/smakam/agentic-systems/blob/main/course/exercises/guardrails-security/recorded-evidence.md#lakera)
