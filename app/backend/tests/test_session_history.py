import asyncio,copy,unittest
from marketplace.session_history import select_history,compact_history
class HistoryTests(unittest.TestCase):
 def fixture(self,n):
  return [x for i in range(n) for x in [{'role':'user','content':f'question {i}'},{'type':'function_call','call_id':str(i),'name':'lookup','arguments':'{}'},{'type':'function_call_output','call_id':str(i),'output':'record'},{'role':'assistant','content':f'answer {i}'}]]
 def test_windows_keep_pairs_and_storage(self):
  source=self.fixture(7);before=copy.deepcopy(source)
  for mode,expected in [('window2',2),('window6',6),('window8',7),('off',6)]:
   selected,meta=asyncio.run(select_history(source,mode));self.assertEqual(meta['recent_blocks'],expected);self.assertEqual(len(selected),expected*4)
  self.assertEqual(source,before)
 def test_manual_any_length_reuse_and_new_exchange(self):
  seen=[]
  async def summarize(xs):seen.append(xs);return 'Remember sample label.'
  for n in (1,7,10):
   source=self.fixture(n);state,generated=asyncio.run(compact_history(source,summarize));self.assertTrue(generated);self.assertEqual(state['source_blocks'],n)
   selected,m=asyncio.run(select_history(source,'off',cached=state));self.assertEqual(m['recent_blocks'],0);self.assertEqual(len(selected),1)
   same,generated=asyncio.run(compact_history(source,summarize,state));self.assertFalse(generated)
   selected,m=asyncio.run(select_history(self.fixture(n+1),'window2',cached=state));self.assertEqual(m['recent_blocks'],1);self.assertEqual(len(selected),5)
  self.assertEqual(len(seen),3)
 def test_stale_summary_not_reused(self):
  async def summarize(xs):return 'summary'
  state,_=asyncio.run(compact_history(self.fixture(7),summarize));source=self.fixture(7);source[0]['content']='changed'
  _,new=asyncio.run(select_history(source,'off',cached=state));self.assertIsNone(new['summary'])
 def test_invalid_pair_rejected(self):
  with self.assertRaises(ValueError):asyncio.run(select_history([{'role':'user','content':'x'},{'type':'function_call','call_id':'bad'}],'window2'))
 def test_excludes_reasoning_and_rejects_empty(self):
  seen=[]
  async def summarize(xs):seen.extend(xs);return 'summary'
  source=self.fixture(1);source[0]['id']='internal-sdk-id';source.insert(1,{'type':'reasoning','content':'private'})
  state,_=asyncio.run(compact_history(source,summarize));_,m=asyncio.run(select_history(source,'off',cached=state));self.assertFalse(any(x.get('type')=='reasoning'for x in seen+m['selected_history']));self.assertFalse(any('id'in x for x in seen))
  async def empty(xs):return ''
  with self.assertRaises(ValueError):asyncio.run(compact_history(source,empty))
  with self.assertRaises(ValueError):asyncio.run(compact_history([],summarize))
if __name__=='__main__':unittest.main()
