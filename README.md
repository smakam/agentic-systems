# Agentic Systems

Private source repository for the marketplace application and agentic-systems course reference implementation.

## Run locally

Start with [the Mac-first setup guide](app/LOCAL-SETUP.md), which also describes Linux and Windows differences. Application commands run from `app/`:

```sh
cp app/.env.example app/.env
# Configure your own model provider key privately in app/.env.
cd app
./scripts/start.sh
```

[Application guide](app/README.md) · [Course outline](course/COURSE-PLAN.md) · [Specification](SPECIFICATION.md) · [Cloud deployment guide](app/cloud/README.md)

## Repository contents

Source, tests, dependency manifests, seed fixtures, deployment scripts and technical documentation are versioned here. Slides, recording material, local credentials, Terraform state, dependency directories and generated run outputs are excluded. Some historical guides link to verification outputs retained locally; those receipts are not distributed in this repository.

The private repository is for the owner's development workflow. Learner publication and a release checkpoint remain separate steps. Existing-cloud and existing-laptop validation does not imply every fresh setup path has been verified.
