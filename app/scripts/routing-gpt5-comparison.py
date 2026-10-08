"""Offline first-question routing replay: nano LLM versus JEV; no answer/judge calls."""
import asyncio,json,time,hashlib,html
from pathlib import Path
from collections import Counter
import httpx
from openai import AsyncOpenAI
APP=Path(__file__).resolve().parents[1];OUT=APP/'results/routing-gpt5-llm-jev-2026-09-29';OUT.mkdir(exist_ok=True)
SOURCE=APP/'results/core18-gpt5-v2-2026-09-29/comparison.json'
PROMPT=(APP/'eval/routing-v2-prompt.txt').read_text()
MAP={'SIMPLE':'eval-nano','COMPLEX':'eval-5'}
SCHEMA={'type':'object','properties':{'tier':{'type':'string','enum':list(MAP)},'reason':{'type':'string'}},'required':['tier','reason'],'additionalProperties':False}
CRITERIA={'SIMPLE':'Direct bounded lookup or ordinary aggregate with clear entities and meaning; no causal explanation, policy application, event reconstruction or material ambiguity. Select inexpensive GPT-5 nano.','COMPLEX':'Causal explanation, event history, policy applied to state, time eligibility, incident scope, ambiguous money movement, reconciliation, conflicting evidence or permissions handling. Select GPT-5; also use if necessary reasoning is uncertain.'}
def save(p,d):
 t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2));t.replace(p)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def env():return {l.split('=',1)[0]:l.split('=',1)[1].strip().strip('\"\'') for l in (APP/'.env').read_text().splitlines() if '=' in l and not l.startswith('#')}
DATA=json.loads(SOURCE.read_text());PAIRS={}
for r in DATA['rows']:PAIRS.setdefault(r['case'],{})[r['model']]=r
for pair in PAIRS.values():assert pair['eval-nano']['fixture_hash']==pair['eval-5']['fixture_hash']
MANIFEST={'source_sha256':sha(SOURCE),'script_sha256':sha(Path(__file__)),'prompt_sha256':sha(APP/'eval/routing-v2-prompt.txt'),'mapping':MAP,'policy':'Opening question only; pin entire saved case including follow-ups','llm':'gpt-5-nano-2025-08-07 via eval-nano on local LiteLLM','jev':'typesafe/jev-1.13 via OpenRouter Decisions API, direct experimental call, not local gateway','criteria':CRITERIA,'budget_usd':.10,'grading':'Current comparison grades with user adjudications; mixed human/assistant provenance','candidates':'Saved answer replay, no regeneration, no judge','sources':['https://openrouter.ai/blog/insights/what-is-jev/','https://openrouter.ai/typesafe/jev-1.13/api'],'input_boundary':'No gold, grade, saved answer, case records or later questions in classifier requests.'}
STATEPATH=OUT/'decisions.json'
STATE=json.loads(STATEPATH.read_text()) if STATEPATH.exists() else {'manifest':MANIFEST,'llm':[],'jev':[],'errors':[]}
assert STATE['manifest']==MANIFEST,'Changed inputs; use new experiment directory'
save(STATEPATH,STATE);(OUT/'prompt.txt').write_text(PROMPT)
async def main():
 keys=env()
 async with AsyncOpenAI(base_url='http://localhost:4000/v1',api_key=keys['EVAL_GATEWAY_KEY'],max_retries=0,timeout=60) as api:
  for cid,pair in sorted(PAIRS.items()):
   if any(x['case']==cid for x in STATE['llm']):continue
   assert sum(x['cost'] for x in STATE['llm'])+.003<.10
   q=pair['eval-nano']['turns'][0]['question'];start=time.monotonic()
   req={'model':'eval-nano','messages':[{'role':'system','content':PROMPT},{'role':'user','content':q}],'reasoning_effort':'low','max_completion_tokens':1024,'response_format':{'type':'json_schema','json_schema':{'name':'routing_decision','strict':True,'schema':SCHEMA}}}
   save(OUT/f'llm-{cid}-request.json',req)
   try:
    r=await api.chat.completions.create(**req);raw=r.model_dump();save(OUT/f'llm-{cid}-response.json',raw)
    parsed=json.loads(r.choices[0].message.content);assert parsed['tier'] in MAP and r.choices[0].finish_reason=='stop'
    STATE['llm'].append({'case':cid,'tier':parsed['tier'],'selected':MAP[parsed['tier']],'reason':parsed['reason'],'cost':(r.usage.prompt_tokens*.05+r.usage.completion_tokens*.4)/1e6,'cost_basis':'uncached list-rate estimate','seconds':time.monotonic()-start})
   except Exception as ex:
    STATE['errors'].append({'classifier':'llm','case':cid,'type':type(ex).__name__});save(STATEPATH,STATE);raise
   save(STATEPATH,STATE);print('LLM',cid,parsed['tier'],flush=True)
 async with httpx.AsyncClient(timeout=60) as api:
  for cid,pair in sorted(PAIRS.items()):
   if any(x['case']==cid for x in STATE['jev']):continue
   assert sum(x['cost'] for x in STATE['llm']+STATE['jev'])+.003<.10
   q=pair['eval-nano']['turns'][0]['question'];start=time.monotonic()
   req={'model':'typesafe/jev-1.13','state':q,'questions':{'tier':{'type':'choice','instructions':PROMPT.replace('Return SIMPLE or COMPLEX and a brief task-based reason.','Choose SIMPLE or COMPLEX.'),'criteria':CRITERIA}}}
   save(OUT/f'jev-{cid}-request.json',req)
   try:
    r=await api.post('https://openrouter.ai/api/alpha/decisions',json=req,headers={'Authorization':'Bearer '+keys['OPENROUTER_API_KEY']});raw=r.json();save(OUT/f'jev-{cid}-response.json',raw);r.raise_for_status()
    choice=raw['answers']['tier'];tier=choice['choice'];assert tier in MAP
    usage=raw['usage'];cost=usage.get('cost');basis='provider-reported usage.cost'
    if cost is None:cost=usage['input_tokens']*.042/1e6;basis='input list-rate estimate; usage.cost absent'
    STATE['jev'].append({'case':cid,'tier':tier,'selected':MAP[tier],'probabilities':choice.get('probabilities'),'confidence':choice.get('confidence'),'cost':cost,'cost_basis':basis,'seconds':time.monotonic()-start,'served_model':raw.get('model')})
   except Exception as ex:
    STATE['errors'].append({'classifier':'jev','case':cid,'type':type(ex).__name__,'status':r.status_code if 'r' in locals() else None});save(STATEPATH,STATE);print('JEV blocked; saved error, no fabricated fallback score.',flush=True);break
   save(STATEPATH,STATE);print('JEV',cid,tier,flush=True)
 summarize()
def agg(rows,overhead=0):
 c=Counter(r['review']['grade'] for r in rows);cost=sum(r['cost'] for r in rows)+overhead
 return {'correct':c['correct'],'partial':c['partially_correct'],'incorrect':c['incorrect'],'fully_correct_percent':100*c['correct']/len(rows),'estimated_total_cost':cost,'classifier_cost':overhead}
def summarize():
 assert sha(SOURCE)==MANIFEST['source_sha256'];result={'always_nano':agg([p['eval-nano'] for p in PAIRS.values()]),'always_gpt5':agg([p['eval-5'] for p in PAIRS.values()])}
 for mode in ['llm','jev']:
  decisions=STATE[mode]
  if len(decisions)==18:
   result[mode]={**agg([PAIRS[x['case']][x['selected']] for x in decisions],sum(x['cost'] for x in decisions)),'selection_counts':dict(Counter(x['selected'] for x in decisions)),'classifier_seconds_mean':sum(x['seconds'] for x in decisions)/18}
 save(OUT/'summary.json',{'policies':result,'new_classifier_spend':sum(x['cost'] for mode in ['llm','jev'] for x in STATE[mode]),'errors':STATE['errors']})
 print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':asyncio.run(main())
