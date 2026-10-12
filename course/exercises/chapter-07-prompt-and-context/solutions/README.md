# Chapter 7 reference solution

## The separate context queries

| Query | Context to inspect | Expected reasoning |
|---|---|---|
| Entity definitions | Catalog balance metrics, units, grain and current balance rows | Report current amounts in rupees. Unpaid can include held and failed payouts and does not by itself mean release is allowed. |
| Relationships | Catalog relationship definitions, order items, listings/products and sellers | Use item grain and correct joins. Quantity is not the number of order-item rows. |
| Policies | Retrieved settlement policy or runbook, version and effective date | Payout requires delivery confirmation and a 24-hour hold. Active returns can block release. The operator releases payouts manually. |

Fresh run amounts and eligibility depend on the recorded revision and clock. Confirm them from tool evidence instead of copying historical values. The full catalog can include both entity and relationship context even when the question emphasizes one category.

## Static and dynamic input

Stable configuration includes the investigator role, tool contracts, read-only boundaries, citation requirements and freshness rules. Dynamic input includes the question, snapshot metadata, retained messages, catalog results, business query results and retrieved policy passages. Catalog content can be relatively stable while still arriving dynamically through a tool call. Policies are separately retrieved documents, not part of the catalog payload. The relationship map does not imply a separate graph database.

The initial call cannot contain a result from a tool that has not returned. Later calls retain tool calls and evidence. Prior generated prose is not equivalent to fresh verified business evidence.

## The UI context comparison

The request carries separate catalog and document-retrieval suppression options. Each investigation binds those flags to its own read tools, including a separate MCP child process. No ontology file or document changes are necessary. Both controls default off and are available only in the test workspace. Changing a control starts a fresh conversation with memory off.

Both tool calls succeed with empty context. Catalog data is null and policy passages are empty. Retrieval does not fall back to another method. The model should explain missing evidence rather than inventing a policy. Inspect evidence and actual answers; do not equate a completed run with a correct conclusion.

Live successful-empty-context checks showed that the agent attempted SQL after receiving null catalog data. Both catalog-empty runs reached the eight-turn limit without a complete answer. Remaining SQL hints in the stable prompt made query construction possible. Empty policy passages led to an answer declining to confirm policy rules. Restored context retrieved normal definitions and policy evidence. Business state was unchanged. This differs from the earlier explicit-error catalog test, which stopped before SQL.

## Saved observations

The earlier six-run test completed full, reduced and restored conditions for two questions. It produced no incorrect numeric answer or join. For Cedar & Co., all conditions reported captured ₹9,396, refunded ₹4,398, fees ₹499.80, paid out ₹4,498.20 and unpaid ₹0 at that recorded snapshot. Semantic removal reduced the explanation: it omitted held/failed payout and immediate-release distinctions. Relationship removal still returned the correct products, quantities and sellers for order-1.

This is a single exploratory run per condition. Schema names, keys, field descriptions and static guidance remained available. The semantic variant removed several sections together, so it cannot attribute the difference to one definition. Prior training is a possible explanation, not an established cause. Do not require the learner run to reproduce a failure or the historical amounts.

The [historical comparison note](../supplied-trace.md) distinguishes the earlier selected-field ablation from the current UI experiment. Inspect the traces from your own UI run for the current exercise.

## Local review checklist

- Static configuration and dynamic context are distinct.
- Tool results appear only after the tool returns.
- Catalog definitions, business rows and policy text have separate sources.
- Claims and citations correspond to the actual trace.
- The comparison preserves snapshot and instruction controls.
- Reported differences describe observed outcomes, without a forced failure claim.

No submission or advanced challenge is required.
