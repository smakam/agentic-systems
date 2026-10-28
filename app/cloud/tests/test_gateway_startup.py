"""Optional integrations must not break baseline startup or remove required controls."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('gateway_startup', Path(__file__).resolve().parents[1] / 'scripts/start-gateway.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class GatewayStartupTests(unittest.TestCase):
    def config(self, required=False):
        return {'model_list': [{'model_name': 'support-model'}], 'guardrails': [
            {'guardrail_name': 'privacy', 'litellm_params': {'guardrail': 'litellm_content_filter'}},
            {'guardrail_name': 'pii', 'litellm_params': {'guardrail': 'presidio', 'default_on': required}},
            {'guardrail_name': 'injection', 'litellm_params': {'guardrail': 'lakera_v2', 'default_on': False}}]}

    def test_baseline_keeps_builtin_controls_without_optional_services(self):
        config = self.config()
        selected = module.configured_guardrails(config, {'LAKERA_API_KEY': 'not-configured'})
        self.assertEqual([g['guardrail_name'] for g in selected['guardrails']], ['privacy'])
        self.assertEqual(selected['model_list'], config['model_list'])
        self.assertEqual(len(config['guardrails']), 3)

    def test_configured_services_keep_their_controls(self):
        config = self.config()
        environment = {'PRESIDIO_ANALYZER_API_BASE': 'http://localhost:3000',
                       'PRESIDIO_ANONYMIZER_API_BASE': 'http://localhost:3001',
                       'LAKERA_API_KEY': 'configured-test-key'}
        self.assertEqual(module.configured_guardrails(config, environment), config)

    def test_incomplete_or_mandatory_controls_fail_closed(self):
        with self.assertRaises(ValueError):
            module.configured_guardrails(self.config(), {'PRESIDIO_ANALYZER_API_BASE': 'http://localhost:3000'})
        with self.assertRaises(ValueError):
            module.configured_guardrails(self.config(required=True), {})


if __name__ == '__main__':
    unittest.main()
