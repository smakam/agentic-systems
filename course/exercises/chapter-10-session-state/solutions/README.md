# Chapter 10 — reference checks and validation status

The executable reference is supplied in [session_strategies.py](session_strategies.py), with the real SDK comparison in [compare_strategies.py](compare_strategies.py). Production history selection stays unchanged. Offline checks and the saved completed live validation pass. Learner runs use the normal configured gateway; the earlier validation routing and failed attempts are retained in the historical validation record.

## Setup for the optional developer lab

These commands are for the optional developer challenges or automated rehearsal. Core UI practice uses the existing marketplace and Langfuse and does not require this database-copy setup.

Run from the code repository root with the local Docker stack running. [reset_lab.sh](reset_lab.sh) copies the fixed evaluation database into `ch10_session_lab`; its source is read-only and its restore destination is fixed in the script. Run it before each complete demo rehearsal. Stop other lab scripts before resetting. It restores the same business data, clock, revision and policy index rather than accumulating purchases from earlier runs.

```sh
bash course/exercises/chapter-10-session-state/solutions/reset_lab.sh
docker compose -f app/compose.yaml exec -T backend mkdir -p /tmp/ch10-code/marketplace /tmp/ch10-exercises
docker cp app/backend/marketplace/. marketplace-lab-backend-1:/tmp/ch10-code/marketplace
docker cp course/exercises/chapter-10-session-state/solutions/. marketplace-lab-backend-1:/tmp/ch10-exercises
```

Then run the three demos against the disposable destination only:

```sh
docker compose -f app/compose.yaml exec -T -w /tmp/ch10-code backend env PYTHONPATH=/tmp/ch10-code DATABASE_URL=postgresql+psycopg://market:market-local@postgres:5432/ch10_session_lab READ_DATABASE_URL=postgresql://agent_reader:reader-local@postgres:5432/ch10_session_lab python /tmp/ch10-exercises/validate_demos.py
docker cp marketplace-lab-backend-1:/tmp/ch10-demo-results.json /tmp/ch10-demo-results.json
```

The reference buys two units from the first in-stock listing in the fixed baseline, queries that order, asks the follow-up, dispatches the shipment through the shared marketplace command handler, and queries again. It records generated order IDs and current snapshots. The boundary fixture uses six neutral arithmetic questions, then inspects selected history and actual model input. This automation exercises the same command handler as the UI; it does not replace the instructor's UI rehearsal.

Run the strategy comparison independently:

```sh
docker compose -f app/compose.yaml exec -T -w /tmp/ch10-code backend env PYTHONPATH=/tmp/ch10-code DATABASE_URL=postgresql+psycopg://market:market-local@postgres:5432/ch10_session_lab READ_DATABASE_URL=postgresql://agent_reader:reader-local@postgres:5432/ch10_session_lab python /tmp/ch10-exercises/compare_strategies.py
docker cp marketplace-lab-backend-1:/tmp/ch10-strategy-results.json /tmp/ch10-strategy-results.json
```

Each strategy receives an identical supplied seven-question history fixture. Those stored answers are teaching fixture data, not fresh model generations. The next answer and the older-history summary use real provider calls. The runner captures actual selected input, recall, input character counts, run usage and separate summary usage. Character counts are not token counts. Cost depends on the configured gateway/model pricing; do not infer a dollar saving from shorter text alone. The three window cases need one answer call each, and the summary case additionally needs one summary call.

Record the resolved model behind `support-model`, source revision, clock, fixture hash and results. Outputs can vary across model runs even with fixed data. Both Python runners refuse any database other than `ch10_session_lab`. `compare_strategies.py` restores the original session class in its `finally` block and modifies only known synthetic conversation rows in this lab.

Offline checks require no API or database:

```sh
python3 -m unittest discover -s course/exercises/chapter-10-session-state/solutions -p 'test_*.py' -v
```

After exporting results, an optional cleanup is `docker compose -f app/compose.yaml exec -T postgres dropdb -U postgres ch10_session_lab`. Never substitute `market_eval` or `market` into this cleanup command. Recreate/reset the lab before another rehearsal.

## Exact comparison questions

The complete seven-block fixture and eighth recall question are written out in [Developer extension 1 in the exercise](../exercise.md#developer-extension-1--change-the-window). The same fixture is restored independently for the two-, six- and eight-block windows and summary-plus-two comparison. Seven prior blocks means the eight-block limit includes all seven; it is not an eight-to-ten-question history.

For summary-plus-two, the older five blocks become a summary while the final two retain exact messages and any paired tool results. Two is a lab choice. The goal is to measure whether early information survives and what input/summary overhead it adds, rather than assuming summary-only or a hybrid is always better. Full stored history remains unchanged.

## Expected checks

- Continuity: the follow-up input contains the earlier order reference. Reusing history may allow an answer without a new business-tool call.
- Freshness: after dispatch, the business revision increases. Fresh returned evidence uses the new snapshot and the answer reports the new shipment state. Old status in history is not current truth.
- Boundary: seven stored prior question blocks become six selected blocks. The early label is absent from actual next-call input while still present in storage. Complete tool-call/result pairs remain intact.
- Window comparison: selection changes; full stored history does not. An eight-block window includes an early block that the six-block window excludes in the supplied seven-block fixture.
- Summary comparison: the summary can preserve the early label while recent blocks remain complete. Verify this in the input and output, and report any failure honestly. Include summary-generation cost in the comparison.

## Saved validation

The saved demo validation contains eleven completed question runs in the disposable lab. Purchase revision 2 returned pending shipment status; the follow-up correctly returned two units using retained context. After dispatch, revision 3 returned fresh evidence and a dispatched answer. In the boundary case, seven stored blocks became six selected blocks: the early label was absent from actual model input while remaining in storage. The answer incorrectly denied that the label had been supplied; this is a limitation of answering from selected history, not a fact about the full conversation.

[Saved demo results](demo-results-2026-10-10.json) retain the original questions and traces. [Historical validation record](../../../../app/results/chapter-10-validation-2026-10-10/historical-validation.md) preserves original execution provenance. This does not claim a fresh rehearsal on the learner's current route.

The fixed evaluation database was unchanged. [Offline checks](offline-validation-2026-10-10.json) confirm the copied baseline and six-block selection. The saved automated run used marketplace command handlers; instructor UI clicks and a complete recording rehearsal are separate.

[Strategy results](strategy-results-2026-10-10.json) record four real SDK answer calls plus one real summary call from the same supplied seven-block fixture:

| Strategy | Label in actual input | Correct label recalled | Selected serialized characters | Answer-call input tokens |
|---|---|---|---:|---:|
| Two blocks | No | No; incorrectly chose “ten” | 214 | 2,014 |
| Six blocks | No | No; incorrectly denied the original label | 642 | 2,110 |
| Eight-block limit, all seven available | Yes | Yes | 790 | 2,137 |
| Summary plus two recent blocks | Yes | Yes | 1,209 | 2,254 |

All contract checks passed, including unchanged stored fixture prefixes. The short fixture is too small for this summary implementation to save input size: the summary wrapper and generated text exceed the original older turns. Summary generation additionally used 230 input plus 155 output tokens (385 total), with $0.0029 reported usage cost for that call. Answer-call dollar figures in app metrics are uncached list-rate estimates; provider prompt caching was observed, so they are not invoices. Do not claim an overall savings or a broad quality improvement. The exercise demonstrates different inclusion/recall behavior and the need to measure compaction overhead.

Initial setup attempts included a gateway startup error and an invalidated run when a lab reset overlapped it. They are excluded from the final valid comparison, not scored as successful runs. The complete final comparison finished before the subsequent demo reset. Instructor UI clicks and the owner's complete dry run remain separate checks.
