"""Offline credential-boundary checks; no Google APIs or real secrets used."""
import contextlib
import importlib.util
import io
from pathlib import Path
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'configure-cloud.py'
spec = importlib.util.spec_from_file_location('configure_cloud', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
CONNECTION = 'example-project:asia-south1:marketplace-postgres'


class CredentialChecks(unittest.TestCase):
    def test_registry_legacy_url_migrates_without_accepting_other_owners(self):
        legacy = module.database_url('mcp_registry', 'fictional', 'market', CONNECTION)
        self.assertEqual(module.stored_database_password(
            legacy, 'mcp_registry', 'market', CONNECTION, raw=True), 'fictional')
        wrong = module.database_url('market', 'fictional', 'market', CONNECTION)
        with self.assertRaises(RuntimeError):
            module.stored_database_password(wrong, 'mcp_registry', 'market', CONNECTION, raw=True)

    def test_password_roundtrip_reserved_characters_and_socket(self):
        password = 'fictional:/@?#%+ space'
        for user, db, raw in [('market', 'market', False), ('agent_reader', 'market', True), ('litellm', 'litellm', True)]:
            with self.subTest(raw=raw):
                dsn = module.database_url(user, password, db, CONNECTION, raw=raw)
                self.assertEqual(module.stored_database_password(
                    dsn, user, db, CONNECTION, raw=raw), password)

    def test_wrong_role_instance_database_and_missing_password_rejected(self):
        values = [
            module.database_url('postgres', 'fictional', 'market', CONNECTION),
            module.database_url('market', 'fictional', 'other', CONNECTION),
            module.database_url('market', 'fictional', 'market', 'other:region:instance'),
            'postgresql+psycopg://market@/market?host=%2Fcloudsql%2F' + CONNECTION,
        ]
        for dsn in values:
            with self.subTest(dsn=dsn):
                with self.assertRaisesRegex(RuntimeError, 'does not match'):
                    module.stored_database_password(dsn, 'market', 'market', CONNECTION)

    def test_api_error_does_not_expose_provider_payload_or_credentials(self):
        google = object.__new__(module.Google)
        google.token = 'fictional-token'
        error = HTTPError('https://example.invalid', 400, 'fictional-secret', {},
                          io.BytesIO(b'fictional-secret'))
        with patch.object(module, 'urlopen', side_effect=error):
            with self.assertRaises(RuntimeError) as caught:
                google.request('POST', 'https://example.invalid', {'password': 'fictional-secret'})
        self.assertEqual(str(caught.exception), 'Google API returned HTTP 400')

    def test_get_timeout_retries_but_mutation_timeout_does_not(self):
        google = object.__new__(module.Google)
        google.token = 'fictional-token'
        with patch.object(module, 'urlopen', side_effect=[TimeoutError(), io.BytesIO(b'{"ok": true}')]) as call, \
                patch.object(module.time, 'sleep'):
            self.assertEqual(google.request('GET', 'https://example.invalid'), {'ok': True})
            self.assertEqual(call.call_count, 2)
        with patch.object(module, 'urlopen', side_effect=TimeoutError('fictional-secret')) as call:
            with self.assertRaisesRegex(RuntimeError, '^Google API connection failed; retry setup$'):
                google.request('POST', 'https://example.invalid', {'password': 'fictional-secret'})
            self.assertEqual(call.call_count, 1)

    def test_get_retry_is_bounded_and_transient_http_errors_retry(self):
        google = object.__new__(module.Google)
        google.token = 'fictional-token'
        with patch.object(module, 'urlopen', side_effect=TimeoutError()) as call, \
                patch.object(module.time, 'sleep'):
            with self.assertRaisesRegex(RuntimeError, 'connection failed'):
                google.request('GET', 'https://example.invalid')
            self.assertEqual(call.call_count, 3)
        error = HTTPError('https://example.invalid', 503, 'fictional-secret', {}, None)
        with patch.object(module, 'urlopen', side_effect=[error, io.BytesIO(b'{}')]) as call, \
                patch.object(module.time, 'sleep'):
            self.assertEqual(google.request('GET', 'https://example.invalid'), {})
            self.assertEqual(call.call_count, 2)

    def test_always_policy_with_pending_startup_waits_existing_operation(self):
        google = Mock()
        waiting = {'state': 'MAINTENANCE', 'settings': {
            'ipConfiguration': {'ipv4Enabled': False}, 'activationPolicy': 'ALWAYS'}}
        ready = dict(waiting, state='RUNNABLE')
        operation = {'status': 'RUNNING', 'selfLink': 'https://example.invalid/operation'}
        google.request.side_effect = [waiting, {'items': [operation]}, ready, ready]
        module.ensure_database_ready(google, 'https://example.invalid/instance',
                                     'example-project', 'marketplace-postgres')
        google.wait.assert_called_once_with(operation, timeout=1800,
                                            phase='existing database operation')
        self.assertTrue(all(call.args[0] == 'GET' for call in google.request.call_args_list))

    def test_pending_operation_failure_prevents_user_mutations(self):
        google = Mock()
        google.request.side_effect = [
            {'settings': {'ipConfiguration': {'ipv4Enabled': False}}},
            {'items': [{'status': 'RUNNING'}]}]
        google.wait.side_effect = RuntimeError('existing database operation failed')
        with self.assertRaisesRegex(RuntimeError, 'operation failed'):
            module.ensure_database_ready(google, 'https://example.invalid/instance',
                                         'example-project', 'marketplace-postgres')
        self.assertEqual(google.request.call_count, 2)
        self.assertTrue(all(call.args[0] == 'GET' for call in google.request.call_args_list))

    def test_wait_timeout_and_failure_messages_do_not_include_operation_error_payload(self):
        google = object.__new__(module.Google)
        with patch.object(module.time, 'monotonic', side_effect=[0, 0, 601]):
            with self.assertRaisesRegex(RuntimeError, 'database credential update timed out'):
                google.wait({'status': 'RUNNING', 'selfLink': 'https://example.invalid'})
        with self.assertRaises(RuntimeError) as caught:
            google.wait({'status': 'DONE', 'error': {'message': 'fictional-secret'}})
        self.assertNotIn('fictional-secret', str(caught.exception))

    def test_interrupted_creation_reuses_stored_password_on_retry(self):
        class FakeGoogle:
            def __init__(self):
                self.values = {'gateway-provider-key': 'fictional-provider',
                               'web-demo-password': 'fictional-login-password',
                               'gateway-lakera-key': 'not-configured'}
                self.users = {'postgres'}
                self.failed_once = False
                self.market_passwords = []

            def secret(self, name):
                return self.values.get(name)

            def store(self, name, value):
                self.values[name] = value

            def wait(self, operation):
                return None

            def request(self, method, url, body=None):
                if method == 'GET' and url.endswith('/users'):
                    return {'items': [{'name': name} for name in self.users]}
                if method == 'GET':
                    return {'state': 'RUNNABLE', 'settings': {'ipConfiguration': {'ipv4Enabled': False},
                                         'activationPolicy': 'ALWAYS'}}
                self.users.add(body['name'])
                if body['name'] == 'market':
                    self.market_passwords.append(body['password'])
                    if not self.failed_once:
                        self.failed_once = True
                        # Simulate an accepted creation whose operation response was lost.
                        raise RuntimeError('interrupted')
                return {'status': 'DONE'}

        google = FakeGoogle()
        argv = ['configure-cloud.py', '--project', 'example-project']
        with patch.object(module, 'Google', return_value=google), \
                patch.object(module, 'input', return_value='example-project', create=True), \
                patch.object(module.getpass, 'getpass', side_effect=AssertionError('unexpected prompt')), \
                patch('sys.argv', argv), contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(RuntimeError, 'interrupted'):
                module.main()
            module.main()
        self.assertEqual(len(google.market_passwords), 2)
        self.assertEqual(google.market_passwords[0], google.market_passwords[1])
        self.assertTrue(google.values['web-read-database-url'].startswith('postgresql://agent_reader:'))
        self.assertTrue(google.values['web-database-url'].startswith('postgresql+psycopg://market:'))
        self.assertEqual(google.values['web-read-database-url'],
                         google.values['mcp-read-database-url'])
        self.assertTrue(google.values['gateway-master-key'].startswith('sk-'))


if __name__ == '__main__':
    unittest.main()
