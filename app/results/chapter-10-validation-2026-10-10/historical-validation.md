# Chapter 10 validation — October 10, 2026

Final automated preparation checks pass. The owner still reviews slides, performs UI demos/exercises, and checks the speaking notes.

## Scope and environment

Production session selection is unchanged. The supplied strategy implementation operates only in the lab runner. `reset_lab.sh` reads the fixed market_eval baseline and restores the disposable ch10_session_lab destination. Fixed business-data fingerprints matched before and after the final demos: `bd1efa43a686ab178a59d024d70e5c7036eee902775b1eaab21f9c2965154095`.

Final live runs used support-model mapped to openrouter/openai/gpt-5.4 in a temporary separate LiteLLM proxy, funded with the existing OpenRouter account. The original direct route was gpt-5.4-2026-03-05 and ran out of credits. OpenRouter's general model ID is recorded separately; no claim of identical dated snapshot behavior is made. No automatic fallback model was configured.

## Three demos

Eleven question runs completed. The initial order status at revision 2 was pending. A same-conversation follow-up returned the prepared quantity of two without another business lookup. Dispatch through the shared marketplace command handler advanced the disposable lab to revision 3; the next question fetched two fresh evidence items at that revision and answered dispatched.

The window fixture stored seven prior question blocks, selected six, preserved complete tool pairs, and excluded cedar-window-731 from actual next-call input while retaining it in PostgreSQL. The answer wrongly said the label had never been provided. This is a limitation of the truncated-input answer, not a statement about stored history. Show stored-versus-supplied evidence rather than rely on recall wording.

## Developer comparison

Four real SDK answer calls and one real summary call completed from the identical supplied seven-block fixture. Limits of two and six omitted the early label. The eight-block limit included all seven available blocks and recalled the label correctly. Summary plus two recent blocks also recalled it correctly. All stored fixture prefixes remained unchanged.

Post-run inspection of actual model inputs confirmed every strategy retained current investigation metadata: revision 1, clock 2026-09-27 12:00:00+00:00, document revision fe36211d2849ebbe. The reference runner now asserts this on subsequent runs as well.

Summary plus two used 1,209 serialized characters and 2,254 answer-call input tokens, compared with 790 characters and 2,137 input tokens for all seven available blocks. Summary generation added 385 tokens. This small example demonstrates recall and overhead, not token savings. Smaller windows returned misleading answers about the missing label; contract-check completion does not imply all answers are accurate.

## Other checks

Three offline tests pass: complete tool pairs and immutable storage, rejecting orphaned tool results, and preserving recent evidence with a labelled summary/source hash. The real SDK selector against PostgreSQL selected six blocks, and the copied lab baseline matched the fixed source. Script syntax checks pass. The eight-slide deck passed package/layout/font/import checks and all slides were visually inspected.

Earlier gateway startup and overlapping-reset attempts were invalidated and excluded from the final comparison. The valid strategy comparison completed before the full demo reset. Earlier direct-provider credit failure is preserved separately. Automated shared-handler testing does not claim browser-click rehearsal.

## Evidence

- ../../../course/exercises/session-state/solutions/demo-results-2026-10-10.json — final three demos and captured model inputs.
- ../../../course/exercises/session-state/solutions/strategy-results-2026-10-10.json — four strategies, summary usage and captured input.
- offline-validation-2026-10-10.json — matching fingerprints and actual SDK selector.
- demo-results-interactive-2026-10-10.json — earlier completed interactive-database run.
- demo-results-lab-partial-2026-10-10.json — earlier direct-provider credit failure.

Runnable setup, reset and cleanup are in README.md. Only supplied lab destinations should be reset or removed.
