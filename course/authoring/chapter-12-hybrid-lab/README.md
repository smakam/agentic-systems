# Historical agent-only hosting experiment

This directory preserves the October 10 validation, results and source scripts for the earlier Cloud Run agent → tunnel → local HTTP MCP experiment. It is not the current Runtime and Hosting learner exercise.

The current exercise is a read-only local/cloud deployment worksheet, with reference answers in course/exercises/runtime-and-hosting/solutions/answers.md. No tunnel, historical hosting UI, cloud deployment, database reset or these scripts are required.

Source scripts and command text are retained as historical snapshots; relative paths may reflect their original location. They are not supported worksheet entry points. Recorded service availability and cleanup describe the validation date, not current live state.

## Topic-based configuration names

The course overlays are `app/compose.course-agent-loop.yaml` and
`app/compose.course-runtime-and-hosting.yaml`. The private hosting configuration
is `app/.course-runtime-and-hosting.env`; its tunnel log/PID and cloud state use
the same `.course-runtime-and-hosting` prefix. These files stay ignored by Git.

New configuration uses `AGENT_LOOP_LAB`, `HOSTING_LAB`, and
`HOSTED_AGENT_URL`, `HOSTED_AGENT_API_KEY`, `HOSTED_AGENT_MODEL`. The backend
also accepts the former environment keys for existing cloud deployments; an
explicit new value takes precedence, including an empty value. Newly generated
configuration uses only the topic-based keys.

The existing `ch11_loop_lab`/`ch12_hosting_lab` database names and `ch11-*`/`ch12-*`
Compose service identifiers and profiles are retained as compatibility identities.
They preserve existing data and containers rather than creating duplicate services
or resetting databases. This source cleanup does not rename deployed cloud
resources, restart services, or redeploy the cloud agent. Historical deployment
records retain their original resource names.

For an existing checkout that still has the former private files, move them to
the topic-based names before the next startup. Do not overwrite an existing
destination. The environment file may retain the old keys temporarily because
the backend accepts them; update them to the new keys before using the cloud
deployment script. Former private filenames also remain ignored throughout
migration.
