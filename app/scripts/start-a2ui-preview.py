#!/usr/bin/env python3
"""Start an additional local preview, reusing the existing Test workspace.

No database initialization/reset, no restart of existing services. Credentials
are copied directly from the local Test container into a private env file.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile

APP = Path(__file__).resolve().parents[1]
BACKEND = 'marketplace-a2ui-preview-backend'
FRONTEND = 'marketplace-a2ui-preview-frontend'


def docker(*args):
    result = subprocess.run(['docker', *args], text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(f'Docker {args[0]} failed: {result.stderr[:500]}')
    return result.stdout


def start():
    protected_names = ['marketplace-lab-backend-1', 'marketplace-lab-frontend-1',
                       'marketplace-lab-test-backend-1', 'marketplace-lab-test-frontend-1']
    protected = json.loads(docker('inspect', *protected_names))
    fingerprint = [(c['Id'], c['State']['StartedAt']) for c in protected]
    current = set(docker('ps', '-a', '--format', '{{.Names}}').splitlines())
    if BACKEND in current or FRONTEND in current:
        raise RuntimeError('A2UI preview already exists; inspect it rather than replacing it.')
    source = next(c for c in protected if c['Name'].endswith('test-backend-1'))
    env = dict(item.split('=', 1) for item in source['Config']['Env'])
    if not env['DATABASE_URL'].endswith('/market_test'):
        raise RuntimeError('Source is not the Test database')
    network = next(iter(source['NetworkSettings']['Networks']))
    env.update(A2UI_DEMO='true', INITIALIZE_ON_STARTUP='false',
               MARKETPLACE_SESSION_COOKIE='market_a2ui_session',
               MARKETPLACE_IDENTITY_NAMESPACE='marketplace-a2ui-preview',
               ALLOWED_ORIGINS='http://127.0.0.1:5180,http://localhost:5180')
    # This preview uses the ordinary local SDK path, independent of A2A/cloud.
    for key in list(env):
        if key.startswith(('DELIVERY_', 'A2A_')) or key in ('MARKETPLACE_OIDC_CONFIG', 'GATEWAY_IAM_AUDIENCE'):
            env.pop(key)
    directory = Path(tempfile.mkdtemp(prefix='marketplace-a2ui-preview-'))
    directory.chmod(0o700)
    envfile = directory / 'backend.env'
    envfile.write_text('\n'.join(f'{k}={v}' for k, v in env.items()) + '\n')
    envfile.chmod(0o600)
    nginx = directory / 'nginx.conf'
    nginx.write_text((APP / 'frontend/nginx.conf').read_text().replace('http://backend:8000', f'http://{BACKEND}:8000'))
    args = ['run', '-d', '--name', BACKEND, '--network', network, '--env-file', str(envfile),
            '--mount', f'type=bind,source={APP / "backend/marketplace"},target=/app/marketplace,readonly',
            '--mount', f'type=bind,source={APP / "backend/tests"},target=/app/tests,readonly',
            '--mount', f'type=bind,source={APP / "data"},target=/data,readonly',
            'marketplace-a2ui-preview-backend:local']
    try:
        docker(*args)
        docker('run', '-d', '--name', FRONTEND, '--network', network,
               '-p', '127.0.0.1:5180:80', '--mount', f'type=bind,source={nginx},target=/etc/nginx/conf.d/default.conf,readonly',
               'marketplace-a2ui-preview-frontend:local')
    finally:
        envfile.unlink(missing_ok=True)
    after = json.loads(docker('inspect', *protected_names))
    assert fingerprint == [(c['Id'], c['State']['StartedAt']) for c in after]
    print('A2UI preview started at http://127.0.0.1:5180; existing Test and production containers unchanged.')


if __name__ == '__main__':
    start()
