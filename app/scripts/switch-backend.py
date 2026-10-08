#!/usr/bin/env python3
"""Select the saved business backend for the existing Google and Lyzr lab agents."""
import argparse
import copy
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from urllib.parse import urlsplit

HERE = Path(__file__).resolve().parent
ACTIONS = {'begin_investigation', 'end_investigation', 'get_catalog',
           'query_business_data', 'search_documents', 'fetch_evidence', 'get_order_history'}
# AgentConfig fields from Lyzr's public OpenAPI. Preserve each current setting.
AGENT_FIELDS = set('name description agent_role agent_instructions agent_goal agent_context agent_output examples features tools tool_usage_description llm_credential_id response_format provider_id model top_p temperature managed_agents tool_configs store_messages file_output disable_artifacts jev_tool_shortlisting a2a_tools voice_config additional_model_params auto_routing image_output_config max_iterations git_agent proxy_config skills_catalog mcp_resources mcp_prompts a2a_card custom_tags custom_metadata is_active'.split())


def request(url, headers, method='GET', payload=None):
    body = None if payload is None else json.dumps(payload).encode()
    req = urllib.request.Request(url, data=body, method=method,
                                headers={**headers, 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.load(response)
    except urllib.error.HTTPError as exc:
        # Response bodies can contain credentials or serialized agent instructions.
        raise RuntimeError(f'{urlsplit(url).hostname}: HTTP {exc.code}; response body withheld.') from None
    except (OSError, ValueError):
        raise RuntimeError(f'{urlsplit(url).hostname}: request failed; inspect connectivity and access.') from None


def load_config(path):
    config = json.loads(Path(path).read_text())
    if not re.fullmatch(r'projects/\d+/locations/[a-z0-9-]+/reasoningEngines/\d+', config['google_runtime']):
        raise ValueError('Invalid Google runtime resource.')
    if not re.fullmatch(r'[a-f0-9]{24}', config['lyzr_agent']):
        raise ValueError('Invalid Lyzr agent ID.')
    for name in ('local', 'cloud'):
        p = config['profiles'][name]
        u = urlsplit(p['url'])
        if u.scheme != 'https' or not u.hostname or u.username or u.password or u.query or u.fragment or u.path != '/mcp':
            raise ValueError('Expected HTTPS MCP endpoint without credentials or query.')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', p['google_secret']) or not str(p['google_secret_version']).isdigit():
            raise ValueError('Expected short Google secret name and pinned numeric version.')
        if not re.fullmatch(r'[a-f0-9]{24}', p['lyzr_server']):
            raise ValueError('Invalid saved Lyzr MCP server ID.')
    return config


def lyzr_key(env_file):
    key = os.environ.get('LYZR_API_KEY')
    if not key and Path(env_file).exists():
        for line in Path(env_file).read_text().splitlines():
            if line.startswith('LYZR_API_KEY='):
                parts = shlex.split(line.split('=', 1)[1], comments=True)
                key = parts[0] if parts else ''
    if not key:
        try:
            result = subprocess.run(['gcloud', 'secrets', 'versions', 'access', 'latest',
                '--secret=marketplace-web-lyzr-api-key', '--project=marketplace-app-511005'],
                capture_output=True, text=True, check=True)
            key = result.stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            pass
    if not key:
        raise RuntimeError('LYZR_API_KEY is required; use the existing inference credential, not an MCP key.')
    return key


def google_headers():
    if shutil.which('gcloud'):
        command = ['gcloud', 'auth', 'print-access-token']
    elif (HERE.parent / '.google-auth/application_default_credentials.json').exists():
        command = ['docker', 'run', '--rm', '--pull=never', '-v',
                   str(HERE.parent / '.google-auth') + ':/root/.config/gcloud:ro',
                   'gcr.io/google.com/cloudsdktool/google-cloud-cli:stable',
                   'gcloud', 'auth', 'application-default', 'print-access-token']
    else:
        raise RuntimeError('Google login is required: authenticated Cloud Shell, or the existing local ADC/Google CLI container.')
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True, timeout=120)
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
        raise RuntimeError('Google token acquisition failed. Check Cloud Shell login or local Docker/ADC access.') from None
    return {'Authorization': 'Bearer ' + result.stdout.strip()}


def google_pair(agent):
    d = agent['spec']['deploymentSpec']
    env = {v['name']: v.get('value') for v in d.get('env', [])}
    secrets = {v['name']: v.get('secretRef') for v in d.get('secretEnv', [])}
    return env.get('REMOTE_MCP_URL'), secrets.get('REMOTE_MCP_API_KEY')


def desired_pair(profile):
    return profile['url'], {'secret': profile['google_secret'], 'version': str(profile['google_secret_version'])}


def google_patch(agent, profile):
    d = agent['spec']['deploymentSpec']
    env = [copy.deepcopy(v) for v in d.get('env', []) if v['name'] != 'REMOTE_MCP_URL']
    secret_env = [copy.deepcopy(v) for v in d.get('secretEnv', []) if v['name'] != 'REMOTE_MCP_API_KEY']
    env.append({'name': 'REMOTE_MCP_URL', 'value': profile['url']})
    secret_env.append({'name': 'REMOTE_MCP_API_KEY', 'secretRef': desired_pair(profile)[1]})
    body = {'name': agent['name'], 'spec': {'deploymentSpec': {'env': env, 'secretEnv': secret_env}}}
    if agent.get('etag'):
        body['etag'] = agent['etag']
    return body


def lyzr_patch(agent, servers, config, profile):
    connections = [t for t in agent.get('tool_configs', [])
                   if t.get('server_id') in {p['lyzr_server'] for p in config['profiles'].values()}]
    if len(connections) != 1 or set(connections[0]['action_names']) != ACTIONS:
        raise RuntimeError('Expected exactly one known marketplace MCP attachment with all seven actions. Nothing changed.')
    server = next((s for s in servers if s['id'] == profile['lyzr_server']), None)
    if not server or server['server_url'] != profile['url'] or server['auth_type'] != 'api_key':
        raise RuntimeError('Saved Lyzr connection does not match the selected URL/authentication. Nothing changed.')
    body = {k: copy.deepcopy(v) for k, v in agent.items() if k in AGENT_FIELDS}
    target = next(t for t in body['tool_configs'] if t.get('server_id') == connections[0]['server_id'])
    old_name = target['tool_name']
    target.update(server_id=server['id'], tool_name=server['name'])
    body['tools'] = [server['name'] if name == old_name else name for name in body.get('tools', [])]
    if any(item.get('server_id') == connections[0]['server_id']
           for field in ('mcp_resources', 'mcp_prompts') for item in body.get(field) or []):
        raise RuntimeError('Marketplace connection has resources/prompts; review their mapping before switching.')
    return body, connections[0]['server_id'] == server['id']


def save_receipt(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(value, indent=2) + '\n')
    tmp.chmod(0o600)
    tmp.replace(path)


def run(args):
    config = load_config(args.config)
    p = config['profiles'][args.backend]
    print(f'Backend: {args.backend}; MCP: {p["url"]}')
    print('Targets: existing Google ADK lab and Lyzr support agent. SDK remains environment-bound.')
    print('Shared hosted agents affect local and cloud callers. Use a fresh chat after switching.')
    if args.plan:
        print('Plan only: select saved Google secret reference and saved Lyzr MCP connection; no keys copied.')
        return 0
    endpoint = f'https://{config["google_runtime"].split("/")[3]}-aiplatform.googleapis.com/v1/'
    print('Checking Google login and current settings...', flush=True)
    gh = google_headers()
    lh = {'x-api-key': lyzr_key(args.env_file)}
    lu = 'https://agent-prod.studio.lyzr.ai/v3/'
    gu = endpoint + config['google_runtime']
    if args.apply and args.receipt.exists():
        previous = json.loads(args.receipt.read_text())
        if previous.get('google') == 'update submitted':
            op = request(endpoint + previous['google_operation'], gh)
            if not op.get('done'):
                raise RuntimeError('A previous Google switch is still pending. Wait for its operation before applying another switch.')
    ga = request(gu, gh)
    print('Checking Lyzr agent and saved MCP connections...', flush=True)
    la = request(lu + 'agents/' + config['lyzr_agent'], lh)
    servers = request(lu + 'tools/mcp/servers', lh)['servers']
    if args.apply:
        deployed_env = {v['name']: v.get('value') for v in ga['spec']['deploymentSpec'].get('env', [])}
        if deployed_env.get('BACKEND_PROFILE_CONFIG_VERSION') != 'runtime-url-v1':
            raise RuntimeError('Google agent requires the runtime-resolved MCP repair deployment before environment-only switching.')
    body, lyzr_matches = lyzr_patch(la, servers, config, p)
    google_matches = google_pair(ga) == desired_pair(p)
    print(f'Google: {"matches" if google_matches else "different backend"}; Lyzr: {"matches" if lyzr_matches else "different backend"}')
    if not args.apply:
        return 0 if google_matches and lyzr_matches else 1
    # Discover the saved connection before making either mutation. Lyzr uses its retained key.
    print('Discovering actions on the selected MCP connection...', flush=True)
    tools = request(lu + 'tools/mcp/servers/' + p['lyzr_server'] + '/tools', lh)
    available = {t['name'] for t in tools['tools']}
    if not ACTIONS <= available:
        raise RuntimeError('Selected Lyzr MCP connection did not discover all seven required actions. Nothing changed.')
    receipt = {'backend': args.backend, 'url': p['url'], 'google': 'unchanged', 'lyzr': 'unchanged', 'verified': False}
    save_receipt(args.receipt, receipt)
    try:
        if not google_matches:
            operation = request(gu + '?updateMask=spec.deployment_spec.env,spec.deployment_spec.secret_env',
                                gh, 'PATCH', google_patch(ga, p))
            receipt.update(google='update submitted', google_operation=operation['name'])
            save_receipt(args.receipt, receipt)
            print('Google update submitted. Waiting for deployment; this can take several minutes. Lyzr remains unchanged until Google completes.', flush=True)
            started = time.monotonic()
            next_report = started + 30
            deadline = started + args.timeout
            while not operation.get('done'):
                if time.monotonic() >= deadline:
                    raise RuntimeError('Google update is still pending. Check the operation in the receipt before retrying.')
                time.sleep(10)
                operation = request(endpoint + receipt['google_operation'], google_headers())
                now = time.monotonic()
                if not operation.get('done') and now >= next_report:
                    print(f'Google deployment still running ({int(now - started)} seconds elapsed). No Lyzr update yet.', flush=True)
                    next_report = now + 30
            if operation.get('error'):
                raise RuntimeError('Google rejected the update. Inspect the operation; Lyzr was not changed.')
            ga = request(gu, google_headers())
            if google_pair(ga) != desired_pair(p):
                raise RuntimeError('Google update completed but target readback did not match; Lyzr was not changed.')
            print('Google deployment completed and its local/cloud settings verified.', flush=True)
            receipt['google'] = 'verified'
            save_receipt(args.receipt, receipt)
        if not lyzr_matches:
            print('Google is ready. Updating Lyzr to the matching saved MCP connection...', flush=True)
            latest = request(lu + 'agents/' + config['lyzr_agent'], lh)
            if latest != la:
                raise RuntimeError('Lyzr configuration changed during Google update. Re-run to preserve its latest settings.')
            request(lu + 'agents/' + config['lyzr_agent'], lh, 'PUT', body)
            receipt['lyzr'] = 'update submitted'
            save_receipt(args.receipt, receipt)
        check = request(lu + 'agents/' + config['lyzr_agent'], lh)
        if any(check.get(k) != v for k, v in body.items()):
            raise RuntimeError('Lyzr settings readback did not match the preserved configuration.')
        ga = request(gu, google_headers())
        if google_pair(ga) != desired_pair(p):
            raise RuntimeError('Final Google readback did not match.')
        receipt.update(google='verified', lyzr='verified', verified=True)
        save_receipt(args.receipt, receipt)
        print('Both hosted backend configurations verified. Start a fresh conversation and run a business question/follow-up before recording.')
        return 0
    except Exception:
        save_receipt(args.receipt, receipt)
        print('Switch is not atomic; inspect the receipt for completed/pending steps. No automatic rollback.', file=sys.stderr)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('backend', choices=('local', 'cloud'))
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument('--plan', action='store_true', help='Show targets without network access or mutations.')
    modes.add_argument('--apply', action='store_true', help='Update both existing hosted agents and verify settings.')
    parser.add_argument('--config', type=Path, default=HERE / 'backend-switch-profiles.json')
    parser.add_argument('--env-file', type=Path, default=HERE.parent / '.env')
    parser.add_argument('--receipt', type=Path, default=HERE.parent / '.backend-switch/last-switch.json')
    parser.add_argument('--timeout', type=int, default=900, help='Google deployment wait limit in seconds.')
    args = parser.parse_args()
    try:
        return run(args)
    except (RuntimeError, ValueError, KeyError, OSError) as exc:
        print(f'Backend switch failed: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
