# Knowledge and Retrieval

## Prerequisites

Complete [Course Setup](../../../app/LOCAL-SETUP.md), including document indexing in both marketplace workspaces. Keep the local stack running. Open the [Test marketplace](http://127.0.0.1:5179/), sign in as **operator** or **support**, and open **Support workspace → OpenAI Agents SDK**. Keep memory, response caching, routing, guardrails and context suppression off; use the GPT-5.4 default.

Under **Workspace options → RAG**, marketplace documents should show all chunks indexed. Operator can use **Index documents** if needed. These marketplace documents are separate from the **Open RAG experiments** below, which have their own synthetic corpus and index. Preparing a demo does not replace marketplace policies or change business records. Embedding and model calls incur normal provider usage.

All steps below run in the browser. No terminal commands, file edits or chunker implementation are required.

## Your task

### Part 1: Inspect retrieval and compare policy versions

#### Quick review: policy and business evidence

1. Start a fresh conversation in the ordinary Support chat and ask: **“What conditions must be met before releasing a seller payout?”** Inspect `search_documents` in local Langfuse: actual query, passages, policy version, dates and source citations.
2. In another fresh conversation ask: **“For order-2, what is each seller’s current payout status, and is their payout eligible for release? Explain why.”** Identify claims supported by current business records versus retrieved policy. Do not assume any payout is held or that eligibility means payment was executed.

#### Policy versions and reindexing

1. Click **RAG → Open RAG experiments** and select **Policy versions and reindexing**. Use the **Demo question** and **Ask the demo question** button inside this panel, not the ordinary Support chat composer. This question searches only the synthetic demo corpus.
2. Click **Prepare V1 index** if the demo has not been prepared. If it was previously used, click **Restore V1**. Verify **Selected: V1** and **Indexed: V1**.
3. Inspect **Selected source document**. V1 requires a **24-hour** wait. The panel supplies fixed facts: payment captured, confirmed delivery **30 hours ago**, no open return. Keep its prefilled question unchanged: **“Is the seller payout eligible for release? State the waiting period and explain why, with policy citations.”**
4. Click **Ask the demo question**. Inspect the answer and expand **Retrieved passages and source lines**. Record indexed version, waiting period, answer and cited passage. Expected: eligible under the simulated V1 rule; this does not mean a payout was executed.
5. Select **V2 — 48-hour wait**, but **do not click Index selected settings yet**. Verify the source preview changed to V2, while **Indexed** still says V1 and a stale-index notice is visible. Ask the exact same question again. Check that the passages and answer still use indexed V1.
6. Click **Index selected settings** and wait until **Indexed: V2** appears. Ask the same question again. Check for the **48-hour** rule and a not-yet-eligible answer: the fixed delivery time is still 30 hours.
7. Click **Restore V1** after recording the three stages. This restores the demo source and index; it does not reset marketplace data.

Explain why changing a document selection alone did not change the retrieved evidence. The demo rebuilds its isolated corpus; it does not demonstrate automatic historical policy-version selection in the marketplace.

### Part 2: Compare chunking and the passage limit

**Purpose:** test whether the retrieved evidence includes all facts required for an answer. A smaller passage limit can omit a needed fact; overlap can bring adjacent facts into one chunk but also repeats text. Neither overlap nor a larger limit is always better.

1. In the same **Open RAG experiments** panel, select **Chunking and passage limit**. Use its expanded source document. It is a synthetic example; Amber Review is a fictional review flag, not a marketplace product or order field.
2. Expand **Selected source document**. One paragraph defines the standard wait as **24 hours**. The next says Amber Review adds **48 hours to that standard wait**, without repeating the base value. A complete answer needs both paragraphs: the total is **72 hours**.
3. Keep the fixed facts unchanged: payment captured, delivery 30 hours ago, no open return, Amber Review applies. Use the same prefilled question for every comparison: **“What are the standard wait, extra review hold and total required wait? Is payout eligible now? Cite the policy.”** The panel automatically supplies the fixed facts to each request.
4. Select **Paragraph**, then click **Prepare paragraph index** or **Index selected settings** as shown. Set **Maximum passages (top K)** to **1** and ask. Then change only top K to **4** and ask again. Top K changes retrieval, not the index.
5. Select **Two-paragraph overlap** and click **Index selected settings**. The chunker uses consecutive paragraph pairs with stride one. Ask at top K **1**, then **4**, keeping the question unchanged. Do not ask until the indexed strategy matches the selected strategy.
6. For each run inspect **Retrieved passages and source lines** and record the following:

| Chunking | Top K | Standard 24-hour rule retrieved? | Extra 48-hour hold retrieved? | Answer and citations | Retrieved characters |
|---|---:|---|---|---|---:|
| Paragraph | 1 | | | | |
| Paragraph | 4 | | | | |
| Overlap | 1 | | | | |
| Overlap | 4 | | | | |

Top K is the **maximum** number of chunks returned, not a similarity threshold. In this lab, blank lines define paragraph boundaries. One paragraph chunk cannot contain both rules; a two-paragraph window spanning the boundary can. Inspect the actual returned text rather than assuming which window ranks first.

If a required policy value is missing, an answer saying it cannot determine eligibility is appropriate. If both rules are returned, the expected calculation is **24 + 48 = 72 hours**, so the simulated payout is not eligible at 30 hours. Compare evidence coverage separately from whether the final answer is right. More characters are a context-volume observation, not a measured API cost or latency result.

Click **Restore paragraph baseline** when finished. This returns the demo to paragraph indexing; it does not change the main marketplace or remove conversations. Save your comparison locally; no submission or database reset is required. See the [worked answers](solutions/answers.md) after trying the comparisons.
