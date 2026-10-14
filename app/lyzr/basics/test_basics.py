import json,unittest
from pathlib import Path
import prepare
class FixtureGroundingTests(unittest.TestCase):
 def test_exact_fixture_and_catalogue(self):
  data=json.loads(prepare.FIXTURE.read_text());text=prepare.render_fixture(data)
  for row in data['orders']:
   self.assertIn(json.dumps(row,indent=2,ensure_ascii=False),text)
  self.assertEqual(text.count('SOURCE RECORD '),3)
  self.assertNotIn('order-demo-999',text)
  self.assertIn('Only these three orders exist',text)
 def test_no_live_data_or_duplicate_ids(self):
  data=json.loads(prepare.FIXTURE.read_text());data['fictional']=False
  with self.assertRaises(ValueError):prepare.render_fixture(data)
  data['fictional']=True;data['orders'].append(data['orders'][0])
  with self.assertRaises(ValueError):prepare.render_fixture(data)
 def test_prompt_no_fake_native_python_tool(self):
  text=(prepare.HERE/'agent-instructions.txt').read_text()
  self.assertIn('Retrieve the attached Knowledge Base',text)
  self.assertIn('no eligibility policy is supplied',text)
  self.assertNotIn('lookup_order(',text)
 def test_create_payload_does_not_copy_existing_connections_or_data(self):
  from deploy import build_agent_config
  payload=build_agent_config('new-kb','authorized-credential')
  self.assertEqual(payload['tools'],[]);self.assertEqual(payload['tool_configs'],[])
  self.assertEqual(payload['managed_agents'],[]);self.assertEqual(payload['agent_context'],'')
  feature=payload['features'][0]
  self.assertEqual(feature['type'],'KNOWLEDGE_BASE')
  self.assertEqual(feature['config']['lyzr_rag']['rag_id'],'new-kb')
  self.assertNotIn('api_key',payload)
 def test_memory_receipt_requires_source_not_answer_format(self):
  from verify_cross_session import evaluate
  r={'owner_id':'owner','agent_id':'agent','seed_session_id':'seed','marker':'marker','before_seed':{'total':0},'native_records':{'memories':[]},'cases':[],'other_native_records':{'total':0}}
  self.assertFalse(evaluate(r)['native_record_source_matches'])
  r['native_records']['memories']=[{'owner_id':'owner','agent_id':'agent','session_id':'seed','content':'marker','original_content':['marker']}]
  self.assertTrue(evaluate(r)['native_record_source_matches'])
  r['native_records']['memories'][0]['owner_id']='other'
  self.assertFalse(evaluate(r)['native_record_source_matches'])
 def test_runner_restores_original_setting_after_failure(self):
  import tempfile
  from verify_cross_session import Lab
  original={'name':'Support Agent Basics','tools':[],'tool_configs':[],'features':[{'type':'MEMORY','config':{'provider':'cognis','lyzr_memory':{'params':{'cross_session':False}}}}]}
  class FakeLab(Lab):
   def __init__(self):self.updates=[]
   def request(self,base,path,payload=None,method=None):
    if method=='PUT':self.updates.append(payload);return {}
    if path.startswith('/v3/agents/'):return original
    raise RuntimeError('synthetic failure')
  lab=FakeLab()
  with tempfile.TemporaryDirectory() as tmp:r=lab.run({'agent_id':'separate'},Path(tmp)/'receipt.json',0)
  self.assertEqual(len(lab.updates),2)
  self.assertTrue(lab.updates[0]['features'][0]['config']['lyzr_memory']['params']['cross_session'])
  self.assertFalse(lab.updates[1]['features'][0]['config']['lyzr_memory']['params']['cross_session'])
  self.assertTrue(r['restored_original_memory_configuration'])
  self.assertEqual(r['cases'],[])
 def test_studio_created_target_requires_no_local_manifest(self):
  import tempfile
  from verify_cross_session import resolve_target
  agent_id='abcdef0123456789abcdef01'
  with tempfile.TemporaryDirectory() as tmp:
   absent=Path(tmp)/'absent.json'
   self.assertEqual(resolve_target(agent_id,absent),{'agent_id':agent_id})
   with self.assertRaisesRegex(ValueError,'--agent-id'):resolve_target(None,absent)
   with self.assertRaises(ValueError):resolve_target('../marketplace',absent)
   supplied=Path(tmp)/'manifest.json';supplied.write_text(json.dumps({'agent_id':'other'}))
   self.assertEqual(resolve_target(agent_id,supplied)['agent_id'],agent_id)
if __name__=='__main__':unittest.main()
