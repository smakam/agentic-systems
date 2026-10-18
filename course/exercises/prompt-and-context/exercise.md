# Prompt and Context

## Prerequisites

Complete **Course Setup** using the [local setup guide](../../../app/LOCAL-SETUP.md), and keep the application running.

Open the **[Test marketplace](http://127.0.0.1:5179/)**. Sign in as support or operator and open **Support workspace**. Under **Agent runtime**, select **OpenAI Agents SDK**. Under **Gateway → Gateway model mapping**, verify **GPT-5.4 (default)**. Keep long-term memory and response caching off. Open **[local Langfuse](http://localhost:3000/)** through the application when inspecting a run.

Use a fresh conversation for each condition and keep the model, business revision and demo clock unchanged. Selecting a previous conversation reopens its saved questions and answers. To repeat a question, copy its text, choose **New conversation**, and paste it. New conversation clears experimental switches, so set the intended suppression option afterward. Changing a suppression option also starts a fresh conversation with memory off.

## Your task

### Part 1: Inspect a complete context investigation

1. Start a new conversation. Under **Context comparison**, leave both suppression options off.
2. Ask:

   > For Cedar & Co., which payouts are currently held, why are they held, and what must happen before each can be released?

3. Read the answer and its evidence, then open the corresponding Langfuse trace. Select each tool call and use **Preview** to inspect its actual inputs and outputs; **Attributes** describes the tool contract.
4. Inspect the three sources:
   - **get_catalog:** collapse the JSON to see its sections, then expand one entity, one relationship and the unpaid metric. Identify currency/money units, time guidance, cautions, versions and validation.
   - **query_business_data:** inspect the seller lookup and the current payout, delivery and return records. Check the SQL, row grain and monetary units.
   - **search_documents:** inspect the returned policy passages and the delivery, hold and return rules supporting the answer.
5. Open a later model call. Identify stable instructions/tool schemas, the question and revision/clock, and the tool calls/results added during the investigation. Connect the final claims and citations to that evidence.

Tool order and call counts can vary. Record which evidence actually supported your answer.

### Part 2: Compare normal, suppressed and restored context

Observe how missing policy or catalog context affects the answer, tool use and completion. Use the same question in a fresh conversation for every condition, changing only the indicated suppression option.

#### A. Policy retrieval

Ask:

> What is the current returns policy?

1. **Normal:** leave both suppression options off. Inspect the retrieved passages, answer and citations.
2. **Suppressed:** start a new conversation, enable only **Suppress policy retrieval**, and repeat the question. Inspect the tool outputs and whether the answer acknowledges missing evidence. If it searches twice, compare each call's **Preview → query** and **top_k** values.
3. **Restored:** clear both options, start a new conversation and repeat. Confirm that policy passages return.

#### B. Catalog context

Ask:

> For Cedar & Co., break down captured, refunded, fees, paid out, and unpaid amounts by product category in rupees.

1. **Normal:** leave both suppression options off. Inspect the catalog, SQL, category breakdown and cited business records.
2. **Suppressed:** start a new conversation, enable only **Suppress catalog context**, and repeat the question. Inspect the empty catalog result, queries, errors/recovery and whether the run completes or reaches its model-turn limit.
3. **Restored:** clear both options, start a new conversation and repeat. Confirm that catalog data and a grounded breakdown return.

Suppression returns successful tool responses with no catalog data or no policy passages. Other tools and some static guidance remain available. Compare what actually happens; a wrong answer or turn-limit stop is not required for the exercise.

Finish with both suppression options off. Keep your questions, observations and traces, then compare them with the [worked answers](solutions/answers.md). No business-data reset or submission is needed.
