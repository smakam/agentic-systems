#!/usr/bin/env python3
"""Exercise real browser-form OAuth code/PKCE and MCP for all four demo accounts.

Credentials and tokens remain in memory. The saved receipt contains only account
names, permitted synthetic order/item identifiers, and verification outcomes.
"""

import base64
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import secrets
from urllib.parse import parse_qs, urljoin, urlsplit

import httpx

STATE = Path(__file__).resolve().parents[1] / '.user-mcp'


class Forms(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.forms = []
        self.current = None
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self.current = {**attrs, 'inputs': []}
            self.forms.append(self.current)
        if tag in ('input', 'button') and self.current is not None:
            self.current['inputs'].append(attrs)

    def handle_endtag(self, tag):
        if tag == 'form':
            self.current = None


def login(client, metadata, settings, username):
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b'=').decode()
    state = secrets.token_urlsafe(24)
    callback = 'http://127.0.0.1:58502/callback'
    response = client.get(metadata['authorization_endpoint'], params={
        'client_id': 'marketplace-local-test',
        'redirect_uri': callback,
        'response_type': 'code',
        'scope': 'openid orders:read',
        'resource': settings['base_url'] + '/orders/mcp',
        'state': state,
        'code_challenge': challenge,
        'code_challenge_method': 'S256',
        'prompt': 'login',
    })
    for _ in range(10):
        if response.is_redirect:
            location = urljoin(str(response.url), response.headers['location'])
            if location.startswith(callback + '?'):
                query = parse_qs(urlsplit(location).query)
                assert query.get('state') == [state], 'OAuth callback state mismatch'
                assert 'code' in query and 'error' not in query, 'Authorization failed'
                code = query['code'][0]
                token_request = {
                    'grant_type': 'authorization_code',
                    'client_id': 'marketplace-local-test',
                    'redirect_uri': callback,
                    'code': code,
                    'code_verifier': verifier,
                    'resource': settings['base_url'] + '/orders/mcp',
                }
                token_response = client.post(metadata['token_endpoint'], data=token_request)
                assert token_response.status_code == 200, 'Authorization-code exchange failed'
                tokens = token_response.json()
                return tokens, token_request
            response = client.get(location)
            continue
        assert response.status_code == 200, f'Login page failed with HTTP {response.status_code}'
        available_forms = Forms(response.text).forms
        forms = [form for form in available_forms if any(
            field.get('name') in ('password', 'accept') for field in form['inputs']
        )]
        assert forms, 'Expected Keycloak credential or consent form'
        form = forms[0]
        fields = {
            field['name']: field.get('value', '')
            for field in form['inputs']
            if field.get('name') and field.get('type') == 'hidden'
        }
        if any(field.get('name') == 'password' for field in form['inputs']):
            fields.update(username=username, password=settings['user_password'])
        else:
            fields['accept'] = 'Yes'
        response = client.post(urljoin(str(response.url), form['action']), data=fields)
    raise AssertionError('OAuth flow exceeded expected redirects')


def rpc(client, base, token, method, params=None):
    response = client.post(base + '/orders/mcp', headers={
        'Authorization': 'Bearer ' + token,
        'Accept': 'application/json, text/event-stream',
    }, json={'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params or {}})
    assert response.status_code == 200, f'MCP request failed with HTTP {response.status_code}'
    result = response.json()
    assert 'error' not in result, 'MCP protocol error'
    return result['result']


def tool(client, base, token, name, **arguments):
    result = rpc(client, base, token, 'tools/call', {'name': name, 'arguments': arguments})
    assert not result.get('isError'), 'MCP tool rejected the request'
    return result.get('structuredContent') or json.loads(result['content'][0]['text'])


def main():
    settings = json.loads((STATE / 'settings.json').read_text())
    base = settings['base_url']
    records = {}
    for account in ('buyer', 'buyer2', 'seller', 'seller2'):
        with httpx.Client(timeout=30, follow_redirects=False) as client:
            challenge = client.post(base + '/orders/mcp', json={})
            assert challenge.status_code == 401
            assert 'resource_metadata=' in challenge.headers['www-authenticate']
            protected = client.get(base + '/.well-known/oauth-protected-resource/orders/mcp').json()
            assert protected['resource'] == base + '/orders/mcp'
            issuer = protected['authorization_servers'][0]
            metadata = client.get(issuer + '/.well-known/openid-configuration').json()
            assert metadata['issuer'] == issuer
            assert 'S256' in metadata['code_challenge_methods_supported']
            tokens, token_request = login(client, metadata, settings, account)
            token = tokens['access_token']
            rpc(client, base, token, 'initialize', {
                'protocolVersion': '2025-11-25', 'capabilities': {},
                'clientInfo': {'name': 'marketplace-oauth-verification', 'version': '1'},
            })
            profile = tool(client, base, token, 'get_my_profile')
            assert profile['name'] == account
            result = tool(client, base, token, 'list_my_orders', limit=50)
            rows = result['orders']
            records[account] = {
                'profile_verified': True,
                'orders': [order['order_id'] for order in rows],
                'items': [item['item_id'] for order in rows for item in order['items']],
                'has_more_orders': result['next_offset'] is not None,
                'pkce_code_flow': 'passed',
                'authorization_code_replay': 'rejected',
            }
            refreshed = client.post(metadata['token_endpoint'], data={
                'grant_type': 'refresh_token',
                'client_id': 'marketplace-local-test',
                'refresh_token': tokens['refresh_token'],
                'resource': base + '/orders/mcp',
            })
            assert refreshed.status_code == 200, 'Token refresh failed'
            identity_after_refresh = tool(client, base, refreshed.json()['access_token'], 'get_my_profile')
            assert identity_after_refresh == profile
            records[account]['refresh_identity'] = 'passed'
            if account == 'buyer':
                hidden = tool(client, base, token, 'get_my_order_status', order_id='order-2')
                assert hidden['status'] == 'unavailable'
            if account == 'buyer2':
                hidden = tool(client, base, token, 'get_my_order_status', order_id='order-1')
                assert hidden['status'] == 'unavailable'
            # Keycloak can revoke the login session after code replay. Check this
            # last, after refresh and tool calls using that session are complete.
            replay = client.post(metadata['token_endpoint'], data=token_request)
            assert replay.status_code == 400, 'Authorization code was accepted twice'
            print(account + ': sign-in, profile, scoped orders, code replay and refresh passed')
    assert set(records['buyer']['orders']).isdisjoint(records['buyer2']['orders'])
    assert set(records['seller']['items']).isdisjoint(records['seller2']['items'])
    receipt = STATE / 'oauth-verification.json'
    receipt.write_text(json.dumps({'transport': 'public HTTPS', 'accounts': records}, indent=2) + '\n')
    receipt.chmod(0o600)
    print('Buyer order and seller-line isolation passed. Saved sanitized verification receipt.')


if __name__ == '__main__':
    main()
