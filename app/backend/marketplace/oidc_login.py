"""Optional Keycloak browser login; both login methods create normal app sessions.

The OAuth client here is the web app, independent of the ChatGPT MCP client.
Only a verified issuer/subject mapping selects the existing marketplace account.
"""

import base64
from functools import lru_cache
import hashlib
import json
import os
from pathlib import Path
import secrets
import time
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
import httpx
import jwt

from .db import User

COOKIE = 'market_oidc_state'
PREFIX = '/api/auth/keycloak'


def configuration():
    path = os.getenv('MARKETPLACE_OIDC_CONFIG')
    return json.loads(Path(path).read_text()) if path else None


@lru_cache(maxsize=4)
def signing_keys(url):
    return jwt.PyJWKClient(url, timeout=5, lifespan=300)


def validate_identity(tokens, config, nonce):
    token = tokens['id_token']
    key = signing_keys(config['jwks_url']).get_signing_key_from_jwt(token)
    claims = jwt.decode(token, key.key, algorithms=['RS256'],
                        audience=config['client_id'], issuer=config['issuer'],
                        options={'require': ['iss', 'sub', 'aud', 'exp', 'iat', 'nonce']})
    if not isinstance(claims['sub'], str) or not claims['sub']:
        raise ValueError('Missing subject')
    if not isinstance(claims['nonce'], str) or not secrets.compare_digest(claims['nonce'], nonce):
        raise ValueError('Invalid nonce')
    audiences = claims['aud'] if isinstance(claims['aud'], list) else [claims['aud']]
    if (len(audiences) > 1 or 'azp' in claims) and claims.get('azp') != config['client_id']:
        raise ValueError('Invalid authorized party')
    if 'at_hash' in claims:
        expected = base64.urlsafe_b64encode(hashlib.sha256(tokens['access_token'].encode()).digest()[:16]).rstrip(b'=').decode()
        if not secrets.compare_digest(claims['at_hash'], expected):
            raise ValueError('Invalid access token binding')
    return claims


def create_router(db_session, create_session):
    router = APIRouter()

    @router.get('/api/auth/providers')
    def providers():
        return {'password': True, 'keycloak': configuration() is not None}

    @router.get(PREFIX + '/login')
    def start(request: Request, origin: str):
        config = configuration()
        if not config:
            raise HTTPException(404, 'Keycloak login is not configured')
        # The browser origin is explicit because the local nginx strips the port.
        # Never construct callback URLs from untrusted Host or arbitrary return URLs.
        if origin not in config['origins']:
            raise HTTPException(400, 'Unrecognized application origin')
        state, nonce, verifier = (secrets.token_urlsafe(32) for _ in range(3))
        callback = origin + PREFIX + '/callback'
        transaction = jwt.encode({'state': state, 'nonce': nonce, 'verifier': verifier,
                                  'origin': origin, 'exp': int(time.time()) + 300,
                                  'aud': config['client_id'], 'iss': 'marketplace-login'},
                                 config['state_secret'], algorithm='HS256')
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
        url = config['authorization_url'] + '?' + urlencode({
            'client_id': config['client_id'], 'redirect_uri': callback,
            'response_type': 'code', 'scope': 'openid', 'state': state, 'nonce': nonce,
            'code_challenge': challenge, 'code_challenge_method': 'S256', 'prompt': 'login',
        })
        response = RedirectResponse(url, status_code=303)
        response.set_cookie(COOKIE, transaction, max_age=300, httponly=True,
                            secure=origin.startswith('https://'), samesite='lax', path=PREFIX)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Referrer-Policy'] = 'no-referrer'
        return response

    @router.get(PREFIX + '/callback')
    def callback(request: Request, db=Depends(db_session)):
        config = configuration()
        if not config:
            raise HTTPException(404, 'Keycloak login is not configured')
        # Reject callbacks without browser-bound state before contacting Keycloak.
        try:
            transaction = jwt.decode(request.cookies.get(COOKIE, ''), config['state_secret'],
                                     algorithms=['HS256'], audience=config['client_id'],
                                     issuer='marketplace-login', options={'require': ['exp', 'state', 'nonce', 'verifier', 'origin']})
            if transaction['origin'] not in config['origins']:
                raise ValueError('Invalid origin')
            if not secrets.compare_digest(request.query_params.get('state', ''), transaction['state']):
                raise ValueError('Invalid state')
        except (jwt.PyJWTError, ValueError, TypeError, KeyError):
            raise HTTPException(400, 'Invalid or expired sign-in. Start again from the login page.')
        origin = transaction['origin']
        response = RedirectResponse(origin + '/', status_code=303)
        response.delete_cookie(COOKIE, path=PREFIX)
        response.headers['Cache-Control'] = 'no-store'
        response.headers['Referrer-Policy'] = 'no-referrer'
        try:
            if request.query_params.get('error') or not request.query_params.get('code'):
                raise ValueError('Authorization was not completed')
            # Tokens stay on the backend. They are never placed in the browser URL
            # or used as the application's session cookie.
            with httpx.Client(timeout=10, follow_redirects=False) as client:
                result = client.post(config['token_url'], data={
                    'grant_type': 'authorization_code', 'client_id': config['client_id'],
                    'client_secret': config['client_secret'], 'code': request.query_params['code'],
                    'redirect_uri': origin + PREFIX + '/callback', 'code_verifier': transaction['verifier'],
                })
                result.raise_for_status()
                claims = validate_identity(result.json(), config, transaction['nonce'])
            links = json.loads(Path(config['identity_links']).read_text())
            account_id = links.get('subjects', {}).get(claims['sub']) if links.get('issuer') == config['issuer'] else None
            user = db.get(User, account_id) if account_id else None
            if not user:
                response.headers['location'] = origin + '/?login_error=account_unlinked'
            else:
                create_session(db, user, response)
        except (httpx.HTTPError, jwt.PyJWTError, ValueError, TypeError, KeyError, OSError):
            # Keep provider responses, credentials, tokens and codes out of logs.
            response.headers['location'] = origin + '/?login_error=keycloak_failed'
        return response

    return router
