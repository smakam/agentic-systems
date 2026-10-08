"""ADK support agent with authenticated business MCP and native memory."""
import os
from pathlib import Path
from urllib.parse import urlsplit

from agentplatform.frameworks import AdkApp
from google.adk.agents import Agent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.tools.base_toolset import BaseToolset

BUSINESS_TOOLS = [
    'begin_investigation', 'end_investigation', 'get_catalog',
    'query_business_data', 'search_documents', 'fetch_evidence', 'get_order_history',
]


def business_headers(_context):
    # Resolve only at invocation: credentials must not enter the serialized agent.
    token = os.environ.get('REMOTE_MCP_API_KEY', '')
    if len(token) < 32:
        raise ValueError('Configure REMOTE_MCP_API_KEY using a runtime secret')
    return {'Authorization': 'Bearer ' + token, 'ngrok-skip-browser-warning': '1'}


class RuntimeBusinessTools(BaseToolset):
    """Resolve endpoint after deployment, never bake a deploy-time URL into pickle."""
    def __init__(self):
        super().__init__()
        self._delegate = None

    async def get_tools(self, readonly_context=None):
        if self._delegate is None:
            endpoint = os.environ.get('REMOTE_MCP_URL', '')
            parsed = urlsplit(endpoint)
            if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
                raise ValueError('REMOTE_MCP_URL must be an authenticated HTTPS MCP endpoint')
            self._delegate = McpToolset(
                connection_params=StreamableHTTPConnectionParams(
                    url=endpoint, timeout=20, sse_read_timeout=180),
                header_provider=business_headers, tool_filter=BUSINESS_TOOLS)
        return await self._delegate.get_tools(readonly_context)

    async def close(self):
        if self._delegate is not None:
            await self._delegate.close()
            self._delegate = None


class OptionalMemory(PreloadMemoryTool):
    """Memory policy belongs to the hosted agent's deployment configuration."""
    async def process_llm_request(self, *, tool_context, llm_request):
        if os.environ.get('GOOGLE_MEMORY_ENABLED', 'true').lower() == 'true':
            await super().process_llm_request(
                tool_context=tool_context, llm_request=llm_request)


def build_agent():
    model = os.environ.get('GOOGLE_AGENT_MODEL', 'gemini-3.5-flash')
    business = RuntimeBusinessTools()
    return Agent(
        name='marketplace_support', model=Gemini(
            model=model,
            client_kwargs={'enterprise': True, 'location': os.environ.get('GOOGLE_MODEL_LOCATION', 'us')},
        ),
        description='Read-only marketplace support with native sessions and memory',
        instruction=Path(__file__).with_name('instructions.txt').read_text(),
        tools=[business, OptionalMemory()],
    )


def build_app():
    # AdkApp selects managed Sessions/Memory Bank after deployment.
    # Local execution uses in-memory services and is not proof of cloud memory.
    # Runtime telemetry is controlled by deploy.py environment settings.
    return AdkApp(agent=build_agent(), app_name='marketplace_support')
