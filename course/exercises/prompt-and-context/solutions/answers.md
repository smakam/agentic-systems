# Prompt and Context — Reference Answers

## UI, database and cleanup

**UI:** [test marketplace](http://127.0.0.1:5179/) from Course Setup; use the role/workspace named in each task. **Database:** disposable practice database `market_test`, separate from main `market` and the fixed evaluation baseline `market_eval`. Test UI changes do not update the main marketplace. Save your questions, results and traces locally.

Use Support with OpenAI Agents SDK and a fresh conversation for each condition. Business questions are read-only; the context controls change returned tool data, not stored catalog, documents or business records.

**Cleanup:** restore both suppression controls to off and the original workspace options. No business database reset is required; saved conversations and traces remain.


## The integrated context investigation

Question: **For Cedar & Co., which payouts are currently held, why are they held, and what must happen before each can be released?**

| Evidence | What to inspect | How it supports the answer |
|---|---|---|
| Catalog | Entity definitions, unpaid metric, units and relationships | Distinguishes unpaid from payout eligibility and supplies correct joins/grain. |
| Business records | Seller, payout, delivery and return state | Establishes the current held amounts and blockers. |
| Retrieved policy | Delivery/hold/return rules and citations | Explains the conditions for release. |

A fresh GPT-5.4 rehearsal retrieved the catalog, resolved the seller, queried current records and retrieved four policy chunks without tool errors. At revision 2, it found a held payout of ₹2,249.10 that still required delivery and the 24-hour hold, with no active return blocker. Verify current amounts from your own evidence rather than copying that snapshot. Tool sequence and call counts can vary.

## Static and dynamic input

Stable configuration includes the investigator role, tool contracts, read-only boundaries, citation requirements and freshness rules. Dynamic input includes the question, snapshot metadata, retained messages, catalog results, business query results and retrieved policy passages. Catalog content can be relatively stable while still arriving dynamically through a tool call. Policies are separately retrieved documents, not part of the catalog payload. The relationship map does not imply a separate graph database.

The application attaches the current revision and demo clock before the first model call for every question, including follow-ups. The initial call cannot contain a result from a tool that has not returned. Later calls retain tool calls and evidence. Prior generated prose is not equivalent to fresh verified business evidence.

## The UI context comparison

The request carries separate catalog and document-retrieval suppression options. Each investigation binds those flags to its own read tools, including a separate MCP child process. No ontology file or document changes are necessary. Both controls default off and are available only in the test workspace. Changing a control starts a fresh conversation with memory off.

Both tool calls succeed with empty context. Catalog data is null and policy passages are empty. Retrieval does not fall back to another method. The model should explain missing evidence rather than inventing a policy. Inspect evidence and actual answers; do not equate a completed run with a correct conclusion.

## Verified GPT-5.4 comparison observations

Fresh conversations, memory and response caching off, same model and revision 2 snapshot:

| Condition | Actual behavior |
|---|---|
| Normal policy | Retrieved policy passages and cited the 30-day return window. |
| Policy retrieval suppressed | Repeated retrieval and fetched evidence, received no passages, then declined to state the current policy without retrieved text. It did not claim the policy does not exist. |
| Normal catalog | Corrected one query error and completed a reconciled breakdown by category, including the meaning of unpaid. |
| Catalog suppressed | Ran several queries, some successful and some erroneous, then reached the eight-model-turn limit without a complete conclusion. It did not stop immediately or fail to construct every query. |

For the normal category question, the recorded snapshot placed Cedar & Co. in Travel: captured ₹7,497; refunded ₹0; fees ₹749.70; paid out ₹0; unpaid ₹6,747.30. Captured minus refunds, fees and paid-out equals unpaid. Unpaid includes held and failed amounts; release eligibility requires additional current records and policy evidence.

Both restored-context rehearsal runs completed: policy passages returned and the category breakdown reconciled to the same totals, with recovery from one SQL error. Restore both controls and repeat the same questions to confirm evidence returns in your run. **New conversation** clears experimental controls, so set the intended comparison switch afterward. This is an exploratory observation per condition, not a guaranteed result or a model benchmark. Business state remained unchanged.

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
