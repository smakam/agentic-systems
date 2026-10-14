# Chapter 18 learner exercise: observe memory across conversations

You will run specified questions, inspect storage and Langfuse evidence, and document what occurred. The goal is to understand how conversation history, memory extraction and retrieval differ. You do not need to tune a provider or prove which one is generally better.

## Workspace and settings

Use **Test workspace** at http://127.0.0.1:5179/, database **market_test**. Sign in as the existing Operator demo user, open **Support**, choose **OpenAI Agents SDK**. Langfuse is http://localhost:3000/, project **marketplace-support**. Do not use the normal marketplace on 5178 or the Agent Loop lab on 5181 for this exercise.

Keep **Model routing → Normal support model**, **Agent design → Off · normal support**, **Gateway guardrail → Off**, **Source-authority prompt → On**, **Private-instruction prompt → Off**, **Test policy document → Clean policy**, and normal catalog/document context enabled. Use the same signed-in user for all recall comparisons.

Use **Refresh memory status** for the latest result and **Memory extraction trace** to inspect the background operation. Record the visible label: **Memory save queued**, **Saving memories in the background**, **Memory save complete**, **Memory save failed**, or **No new memories to save**. Queued and provider-pending share a UI label; the extraction trace supplies the more precise phase.

Mem0 must be configured by the course operator. If it is marked unavailable, complete the Internal cases and document the external setup limitation. Do not use a provider error as evidence that no memory exists.

## Part A: conversation history

Select **Internal memory**. Turn **Use long-term memory** and **Allow memory changes for this question** off.

1. Start **New conversation**. Ask **“List the products and quantities in order-1.”**
2. In the same conversation ask **“Which sellers supplied those items?”**
3. Start another new conversation and ask **“Which sellers supplied those items?”** without restating the order.
4. Compare retained input and current tool calls in the two traces. Record how the answer handles the missing reference in the fresh chat.

## Part B: explicit saving and automatic extraction

### B1: Internal memory

1. Select **Internal memory**, turn **Use long-term memory** on, start a fresh conversation, and enable **Allow memory changes for this question**.
2. Ask **“Remember my Chapter 18 learner preference: explain refund questions as three numbered steps with the policy source at the end.”**
3. Open **Saved memories · Internal**. Record the saved content, kind, version and source. The write permission resets after the question.
4. Start **New conversation**, retain memory reads on and writes off. Ask **“What is my Chapter 18 learner preference for refund explanations?”** Record the search query, actual returned record and answer.
5. In another fresh chat ask **“How should you lay out a reimbursement explanation for me?”** Record the same fields, including any miss.

### B2: Mem0

1. Select **Mem0** and turn **Retrieve saved memories** on. Changing provider starts a fresh conversation.
2. State **“My Chapter 18 learner preference is to explain refund questions as three numbered steps with the policy source at the end.”** Do not request a save.
3. Click **New conversation** to queue extraction. Continue without waiting, but inspect the previous conversation's background status. Record the trigger and whether processing is still pending.
4. Once extraction completes, open **Saved memories · Mem0**. Record every related entry and provider category, even if the result differs from the intended preference or is empty.
5. In a fresh chat ask **“How should you lay out a reimbursement explanation for me?”** Inspect **Mem0 memory search** in Langfuse and record query, matches, scores when supplied and answer.

Do not assume Mem0 will win. The two paths change both formation and retrieval, and the internal agent may choose search words that happen to match. Record what the actual traces show.

## Part C: edit, current instruction and forget

Repeat C1–C4 separately for each provider.

1. Identify the named learner preference in **Saved memories**, click **Edit**, and change its content to **“My Chapter 18 learner preference is one short paragraph for refund explanations.”** Confirm the stored result.
2. Start a new conversation with retrieval on. Ask **“What is my Chapter 18 learner preference for refund explanations?”** Inspect the returned record and answer.
3. Ask **“For this answer, use a numbered list instead of my usual format. What is the current returns policy?”** Record the current instruction, any retrieved preference and the answer's format. Verify business policy claims against the policy evidence.
4. After any pending extraction completes, **Forget** the named learner entry and related extracted records about that same preference. Confirm the listing. Start a new conversation and repeat the recall question. Record whether retrieval still finds a matching entry.

Deleting a record does not erase old chat history. Restating a preference in a later Mem0 conversation can extract it again; inspect remaining entries and extraction jobs before deciding that forgetting failed.

## Part D: historical checkpoint and procedural guidance

Select **Internal memory**, memory reads on. Enable writes only for each save.

1. Save **“Remember a Chapter 18 learner checkpoint: we previously investigated order-2. Next time, recheck its current payout records rather than assuming the earlier status.”** Inspect the episodic kind and source.
2. Save **“Remember this Chapter 18 learner refund checklist: find the applicable policy, check item delivery dates, and distinguish refund eligibility from any actual refund payment.”** Inspect the procedural kind and source.
3. Start a new conversation, writes off. Ask **“Resume my Chapter 18 learner checkpoint for order-2 and explain its current payout status.”** Inspect remembered content and current business tools separately.
4. In another fresh conversation ask **“Investigate refund eligibility for order-1 using my Chapter 18 learner checklist.”** Inspect which memory was retrieved, which checks occurred, and any unresolved evidence.

These cases show memory types and authority. A historical checkpoint cannot establish current status, and a saved checklist cannot replace the policy or change tool permissions.

## What to record

Use one row for every completed question, plus a row for each background extraction and lifecycle operation. Keep trace links rather than copying long opaque identifiers into your explanation.

| Case | Provider and read/write settings | Fresh or same conversation | Question or operation | Stored/extracted content and type/category | Search query and actual matches | Pending/complete/failed state | Answer and current evidence | Trace link |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| A follow-up | | | | | | | | |
| A fresh chat | | | | | | | | |
| B1 save / recall / paraphrase | | | | | | | | |
| B2 extraction / recall | | | | | | | | |
| C Internal edit / override / forget | | | | | | | | |
| C Mem0 edit / override / forget | | | | | | | | |
| D checkpoint / checklist use | | | | | | | | |

Add more rows as needed. When a field does not apply, write “not applicable” and explain why.

Answer these observation questions:

1. Which result came from same-conversation history, and which had a confirmed long-term memory retrieval?
2. Who chose when to save and what to retain in each provider path?
3. For the paraphrase, what did the search actually return? What can this small observation establish?
4. What changed after Edit and Forget, and how did you avoid testing against old chat history?
5. Did current instructions and current records retain authority over remembered context?
6. Did the extraction trace show confirmed completion, and what did the later retrieval trace show?

**Optional scope check:** if the instructor supplies a second course account, sign in as it and confirm the first account's named memories are absent in the listing and retrieval. Return to the original user. Do not create accounts or modify another user's records for this exercise.

## Cleanup and submission

While Mem0 is selected, click New conversation to queue the final completed lab chat and leave the new empty chat unanswered. Wait for the observed extraction jobs to finish. Remove only your named learner records and related extracted lab entries, then verify the Mem0 listing without another question. Select Internal memory, remove only its named learner preference, checkpoint and checklist, turn memory reads/writes off and start a fresh conversation. This avoids submitting a final conversation after deleting its extracted entries. Keep business data unchanged.

Submit the table and six short explanations. Compare your reasoning with [solutions/answers.md](solutions/answers.md). Provider wording and model answers can vary; your recorded evidence matters more than reproducing an exact sentence.
