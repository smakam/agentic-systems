"""No-paid-call fixture and deployment boundary checks."""
import inspect
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from support_agent_basics.tools import lookup_order,load_fixture
import deploy

class BasicsTests(unittest.TestCase):
    def test_known_order_exact_products_and_statuses(self):
        result=lookup_order('order-demo-1')
        self.assertTrue(result['found'])
        self.assertEqual(result['order']['items'][0]['product'],'Ceramic Mug Set')
        self.assertEqual(result['order']['items'][0]['quantity'],2)
        self.assertEqual(result['order']['payment_status'],'received')
        self.assertEqual(result['order']['payout_status'],'held')
        self.assertTrue(result['source']['fictional'])
    def test_other_orders_distinct_and_unknown_not_invented(self):
        self.assertEqual(lookup_order('order-demo-2')['order']['payout_status'],'released')
        self.assertEqual(lookup_order('order-demo-3')['order']['payment_status'],'refunded')
        unknown=lookup_order('order-demo-999')
        self.assertFalse(unknown['found']);self.assertNotIn('order',unknown)
    def test_no_path_sql_or_identity_input_surface(self):
        self.assertEqual(list(inspect.signature(lookup_order).parameters),['order_id'])
        for value in ('../orders.json',"order-demo-1' OR 1=1",'operator','',None):
            self.assertFalse(lookup_order(value)['found'])
    def test_results_do_not_mutate_packaged_data(self):
        result=lookup_order('order-demo-1');result['order']['items'][0]['quantity']=99
        self.assertEqual(lookup_order(' ORDER-DEMO-1 ')['order']['items'][0]['quantity'],2)
    def test_fixture_rejects_duplicate_and_boolean_quantities(self):
        data=load_fixture();data['orders'].append(data['orders'][0])
        with patch('support_agent_basics.tools.Path.read_text',return_value=json.dumps(data)):
            with self.assertRaises(ValueError):load_fixture()
        data=load_fixture();data['orders'][0]['items'][0]['quantity']=True
        with patch('support_agent_basics.tools.Path.read_text',return_value=json.dumps(data)):
            with self.assertRaises(ValueError):load_fixture()
    def test_deployment_has_no_mcp_secret_or_existing_runtime_target(self):
        env={'GOOGLE_STAGING_BUCKET':'gs://synthetic-staging','GOOGLE_RUNTIME_SERVICE_ACCOUNT':'synthetic-runtime@example.invalid','GOOGLE_RUNTIME_RESOURCE':'existing-runtime-must-be-ignored'}
        with patch.dict('os.environ',env):config=deploy.deployment_config()
        self.assertEqual(config['display_name'],'Support Agent Basics')
        self.assertFalse(any('MCP' in x or 'SECRET' in x or 'API_KEY' in x for x in config['env_vars']))
        self.assertNotIn('resource_name',config)
        self.assertEqual(config['extra_packages'],['support_agent_basics'])
    def test_package_contains_static_data_and_no_middleware_imports(self):
        package=Path(__file__).with_name('support_agent_basics')
        self.assertTrue((package/'orders.json').is_file());self.assertTrue((package/'instructions.txt').is_file())
        source=(package/'agent.py').read_text()
        self.assertNotIn('McpToolset',source);self.assertNotIn('marketplace_google',source)
        self.assertIn('tools=[lookup_order,OptionalMemory()]',source)
    def test_creation_refuses_existing_basics_manifest(self):
        with patch.object(deploy.MANIFEST.__class__,'exists',return_value=True):
            with self.assertRaises(SystemExit):deploy.main()

if __name__=='__main__':unittest.main()

class CreateOnlyTests(unittest.TestCase):
    def test_new_runtime_creation_does_not_target_existing_lab(self):
        import tempfile
        from types import SimpleNamespace
        import sys
        calls=[]
        class Runtimes:
            def create(self,**kwargs):
                calls.append(kwargs)
                return SimpleNamespace(api_resource=SimpleNamespace(name='projects/synthetic/locations/test/reasoningEngines/new-basics'))
        fake_client=SimpleNamespace(runtimes=Runtimes())
        fake_platform=SimpleNamespace(Client=lambda **kwargs:fake_client)
        env={'GOOGLE_CLOUD_PROJECT':'synthetic-project','GOOGLE_CLOUD_LOCATION':'test','GOOGLE_STAGING_BUCKET':'gs://synthetic-staging','GOOGLE_RUNTIME_SERVICE_ACCOUNT':'synthetic-runtime@example.invalid','GOOGLE_RUNTIME_RESOURCE':'original-lab-must-remain-untouched'}
        with tempfile.TemporaryDirectory() as tmp:
            manifest=Path(tmp)/'support-basics-deployment.json'
            with patch.dict('os.environ',env),patch.object(deploy,'MANIFEST',manifest),patch.dict(sys.modules,{'agentplatform':fake_platform,'support_agent_basics.agent':SimpleNamespace(build_app=lambda:'synthetic-app')}),patch('builtins.print'):
                deploy.main()
            saved=json.loads(manifest.read_text())
        self.assertEqual(len(calls),1)
        self.assertEqual(saved['app_name'],'support_agent_basics')
        self.assertTrue(saved['resource_name'].endswith('new-basics'))
        self.assertNotIn('original-lab-must-remain-untouched',json.dumps(calls))
