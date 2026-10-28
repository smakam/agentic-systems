#!/usr/bin/env python3
"""Coordinate a fresh two-project course deployment; no secrets in configuration.

Default mode checks local inputs only. --deploy is interactive and billable.
Project-specific Terraform copies and checkpoints keep retries from rewinding
an already deployed application. An uncertain agent create is never replayed.
"""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[3]
CLOUD = ROOT / 'app/cloud'
PHASES = ('preflight', 'infrastructure', 'credentials', 'images', 'gateway',
          'initialize', 'gateway-keys', 'application', 'agent-foundation',
          'agent-package', 'agent-deploy', 'connect', 'health')
HOSTS = {'https://cloud.langfuse.com', 'https://us.cloud.langfuse.com',
         'https://jp.cloud.langfuse.com', 'https://hipaa.cloud.langfuse.com'}


def source_fingerprint():
    files = sorted((CLOUD / 'terraform').glob('*.tf')) + sorted((CLOUD / 'bootstrap').glob('*.tf'))
    files += [Path(__file__).resolve(), ROOT / 'app/google/deploy.py', ROOT / 'app/google/requirements.txt']
    files += sorted(CLOUD.glob('Dockerfile.*'))
    files += sorted((CLOUD / 'scripts').glob('*.py')) + sorted((CLOUD / 'scripts').glob('*.sh'))
    # Include actual Docker/package inputs so an application fix cannot reuse
    # an old image tag or silently change a resumed deployment.
    for directory in ('app/backend/marketplace', 'app/frontend/src', 'app/data', 'app/google/marketplace_google'):
        files += [p for p in (ROOT / directory).rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts and p.suffix != '.pyc']
    for name in ('app/.dockerignore', 'app/backend/requirements.txt', 'app/frontend/package.json',
                 'app/frontend/package-lock.json', 'app/frontend/index.html', 'app/frontend/vite.config.js',
                 'app/infra/litellm.yaml', 'app/infra/lakera-guardrail.fragment.yaml', 'app/infra/gateway_audit.py'):
        path = ROOT / name
        if path.exists():
            files.append(path)
    digest = hashlib.sha256()
    for path in sorted(set(files)):
        label = str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else path.name
        digest.update(label.encode() + b'\0' + path.read_bytes() + b'\0')
    return digest.hexdigest()


def configuration(path):
    """Read literal KEY=value lines, never execute a sourced shell file."""
    values = {}
    allowed = {'MARKETPLACE_GCP_PROJECT', 'MARKETPLACE_GCP_REGION',
               'MARKETPLACE_LF_HOST', 'AGENT_GCP_PROJECT', 'AGENT_GCP_REGION',
               'AGENT_STAGING_BUCKET', 'AGENT_RUNTIME_SERVICE_ACCOUNT',
               'AGENT_MCP_SECRET_NAME'}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('export '):
            line = line[7:]
        key, sep, value = line.partition('=')
        if not sep or key not in allowed or key in values:
            raise ValueError('Use one literal assignment per supported configuration key.')
        value = value.strip().strip('"\'')
        if not re.fullmatch(r'[A-Za-z0-9:/_.@-]+', value):
            raise ValueError('Configuration must contain literal references, not shell expressions.')
        values[key] = value
    for key in ('MARKETPLACE_GCP_PROJECT', 'AGENT_GCP_PROJECT'):
        if not re.fullmatch(r'[a-z][a-z0-9-]{4,28}[a-z0-9]', values.get(key, '')):
            raise ValueError(f'Set {key} to your project ID, not its display name.')
    if values['MARKETPLACE_GCP_PROJECT'] == values['AGENT_GCP_PROJECT']:
        raise ValueError('Use two distinct projects for this course setup.')
    for key, default in [('MARKETPLACE_GCP_REGION', 'asia-south1'),
                         ('AGENT_GCP_REGION', 'us-central1')]:
        values.setdefault(key, default)
        if not re.fullmatch(r'[a-z]+-[a-z]+[0-9]', values[key]):
            raise ValueError(f'Invalid region in {key}.')
    values.setdefault('MARKETPLACE_LF_HOST', 'https://cloud.langfuse.com')
    if values['MARKETPLACE_LF_HOST'] not in HOSTS:
        raise ValueError('Select a supported Langfuse regional HTTPS host.')
    agent = values['AGENT_GCP_PROJECT']
    values.setdefault('AGENT_STAGING_BUCKET', f'gs://{agent}-agent-staging')
    values.setdefault('AGENT_RUNTIME_SERVICE_ACCOUNT', f'marketplace-agent@{agent}.iam.gserviceaccount.com')
    values.setdefault('AGENT_MCP_SECRET_NAME', 'marketplace-business-mcp')
    if not re.fullmatch(r'gs://[a-z0-9][a-z0-9.-]{1,220}[a-z0-9]', values['AGENT_STAGING_BUCKET']):
        raise ValueError('Invalid private staging bucket name.')
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,28}[a-z0-9]@' + re.escape(agent) + r'\.iam\.gserviceaccount\.com', values['AGENT_RUNTIME_SERVICE_ACCOUNT']):
        raise ValueError('The runtime service account must belong to the agent project.')
    if not re.fullmatch(r'[A-Za-z0-9_-]{1,255}', values['AGENT_MCP_SECRET_NAME']):
        raise ValueError('Invalid agent MCP secret name.')
    return values


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, indent=2) + '\n')
    temporary.chmod(0o600)
    temporary.replace(path)


class Setup:
    def __init__(self, config, runner=subprocess.run):
        self.c = config
        self.runner = runner
        self.project = config['MARKETPLACE_GCP_PROJECT']
        self.agent = config['AGENT_GCP_PROJECT']
        self.region = config['MARKETPLACE_GCP_REGION']
        self.work = CLOUD / '.setup' / self.project
        self.receipt = self.work / 'progress.json'
        self.state = json.loads(self.receipt.read_text()) if self.receipt.exists() else {
            'config': config, 'completed': [], 'variables': {
                'project_id': self.project, 'region': self.region,
                'database_active': True, 'application_enabled': False,
                'public_web': True, 'public_mcp': True,
                'langfuse_host': config['MARKETPLACE_LF_HOST']}}
        if self.state['config'] != config:
            raise ValueError('Configuration differs from this deployment checkpoint. Restore it before resuming.')
        digest = source_fingerprint()
        if self.state.get('source_digest', digest) != digest:
            raise ValueError('Deployment sources changed since setup began. Review the saved state before continuing.')
        self.state['source_digest'] = digest

    def run(self, args, cwd=None, capture=False, env=None, input=None):
        result = self.runner([str(a) for a in args], cwd=cwd or ROOT,
                             env=env, input=input, text=True,
                             stdout=subprocess.PIPE if capture else None,
                             stderr=subprocess.PIPE if capture else None)
        if result.returncode:
            raise RuntimeError(f'{Path(str(args[0])).name} failed; inspect the named phase. No later phase ran.')
        return result.stdout.strip() if capture else ''

    def gc(self, *args, project=None, capture=True):
        return self.run(['gcloud', *args, f'--project={project or self.project}'], capture=capture)

    def persist(self):
        save(self.receipt, self.state)

    def phase(self, name, action):
        if name in self.state['completed']:
            print(f'Already completed: {name}')
            return
        if self.state.get('uncertain_agent_create') and name == 'agent-deploy' and not (self.work / 'agent/deployment.json').exists():
            raise RuntimeError('Agent creation was interrupted. Inspect the agent project runtime list; do not retry creation. See troubleshooting.')
        print(f'\nSetup phase: {name}', flush=True)
        self.state['current_phase'] = name
        self.persist()
        action()
        self.state['completed'].append(name)
        self.persist()

    def tf(self, directory, *args, capture=False):
        return self.run(['terraform', f'-chdir={self.work / directory}', *args], capture=capture)

    def apply(self, directory='terraform'):
        if directory == 'terraform':
            save(self.work / directory / 'setup.auto.tfvars.json', self.state['variables'])
        self.tf(directory, 'plan', '-input=false', '-out=setup.tfplan')
        # Apply exactly the displayed saved plan. Terraform still asks for approval
        # when no saved plan is supplied; this wrapper has its own target confirmation.
        self.tf(directory, 'apply', '-input=false', 'setup.tfplan')

    def output(self, key):
        value = json.loads(self.tf('terraform', 'output', '-json', key, capture=True))
        if key == 'service_urls' and any(not url for url in value.values()):
            # A failed create followed by a successful in-place revision can
            # leave a computed URI empty in the provider's saved outputs.
            # Refresh-only reconciles state; it does not change cloud resources.
            self.tf('terraform', 'apply', '-refresh-only', '-auto-approve', '-input=false')
            value = json.loads(self.tf('terraform', 'output', '-json', key, capture=True))
            if any(not url for url in value.values()):
                raise RuntimeError('A deployed service URL is unavailable; inspect readiness before provisioning keys.')
        return value

    def preflight(self):
        for executable in ('gcloud', 'terraform', 'docker', 'python3.12'):
            if not shutil.which(executable):
                raise RuntimeError(f'Install {executable} before deployment.')
        version = json.loads(self.run(['terraform', 'version', '-json'], capture=True))['terraform_version']
        parts = tuple(int(p) for p in version.split('.')[:2])
        if not (1, 7) <= parts < (2, 0):
            raise RuntimeError('Terraform must be at least 1.7 and below 2.0.')
        self.run(['docker', 'info'], capture=True)
        self.gc('auth', 'print-access-token')
        self.gc('auth', 'application-default', 'print-access-token')
        for project in (self.project, self.agent):
            info = json.loads(self.gc('projects', 'describe', project, '--format=json', project=project))
            if info.get('lifecycleState') != 'ACTIVE':
                raise RuntimeError('Both projects must be active.')
            billing = json.loads(self.gc('billing', 'projects', 'describe', project, '--format=json', project=project))
            if not billing.get('billingEnabled'):
                raise RuntimeError('Enable billing in both projects before deployment.')
    def infrastructure(self):
        # Enable discovery before checking for an existing stack. API enablement
        # alone creates no compute instance and never starts Cloud SQL.
        if not self.state.get('fresh_project_checked'):
            self.gc('services', 'enable', 'run.googleapis.com', 'sqladmin.googleapis.com')
            services = json.loads(self.gc('run', 'services', 'list', f'--region={self.region}', '--format=json'))
            databases = json.loads(self.gc('sql', 'instances', 'list', '--format=json'))
            if any('marketplace-' in row.get('metadata', {}).get('name', '') for row in services) or any(row.get('name') == 'marketplace-postgres' for row in databases):
                raise RuntimeError('Marketplace resources already exist. Use a fresh project; this installer does not adopt instructor resources.')
            self.state['fresh_project_checked'] = True
            self.persist()
        for directory in ('bootstrap', 'terraform'):
            target = self.work / directory
            target.mkdir(parents=True, exist_ok=True)
            for source in (CLOUD / directory).glob('*.tf'):
                shutil.copy2(source, target / source.name)
        save(self.work / 'bootstrap/setup.auto.tfvars.json', {'project_id': self.project, 'region': self.region})
        self.tf('bootstrap', 'init', '-input=false')
        self.apply('bootstrap')
        self.tf('terraform', 'init', '-input=false',
                f'-backend-config=bucket={self.project}-tfstate', '-backend-config=prefix=marketplace')
        self.apply()

    def credentials(self):
        self.run([sys.executable, CLOUD / 'scripts/configure-cloud.py', '--project', self.project, '--region', self.region])
        public = self.work / 'langfuse-public.env'
        if not public.exists():
            self.run(['bash', CLOUD / 'scripts/configure-langfuse.sh'], cwd=self.work,
                     env={**os.environ, **self.c})
        values = dict(line.split('=', 1) for line in public.read_text().splitlines())
        if values.get('LANGFUSE_HOST') != self.c['MARKETPLACE_LF_HOST']:
            raise RuntimeError('Langfuse public configuration host does not match setup configuration.')
        self.state['variables']['langfuse_public_key'] = values['LANGFUSE_PUBLIC_KEY']
        # The local seeded project slug is not the hosted project's ID. Resolve
        # it with the matching project keys, without adding another learner input.
        key = self.gc('secrets', 'versions', 'access', 'latest', '--secret=marketplace-web-langfuse-secret')
        authorization = base64.b64encode((values['LANGFUSE_PUBLIC_KEY'] + ':' + key).encode()).decode()
        request = urllib.request.Request(values['LANGFUSE_HOST'] + '/api/public/projects',
                                         headers={'Authorization': 'Basic ' + authorization})
        with urllib.request.urlopen(request, timeout=30) as response:
            projects = json.load(response)['data']
        if len(projects) != 1 or not re.fullmatch(r'[A-Za-z0-9_-]+', projects[0].get('id', '')):
            raise RuntimeError('Tracing keys must identify one Langfuse project.')
        self.state['langfuse_project_id'] = projects[0]['id']

    def images(self):
        repo = self.output('image_repository')
        self.gc('auth', 'configure-docker', f'{self.region}-docker.pkg.dev', '--quiet', capture=False)
        for image in ('web', 'gateway'):
            tag = f'{repo}/{image}:setup-{self.state["source_digest"][:12]}'
            command = ['docker', 'build', '--platform', 'linux/amd64', '-f', CLOUD / f'Dockerfile.{image}', '-t', tag]
            if image == 'web':
                command += ['--build-arg', f'VITE_LANGFUSE_URL={self.c["MARKETPLACE_LF_HOST"]}',
                            '--build-arg', f'VITE_LANGFUSE_PROJECT_ID={self.state["langfuse_project_id"]}']
            self.run([*command, ROOT / 'app'])
            self.run(['docker', 'push', tag])
            self.state['variables'][f'{image}_image'] = tag
        self.persist()

    def gateway(self):
        self.apply()

    def initialize(self):
        # initialize.py preserves existing records; no reset or fixture-copy helper.
        self.gc('run', 'jobs', 'execute', 'marketplace-initialize', f'--region={self.region}', '--wait', capture=False)

    def gateway_keys(self):
        self.run([sys.executable, CLOUD / 'scripts/configure-gateway-keys.py', '--project', self.project,
                  '--gateway', self.output('service_urls')['gateway']])

    def application(self):
        self.state['variables']['application_enabled'] = True
        self.apply()
        self.state['urls'] = self.output('service_urls')

    def generate_service_identity(self, number):
        # Use the official API so an uninstalled gcloud beta component cannot
        # leave an invisible install prompt inside captured command output.
        token = self.gc('auth', 'print-access-token')
        base = 'https://serviceusage.googleapis.com/v1beta1/'
        request = urllib.request.Request(
            base + f'projects/{number}/services/aiplatform.googleapis.com:generateServiceIdentity',
            data=b'', method='POST', headers={'Authorization': 'Bearer ' + token})
        with urllib.request.urlopen(request, timeout=60) as response:
            operation = json.load(response)
        deadline = time.monotonic() + 600
        while not operation.get('done'):
            if time.monotonic() > deadline:
                raise RuntimeError('Agent service identity preparation timed out; inspect Service Usage operations.')
            time.sleep(2)
            request = urllib.request.Request(base + operation['name'], headers={'Authorization': 'Bearer ' + token})
            with urllib.request.urlopen(request, timeout=60) as response:
                operation = json.load(response)
        if operation.get('error'):
            raise RuntimeError('Agent service identity preparation failed; inspect Service Usage operations.')

    def agent_foundation(self):
        project = self.agent
        self.gc('services', 'enable', 'aiplatform.googleapis.com', 'iam.googleapis.com',
                'secretmanager.googleapis.com', 'storage.googleapis.com', 'cloudresourcemanager.googleapis.com',
                'logging.googleapis.com', 'monitoring.googleapis.com', 'cloudtrace.googleapis.com', 'telemetry.googleapis.com', project=project)
        number = self.gc('projects', 'describe', project, '--format=value(projectNumber)', project=project)
        self.state['agent_number'] = number
        self.generate_service_identity(number)
        sa = self.c['AGENT_RUNTIME_SERVICE_ACCOUNT']
        accounts = json.loads(self.gc('iam', 'service-accounts', 'list', '--format=json', project=project))
        if not any(a.get('email') == sa for a in accounts):
            self.gc('iam', 'service-accounts', 'create', sa.split('@')[0], project=project)
        for role in ('roles/aiplatform.user', 'roles/logging.logWriter', 'roles/monitoring.metricWriter', 'roles/cloudtrace.agent'):
            self.gc('projects', 'add-iam-policy-binding', project, f'--member=serviceAccount:{sa}', f'--role={role}', '--condition=None', project=project)
        deployer = self.gc('config', 'get-value', 'account')
        if not deployer or '@' not in deployer:
            raise RuntimeError('Select an authenticated deployment account in gcloud.')
        principal = ('serviceAccount:' if deployer.endswith('.gserviceaccount.com') else 'user:') + deployer
        self.gc('iam', 'service-accounts', 'add-iam-policy-binding', sa,
                f'--member={principal}', '--role=roles/iam.serviceAccountUser', '--condition=None', project=project)
        bucket = self.c['AGENT_STAGING_BUCKET']
        buckets = json.loads(self.gc('storage', 'buckets', 'list', '--format=json', project=project))
        if not any(b.get('name') == bucket[5:] or b.get('storage_url') == bucket for b in buckets):
            self.gc('storage', 'buckets', 'create', bucket, f'--location={self.c["AGENT_GCP_REGION"]}',
                    '--uniform-bucket-level-access', '--public-access-prevention', project=project)
        self.gc('storage', 'buckets', 'add-iam-policy-binding', bucket, f'--member=serviceAccount:{sa}', '--role=roles/storage.objectViewer', project=project)
        self.gc('storage', 'buckets', 'add-iam-policy-binding', bucket,
                f'--member={principal}', '--role=roles/storage.admin', project=project)
        # Injected secrets must belong to the runtime's project. Copy the
        # generated MCP credential privately, never through argv or TF state.
        name = self.c['AGENT_MCP_SECRET_NAME']
        secrets = json.loads(self.gc('secrets', 'list', '--format=json', project=project))
        if not any(item.get('name', '').endswith('/secrets/' + name) for item in secrets):
            self.gc('secrets', 'create', name, '--replication-policy=automatic', project=project)
        credential = self.gc('secrets', 'versions', 'access', 'latest', '--secret=marketplace-mcp-api-key')
        versions = json.loads(self.gc('secrets', 'versions', 'list', name,
                                     '--filter=state:ENABLED', '--format=json', project=project))
        current = self.gc('secrets', 'versions', 'access', 'latest', '--secret=' + name, project=project) if versions else None
        if current != credential:
            self.run(['gcloud', 'secrets', 'versions', 'add', name, '--data-file=-', '--project=' + project],
                     input=credential, capture=True)
        self.gc('secrets', 'add-iam-policy-binding', name, f'--member=serviceAccount:{sa}',
                '--role=roles/secretmanager.secretAccessor', '--condition=None', project=project)
        version = json.loads(self.gc('secrets', 'versions', 'describe', 'latest', '--secret=' + name,
                                    '--format=json', project=project))
        self.state['mcp_secret_version'] = version['name'].split('/')[-1]
        self.persist()

    def agent_package(self):
        target = self.work / 'agent'
        target.mkdir(exist_ok=True)
        for filename in ('deploy.py', 'requirements.txt', 'backend_profiles.py', 'test_agent.py'):
            shutil.copy2(ROOT / 'app/google' / filename, target / filename)
        shutil.copytree(ROOT / 'app/google/marketplace_google', target / 'marketplace_google', dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        self.run(['python3.12', '-m', 'venv', target / '.venv'])
        python = target / '.venv/bin/python'
        self.run([python, '-m', 'pip', 'install', '-r', 'requirements.txt'], cwd=target)
        self.run([python, '-m', 'unittest', 'test_agent', '-v'], cwd=target)

    def agent_deploy(self):
        target = self.work / 'agent'
        manifest = target / 'deployment.json'
        if manifest.exists():
            data = json.loads(manifest.read_text())
            expected = f'projects/{self.state["agent_number"]}/locations/{self.c["AGENT_GCP_REGION"]}/reasoningEngines/'
            if (not data.get('resource_name', '').startswith(expected)
                    or data.get('mcp_url') != self.state['urls']['mcp'] + '/mcp'
                    or data.get('project') != self.agent
                    or data.get('mcp_secret') != f'projects/{self.agent}/secrets/{self.c["AGENT_MCP_SECRET_NAME"]}'
                    or data.get('mcp_secret_version') != self.state['mcp_secret_version']):
                raise RuntimeError('Agent manifest does not match the intended project and MCP endpoint.')
            self.state['runtime'] = data['resource_name']
            self.state['uncertain_agent_create'] = False
            return
        env = {k: v for k, v in os.environ.items() if not k.startswith(('GOOGLE_', 'REMOTE_MCP_', 'BACKEND_PROFILE_'))}
        env.update({'GOOGLE_GENAI_USE_ENTERPRISE': 'TRUE', 'GOOGLE_CLOUD_PROJECT': self.agent,
                    'GOOGLE_CLOUD_LOCATION': self.c['AGENT_GCP_REGION'],
                    'GOOGLE_STAGING_BUCKET': self.c['AGENT_STAGING_BUCKET'],
                    'GOOGLE_RUNTIME_SERVICE_ACCOUNT': self.c['AGENT_RUNTIME_SERVICE_ACCOUNT'],
                    'GOOGLE_MCP_SECRET': f'projects/{self.agent}/secrets/{self.c["AGENT_MCP_SECRET_NAME"]}',
                    'GOOGLE_MCP_SECRET_VERSION': self.state['mcp_secret_version'],
                    'REMOTE_MCP_URL': self.state['urls']['mcp'] + '/mcp'})
        self.state['uncertain_agent_create'] = True
        self.persist()
        self.run([target / '.venv/bin/python', 'deploy.py'], cwd=target, env=env)
        self.state['uncertain_agent_create'] = False
        self.agent_deploy()

    def connect(self):
        self.state['variables'].update(google_runtime_project_id=self.agent, google_runtime_resource=self.state['runtime'])
        self.apply()

    def health(self):
        url = self.state['urls']['web']
        with urllib.request.urlopen(url + '/api/health', timeout=90) as response:
            if json.load(response).get('status') != 'ok':
                raise RuntimeError('Web health check did not pass.')
        save(self.work / 'result.json', {'projects': [self.project, self.agent],
             'urls': self.state['urls'], 'runtime': self.state['runtime'],
             'health': 'passed', 'live_agent_acceptance': 'pending'})
        print('Web health passed. Complete the live acceptance checklist in the Cloud Setup guide.')
        print('Marketplace: ' + url)

    def deploy(self):
        # Require identity confirmation on every invocation, including resume.
        if input(f'Deploy billable resources in {self.project} and {self.agent}? Type both IDs separated by a space: ').strip() != f'{self.project} {self.agent}':
            raise RuntimeError('Targets not confirmed; nothing deployed.')
        self.work.mkdir(parents=True, exist_ok=True, mode=0o700)
        lock = self.work / 'setup.lock'
        try:
            descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        except FileExistsError:
            raise RuntimeError('Setup lock exists. Check that no setup process is running before removing it.') from None
        try:
            os.close(descriptor)
            for name in PHASES:
                self.phase(name, getattr(self, name.replace('-', '_')))
        finally:
            lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=CLOUD / '.env')
    parser.add_argument('--deploy', action='store_true', help='Create billable resources after target confirmation; resume completed phases safely.')
    args = parser.parse_args()
    try:
        config = configuration(args.config)
        setup = Setup(config)
        if args.deploy:
            setup.deploy()
        else:
            print('Configuration valid. No network calls or resource changes performed.')
            print('Projects: ' + config['MARKETPLACE_GCP_PROJECT'] + ' / ' + config['AGENT_GCP_PROJECT'])
            print('Deployment phases: ' + ' -> '.join(PHASES))
            missing = [name for name in ('gcloud', 'terraform', 'docker', 'python3.12') if not shutil.which(name)]
            if missing:
                print('Install before deploying: ' + ', '.join(missing))
            print('Configuration checks do not prove live behavior. Complete the Cloud Setup acceptance checklist for your installation.')
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        print(f'Setup stopped: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
