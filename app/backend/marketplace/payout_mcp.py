"""Dedicated OAuth MCP resource for the simulated payout service."""
import os
from typing import Annotated
from urllib.parse import urlsplit
from mcp.server import MCPServer
from mcp.server.auth.middleware.auth_context import get_access_token
from mcp.server.auth.settings import AuthSettings
from mcp.server.mcpserver.exceptions import ToolError
from mcp.server.transport_security import TransportSecuritySettings
from mcp.shared.exceptions import MCPError
from mcp_types import INVALID_PARAMS, ToolAnnotations
from pydantic import Field
from starlette.responses import JSONResponse
from .user_mcp_auth import KeycloakTokenVerifier, VerifiedPrincipal
from .payout_service import PayoutAccess


def create_app(*, verifier=None, payout_access=None):
    resource = os.environ['PAYOUT_MCP_RESOURCE_URL']
    issuer = os.environ['PAYOUT_MCP_ISSUER_URL']
    for value in (resource, issuer):
        url = urlsplit(value)
        if url.query or url.fragment or url.username or not (url.scheme == 'https' or
                (url.scheme == 'http' and url.hostname in ('localhost', '127.0.0.1'))):
            raise ValueError('Invalid OAuth URL')
    if payout_access is None:
        if not os.environ.get('DATABASE_URL', '').endswith('/market_test'):
            raise ValueError('Payout service requires isolated Test database market_test')
        payout_access = PayoutAccess(os.environ['PAYOUT_SERVICE_POLICY'])
    verifier = verifier or KeycloakTokenVerifier(issuer, resource, os.environ['PAYOUT_MCP_JWKS_URL'],
                                               ['marketplace-payout-worker'])

    async def strict(context, call_next):
        if context.method == 'tools/call':
            params = context.params or {}
            for tool in await server.list_tools():
                if tool.name == params.get('name'):
                    args = params.get('arguments') or {}
                    if isinstance(args, dict) and set(args) - set(tool.input_schema.get('properties', {})):
                        raise MCPError(INVALID_PARAMS, 'Unsupported tool arguments')
        return await call_next(context)

    server = MCPServer('Marketplace simulated payouts', token_verifier=verifier, middleware=[strict],
        auth=AuthSettings(issuer_url=issuer, resource_server_url=resource,
                          required_scopes=['payouts:read'], validate_token_resource=True))

    def principal():
        token = get_access_token()
        if token is None or not token.subject:
            raise ToolError('Verified service identity required')
        return VerifiedPrincipal((token.claims or {}).get('iss', ''), token.subject,
                                 token.client_id, frozenset(token.scopes))

    @server.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False))
    def list_eligible_payouts(limit: Annotated[int, Field(ge=1, le=50)] = 10,
            run_id: Annotated[str | None, Field(min_length=8, max_length=100)] = None) -> dict:
        """List advisory candidates within service seller and amount policy. Amounts are paise."""
        return payout_access.eligible(principal(), limit, run_id)

    @server.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=True, idempotentHint=True, openWorldHint=False))
    def request_payout_release(payout_id: Annotated[str, Field(min_length=1, max_length=100)],
            idempotency_key: Annotated[str, Field(min_length=8, max_length=120)],
            run_id: Annotated[str, Field(min_length=8, max_length=100)]) -> dict:
        """Release a simulated payout; recheck all rules atomically. Requires payouts:release."""
        return payout_access.release(principal(), payout_id, idempotency_key, run_id)

    @server.custom_route('/health', methods=['GET'])
    async def health(request):
        return JSONResponse({'status': 'ok', 'simulation': True, 'workspace': 'Test'})

    return server.streamable_http_app(streamable_http_path=urlsplit(resource).path, json_response=True,
        stateless_http=True, max_request_body_size=16384,
        transport_security=TransportSecuritySettings(allowed_hosts=[urlsplit(resource).netloc,
            'localhost:*', '127.0.0.1:*', 'payouts:*', 'testserver'], allowed_origins=[]))


def main():
    import uvicorn
    uvicorn.run(create_app(), host='0.0.0.0', port=8003, access_log=False)


if __name__ == '__main__':
    main()
