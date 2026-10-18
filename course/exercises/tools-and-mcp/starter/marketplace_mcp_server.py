"""Lab server template: add the seller-balance import and registration."""
import json
import os
from mcp.server import MCPServer
from .tools import ReadContext
from .tool_contracts import build_tool_functions
# TODO: import register_seller_balance from .seller_balance_tool


def main():
    settings = json.loads(os.getenv('CONTEXT_COMPARISON_JSON', '{}'))
    ctx = ReadContext(suppress_catalog=bool(settings.get('suppress_catalog')),
                      suppress_documents=bool(settings.get('suppress_documents')))
    server = MCPServer('Marketplace read tools with seller-balance lab extension')
    for fn in build_tool_functions(ctx):
        server.tool(structured_output=False)(fn)

    # TODO: register the seller-balance tool here with this server and ctx.

    @server.resource('marketplace://run/state')
    def run_state() -> str:
        return json.dumps(dict(snapshot=ctx.snapshot, doc_hash=ctx.doc_hash,
                              evidence=ctx.evidence, calls=ctx.calls), default=str)

    try:
        server.run(transport='stdio')
    finally:
        ctx.close()


if __name__ == '__main__':
    main()
