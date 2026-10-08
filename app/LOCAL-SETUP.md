# Course setup — Mac walkthrough, Linux and Windows notes

This is the canonical learner setup for the **local** marketplace, agent, SQL/RAG tools, PostgreSQL, LiteLLM and Langfuse. The baseline services run in Docker; the startup shell script and small Python key-provisioning script run on the host. Google ADK and Lyzr are covered in later platform chapters; they are not required for the initial setup. The [cloud architecture](../course/MARKETPLACE-DEPLOYMENT-ARCHITECTURE.md) is a separate deployment path; local data does not automatically synchronize with it.

The setup chapter demonstrates **Mac**. Follow sections 1–4 for the first run; later chapters keep using that same environment. Sections 5–6 cover optional test data and lifecycle operations. Linux and Windows differences are listed separately below so the main walkthrough stays focused.

**Verification status — October 8, 2026:** commands below are checked against the current scripts and configuration. The existing Mac development machine has exercised the local stack, main/test workspaces, memory, citations and feedback. This is an existing-machine check, not a fresh Mac installation. A clean Google Cloud Linux VM rehearsal is planned and has not passed yet; Windows/WSL2 is documented but unverified. A Linux result would validate the shared container workflow, not Mac installation or processor compatibility. The published GitHub URL/versioned learner checkpoint also remains a release check. Replace the clone placeholders before distributing the course.

| Path | Coverage today |
|---|---|
| Mac walkthrough | Existing development environment exercised; clean installation pending |
| Linux | Commands reviewed; clean Google VM rehearsal pending |
| Windows with WSL2 | Adaptation notes only; not tested |

### Setup chapter recording plan

Use a few orientation slides for prerequisites and the setup sequence, then show the local terminal and application. Link this guide as the learner reference. Demonstrate configuration without displaying keys, startup, login, one successful question, and its trace. Keep detailed installation commands and troubleshooting in this document rather than reading every command aloud. Learners finish setup when the first-run checks in section 4 pass; the next chapter walks through the first agent and its code.

## 1. Install the prerequisites on Mac

| Requirement | What you need |
|---|---|
| Git | To download the course checkpoint |
| Docker Desktop | Running, with Docker Compose **2.24.4 or newer**; the optional test workspace uses Compose override tags |
| Python 3 | For `scripts/provision-gateway-keys.py`; no local pip packages are required for startup |
| Shell | macOS/Linux shell, or WSL2 on Windows; Windows commands below run inside WSL, not PowerShell |
| Browser | For the marketplace, gateway and traces |
| OpenAI API account | A funded API key with access to the configured support and embedding models; a ChatGPT subscription is separate |
| Internet | Initial image/package downloads, model and embedding calls |

On Mac:

1. Install Git, or use the Git supplied by Apple's Command Line Tools. If `git --version` opens an installation prompt, complete that installation before proceeding.
2. Install and launch [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/), choosing the installer for Apple silicon or Intel to match your machine. Wait until Docker is running.
3. Install Python 3 if `python3 --version` is unavailable. The startup helper uses Python's standard library, so no virtual environment or local package installation is needed for the initial walkthrough.
4. Open **Terminal**. Run every command in this guide there, from the stated directory. Keep Docker Desktop running while using the course stack.

Allow several GB of free RAM and disk for Langfuse's PostgreSQL, ClickHouse, Redis and object storage. A previous idle/light-use observation was about 3.3 GiB across the stack with 7.75 GiB allocated to Docker; this is not a hardware minimum or peak measurement. Start with roughly 8 GiB available to Docker and inspect actual usage. ARM/x86 and Windows fresh-install compatibility have not been independently verified for this release.

You do **not** need local Node.js, PostgreSQL, LiteLLM or Langfuse installations. Their runtimes are packaged in the containers. Python 3.12 and Node 22 are pinned in the image builds; a code editor is optional for the first run.

Check the tools before continuing:

```sh
git --version
docker version
docker compose version
python3 --version
```

`docker version` must show a working server, not just an installed client. Keep ports **5178, 5179, 58000, 55432, 4000, 3000 and 9090** free. Port 5179 is only needed for the optional test UI.

## 2. Download the checkpoint and configure inference

Replace both placeholders with the repository URL and checkpoint supplied with the course. No published remote is configured in the current source directory, so a URL is not invented here.

```sh
git clone --branch <COURSE_CHECKPOINT> <COURSE_REPOSITORY_URL> ai-systems-blogging
cd ai-systems-blogging/app
[ -f .env ] || cp .env.example .env
chmod 600 .env
```

Open `.env` in your editor. Set **OPENAI_API_KEY** to your own API key and save. Leave `SUPPORT_GATEWAY_KEY`, `EVAL_GATEWAY_KEY` and `JUDGE_GATEWAY_KEY` empty on a new installation: startup generates model-scoped virtual keys for them. Do not paste your provider key into those fields or into the browser.

The baseline needs only the OpenAI key. `ANTHROPIC_API_KEY` is for the optional evaluation judge; `LAKERA_API_KEY` is for the later Lakera lesson. Leave the other optional fields empty until that lesson. Keep `AGENT_TOOL_TRANSPORT=mcp` for the baseline.

The current configuration in `compose.yaml`/`infra/litellm.yaml` uses **GPT-5.4** through the `support-model` alias and `text-embedding-3-small` for embeddings. Historical reports may use Nano; they do not describe the current default. Check the checkpoint configuration before changing a model. If your account cannot access a configured model, resolve that before treating an answer as a course test result.

Real questions and document indexing incur provider charges. The app's cost estimate is not an invoice or a billing-account cap. Its run cost stop is checked after a model call and can overshoot by one call; embedding charges are separate. Set provider-side spending controls appropriate to your lab.

## 3. Start the stack

From the `app` directory:

```sh
./scripts/start.sh
docker compose ps
curl --fail http://localhost:58000/api/health
```

Startup creates PostgreSQL, initializes the gateway database, provisions scoped keys into the gitignored `.env`, builds/starts the application and Langfuse services, then attempts document embeddings. The first run may take several minutes. Restarting an existing setup does not reset its business data or conversations.

If startup reports that vector indexing is unavailable, the UI may still load. Fix the key/provider error and index again; don't count lexical fallback as a successful vector-retrieval test.

| Surface | URL | Login |
|---|---|---|
| Marketplace | [localhost:5178](http://localhost:5178/) | `operator` or `support`, password `demo-marketplace` |
| Local Langfuse | [localhost:3000](http://localhost:3000/) | `operator@example.local`, password `demo-marketplace` |
| LiteLLM dashboard | [localhost:4000/ui](http://localhost:4000/ui/) | `admin`, password is the **local demo master key** configured in `compose.yaml` |
| Backend API docs | [localhost:58000/docs](http://localhost:58000/docs) | Browser/API authentication required for protected operations |

Other seeded marketplace usernames are `buyer`, `buyer2` and `seller`, with the same demo password. Use **localhost** consistently for the main UI. These public demo credentials and loopback port bindings are for a laptop lab; they are not a cloud authentication setup.

Sign in as **operator**, open **Support workspace**, and find **Workspace options → Documents** on the right. Click **Index documents** if needed, and wait for the indexing status. Indexing embeds missing chunks; it does not reset business records.

## 4. Verify one complete question and its trace

Use a newly seeded workspace for the stated business expectations. An existing workspace may have different order status because you changed it in a prior lesson.

1. Start a new conversation. Leave gateway guardrails **Off**, long-term memory **Off**, and memory changes **Off**. Keep source authority at its normal enabled setting.
2. Ask: **“What products, quantities and sellers are in order-1?”** Expected seed: two Canvas Weekenders from Cedar & Co. and two Desk Lamps from Northstar Goods. Open the database citation to inspect records; prose alone is not evidence.
3. In that same conversation, ask: **“What is the total quantity of those items?”** Expected total: **4**. This checks short-term conversation context, regardless of whether the model reuses records or queries again.
4. In a new conversation, ask: **“What does the payout policy require before a seller can be paid?”** Inspect policy citations and the search result. The normal policy requires confirmed delivery plus a 24-hour hold, subject to blockers such as active returns. Verify vector versus lexical retrieval in the returned technical details.
5. Open the answer's trace in local Langfuse, project **Support experiments**. One question execution is one trace; generations and tool calls are observations within it. Follow model input → tool result → subsequent generation → final answer. Tool selection is model-dependent, so every question need not follow an identical sequence.
6. Give a completed answer thumbs-down, reload/reopen the conversation, and check the vote persists. Its trace should show `user_feedback = False`; thumbs-up is `True`. PostgreSQL is authoritative; score export to Langfuse is best effort. Scores analytics summarize **rated** answers, not correctness.

The conversation must belong to the signed-in user to rate it. If an answer is incorrect, preserve the trace and evidence; don't change the fixture merely to make it pass. Saved [regression answers](results/core18-history-v3-2026-10-01/REPORT.md) can be inspected without paying to rerun a benchmark.

### Optional long-term memory smoke check

Use a harmless preference and the same signed-in user throughout:

1. New conversation: enable **Use long-term memory** and **Allow memory changes for this question**. Ask: **“Remember that I prefer payout investigation answers as three short bullet points.”**
2. Inspect saved memories and the trace for a successful `save_memory` operation. An acknowledgment alone does not prove persistence. Permission to change memory resets after each question.
3. Start a **new conversation**, keep long-term memory enabled and memory changes disabled. Ask: **“What format do I prefer for payout investigation answers?”** Inspect `search_memories`, its returned preference, and the answer.
4. In another new conversation with long-term memory disabled, ask the same question. It should not retrieve that stored preference. This contrasts cross-conversation memory with ordinary history.

Memory is private per application user. A new conversation is not the same as switching sidebar tabs. A remembered investigation checkpoint is historical context, never authority for current business status. For detailed cases and cleanup use the [memory catalogue](eval/memory-v2/README.md).

## 5. Open the isolated test workspace when a lesson needs it

The main UI uses `market`; the optional test UI uses **disposable `market_test`**. They share the local gateway and observability services, but not business records, logins, conversations or memories. An operator-created memory does not become a support user's memory.

From `app`, with the main stack running:

```sh
sh scripts/memory-repeatable.sh --reset
docker compose -f compose.yaml -f compose.memory.yaml up -d --no-deps --build memory-backend memory-frontend
```

Open **[127.0.0.1:5179](http://127.0.0.1:5179/)** and sign in with the seeded demo accounts. Use **127.0.0.1**, not localhost: the test backend allows that origin, and the separate hostname avoids login-cookie collisions with the main workspace. Test questions still incur inference charges.

For a prepared historical-checkpoint scenario, stop the test services before replacing their data:

```sh
docker compose -f compose.yaml -f compose.memory.yaml stop memory-frontend memory-backend
sh scripts/memory-repeatable.sh --prepare checkpoint
docker compose -f compose.yaml -f compose.memory.yaml up -d --no-deps memory-backend memory-frontend
```

Reload the page and sign in again after a fixture reset. Prepared scenario memories belong to **support**. Follow the [catalogue's exact question and expected state](eval/memory-v2/README.md); this fixture is different from the clean baseline.

Never run a fixture reset, `scripts/test.sh`, or another runner against `market_test` while someone is using the test UI. They share and may replace that disposable database. No fixture/reset command here should be pointed at a real external database.

## 6. Stop, resume and reset deliberately

| Action | Effect |
|---|---|
| `docker compose stop` | Stops the main stack, keeps named volumes/data |
| `./scripts/start.sh` | Resumes the main stack; preserves existing data |
| `./scripts/reset.sh --confirm-demo-reset` | Erases/reseeds main marketplace state, sessions, conversations and memories; local Langfuse traces remain |
| `sh scripts/memory-repeatable.sh --reset` | Erases/reseeds **only market_test**; stop the optional UI first |

Stop the optional test UI using the two-file Compose command in section 5 before stopping the shared main stack. After either database reset, sign in again and check document indexing. Do not use `docker compose down -v` as normal cleanup: it deletes named volumes, including database and trace storage.

The integration test command `./scripts/test.sh` also uses disposable `market_test`, not the interactive `market` database. The evaluation command `./scripts/evaluate.sh` uses `market_eval` and makes **paid model calls**. Neither is required for the first UI smoke check.

## Linux differences — Ubuntu laptop or Google Cloud VM

Use the same application configuration, startup script and verification questions. For a headless VM, install [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/) with its **Docker Compose plugin**, rather than Docker Desktop. Install Git, Python 3 and curl through the distribution's package manager. Check the installed Compose version against section 1; an older distribution package may not support our override tags.

Run `docker version` and `docker compose version` as the same account that will run `./scripts/start.sh`. Configure Docker access according to the installation guide before startup. Do not alternate between a normal checkout and `sudo ./scripts/start.sh`: that can create root-owned files and a different Docker setup. Membership in the Docker group grants extensive host access and is appropriate only for a trusted lab account.

Our service ports bind to loopback. On a remote VM, `localhost` in your laptop browser is your laptop, not the VM. Use SSH port forwarding for the required UI ports and keep the services private; do not change the Compose bindings to public addresses just to reach the demo. Forward **5178** for the marketplace, **3000** for Langfuse, and **4000** for the gateway dashboard. Add **5179** only for the optional test workspace. Preserve the documented browser hostnames for main and test workspaces.

### Clean Google Cloud Linux VM rehearsal

This is an installation rehearsal of the **local Docker stack on a fresh Linux host**, separate from the managed Cloud Run/Cloud SQL deployment. It does not need the existing cloud marketplace database, ADK or Lyzr configuration.

1. Create a disposable Ubuntu VM in the designated rehearsal project, record its OS, CPU architecture, RAM, disk and Docker/Compose versions, and connect by SSH. Start with enough RAM/disk for the full Langfuse stack; the Mac observation above is an estimate, not a guaranteed VM minimum.
2. Install only the prerequisites documented here. Start with an empty working directory and no pre-existing Docker volumes. Avoid copying the instructor's `.env`, ADC credentials, private overlays, runtime profiles or cached images into the learner checkout.
3. Clone the published course checkpoint and follow sections 2–3 literally. Until the repository is published, a sanitized checkpoint archive can rehearse installation, but it does **not** validate the learner's GitHub clone step. Record that limitation.
4. Enter the rehearsal's provider key privately in its ignored `.env`. Verify the funded account has access to the configured model and embedding model. Do not copy keys into the report or shell history.
5. Establish SSH port forwarding, then complete **every section 4 check**: fresh login, seeded order evidence, follow-up quantity, vector policy retrieval, detailed Langfuse trace and feedback persistence. Run the optional memory check and section 5 test workspace if they are included in the learner checkpoint.
6. Stop and resume the stack, reopen the conversation and check retained data. Capture health, indexing mode, pass/fail observations, first-start duration and resource usage. Record observed API usage/cost where available, without treating estimates as billing totals.
7. Fix the guide or scripts for any reproducible gap, then retry from a clean disposable setup if the change affects installation. Do not mark this path validated merely because containers start or health passes.
8. Save a redacted validation report with the exact checkpoint and remaining limitations, then delete the rehearsal VM and associated disks/resources once its results are retained. Merely stopping a VM can retain storage charges.

No clean Linux rehearsal has been completed by the documentation edit. Its result must be added after the actual run.

## Windows differences — WSL2

Use Linux commands inside **WSL2**, rather than translating these scripts into PowerShell. Follow [Docker Desktop's WSL2 setup](https://docs.docker.com/desktop/features/wsl/) to install/configure the backend and enable integration for your Linux distribution. Install Git, Python 3 and curl inside that distribution; confirm the section 1 version commands work in its terminal.

Clone into the WSL Linux home directory, such as `~/courses`, instead of a Windows-mounted directory such as `/mnt/c`. This avoids mixing Windows filesystem behavior with the Linux container workflow. Keep shell scripts with LF line endings; do not copy a Windows-formatted `.env` from another machine. Edit the ignored `.env` locally and use the same startup commands from the WSL checkout.

Open the documented UI URLs in your Windows browser after startup. If loopback forwarding or Docker integration prevents access, inspect WSL/Docker networking before changing application origins or exposing ports. File locations, Docker installation and host networking differ from the recorded Mac walkthrough; application questions and expected evidence are shared. These notes have **not** been validated on a Windows machine for this release.

## Troubleshooting

| Symptom | What to check |
|---|---|
| Docker daemon unavailable | Start Docker Desktop; rerun `docker version` before startup |
| Compose rejects `!reset` or `!override` | Upgrade Docker Desktop/Compose to a version supporting these tags |
| Port already allocated | Stop the conflicting local service; keep frontend proxy/origin settings consistent if deliberately changing ports |
| App will not load | Check `docker compose ps`, then `docker compose logs --tail=80 backend frontend`; backend health must pass before frontend startup |
| Model or indexing fails | Check `.env` key, provider billing/model access and `docker compose logs --tail=80 gateway`; distinguish authentication/rate limits from answer quality |
| Keys changed but old behavior persists | Rerun `./scripts/start.sh` so gateway environment and generated keys reach dependent containers |
| Origin rejected in test UI | Use exactly `http://127.0.0.1:5179/`; refresh and sign in after test backend rebuild |
| Wrong user or unexpected login expires | Main uses localhost, test uses 127.0.0.1; use the documented URLs and sign in again after a reset |
| Retrieval uses lexical fallback | Fix embedding access, then use operator **Workspace options → Documents → Index documents** |
| Trace/feedback score missing | Wait briefly and refresh local Langfuse; check `langfuse-web`/`langfuse-worker` logs. An app-stored vote is not proof of score export |
| Memory not recalled | Same user, new conversation, memory enabled; inspect actual save/search tool results before diagnosing model behavior |
| Order differs from stated seed | You may be on main data modified by prior lessons, or a prepared test scenario. Reset only the intended disposable/demo workspace |
| Container killed or unhealthy | Check `docker stats --no-stream`, free disk and Docker's RAM allocation; the full local tracing stack is heavier than the app alone |

Do not paste `.env`, authentication headers or full rendered Compose configuration into support messages. Share a redacted error and the failing step; logs can include prompts and evidence.

## Later lessons: optional services and hosted platforms

- **Guardrails:** the first smoke test needs none. Built-in privacy is configured in the gateway; Presidio requires the optional `compose.guardrails.yaml` services, and Lakera requires its provider key/config overlay. Follow the [combined Guardrails and Agent Security guide](docs/SECURITY-CHAPTER-DEMO.md) rather than enabling every profile during initial setup.
- **Lyzr / Google ADK:** native hosted sessions, memory and telemetry belong to those platform lessons. A tunnel is only needed when a hosted agent must reach your laptop's authenticated remote business MCP endpoint. It is not needed for local SQL, RAG or personal memory. Use [Lyzr setup](lyzr/README.md) or the [single Google walkthrough](../course/GOOGLE-PLATFORM-WALKTHROUGH.md); remote access/secrets must be configured deliberately. The current shared remote business key does not establish per-user private memory access.
- **Cloud:** use the [cloud deployment guide](cloud/README.md) for the separately deployed stack; the existing project has been exercised, while a fresh-project learner rehearsal remains pending. The local Compose file intentionally uses local Langfuse; creating a Langfuse Cloud account does not automatically redirect this laptop's traces.

Before recording/distribution, replace the clone placeholders, perform a clean-machine install with an empty volume set, record host requirements and observed first-run API cost, and verify model availability. This guide is a code-checked learner path, not evidence that those release checks have already passed.


### Returning to local-only work

Use the local marketplace and select **OpenAI Agents SDK** for the main course demos. The SDK's tools, business data, memory, LiteLLM and Langfuse remain local. `scripts/start.sh` now retains the private Google ADC overlay and test workspace if that overlay already exists, and restarts frontend proxies after backend rebuilds. Fresh learners without the overlay retain the ordinary local startup path. Shell syntax was checked; the full startup script was not rerun against the existing data merely to validate this change.

The independent hosted-backend switch is `python3 scripts/switch-backend.py local --apply` from `app`. It selects the retained local tunnel/key profile for both Google and Lyzr and affects every caller of those shared agents. Keep the laptop MCP service and tunnel running; start fresh platform conversations after switching. Switch back with `cloud --apply` only after restarting the cloud database.

Cloud SQL may be stopped between labs. This preserves cloud records, conversations and memories but makes the cloud marketplace and cloud MCP unavailable until restarted. Storage and retained backups remain billable; stopping SQL does not erase other cloud resources or guarantee zero total project cost. Keep Terraform `database_active=false` while parked so a later apply does not restart compute unintentionally.
