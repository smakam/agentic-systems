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
        self.assertIn('tools=[lookup_order,remember_preference,OptionalMemory()]',source)
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

class PreferenceSaveTests(unittest.IsolatedAsyncioTestCase):
    def context(self, text, error=None):
        from types import SimpleNamespace
        from unittest.mock import AsyncMock
        from google.genai import types
        return SimpleNamespace(user_content=types.Content(role='user',parts=[types.Part(text=text)]),
                               add_events_to_memory=AsyncMock(side_effect=error))

    async def test_explicit_request_sends_only_requested_preference(self):
        from support_agent_basics.preference_memory import remember_preference
        ctx=self.context('Please remember: I prefer answers in a compact table. Also what is order-demo-1?')
        result=await remember_preference('I prefer answers in a compact table.',ctx)
        self.assertEqual(result['status'],'generation_requested')
        events=ctx.add_events_to_memory.call_args.kwargs['events']
        self.assertEqual(len(events),1)
        self.assertEqual(events[0].author,'user')
        self.assertEqual(events[0].content.parts[0].text,'I prefer answers in a compact table.')
        self.assertNotIn('order-demo-1',str(events))

    async def test_no_save_without_current_explicit_authorization(self):
        from support_agent_basics.preference_memory import remember_preference
        for message in ['I prefer answers in a compact table.','Do not remember: I prefer answers in a compact table.',
                        'What is the payout status for order-demo-1?']:
            ctx=self.context(message)
            result=await remember_preference('I prefer answers in a compact table.',ctx)
            self.assertFalse(result['generation_requested']);ctx.add_events_to_memory.assert_not_called()

    async def test_cannot_invent_preference_or_save_business_status(self):
        from support_agent_basics.preference_memory import remember_preference
        for message,preference in [('Remember my format.','I prefer detailed tables.'),
                                   ('Remember that order-demo-1 is held.','order-demo-1 is held')]:
            ctx=self.context(message);result=await remember_preference(preference,ctx)
            self.assertFalse(result['generation_requested']);ctx.add_events_to_memory.assert_not_called()

    async def test_disabled_and_provider_failure_are_not_success(self):
        from support_agent_basics.preference_memory import remember_preference
        ctx=self.context('Remember: I prefer brief answers.')
        with patch.dict('os.environ',{'GOOGLE_MEMORY_ENABLED':'false'}):
            result=await remember_preference('I prefer brief answers.',ctx)
        self.assertFalse(result['generation_requested']);ctx.add_events_to_memory.assert_not_called()
        ctx=self.context('Remember: I prefer brief answers.',RuntimeError('private provider detail'))
        result=await remember_preference('I prefer brief answers.',ctx)
        self.assertEqual(result['status'],'generation_unconfirmed');self.assertNotIn('private',str(result))

    async def test_real_adk_context_scopes_memory_to_trusted_user(self):
        from types import SimpleNamespace
        from unittest.mock import AsyncMock
        from google.adk.tools import ToolContext
        from google.adk.sessions import Session
        from google.genai import types
        from support_agent_basics.preference_memory import remember_preference
        service=SimpleNamespace(add_events_to_memory=AsyncMock())
        session=Session(id='owned-session',app_name='support_agent_basics',user_id='trusted-user')
        invocation=SimpleNamespace(session=session,memory_service=service,
            user_content=types.Content(role='user',parts=[types.Part(text='Remember: I prefer brief answers.')]))
        ctx=ToolContext(invocation)
        result=await remember_preference('I prefer brief answers.',ctx)
        self.assertTrue(result['generation_requested'])
        call=service.add_events_to_memory.call_args.kwargs
        self.assertEqual((call['user_id'],call['app_name'],call['session_id']),
                         ('trusted-user','support_agent_basics','owned-session'))

    def test_agent_exposes_context_only_save_tool(self):
        from google.adk.tools import FunctionTool
        from support_agent_basics.agent import build_agent
        agent=build_agent()
        tool=next(t for t in agent.tools if getattr(t,'__name__','')=='remember_preference')
        declaration=FunctionTool(func=tool)._get_declaration()
        self.assertEqual(set(declaration.parameters_json_schema['properties']),{'preference'})

class BasicsUpdateTests(unittest.TestCase):
    def test_update_preserves_runtime_identity_environment_and_limits(self):
        from types import SimpleNamespace as Obj
        from update import update_config
        resource=Obj(display_name='Support Agent Basics',spec=Obj(
            service_account='existing@example.invalid',package_spec=Obj(
                pickle_object_gcs_uri='gs://existing-bucket/agent/agent.pkl',python_version='3.12'),
            deployment_spec=Obj(secret_env=[],env=[Obj(name='GOOGLE_MEMORY_ENABLED',value='true'),
                Obj(name='GOOGLE_AGENT_MODEL',value='existing-model')],min_instances=0,max_instances=1)))
        config=update_config(resource)
        self.assertEqual(config['service_account'],'existing@example.invalid')
        self.assertEqual(config['staging_bucket'],'gs://existing-bucket')
        self.assertEqual(config['env_vars']['GOOGLE_AGENT_MODEL'],'existing-model')
        resource.display_name='Marketplace Support ADK Lab'
        with self.assertRaises(ValueError):update_config(resource)
