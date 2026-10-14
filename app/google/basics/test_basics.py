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

class VerificationPredicatesTests(unittest.TestCase):
    def test_known_answer_requires_native_lookup_evidence(self):
        from verify_basics import check_case
        answer={'answer':'2 Ceramic Mug Sets','order_results':[],'errors':[]}
        self.assertFalse(check_case('known_order',answer))
        answer['order_results']=[lookup_order('order-demo-1')]
        self.assertTrue(check_case('known_order',answer))
    def test_memory_format_without_fixture_evidence_is_insufficient(self):
        from verify_basics import check_case
        answer={'answer':'Finding Evidence Next action released','order_results':[],'errors':[]}
        self.assertFalse(check_case('fresh_session_business_memory',answer))
        answer['order_results']=[lookup_order('order-demo-2')]
        self.assertTrue(check_case('fresh_session_business_memory',answer))
    def test_preload_requires_model_input_not_formatted_output(self):
        from verify_traces import preload_evidence
        text='<PAST_CONVERSATIONS> prefers Finding, Evidence and Next action'
        self.assertFalse(preload_evidence([{'output':text}]))
        self.assertTrue(preload_evidence([{'model_input':text}]))

    def test_unexpected_and_error_events_are_not_erased(self):
        from verify_basics import summarize
        result=summarize([{'error':{'code':500,'message':'synthetic failure'},'details':'transport detail','authorization':'secret'},{}])
        self.assertEqual(result['events'][0]['details'],'transport detail')
        self.assertEqual(result['events'][0]['authorization'],'[redacted]')
        self.assertEqual(result['errors'][0]['error']['code'],500)
        self.assertEqual(len(result['diagnostics']),2)
        self.assertEqual(result['answer'],'')
    def test_wrapped_native_content_is_recognized(self):
        from verify_basics import summarize
        result=summarize([{'result':{'content':{'parts':[{'text':'held'}]}}}])
        self.assertEqual(result['answer'],'held')
        self.assertEqual(result['diagnostics'],[])
    def test_followup_can_use_verified_same_session_lookup_only(self):
        from verify_basics import check_case
        result={'session':'first','answer':'The payout is held','order_results':[],'errors':[],
                'retained_lookup_evidence':{'session':'first','source_case':'known_order','order_results':[lookup_order('order-demo-1')]}}
        self.assertTrue(check_case('same_session_followup',result))
        result['retained_lookup_evidence']['session']='other'
        self.assertFalse(check_case('same_session_followup',result))
