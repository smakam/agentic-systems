#!/usr/bin/env python3
"""Add optional Keycloak login to the local main/Test marketplace frontends.

Run after user-mcp/setup.py and starting Keycloak. Credentials remain in ignored
private files. This registers a separate web client; MCP permissions are unchanged.
"""
import json
import os
from pathlib import Path
import secrets
import uuid

import httpx

STATE = Path(__file__).resolve().parents[1] / '.user-mcp'


def save(name, data):
    path = STATE / name
    path.write_text(json.dumps(data, indent=2) + '\n')
    path.chmod(0o600)


def main():
    settings = json.loads((STATE / 'settings.json').read_text())
    for name in ('ui_client_secret', 'ui_state_secret'):
        settings.setdefault(name, secrets.token_urlsafe(48))
    save('settings.json', settings)
    base = settings['base_url']
    issuer = base + '/identity/realms/marketplace'
    links = json.loads((STATE / 'identity-links.json').read_text())
    origins = [f'http://{host}:{port}' for port in (5178, 5179) for host in ('127.0.0.1', 'localhost')]
    client_config = {
        'clientId': 'marketplace-web', 'enabled': True, 'protocol': 'openid-connect',
        'publicClient': False, 'secret': settings['ui_client_secret'],
        'standardFlowEnabled': True, 'directAccessGrantsEnabled': False,
        'implicitFlowEnabled': False, 'serviceAccountsEnabled': False,
        'consentRequired': False, 'fullScopeAllowed': False,
        'defaultClientScopes': ['basic'], 'optionalClientScopes': [],
        'redirectUris': [origin + '/api/auth/keycloak/callback' for origin in origins],
        'webOrigins': [], 'attributes': {'pkce.code.challenge.method': 'S256'},
    }
    with httpx.Client(base_url=os.getenv('KEYCLOAK_ADMIN_BASE_URL', 'http://127.0.0.1:58501'), timeout=15) as client:
        result = client.post('/identity/realms/master/protocol/openid-connect/token', data={
            'client_id': 'admin-cli', 'grant_type': 'password',
            'username': 'experiment-admin', 'password': settings['admin_password'],
        })
        result.raise_for_status()
        client.headers['Authorization'] = 'Bearer ' + result.json()['access_token']
        admin = '/identity/admin/realms/marketplace'
        result = client.get(admin + '/clients', params={'clientId': 'marketplace-web'})
        result.raise_for_status()
        existing = result.json()
        result = (client.put(admin + '/clients/' + existing[0]['id'], json=client_config)
                  if existing else client.post(admin + '/clients', json=client_config))
        result.raise_for_status()
        for account in ('support', 'operator'):
            result = client.get(admin + '/users', params={'username': account, 'exact': 'true'})
            result.raise_for_status()
            users = result.json()
            if users:
                subject = users[0]['id']
            else:
                subject = str(uuid.uuid5(uuid.NAMESPACE_URL, issuer + '/' + account))
                result = client.post(admin + '/users', json={
                    'id': subject, 'username': account, 'enabled': True,
                    'firstName': account.capitalize(), 'lastName': 'Demo',
                    'email': account + '@example.test', 'emailVerified': True,
                    'credentials': [{'type': 'password', 'value': settings['user_password'], 'temporary': False}],
                })
                result.raise_for_status()
                # Admin create may assign a different ID; link the stored subject.
                result = client.get(admin + '/users', params={'username': account, 'exact': 'true'})
                result.raise_for_status()
                subject = result.json()[0]['id']
            links['subjects'][subject] = account
    save('ui-identity-links.json', links)
    internal = 'http://marketplace-user-mcp-proxy-1:8080/identity/realms/marketplace/protocol/openid-connect'
    for port in (5178, 5179):
        save(f'ui-login-{port}.json', {
            'issuer': issuer, 'authorization_url': issuer + '/protocol/openid-connect/auth',
            'token_url': internal + '/token', 'jwks_url': internal + '/certs',
            'client_id': 'marketplace-web', 'client_secret': settings['ui_client_secret'],
            'state_secret': settings['ui_state_secret'],
            'identity_links': '/config/ui-identity-links.json',
            'origins': [origin for origin in origins if origin.endswith(':' + str(port))],
        })
    print('Registered marketplace-web and linked six demo roles for both local app ports.')


if __name__ == '__main__':
    main()
