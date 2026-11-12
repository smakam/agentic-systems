# A2UI marketplace experiment

Status: implemented and locally verified, 12 November 2026. The common Test preview is running on port 5179. See the Test incident below for the separate data-recovery limitation.

## Purpose

Let the existing marketplace support agent answer a question with a UI composed for that question, while keeping its text answer and source evidence available. Demonstrate the difference between a model choosing a fixed view and a model choosing both components and their arrangement.

## Scope and workspace

After the isolated prototype, combine A2UI with the A2A review branch, as requested. Both experiments are selectable in the same Test workspace. A2UI remains technically independent of A2A and initially requires standard API mode with A2A off. Use no database reset or startup seed. Main and production are outside this change.

The first experiment is read only, with an optional Show order history button. MCP remains the support agent's business-data connection. A2UI messages travel from backend to React over the existing HTTP API. MCP Apps, A2A integration, new delivery-provider integration, refunds, purchases, and UI-triggered business mutations are out of scope.

## User experience

1. In Support → Workspace options, expand A2UI and enable Agent-composed answers. It starts off and resets to off with Reset to defaults.
2. Ask a normal support question. The existing investigation obtains business evidence and produces its normal text answer.
3. A separate presentation-model call receives the question, answer, bounded evidence bindings, and the approved catalog. It chooses components and their arrangement. Application code does not select a fixed layout from question keywords.
4. React renders the validated A2UI result with marketplace styling. Text answer and clickable source evidence remain available alongside it, including when UI generation fails.
5. A collapsed composition inspector exposes the allowed components, presentation instructions, model layout output, final A2UI messages, and separate presentation latency/token counts.

## Component catalog and ownership

The display catalog supports Column, Row, Card, Text and Divider, Button for the single permitted read action, plus three marketplace components:

| Component | Purpose |
|---|---|
| OrderSummary | Compact key/value summary of one returned business record; suitable for order and shipment status |
| EventTimeline | Chronological event records, preserving source order, dates, revisions and evidence references |
| RecordTable | Multiple returned records or comparisons, with application-supplied headers and values |

The model selects instances, supported properties, evidence bindings and arrangement. It can omit irrelevant components and combine a table with a timeline. The catalog and developer prompt explain when each is useful; they do not require all components on every answer.

React owns actual component implementations, typography, color, spacing, responsive behavior and accessibility. The Fieldwork client theme adds the diamond brand mark to each marketplace widget, grouped order status badges and details, rupee/date formatting, event timeline cards, and a high-contrast history action. When a generated view contains marketplace widgets, its complete Markdown answer is shown only in the shared Text answer and sources disclosure, avoiding duplicate tables in the main view. Text-only compositions remain visible. The text fallback is collapsed after successful composition and stays open when composition fails. These render changes also apply to saved A2UI answers without a new model call. Python and React must agree on catalog ID, protocol version, component properties and binding names. Use the official A2UI 1.0 Python compiler/validator and React renderer. Pin compatible packages and verify the emitted messages in the actual browser.

Business values are supplied by the application from evidence already obtained by the investigation. The presentation model may reference only supplied paths; it cannot assign new business data, invent labels for facts, fetch additional records or mutate business state. Evidence is bounded, source-labelled and annotated when truncated. UI summaries do not silently imply a complete dataset. Ambiguous questions remain clarification answers; no order is guessed for presentation.

## Request and response

The existing question request gains an optional A2UI flag. The backend accepts it only in the designated Test preview with the normal SDK runtime and compatible workspace settings. Other runtimes/experiments must not accidentally invoke UI generation.

The normal answer, evidence, run status and metrics remain intact. Optional A2UI metrics contain validated messages, catalog/protocol version, composition metadata and usage. Each answer is an independent surface; follow-ups use the normal conversation history and current evidence rules. Retained prior evidence used by the answer must be included or clearly unavailable to the UI, without being relabelled as a current read.

## Read-only interaction

The model may offer a Show order history button when an order identifier is available in returned evidence. Its label binds to server-supplied data, and its event carries only an allowlisted action reference. The host adds the source answer ID and sends this selection through the existing HTTP question endpoint. The backend verifies conversation ownership, source answer, action name and stored order reference, then constructs the history question itself. It does not trust a client-supplied order ID or free-form button instruction. The normal support agent chooses its history tool and the presentation stage can return an event timeline.

Buttons are optional and disabled while work runs or A2UI is switched off. No refund, purchase or other mutation is offered. A repeated click starts another read, with no business-state change.

## Failure handling and limits

Reject unknown components/properties, literal business facts, unapproved bindings, functions, URLs, unknown actions, model-supplied data, invalid trees and excessive complexity. Validate on the backend and again before browser rendering. Keep bounded output, timeout and component counts. An unavailable model, malformed layout or renderer exception must leave the normal text answer accessible and must not turn a successful investigation into a failed business answer.

The presentation call has its own Langfuse observation, latency and usage. Totals must distinguish investigation and presentation costs. Do not claim two-agent delegation: this is a presentation stage after the existing support investigation.

## Acceptance and verification

- Simple order question: model-generated summary with actual returned facts and text fallback.
- Timeline question: event timeline in source chronology, with no duplicated refund inferred from failed attempts.
- Multi-record question: readable record table; paise remain clearly labelled or formatted deterministically as rupees.
- Two different questions produce inspectably different model-chosen layouts rather than a host-selected template.
- Malformed/active UI payloads are rejected and the text answer survives; only the validated history action is exposed.
- Feature off, reload/history, Reset to defaults and incompatible settings behave predictably.
- Run focused backend contract/failure tests, frontend binding/validation tests, the existing relevant suites and production build.
- Verify the order-history button round trip, stale/foreign source rejection and no mutation.
- Exercise the real model and browser in the isolated preview. Check desktop and narrow layouts, inspect generated messages and confirm sources stay accessible.
- Verify A2A and production previews remain available and no existing data is reset.

## References

- Source research: Homeward and Alder analysis in the AI system series research workspace, dated 12 November 2026.
- [A2UI agent integration](https://a2ui.org/guides/agent-integration/)
- [A2UI client integration](https://a2ui.org/guides/client-integration/)

## Implementation results

The independent prototype verified a real-model RecordTable and an optional history button that returned an EventTimeline. Text fallback also survived invalid layouts and renderer errors. The code is integrated into the common A2A review branch. The combined suite passes 367 backend tests (10 optional skips) and 56 frontend tests; the production build passes. Browser checks in the common Test preview on port 5179 verified both Agent Cards, a completed A2A support request, an A2UI OrderSummary with working source links, and the order-history action returning an EventTimeline. The business revision and order count stayed unchanged across the read-only flow. Reset was also checked after namespacing the A2A/A2UI/RAG component keys; it now leaves one settings panel per experiment. Narrow layouts were checked at 390 pixels without page overflow.

Test incident: a reset-capable OIDC regression was mistakenly run against the shared Test database. Its marketplace orders and support history were reset. The pre-reset browser retained 24 order panels, 93 business event details, and 25 settlement panels; this evidence was saved separately in the research workspace. It is not a full database backup, and full history recovery is not claimed. All subsequent destructive tests use the separate disposable regression database; production was not targeted.

## Running the experiments

Open the existing Test workspace at http://127.0.0.1:5179. Both experiments are on the common review branch; no branch switch is required. To try A2UI, use Reset to defaults to turn A2A off, expand A2UI, enable Agent-composed answers and start a new conversation. Ask for the status of order-1 or order-2, then use Show order history if the model offers it. The model may choose a summary for one record or a table for multiple item rows.

To run A2A, select the desired experiment under A2A; the A2UI toggle turns off for that mode. Existing A2A Agent Cards and delivery scenarios remain available. This first implementation compares the approaches independently rather than composing A2UI inside A2A responses.

Run backend regressions with `python3 app/scripts/test-a2ui-preview.py`. This launcher uses the dedicated database container on its separate Docker bridge network and dummy model credentials. Never run the reset-capable backend suite inside the shared Test backend. Frontend checks use `node --test src/*.test.js` and `npm run build` from the frontend directory.

The local preview update script takes a current Test database dump, disables startup initialization, retains previous containers for rollback and verifies business-state counts and production container identities before and after the update. That deployment backup was taken after the earlier test reset; it is not a recovery of pre-reset history.

Package notes: the pinned React SDK currently brings a Markdown peer-range warning and npm reports four high-severity advisories in its Zod 3 dependency chain. The prototype uses a bounded, validated catalog and passed actual browser rendering; this does not establish production readiness or an upstream vulnerability fix.
