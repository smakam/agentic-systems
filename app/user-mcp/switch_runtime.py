#!/usr/bin/env python3
"""Switch existing marketplace UI/API containers between this checkout and main.

Preserve the active Compose configuration, environment and database services.
Only the four main/Test frontend and backend services are recreated.
"""

import argparse
import json
from pathlib import Path
import subprocess

APP = Path(__file__).resolve().parents[1]
STATE = APP / '.user-mcp'
SERVICES = ['backend', 'frontend', 'memory-backend', 'memory-frontend']


def run(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('checkout', choices=['branch', 'main'])
    args = parser.parse_args()
    state_file = STATE / 'app-runtime.json'
    if state_file.exists():
        previous = json.loads(state_file.read_text())
    else:
        inspected = run(['docker', 'inspect', 'marketplace-lab-backend-1'],
                        capture_output=True, text=True)
        labels = json.loads(inspected.stdout)[0]['Config']['Labels']
        previous = {
            'directory': labels['com.docker.compose.project.working_dir'],
            'compose_files': labels['com.docker.compose.project.config_files'].split(','),
        }
        state_file.write_text(json.dumps(previous, indent=2) + '\n')
    command = ['docker', 'compose']
    for config in previous['compose_files']:
        command.extend(['-f', config])
    if args.checkout == 'branch':
        branch_services = {}
        for name in SERVICES:
            kind = 'backend' if name.endswith('backend') else 'frontend'
            config = {
                'image': 'marketplace-user-mcp-' + kind,
                'build': {'context': str(APP / kind)},
            }
            if kind == 'backend':
                config['volumes'] = [str(APP / 'backend/marketplace') + ':/app/marketplace:ro']
                port = 5178 if name == 'backend' else 5179
                oidc_config = STATE / f'ui-login-{port}.json'
                if oidc_config.exists():
                    config['volumes'].extend([str(oidc_config) + ':/config/oidc.json:ro',
                                              str(STATE / 'ui-identity-links.json') + ':/config/ui-identity-links.json:ro'])
                    config['environment'] = {'MARKETPLACE_OIDC_CONFIG': '/config/oidc.json'}
                # OAuth callback query strings contain single-use authorization codes.
                config['command'] = ['uvicorn', 'marketplace.api:app', '--host', '0.0.0.0', '--port', '8000', '--no-access-log']
            branch_services[name] = config
        overlay = STATE / 'branch-runtime.yaml'
        overlay.write_text(json.dumps({'services': branch_services}, indent=2) + '\n')
        command.extend(['-f', str(overlay)])
        run(command + ['build', 'backend', 'frontend'], cwd=previous['directory'])
    run(command + ['up', '-d', '--no-deps', *SERVICES], cwd=previous['directory'])
    # Nginx resolves backend names at startup. Recreated backends can receive
    # different addresses even when an unchanged frontend image stays running.
    run(command + ['restart', 'frontend', 'memory-frontend'], cwd=previous['directory'])
    print('Marketplace main and Test application services now use ' + args.checkout + ' runtime configuration.')


if __name__ == '__main__':
    main()
