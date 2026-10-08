import asyncio, os, unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch
import cloudpickle
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from marketplace_google.agent import build_app, business_headers, OptionalMemory, RuntimeBusinessTools

class AgentChecks(unittest.TestCase):
    def test_credentials_not_serialized(self):
        token='synthetic-credential-do-not-serialize-1234567890'
        with patch.dict(os.environ, {'REMOTE_MCP_URL':'https://example.test/mcp','REMOTE_MCP_API_KEY':token}):
            package=cloudpickle.dumps(build_app())
            self.assertNotIn(token.encode(), package)
            self.assertNotIn(b'https://example.test/mcp', package)
            self.assertEqual(business_headers(None)['Authorization'], 'Bearer '+token)
    def test_https_without_url_credentials(self):
        for url in ['http://example.test/mcp','https://user:secret@example.test/mcp','']:
            with self.subTest(url=url),patch.dict(os.environ, {'REMOTE_MCP_URL':url}):
                with self.assertRaises(ValueError): asyncio.run(RuntimeBusinessTools().get_tools())
    def test_endpoint_resolved_after_serialization(self):
        with patch.dict(os.environ, {'REMOTE_MCP_URL':'https://cloud.example/mcp'}):
            package=cloudpickle.dumps(RuntimeBusinessTools())
        tools=cloudpickle.loads(package)
        with patch.dict(os.environ, {'REMOTE_MCP_URL':'https://local.example/mcp'}), \
             patch('marketplace_google.agent.McpToolset') as toolset:
            toolset.return_value.get_tools=AsyncMock(return_value=[])
            asyncio.run(tools.get_tools())
            self.assertEqual(toolset.call_args.kwargs['connection_params'].url,'https://local.example/mcp')
    def test_memory_control(self):
        async def check():
            with patch.object(PreloadMemoryTool,'process_llm_request',new_callable=AsyncMock) as retrieval:
                tool=OptionalMemory()
                with patch.dict(os.environ, {'GOOGLE_MEMORY_ENABLED':'false'}):
                    await tool.process_llm_request(tool_context=SimpleNamespace(state={'memory_enabled':True}),llm_request=None)
                    retrieval.assert_not_awaited()
                with patch.dict(os.environ, {'GOOGLE_MEMORY_ENABLED':'true'}):
                    await tool.process_llm_request(tool_context=SimpleNamespace(state={'memory_enabled':False}),llm_request=None)
                retrieval.assert_awaited_once()
        asyncio.run(check())
if __name__=='__main__': unittest.main()
