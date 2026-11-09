#!/usr/bin/env python3
"""Build and run the existing marketplace UI/API services from this checkout or main.

Keep the active Compose environment, private Keycloak configuration, databases,
and published ports. Only the four main/Test application services are recreated.
"""

import argparse
import json
from pathlib import Path
import subprocess

APP = Path(__file__).resolve().parents[1]
STATE = APP / '.user-mcp'
SERVICES = ['backend', 'frontend', 'memory-backend', 'memory-frontend']
BACKENDS = ['backend', 'memory-backend']
CONTAINERS = ['marketplace-lab-backend-1', 'marketplace-lab-test-backend-1']


def run(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def source_app(checkout):
    if checkout == 'branch':
        return APP
    result = run(['git', '-C', str(APP.parent), 'worktree', 'list', '--porcelain'],
                 capture_output=True, text=True)
    for record in result.stdout.split('\n\n'):
        fields = dict(line.split(' ', 1) for line in record.splitlines() if ' ' in line)
        if fields.get('branch') == 'refs/heads/main':
            app = Path(fields['worktree']) / 'app'
            if not (app / 'backend/marketplace').is_dir() or not (app / 'frontend').is_dir():
                raise RuntimeError('The main worktree does not contain the marketplace application')
            return app
    raise RuntimeError('Check out main in a worktree before selecting the main runtime')


def active_identity(inspected):
    result = {}
    for name, container in zip(BACKENDS, inspected):
        environment = dict(value.split('=', 1) for value in container['Config'].get('Env', []) if '=' in value)
        oidc_destination = environment.get('MARKETPLACE_OIDC_CONFIG')
        if not oidc_destination:
            continue
        mounts = {mount['Destination']: mount['Source'] for mount in container.get('Mounts', [])}
        links = mounts.get('/config/ui-identity-links.json')
        oidc = mounts.get(oidc_destination)
        if not oidc or not links:
            raise RuntimeError('Active Keycloak configuration is missing a private file mount')
        result[name] = (Path(oidc), Path(links))
    return result


def runtime_overlay(app, active):
    services = {}
    for name in SERVICES:
        kind = 'backend' if name.endswith('backend') else 'frontend'
        config = {'image': 'marketplace-user-mcp-' + kind,
                  'build': {'context': str(app / kind)}}
        if kind == 'backend':
            config['volumes'] = [str(app / 'backend/marketplace') + ':/app/marketplace:ro']
            port = 5178 if name == 'backend' else 5179
            oidc = STATE / f'ui-login-{port}.json'
            links = STATE / 'ui-identity-links.json'
            identity = active.get(name)
            if identity is None and oidc.exists():
                identity = (oidc, links)
            if identity is not None:
                oidc, links = identity
                if not oidc.is_file() or not links.is_file():
                    raise RuntimeError('Private Keycloak configuration files are unavailable; runtime was not switched')
                config['volumes'].extend([str(oidc) + ':/config/oidc.json:ro',
                                          str(links) + ':/config/ui-identity-links.json:ro'])
                config['environment'] = {'MARKETPLACE_OIDC_CONFIG': '/config/oidc.json'}
            # Callback query strings contain single-use authorization codes.
            config['command'] = ['uvicorn', 'marketplace.api:app', '--host', '0.0.0.0',
                                 '--port', '8000', '--no-access-log']
        services[name] = config
    return {'services': services}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', choices=['branch', 'main'])
    args = parser.parse_args()
    inspected = json.loads(run(['docker', 'inspect', *CONTAINERS],
                               capture_output=True, text=True).stdout)
    if len(inspected) != len(CONTAINERS):
        raise RuntimeError('Both main and Test application backends must exist before switching')
    app = source_app(args.checkout)
    overlay_data = runtime_overlay(app, active_identity(inspected))
    STATE.mkdir(mode=0o700, parents=True, exist_ok=True)
    state_file = STATE / 'app-runtime.json'
    if state_file.exists():
        previous = json.loads(state_file.read_text())
    else:
        labels = inspected[0]['Config']['Labels']
        previous = {'directory': labels['com.docker.compose.project.working_dir'],
                    'compose_files': labels['com.docker.compose.project.config_files'].split(',')}
        state_file.write_text(json.dumps(previous, indent=2) + '\n')
        state_file.chmod(0o600)
    overlay = STATE / 'runtime-overlay.yaml'
    overlay.write_text(json.dumps(overlay_data, indent=2) + '\n')
    overlay.chmod(0o600)
    command = ['docker', 'compose']
    for config in previous['compose_files']:
        command.extend(['-f', config])
    command.extend(['-f', str(overlay)])
    run(command + ['build', 'backend', 'frontend'], cwd=previous['directory'])
    run(command + ['up', '-d', '--no-deps', *SERVICES], cwd=previous['directory'])
    # Recreated backends may receive new IP addresses. Refresh nginx resolution.
    run(command + ['restart', 'frontend', 'memory-frontend'], cwd=previous['directory'])
    print('Marketplace main and Test application services now use ' + args.checkout + ' sources.')


if __name__ == '__main__':
    main()
