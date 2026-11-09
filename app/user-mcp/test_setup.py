"""Provisioning regression checks for the ChatGPT OAuth refresh flow."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


class IdentitySetupTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('identity_setup', Path(__file__).with_name('setup.py'))
        self.setup_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.setup_module)
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.setup_module.APP = Path(self.temporary.name) / 'app'
        self.setup_module.APP.mkdir()
        self.setup_module.STATE = self.setup_module.APP / '.user-mcp'
        self.arguments = ['setup.py', '--base-url', 'https://marketplace.example.test',
                          '--chatgpt-callback', 'https://chatgpt.com/connector_platform_oauth_redirect']
        self.generate()

    def generate(self):
        with patch.object(sys, 'argv', self.arguments):
            self.setup_module.main()
        self.realm = json.loads((self.setup_module.STATE / 'marketplace-realm.json').read_text())

    def test_chatgpt_refresh_scope_keeps_read_only_access_and_exact_callback(self):
        client = next(c for c in self.realm['clients'] if c['clientId'] == 'marketplace-chatgpt')
        self.assertEqual(client['defaultClientScopes'], ['orders:read'])
        self.assertEqual(client['optionalClientScopes'], ['offline_access'])
        self.assertEqual(client['redirectUris'], [self.arguments[-1]])
        self.assertFalse(client['fullScopeAllowed'])
        self.assertFalse(client['directAccessGrantsEnabled'])
        self.assertEqual(client['attributes']['pkce.code.challenge.method'], 'S256')

    def test_browser_test_client_does_not_receive_the_offline_scope(self):
        client = next(c for c in self.realm['clients'] if c['clientId'] == 'marketplace-local-test')
        self.assertTrue(client['publicClient'])
        self.assertEqual(client['optionalClientScopes'], [])

    def test_four_demo_accounts_have_the_required_offline_refresh_role(self):
        self.assertEqual({u['username'] for u in self.realm['users']}, {'buyer', 'buyer2', 'seller', 'seller2'})
        for user in self.realm['users']:
            with self.subTest(user=user['username']):
                self.assertIn('offline_access', user['realmRoles'])

    def test_rerunning_setup_preserves_existing_identities_and_credentials(self):
        before = {u['username']: (u['id'], u['credentials']) for u in self.realm['users']}
        self.generate()
        after = {u['username']: (u['id'], u['credentials']) for u in self.realm['users']}
        self.assertEqual(after, before)


if __name__ == '__main__':
    unittest.main()
