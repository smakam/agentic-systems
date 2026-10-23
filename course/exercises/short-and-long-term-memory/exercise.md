# Learner exercise: observe memory across conversations

You will run specified questions, inspect storage and Langfuse evidence, and document what occurred. The goal is to understand how conversation history, memory extraction and retrieval differ. You do not need to tune a provider or prove which one is generally better.

## Workspace and settings

Use **Test workspace** at http://127.0.0.1:5179/, database **market_test**. Sign in as the existing Operator demo user, open **Support**, choose **OpenAI Agents SDK**. Langfuse is http://localhost:3000/, project **marketplace-support**. Do not use the normal marketplace on 5178 or the Agent Loop lab on 5181 for this exercise.

Keep **Model routing → Normal support model**, **Agent design → Off · normal support**, **Gateway guardrail → Off**, **Source-authority prompt → On**, **Private-instruction prompt → Off**, **Test policy document → Clean policy**, and normal catalog/document context enabled. Use the same signed-in user for all recall comparisons.

Use **Refresh memory status** for the latest result and **Memory extraction trace** to inspect the background operation. Record the visible label: **Memory save queued**, **Saving memories in the background**, **Memory save complete**, **Memory save failed**, or **No new memories to save**. Queued and provider-pending share a UI label; the extraction trace supplies the more precise phase.

### Mem0 API-key setup (before the Mem0 cases)

Internal memory needs no Mem0 account or key. To run the hosted Mem0 cases in your own installation:

1. Sign in to [Mem0 Platform and create a dashboard API key](https://docs.mem0.ai/platform/quickstart). Check your account quota and billing before running the lab.
2. In the repository's `app` directory, open the existing private, gitignored `.env` file in your editor. Add `MEM0_API_KEY=your-own-key`, replacing the placeholder with your dashboard key. Keep the key out of chat, screenshots, frontend code and committed files.
3. When no investigation is running, apply the configuration from `app` with `./scripts/start.sh`. No separate host Mem0 SDK installation is required; the backend calls the hosted service.
4. Refresh the Test workspace, open Support with **OpenAI Agents SDK**, and confirm **Mem0** is available in the memory-provider selector. An available selector confirms configuration, not successful authentication or extraction; verify those during the Mem0 cases below.

For a shared course workspace, the course operator configures the backend key. If Mem0 is unavailable, complete the Internal cases and record the setup limitation. Do not interpret a provider error as proof that no memory exists. See [local setup: Mem0 configuration](../../../app/LOCAL-SETUP.md#optional-mem0-setup-for-chapter-18) for the complete setup and verification sequence.

**Preference retrieval and precedence:** both provider paths instruct the agent to look for relevant saved preferences before answering a business question. The model controls whether and how it calls search, so inspect the actual trace rather than assuming a call. A retrieved relevant format preference takes precedence over the default answer layout; an explicit instruction in the current question takes precedence over the saved preference. Current business evidence still governs factual claims.

## Part A: conversation history

Select **Internal memory**. Turn **Use long-term memory** and **Allow memory changes for this question** off.

1. Start **New conversation**. Ask **“List the products and quantities in order-1.”**
2. In the same conversation ask **“Which sellers supplied those items?”**
3. Start another new conversation and ask **“Which sellers supplied those items?”** without restating the order.
4. Compare retained input and current tool calls in the two traces. Record how the answer handles the missing reference in the fresh chat.

## Part B: explicit saving and automatic extraction

### B1: Internal memory

1. Select **Internal memory**, turn **Use long-term memory** on, start a fresh conversation, and enable **Allow memory changes for this question**.
2. Ask **“Remember my learner preference: explain refund questions as three numbered steps with the policy source at the end.”**
3. Open **Saved memories · Internal**. Record the saved content, kind, version and source. The write permission resets after the question.
4. Start **New conversation**, retain memory reads on and writes off. Ask **“Is order-1 eligible for a refund under the current returns policy?”** Do not mention memory, preference or formatting. Record the actual search query/preference match, per-item eligibility and current policy/business evidence. Observe whether the answer uses three numbered steps with the policy source at the end; do not assume that format.
5. Optional diagnosis: ask **“What is my learner preference for refund explanations?”** or **“How should you lay out a reimbursement explanation for me?”** in another fresh chat. These are diagnostic questions, not the primary business test.

**Automatic-save eligibility:** before calling Mem0, the application checks user messages for durable intent. Natural preferences such as “I like payout explanations in a compact table”, accepted reusable checklists and explicit historical resume requests can qualify. Chats containing only business questions, recall requests or temporary formatting instructions produce a completed no-op without a provider add call. For an eligible chat, the full conversation goes to the extraction API with per-request guidelines; Mem0 still chooses what to retain.

**Clean observation:** finish pending jobs, remove only your lab memories, verify no relevant lab entries and no pending jobs, then start a fresh chat. Run a business-only conversation first and confirm no new memory/provider add; next state a natural durable preference, end that chat and inspect extraction. In a fresh business question inspect actual retrieval, then test Edit and Forget in new chats.

**Extraction policy:** the application submits the completed conversation with per-request guidelines to retain stable preferences, accepted checklists and explicitly requested historical resume checkpoints. Routine business-answer snapshots and assistant acknowledgements/promises are excluded by those guidelines. Mem0 still selects the entries; inspect the saved results. Submission uses the extraction API; retrieval and saved-memory operations use hosted MCP.

### B2: Mem0

1. Select **Mem0** and turn **Retrieve saved memories** on. Changing provider starts a fresh conversation.
2. State **“My learner preference is to explain refund questions as three numbered steps with the policy source at the end.”** Do not request a save.
3. Click **New conversation** to queue extraction. Continue without waiting, but inspect the previous conversation's background status. Record the trigger and whether processing is still pending.
4. Once extraction completes, open **Saved memories · Mem0**. Record every related entry and provider category, even if the result differs from the intended preference or is empty.
   Also open the [Mem0 dashboard — Memories](https://app.mem0.ai/dashboard/memories) in the account/project used by the backend API key. Find the lab memory for the same user scope and check the actual stored text against the stated preference and the app’s saved-memory listing. A chat acknowledgement or queued extraction is not proof that the memory was stored. If no matching entry appears, inspect extraction status and confirm the account/project and user scope before testing recall.
5. In a fresh chat ask **“Is order-1 eligible for a refund under the current returns policy?”** without requesting a format or memory recall. Inspect **Mem0 memory search**, the actual preference match and scores, current per-item evidence/policy and the answer. Record whether the saved three-step format appears, including any miss or different format.

Do not assume Mem0 will win. The two paths change both formation and retrieval, and the internal agent may choose search words that happen to match. Record what the actual traces show.

## Part C: edit, current instruction and forget

Repeat C1–C4 separately for each provider.

1. Identify the named learner preference in **Saved memories**, click **Edit**, and change its content to **“My learner preference is one short paragraph for refund explanations.”** Confirm the stored result.
2. Start a new conversation with retrieval on. Ask **“Is order-1 eligible for a refund under the current returns policy?”** Inspect the returned preference record, current evidence and actual answer format after the edit.
3. Ask **“For this answer, use a numbered list instead of my usual format. What is the current returns policy?”** Record the current instruction, any retrieved preference and the answer's format. Verify business policy claims against the policy evidence.
4. After any pending extraction completes, **Forget** the named learner entry and related extracted records about that same preference. Confirm the listing. Start a new conversation and repeat the same refund-eligibility business question. Record whether retrieval still finds the deleted preference; the business answer can remain correct without it.

Deleting a record does not erase old chat history. Restating a preference in a later Mem0 conversation can extract it again; inspect remaining entries and extraction jobs before deciding that forgetting failed.

## Part D: historical checkpoint and procedural guidance

**Memory-type clarification:** A saved historical investigation checkpoint is **episodic memory**: it records where a past investigation stopped so a later conversation can resume it. A reusable investigation checklist is **procedural memory**: it describes how to carry out the task.

Select **Internal memory**, memory reads on. Enable writes only for each save.

1. Save **“Remember a learner checkpoint: we previously investigated order-2. Next time, recheck its current payout records rather than assuming the earlier status.”** Inspect the episodic kind and source.
2. Save **“Remember this learner refund checklist: find the applicable policy, check item delivery dates, and distinguish refund eligibility from any actual refund payment.”** Inspect the procedural kind and source.
3. Start a new conversation, writes off. Ask **“Resume my learner checkpoint for order-2 and explain its current payout status.”** Inspect remembered content and current business tools separately.
4. In another fresh conversation ask **“Investigate refund eligibility for order-1 using my learner checklist.”** Inspect which memory was retrieved, which checks occurred, and any unresolved evidence.

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

Answer these observation questions. The sample answers below are **illustrative**, not fixed expected results. Replace them with your own observed settings, matches and trace links; a documented miss is valid.

1. **Which result came from same-conversation history, and which had a confirmed long-term memory retrieval?**

   Inspect/record: compare Part A's same-chat and fresh-chat traces with Part B's actual memory-search results. Identify the prior messages or returned record that supplied context.

   Illustrative answer: “My Part A follow-up resolved ‘those items’ from the earlier order question, with memory off. In B2's fresh refund question, the search returned my saved three-step preference. I recorded both trace links.” If no record was returned, say so.

2. **Who chose when to save and what to retain in each provider path?**

   Inspect/record: note Internal's explicit save request and write permission; for Mem0, record the conversation-end trigger, eligibility decision and saved entries.

   Illustrative answer: “I chose the Internal preference content and enabled writes. For Mem0 I stated a lasting refund preference; New conversation triggered processing, the app admitted it under the durable-intent policy, and Mem0 selected the stored fact.” A business-only no-op has no provider add.

3. **For the optional paraphrase, what did the search actually return? What can this small observation establish?**

   Inspect/record: if you ran the optional diagnostic, record its question, actual search query, matches and available scores for each provider. Otherwise write **not applicable — optional paraphrase not run**.

   Illustrative answer: “For my reimbursement paraphrase, Internal returned no preference and Mem0 returned the refund-format preference. This describes one query, not proof that one provider is always better.” Record the opposite result if that is what happened.

4. **What changed after Edit and Forget, and how did you avoid testing against old chat history?**

   Inspect/record: compare the stored text before/after Edit, the listing after Forget and retrieval in fresh conversations. Check pending jobs and related entries.

   Illustrative answer: “Edit changed my preference from three steps to one paragraph. A new chat retrieved the edited text. After pending jobs finished and I forgot related lab entries, another fresh chat did not retrieve that preference. The refund answer still used policy evidence.” Answer format alone does not prove deletion.

5. **Did current instructions and current records retain authority over remembered context?**

   Inspect/record: compare the explicit numbered-list instruction with the stored paragraph preference; identify policy/item evidence supporting eligibility and fresh records used for the checkpoint.

   Illustrative answer: “The current numbered-list request overrode my usual paragraph format. The answer assessed refund eligibility per item using the applicable policy and delivery records; the preference changed presentation, not the business facts.” Document conflicts or missing evidence instead of assuming compliance.

6. **Did the extraction trace show confirmed completion, and what did the later retrieval trace show?**

   Inspect/record: capture processing status, no-op versus provider extraction, saved IDs/content and the later business question's actual search result. Keep both trace links.

   Illustrative answer: “The natural-preference chat completed provider extraction and stored one refund preference. The later fresh refund question returned that record. My business-only control completed as a no-op without a provider add.” Queued is not saved, and completed can mean no-op or zero extracted entries.

**Optional scope check:** if the instructor supplies a second course account, sign in as it and confirm the first account's named memories are absent in the listing and retrieval. Return to the original user. Do not create accounts or modify another user's records for this exercise.

## Cleanup and submission

While Mem0 is selected, click New conversation to queue the final completed lab chat and leave the new empty chat unanswered. Wait for the observed extraction jobs to finish. Remove only your named learner records and related extracted lab entries, then verify the Mem0 listing without another question. Select Internal memory, remove only its named learner preference, checkpoint and checklist, turn memory reads/writes off and start a fresh conversation. This avoids submitting a final conversation after deleting its extracted entries. Keep business data unchanged.

Submit the table and six short explanations. Compare your reasoning with [solutions/answers.md](solutions/answers.md). Provider wording and model answers can vary; your recorded evidence matters more than reproducing an exact sentence.
