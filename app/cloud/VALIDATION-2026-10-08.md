# Cloud deployment verification — October 8, 2026

Project: `marketplace-app-511005`, region `asia-south1`. [Application](https://marketplace-web-327903210973.asia-south1.run.app/). Checks used synthetic course data and the owner's stored credentials without printing secret values.

| Check | Observed result |
|---|---|
| Terraform rollout | Three Cloud Run services deployed; final update changed four resources, deleted none |
| Initializer | Final corrected image rerun completed successfully; existing data preserved |
| Web/API | Login page loaded; health returned ok; operator and support authenticated |
| Documents | All 20 documents indexed through private gateway; repeat indexing returned zero |
| SQL/RAG answer | Order-2 held for ₹1,618.20; database/event/policy evidence retained |
| Short-term memory | BLUE42 recalled in a follow-up turn |
| Long-term memory | Three-bullet payout format saved and recalled in a new conversation with writes disabled |
| Feedback | Thumbs-down persisted and Langfuse Cloud received one feedback score |
| Built-in privacy | Synthetic email reply masked; gateway input observation contained a redaction marker and no original synthetic email |
| Lakera | Direct instruction attack returned blocked |
| HTTP MCP | Authenticated begin, SELECT and end succeeded across separate requests; payout-2 status held |
| Langfuse | Trace fetched from intended Japan project with model/tool and gateway input observations |

Database is running for owner testing, private IP only. Stop it between labs to reduce compute cost. Runtime services use minimum instances zero.

## Fixes included in learner setup

- Initializer handles LiteLLM-owned objects without requiring superuser access.
- Reader search path, read-only default and statement timeout match local setup.
- MCP registry secret uses the direct psycopg URL format; credential helper safely recognizes the original format. Ten offline credential checks passed.
- Registry credential rotated after diagnostic exposure; old secret version disabled. Do not print database connection exceptions.
- Frontend image includes Langfuse Cloud Japan navigation URL; trace export drains before request completion.

## Limits and follow-up

API acceptance and visible login page are verified; a full owner browser walkthrough remains to do. The HTTP check did not force an instance restart. Presidio sidecars are deployed, but the final cloud answer checks here covered built-in privacy and Lakera. Hosted Google ADK was subsequently switched to the new MCP endpoint on October 8 using separate local/cloud profiles. The same runtime completed its update; deployed URL/secret metadata and a fresh cited payout investigation passed. The original local secret is preserved. Lyzr cloud reconnection and the shared UI runtime adapters are now verified; see the runtime selector addendum below. A fresh-project deployment rehearsal, clean laptop install and learner-repository publication remain pending. No high-availability or production-readiness claim is made.

## Owner-reported first-request failure follow-up

A question after inactivity failed with `APITimeoutError` before tool calls. Gateway startup logs overlapped the request; the same question succeeded when warm in about eight seconds. The cloud client timeout was 40 seconds. Updated it to 120 seconds for Cloud Run IAM connections (local default stays 40); both HTTP and SDK timeouts use the same configurable value. Configuration checks cover local, cloud and explicit override. Minimum instances remain zero. A fully idle gateway cold-start rerun remains distinct from a warm browser check.

The corrected image was deployed successfully. A fresh browser conversation then answered the same order question in 9.73 seconds with two evidence records. This verifies the deployed revision and warm end-to-end path; it does not replace the fully idle cold-start check.

## Runtime selector acceptance addendum

Google and Lyzr cloud order questions, same-session follow-ups and fresh-session native memory recall are verified. Local Lyzr credentials are configured in ignored `app/.env`, both local backends restarted, and the local order-2 question and same-session follow-up passed. Local Google ADC is configured; local main question and follow-up passed. Switching runtime opens a new conversation; Google history restores its bound runtime. Lyzr cloud thumbs-up feedback persisted after reload. The final web image is `course-20261008-r8`; Terraform applied four in-place updates, with no creates or deletes. Google deployment metadata confirms the cloud MCP target, the earlier inconsistent revision did not reproduce in fresh memory-off or memory-on reruns. The verifier now compares the answer with actual tool snapshot metadata; the original cause remains unconfirmed. Native hosted spans stay in platform telemetry; Langfuse receives a marketplace request/answer wrapper.


## Shared answer/evidence and MCP concurrency update

Final r15 web/MCP image: `sha256:f70aaca1a54518c20966cf19135e4db5e87dd9ee7db0f449798695ac0b1340df`. Both services report ready and 100% latest-revision traffic. Shared rendering supports tables/safe breaks; Google event sources and matching Lyzr trace sources feed saved-record/policy viewers. The durable MCP registry now waits asynchronously for investigation row locks. A timed-out Lyzr payout question passed after this fix (80.29 seconds); status tests passed with clickable revision-1 records. See [full validation and screenshots](../BACKEND-SWITCH-VALIDATION-2026-10-08.md).


### Local/cloud business snapshot alignment

On 8 October, the user approved aligning the cloud `market` database with the current local `market` snapshot for easier runtime comparisons. The one-off Cloud Run job completed successfully. Its transaction locked the selected business tables, retained the previous cloud snapshot in `public.business_snapshot_backups`, copied business records, commands, policy chunks including embeddings, revision and clock, then compared every copied row before commit. User accounts/passwords, login sessions, conversations, feedback and personal memories were excluded.

Verified source and destination: revision **24**, clock **2026-09-28 12:00 UTC**, 5 orders, 26 events and 20 indexed policy chunks. Canonical full-snapshot SHA-256: `429e4c7e1bca3beaa6bc0d151fbeb76cff24c2005ffa4caf50b279542c43b924`. Backup identifier: `before-local-alignment-b7d62e4a64471f6b`. The backup is accessible only through the existing bootstrap database identity; runtime roles were explicitly denied access. This is a one-time alignment, not continuous synchronization; `market_test` and `market_eval` were not changed. Existing answers retain their historical snapshot; start a fresh conversation for comparisons.

Implementation: `scripts/sync-business-snapshot.py`, run inside the local backend with existing Google ADC. The script refuses to replace a cloud snapshot that has already advanced beyond revision 1. The job completed with one success; its verification log was read through Cloud Shell after local ADC log readback encountered a quota error.

A fresh Google ADK question through the cloud marketplace confirmed revision 24 and the aligned clock, with **2 orders on 27 September and 1 on 28 September**. These counts matched both direct local SQL and the freshly formatted local SDK answer.

User manual confirmation: local order-summary formatting accepted; cloud marketplace with **OpenAI Agents SDK** displayed the detailed Langfuse trace. Google ADK displayed the expected `marketplace-hosted-answer` wrapper; its detailed calls remain in Google native telemetry.

### Local working mode and cloud cost pause

At the user's request, the Cloud SQL stop operation completed successfully on 8 October. Readback showed activation policy `NEVER` (the instance API still labels the retained instance `RUNNABLE`; the completed stop and NEVER policy control whether its compute runs). Cloud data and rollback snapshot are retained. Cloud marketplace/MCP cannot serve database-dependent requests until restart. Storage and retained backups remain billable. The local SDK stack is healthy. Hosted agents' local-profile switch is tracked separately in the runtime guide.


### Local-first pause acceptance — October 8

Both Google and Lyzr local profile settings were read back as verified by the switching script. Fresh direct local marketplace API questions completed through each hosted runtime while Cloud SQL was stopped. Google reported paid/captured/pending; Lyzr reported paid/captured/held and no return/refund. Saved source evidence was present for both. The first smoke predicate incorrectly required an unrequested payout amount in every answer; the saved responses were regraded for the requested order/payment status and evidence instead, without another inference run. Both passed. Cloud database activation policy is NEVER; restart before using cloud chat/SDK/MCP. Local UI remains on the SDK for the user's recording work.
