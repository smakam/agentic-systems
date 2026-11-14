# Agentic UI Review Validation

Validated on 14 November 2026, on the isolated `codex/marketplace-agentic-ui` branch from merged main.

## Automated Checks

- Backend: **373 passed, 10 optional skipped, 30 subtests passed**, using `python3 app/scripts/test-a2ui-preview.py` and its dedicated disposable regression database.
- Frontend and MCP protocol: **58 passed**, using `node --test src/*.test.js mcp-app-server.test.mjs` in app/frontend.
- Production frontend and self-contained MCP UI resource builds: passed (`npm run build`). Vite reports the large-bundle warning; this is a teaching build, not a bundle-size optimization change.
- `git diff --check`: passed.
- Reusable isolated review-start script: exercised against its existing dedicated copy; health responding after restart.

## Live And Browser Checks

- Declarative status investigation completed through the local support agent/gateway. Source rows showed paid order-1, captured payment, two items, and delivered shipments.
- Controlled status selected table/d0 and rendered the fixed view. Component identifiers were corrected to the protocol's supported identifier form during browser verification.
- Declarative status rendered Text, RecordTable, a Button label/Button, and Column. Widgets were implemented by the application.
- Open-ended status generated a complete HTML/CSS document and rendered the same order/payment/item/delivery facts. Browser inspection found zero scripts and links; the frame has an empty sandbox allowance and no-script/no-network CSP.
- Declarative history returned EventTimeline plus RecordTable, including four recorded events and separate returns/refunds/payout records.
- Controlled history selected timeline/d1 and rendered the fixed timeline.
- Open-ended history generated and rendered a separate HTML/CSS history view; browser inspection confirmed no scripts.
- MCP Apps SDK initialization, tools/list UI metadata, resources/read HTML, AppBridge/App tool-result delivery, and embedded A2UI rendering succeeded.
- Embedded history: iframe → host → MCP tools/call → authenticated support API → result → iframe completed. Browser inspection confirmed an EventTimeline and a RecordTable.
- Langfuse Observations API v2 returned the comparison observation and mode-specific generation child. Source investigation metadata links the comparison to the original evidence.

## Limits

- Local teaching host only; no third-party assistant installation was tested. MCP embedding is limited to declarative mode here.
- Open-ended execution is sanitized static HTML/CSS; arbitrary model JavaScript is not executed.
- Facts were inspected for these examples, not benchmarked over repeated trials. One oversized HTML attempt reached the output limit and retained text fallback; a compact prompt and retry affordance were then checked.
- Controlled and declarative status outputs both used a table in the observed run. Their model output and decision ownership differ.
- The SDK client tries an optional GET event stream; this stateless server responds 405. Resource/tool POST requests work.
- The inherited A2UI/Zod dependency chain retains an upstream audit finding. Payload limits/validation remain; no audit-clean claim is made.
- Existing Test/production previews were not replaced. The review has its own database container and loopback ports.
- No main merge, production deployment, AG-UI runtime integration, or publication was performed.
