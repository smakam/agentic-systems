"""Local read-only MCP server. One process owns one investigation snapshot."""
import json, os
from mcp.server import MCPServer
from .tools import ReadContext
from .tool_contracts import build_tool_functions

def main():
    settings=json.loads(os.getenv("CONTEXT_COMPARISON_JSON", "{}"))
    ctx = ReadContext(suppress_catalog=bool(settings.get("suppress_catalog")),suppress_documents=bool(settings.get("suppress_documents")))
    server = MCPServer('Marketplace read tools')
    for fn in build_tool_functions(ctx):
        server.tool(structured_output=False)(fn)

    @server.resource('marketplace://run/state')
    def run_state() -> str:
        """Application bookkeeping; not an additional model tool."""
        return json.dumps(dict(snapshot=ctx.snapshot, doc_hash=ctx.doc_hash,
                              evidence=ctx.evidence,
                              calls=ctx.calls), default=str)

    try:
        server.run(transport='stdio')
    finally:
        ctx.close()

if __name__ == '__main__':
    main()
