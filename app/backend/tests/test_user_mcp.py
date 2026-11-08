"""Exercise signed-token HTTP MCP calls against isolated PostgreSQL fixtures."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import json
import time
from types import SimpleNamespace

from cryptography.hazmat.primitives.asymmetric import rsa
import jwt
import pytest
from starlette.testclient import TestClient

from marketplace.user_mcp import create_app
from marketplace.user_mcp_auth import KeycloakTokenVerifier
from marketplace.user_orders import OrderAccess
from test_integration import reset

ISSUER = 'https://identity.example.test/realms/marketplace'
RESOURCE = 'https://orders.example.test/orders/mcp'


@pytest.fixture
def credentials():
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def mint(subject='subject-buyer', **overrides):
        claims = {
            'iss': ISSUER,
            'sub': subject,
            'aud': RESOURCE,
            'iat': int(time.time()),
            'exp': int(time.time()) + 300,
            'azp': 'marketplace-chatgpt',
            'typ': 'Bearer',
            'scope': 'orders:read',
            **overrides,
        }
        return jwt.encode(claims, key, algorithm='RS256', headers={'kid': 'test-key'})

    jwks = SimpleNamespace(get_signing_key_from_jwt=lambda token: SimpleNamespace(key=key.public_key()))
    verifier = KeycloakTokenVerifier(ISSUER, RESOURCE, 'https://unused.example.test/keys',
                                     ['marketplace-chatgpt'], jwks_client=jwks)
    return mint, verifier


@pytest.fixture
def connection(monkeypatch, tmp_path, credentials):
    monkeypatch.setenv('USER_MCP_RESOURCE_URL', RESOURCE)
    monkeypatch.setenv('USER_MCP_ISSUER_URL', ISSUER)
    links = tmp_path / 'links.json'
    links.write_text(json.dumps({
        'issuer': ISSUER,
        'subjects': {'subject-' + user: user for user in ('buyer', 'buyer2', 'seller', 'seller2', 'support')},
    }))
    mint, verifier = credentials
    with TestClient(create_app(verifier=verifier, order_access=OrderAccess(ISSUER, links))) as client:
        yield client, mint, links


def rpc(client, token, method, params=None):
    headers = {'accept': 'application/json, text/event-stream'}
    if token:
        headers['authorization'] = 'Bearer ' + token
    return client.post('/orders/mcp', headers=headers, json={
        'jsonrpc': '2.0', 'id': 1, 'method': method, 'params': params or {},
    })


def call(client, token, name='list_my_orders', **arguments):
    response = rpc(client, token, 'tools/call', {'name': name, 'arguments': arguments})
    assert response.status_code == 200, response.text
    result = response.json()['result']
    assert not result.get('isError'), result
    return result.get('structuredContent') or json.loads(result['content'][0]['text'])


def test_discovery_challenge_and_tool_surface(connection):
    client, mint, _ = connection
    denied = rpc(client, None, 'tools/list')
    assert denied.status_code == 401
    assert 'resource_metadata=' in denied.headers['www-authenticate']
    metadata = client.get('/.well-known/oauth-protected-resource/orders/mcp').json()
    assert metadata['authorization_servers'] == [ISSUER]
    assert metadata['resource'] == RESOURCE
    assert 'orders:read' in metadata['scopes_supported']
    tools = rpc(client, mint(), 'tools/list').json()['result']['tools']
    assert {tool['name'] for tool in tools} == {'get_my_profile', 'list_my_orders', 'get_my_order_status'}
    assert all(tool['annotations']['readOnlyHint'] for tool in tools)
    assert all('user_id' not in tool['inputSchema']['properties'] for tool in tools)
    assert client.get('/health').json()['status'] == 'ok'


@pytest.mark.parametrize('overrides', [
    {'aud': 'https://another.example.test/mcp'},
    {'iss': 'https://another.example.test/realm'},
    {'exp': 1},
    {'iat': int(time.time()) + 10000},
    {'azp': 'unapproved-client'},
    {'typ': 'ID'},
    {'sub': ''},
])
def test_invalid_token_rejected_before_tool_execution(connection, overrides):
    client, mint, _ = connection
    assert rpc(client, mint(**overrides), 'tools/list').status_code == 401


def test_forged_signature_and_missing_scope(connection):
    client, mint, _ = connection
    other = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    claims = jwt.decode(mint(), options={'verify_signature': False})
    forged = jwt.encode(claims, other, algorithm='RS256')
    assert rpc(client, forged, 'tools/list').status_code == 401
    assert rpc(client, mint(scope='profile'), 'tools/list').status_code == 403
    assert client.post('/orders/mcp', headers={'x-api-key': 'old-support-key'}, json={}).status_code == 401


@pytest.mark.parametrize('user,orders,items', [
    ('buyer', {'order-1'}, {'item-1', 'item-2'}),
    ('buyer2', {'order-2'}, {'item-3'}),
    ('seller', {'order-1'}, {'item-1'}),
    ('seller2', {'order-1'}, {'item-2'}),
])
def test_each_identity_sees_only_its_orders_and_lines(connection, user, orders, items):
    client, mint, _ = connection
    result = call(client, mint('subject-' + user))
    assert {order['order_id'] for order in result['orders']} == orders
    assert {item['item_id'] for order in result['orders'] for item in order['items']} == items
    assert all('payment_amount' not in order and 'customer_id' not in order for order in result['orders'])
    assert all('order_status' in order for order in result['orders'])
    assert all('shipment_status' in item for order in result['orders'] for item in order['items'])


def test_cross_account_order_and_unknown_order_are_indistinguishable(connection):
    client, mint, _ = connection
    token = mint()
    denied = call(client, token, 'get_my_order_status', order_id='order-2')
    absent = call(client, token, 'get_my_order_status', order_id='missing-order')
    assert denied == absent == {'status': 'unavailable', 'message': 'Order unavailable for this account'}
    assert call(client, token, 'get_my_order_status', order_id='order-1')['status'] == 'ok'


def test_profile_unlinked_subject_and_link_revocation(connection):
    client, mint, links = connection
    assert call(client, mint(), 'get_my_profile') == {
        'id': 'subject-buyer', 'name': 'buyer', 'nickname': 'buyer',
    }
    for subject in ('unlinked-subject', 'subject-support'):
        response = rpc(client, mint(subject), 'tools/call', {'name': 'list_my_orders', 'arguments': {}})
        assert response.json()['result']['isError']
    config = json.loads(links.read_text())
    del config['subjects']['subject-buyer']
    links.write_text(json.dumps(config))
    response = rpc(client, mint(), 'tools/call', {'name': 'list_my_orders', 'arguments': {}})
    assert response.json()['result']['isError']


def test_concurrent_requests_keep_identity_separate(connection):
    client, mint, _ = connection

    def orders_for(user):
        result = call(client, mint('subject-' + user))
        return {item['item_id'] for order in result['orders'] for item in order['items']}

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(orders_for, ['buyer', 'buyer2', 'seller', 'seller2'] * 3))
    assert results == [{'item-1', 'item-2'}, {'item-3'}, {'item-1'}, {'item-2'}] * 3


def test_invalid_pagination_and_injected_identity_arguments(connection):
    client, mint, _ = connection
    for arguments in ({'limit': 0}, {'limit': 1000}, {'offset': -1}, {'user_id': 'buyer2'}):
        response = rpc(client, mint(), 'tools/call', {'name': 'list_my_orders', 'arguments': arguments})
        result = response.json()
        assert 'error' in result or result['result'].get('isError'), result


def test_verifier_never_accepts_unsigned_tokens(credentials):
    _, verifier = credentials
    token = jwt.encode({'sub': 'buyer'}, key='', algorithm='none')
    assert asyncio.run(verifier.verify_token(token)) is None
