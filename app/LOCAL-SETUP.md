# Course setup — Mac walkthrough, Linux and Windows notes

This is the canonical learner setup for the **local** marketplace, agent, SQL/RAG tools, PostgreSQL, LiteLLM and Langfuse. The baseline services run in Docker; the startup shell script and small Python key-provisioning script run on the host. Google ADK and Lyzr are covered in later platform chapters; they are not required for the initial setup. The [cloud architecture](../course/MARKETPLACE-DEPLOYMENT-ARCHITECTURE.md) is a separate deployment path; local data does not automatically synchronize with it.

The setup chapter demonstrates **Mac**. Follow sections 1–4 for the first run; later chapters keep using that same environment. Sections 5–6 explain the automatically available test workspace and lifecycle operations. Linux and Windows differences are listed separately below so the main walkthrough stays focused.

**Verification status:** the existing Mac development environment has exercised the local stack, main/test workspaces, memory, citations and feedback; this is not a clean Mac installation. The October 8 clean Google Cloud Ubuntu VM passed installation, startup, health, login, database persistence and Langfuse health checks. Live provider questions, vector retrieval, agent traces and feedback on that VM remain unvalidated; see [Linux rehearsal report](LINUX-SETUP-VALIDATION-2026-10-08.md). Windows/WSL2 remains documented but untested. Provider switching, synthetic model/tool calls and embeddings pass for both providers on the existing Mac setup; fresh installation and real-record OpenRouter acceptance are not verified. The repository URL and main branch are supplied below; no versioned release tag is pinned yet.

| Path | Coverage today |
|---|---|
| Mac walkthrough | Existing development environment exercised; clean installation pending |
| Linux | Clean Google VM installation/health passed; live inference/RAG acceptance pending |
| Windows with WSL2 | Adaptation notes only; not tested |

## 1. Install the prerequisites on Mac

| Requirement | What you need |
|---|---|
| Git | To download the course checkpoint |
| Docker Desktop | Running, with Docker Compose **2.24.4 or newer**; the test workspace uses Compose override tags |
| Python 3 | For `scripts/provision-gateway-keys.py`; no local pip packages are required for startup |
| Shell | macOS/Linux shell, or WSL2 on Windows; Windows commands below run inside WSL, not PowerShell |
| Browser | For the marketplace, gateway and traces |
| Inference provider account | A funded OpenAI or OpenRouter API key with access to the configured chat and embedding models; a ChatGPT subscription is separate |
| Internet | Initial image/package downloads, model and embedding calls |

On Mac:

1. Install Git, or use the Git supplied by Apple's Command Line Tools. If `git --version` opens an installation prompt, complete that installation before proceeding.
2. Install and launch [Docker Desktop for Mac](https://docs.docker.com/desktop/setup/install/mac-install/), choosing the installer for Apple silicon or Intel to match your machine. Wait until Docker is running.
3. Install Python 3 if `python3 --version` is unavailable. The startup helper uses Python's standard library, so no virtual environment or local package installation is needed for the initial walkthrough.
4. Open **Terminal**. Run every command in this guide there, from the stated directory. Keep Docker Desktop running while using the course stack.

### CPU, memory and disk guidance

| Resource | Practical starting point |
|---|---|
| Laptop CPU | 4 CPU cores available for comfortable use; no local GPU is required because model inference runs at the selected provider |
| Laptop memory | 16 GB total RAM recommended, with about 8 GB available to Docker; leave room for the OS and browser |
| Free disk | Reserve about 20 GB for initial images/builds and lab data, with more space for growing traces; this is a planning allowance, not a measured installation size |
| Tested Linux VM | 2 vCPUs, 8 GB RAM and a 60 GB boot disk passed installation/health checks; live model/RAG acceptance on that VM remains partial |

An earlier idle/light-use observation was about 3.3 GB across the stack with 7.75 GB allocated to Docker. These figures are not hard minimums or peak measurements. Large batches, indexing and Langfuse retention can increase resource use. Inspect actual Docker memory and disk usage if startup is slow or containers restart. ARM/x86 Mac and Windows fresh-install compatibility have not been independently verified for this release.

You do **not** need local Node.js, PostgreSQL, LiteLLM or Langfuse installations. Their runtimes are packaged in the containers. Python 3.12 and Node 22 are pinned in the image builds; a code editor is optional for the first run.

Check the tools before continuing:

```sh
git --version
docker version
docker compose version
python3 --version
```

`docker version` must show a working server, not just an installed client. Keep ports **5178, 5179, 58000, 55432, 4000, 3000 and 9090** free. Port 5179 is used by the test UI, which startup also launches.

## 2. Download the repository and configure inference

Use the course repository’s `main` branch for the current setup. A course checkpoint is a named branch or tag; we have not pinned a release tag yet, so `main` can change as the course is updated.

```sh
git clone --branch main https://github.com/smakam/agentic-systems.git
cd agentic-systems/app
[ -f .env ] || cp .env.example .env
chmod 600 .env
```

### Get an API account, credit balance and key

You create an API key; you purchase API credits or enable billing on the account that key belongs to.

- **OpenAI:** [sign up or sign in to the OpenAI API platform](https://platform.openai.com/), configure a payment method and add credit through [API billing](https://platform.openai.com/settings/organization/billing/overview), then create a key in [API keys](https://platform.openai.com/api-keys). Use the course’s configured OpenAI models; account/model access may vary. A ChatGPT subscription does not fund API requests. See the [official API quickstart](https://developers.openai.com/api/docs/quickstart).
- **OpenRouter:** [sign up or sign in](https://openrouter.ai/), add funds through [Credits](https://openrouter.ai/settings/credits), then create a key in [API keys](https://openrouter.ai/settings/keys). The balance pays for requests to supported models across OpenRouter’s providers, subject to access, routing and pricing. The course still uses its configured models; it does not provide an arbitrary-model selector. See [OpenRouter account and credit guidance](https://openrouter.ai/support).

**Budget guidance:** USD **10–20 as an initial API-credit planning allowance**, not a measured or guaranteed cost for completing every chapter. Usage depends on repetitions, models, embeddings and evaluation runs. Credit-purchase fees/taxes and optional hosted-platform charges may be additional. A complete course-wide cost estimate has not been measured. Later platform labs are optional; eligible Google Cloud/AWS newcomers and Lyzr free-plan users may receive limited credits, with differing expiry and service restrictions: [Google Cloud](https://cloud.google.com/signup-faqs), [AWS](https://aws.amazon.com/free/), [Lyzr](https://docs.lyzr.ai/agent-lab/plans). Check each lesson and current terms before creating paid resources.

Open `.env` in your editor. Set `INFERENCE_PROVIDER` to `openai` (default) or `openrouter`. For `openai`, fill `OPENAI_API_KEY`; for `openrouter`, fill `OPENROUTER_API_KEY`. Save the file. You do not need both keys for the baseline. Run `./scripts/start.sh` after changing this selection: startup generates the gateway routes for chat, embeddings and the OpenAI evaluation models. The chat UI does not select the inference provider.

| Setting/key | Where it is used | Required? |
|---|---|---|
| `INFERENCE_PROVIDER` | Chooses direct OpenAI or OpenRouter routing in the local LiteLLM gateway | Select one |
| `OPENAI_API_KEY` | LiteLLM calls OpenAI for agent model requests, document/query embeddings and OpenAI evaluation models | Only when `openai` is selected |
| `OPENROUTER_API_KEY` | LiteLLM calls those model and embedding services through OpenRouter | Only when `openrouter` is selected |
| `ANTHROPIC_API_KEY` | Optional evaluation judge through direct Anthropic | Optional, for that evaluation lesson |
| `LAKERA_API_KEY` | Optional Lakera guardrail checks | Optional, for that security lesson |
| `SUPPORT_GATEWAY_KEY`, `EVAL_GATEWAY_KEY`, `JUDGE_GATEWAY_KEY` | Application-to-LiteLLM access, scoped to the allowed model aliases | Generated by startup |

Leave the three gateway keys empty on a new installation. Startup provisions them; do not paste a provider key into those fields or the browser. The agent sends model requests to LiteLLM using its scoped gateway key, and LiteLLM authenticates upstream with the selected provider key. Document indexing and query embeddings also pass through the gateway. Provider choice does not move the application or database to the cloud. Keep `AGENT_TOOL_TRANSPORT=mcp` for the baseline.

The course uses the configured model aliases for repeatable demonstrations. Arbitrary model selection is not part of the setup UI: advanced learners may change the code/configuration, but those choices are not validated against the course’s expected results.

The selected provider also routes the OpenAI model comparisons used later. The optional judge continues to use Anthropic directly. Provider routes can differ in model availability and behavior; record the chosen route when comparing results. OpenRouter’s embedding endpoint supports the same `text-embedding-3-small` model used by our baseline: [OpenRouter embedding documentation](https://openrouter.ai/docs/api/api-reference/embeddings/create-embeddings). Both routes keep the embedding model/dimension unchanged; do not switch embedding families without rebuilding the index.

Validation status: both routes passed live synthetic model/tool calls and 1,536-dimensional embeddings, and the actual startup script switched to OpenRouter and back to OpenAI on the existing Mac setup. This is not a clean-install or real-record OpenRouter acceptance test. See the [provider-switch report](results/provider-switch-2026-10-12/REPORT.md).

The default provider routes use **GPT-5.4** through the `support-model` alias and `text-embedding-3-small` for embeddings. Historical reports may use Nano; they do not describe the current default. Check the provider configuration before changing a model. If your account cannot access a configured model, resolve that before treating an answer as a course test result.

Real questions and document indexing incur provider charges. The app's cost estimate is not an invoice or a billing-account cap. Its run cost stop is checked after a model call and can overshoot by one call; embedding charges are separate. Set provider-side spending controls appropriate to your lab.

## 3. Start both workspaces and shared services

From the `app` directory:

```sh
./scripts/start.sh
docker compose ps
curl --fail http://localhost:58000/api/health
```

Startup creates PostgreSQL, initializes the gateway database, provisions scoped keys into the gitignored `.env`, and starts the main marketplace, isolated test workspace, gateway and Langfuse services. It creates the test database if missing and attempts document embeddings in both workspaces. The first run may take several minutes. Restarting an existing setup does not reset its business data or conversations.

| Workspace | Purpose |
|---|---|
| Main marketplace | Normal exploration: place orders, change business states and keep your ongoing conversations/data |
| Isolated test marketplace | Repeatable lessons and exercises using a known seeded baseline or a named fixture, without changing main-workspace data |

Most investigation exercises only read business records, so they do not require a reset after each question. Questions still save conversations and traces. Some lessons deliberately change marketplace state or saved memory; those lessons specify when to restore their seed/fixture before repeating the scenario. Reset only when the required starting state has changed, not after every read-only exercise. Normal startup preserves both workspaces and never performs a lesson reset. Section 5 explains isolation; lesson-specific guides provide any required reset instructions.

If startup reports that vector indexing is unavailable, the UI may still load. Fix the key/provider error and index again; don't count lexical fallback as a successful vector-retrieval test.

| Surface | URL | Login |
|---|---|---|
| Marketplace | [localhost:5178](http://localhost:5178/) | `operator` or `support`, password `demo-marketplace` |
| Isolated test marketplace | [127.0.0.1:5179](http://127.0.0.1:5179/) | Same seeded demo accounts/password, with separate data and sessions |
| Local Langfuse | [localhost:3000](http://localhost:3000/) | `operator@example.local`, password `demo-marketplace` |
| LiteLLM dashboard | [localhost:4000/ui](http://localhost:4000/ui/) | `admin`, password `sk-marketplace-local` (**local demo gateway master key**, not a provider API key) |
| Backend API docs | [localhost:58000/docs](http://localhost:58000/docs) | Browser/API authentication required for protected operations |

Other seeded marketplace usernames are `buyer`, `buyer2` and `seller`, with the same demo password. Use **localhost** consistently for the main UI and **127.0.0.1** for the test UI. Both hostnames point to your laptop. We intentionally use different hostnames because browser login cookies are scoped by hostname, not by port; this keeps the two workspaces’ login sessions from interfering with each other. Both are started by the same command; no additional setup is required. Section 5 explains test-workspace use and explicit fixture resets. These public demo credentials and loopback port bindings are for a laptop lab; they are not a cloud authentication setup.

Sign in as **operator**, open **Support workspace**, and find **Workspace options → Documents** on the right. Click **Index documents** if needed, and wait for the indexing status. Indexing embeds missing chunks; it does not reset business records.

## 4. Verify the services and logins

For this setup chapter, confirm that the services are running and that you can open and sign in to all four applications. You do not need to ask an agent question yet.

| Application | Check |
|---|---|
| Main marketplace | Open `http://localhost:5178`, sign in as `operator`, and see the marketplace and Support workspace |
| Isolated test marketplace | Open `http://127.0.0.1:5179`, sign in as `operator`, and see the separate test workspace |
| LiteLLM dashboard | Open `http://localhost:4000/ui`, sign in with the local demo credentials in section 3, and confirm the dashboard loads |
| Local Langfuse | Open `http://localhost:3000`, sign in with the local demo credentials in section 3, and open the local project |

Use the documented main/test hostnames to keep login sessions separate. If a service is not ready, use section 9 before proceeding. A successful login verifies service access, not model answer quality or provider billing/access. Keep your selected provider key configured; Chapter Five verifies model/tool calls, business and policy evidence, and traces using the [first-agent verification checks](docs/FIRST-AGENT-VERIFICATION.md).

## 5. Use the automatically available test workspace

`./scripts/start.sh` starts both workspaces. The main UI uses `market`; the test UI uses disposable `market_test`. Startup creates the test database if missing; the test backend initializes/seeds an empty database, while existing test data is preserved. Both workspaces share the gateway and observability services, but not business records, logins, conversations or memories. An operator-created memory does not become a support user's memory.

No additional first-run command is needed. Open **[127.0.0.1:5179](http://127.0.0.1:5179/)** and sign in with the seeded demo accounts. Use **127.0.0.1**, not localhost: the test backend allows that origin, and the separate hostname avoids login-cookie collisions with the main workspace. Test questions still incur inference charges. Startup indexes documents in both workspaces; verify readiness before using vector-retrieval exercises.

Never run a fixture reset, `scripts/test.sh`, or another runner against `market_test` while someone is using the test UI. They share and may replace that disposable database. No fixture/reset command here should be pointed at a real external database.

## 6. Stop, resume and reset deliberately

| Action | Effect |
|---|---|
| `docker compose -f compose.yaml -f compose.memory.yaml stop` | Stops both workspaces and shared services; keeps named volumes/data |
| `./scripts/start.sh` | Starts/resumes both workspaces; applies provider selection and preserves existing data |
| `./scripts/reset.sh --confirm-demo-reset` | Erases/reseeds main marketplace state, sessions, conversations and memories; local Langfuse traces remain |
| `./scripts/memory-repeatable.sh --reset` | Erases/reseeds **only market_test**; stop the test UI first |

**When to reset:**

- **Main marketplace:** after placing orders, processing returns or payouts, changing the demo clock, or other exploration, when you intentionally want to start again from the original seeded marketplace. This also removes that workspace’s logins, conversations and saved memories.
- **Test workspace:** after a lesson/test changes its business records or saved memory and you need the clean baseline before repeating that exercise. If a lesson requires a named fixture, use that lesson’s preparation instructions rather than assuming the clean baseline is its starting point.
- **No reset needed:** ordinary read-only questions, stopping/resuming services, or changing the inference provider. Startup preserves existing data.

The two reset commands target different databases: `./scripts/reset.sh --confirm-demo-reset` resets only the main `market` workspace and does not reset `market_test`. `./scripts/memory-repeatable.sh --reset` resets only `market_test` and does not change the main workspace.

The stop command above includes both workspaces. After either database reset, sign in again and check document indexing. Do not use `docker compose down -v` as normal cleanup: it deletes named volumes, including database and trace storage.

The integration test command `./scripts/test.sh` also uses disposable `market_test`, not the interactive `market` database. The evaluation command `./scripts/evaluate.sh` uses `market_eval` and makes **paid model calls**. Neither is required for the first UI smoke check.

## 7. Linux differences — Ubuntu laptop or Google Cloud VM

Use the same application configuration, startup script and verification questions. For a headless VM, install [Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/) with its **Docker Compose plugin**, rather than Docker Desktop. Install Git, Python 3 and curl through the distribution's package manager. Check the installed Compose version against section 1; an older distribution package may not support our override tags.

Run `docker version` and `docker compose version` as the same account that will run `./scripts/start.sh`. Configure Docker access according to the installation guide before startup. Do not alternate between a normal checkout and `sudo ./scripts/start.sh`: that can create root-owned files and a different Docker setup. Membership in the Docker group grants extensive host access and is appropriate only for a trusted lab account.

Our service ports bind to loopback. On a remote VM, `localhost` in your laptop browser is your laptop, not the VM. Use SSH port forwarding for the required UI ports and keep the services private; do not change the Compose bindings to public addresses just to reach the demo. Forward **5178** for the marketplace, **3000** for Langfuse, and **4000** for the gateway dashboard. Forward **5179** for the test workspace. Preserve the documented browser hostnames for main and test workspaces.

## 8. Windows setup — Ubuntu inside Windows using WSL2

For Windows, this course uses **Ubuntu inside Windows through Windows Subsystem for Linux 2 (WSL2)**. You keep using your Windows desktop and browser, but run our shell scripts in the Ubuntu terminal. You do not need to create a separate cloud VM or translate the scripts into PowerShell.

1. **Install WSL2 and Ubuntu.** Follow [Microsoft’s WSL installation guide](https://learn.microsoft.com/en-us/windows/wsl/install). On a supported Windows installation, open PowerShell as administrator and run:
   ```powershell
   wsl --install -d Ubuntu
   ```
   Restart Windows when prompted. Launch **Ubuntu** from the Start menu and create the Linux username/password when asked. In PowerShell, `wsl --list --verbose` should show Ubuntu using version **2**; use Microsoft’s guide if it does not.
2. **Install Docker Desktop for Windows.** Follow [Docker Desktop’s WSL2 setup](https://docs.docker.com/desktop/features/wsl/). Enable the WSL2 engine and Ubuntu integration in Docker Desktop’s settings. Keep Docker Desktop running. Follow its current Windows/WSL system requirements; do not separately install Docker Engine inside Ubuntu for this Docker Desktop path.
3. **Open the Ubuntu terminal and install the command-line prerequisites.** Run the following inside Ubuntu, not PowerShell:
   ```sh
   sudo apt update
   sudo apt install -y git python3 curl
   git --version
   python3 --version
   docker version
   docker compose version
   ```
   Docker must show a working server, and Compose must meet the version requirement in section 1.
4. **Run the shared application setup in Ubuntu.** Create a working folder in your Linux home directory, for example `mkdir -p ~/courses && cd ~/courses`. Follow sections 2–4 from there: clone the repository, create/configure the ignored `.env`, run `./scripts/start.sh`, and verify the application. Use the resource guidance in section 1. Clone inside the Linux filesystem rather than `/mnt/c`, and preserve LF shell-script line endings.
5. **Open the application in your Windows browser.** Use the same URLs in section 3: main workspace on `localhost`, test workspace on `127.0.0.1`, with their documented ports. If access fails, check Docker/WSL integration and local forwarding before changing application origins or exposing ports.

Only the initial WSL/Docker setup and the shell/file locations differ from Mac. Application commands, provider selection, questions and expected evidence are shared. This Windows/WSL2 path is **documented from the official instructions but has not been validated on a Windows machine for this release**.

## 9. Troubleshooting

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

## 10. Optional cloud setup

For a separately deployed marketplace, OpenAI Agents SDK, HTTP MCP service and cloud tracing, follow [CLOUD-SETUP.md](CLOUD-SETUP.md). It covers the optional Google Cloud path and the application, MCP and Langfuse URLs used in Chapters Five and Eight. This is not an option passed to `scripts/start.sh`, and local/cloud data does not synchronize automatically.

The cloud path currently uses OpenAI and Langfuse Cloud Japan. Existing deployed behavior is verified; a fresh-project installation rehearsal remains deferred. Local setup is sufficient for the required course path.

## 11. Later lessons: optional services and hosted platforms

- **Guardrails:** the first smoke test needs none. Built-in privacy is configured in the gateway; Presidio requires the optional `compose.guardrails.yaml` services, and Lakera requires its provider key/config overlay. Follow the [combined Guardrails and Agent Security guide](docs/SECURITY-CHAPTER-DEMO.md) rather than enabling every profile during initial setup.
- **Lyzr / Google ADK:** native hosted sessions, memory and telemetry belong to those platform lessons. A tunnel is only needed when a hosted agent must reach your laptop's authenticated remote business MCP endpoint. It is not needed for local SQL, RAG or personal memory. Use [Lyzr setup](lyzr/README.md) or the [single Google walkthrough](../course/GOOGLE-PLATFORM-WALKTHROUGH.md); remote access/secrets must be configured deliberately. The current shared remote business key does not establish per-user private memory access.
- **Cloud:** the optional setup path is in Section 10. The local Compose file uses local Langfuse; creating a Langfuse Cloud account does not redirect laptop traces automatically.
