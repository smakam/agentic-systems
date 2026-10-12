import asyncio, os, unittest
from unittest.mock import patch
from marketplace.gateway_identity import current_key, for_role
from marketplace.mcp_client import open_mcp

class GatewayIdentityTests(unittest.TestCase):
 def test_concurrent_roles_do_not_share_or_leak_keys(self):
  async def check():
   ready=asyncio.Event();seen=[]
   async def operator():
    with for_role('operator'):
     ready.set();await asyncio.sleep(.01);seen.append(('operator',current_key()))
   async def support():
    await ready.wait()
    with for_role('support'):
     await asyncio.sleep(.02);seen.append(('support',current_key()))
   await asyncio.gather(operator(),support())
   self.assertCountEqual(seen,[('operator','operator-test'),('support','support-test')])
   self.assertEqual(current_key(),'support-test')
  with patch.dict(os.environ,{'LITELLM_API_KEY':'support-test','OPERATOR_GATEWAY_KEY':'operator-test'}):asyncio.run(check())
 def test_exception_restores_previous_identity(self):
  with patch.dict(os.environ,{'LITELLM_API_KEY':'support-test','OPERATOR_GATEWAY_KEY':'operator-test'}):
   with self.assertRaises(ValueError):
    with for_role('operator'):raise ValueError('validation failure')
   self.assertEqual(current_key(),'support-test')
 def test_mcp_receives_only_selected_key(self):
  with patch.dict(os.environ,{'LITELLM_API_KEY':'support-test','OPERATOR_GATEWAY_KEY':'operator-test','OPENAI_API_KEY':'must-not-pass'}):
   with patch('marketplace.mcp_client.MCPServerStdio') as server:
    with for_role('operator'):open_mcp()
    env=server.call_args.kwargs['params']['env']
    self.assertEqual(env['LITELLM_API_KEY'],'operator-test')
    self.assertNotIn('OPENAI_API_KEY',env);self.assertNotIn('OPERATOR_GATEWAY_KEY',env)
if __name__=='__main__':unittest.main()
