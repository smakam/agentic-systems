# Marketplace deployment architecture

The canonical deployment commands and project-boundary diagram are in [Cloud Setup](../app/CLOUD-SETUP.md). This document records system responsibilities, not a second setup procedure.

## Supported course paths

| Path | Application and business data | Agent execution |
|---|---|---|
| Local Marketplace | Laptop Docker services | Local SDK in the backend, stdio business MCP |
| Standalone platform Basics | Packaged fictional data / platform Knowledge Base | Native platform Playground |
| Full cloud Marketplace | Google Cloud Marketplace project | SDK in its backend, or a configured hosted Google/Lyzr agent |

The supported learner paths do not mix local chat with cloud business data or use a laptop tunnel. Historical experiments are retained in Git history.

## Project boundaries

- **Marketplace Google Cloud project:** Cloud Run web application/backend, business HTTP MCP service, private LiteLLM gateway, Cloud SQL, runtime identities, Secret Manager, image registry and Terraform state support.
- **Google agent project:** the Marketplace-compatible managed Google agent, its runtime identity/staging resources, and native sessions, memory and telemetry. The Marketplace backend has scoped runtime-query permission in this project. The agent calls the Marketplace project's authenticated business MCP endpoint.
- **External services:** OpenAI handles SDK inference/embeddings; Langfuse Cloud receives application/gateway telemetry. Lyzr remains a separate hosted platform configured in its own lesson.

The standalone Google Basics deployment is a different agent, with fictional JSON/native tools. It does not contain Marketplace MCP tools and cannot replace the integrated Marketplace agent.

## Runtime and data contracts

The frontend and application backend share one Cloud Run web service. The SDK executes inside that backend. Choosing a hosted runtime changes the execution adapter and starts a new conversation; history retains its original runtime/session. Runtime selection does not deploy an agent or repoint its tool endpoint.

Business tools retain evidence for the investigation. The backend binds trusted user/session context; business middleware enforces authorization. The model cannot grant itself access. Provider keys and service credentials remain on trusted servers, scoped through Secret Manager and runtime identity.

Local and cloud data, conversations and memory are independent. Native platform memory is distinct from SDK Internal/Mem0 controls. A one-time historical data alignment does not establish ongoing synchronization.

## Telemetry and verification

SDK runs expose model/tool observations in the appropriate local or cloud Langfuse project. Hosted Google/Lyzr runs have application-boundary observations, while native internal execution is inspected in the platform's own traces. An application trace is not proof of every hosted internal tool call.

Existing deployment checks are bounded historical acceptance, not a production-readiness claim. The fresh two-project learner installation remains unvalidated. See [HTTP MCP acceptance](../app/cloud/VALIDATION-2026-10-10-SDK-HTTP-MCP.md) and the status in [Cloud Setup](../app/CLOUD-SETUP.md).
