# Lyzr Agent Platform

For the standalone lesson, follow [Support Agent Basics](../../course/setup/lyzr-agent-platform/setup-guide.md). It uses the supplied fictional document and native knowledge base in Playground, without the Marketplace MCP service.

The optional [full-cloud marketplace integration](../../course/setup/lyzr-agent-platform/cloud-integration.md) connects a separately created Lyzr agent to your authenticated Google Cloud business tools and existing web backend. Lyzr owns the agent loop; Google Cloud hosts the application and business data. Keep the Basics agent unchanged and use your own agents, credentials and cloud resources.

`agent-instructions.txt` contains the marketplace agent instructions. The application runtime configuration is described in [Runtime selector](../RUNTIME-SELECTOR.md).

The repository also retains local remote-MCP/tunnel scripts for development. Those historical paths are not required for either course setup path and depend on separately provisioned tunnel services. Do not reuse an instructor endpoint, agent ID or credential.
