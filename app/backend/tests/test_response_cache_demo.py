import unittest,httpx
from marketplace import response_cache_demo as demo
class CacheDemoTests(unittest.IsolatedAsyncioTestCase):
 def test_namespace_isolates_user_snapshot_and_policy(self):
  base=demo.controls(True,'user1',1,'doc1')
  for scope,revision,doc in [('user2',1,'doc1'),('user1',2,'doc1'),('user1',1,'doc2')]:
   self.assertNotEqual(base['namespace'],demo.controls(True,scope,revision,doc)['namespace'])
  self.assertEqual(base,demo.controls(True,'user1',1,'doc1'))
  self.assertEqual(demo.controls(False,'user1',1,'doc1'),{'no-cache':True,'no-store':True})
 def test_invalid_modes_refused(self):
  valid=dict(available=True,runtime='sdk',routing='off',design='off',memory=False,guardrail='off',loop='normal')
  demo.validate(True,**valid)
  for key,value in [('available',False),('runtime','lyzr'),('routing','fixed_nano'),('design','single'),('memory',True),('guardrail','builtin-privacy'),('loop','tool_error')]:
   with self.assertRaises(ValueError):demo.validate(True,**{**valid,key:value})
 async def test_receipts_use_gateway_cache_header_not_prompt_tokens(self):
  request=httpx.Request('POST','http://gateway/v1/chat/completions')
  def response(headers={}):return httpx.Response(200,request=request,headers={'content-type':'application/json',**headers},json={'id':'response-1','model':'model','usage':{'prompt_tokens_details':{'cached_tokens':123}}})
  with demo.capture():
   await demo.record(response());await demo.record(response({'x-litellm-cache-key':'private-key'}))
   self.assertEqual([x['cache_hit'] for x in demo.observed()],[False,True])
   self.assertNotIn('private-key',str(demo.observed()))
  self.assertEqual(demo.observed(),[])
 async def test_failed_or_non_chat_responses_not_recorded(self):
  with demo.capture():
   await demo.record(httpx.Response(500,request=httpx.Request('POST','http://gateway/v1/chat/completions')))
   self.assertEqual(demo.observed(),[])
