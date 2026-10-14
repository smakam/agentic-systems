import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock
from openai import AsyncOpenAI
from agents import Agent, OpenAIChatCompletionsModel, ModelSettings
from marketplace.agent_design_demo import execute, Review, validate, configuration

class Session:
    session_id='owned-test-conversation'
    def __init__(self): self.committed=[]
    async def get_items(self,limit=None): return []
    async def add_items(self,items): self.committed.extend(items)

class Item:
    def __init__(self,value): self.value=value
    def to_input_item(self): return self.value

class WorkflowTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.api=AsyncOpenAI(api_key='unit-test-not-a-real-key')
        self.agent=Agent(name='base',instructions='read only',model=OpenAIChatCompletionsModel(model='eval-nano',openai_client=self.api),model_settings=ModelSettings())
        self.session=Session();self.state={};self.calls=[]
        self.settings=configuration('review','nano','gpt54')['workflow']
        self.ctx=SimpleNamespace(evidence={'record':{'rows':[{'quantity':2}]}})
    async def asyncTearDown(self): await self.api.close()
    def fake(self,revision=False,fail_review=False):
        async def run(agent,payload,**kwargs):
            self.calls.append((agent.name,payload,kwargs))
            if agent.name.endswith('Generator'):
                await kwargs['session'].add_items([{'role':'user','content':'question'},{'role':'assistant','content':'draft'}])
                return SimpleNamespace(final_output='draft',to_input_list=lambda:[{'role':'user','content':'question'},{'role':'assistant','content':'draft'}])
            if agent.name.startswith('Reviewer'):
                self.assertFalse(agent.tools);self.assertFalse(agent.mcp_servers)
                if fail_review:raise RuntimeError('unavailable')
                return SimpleNamespace(final_output=Review(needs_revision=revision,issues=['wrong quantity'] if revision else [],correction_instructions='verify quantity',sufficient_evidence=True))
            return SimpleNamespace(final_output='corrected',new_items=[Item({'type':'function_call','call_id':'c1'}),Item({'type':'function_call_output','call_id':'c1','output':'2'}),Item({'role':'assistant','content':'corrected'})])
        return run
    async def invoke(self,run,timeout=5):
        return await execute(self.agent,'question',self.session,self.ctx,None,self.api,None,None,None,self.settings,self.state,8,timeout,run=run)
    async def test_accept_commits_draft_and_no_correction(self):
        self.assertEqual(await self.invoke(self.fake()),'draft')
        self.assertEqual(len(self.calls),2);self.assertEqual(self.state['decision'],'accept_draft')
        self.assertEqual(self.session.committed[-1]['content'],'draft')
    async def test_correction_keeps_tools_without_feedback_in_history(self):
        self.assertEqual(await self.invoke(self.fake(revision=True)),'corrected')
        self.assertEqual(len(self.calls),3);self.assertTrue(self.state['correction_performed'])
        self.assertNotIn('draft',[i.get('content') for i in self.session.committed])
        self.assertEqual(self.session.committed[-1]['content'],'corrected')
        self.assertEqual(sum(i.get('role')=='user' for i in self.session.committed),1)
        self.assertEqual(self.session.committed[1]['call_id'],self.session.committed[2]['call_id'])
    async def test_reviewer_failure_never_commits_unreviewed_draft(self):
        with self.assertRaises(RuntimeError):await self.invoke(self.fake(fail_review=True))
        self.assertEqual(self.session.committed,[]);self.assertEqual(self.state['status'],'failed')
        self.assertEqual(self.state['stages'][-1]['status'],'failed')
    async def test_deadline_prevents_model_call(self):
        with self.assertRaises(TimeoutError):await self.invoke(self.fake(),timeout=0)
        self.assertEqual(self.calls,[]);self.assertEqual(self.session.committed,[])
    def test_config_restricts_aliases_and_workspace(self):
        for mode,gen,rev,runtime,available in [('review','nano','gpt54','sdk',False),('review','nano','gpt54','google',True),('review','arbitrary','gpt54','sdk',True)]:
            with self.assertRaises(ValueError):validate(mode,gen,rev,runtime,available)
        self.assertEqual(configuration('review','nano','gpt54')['workflow']['reviewer_alias'],'eval-54')

if __name__=='__main__':unittest.main()
