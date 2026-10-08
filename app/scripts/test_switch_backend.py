"""Exercise coordinated-switch failures and configuration preservation offline."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('switch_backend', Path(__file__).with_name('switch-backend.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
C = m.load_config(Path(__file__).with_name('backend-switch-profiles.json'))


class SwitchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.args = SimpleNamespace(config=Path(__file__).with_name('backend-switch-profiles.json'),
            backend='local', plan=False, apply=True, env_file=Path('/absent'),
            receipt=Path(self.temp.name) / 'receipt.json', timeout=1)
        self.ga = {'name': C['google_runtime'], 'etag': 'read-version',
            'spec': {'deploymentSpec': {'env': [{'name': 'KEEP', 'value': 'yes'}, {'name': 'BACKEND_PROFILE_CONFIG_VERSION', 'value': 'runtime-url-v1'},
                {'name': 'REMOTE_MCP_URL', 'value': C['profiles']['cloud']['url']}],
                'secretEnv': [{'name': 'OTHER_SECRET', 'secretRef': {'secret': 'keep', 'version': '2'}},
                    {'name': 'REMOTE_MCP_API_KEY', 'secretRef': m.desired_pair(C['profiles']['cloud'])[1]}]}}}
        self.la = {'name': 'support', 'model': 'keep-model', 'provider_id': 'OpenAI', 'top_p': 1, 'temperature': 0,
            'features': [{'type': 'MEMORY', 'config': {'keep': True}}], 'agent_instructions': 'keep instructions',
            'tools': ['cloud connection', 'other'],
            'tool_configs': [{'tool_name': 'cloud connection', 'server_id': C['profiles']['cloud']['lyzr_server'],
                'action_names': sorted(m.ACTIONS), 'tool_source': 'mcp', 'persist_auth': True}]}
        self.servers = [{'id': p['lyzr_server'], 'name': n + ' connection', 'server_url': p['url'],
                         'auth_type': 'api_key'} for n, p in C['profiles'].items()]
        self.calls = []
        self.fail_google = False

    def api(self, url, headers, method='GET', payload=None):
        self.calls.append((method, url))
        if method == 'PATCH':
            self.assertEqual(payload['etag'], 'read-version')
            if not self.fail_google:
                self.ga['spec']['deploymentSpec'].update(payload['spec']['deploymentSpec'])
            return {'name': C['google_runtime'] + '/operations/test', 'done': True,
                    **({'error': {'code': 400}} if self.fail_google else {})}
        if method == 'PUT':
            self.la = copy.deepcopy(payload)
            return {'message': 'updated'}
        if '/tools/mcp/servers/' in url:
            return {'tools': [{'name': n} for n in m.ACTIONS]}
        if url.endswith('/tools/mcp/servers'):
            return {'servers': copy.deepcopy(self.servers)}
        if '/agents/' in url:
            return copy.deepcopy(self.la)
        return copy.deepcopy(self.ga)

    def run_switch(self):
        with patch.object(m, 'request', self.api), patch.object(m, 'google_headers', return_value={}), \
             patch.object(m, 'lyzr_key', return_value='private-test-key'):
            return m.run(self.args)

    def test_preserves_settings_and_switches_both(self):
        before = copy.deepcopy(self.la)
        self.assertEqual(self.run_switch(), 0)
        self.assertEqual(m.google_pair(self.ga), m.desired_pair(C['profiles']['local']))
        self.assertEqual(self.ga['spec']['deploymentSpec']['env'][0], {'name': 'KEEP', 'value': 'yes'})
        self.assertEqual(self.ga['spec']['deploymentSpec']['secretEnv'][0]['secretRef']['secret'], 'keep')
        self.assertEqual(self.la['tools'], ['local connection', 'other'])
        for k in ('features', 'model', 'agent_instructions'):
            self.assertEqual(self.la[k], before[k])
        self.assertTrue(json.loads(self.args.receipt.read_text())['verified'])

    def test_bad_saved_connection_prevents_both_updates(self):
        self.servers[0]['server_url'] = 'https://wrong.example/mcp'
        with self.assertRaises(RuntimeError): self.run_switch()
        self.assertFalse(any(method != 'GET' for method, _ in self.calls))

    def test_google_rejection_prevents_lyzr_update_and_records_failure(self):
        self.fail_google = True
        with self.assertRaises(RuntimeError): self.run_switch()
        self.assertFalse(any(method == 'PUT' for method, _ in self.calls))
        self.assertFalse(json.loads(self.args.receipt.read_text())['verified'])

    def test_read_only_check_never_updates(self):
        self.args.apply = False
        self.assertEqual(self.run_switch(), 1)
        self.assertFalse(any(method != 'GET' for method, _ in self.calls))

    def test_plan_requires_neither_credentials_nor_network(self):
        self.args.plan = True
        with patch.object(m, 'request', side_effect=AssertionError('network')), \
             patch.object(m, 'google_headers', side_effect=AssertionError('credentials')):
            self.assertEqual(m.run(self.args), 0)

    def test_noop_apply_never_mutates(self):
        self.args.backend = 'cloud'
        self.assertEqual(self.run_switch(), 0)
        self.assertFalse(any(method != 'GET' for method, _ in self.calls))

    def test_legacy_packaged_agent_cannot_switch(self):
        self.ga['spec']['deploymentSpec']['env'] = [item for item in
            self.ga['spec']['deploymentSpec']['env'] if item['name'] != 'BACKEND_PROFILE_CONFIG_VERSION']
        with self.assertRaisesRegex(RuntimeError, 'runtime-resolved MCP repair'):
            self.run_switch()
        self.assertFalse(any(method != 'GET' for method, _ in self.calls))

    def test_missing_action_prevents_both_updates(self):
        api = self.api
        def missing(url, headers, method='GET', payload=None):
            if '/tools/mcp/servers/' in url:
                return {'tools': [{'name': 'get_catalog'}]}
            return api(url, headers, method, payload)
        with patch.object(m, 'request', missing), patch.object(m, 'google_headers', return_value={}), \
             patch.object(m, 'lyzr_key', return_value='private-test-key'):
            with self.assertRaises(RuntimeError): m.run(self.args)
        self.assertFalse(any(method != 'GET' for method, _ in self.calls))

    def test_previous_pending_google_operation_blocks_new_apply(self):
        self.args.receipt.write_text(json.dumps({'google': 'update submitted',
            'google_operation': C['google_runtime'] + '/operations/pending'}))
        api = self.api
        def pending(url, headers, method='GET', payload=None):
            if '/operations/pending' in url: return {'done': False}
            return api(url, headers, method, payload)
        with patch.object(m, 'request', pending), patch.object(m, 'google_headers', return_value={}), \
             patch.object(m, 'lyzr_key', return_value='private-test-key'):
            with self.assertRaises(RuntimeError): m.run(self.args)
        self.assertFalse(any(method != 'GET' for method, _ in self.calls))

    def test_unexpected_lyzr_readback_is_not_success(self):
        api = self.api
        def corrupt(url, headers, method='GET', payload=None):
            result = api(url, headers, method, payload)
            if method == 'PUT': self.la['model'] = 'unexpected-change'
            return result
        with patch.object(m, 'request', corrupt), patch.object(m, 'google_headers', return_value={}), \
             patch.object(m, 'lyzr_key', return_value='private-test-key'):
            with self.assertRaises(RuntimeError): m.run(self.args)
        self.assertFalse(json.loads(self.args.receipt.read_text())['verified'])


if __name__ == '__main__': unittest.main()
