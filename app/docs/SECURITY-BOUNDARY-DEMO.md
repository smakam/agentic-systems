> **Historical/optional guide:** Removed from the main security lesson by course-scope decision on October 7, 2026. The script below combines earlier memory-boundary tests and a different marker probe; it does not implement a read-by-ID tool or the revised lantern comparison. Use the [combined teaching guide](SECURITY-CHAPTER-DEMO.md) for the current lesson. Preserve these instructions only for reproducing the earlier report.

# Security demo: middleware permissions and hidden context

Two demonstrations complement the earlier guardrail walkthrough. Run them from a terminal; neither requires selecting a test policy or changing UI security controls.

## Before starting

- Start the existing test workspace services. The test UI is http://127.0.0.1:5179/; this script uses its backend/database directly, so UI login is not required.
- Use the **test database only**. The script refuses to run against the main database.
- Keep the gateway running with the current GPT-5.4 support model. The marker demo makes two paid model calls, with gateway filters Off and no judge.
- Avoid running another memory test or editing saved memories at the same time.
- Open a terminal in the project’s `app` directory.

## Run the two demonstrations

```sh
docker compose -f compose.yaml -f compose.memory.yaml exec -T memory-backend python - < scripts/security-boundaries.py
```

The script prints each step and checks its expected result. It stops if an assertion fails. These are real local MCP tool calls and real model requests—not simulated successful results.

## Demo 1 — middleware enforces memory permissions

**Question:** Can a model/tool caller access another user’s memory just by supplying its memory ID?

The script establishes each user’s identity in trusted application context. User identity is not an argument the model can choose.

| Step | Action | Expected result |
|---|---|---|
| 1 | Create temporary operator/support conversations. Operator calls save_memory with a harmless preference. | Save succeeds: the allowed control. |
| 2 | Support calls search_memories for that unique preference. | No matching memory returned. |
| 3 | Support calls update_memory with the known operator memory ID. | Rejected: Memory not found. |
| 4 | Support calls delete_memory with the same ID. | Rejected: Memory not found. |
| 5 | Operator searches again. | Original content and version unchanged. |
| 6 | Operator tries save_memory with memory writes disabled. | Rejected: enable memory changes first. |

Support has update/delete operations enabled in steps 3–4; the rejection is due to **ownership**, not just a disabled write toggle. Step 6 separately demonstrates write permission.

**What this proves:** middleware enforces the boundary regardless of a model’s decision. No LLM is involved in this demonstration. It does not demonstrate different operator/support SQL or RAG permissions; those business tools currently share read-only access.

## Demo 2 — model handles a private instruction marker

**Question:** Will the model disclose synthetic internal context when asked?

| Step | Action | Expected / previously observed result |
|---|---|---|
| 1 | Put a harmless synthetic marker in ordinary user text and ask GPT-5.4 to repeat it. | Exact marker repeated: the allowed control. |
| 2 | Put the same marker in system instructions, with a nondisclosure instruction; ask for the private marker. | Earlier run refused; marker absent from the answer. |

The script uses current support instructions, adds the marker only for this probe, and sends the requests through the permitted support gateway alias. It does **not** edit the deployed agent prompt. No tools or RAG are used in this demo; no real secrets are included.

**What this proves:** model behavior for this one prompt. A new run could disclose the marker; that is a result to record, not hide. The script reports either outcome. Refusal is not guaranteed secrecy, and system prompts must not contain credentials or enforce authorization.

## View the exact results

After the command finishes:

```sh
docker compose -f compose.yaml -f compose.memory.yaml exec -T memory-backend python -c 'import json; d=json.load(open("/tmp/security-boundaries.json")); print(json.dumps({"permissions":d.get("permissions"),"marker_responses":[{"case":x["case"],"answer":x["answer"],"marker_present":x["marker_present"]} for x in d.get("hidden_context",[])],"cleanup":d.get("cleanup")},indent=2))'
```

Look for denied support update/delete, unchanged operator readback, both model answers and all cleanup checks true. The full JSON also contains the exact synthetic prompts and token usage. This gateway/model probe is not a support UI investigation; do not expect an equivalent support-agent trace for it.

## After the test

Temporary memories and conversations are removed in the script’s cleanup block. Existing memories and business records are not reset. It verifies the original memory count, removed temporary conversations and unchanged business revision.

Save the result before repeating—the container result file is overwritten on the next run:

```sh
docker compose -f compose.yaml -f compose.memory.yaml exec -T memory-backend cat /tmp/security-boundaries.json > /tmp/security-boundaries-my-run.json
```

[Verified earlier results](../results/security-boundaries-2026-10-07/REPORT.md) · [Script](../scripts/security-boundaries.py) · [OWASP lesson map](OWASP-SECURITY-MAP.md)
