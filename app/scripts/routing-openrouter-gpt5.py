"""Bounded Auto Router selection probes; saved answer replay, not answer evaluation."""
import asyncio,json,time
from pathlib import Path
import httpx
APP=Path(__file__).resolve().parents[1];OUT=APP/'results/routing-gpt5-llm-jev-2026-09-29';source=APP/'results/core18-gpt5-v2-2026-09-29/comparison.json'
d=json.loads(source.read_text());pairs={}
for row in d['rows']:pairs.setdefault(row['case'],{})[row['model']]=row
prompt=(APP/'eval/routing-v2-prompt.txt').read_text();context=prompt.split('APPLICATION AND AVAILABLE TOOLS\n',1)[1].split('\n\nWHAT MAKES',1)[0]+'\n\nAPPLICATION ONTOLOGY\n'+prompt.split('APPLICATION ONTOLOGY (generic definitions, not case records)\n',1)[1]
def save(p,d):p.write_text(json.dumps(d,indent=2))
p=OUT/'openrouter-decisions.json';state=json.loads(p.read_text()) if p.exists() else {'policy':'low cost tier, nano/GPT-5 only, first question pinned for offline replay','probe':'16 completion tokens; includes completion invocation; not classifier-only latency or cost','context':context,'decisions':[],'errors':[]}
async def main():
 env={l.split('=',1)[0]:l.split('=',1)[1].strip().strip('\"\'') for l in (APP/'.env').read_text().splitlines() if '=' in l and not l.startswith('#')}
 async with httpx.AsyncClient(timeout=60) as api:
  for cid,pair in sorted(pairs.items()):
   if any(x['case']==cid for x in state['decisions']):continue
   assert sum(x['probe_cost'] for x in state['decisions'])+.01<.10
   req={'model':'openrouter/auto','session_id':'routing-gpt5-offline-20260929-'+cid,'messages':[{'role':'system','content':context},{'role':'user','content':pair['eval-nano']['turns'][0]['question']}],'plugins':[{'id':'auto-router','allowed_models':['openai/gpt-5-nano','openai/gpt-5'],'cost_tier':'low'}],'max_tokens':16,'reasoning':{'effort':'low'}}
   save(OUT/f'auto-{cid}-request.json',req);start=time.monotonic()
   try:
    resp=await api.post('https://openrouter.ai/api/v1/chat/completions',json=req,headers={'Authorization':'Bearer '+env['OPENROUTER_API_KEY'],'X-OpenRouter-Metadata':'enabled'});raw=resp.json();save(OUT/f'auto-{cid}-response.json',raw);resp.raise_for_status()
    model=raw['model'];assert model in ['openai/gpt-5-nano','openai/gpt-5','openai/gpt-5-nano-2025-08-07','openai/gpt-5-2025-08-07'],model
    alias='eval-nano' if 'nano' in model else 'eval-5';u=raw['usage'];cost=u.get('cost');assert cost is not None,'Missing cost'
    state['decisions'].append({'case':cid,'selected':alias,'model':model,'probe_cost':cost,'probe_seconds':time.monotonic()-start,'metadata':raw.get('openrouter_metadata'),'usage':u});save(p,state);print('AUTO',cid,model,flush=True)
   except Exception as ex:
    state['errors'].append({'case':cid,'error':type(ex).__name__});save(p,state);print('Auto Router stopped; inspect saved response; no fallback score.',flush=True);break
 save(p,state)
asyncio.run(main())
