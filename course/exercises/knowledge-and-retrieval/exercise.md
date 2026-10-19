# Knowledge and Retrieval

## Prerequisites

Complete [Course Setup](../../../app/LOCAL-SETUP.md), and wait for automatic document preparation to show Ready in both marketplace workspaces. Keep the local stack running. Open the [Test marketplace](http://127.0.0.1:5179/), sign in as **operator** or **support**, and open **Support workspace → OpenAI Agents SDK**. Keep memory, response caching, routing, guardrails and context suppression off; use the GPT-5.4 default.

Under **Workspace options → RAG**, marketplace documents should show **Ready**. Indexing is automatic; if preparation fails, resolve embedding access and use **Retry preparation**. The RAG experiment selector changes what the main Support question box searches: Off uses marketplace evidence; policy-version mode applies isolated lab policy documents to current Test order records; chunking mode uses isolated lab documents and fixed facts. Preparing an order can add labelled Test records, but does not modify existing orders or marketplace policies. Embedding and model calls incur normal provider usage.

All steps below run in the browser. No terminal commands, file edits or chunker implementation are required.

## Your task

### Part 1: Inspect retrieval and compare policy versions

#### Quick review: policy and business evidence

1. Start a fresh conversation in the ordinary Support chat and ask: **“What conditions must be met before releasing a seller payout?”** Inspect `search_documents` in local Langfuse: actual query, passages, policy version, dates and source citations.
2. In another fresh conversation ask: **“For order-2, what is each seller’s current payout status, and is their payout eligible for release? Explain why.”** Identify claims supported by current business records versus retrieved policy. Do not assume any payout is held or that eligibility means payment was executed.

#### Policy versions and order eligibility

**Purpose:** hold one order's recorded facts constant and show how a retrieved policy changes the eligibility explanation. V1 requires 24 hours; V2 requires 48 hours.

1. Under **Workspace options → RAG → RAG experiment**, select **Policy versions and order eligibility**. Ask questions in the main Support question box.
2. Click **Prepare demo order**. The application first reuses a suitable recorded Test order: captured payment, delivered between 24 and 48 hours before the current demo clock, no active return and a positive held payout. Otherwise it creates a labelled single-item Test order delivered 30 hours before that clock. The panel shows its **order ID, delivery age and held payout status**. Keep that ID for both runs.
3. Choose **V1 — 24-hour wait** and wait for **Ready**. Expand **Selected source document**, below **Use order question**, to read the policy. Reference copies: [V1 source](fixtures/payout-demo-v1.md) and [V2 source](fixtures/payout-demo-v2.md). Changing the version prepares the selected policy automatically and reuses cached embeddings when available.
4. Click **Use order question** to fill a question containing the displayed order ID. Start a fresh conversation, keep this experiment selected, and ask that question. Inspect **Current order records** and **Retrieved passages and source lines** below the answer. Expected: eligible under V1, with record and policy citations. A held payout is still held; eligibility does not mean payment was executed.
5. Choose **V2 — 48-hour wait** and wait for **Ready**. Start a fresh conversation and ask the identical order question. Expected: not yet eligible. Confirm the same order and delivery timestamp were used, with the 48-hour retrieved policy.
6. **Restore V1**, then turn the experiment **Off**. This restores normal marketplace retrieval. It keeps the prepared order; it does not undo or execute any payout.

Do not move the demo clock, change delivery/payment/return records or execute the payout between the two runs. If the clock or order changes and it is no longer suitable, click **Prepare demo order** again and repeat both versions with the returned ID. Preparation leaves existing orders and the clock unchanged. A newly created fixture adds Test records and can change workspace-wide counts or totals; it uses a dedicated lab seller and product. Reset to defaults does not delete these records.

This compares selected lab policies against actual Test records. It does not demonstrate automatic historical policy selection or replace the operational payout execution rules. There is no manual indexing or stale-index step.

### Part 2: Compare chunking and the passage limit

**Purpose:** test whether the retrieved evidence includes all facts required for an answer. A smaller passage limit can omit a needed fact; overlap can bring adjacent facts into one chunk but also repeats text. Neither overlap nor a larger limit is always better.

1. Under **Workspace options → RAG → RAG experiment**, select **Chunking and passage limit**. Use its expanded source document. It is a synthetic example; Amber Review is a fictional review flag, not a marketplace product or order field.
2. Expand **Selected source document**. One paragraph defines the standard wait as **24 hours**. The next says Amber Review adds **48 hours to that standard wait**, without repeating the base value. A complete answer needs both paragraphs: the total is **72 hours**.
3. Keep the fixed facts unchanged: payment captured, delivery 30 hours ago, no open return, Amber Review applies. Click **Use example question** and use the same question in the main composer for every comparison: **“What are the standard wait, extra review hold and total required wait? Is payout eligible now? Cite the policy.”** The panel automatically supplies the fixed facts to each request.
4. Select **Paragraph** and wait for **Ready**. Set **Maximum passages (top K)** to **1**, start a fresh conversation and ask. Then change only top K to **4**, start a fresh conversation and repeat the same question. Top K changes retrieval, not the document index.
5. Select **Two-paragraph overlap** and wait for automatic preparation to show **Ready**. The chunker uses consecutive paragraph pairs with stride one. Ask at top K **1**, then **4**, using a fresh conversation and the identical question for each run. Do not ask until the indexed strategy matches the selected strategy.
6. For each run inspect **Retrieved passages and source lines** and record the following:

| Chunking | Top K | Standard 24-hour rule retrieved? | Extra 48-hour hold retrieved? | Answer and citations | Retrieved characters |
|---|---:|---|---|---|---:|
| Paragraph | 1 | | | | |
| Paragraph | 4 | | | | |
| Overlap | 1 | | | | |
| Overlap | 4 | | | | |

Top K is the **maximum** number of chunks returned, not a similarity threshold. In this lab, blank lines define paragraph boundaries. One paragraph chunk cannot contain both rules; a two-paragraph window spanning the boundary can. Inspect the actual returned text rather than assuming which window ranks first.

If a required policy value is missing, an answer saying it cannot determine eligibility is appropriate. If both rules are returned, the expected calculation is **24 + 48 = 72 hours**, so the simulated payout is not eligible at 30 hours. Compare evidence coverage separately from whether the final answer is right. More characters are a context-volume observation, not a measured API cost or latency result.

Click **Restore paragraph baseline**, then turn the experiment **Off** when finished. Alternatively, **Reset to defaults** at the top of Workspace options restores all settings and existing demo baselines, without opening a new conversation or deleting history, saved memories or business records. Start a fresh conversation yourself for a clean comparison. This returns the demo to paragraph indexing; it does not change the main marketplace or remove conversations. Save your comparison locally; no submission or database reset is required. See the [worked answers](solutions/answers.md) after trying the comparisons.
