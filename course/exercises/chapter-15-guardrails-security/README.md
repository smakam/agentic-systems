# Chapter 15 — Guardrails and Agent Security

The package reuses four existing Security demo cases: built-in input privacy, output-only privacy, Presidio card blocking and Lakera on retrieved attack content. The slide deck presents combined OWASP risks, runtime controls, security design and prevention/detection/response.

- [Instructor walkthrough](instructor-demo.md): each case has setup, numbered actions, expected observations and resets.
- [Learner exercise](exercise.md): repeat the comparisons and inspect their boundaries.
- [Worksheet](worksheet.md): record settings, outcomes, enforcement stage and evidence.
- [Recorded evidence](recorded-evidence.md): supplied results and limits, with source hashes.
- [Separate solutions](solutions/answers.md): review after completing the exercise.

Use the existing isolated test Support workspace and local Langfuse. Presidio/Lakera prerequisites are in the [existing setup guide](../../../app/docs/GUARDRAILS-MANUAL.md). No new detector integration or script is required. Live rehearsal can incur model and hosted-screening usage charges; saved evidence is labelled separately. This package was authored from existing code/reports; no new security runs were performed during this revision. Owner rehearsal remains.

After testing, restore Clean policy, gateway Off, private-instruction example Off and memory Off. Do not change business records to match a forged document. Conversation/memory ownership and read-only business access are different controls; role-specific business SQL/RAG authorization is not claimed.
