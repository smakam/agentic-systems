"""Local stdio memory tools scoped by trusted application launch context."""
import json
import os
from mcp.server import MCPServer
from .memory import MemoryStore, build_memory_functions

def main():
    config=json.loads(os.environ['MEMORY_CONTEXT_JSON'])
    store=MemoryStore(**config)
    server=MCPServer('Marketplace personal memory')
    for fn in build_memory_functions(store):
        server.tool(structured_output=False)(fn)

    @server.resource('marketplace://memory/operations')
    def operations() -> str:
        """Application audit bookkeeping, outside model-visible tool arguments."""
        return json.dumps(store.operations,default=str)

    server.run(transport='stdio')

if __name__=='__main__':
    main()
