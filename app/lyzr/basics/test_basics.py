import json,unittest
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
if __name__=='__main__':unittest.main()
