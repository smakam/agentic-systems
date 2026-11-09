#!/usr/bin/env python3
"""Provision private, local Keycloak demo configuration for self-service MCP."""

import argparse
import json
import os
from pathlib import Path
import secrets
from urllib.parse import urlsplit
import uuid

APP = Path(__file__).resolve().parents[1]
STATE = APP / '.user-mcp'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--chatgpt-callback', required=True)
    args = parser.parse_args()
    base = args.base_url.rstrip('/')
    parsed = urlsplit(base)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.path or parsed.query or parsed.fragment:
        parser.error('--base-url must be an HTTPS origin')
    callback = urlsplit(args.chatgpt_callback)
    if callback.scheme != 'https' or callback.hostname != 'chatgpt.com' or callback.query or callback.fragment:
        parser.error('Use the exact HTTPS callback shown by the ChatGPT connection')
    STATE.mkdir(mode=0o700, exist_ok=True)
    os.chmod(STATE, 0o700)
    settings_path = STATE / 'settings.json'
    if settings_path.exists():
        settings = json.loads(settings_path.read_text())
        if settings['base_url'] != base or settings['chatgpt_callback'] != args.chatgpt_callback:
            parser.error('Existing realm configuration differs; update Keycloak explicitly rather than silently replacing it')
    else:
        settings = {
            'base_url': base,
            'chatgpt_callback': args.chatgpt_callback,
            'admin_password': secrets.token_urlsafe(24),
            'chatgpt_secret': secrets.token_urlsafe(32),
            'user_password': secrets.token_urlsafe(18),
        }
        settings_path.write_text(json.dumps(settings, indent=2) + '\n')
        settings_path.chmod(0o600)
    resource = base + '/orders/mcp'
    issuer = base + '/identity/realms/marketplace'
    links_file = STATE / 'identity-links.json'
    if links_file.exists():
        subjects = json.loads(links_file.read_text())['subjects']
    else:
        subjects = {
            str(uuid.uuid5(uuid.NAMESPACE_URL, issuer + '/' + account)): account
            for account in ('buyer', 'buyer2', 'seller', 'seller2')
        }
    if set(subjects.values()) != {'buyer', 'buyer2', 'seller', 'seller2'}:
        parser.error('Expected explicit links for the four demo accounts')
    clients = []
    for client_id, public, redirects in (
        ('marketplace-chatgpt', False, [args.chatgpt_callback]),
        ('marketplace-local-test', True, ['http://127.0.0.1:58502/callback']),
    ):
        client = {
            'clientId': client_id,
            'enabled': True,
            'protocol': 'openid-connect',
            'publicClient': public,
            'standardFlowEnabled': True,
            'directAccessGrantsEnabled': False,
            'implicitFlowEnabled': False,
            'serviceAccountsEnabled': False,
            'consentRequired': True,
            'redirectUris': redirects,
            'webOrigins': [],
            'fullScopeAllowed': False,
            'defaultClientScopes': ['orders:read'],
            'optionalClientScopes': ['offline_access'] if client_id == 'marketplace-chatgpt' else [],
            'attributes': {'pkce.code.challenge.method': 'S256'},
        }
        if not public:
            client['secret'] = settings['chatgpt_secret']
        clients.append(client)
    realm = {
        'realm': 'marketplace',
        'displayName': 'Marketplace identity experiment',
        'enabled': True,
        'sslRequired': 'external',
        'registrationAllowed': False,
        'resetPasswordAllowed': False,
        'bruteForceProtected': True,
        'failureFactor': 5,
        'accessTokenLifespan': 300,
        'ssoSessionIdleTimeout': 1800,
        'ssoSessionMaxLifespan': 3600,
        'clients': clients,
        'clientScopes': [{
            'name': 'orders:read',
            'protocol': 'openid-connect',
            'attributes': {
                'include.in.token.scope': 'true',
                'display.on.consent.screen': 'true',
                'consent.screen.text': 'Read the orders and item statuses permitted for your marketplace account',
            },
            'protocolMappers': [{
                'name': 'marketplace-mcp-audience',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-audience-mapper',
                'config': {'included.custom.audience': resource, 'access.token.claim': 'true', 'id.token.claim': 'false'},
            }, {
                'name': 'subject',
                'protocol': 'openid-connect',
                'protocolMapper': 'oidc-sub-mapper',
                'config': {'access.token.claim': 'true', 'introspection.token.claim': 'true'},
            }],
        }],
        'users': [{
            'id': subject,
            'username': account,
            'enabled': True,
            'firstName': account.capitalize(),
            'lastName': 'Demo',
            'email': account + '@example.test',
            'emailVerified': True,
            # ChatGPT requests offline refresh for its existing read-only order connection.
            'realmRoles': ['offline_access'],
            'credentials': [{'type': 'password', 'value': settings['user_password'], 'temporary': False}],
        } for subject, account in subjects.items()],
    }
    for name, value in (
        ('marketplace-realm.json', realm),
        ('identity-links.json', {'issuer': issuer, 'subjects': subjects}),
    ):
        target = STATE / name
        target.write_text(json.dumps(value, indent=2) + '\n')
        target.chmod(0o600)
    env = APP / '.env.user-mcp'
    env.write_text(
        f'USER_MCP_BASE_URL={base}\n'
        f'KEYCLOAK_ADMIN_PASSWORD={settings["admin_password"]}\n'
    )
    env.chmod(0o600)
    proxy = '''server {
    listen 8080;
    server_name _;
    client_max_body_size 64k;
    access_log off;
    location /identity/realms/marketplace/ {
        # Reconnect responses can include a large Location header and SSO cookies.
        proxy_buffer_size 32k;
        proxy_buffers 8 32k;
        proxy_busy_buffers_size 64k;
        proxy_pass http://identity:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port 443;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
    location /identity/resources/ {
        proxy_pass http://identity:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-Proto https;
        proxy_set_header X-Forwarded-Host $host;
        proxy_set_header X-Forwarded-Port 443;
        proxy_set_header X-Forwarded-For $remote_addr;
    }
    location /identity/ { return 404; }
    location /mcp {
        proxy_pass http://marketplace-lab-remote-mcp-1:8001;
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_read_timeout 90s;
    }
    location / {
        proxy_pass http://orders:8002;
        proxy_set_header Host $host;
        proxy_buffering off;
        proxy_read_timeout 90s;
    }
}
'''
    (STATE / 'proxy.conf').write_text(proxy)
    access = STATE / 'Access.md'
    access.write_text(
        '# Private local MCP experiment access\n\n'
        f'MCP endpoint: {resource}\n\n'
        f'Keycloak issuer: {issuer}\n\n'
        'ChatGPT OAuth client: `marketplace-chatgpt`\n\n'
        f'ChatGPT client secret: `{settings["chatgpt_secret"]}`\n\n'
        f'Configured callback: {args.chatgpt_callback}\n\n'
        'Demo user names: `buyer`, `buyer2`, `seller`, `seller2`\n\n'
        f'Demo user password: `{settings["user_password"]}`\n\n'
        'Use the user password in the Keycloak sign-in page. Keep this file private.\n'
    )
    access.chmod(0o600)
    print('Generated private realm, identity links, proxy configuration and access notes.')


if __name__ == '__main__':
    main()
