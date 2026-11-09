"""Signed-token HTTP MCP, transaction races, operator toggle and worker checks."""
import asyncio
from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
import json
import time
from types import SimpleNamespace
import httpx
import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from starlette.testclient import TestClient
from sqlalchemy import select, func
from marketplace.db import User, Session, Payout, Shipment, State, Event, Command, Return, Allocation, Item
from marketplace.api import app
from marketplace.business import BusinessError, execute
from marketplace.user_mcp_auth import KeycloakTokenVerifier, VerifiedPrincipal
from marketplace.payout_service import PayoutAccess
from marketplace.payout_mcp import create_app
from marketplace.payout_automation import PayoutAutomation
from marketplace.payout_worker import run_once
from test_integration import reset

ISSUER = 'https://issuer.example.test/marketplace'
RESOURCE = 'http://127.0.0.1:58503/payouts/mcp'
CLIENT = 'marketplace-payout-worker'
SUBJECT = 'service-subject'
PRINCIPAL = VerifiedPrincipal(ISSUER, SUBJECT, CLIENT, frozenset(['payouts:read', 'payouts:release']))


@pytest.fixture
def setup(monkeypatch, tmp_path):
    monkeypatch.setenv('PAYOUT_MCP_RESOURCE_URL', RESOURCE)
    monkeypatch.setenv('PAYOUT_MCP_ISSUER_URL', ISSUER)
    policy = {'issuer': ISSUER, 'client_id': CLIENT, 'subject': SUBJECT, 'simulation_only': True,
        'seller_scope': 'all', 'max_payout_paise': 1000000, 'max_run_paise': 2000000, 'max_run_count': 10}
    path = tmp_path / 'policy.json'
    path.write_text(json.dumps(policy))
    access = PayoutAccess(path)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwks = SimpleNamespace(get_signing_key_from_jwt=lambda _: SimpleNamespace(key=key.public_key()))
    verifier = KeycloakTokenVerifier(ISSUER, RESOURCE, 'unused', [CLIENT], jwks_client=jwks)
    def mint(**overrides):
        return jwt.encode({'iss': ISSUER, 'sub': SUBJECT, 'azp': CLIENT, 'aud': RESOURCE,
            'iat': int(time.time()), 'exp': int(time.time()) + 300, 'typ': 'Bearer',
            'scope': 'payouts:read payouts:release', **overrides}, key, algorithm='RS256')
    with TestClient(create_app(verifier=verifier, payout_access=access)) as client:
        yield SimpleNamespace(access=access, path=path, policy=policy, mint=mint, client=client)


def enable():
    with Session.begin() as db:
        db.add(PayoutAutomation(id=1, enabled=True))


def rpc(setup, name, args=None, **claims):
    return setup.client.post('/payouts/mcp', headers={'Authorization': 'Bearer ' + setup.mint(**claims),
        'Accept': 'application/json, text/event-stream'}, json={'jsonrpc': '2.0', 'id': 1,
        'method': 'tools/call', 'params': {'name': name, 'arguments': args or {}}})


def result(response):
    payload = response.json()['result']
    assert not payload.get('isError'), payload
    return payload.get('structuredContent') or json.loads(payload['content'][0]['text'])


def release(setup, payout='payout-1', key='stable-payout-key', run='run-one-123'):
    return setup.access.release(PRINCIPAL, payout, key, run)


def test_default_disabled_scope_and_candidates(setup):
    assert result(rpc(setup, 'list_eligible_payouts'))['candidates'] == []
    with pytest.raises(BusinessError, match='disabled'):
        release(setup)
    with Session.begin() as db:
        db.get(PayoutAutomation, 1).enabled = True
    candidates = result(rpc(setup, 'list_eligible_payouts'))['candidates']
    assert {p['payout_id'] for p in candidates} == {'payout-1', 'payout-2'}
    assert {p['seller_id'] for p in candidates} == {'seller-1', 'seller-2'}
    with Session() as db:
        assert db.get(PayoutAutomation, 1).service_policy['seller_scope'] == 'all'


@pytest.mark.parametrize('claims', [
    {'aud': 'orders'}, {'iss': 'https://other'}, {'exp': 1}, {'azp': 'marketplace-chatgpt'},
    {'typ': 'ID'}, {'iat': int(time.time()) + 5000}, {'sub': ''},
])
def test_invalid_tokens_rejected(setup, claims):
    assert rpc(setup, 'list_eligible_payouts', **claims).status_code == 401


def test_permissions_unknown_identity_and_injected_actor(setup):
    enable()
    assert rpc(setup, 'list_eligible_payouts', scope='orders:read').status_code == 403
    assert rpc(setup, 'list_eligible_payouts', sub='buyer-subject').json()['result']['isError']
    response = rpc(setup, 'request_payout_release', {'payout_id': 'payout-1',
        'idempotency_key': 'release-read-only', 'run_id': 'run-readonly'}, scope='payouts:read')
    assert response.json()['result']['isError']
    assert rpc(setup, 'list_eligible_payouts', {'user_id': 'operator'}).json().get('error')
    assert setup.client.post('/payouts/mcp', headers={'x-api-key': 'shared'}, json={}).status_code == 401


def test_idempotency_audit_and_concurrent_release(setup):
    enable()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: release(setup), range(2)))
    assert results[0] == results[1]
    with Session() as db:
        assert db.get(Payout, 'payout-1').status == 'completed'
        events = db.scalars(select(Event).where(Event.kind == 'service_payout_release')).all()
        assert len(events) == 1
        assert events[0].details['subject'] == SUBJECT
        assert events[0].details['client_id'] == CLIENT
        assert events[0].details['run_id'] == 'run-one-123'
        assert db.scalar(select(func.count()).select_from(Command)) == 1
        assert db.scalar(select(func.count()).select_from(Event).where(Event.kind == 'service_payout_retry')) == 1
    with pytest.raises(BusinessError, match='already completed'):
        release(setup, key='different-payout-key')


@pytest.mark.parametrize('case', ['hold', 'return', 'amount', 'disabled', 'zero'])
def test_backend_rechecks_after_candidate_read(setup, case):
    enable()
    assert setup.access.eligible(PRINCIPAL)['candidates']
    with Session.begin() as db:
        if case == 'hold':
            db.get(Shipment, 'shipment-1').delivered_at = db.get(State, 1).clock
        elif case == 'return':
            db.add(Return(id='blocking-return', item_id='item-1', quantity=1, status='requested'))
        elif case == 'amount':
            db.get(Payout, 'payout-1').amount = 1000001
        elif case == 'zero':
            db.get(Payout, 'payout-1').amount = 0
        else:
            db.get(PayoutAutomation, 1).enabled = False
    with pytest.raises(BusinessError):
        release(setup)
    with Session() as db:
        assert db.get(Payout, 'payout-1').status in ('held', 'failed')
        assert db.scalar(select(func.count()).select_from(Event).where(Event.kind == 'service_payout_denied')) == 1


def test_run_amount_count_limits_and_retry_key_conflict(setup):
    enable()
    with Session.begin() as db:
        shipment = db.get(Shipment, 'shipment-2')
        shipment.status = 'delivered'
        shipment.delivered_at = db.get(State, 1).clock - timedelta(hours=48)
    setup.policy['max_run_paise'] = 450000
    setup.path.write_text(json.dumps(setup.policy))
    release(setup)
    with pytest.raises(BusinessError, match='different request'):
        release(setup, payout='payout-2')
    with pytest.raises(BusinessError, match='amount limit'):
        release(setup, payout='payout-2', key='second-release-key')
    setup.policy['max_run_paise'] = 2000000
    setup.policy['max_run_count'] = 1
    setup.path.write_text(json.dumps(setup.policy))
    with pytest.raises(BusinessError, match='count limit'):
        release(setup, payout='payout-2', key='second-release-key')


def test_scope_revocation_and_disabled_retry(setup):
    enable()
    release(setup)
    setup.policy['subject'] = 'revoked'
    setup.path.write_text(json.dumps(setup.policy))
    with pytest.raises(BusinessError, match='identity'):
        release(setup)


def test_operator_toggle_csrf_main_guard_and_manual_command(setup, monkeypatch):
    with TestClient(app) as client:
        assert client.get('/api/payout-automation').status_code == 401
        login = client.post('/api/login', json={'username': 'operator', 'password': 'demo-marketplace'}).json()
        assert client.get('/api/payout-automation').json()['enabled'] is False
        assert client.post('/api/payout-automation', json={'enabled': True}).status_code == 403
        client.headers['x-csrf-token'] = login['csrf']
        enabled = client.post('/api/payout-automation', json={'enabled': True}).json()
        assert enabled['enabled'] and enabled['can_configure'] and enabled['workspace'] == 'test'
        denied = client.post('/api/commands', json={'action': 'payout', 'data': {'id': 'payout-1'},
            'idempotency_key': 'manual-while-automated'})
        assert denied.status_code == 409
        assert client.post('/api/payout-automation', json={'enabled': 'yes'}).status_code == 422
        assert client.post('/api/payout-automation', json={'enabled': False}).json()['enabled'] is False
        monkeypatch.setenv('DATABASE_URL', 'postgresql://unused/market')
        assert client.get('/api/payout-automation').json()['can_configure'] is False
        assert client.post('/api/payout-automation', json={'enabled': True}).status_code == 403


@pytest.mark.parametrize('account', ['buyer', 'seller', 'support'])
def test_nonoperator_cannot_read_or_toggle_automation(setup, account):
    with TestClient(app) as client:
        login = client.post('/api/login', json={'username': account, 'password': 'demo-marketplace'}).json()
        client.headers['x-csrf-token'] = login['csrf']
        assert client.get('/api/payout-automation').status_code == 403
        assert client.post('/api/payout-automation', json={'enabled': True}).status_code == 403


def test_worker_retries_network_failure_with_stable_idempotency():
    requests, released = [], False
    def handle(request):
        nonlocal released
        if request.url.path == '/token':
            return httpx.Response(200, json={'access_token': 'service-token'})
        body = json.loads(request.content)
        args = body['params']['arguments']
        if body['params']['name'] == 'list_eligible_payouts':
            data = {'candidates': [{'payout_id': 'payout-fixture', 'amount_paise': 100}]}
        else:
            requests.append(args)
            if not released:
                released = True
                raise httpx.ReadTimeout('Response lost after commit')
            data = {'id': 'payout-fixture', 'amount': 100}
        return httpx.Response(200, json={'result': {'structuredContent': data}})
    config = {'token_url': 'http://local/token', 'mcp_url': 'http://local/mcp', 'client_id': CLIENT,
        'client_secret': 'test', 'max_run_count': 10, 'max_run_paise': 1000}
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        summary = run_once(config, client)
    assert summary['completed'] == ['payout-fixture']
    assert len(requests) == 2 and requests[0] == requests[1]


def test_scheduled_summary_excludes_unrelated_debug_denials(setup):
    enable()
    setup.access.eligible(PRINCIPAL, run_id='scheduled-run-123')
    release(setup, run='scheduled-run-123')
    with pytest.raises(BusinessError):
        release(setup, payout='payout-3', key='unrelated-debug-denial', run='debug-run-123')
    with Session() as db:
        summary = db.get(PayoutAutomation, 1).last_result
        assert summary['run_id'] == 'scheduled-run-123'
        assert summary['completed'] == ['payout-1'] and summary['denied'] == []
        history = db.scalar(select(Event).where(Event.kind == 'service_payout_run'))
        assert history.details['completed'] == ['payout-1']


@pytest.mark.parametrize('seller_scope', [None, '', 'seller-1', ['seller-1']])
def test_invalid_seller_coverage_policy_is_rejected(setup, seller_scope):
    setup.policy['seller_scope'] = seller_scope
    setup.path.write_text(json.dumps(setup.policy))
    with pytest.raises(BusinessError, match='Invalid service policy'):
        setup.access.eligible(PRINCIPAL)


def test_worker_releases_eligible_orders_for_all_sellers_after_hold(setup):
    enable()
    def command(actor, action, data, key):
        with Session.begin() as db:
            return execute(db, db.get(User, actor), key, action, data)

    order = command('buyer', 'purchase', {'items': [
        {'listing_id': f'listing-{n}', 'quantity': 1} for n in (1, 2, 3)]}, 'all-seller-purchase')
    with Session() as db:
        items = db.scalars(select(Item).where(Item.order_id == order['id'])).all()
        assert {item.seller_id for item in items} == {'seller-1', 'seller-2', 'seller-3'}
        shipments = [(item.seller_id, db.scalar(select(Shipment.id).where(Shipment.item_id == item.id)))
                     for item in items]
        payouts = set(db.scalars(select(Payout.id).join(Allocation).join(Item)
                                .where(Item.order_id == order['id'])).all())
    for seller, shipment in shipments:
        actor = {'seller-1': 'seller', 'seller-2': 'seller2'}.get(seller, 'operator')
        command(actor, 'dispatch', {'id': shipment}, 'dispatch-' + shipment)
        command(actor, 'deliver', {'id': shipment}, 'deliver-' + shipment)
    assert not payouts.intersection(p['payout_id'] for p in setup.access.eligible(PRINCIPAL)['candidates'])
    for payout in payouts:
        with pytest.raises(BusinessError, match='hold'):
            release(setup, payout=payout, key='held-' + payout)
    command('operator', 'advance_clock', {'hours': 24}, 'all-seller-advance-clock')
    assert payouts <= {p['payout_id'] for p in setup.access.eligible(PRINCIPAL)['candidates']}

    def handle(request):
        if request.url.path == '/token':
            return httpx.Response(200, json={'access_token': setup.mint()})
        response = setup.client.post('/payouts/mcp', headers={
            'Authorization': request.headers['Authorization'], 'Content-Type': 'application/json',
            'Accept': 'application/json, text/event-stream'}, content=request.content)
        return httpx.Response(response.status_code, json=response.json())

    config = {'token_url': 'http://local/token', 'mcp_url': 'http://local/payouts/mcp',
              'client_id': CLIENT, 'client_secret': 'test', 'max_run_count': 10, 'max_run_paise': 2000000}
    with httpx.Client(transport=httpx.MockTransport(handle)) as client:
        first, second = run_once(config, client), run_once(config, client)
    assert payouts <= set(first['completed'])
    assert not first['denied']
    assert second['completed'] == [] and second['amount_paise'] == 0
    with Session() as db:
        assert all(db.get(Payout, payout).status == 'completed' for payout in payouts)
    for payout in payouts:
        retried = release(setup, payout=payout, key='simulated-payout:' + payout, run='retry-run-123')
        assert retried['id'] == payout and retried['run_id'] == first['run_id']
    with Session() as db:
        events = db.scalars(select(Event).where(Event.kind == 'service_payout_release')).all()
        assert len(events) == len(first['completed'])
