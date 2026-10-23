# Chapter 17 — earlier demo verification

This records the earlier accept/incomplete-correction rehearsal. The revised instructor and learner examples are documented in [success-rehearsal.md](success-rehearsal.md).

- Focused controller tests: draft acceptance without correction, one correction, preservation of tool call/result pairs, exclusion of internal feedback from conversation history, reviewer failure without draft commit, shared deadline and approved model/workspace boundaries.
- Frontend production build passed.
- Live Test workspace UI: Nano generator and GPT-5.4 reviewer completed an accepted order-2 lookup and a corrected order-1 eligibility investigation.
- Langfuse v4 observations readback confirmed one root with Generate draft, Review draft, Workflow decision and (in the revision case) Correct draft beneath it.
- Stored conversation history ends with the corrected final answer, has one original user question, and does not contain the internal correction-feedback user message.
- Live answer quality was not claimed as universally correct: the recorded correction left missing delivery evidence unresolved.

The machine-readable rehearsal record is [verification/live-workflow-rehearsal.json](verification/live-workflow-rehearsal.json). It describes specific observations, not expected outcomes for every learner run. Additional model combinations and the follow-up scenario are checked before publication; see the record for their actual outcomes.
