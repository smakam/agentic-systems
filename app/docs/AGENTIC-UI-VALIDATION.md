# Agentic UI Review Validation

Validated on 14 November 2026, on the isolated `codex/marketplace-agentic-ui` branch from merged main.

## Automated Checks

- Backend: **373 passed, 10 optional skipped, 30 subtests passed**, using `python3 app/scripts/test-a2ui-preview.py` and its dedicated disposable regression database.
- Frontend and MCP protocol: **60 passed**, using `node --test src/*.test.js mcp-app-server.test.mjs` in app/frontend.
- Production frontend and self-contained MCP UI resource builds: passed (`npm run build`). Vite reports the large-bundle warning; this is a teaching build, not a bundle-size optimization change.
- `git diff --check`: passed.
- Reusable isolated review-start script: exercised against its existing dedicated copy; health responding after restart.

## Live And Browser Checks

- Declarative status investigation completed through the local support agent/gateway. Source rows showed paid order-1, captured payment, two items, and delivered shipments.
- Controlled status selected table/d0 and rendered the fixed view. Component identifiers were corrected to the protocol's supported identifier form during browser verification.
- Declarative status rendered Text, RecordTable, a Button label/Button, and Column. Widgets were implemented by the application.
- Open-ended status generated a complete HTML/CSS document and rendered the same order/payment/item/delivery facts. The revised model generates the history button inside the document. Browser inspection confirmed one nonce-authorized application script, no external scripts, and no forms; model scripts and network calls remain blocked. Clicking the generated button produced a new history answer.
- Declarative history returned EventTimeline plus RecordTable, including four recorded events and separate returns/refunds/payout records.
- Controlled history selected timeline/d1 and rendered the fixed timeline.
- Open-ended history generated and rendered a separate HTML/CSS history view; only the application-authored bridge executes.
- MCP Apps SDK initialization, tools/list UI metadata, resources/read HTML, AppBridge/App tool-result delivery, and embedded A2UI rendering succeeded.
- Embedded history: iframe → host → MCP tools/call → authenticated support API → result → iframe completed. Browser inspection confirmed an EventTimeline and a RecordTable.
- Langfuse Observations API v2 returned the comparison observation and mode-specific generation child. Source investigation metadata links the comparison to the original evidence.

## Limits

- Local teaching host only; no third-party assistant installation was tested. MCP embedding is limited to declarative mode here.
- Open-ended execution is sanitized HTML/CSS and generated button markup; an application-authored action bridge handles clicks. Arbitrary model JavaScript is not executed.
- Facts were inspected for these examples, not benchmarked over repeated trials. One oversized HTML attempt reached the output limit and retained text fallback; a compact prompt and retry affordance were then checked.
- Controlled and declarative status outputs both used a table in the observed run. Their model output and decision ownership differ.
- The SDK client tries an optional GET event stream; this stateless server responds 405. Resource/tool POST requests work.
- The inherited A2UI/Zod dependency chain retains an upstream audit finding. Payload limits/validation remain; no audit-clean claim is made.
- Existing Test/production previews were not replaced. The review has its own database container and loopback ports.
- No main merge, production deployment, AG-UI runtime integration, or publication was performed.

## Direct Controlled Renderer Follow-up — 15 November 2026

- Controlled responses now contain a validated `selection`, selected `data`, and application-owned `actions`; they contain no A2UI messages. `ControlledAnswer` renders prebuilt React views without the A2UI processor. Declarative mode retains A2UI.
- Saved legacy controlled presentations offer regeneration rather than silently using the A2UI renderer. Switching modes retains a regenerated presentation.
- Backend: 375 passed, 10 optional skipped, 30 subtests passed on the disposable regression database. Frontend/MCP: 65 passed. Both frontend and MCP resource builds passed.
- Installed only on the normal Test UI (port 5179); Test state preserved during installation and regular preview containers unchanged.
- Live Test request selected a table and data reference with no `messages` field. Browser displayed the prebuilt table, plain-data inspector, and no A2UI message inspector. Its history button returned a new controlled timeline without an alert.
- Declarative mode still renders its RecordTable through A2UI in the browser, with its A2UI message inspector and no alert.
- The code change is on `codex/controlled-ui-direct-rendering`; not yet merged into main.
