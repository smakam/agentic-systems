"""OAuth-protected buyer/seller tools, separate from broad support investigation."""

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
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from .user_mcp_auth import KeycloakTokenVerifier, VerifiedPrincipal
from .user_orders import OrderAccess

ORDER_SCOPE = 'orders:read'


class Profile(BaseModel):
    id: str
    name: str
    nickname: str


def create_app(*, verifier=None, order_access=None):
    resource = os.environ['USER_MCP_RESOURCE_URL'].rstrip('/')
    issuer = os.environ['USER_MCP_ISSUER_URL'].rstrip('/')
    for url in (resource, issuer):
        parsed = urlsplit(url)
        if parsed.query or parsed.fragment or parsed.username:
            raise ValueError('OAuth URLs must not contain credentials, queries or fragments')
        if parsed.scheme != 'https' and not (
            parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1')
        ):
            raise ValueError('OAuth URLs require HTTPS except for local loopback tests')
    if verifier is None:
        verifier = KeycloakTokenVerifier(
            issuer,
            resource,
            os.getenv('USER_MCP_JWKS_URL', issuer + '/protocol/openid-connect/certs'),
            os.getenv('USER_MCP_ALLOWED_CLIENTS', 'marketplace-chatgpt,marketplace-local-test').split(','),
        )
    order_access = order_access or OrderAccess(issuer, os.environ['USER_MCP_IDENTITY_LINKS'])

    async def strict_tool_arguments(context, call_next):
        if context.method == 'tools/call':
            params = context.params or {}
            for tool in await server.list_tools():
                if tool.name == params.get('name'):
                    supplied = params.get('arguments') or {}
                    if isinstance(supplied, dict) and set(supplied) - set(tool.input_schema.get('properties', {})):
                        raise MCPError(INVALID_PARAMS, 'Unsupported tool arguments')
        return await call_next(context)

    server = MCPServer(
        'Marketplace self-service orders',
        instructions='Read orders for the authenticated buyer or seller. Identity comes from the access token. '
                     'An unavailable order may not exist or may be outside this account. '
                     'Order status and per-item shipment status are separate facts.',
        token_verifier=verifier,
        middleware=[strict_tool_arguments],
        auth=AuthSettings(
            issuer_url=issuer,
            resource_server_url=resource,
            required_scopes=[ORDER_SCOPE],
            validate_token_resource=True,
        ),
    )
    annotations = ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False)
    security = {'securitySchemes': [{'type': 'oauth2', 'scopes': [ORDER_SCOPE]}]}

    def principal():
        token = get_access_token()
        if token is None or not token.subject:
            raise ToolError('Authenticated user required')
        return VerifiedPrincipal(
            issuer=(token.claims or {}).get('iss', ''),
            subject=token.subject,
            client_id=token.client_id,
            scopes=frozenset(token.scopes),
        )

    @server.tool(annotations=annotations, meta={**security, 'openai/profile': True})
    def get_my_profile() -> Profile:
        """Return the identity represented by this connection, including its buyer/seller display role."""
        return Profile(**order_access.profile(principal()))

    @server.tool(annotations=annotations, meta=security)
    def list_my_orders(
        limit: Annotated[int, Field(ge=1, le=50)] = 20,
        offset: Annotated[int, Field(ge=0, le=10000)] = 0,
    ) -> dict:
        """List the authenticated account's orders. Sellers receive only their own order lines."""
        return order_access.orders(principal(), limit=limit, offset=offset)

    @server.tool(annotations=annotations, meta=security)
    def get_my_order_status(order_id: Annotated[str, Field(min_length=1, max_length=100)]) -> dict:
        """Get an accessible order's status and own item shipments; inaccessible orders are unavailable."""
        result = order_access.orders(principal(), order_id=order_id, limit=1)
        if not result['orders']:
            return {'status': 'unavailable', 'message': 'Order unavailable for this account'}
        return {'status': 'ok', 'order': result['orders'][0]}

    @server.custom_route('/health', methods=['GET'])
    async def health(request):
        return JSONResponse({'status': 'ok', 'service': 'marketplace-self-service-mcp'})

    host = urlsplit(resource).netloc
    return server.streamable_http_app(
        streamable_http_path=urlsplit(resource).path or '/mcp',
        json_response=True,
        stateless_http=True,
        max_request_body_size=16384,
        transport_security=TransportSecuritySettings(
            allowed_hosts=[host, 'localhost:*', '127.0.0.1:*', 'testserver'],
            allowed_origins=[],
        ),
    )


def main():
    import uvicorn
    uvicorn.run(create_app(), host='0.0.0.0', port=int(os.getenv('USER_MCP_PORT', '8002')), access_log=False)


if __name__ == '__main__':
    main()
