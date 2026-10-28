"""Offline installer safety tests. These never contact cloud services."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('cloud_setup', Path(__file__).resolve().parents[1] / 'scripts/setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)

CONFIG = '''export MARKETPLACE_GCP_PROJECT=course-market-test
export AGENT_GCP_PROJECT=course-agent-test
export MARKETPLACE_LF_HOST=https://cloud.langfuse.com
'''


class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.cloud = self.root / 'app/cloud'
        for directory in ('terraform', 'bootstrap', 'scripts'):
            (self.cloud / directory).mkdir(parents=True)
        google = self.root / 'app/google'
        google.mkdir()
        (google / 'marketplace_google').mkdir()
        for name in ('deploy.py', 'requirements.txt', 'backend_profiles.py', 'test_agent.py'):
            (google / name).write_text('')
        self.config = self.root / 'config.env'
        self.config.write_text(CONFIG)
        self.patches = [patch.object(setup, 'ROOT', self.root), patch.object(setup, 'CLOUD', self.cloud)]
        for p in self.patches:
            p.start()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        self.temp.cleanup()

    def installer(self, runner=None):
        return setup.Setup(setup.configuration(self.config), runner=runner or subprocess.run)

    def test_rejects_shell_payload_without_executing_it(self):
        marker = self.root / 'unsafe'
        self.config.write_text(CONFIG + f'export AGENT_STAGING_BUCKET=$(touch {marker})\n')
        with self.assertRaises(ValueError):
            setup.configuration(self.config)
        self.assertFalse(marker.exists())

    def test_rejects_same_project_or_wrong_runtime_identity(self):
        for contents in (CONFIG.replace('course-agent-test', 'course-market-test'),
                         CONFIG + 'AGENT_RUNTIME_SERVICE_ACCOUNT=runtime@other-project.iam.gserviceaccount.com\n'):
            self.config.write_text(contents)
            with self.assertRaises(ValueError):
                setup.configuration(self.config)

    def test_failure_stops_later_phases_and_resume_does_not_rewind(self):
        calls = []
        def actions(installer, failing=None):
            for phase in setup.PHASES:
                def action(name=phase):
                    calls.append(name)
                    if name == failing:
                        raise RuntimeError('simulated deployment failure')
                setattr(installer, phase.replace('-', '_'), action)
        installer = self.installer()
        actions(installer, 'gateway')
        confirmation = 'course-market-test course-agent-test'
        with patch('builtins.input', return_value=confirmation), self.assertRaises(RuntimeError):
            installer.deploy()
        self.assertEqual(calls, list(setup.PHASES[:5]))
        self.assertFalse((installer.work / 'setup.lock').exists())
        calls.clear()
        resumed = self.installer()
        actions(resumed)
        with patch('builtins.input', return_value=confirmation):
            resumed.deploy()
        self.assertEqual(calls, list(setup.PHASES[4:]))
        self.assertEqual(resumed.state['completed'], list(setup.PHASES))

    def test_target_or_source_change_cannot_reuse_checkpoint(self):
        installer = self.installer()
        installer.persist()
        self.config.write_text(CONFIG.replace('course-agent-test', 'different-agent-project'))
        with self.assertRaises(ValueError):
            self.installer()
        self.config.write_text(CONFIG)
        (self.cloud / 'terraform/main.tf').write_text('# changed infrastructure')
        with self.assertRaises(ValueError):
            self.installer()

    def test_uncertain_agent_creation_cannot_be_blindly_replayed(self):
        installer = self.installer()
        installer.state['uncertain_agent_create'] = True
        with self.assertRaises(RuntimeError):
            installer.phase('agent-deploy', lambda: self.fail('must not create'))

    def test_existing_agent_manifest_requires_matching_project_and_endpoint(self):
        commands = []
        def runner(args, **kwargs):
            commands.append(args)
            self.fail('Existing manifest should not create a runtime')
        installer = self.installer(runner)
        installer.state.update(agent_number='123456789', urls={'mcp': 'https://mcp.example.run.app'}, mcp_secret_version='1')
        target = installer.work / 'agent/deployment.json'
        setup.save(target, {'resource_name': 'projects/123456789/locations/us-central1/reasoningEngines/456',
                            'project': 'course-agent-test', 'location': 'us-central1',
                            'mcp_url': 'https://mcp.example.run.app/mcp',
                            'mcp_secret': 'projects/course-market-test/secrets/marketplace-mcp-api-key',
                            'mcp_secret_version': '1'})
        installer.agent_deploy()
        self.assertEqual(installer.state['runtime'].split('/')[-1], '456')
        data = json.loads(target.read_text())
        data['mcp_url'] = 'https://wrong.example.run.app/mcp'
        setup.save(target, data)
        with self.assertRaises(RuntimeError):
            installer.agent_deploy()
        self.assertEqual(commands, [])

    def test_command_errors_do_not_echo_captured_secrets(self):
        def runner(args, **kwargs):
            return subprocess.CompletedProcess(args, 1, stdout='private-token', stderr='private-password')
        installer = self.installer(runner)
        with self.assertRaises(RuntimeError) as caught:
            installer.run(['gcloud', 'auth', 'print-access-token'], capture=True)
        self.assertNotIn('private-', str(caught.exception))

    def test_full_command_sequence_uses_derived_outputs_and_no_inherited_runtime(self):
        commands = []
        urls = {'web': 'https://web.example.run.app', 'mcp': 'https://mcp.example.run.app', 'gateway': 'https://gateway.example.run.app'}
        def runner(args, **kwargs):
            commands.append(args)
            output = ''
            if args[:3] == ['terraform', 'version', '-json']:
                output = '{"terraform_version":"1.9.8"}'
            elif args[0] == 'terraform' and 'output' in args:
                output = json.dumps(urls if args[-1] == 'service_urls' else 'asia-south1-docker.pkg.dev/course-market-test/marketplace')
            elif args[0] == 'gcloud':
                if 'billing' in args:
                    output = '{"billingEnabled":true}'
                elif 'projects' in args and 'describe' in args:
                    output = '123456789' if '--format=value(projectNumber)' in args else '{"lifecycleState":"ACTIVE"}'
                elif 'list' in args:
                    output = '[]'
                elif 'config' in args:
                    output = 'learner@example.com'
                elif 'versions' in args and 'describe' in args:
                    output = '{"name":"projects/course-market-test/secrets/marketplace-mcp-api-key/versions/1"}'
            if any(str(a).endswith('configure-langfuse.sh') for a in args):
                (Path(kwargs['cwd']) / 'langfuse-public.env').write_text('LANGFUSE_HOST=https://cloud.langfuse.com\nLANGFUSE_PUBLIC_KEY=pk-lf-test\n')
            if args[-1] == 'deploy.py':
                env = kwargs['env']
                self.assertNotIn('GOOGLE_RUNTIME_RESOURCE', env)
                setup.save(Path(kwargs['cwd']) / 'deployment.json', {
                    'resource_name': 'projects/123456789/locations/us-central1/reasoningEngines/456',
                    'project': env['GOOGLE_CLOUD_PROJECT'], 'mcp_url': env['REMOTE_MCP_URL'],
                    'mcp_secret': env['GOOGLE_MCP_SECRET'], 'mcp_secret_version': env['GOOGLE_MCP_SECRET_VERSION']})
            return subprocess.CompletedProcess(args, 0, stdout=output, stderr='')
        installer = self.installer(runner)
        # Only the HTTP health response is mocked; all installer phases execute.
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return b'{"status":"ok","data":[{"id":"hosted-trace-project"}]}'
        with patch('builtins.input', return_value='course-market-test course-agent-test'), patch.object(setup.shutil, 'which', return_value='/fake/tool'), patch.object(setup.urllib.request, 'urlopen', return_value=Response()), patch.dict(setup.os.environ, {'GOOGLE_RUNTIME_RESOURCE': 'instructor-runtime'}):
            installer.deploy()
        index = lambda token: next(i for i, cmd in enumerate(commands) if token in cmd)
        self.assertLess(index('execute'), index('deploy.py'))
        self.assertEqual(sum(cmd[-1] == 'deploy.py' for cmd in commands), 1)
        final = json.loads((installer.work / 'terraform/setup.auto.tfvars.json').read_text())
        self.assertEqual(final['google_runtime_project_id'], 'course-agent-test')
        self.assertEqual(final['google_runtime_resource'], 'projects/123456789/locations/us-central1/reasoningEngines/456')
        self.assertTrue(final['application_enabled'])
        self.assertTrue(any('VITE_LANGFUSE_PROJECT_ID=hosted-trace-project' in command for command in commands))
        self.assertEqual(json.loads((installer.work / 'result.json').read_text())['live_agent_acceptance'], 'pending')

    def test_empty_deployed_url_is_reconciled_without_resource_changes(self):
        calls = []
        def runner(args, **kwargs):
            calls.append(args)
            refreshed = any('-refresh-only' in cmd for cmd in calls)
            output = json.dumps({'gateway': 'https://gateway.example.run.app' if refreshed else ''})
            return subprocess.CompletedProcess(args, 0, stdout=output, stderr='')
        installer = self.installer(runner)
        self.assertEqual(installer.output('service_urls')['gateway'], 'https://gateway.example.run.app')
        mutations = [cmd for cmd in calls if 'apply' in cmd]
        self.assertEqual(len(mutations), 1)
        self.assertIn('-refresh-only', mutations[0])

    def test_missing_url_after_refresh_stops_before_key_provisioning(self):
        def runner(args, **kwargs):
            return subprocess.CompletedProcess(args, 0, stdout='{"gateway":""}', stderr='')
        installer = self.installer(runner)
        with self.assertRaises(RuntimeError):
            installer.output('service_urls')

    def test_wrong_confirmation_and_concurrent_run_make_no_changes(self):
        installer = self.installer()
        with patch('builtins.input', return_value='wrong project'), self.assertRaises(RuntimeError):
            installer.deploy()
        self.assertFalse(installer.work.exists())
        installer.work.mkdir(parents=True)
        (installer.work / 'setup.lock').write_text('')
        with patch('builtins.input', return_value='course-market-test course-agent-test'), self.assertRaises(RuntimeError):
            installer.deploy()
        self.assertFalse(installer.receipt.exists())


if __name__ == '__main__':
    unittest.main()
