# Local restart end-to-end verification — 8 October 2026

Project: `/Users/srmakam/mycode/agentic-systems`.

## Passed checks

| Path | Verified behavior |
|---|---|
| Main SDK | Order-2 status, captured payment, same-session quantity follow-up, saved answer/history |
| Google ADK adapter | Order-2 paid/captured status, same-session quantity follow-up, runtime binding and saved history |
| Lyzr adapter | Order-2 paid/captured status, same-session quantity follow-up, runtime binding and saved history |
| Feedback | Down then up, latest vote persists through a new login for all three runtimes |
| SDK policy retrieval | Policy answer includes delivery/24-hour conditions and pgvector evidence |
| SDK long-term memory | Explicit temporary preference saved, recalled in a new conversation with writes off, isolated from support, deleted afterward |
| Ownership | Support cannot read the operator test conversation (404) |
| Test workspace | Login, all 20 documents indexed, completed order question, lantern comparison in separate conversations |
| Browser | Fresh login, Enter submits, answer table renders, evidence opens, thumbs-up survives reload; runtime change clears the current conversation and reopening history restores SDK |
| Langfuse | Readback of SDK GENERATION/TOOL observations, hosted runtime SPAN observations and three latest user_feedback=true scores |
| Relocation | Container bind mounts reference the new project path; database volumes retained; authenticated public MCP initialization passed |

## Evidence and limits

[API run receipts](results/relocation-e2e-2026-10-08/runs.json),
[Langfuse readback](results/relocation-e2e-2026-10-08/telemetry.json),
and [browser screenshot](results/relocation-e2e-2026-10-08/browser.png).

These checks use the existing local revision-24 business snapshot. Test questions and ratings remain in conversation history; temporary personal test memories were removed. No business transactions were performed. This is a relocation smoke/acceptance run, not an exhaustive regression suite. Native Google/Lyzr long-term memory was not retested in this run; SDK memory was. Hosted agents' internal traces remain in their own platforms.

Initial verification-client failures were corrected: the test workspace allows `127.0.0.1:5179`, not `localhost:5179`; hosted status answers were correct but did not include an unrequested payment amount; a memory harness referenced a field not returned by the API. Supported Langfuse v3 score-list readback was used after older endpoint attempts failed. These were verifier issues, not failed application behavior.

The restart temporarily caused Langfuse initialization to fail while PostgreSQL was being recreated. Restarting its web and worker after PostgreSQL was stable restored HTTP 200 UI and health; subsequent traces and ratings were verified.

Use main `http://localhost:5178`, test `http://127.0.0.1:5179`, and Langfuse `http://localhost:3000`. Cloud SQL and the stopped learner rehearsal VM were not changed.
