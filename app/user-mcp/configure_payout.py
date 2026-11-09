#!/usr/bin/env python3
"""Register narrow Keycloak client-credentials service; store secrets in ignored files."""
import json
import os
from pathlib import Path
import secrets
import httpx
STATE = Path(__file__).resolve().parents[1] / '.user-mcp'


def save(name, value):
    target = STATE / name
    target.write_text(json.dumps(value, indent=2) + '\n')
    target.chmod(0o600)


def main():
    settings = json.loads((STATE / 'settings.json').read_text())
    credential_file = STATE / 'payout-credentials.json'
    credentials = json.loads(credential_file.read_text()) if credential_file.exists() else {
        'client_id': 'marketplace-payout-worker', 'client_secret': secrets.token_urlsafe(48)}
    issuer = settings['base_url'] + '/identity/realms/marketplace'
    resource = 'http://127.0.0.1:58503/payouts/mcp'
    with httpx.Client(base_url=os.getenv('KEYCLOAK_ADMIN_BASE_URL', 'http://127.0.0.1:58501'), timeout=15) as client:
        response = client.post('/identity/realms/master/protocol/openid-connect/token', data={
            'client_id': 'admin-cli', 'grant_type': 'password', 'username': 'experiment-admin',
            'password': settings['admin_password']})
        response.raise_for_status()
        client.headers['Authorization'] = 'Bearer ' + response.json()['access_token']
        admin = '/identity/admin/realms/marketplace'
        response = client.get(admin + '/client-scopes'); response.raise_for_status()
        scopes = {scope['name']: scope['id'] for scope in response.json()}
        for name in ('payouts:read', 'payouts:release'):
            definition = {'name': name, 'protocol': 'openid-connect',
                'attributes': {'include.in.token.scope': 'true', 'display.on.consent.screen': 'false'},
                'protocolMappers': [{'name': 'payout-audience', 'protocol': 'openid-connect',
                    'protocolMapper': 'oidc-audience-mapper', 'config': {
                        'included.custom.audience': resource, 'access.token.claim': 'true', 'id.token.claim': 'false'}},
                    {'name': 'subject', 'protocol': 'openid-connect', 'protocolMapper': 'oidc-sub-mapper',
                     'config': {'access.token.claim': 'true', 'introspection.token.claim': 'true'}}]}
            if name in scopes:
                response = client.put(admin + '/client-scopes/' + scopes[name], json=definition)
            else:
                response = client.post(admin + '/client-scopes', json=definition)
            response.raise_for_status()
        definition = {'clientId': credentials['client_id'], 'secret': credentials['client_secret'],
            'enabled': True, 'protocol': 'openid-connect', 'publicClient': False,
            'serviceAccountsEnabled': True, 'standardFlowEnabled': False,
            'directAccessGrantsEnabled': False, 'implicitFlowEnabled': False,
            'fullScopeAllowed': False, 'defaultClientScopes': ['payouts:read'],
            'optionalClientScopes': ['payouts:release'], 'redirectUris': [], 'webOrigins': []}
        response = client.get(admin + '/clients', params={'clientId': credentials['client_id']}); response.raise_for_status()
        found = response.json()
        response = (client.put(admin + '/clients/' + found[0]['id'], json=definition)
                    if found else client.post(admin + '/clients', json=definition))
        response.raise_for_status()
        response = client.get(admin + '/clients', params={'clientId': credentials['client_id']}); response.raise_for_status()
        client_uuid = response.json()[0]['id']
        response = client.get(admin + '/clients/' + client_uuid + '/service-account-user'); response.raise_for_status()
        subject = response.json()['id']
    save('payout-credentials.json', credentials)
    policy_file = STATE / 'payout-policy.json'
    policy = json.loads(policy_file.read_text()) if policy_file.exists() else {
        'simulation_only': True, 'seller_scope': 'all', 'max_payout_paise': 1000000,
        'max_run_paise': 2000000, 'max_run_count': 10}
    # Payout automation applies to every marketplace seller; eligibility and budgets still gate each release.
    policy.pop('seller_ids', None)
    policy.update(seller_scope='all', issuer=issuer, client_id=credentials['client_id'], subject=subject)
    save('payout-policy.json', policy)
    save('payout-worker.json', {**credentials, 'simulation_only': True, 'workspace': 'Test',
        'token_url': 'http://identity:8080/identity/realms/marketplace/protocol/openid-connect/token',
        'mcp_url': 'http://payouts:8003/payouts/mcp', 'max_run_paise': policy['max_run_paise'],
        'max_run_count': policy['max_run_count']})
    (STATE / 'payout-runs').mkdir(mode=0o700, exist_ok=True)
    print('Registered payout service identity and saved private Test-only policy. Scheduler remains off.')


if __name__ == '__main__':
    main()
