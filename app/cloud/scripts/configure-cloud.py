"""Operator-run credential setup. Secrets stay in memory and Secret Manager.

Run interactively in Cloud Shell after Terraform creates the secret containers.
This sets database credentials; never run it automatically from an app replica.
"""
import argparse
import base64
import getpass
import json
import secrets
import subprocess
import time
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote, unquote, urlsplit
from urllib.request import Request, urlopen


PHASE = 'configuration confirmation'


class Google:
    def __init__(self, project):
        self.project = project
        self.token = subprocess.check_output(
            ['gcloud', 'auth', 'print-access-token'], text=True).strip()

    def request(self, method, url, body=None):
        payload = None if body is None else json.dumps(body).encode()
        req = Request(url, data=payload, method=method, headers={
            'Authorization': 'Bearer ' + self.token,
            'Content-Type': 'application/json'})
        # Only reads retry automatically: a timed-out mutation may already have
        # succeeded, so replaying it could create an extra secret version.
        attempts = 3 if method == 'GET' else 1
        for attempt in range(attempts):
            try:
                with urlopen(req, timeout=30) as response:
                    return json.load(response)
            except HTTPError as error:
                retry = method == 'GET' and error.code in (429, 500, 502, 503, 504)
                error.close()
                if retry and attempt + 1 < attempts:
                    time.sleep(2 ** attempt)
                    continue
                # Never expose API bodies, URLs or arbitrary error descriptions.
                raise RuntimeError(f'Google API returned HTTP {error.code}') from None
            except (URLError, TimeoutError, OSError):
                if attempt + 1 < attempts:
                    time.sleep(2 ** attempt)
                    continue
                raise RuntimeError('Google API connection failed; retry setup') from None

    def secret(self, name):
        url = (f'https://secretmanager.googleapis.com/v1/projects/{self.project}'
               f'/secrets/marketplace-{name}/versions/latest:access')
        try:
            data = self.request('GET', url)
        except RuntimeError as error:
            if str(error).endswith('HTTP 404'):
                return None
            raise
        return base64.b64decode(data['payload']['data']).decode()

    def store(self, name, value):
        if self.secret(name) == value:
            return
        self.request('POST',
            f'https://secretmanager.googleapis.com/v1/projects/{self.project}'
            f'/secrets/marketplace-{name}:addVersion',
            {'payload': {'data': base64.b64encode(value.encode()).decode()}})
        print(f'Secret configured: marketplace-{name}')

    def wait(self, operation, *, timeout=600, phase='database credential update'):
        deadline = time.monotonic() + timeout
        progress_at = time.monotonic()
        while operation.get('status') != 'DONE':
            if time.monotonic() > deadline:
                raise RuntimeError(f'{phase} timed out; inspect Cloud SQL operations and retry')
            if time.monotonic() >= progress_at:
                print(f'Waiting for {phase}; no credentials are displayed.', flush=True)
                progress_at = time.monotonic() + 60
            time.sleep(3)
            operation = self.request('GET', operation['selfLink'])
        if operation.get('error'):
            raise RuntimeError(f'{phase} failed; inspect Cloud SQL operations')



def ensure_database_ready(google, sql, project, instance_name):
    """Wait for an interrupted startup before attempting any user mutations."""
    def inspect():
        value = google.request('GET', sql)
        if value['settings']['ipConfiguration'].get('ipv4Enabled'):
            raise RuntimeError('Expected private-only database; inspect configuration first')
        return value

    inspect()
    operations_url = (f'https://sqladmin.googleapis.com/sql/v1beta4/projects/{project}'
                      f'/operations?instance={quote(instance_name, safe="")}&maxResults=100')
    # Do not PATCH or edit SQL users while a previous operation is running.
    for operation in google.request('GET', operations_url).get('items', []):
        if operation.get('status') != 'DONE':
            google.wait(operation, timeout=1800, phase='existing database operation')
    instance = inspect()
    if instance['settings'].get('activationPolicy') != 'ALWAYS':
        print('Starting PostgreSQL for credential setup.', flush=True)
        operation = google.request('PATCH', sql, {'settings': {'activationPolicy': 'ALWAYS'}})
        google.wait(operation, timeout=1800, phase='database startup')
    deadline = time.monotonic() + 1800
    progress_at = time.monotonic()
    while True:
        instance = inspect()
        if (instance.get('state') == 'RUNNABLE'
                and instance['settings'].get('activationPolicy') == 'ALWAYS'):
            return
        if instance.get('state') in ('FAILED', 'SUSPENDED'):
            raise RuntimeError('Database is unavailable; inspect Cloud SQL status')
        if time.monotonic() >= deadline:
            raise RuntimeError('Database readiness timed out; inspect Cloud SQL status and retry')
        if time.monotonic() >= progress_at:
            print('Waiting for PostgreSQL readiness before configuring users.', flush=True)
            progress_at = time.monotonic() + 60
        time.sleep(3)


def database_url(user, password, database, connection, *, raw=False):
    scheme = 'postgresql' if raw else 'postgresql+psycopg'
    host = 'localhost' if raw else ''
    socket = quote('/cloudsql/' + connection, safe='')
    return f'{scheme}://{user}:{quote(password, safe="")}@{host}/{database}?host={socket}'



def stored_database_password(stored, user, database, connection, *, raw=False):
    """Recover only this deployment's credential; never reset from a wrong secret."""
    if raw and user == 'mcp_registry' and stored.startswith('postgresql+psycopg://'):
        # Migrate the first deployment's SQLAlchemy URL to the psycopg format,
        # retaining the same strict role/database/socket validation.
        return stored_database_password(stored, user, database, connection, raw=False)
    parsed = urlsplit(stored)
    expected_scheme = 'postgresql' if raw else 'postgresql+psycopg'
    if (parsed.scheme != expected_scheme
            or unquote(parsed.username or '') != user
            or unquote(parsed.path.lstrip('/')) != database
            or parsed.hostname != ('localhost' if raw else None)
            or parse_qs(parsed.query).get('host') != ['/cloudsql/' + connection]
            or not parsed.password):
        raise RuntimeError('Stored database credential does not match this role and instance; reconcile manually')
    return unquote(parsed.password)


def main():
    global PHASE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--region', default='asia-south1')
    parser.add_argument('--instance', default='marketplace-postgres')
    args = parser.parse_args()
    confirmation = input(f'Configure credentials in {args.project}? Type the project ID: ').strip()
    if confirmation != args.project:
        raise SystemExit('No changes made.')
    PHASE = 'Google authentication'
    google = Google(args.project)
    connection = f'{args.project}:{args.region}:{args.instance}'
    sql = f'https://sqladmin.googleapis.com/sql/v1beta4/projects/{args.project}/instances/{args.instance}'
    PHASE = 'database startup and readiness'
    ensure_database_ready(google, sql, args.project, args.instance)
    PHASE = 'database user discovery'
    existing = {u['name'] for u in google.request('GET', sql + '/users').get('items', [])}
    roles = [('postgres', 'bootstrap-database-url', 'market', False),
             ('market', 'web-database-url', 'market', False),
             ('agent_reader', 'web-read-database-url', 'market', True),
             ('mcp_registry', 'mcp-registry-database-url', 'market', True),
             ('litellm', 'gateway-database-url', 'litellm', True)]
    for user, secret_name, database, raw in roles:
        PHASE = f'{user} database credential configuration'
        stored = google.secret(secret_name)
        if user in existing and not stored and user != 'postgres':
            raise SystemExit(f'{user} exists without the expected secret; reconcile manually before retry.')
        password = (stored_database_password(stored, user, database, connection, raw=raw)
                    if stored else secrets.token_urlsafe(36))
        dsn = database_url(user, password, database, connection, raw=raw)
        # Store first, so a retry can recover after an interrupted API operation.
        google.store(secret_name, dsn)
        method = 'PUT' if user in existing else 'POST'
        endpoint = sql + '/users' + ('?name=' + quote(user) if method == 'PUT' else '')
        google.wait(google.request(method, endpoint, {'name': user, 'password': password}))
        print(f'Database credential configured: {user}')
        if user == 'agent_reader':
            google.store('mcp-read-database-url', dsn)
    PHASE = 'gateway and middleware key configuration'
    for name, prefix in [('gateway-master-key', 'sk-'), ('mcp-api-key', '')]:
        if not google.secret(name):
            google.store(name, prefix + secrets.token_urlsafe(36))
    PHASE = 'demo login password configuration'
    if not google.secret('web-demo-password'):
        password = getpass.getpass('New marketplace demo login password (at least 16 characters): ')
        if len(password) < 16 or password != getpass.getpass('Confirm demo login password: '):
            raise SystemExit('Demo password not stored; rerun to finish.')
        google.store('web-demo-password', password)
    PHASE = 'model provider key configuration'
    if not google.secret('gateway-provider-key'):
        provider = getpass.getpass('OpenAI API key for cloud LiteLLM (hidden): ').strip()
        if not provider.startswith('sk-'):
            raise SystemExit('Provider key not stored; rerun with an OpenAI API key.')
        google.store('gateway-provider-key', provider)
    PHASE = 'Lakera key configuration'
    if not google.secret('gateway-lakera-key'):
        lakera = getpass.getpass('Lakera API key (hidden; blank leaves Lakera unavailable): ').strip()
        google.store('gateway-lakera-key', lakera or 'not-configured')
    print('Credential setup completed. Run initialization before deploying app services.')
    print('PostgreSQL is running for setup. Stop it after verification to avoid idle compute charges.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError):
        raise SystemExit(f'Setup stopped during {PHASE}. Inspect service status and retry; secret values were not logged.') from None
