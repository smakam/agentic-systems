# Optional exercise: connect your full cloud marketplace to Lyzr

This is one adventurous optional integration exercise. The required lesson is the native Basics demonstration. You must already have completed [Cloud Setup](../../../app/CLOUD-SETUP.md), with your own cloud chat/backend, authenticated business MCP service and database/policy store working. This exercise does not redeploy that stack.

## Select the correct resources

Use your authorized GCP project and a **separate marketplace-integration Lyzr agent**. The standalone Basics agent has only a fictional KB and must remain unchanged. The desired path is:

**Cloud chat → GCP application backend → Lyzr hosted agent → authenticated GCP MCP backend → Cloud SQL/policy evidence.**

The app's Lyzr inference credential and the MCP connection credential are different. Keep both in backend/connection secret configuration; never put them in browser code, prompts or screenshots.

## Steps

1. Verify the cloud chat/backend, stable MCP HTTPS endpoint and data/policy target from Cloud Setup. Record resource locations and the endpoint without secret values.
2. Create or identify a marketplace agent you own. Follow the [Lyzr integration reference](../../../app/lyzr/README.md) for its read-only instructions and seven investigation tools, using your **cloud** MCP endpoint instead of historical laptop/tunnel URLs. Confirm begin/end investigation and all business tools are attached.
3. Configure the Lyzr MCP connection's trusted credential to your cloud MCP service. Verify authenticated discovery and an actual read. Do not add unrelated KB/Data Query features as substitute evidence.
4. Configure the cloud web deployment's `lyzr_enabled=true` and your `lyzr_agent_id` in its Terraform variables. From `app`, use `python3 cloud/scripts/configure-lyzr.py --project YOUR_PROJECT_ID` to enter the Lyzr inference key privately into the pre-provisioned secret. Apply your existing Cloud Setup deployment workflow to activate the runtime. This helper writes the secret; it does not deploy the agent or web service.
5. Open your **cloud** marketplace Support interface, select Lyzr runtime and start a fresh conversation. Ask **“Show the items and quantities for order-2.”** Check against the business-tool evidence in your own fixture, not the Basics `order-demo-*` snapshot.
6. In the same conversation ask **“What is their total quantity?”** Then try the follow-up in a new conversation. Record retained context, fresh reads and clarification behavior.
7. Inspect native Lyzr Activity/Traces for model and tool calls. If cloud Langfuse is enabled, compare the application's hosted boundary span with native internal events. One does not prove the other exists.
8. Confirm the business calls reach your GCP backend without relying on a laptop tunnel. Preserve any unrelated deployed agents and databases.

## Document the result

Supply one architecture diagram and a table recording UI/backend/agent/MCP/data placement; authenticated tool names and arguments; returned evidence; session continuity; configured model; native trace link; optional application trace; cost drivers; failed or untested checks. Explain what Lyzr operates and what you still operate. If observing the instructor rather than deploying, label it **observation only**.

There is no required memory benchmark, new dataset or second cloud exercise. Native memory can be inspected during the Basics demo if verified. The fresh-project integration sequence has not been rehearsed end to end; record account-specific adaptations.

## Cleanup

Remove only lab resources you created and disable your optional Lyzr runtime if no longer needed. Revoke/remove your lab connections and secret versions through your normal cloud administration process. Do not delete shared business data, the instructor's agent or the separate Basics agent. Compare your work with [solutions/answers.md](solutions/answers.md).
