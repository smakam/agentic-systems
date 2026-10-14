# Optional exercise: connect your full cloud marketplace to Lyzr

This is the one optional Chapter20 integration exercise. The required lesson is the native Basics demonstration. Complete [Cloud Setup](../../../app/CLOUD-SETUP.md) first with your own cloud chat/backend, authenticated business MCP service and database/policy store working.

## What to do

Follow [LYZR-PLATFORM-PLAN.md](../../LYZR-PLATFORM-PLAN.md) to connect your existing cloud stack to a separate Lyzr marketplace agent. The plan contains the architecture, connection setup, secret destinations, deployment steps and validation questions. Preserve the separate Basics agent and instructor resources. Do not repeat those implementation instructions in your submission.

## What to document

Submit one architecture diagram and a table recording:

- Your UI, backend, Lyzr agent, MCP and data/policy placement.
- Authenticated tool names/arguments and returned evidence for **“Show the items and quantities for order-2.”**
- Same-chat **“What is their total quantity?”** behavior and a fresh-chat comparison.
- Configured model, session identity, native Activity/trace link, and optional application trace.
- Which component owns the loop, tool permissions and business data.
- Observed cost drivers, failures, untested checks and your cleanup.

Use your own fixture’s expected values. Do not submit credentials. If observing the instructor rather than deploying, label the result **observation only**. There is no second cloud exercise or required memory benchmark. Compare your work with [solutions/answers.md](solutions/answers.md).

## Optional native memory observation

Separately from the cloud integration assignment, you may follow [instructor-demo.md, Part D](instructor-demo.md#d-optional-native-cross-session-memory-experiment) on an agent you own. Document the ON configuration, zero-record baseline, automatically extracted preference and provenance, fresh same-owner recall/business answer, other-owner negative check, and restoration to your previous setting. Run `python3 verify_cross_session.py --agent-id YOUR_OWN_BASICS_AGENT_ID --wait 35` from `app/lyzr/basics`, with a private API key and your own separate Basics target. The script makes at most four model calls, inspects native records and restores the prior memory setting; inspect its receipt and restoration status. Native UI acknowledgement/formatting alone is not record evidence. This is optional; the core demo remains Cross Session OFF.
