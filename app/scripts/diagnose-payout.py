"""Six bounded synthesis probes; no DB changes, candidate reruns or judge calls."""
import asyncio,ast,hashlib,json,time
from datetime import datetime,timedelta
from pathlib import Path
from openai import AsyncOpenAI
APP=Path(__file__).resolve().parents[1];BASE=APP/'results/core18-2026-09-28-03';OUT=APP/'results/payout-diagnostic-2026-09-29'
def dump(p,x):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(x,indent=2));t.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
async def main():
 OUT.mkdir(exist_ok=True)
 source=json.loads((BASE/'results.json').read_text())
 # Extract static instructions verbatim, without executing app code or accessing DB.
 tree=ast.parse((BASE/'source/agent.py').read_text());system=None
 for n in ast.walk(tree):
  if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='instructions' for t in n.targets):system=n.value.left.value
 assert system
 system+='\nDiagnostic mode: tools are unavailable. Answer the user question using the supplied saved evidence. Do not claim to execute a payout. If evidence is insufficient, say so.'
 manifest={'source_sha256':sha(BASE/'results.json'),'script_sha256':sha(Path(__file__)),'system':system,'model_alias':'eval-54','configured_model':'gpt-5.4-2026-03-05','reasoning_effort':'low','max_completion_tokens':4096,'estimated_budget_usd':1,'limits':'Synthesis probes, not exact full-agent replays. Static original instructions retained; orientation graph omitted; evidence in user message rather than tool turns. No historical conversation or hidden gold supplied. One sample per condition.'}
 path=OUT/'results.json';state=json.loads(path.read_text()) if path.exists() else {'manifest':manifest,'runs':[]}
 assert state['manifest']==manifest
 dump(path,state)
 env={}
 for l in (APP/'.env').read_text().splitlines():
  if '=' in l and not l.lstrip().startswith('#'):
   k,v=l.split('=',1);env[k.strip()]=v.strip().strip('\"\'')
 api=AsyncOpenAI(base_url='http://localhost:4000/v1',api_key=env['EVAL_GATEWAY_KEY'],max_retries=0,timeout=90)
 try:
  for cid in ['16','17']:
   r=next(r for r in source['results'] if r['case']['id']==cid and 'nano' not in r['model']);t=r['turns'][0];tools=t['run']['metrics']['tool_attempts']
   hist=next(x['result'] for x in tools if x['name']=='get_order_history');docs=next(x['result'] for x in tools if x['name']=='search_documents')
   delivered=next(e['occurred_at'] for e in hist['event_timeline']['rows'] if e['kind']=='deliver');clock=hist['current_records']['snapshot']['clock']
   compact={'snapshot':hist['current_records']['snapshot'],'current_records':hist['current_records']['rows'],'delivery_occurred_at':delivered,'delivery_event_citation':hist['event_timeline']['handle'],'current_records_citation':hist['current_records']['handle'],
    'policy':[c for c in docs['chunks'] if c['id']=='settlement:settlement-v1:5'],'policy_citation':docs['handle']}
   dt=datetime.fromisoformat(delivered);now=datetime.fromisoformat(clock);release=dt+timedelta(hours=24)
   computed={**compact,'computed_timing':{'elapsed_seconds':(now-dt).total_seconds(),'hold_duration_seconds':86400,'release_at':release.isoformat(),'remaining_hold_seconds':max(0,(release-now).total_seconds())}}
   assert (now-dt).total_seconds()==(23 if cid=='16' else 24)*3600
   variants={'raw_evidence':[{'tool':x['name'],'result':x['result']} for x in tools],'compact_evidence':compact,'computed_time':computed}
   for name,evidence in variants.items():
    key=cid+'-'+name
    if any(x['key']==key for x in state['runs']):continue
    assert sum(x['estimated_usd'] for x in state['runs'])+.12<1
    body=json.dumps({'question':t['question'],'evidence':evidence});assert len(body)<30000
    start=time.monotonic();res=await api.chat.completions.create(model='eval-54',messages=[{'role':'system','content':system},{'role':'user','content':body}],reasoning_effort='low',max_completion_tokens=4096)
    u=res.usage;row={'key':key,'case':cid,'condition':name,'input':json.loads(body),'answer':res.choices[0].message.content,'finish_reason':res.choices[0].finish_reason,'usage':u.model_dump(),'gateway_model':res.model,'elapsed_seconds':time.monotonic()-start,'estimated_usd':(u.prompt_tokens*2.5+u.completion_tokens*15)/1e6}
    state['runs'].append(row);dump(path,state);print(key,row['answer'],flush=True)
 finally:await api.close()
 assert sha(BASE/'results.json')==manifest['source_sha256']
 (OUT/'diagnose-payout.py').write_bytes(Path(__file__).read_bytes())
 print('Total new estimate',sum(x['estimated_usd'] for x in state['runs']))
if __name__=='__main__':asyncio.run(main())
