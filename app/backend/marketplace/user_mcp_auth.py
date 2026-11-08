"""Verify Keycloak access tokens for the user-scoped marketplace MCP resource."""

import asyncio
from dataclasses import dataclass
import logging

import jwt
from mcp.server.auth.provider import AccessToken

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class VerifiedPrincipal:
    """Internal identity handoff, constructed only after token verification."""

    issuer: str
    subject: str
    client_id: str
    scopes: frozenset[str]


class KeycloakTokenVerifier:
    def __init__(self, issuer, resource, jwks_url, allowed_clients, *, jwks_client=None):
        self.issuer = issuer
        self.resource = resource
        self.allowed_clients = frozenset(allowed_clients)
        self.jwks = jwks_client or jwt.PyJWKClient(jwks_url, timeout=5, lifespan=300)

    async def verify_token(self, token):
        try:
            key = await asyncio.to_thread(self.jwks.get_signing_key_from_jwt, token)
            claims = jwt.decode(
                token,
                key.key,
                algorithms=['RS256'],
                audience=self.resource,
                issuer=self.issuer,
                options={'require': ['iss', 'sub', 'aud', 'exp', 'iat', 'azp']},
            )
            if claims.get('typ') != 'Bearer' or claims['azp'] not in self.allowed_clients:
                return None
            if not isinstance(claims['sub'], str) or not claims['sub']:
                return None
            scope = claims.get('scope', '')
            if not isinstance(scope, str):
                return None
            return AccessToken(
                token=token,
                client_id=claims['azp'],
                subject=claims['sub'],
                scopes=scope.split(),
                expires_at=claims['exp'],
                resource=self.resource,
                claims={'iss': self.issuer},
            )
        except (jwt.PyJWTError, ValueError, TypeError, KeyError):
            # Credentials, claims and JWTs must never be written to logs.
            logger.info('Rejected marketplace MCP access token')
            return None
