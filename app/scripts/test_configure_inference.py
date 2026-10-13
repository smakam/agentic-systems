import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('configure_inference', Path(__file__).with_name('configure-inference.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ConfigurationPreservation(unittest.TestCase):
    def test_switching_provider_preserves_native_routes_and_lakera(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / 'infra').mkdir()
            (root / '.env').write_text('LAKERA_API_KEY=test-only-placeholder\n')
            (root / 'infra/litellm.yaml').write_text('model_list:\n  - model_name: support-model\n    litellm_params:\n      model: openai/original\n      api_key: os.environ/OPENAI_API_KEY\nlitellm_settings:\n  drop_params: false\nguardrails:\n  - guardrail_name: existing-filter\n')
            (root / 'infra/routing-demo.models.yaml').write_text('  - model_name: ch16-llm-question\n    litellm_params: {model: auto_router/complexity_router}\n')
            (root / 'infra/lakera-guardrail.fragment.yaml').write_text('  - guardrail_name: marketplace-lakera-pre\n    litellm_params: {guardrail: lakera_v2}\n')
            for provider in ('openai', 'openrouter', 'openai'):
                with patch.object(module, 'ROOT', root), patch.dict(os.environ, {'INFERENCE_PROVIDER': provider}):
                    module.main()
                text = (root / 'infra/litellm.provider.generated.yaml').read_text()
                self.assertEqual(text.count('model_name: ch16-llm-question'), 1)
                self.assertEqual(text.count('guardrail_name: marketplace-lakera-pre'), 1)
                self.assertIn('guardrail_name: existing-filter', text)
                self.assertNotIn('test-only-placeholder', text)
                self.assertIn('model: ' + module.ROUTES[provider]['support-model'], text)

if __name__ == '__main__': unittest.main()
