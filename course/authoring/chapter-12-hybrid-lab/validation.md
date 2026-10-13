# Validation — 10 October 2026

All agreed Chapter 12 preparation is complete. Owner review and rehearsal remain.

## Live hybrid path

Deployed temporary Cloud Run service ch12-hosting-415dddbe in asia-south1, with one CPU, 1 GiB, 180-second deadline, concurrency one and zero-to-one instances. The only cloud component is the agent; local chat, history and middleware use a disposable ch12_hosting_lab baseline copy. The worker calls OpenAI directly using GPT-5.4-2026-03-05 through Responses API, and reaches HTTP MCP through a dedicated authenticated HTTPS tunnel. Existing cloud provider secret was reused; no laptop provider key was uploaded.

Two API questions completed in conversation chat-1828fb9bc1: run-a9b1e55228 and run-189623a1ab, three model calls and two tool invocations each. Answers identify the held payout, missing delivery confirmation and required 24-hour post-delivery hold, using fresh retained record/policy citations. Both confirmed investigation cleanup; both saved their local history/results. See solutions/validated-results.json.

An actual UI-submitted follow-up also completed: run-843a4f054b, three model calls, two tool calls, 9.71 seconds, current evidence and confirmed cleanup. The final UI displays the Cloud Run/direct OpenAI/HTTP MCP route; lab memory toggles are disabled and gateway security controls hidden. Token usage is not supplied by this lab worker, and the UI marks it unavailable. See solutions/ui-readback.json.

Initial validation identified a direct-provider compatibility error: GPT-5.4 reasoning-enabled function tools require Responses rather than Chat Completions. A follow-up then reused an old handle; the evidence verifier correctly rejected it. The lab prompt now explicitly requires new evidence on each question, and the two-question sequence plus UI follow-up passed after correction. Refresh is prompt-directed and evidence-checked; it is not an automatic checkpoint or general guarantee of model behavior.

## Local checks and unchanged baseline

Five hosting contract tests passed, covering direct Responses selection/bounded input, citation rejection, cleanup after interruption, authentication/instruction-role boundaries and refusal of the fixed database. Frontend production build passed. Public cloud health returned 200; unauthenticated investigation returned 401. Read-only Docker and existing Cloud Run configuration were inspected for the configuration demo. Both replacement eight-slide decks passed package/layout/note checks and full-size visual review.

Fixed market_eval business fingerprint: bd1efa43a686ab178a59d024d70e5c7036eee902775b1eaab21f9c2965154095, identical to the earlier recorded baseline. The disposable copy was reset after results were saved.

## Cleanup confirmed

Cloud service, both dedicated lab secrets and the lab image package (including old revisions) were deleted. Existing provider secret preserved. Dedicated tunnel stopped; only three Chapter 12 lab containers stopped. Cloud SQL remains STOPPED with activationPolicy NEVER and was not started for this chapter. See solutions/cleanup-readback.json. Shared services and earlier chapter environments were preserved.

The cloud credential helper uses a read-only ADC file with a writable ephemeral CLI cache. Cleanup is safe to retry after a partial deletion and targets only recorded lab resources. The instructor endpoint and tunnel are now unavailable by design; learners deploy their own IDs using the supplied instructions.
