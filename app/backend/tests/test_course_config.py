"""Configuration migration must retain old deployments and fail closed."""
import os
import unittest
from unittest.mock import patch
from marketplace.course_config import setting

class CourseConfigTests(unittest.TestCase):
    def test_legacy_deployment_names_remain_readable(self):
        for current, legacy in {
            'AGENT_LOOP_LAB': 'CH11_LOOP_LAB',
            'HOSTING_LAB': 'CH12_HOSTING_LAB',
            'HOSTED_AGENT_URL': 'CH12_AGENT_URL',
            'HOSTED_AGENT_API_KEY': 'CH12_AGENT_API_KEY',
            'HOSTED_AGENT_MODEL': 'CH12_MODEL',
        }.items():
            with self.subTest(setting=current), patch.dict(os.environ, {legacy: 'legacy-value'}, clear=True):
                self.assertEqual(setting(current), 'legacy-value')

    def test_new_value_overrides_legacy_including_empty(self):
        for value in ('current-value', ''):
            with patch.dict(os.environ, {'HOSTED_AGENT_API_KEY': value, 'CH12_AGENT_API_KEY': 'old-key'}, clear=True):
                self.assertEqual(setting('HOSTED_AGENT_API_KEY'), value)

    def test_missing_value_uses_explicit_default(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(setting('HOSTED_AGENT_MODEL', 'fallback'), 'fallback')
            self.assertEqual(setting('HOSTING_LAB'), '')
