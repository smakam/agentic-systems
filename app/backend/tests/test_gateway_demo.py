import copy,os,unittest,json
from types import SimpleNamespace
from unittest.mock import patch
import httpx
from fastapi.testclient import TestClient
from marketplace import gateway_demo as demo

class GatewayDemoTests(unittest.IsolatedAsyncioTestCase):
 def setUp(self):
  self.env=patch.dict(os.environ,{'LITELLM_API_KEY':'test-support-key','OPERATOR_GATEWAY_KEY':'test-operator-key','GATEWAY_MODEL_DEMO_ADMIN_KEY':'admin-test','GATEWAY_MODEL_DEMO_ENABLED':'true'});self.env.start();self.addCleanup(self.env.stop)
  self.keys={k:{'key_alias':a,'models':[demo.ALIAS,'embedding'],'aliases':{}} for k,a in [('test-support-key','marketplace-test-support'),('test-operator-key','marketplace-test-operator')]}
  self.rows=[{'model_name':'support-model','litellm_params':{'model':'openai/gpt-5.4-2026-03-05'},'model_info':{'id':'main-model','db_model':False}},{'model_name':demo.ALIAS,'litellm_params':{'model':'openai/gpt-5.4-2026-03-05'},'model_info':{'id':demo.MODEL_ID,'db_model':True}}]
  self.before=copy.deepcopy((self.keys,self.rows));self.writes=[];self.fail_once=False
 def api(self):
  def handle(request):
   if request.url.path=='/key/info':return httpx.Response(200,json={'info':self.keys[request.url.params['key']]})
   if request.url.path=='/model/info':return httpx.Response(200,json={'data':self.rows})
   assert request.url.path=='/model/update',request.url.path
   body=json.loads(request.content);self.writes.append(body);assert body['model_info']['id']==demo.MODEL_ID
   self.rows[1]['litellm_params']['model']=body['litellm_params']['model']
   if self.fail_once:self.fail_once=False;return httpx.Response(503,json={'error':'not exposed'})
   return httpx.Response(200,json={})
  return httpx.AsyncClient(base_url='http://gateway',transport=httpx.MockTransport(handle))
 async def test_changes_alias_definition_not_keys_or_main_model(self):
  with patch.object(demo,'require_enabled'),patch.object(demo,'client',self.api):
   state=await demo.set_model('nano');self.assertEqual(state['requested_alias'],demo.ALIAS);self.assertEqual(state['choice'],'nano')
   self.assertEqual(self.keys,self.before[0]);self.assertEqual(self.rows[0],self.before[1][0]);self.assertEqual(self.rows[1]['litellm_params']['model'],'openai/gpt-5-nano-2025-08-07')
   self.assertNotIn('test-support-key',str(state));self.assertNotIn('admin-test',str(state));self.assertEqual(demo.configuration(state)['alias'],demo.ALIAS)
   self.assertEqual((await demo.set_model('gpt54'))['choice'],'gpt54')
 async def test_ambiguous_failure_restores_alias_definition(self):
  self.fail_once=True
  with patch.object(demo,'require_enabled'),patch.object(demo,'client',self.api):
   with self.assertRaisesRegex(demo.Unavailable,'restored'):await demo.set_model('nano')
  self.assertEqual((self.keys,self.rows),self.before)
 async def test_refuses_main_key_before_write(self):
  self.keys['test-support-key']['key_alias']='marketplace-support'
  with patch.object(demo,'require_enabled'),patch.object(demo,'client',self.api):
   with self.assertRaises(demo.Unavailable):await demo.set_model('nano')
  self.assertFalse(self.writes)
 async def test_refuses_file_model_or_duplicate_alias(self):
  self.rows[1]['model_info']['db_model']=False
  with patch.object(demo,'require_enabled'),patch.object(demo,'client',self.api):
   with self.assertRaises(demo.Unavailable):await demo.set_model('nano')
  self.assertFalse(self.writes)
 async def test_unknown_model_and_main_database_rejected(self):
  with patch.object(demo,'require_enabled'):
   with self.assertRaises(ValueError):await demo.set_model('arbitrary-provider')
  with patch('marketplace.security_demo.is_test',return_value=False):
   self.assertFalse(demo.enabled())
   with self.assertRaises(ValueError):await demo.set_model('nano')
 async def test_openrouter_preserves_provider(self):
  self.rows[1]['litellm_params']['model']='openrouter/openai/gpt-5.4'
  with patch.object(demo,'require_enabled'),patch.object(demo,'client',self.api):
   state=await demo.set_model('nano');self.assertEqual(state['model'],'openrouter/openai/gpt-5-nano')

class GatewayDemoApiTests(unittest.TestCase):
 def setUp(self):
  from marketplace.api import app,identity
  self.app=app;self.identity=identity;self.client=TestClient(app);app.dependency_overrides[identity]=lambda:SimpleNamespace(role='support');self.addCleanup(app.dependency_overrides.clear)
 def test_main_disabled_and_mutation_denied(self):
  with patch.object(demo,'enabled',return_value=False):
   self.assertEqual(self.client.get('/api/gateway-model-demo').json(),{'enabled':False});self.assertEqual(self.client.post('/api/gateway-model-demo',json={'choice':'nano'}).status_code,403)
 def test_buyer_and_arbitrary_choice_denied(self):
  self.app.dependency_overrides[self.identity]=lambda:SimpleNamespace(role='buyer');self.assertEqual(self.client.get('/api/gateway-model-demo').status_code,403)
  self.app.dependency_overrides[self.identity]=lambda:SimpleNamespace(role='support');self.assertEqual(self.client.post('/api/gateway-model-demo',json={'choice':'other'}).status_code,422)
 def test_running_answer_prevents_change(self):
  from contextlib import nullcontext
  lock=SimpleNamespace(execute=lambda *a,**kw:SimpleNamespace(scalar=lambda:False))
  with patch.object(demo,'enabled',return_value=True),patch('marketplace.api.engine.connect',return_value=nullcontext(lock)):
   self.assertEqual(self.client.post('/api/gateway-model-demo',json={'choice':'nano'}).status_code,409)
