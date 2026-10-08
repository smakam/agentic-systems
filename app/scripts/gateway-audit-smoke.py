"""Synthetic email probe: persist response and read back provider-bound audit."""
import asyncio,json,httpx,os
from marketplace.agent import lf
async def main():
 async with httpx.AsyncClient(base_url='http://backend:8000',timeout=180) as c:
  r=await c.post('/api/login',json={'username':'support','password':'demo-marketplace'});r.raise_for_status();c.headers['x-csrf-token']=r.json()['csrf']
  r=await c.post('/api/conversations',json={});r.raise_for_status();cid=r.json()['id']
  r=await c.post(f'/api/conversations/{cid}/ask',json={'question':'My synthetic demo email is alice@example.com. Repeat the email address.','guardrail':os.getenv('AUDIT_TEST_GUARDRAIL','builtin-privacy'),'memory_enabled':False});r.raise_for_status();d=r.json()
  open('/tmp/gateway-audit-run.json','w').write(json.dumps(d));print(json.dumps({'status':d['status'],'answer':d['answer'],'trace':d['metrics'].get('trace_id')}),flush=True)
  for _ in range(12):
   observations=lf.api.observations.get_many(trace_id=d['metrics']['trace_id'],name='Gateway output → Model input',fields='core,io,metadata').data
   if observations:break
   await asyncio.sleep(2)
  assert observations,'Provider audit missing'
  assert all('alice@example.com' not in str(o.input) for o in observations)
  assert any('EMAIL_REDACTED' in str(o.input) or 'EMAIL_ADDRESS' in str(o.input) for o in observations)
  open('/tmp/gateway-audit-observations.json','w').write(json.dumps([o.dict() for o in observations],default=str))
  print('PASS: masked gateway request in linked Langfuse observation',flush=True)
asyncio.run(main())
