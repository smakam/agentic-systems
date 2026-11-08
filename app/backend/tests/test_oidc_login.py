"""Browser-bound OIDC login and existing password-session regression checks."""
import json
import time
from types import SimpleNamespace
from urllib.parse import parse_qs, urlsplit

from cryptography.hazmat.primitives.asymmetric import rsa
import jwt
import pytest
from starlette.testclient import TestClient

from marketplace import oidc_login
from marketplace.api import app
from test_integration import reset


@pytest.fixture
def browser(monkeypatch, tmp_path):
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    issuer = 'https://identity.example.test/realms/marketplace'
    links = tmp_path / 'links.json'
    links.write_text(json.dumps({'issuer': issuer, 'subjects': {'subject-buyer': 'buyer', 'subject-support': 'support'}}))
    config = {'issuer': issuer, 'client_id': 'marketplace-web', 'client_secret': 'client-secret',
              'authorization_url': issuer + '/protocol/openid-connect/auth',
              'token_url': issuer + '/protocol/openid-connect/token', 'jwks_url': issuer + '/certs',
              'state_secret': 'test-only-signing-key-with-at-least-thirty-two-bytes',
              'origins': ['http://testserver'], 'identity_links': str(links)}
    monkeypatch.setattr(oidc_login, 'configuration', lambda: config)
    monkeypatch.setattr(oidc_login, 'signing_keys', lambda url: SimpleNamespace(
        get_signing_key_from_jwt=lambda token: SimpleNamespace(key=key.public_key())))
    client = TestClient(app)
    response = client.get('/api/auth/keycloak/login?origin=http://testserver', follow_redirects=False)
    assert response.status_code == 303
    params = parse_qs(urlsplit(response.headers['location']).query)
    assert params['code_challenge_method'] == ['S256'] and params['scope'] == ['openid']
    assert 'HttpOnly' in response.headers['set-cookie'] and 'SameSite=lax' in response.headers['set-cookie']
    claims = {'iss': issuer, 'sub': 'subject-buyer', 'aud': config['client_id'], 'azp': config['client_id'],
              'exp': int(time.time()) + 60, 'iat': int(time.time()), 'nonce': params['nonce'][0]}
    sent = []

    class Exchange:
        def __init__(self, **kwargs): pass
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def post(self, url, data):
            sent.append(data)
            return SimpleNamespace(raise_for_status=lambda: None, json=lambda: {
                'id_token': jwt.encode(claims, key, algorithm='RS256'), 'access_token': 'not-stored'})

    monkeypatch.setattr(oidc_login.httpx, 'Client', Exchange)
    return client, params['state'][0], claims, sent


def finish(client, state):
    return client.get('/api/auth/keycloak/callback', params={'state': state, 'code': 'one-use-code'}, follow_redirects=False)


def test_keycloak_session_uses_existing_role_and_csrf(browser):
    client, state, _, sent = browser
    response = finish(client, state)
    assert response.headers['location'] == 'http://testserver/'
    assert 'market_session=' in response.headers['set-cookie']
    assert sent[0]['code_verifier'] and sent[0]['client_id'] == 'marketplace-web'
    identity = client.get('/api/me').json()
    assert identity['user']['username'] == 'buyer'
    assert identity['user']['role'] == 'buyer'
    assert client.post('/api/logout').status_code == 403
    assert client.post('/api/logout', headers={'x-csrf-token': identity['csrf']}).status_code == 200
    assert client.get('/api/me').status_code == 401


def test_support_mapping_uses_database_role(browser):
    client, state, claims, _ = browser
    claims.update(sub='subject-support', role='buyer')
    assert finish(client, state).headers['location'] == 'http://testserver/'
    assert client.get('/api/me').json()['user']['role'] == 'support'


@pytest.mark.parametrize('changes', [
    {'nonce': 'another-login'}, {'aud': 'marketplace-chatgpt'}, {'iss': 'https://untrusted.test'},
    {'exp': 1}, {'azp': 'another-client'}, {'sub': ''},
])
def test_invalid_id_token_never_creates_session(browser, changes):
    client, state, claims, _ = browser
    claims.update(changes)
    assert 'login_error=keycloak_failed' in finish(client, state).headers['location']
    assert client.get('/api/me').status_code == 401


def test_other_browser_or_wrong_state_rejected_before_exchange(browser):
    client, state, _, sent = browser
    assert finish(client, 'wrong-state').status_code == 400
    client.cookies.clear()
    assert finish(client, state).status_code == 400
    assert sent == []


def test_unlinked_subject_cannot_select_account_by_claim(browser):
    client, state, claims, _ = browser
    claims.update(sub='unlinked', preferred_username='operator')
    assert 'login_error=account_unlinked' in finish(client, state).headers['location']
    assert client.get('/api/me').status_code == 401


def test_untrusted_callback_origin_rejected(browser):
    client, _, _, _ = browser
    assert client.get('/api/auth/keycloak/login?origin=https://attacker.test').status_code == 400


def test_existing_password_login_remains_available(browser):
    client, _, _, _ = browser
    assert client.get('/api/auth/providers').json() == {'password': True, 'keycloak': True}
    response = client.post('/api/login', json={'username': 'support', 'password': 'demo-marketplace'})
    assert response.status_code == 200
    assert client.get('/api/me').json()['user']['username'] == 'support'


def test_keycloak_optional_when_not_configured(monkeypatch):
    monkeypatch.setattr(oidc_login, 'configuration', lambda: None)
    client = TestClient(app)
    assert client.get('/api/auth/providers').json() == {'password': True, 'keycloak': False}
    assert client.get('/api/auth/keycloak/login?origin=http://testserver').status_code == 404


def test_forged_signature_rejected(browser, monkeypatch):
    client, state, _, _ = browser
    wrong = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    monkeypatch.setattr(oidc_login, 'signing_keys', lambda url: SimpleNamespace(
        get_signing_key_from_jwt=lambda token: SimpleNamespace(key=wrong.public_key())))
    assert 'login_error=keycloak_failed' in finish(client, state).headers['location']
    assert client.get('/api/me').status_code == 401


def test_denied_consent_does_not_create_session(browser):
    client, state, _, sent = browser
    response = client.get('/api/auth/keycloak/callback', params={'state': state, 'error': 'access_denied'}, follow_redirects=False)
    assert 'login_error=keycloak_failed' in response.headers['location']
    assert sent == [] and client.get('/api/me').status_code == 401
