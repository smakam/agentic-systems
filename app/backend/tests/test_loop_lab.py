import json
import os
import unittest
from unittest.mock import patch
from marketplace.loop_lab import validate, inject_once, enabled

class LabTests(unittest.IsolatedAsyncioTestCase):
    def test_lab_controls_fail_closed(self):
        with patch('marketplace.loop_lab.enabled',return_value=False):
            validate('normal')
            for mode in ('tool_error','turn_limit'):
                with self.assertRaises(ValueError): validate(mode)
        with patch('marketplace.loop_lab.enabled',return_value=True):
            with self.assertRaises(ValueError): validate('tool_error','google')
            validate('tool_error')

    def test_only_matching_test_and_legacy_databases_are_enabled(self):
        from types import SimpleNamespace
        for database, reader, flag, expected in (
            ('market_test','market_test','true',True),
            ('ch11_loop_lab','ch11_loop_lab','true',True),
            ('market','market','true',False),
            ('market_eval','market_eval','true',False),
            ('market_test','market','true',False),
            ('market_test','market_test','false',False),
        ):
            with self.subTest(database=database,reader=reader,flag=flag):
                with patch('marketplace.db.engine',SimpleNamespace(url=SimpleNamespace(database=database))), patch('marketplace.loop_lab.setting',return_value=flag), patch.dict(os.environ,{'READ_DATABASE_URL':'postgresql://reader@localhost/'+reader}):
                    self.assertEqual(enabled(),expected)

    async def test_error_is_once_per_investigation_and_skips_execution(self):
        class Server:
            def __init__(self): self.calls=[]
            async def call_tool(self,name,args):
                self.calls.append((name,args)); return 'real-result'
        server=Server(); state=inject_once(server)
        await server.call_tool('get_catalog',{})
        result=await server.call_tool('query_business_data',{'sql':'SELECT 1'})
        self.assertEqual(json.loads(result.content[0].text)['code'],'LAB_TEMPORARY_READ_FAILURE')
        self.assertEqual(len(server.calls),1)
        self.assertEqual(await server.call_tool('query_business_data',{'sql':'SELECT 1'}),'real-result')
        self.assertEqual(len(server.calls),2)
        self.assertTrue(state['injected'])

    async def test_hook_classifies_mcp_error_payload(self):
        from types import SimpleNamespace
        from marketplace.agent import BudgetHooks
        hooks=BudgetHooks()
        tool=SimpleNamespace(name='query_business_data')
        await hooks.on_tool_start(SimpleNamespace(tool_arguments='{}'),None,tool)
        await hooks.on_tool_end(None,None,tool,json.dumps({'type':'text','text':json.dumps({'status':'error','code':'LAB_TEMPORARY_READ_FAILURE'})}))
        self.assertEqual(hooks.tool_attempts[0]['status'],'error')
        self.assertEqual(hooks.tool_attempts[0]['result']['code'],'LAB_TEMPORARY_READ_FAILURE')
