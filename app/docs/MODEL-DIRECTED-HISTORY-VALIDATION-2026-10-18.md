# Model-directed order history validation

The SDK agent no longer preloads order history based on keywords in a question.
The initial user message contains the question and snapshot metadata. The model
selects get_order_history from the existing tools when history is needed.
Historical conversations retain their original messages; use a fresh chat when
comparing the new behavior with the previous application-prefetched behavior.

## Automated checks

17 checks passed: three isolated agent-loop cases (status, history, retries),
metadata construction without preloaded business evidence, and the isolated HTTP
MCP suite. No marketplace resets or business commands were run.

## Live Test workspace checks

GPT-5.4; SDK; memory off; response cache off; no context suppression; revision 2.
Fresh chats except the deliberate status-to-history follow-up. Each run completed,
all recorded tool attempts completed, and all answer citations resolved to saved
evidence. The combined example used all four tools without naming them in the
question. These are observed runs, not a guarantee of future model choices.

| Case | Turn | Model-requested tools | Local Langfuse trace |
|---|---:|---|---|
| combined | 1 | get_order_history, search_documents, get_catalog, query_business_data | `ca49a0dd6a114073b5989495fd2145a5` |
| policy | 1 | search_documents | `64bf88c3ff46be7bf5332b4558edf1a3` |
| retry | 1 | get_order_history | `973f638ba579a13cc6056ca2d157c142` |
| status-followup | 1 | get_catalog, query_business_data | `173914abd9e413fd25c68f2eb05bf474` |
| status-followup | 2 | get_order_history | `56e74d5ac76624bf40e7bad67441ff9c` |
| unknown | 1 | get_order_history | `16ca23f920ff379f21dfba719ffbafef` |

Combined question:

> For order-1, show the chronological order and payout history, including any failed or retried attempts. Show each seller’s current payout amount and status, explain why any payout remains held or failed, and what the applicable policy requires before release.

The retry answer correctly reported one recorded failure and no recorded successes
or retries in the Test event timeline. The unknown-order case returned no records
without inventing a timeline. The simple status case used catalog and SQL; its
follow-up requested order history explicitly. The policy-only case used retrieval.

## Regular local workspace rollout

Activated only after Test validation. The existing container lacked the repository's
response_cache_demo and gateway_demo modules; those two missing modules were
copied from the current repository before repeating the smoke test. No key,
model mapping, container environment, database schema or business record was changed.
Both backend images were rebuilt for subsequent starts.

The regular workspace history-and-policy question completed on GPT-5.4. Its saved
SDK conversation contains model-requested get_order_history and search_documents
calls. The first user input has no application-provided order-history block. The
answer correctly distinguished the regular workspace's historical failed payout
from its later successful retry and completed current payouts. This dataset is
independent of Test's held/failed payout fixture.

Regular local trace: `7b69c75b1573942963a7019465514b46`.

Cloud Run was not redeployed as part of this local-workspace rollout.
