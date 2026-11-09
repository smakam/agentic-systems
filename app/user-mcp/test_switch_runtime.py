"""Runtime switching keeps login configuration while changing application sources."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch


class RuntimeSwitchTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('runtime_switch', Path(__file__).with_name('switch_runtime.py'))
        self.runtime = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.runtime)
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.current = self.root / 'feature checkout/app'
        self.main_app = self.root / 'main checkout/app'
        for app in (self.current, self.main_app):
            (app / 'backend/marketplace').mkdir(parents=True)
            (app / 'frontend').mkdir()
        self.runtime.APP = self.current
        self.runtime.STATE = self.current / '.user-mcp'
        self.runtime.STATE.mkdir()
        self.private = self.root / 'active private config'
        self.private.mkdir()
        self.identity_files = {}
        self.containers = []
        for name, port in [('backend', 5178), ('memory-backend', 5179)]:
            oidc = self.private / f'ui-login-{port}.json'
            links = self.private / 'ui-identity-links.json'
            oidc.write_text('{}')
            links.write_text('{}')
            self.identity_files[name] = (oidc, links)
            self.containers.append({'Config': {
                'Env': ['MARKETPLACE_OIDC_CONFIG=/config/oidc.json'],
                'Labels': {'com.docker.compose.project.working_dir': str(self.main_app),
                           'com.docker.compose.project.config_files': str(self.main_app / 'compose.yaml') + ',' + str(self.main_app / 'compose.memory.yaml')}},
                'Mounts': [{'Source': str(oidc), 'Destination': '/config/oidc.json'},
                           {'Source': str(links), 'Destination': '/config/ui-identity-links.json'}]})
        self.calls = []

    def fake_run(self, command, **kwargs):
        self.calls.append((command, kwargs))
        if command[:2] == ['docker', 'inspect']:
            return SimpleNamespace(stdout=json.dumps(self.containers))
        if command[0] == 'git':
            return SimpleNamespace(stdout=f'worktree {self.main_app.parent}\nHEAD main-head\nbranch refs/heads/main\n\nworktree {self.current.parent}\nHEAD feature-head\nbranch refs/heads/feature\n')
        return SimpleNamespace(stdout='')

    def invoke(self, checkout):
        with patch.object(sys, 'argv', ['switch_runtime.py', checkout]), \
             patch.object(self.runtime, 'run', side_effect=self.fake_run), \
             contextlib.redirect_stdout(io.StringIO()):
            self.runtime.main()
        return json.loads((self.runtime.STATE / 'runtime-overlay.yaml').read_text())['services']

    def test_main_uses_main_sources_and_preserves_both_active_logins(self):
        services = self.invoke('main')
        self.assertEqual(set(services), set(self.runtime.SERVICES))
        for name, service in services.items():
            with self.subTest(service=name):
                kind = 'backend' if name.endswith('backend') else 'frontend'
                self.assertEqual(service['build']['context'], str(self.main_app / kind))
                self.assertNotIn('ports', service)
                self.assertNotIn('DATABASE_URL', service.get('environment', {}))
                if kind == 'backend':
                    oidc, links = self.identity_files[name]
                    self.assertIn(str(self.main_app / 'backend/marketplace') + ':/app/marketplace:ro', service['volumes'])
                    self.assertIn(str(oidc) + ':/config/oidc.json:ro', service['volumes'])
                    self.assertIn(str(links) + ':/config/ui-identity-links.json:ro', service['volumes'])
                    self.assertEqual(service['environment']['MARKETPLACE_OIDC_CONFIG'], '/config/oidc.json')
                    self.assertIn('--no-access-log', service['command'])

    def test_branch_remains_compatible_and_also_rebuilds_current_checkout(self):
        services = self.invoke('branch')
        self.assertEqual(services['backend']['build']['context'], str(self.current / 'backend'))
        self.assertFalse(any(command[0] == 'git' for command, _ in self.calls))
        self.assertTrue(any('build' in command for command, _ in self.calls))

    def test_build_precedes_application_only_recreation_using_existing_compose_files(self):
        self.invoke('main')
        compose = [(command, kw) for command, kw in self.calls if command[:2] == ['docker', 'compose']]
        self.assertEqual(len(compose), 3)
        self.assertEqual(compose[0][0][-3:], ['build', 'backend', 'frontend'])
        self.assertEqual(compose[1][0][-7:], ['up', '-d', '--no-deps', *self.runtime.SERVICES])
        self.assertEqual(compose[2][0][-3:], ['restart', 'frontend', 'memory-frontend'])
        for command, kwargs in compose:
            self.assertEqual(command[2:6], ['-f', str(self.main_app / 'compose.yaml'), '-f', str(self.main_app / 'compose.memory.yaml')])
            self.assertEqual(kwargs['cwd'], str(self.main_app))
            self.assertFalse({'down', '--volumes', 'postgres', 'identity', 'payout-worker'} & set(command))

    def test_generated_configuration_can_enable_optional_login_before_first_switch(self):
        for container in self.containers:
            container['Config']['Env'] = []
            container['Mounts'] = []
        for port in (5178, 5179):
            (self.runtime.STATE / f'ui-login-{port}.json').write_text('{}')
        (self.runtime.STATE / 'ui-identity-links.json').write_text('{}')
        services = self.invoke('main')
        for name in self.runtime.BACKENDS:
            self.assertEqual(services[name]['environment']['MARKETPLACE_OIDC_CONFIG'], '/config/oidc.json')

    def test_missing_private_configuration_stops_before_rebuild(self):
        self.identity_files['memory-backend'][0].unlink()
        with self.assertRaisesRegex(RuntimeError, 'Private Keycloak configuration files'):
            self.invoke('main')
        self.assertFalse(any(command[:2] == ['docker', 'compose'] for command, _ in self.calls))

    def test_main_without_a_main_worktree_is_not_a_silent_branch_fallback(self):
        with patch.object(self.runtime, 'run', return_value=SimpleNamespace(stdout='worktree /tmp/feature\nbranch refs/heads/feature\n')):
            with self.assertRaisesRegex(RuntimeError, 'Check out main'):
                self.runtime.source_app('main')


if __name__ == '__main__':
    unittest.main()
