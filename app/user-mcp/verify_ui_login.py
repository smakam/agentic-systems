"""Read-only real login checks for both auth methods and both local workspaces."""
from html.parser import HTMLParser
from http.cookiejar import CookieJar
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode, urljoin
from urllib.request import build_opener, HTTPCookieProcessor, HTTPRedirectHandler, Request

STATE = Path(__file__).resolve().parents[1] / '.user-mcp'


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args): return None


class Forms(HTMLParser):
    def __init__(self, source):
        super().__init__(); self.forms = []; self.current = None; self.feed(source)
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form': self.current = {**attrs, 'inputs': []}; self.forms.append(self.current)
        if tag in ('input', 'button') and self.current is not None: self.current['inputs'].append(attrs)
    def handle_endtag(self, tag):
        if tag == 'form': self.current = None


def request(client, url, data=None, headers=None):
    try: response = client.open(Request(url, data=data, headers=headers or {}), timeout=20)
    except HTTPError as response_error: response = response_error
    return response.status, response.headers, response.read().decode()


def main():
    settings = json.loads((STATE / 'settings.json').read_text())
    receipts = []
    for port in (5178, 5179):
        for account in ('buyer', 'buyer2', 'seller', 'seller2', 'support', 'operator'):
            origin = f'http://127.0.0.1:{port}'
            for method in ('password', 'keycloak'):
                client = build_opener(HTTPCookieProcessor(CookieJar()), NoRedirect())
                if method == 'password':
                    status, _, _ = request(client, origin + '/api/login', json.dumps({
                        'username': account, 'password': 'demo-marketplace'}).encode(),
                        {'Content-Type': 'application/json', 'Origin': origin})
                    assert status == 200, f'{port} {account}: password login failed'
                else:
                    url = origin + '/api/auth/keycloak/login?' + urlencode({'origin': origin})
                    status, headers, body = request(client, url)
                    for _ in range(15):
                        if status in (302, 303):
                            url = urljoin(url, headers['Location'])
                            assert 'login_error' not in url, f'{port} {account}: Keycloak callback rejected'
                            if url == origin + '/': break
                            status, headers, body = request(client, url)
                            continue
                        assert status == 200, f'{port} {account}: Keycloak flow HTTP {status}'
                        forms = [f for f in Forms(body).forms if any(i.get('name') in ('password', 'accept') for i in f['inputs'])]
                        assert forms, 'No Keycloak login/consent form'
                        form = forms[0]
                        fields = {i['name']: i.get('value', '') for i in form['inputs'] if i.get('name') and i.get('type') == 'hidden'}
                        if any(i.get('name') == 'password' for i in form['inputs']):
                            fields.update(username=account, password=settings['user_password'])
                        else: fields['accept'] = 'Yes'
                        url = urljoin(url, form['action'])
                        status, headers, body = request(client, url, urlencode(fields).encode(), {'Content-Type': 'application/x-www-form-urlencoded'})
                    else: raise AssertionError('Keycloak exceeded redirect budget')
                status, _, body = request(client, origin + '/api/me')
                profile = json.loads(body)
                assert status == 200 and profile['user']['username'] == account, f'{port} {account}: wrong session identity'
                status, _, body = request(client, origin + '/api/market')
                assert status == 200, f'{port} {account}: marketplace read failed'
                market = json.loads(body)
                if account.startswith('buyer'):
                    assert all(o['customer_id'] == profile['user']['id'] for o in market['orders'])
                if account.startswith('seller'):
                    assert all(i['seller_id'] == profile['user']['seller_id'] for i in market['items'])
                status, _, _ = request(client, origin + '/api/logout', b'{}', {
                    'Content-Type': 'application/json', 'x-csrf-token': profile['csrf'], 'Origin': origin})
                assert status == 200, 'Logout failed'
                assert request(client, origin + '/api/me')[0] == 401, 'Logout did not end app session'
                receipts.append({'port': port, 'account': account, 'method': method, 'login': 'passed', 'scope': 'passed', 'logout': 'passed'})
                print(f'{port} {account} {method}: passed', flush=True)
    (STATE / 'ui-login-verification.json').write_text(json.dumps(receipts, indent=2) + '\n')
    print(f'{len(receipts)} real login/scope/logout combinations passed.')


if __name__ == '__main__': main()
