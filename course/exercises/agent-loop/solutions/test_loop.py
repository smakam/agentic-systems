import json
import unittest
import importlib
import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
run_loop=importlib.import_module(os.getenv('LOOP_IMPLEMENTATION','minimal_loop')).run_loop

TOOLS = [{'type':'function','function':{'name':'lookup','parameters':{'type':'object'}}}]
def call(name='lookup', args='{}', id='call-1'):
    return {'id':id,'type':'function','function':{'name':name,'arguments':args}}

class LoopTests(unittest.IsolatedAsyncioTestCase):
    async def run_case(self, outputs, max_turns=8):
        inputs=[]; executed=[]
        async def model(messages, tools):
            inputs.append(messages)
            return outputs.pop(0)
        async def tool(name, args):
            executed.append((name,args))
            return {'status':'ok','rows':[{'quantity':2}]}
        result=await run_loop(model,tool,TOOLS,'Question',instructions='Use evidence',max_turns=max_turns)
        return result,inputs,executed

    async def test_result_returns_to_next_model_call(self):
        result,inputs,executed=await self.run_case([{'content':'Checking','tool_calls':[call()]},{'content':'Two units'}])
        self.assertEqual(result['turns'],2)
        self.assertEqual(inputs[1][-1]['tool_call_id'],'call-1')
        self.assertEqual(json.loads(inputs[1][-1]['content'])['rows'][0]['quantity'],2)
        self.assertEqual(len(executed),1)

    async def test_multiple_calls_are_one_model_turn(self):
        result,_,executed=await self.run_case([{'tool_calls':[call(id='a'),call(id='b')]},{'content':'Done'}])
        self.assertEqual(result['turns'],2)
        self.assertEqual(len(executed),2)

    async def test_unknown_and_invalid_arguments_not_executed(self):
        result,inputs,executed=await self.run_case([{'tool_calls':[call('delete_all'),call(args='{')]},{'content':'Cannot retrieve'}])
        self.assertEqual(executed,[])
        self.assertEqual(json.loads(inputs[1][-1]['content'])['status'],'error')

    async def test_limit_never_makes_next_model_call(self):
        result,inputs,_=await self.run_case([{'tool_calls':[call()]}],1)
        self.assertEqual(len(inputs),1)
        self.assertEqual(result['status'],'turn_limit')

    async def test_error_can_be_repaired(self):
        result,inputs,executed=await self.run_case([{'tool_calls':[call(args='bad')]},{'tool_calls':[call(id='repair')]},{'content':'Two units'}])
        self.assertEqual(len(executed),1)
        self.assertEqual(result['turns'],3)
        self.assertEqual(json.loads(inputs[1][-1]['content'])['status'],'error')

if __name__=='__main__': unittest.main()
