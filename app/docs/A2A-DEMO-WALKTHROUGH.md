# A2A experiment: shared demonstration and test sequence

11 November 2026 · Target workflow for the agreed review-branch changes.

**Validation status: implemented on the separate review branch and exercised on 11 November 2026.** Browser checks covered workspace controls, both Agent Cards, account switching, purchase and ordinary seller dispatch. Live API checks covered the status/tracking comparisons, normal and exception records, delivery completion, follow-up tasks and outage/retry; Langfuse observations were read back independently. The entire sequence was not performed exclusively through browser clicks. Use the test workspace at http://127.0.0.1:5179. Preserve the production workspace and main branch.

## Preparation

1. Verify that the test workspace is running the review branch and uses the intended isolated test database. Record the branch revision, database name, demo clock and Langfuse project. Stop if the database is production or unknown.
2. Sign in as support/operator. Open Workspace options → A2A. Confirm the three modes and start with Standard API.
3. Open Langfuse beside the application. Use a recent time window. Record each question's run/trace link so older traces cannot be mistaken for the current call. Record order and shipment identifiers as you create them.

Use ordinary buyer and seller accounts throughout. Keep other testers from changing the shared workspace settings during the sequence. The setting is captured when an order creates its shipments; select the intended mode/scenario **before purchase**. A later setting change does not enroll an existing local shipment or rewrite an existing remote shipment's scenario.

## Part 1: same support workflow, two interfaces

4. In Standard API, switch to buyer and purchase one item. Record its order and shipment. Switch to the seller who owns that item and use ordinary Dispatch. It should follow the local marketplace path.
5. Switch back to support. Verify Standard API is still selected. Start a fresh conversation and ask: “What is the shipment status of order <recorded order>?” Save the answer and trace link. Expect a Standard API request span containing the support investigation, with no delivery-agent call for this local shipment.
6. Select Marketplace A2A and open View Agent Card. Expect the marketplace support card, its endpoint, description, skills and capabilities. Expand Details to inspect the raw card, then close the viewer.
7. Start a fresh Marketplace A2A conversation and ask the same question about the **same local order**. Expect the same factual shipment state; exact wording and model tool choices may differ. In Langfuse, expect an A2A request span with SendMessage, protocol version, task/context identifiers and outcome, enclosing the support investigation. There should be no delivery-agent call for this local shipment.
8. In that conversation ask: “Has it been delivered yet?” Expect a new A2A task within the same context, with conversation history available. Inspect task/context metadata rather than inferring continuity from answer wording alone.

Teaching point: A2A changes the communication contract. It does not require a different model, prompt or reasoning workflow. The Agent Card advertises the service; the executed protocol span is evidence of invocation.

## Part 2: delegation to a separate delivery agent

### Main demonstration: what the delivery agent adds

After creating and dispatching a linked Depot exception shipment, pause before marking it delivered. Use this same shipment for all four questions below, starting fresh conversations when changing modes:

| Mode and question | Expected answer and trace evidence |
|---|---|
| Marketplace A2A: “What is the status of order <exception order>?” | Marketplace says dispatched. The inbound request uses A2A; no delivery-agent call. |
| Marketplace A2A: “Can you track its delivery and give me more details?” | Reports dispatched and explains detailed delivery tracking is unavailable here. No invented location, delay reason or arrival estimate; no delivery-agent call. |
| Multi-agent A2A: “What is the status of order <exception order>?” | Still reports the marketplace state, dispatched. No delivery-agent call is needed for basic order status. |
| Multi-agent A2A: “Can you track its delivery and give me more details?” | Retrieves the recorded depot exception, reason and supporting tracking/schedule evidence. Langfuse shows the delivery delegation and remote status/problem-detail tools. |

This is the central value comparison: the same question gains access to another service's evidence. A changed answer alone is insufficient proof; inspect the executed remote call. This demonstration does not claim that a simple status lookup requires an LLM agent.

For the same linked shipment in Multi-agent A2A mode, first ask “What is my order status?” Expect the marketplace state and no delivery-agent call. Then ask “Can you track my delivery and tell me whether there is a delay?” Expect remote tracking evidence and a delivery-agent call. Natural wording variants should work; this must not rely on exact trigger phrases. Repeat the detailed-tracking request in Standard API and Marketplace A2A modes: expect an explanation that remote tracking is unavailable in that mode, with no remote invocation. The nine live mode/question comparisons passed; protocol observations confirmed which questions did and did not delegate.

9. Select Multi-agent A2A and Normal transit. Open View Agent Card; expect separate marketplace and delivery cards. Switch to buyer, create a **new order**, and record its shipment. Switch to seller and Dispatch using the regular button. Expect marketplace dispatched plus a linked delivery record reporting in transit.
10. Return to support and confirm the mode/scenario survived account switching. Start a fresh conversation and ask: “Is the shipment for order <normal order> on schedule?” Expect recorded delivery status and schedule evidence. In Langfuse, inspect the support request, outbound delivery A2A call, inbound delivery task and delivery agent's model/tool activity. The remote status tool must run; problem details are conditional.
11. Change only the scenario to Depot exception **before creating another order**. Switch to buyer, purchase, then switch to the correct seller and Dispatch. Record this second order/shipment. Expect marketplace dispatched while the remote delivery state is exception.
12. Return to support, start a fresh conversation, and ask: “What is the shipment status of orders <normal order> and <exception order>, and why is either shipment stuck?” Expect normal transit for the first and the recorded depot problem for the second. The exception investigation must check status and supporting problem details. Exception does not automatically mean overdue; compare against the recorded demo clock and expected delivery time.
13. Ask a follow-up about the exception. If support reuses valid earlier evidence, a new remote call is not mandatory. For a reliable live demonstration of remote investigation, use a fresh conversation and a specific shipment question. Never describe an absent remote call as having occurred.
14. Switch to the exception shipment's seller and use ordinary Deliver. Return to support, start a fresh conversation, and ask its status again. Expect both marketplace and delivery service to report delivered, with delivery time based on the demo clock. Do not expect the earlier exception to remain the current state.

Teaching point: the marketplace resolves the shipment; the remote delivery agent investigates its own recorded evidence. Booking and manual delivery updates are deterministic backend operations. This example demonstrates an agent boundary; these simple status checks could also be implemented as a workflow.

## Persistence and failure checks

15. Change the workspace to Standard API. In a fresh conversation, ask about the previously linked exception shipment (before step 14 delivery completion, if demonstrating the exception contrast), or the still-dispatched normal shipment. Expect marketplace-only evidence, such as dispatched, and **no delivery-agent call** in Langfuse. Repeat in Marketplace A2A: the inbound request uses A2A, but there must still be no outbound delivery call. Switch back to Multi-agent A2A and start a fresh conversation; remote findings become available again without deleting or recreating the saved shipment link. New purchases in Standard API remain local. Also verify old remote findings are not presented as current evidence after switching modes.
16. In a controlled maintainer test, temporarily make the delivery service unavailable and dispatch a newly purchased multi-agent shipment. Expect a visible error and no marketplace transition to dispatched. Restore the service and retry; expect one linked booking and a successful dispatch. Do not take down a shared service during someone else's walkthrough.
17. Confirm an unavailable delivery investigation is reported as unavailable, rather than replaced with invented fresh status. Confirm failures are visible in protocol traces/logs and credentials are absent.

## Execution record

| Check | Implementer result and evidence | User result |
|---|---|---|
| Test branch/database/clock verified | Verified: review branch, market_test, actual demo clock recorded | Pending |
| Standard API local baseline | Passed live request and Langfuse request span | Pending |
| Marketplace A2A same-order comparison | Passed live request and A2A protocol span | Pending |
| Follow-up: new task, same context | Passed live follow-up and ownership/task regression tests | Pending |
| Both Agent Cards and raw details | Browser: one marketplace card or both cards on demand | Pending |
| Normal remote shipment | Passed; in transit, status tool only | Pending |
| Exception and recorded reason | Passed; exception, status and problem-detail tools | Pending |
| Ordinary Deliver synchronizes both states | Passed live command and delivered tracking evidence | Pending |
| Settings and shipment associations persist | Browser account switching plus purchase-intent regression test | Pending |
| Outage, retry and trace failure evidence | Live dispatch 503 left pending; recovery retry succeeded; protocol failure unit checks | Pending |

Populate actual trace links, order references and observed results after execution. Keep failures and skipped checks explicit. Complete this review on the separate branch before requesting a merge to main.
