"""MCP connection and run bookkeeping, separate from model-visible tools."""
import json
import os
import sys
from agents.mcp import MCPServerStdio

def open_mcp():
    # Do not pass business-write credentials, provider keys or tracing secrets.
    allowed = ('READ_DATABASE_URL', 'LITELLM_URL', 'LITELLM_API_KEY', 'DATA_DIR',
               'GATEWAY_IAM_AUDIENCE')
    return MCPServerStdio(
        name='Marketplace read tools',
        params={'command': sys.executable, 'args': ['-m', 'marketplace.mcp_server'],
                'env': {k: os.environ[k] for k in allowed if k in os.environ}},
        cache_tools_list=True, client_session_timeout_seconds=60)

class RemoteReadContext:
    def __init__(self, server):
        self.server = server

    @classmethod
    async def create(cls, server):
        ctx = cls(server)
        await ctx.refresh()
        return ctx

    async def refresh(self):
        result = await self.server.read_resource('marketplace://run/state')
        data = json.loads(result.contents[0].text)
        self.snapshot = data['snapshot']
        self.doc_hash = data['doc_hash']
        self.evidence = data['evidence']
        self.calls = data['calls']

    async def order_history(self, order_id):
        result = await self.server.call_tool('get_order_history', {'order_id': order_id})
        if result.is_error:
            raise RuntimeError('MCP order history unavailable')
        return json.loads(result.content[0].text)


def open_memory_mcp(owner_id, conversation_id, snapshot, *, run_id=None,
                    allow_write=False, allowed_operations=()):
    """Bind identity/permissions at process launch, never through model arguments."""
    config=dict(owner_id=owner_id,conversation_id=conversation_id,snapshot=snapshot,
                run_id=run_id,allow_write=allow_write,
                allowed_operations=sorted(allowed_operations))
    env={k:os.environ[k] for k in ('DATABASE_URL',) if k in os.environ}
    env['MEMORY_CONTEXT_JSON']=json.dumps(config,default=str)
    return MCPServerStdio(name='Marketplace personal memory',
        params={'command':sys.executable,'args':['-m','marketplace.memory_mcp_server'],'env':env},
        cache_tools_list=True,client_session_timeout_seconds=60)

class LocalMemoryContext:
    def __init__(self,server):
        self.server=server
        self.operations=[]

    async def refresh(self):
        result=await self.server.read_resource('marketplace://memory/operations')
        self.operations=json.loads(result.contents[0].text)
