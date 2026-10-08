"""Read-only native classifier replay in the installed gateway image; no answer calls."""
import asyncio,json,time,hashlib,importlib.metadata,os
from pathlib import Path
from litellm import Router
from litellm.router_strategy.complexity_router.complexity_router import ComplexityRouter
APP=Path('/work'); OUT=APP/'results/routing-classifiers-2026-09-30'; CFG=APP/'eval/routing-final-v1/classifiers.json'
config=json.loads(CFG.read_text()); source=APP/'results/core18-gpt5-v2-2026-09-29/comparison.json'
pairs={}
for r in json.loads(source.read_text())['rows']:pairs.setdefault(r['case'],{})[r['model']]=r
keys={l.split('=',1)[0]:l.split('=',1)[1].strip().strip('\"\'') for l in (APP/'.env').read_text().splitlines() if '=' in l and not l.startswith('#')}
r=Router(model_list=[{'model_name':'embedding','litellm_params':{'model':'openai/embedding','api_base':'http://gateway:4000/v1','api_key':keys['EVAL_GATEWAY_KEY']}}],num_retries=0)
state={'version':importlib.metadata.version('litellm'),'config_sha256':hashlib.sha256(CFG.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'decisions':[],'embedding_calls':[]}
def save(): (OUT/'native.json').write_text(json.dumps(state,indent=2))
original_sync=r.embedding;original_async=r.aembedding
# Capture usage only, never credentials; route-index construction also incurs embeddings.
def capture(resp,seconds):
 state['embedding_calls'].append({'usage':resp.usage.model_dump(),'seconds':seconds,'estimated_cost':resp.usage.prompt_tokens*.02/1e6});save();return resp
def emb(*args,**kw):
 t=time.monotonic();return capture(original_sync(*args,**kw),time.monotonic()-t)
async def aemb(*args,**kw):
 t=time.monotonic();resp=await original_async(*args,**kw);return capture(resp,time.monotonic()-t)
r.embedding=emb;r.aembedding=aemb
async def main():
 for mode in ['heuristic','keyword','semantic']:
  cfg={'tiers':config['tiers'],'classifier_type':'heuristic','session_affinity':False}
  if mode!='heuristic':cfg['keyword_tier_rules']=config['semantic_rules' if mode=='semantic' else 'keyword_rules']
  if mode=='semantic':cfg.update(semantic_keyword_matching=True,embedding_model='embedding',match_threshold=config['semantic_threshold'])
  router=ComplexityRouter('offline-'+mode,r,cfg,derive_savings_baseline=False)
  state.setdefault('effective_configs',{})[mode]=router.config.model_dump(mode='json')
  if mode=='semantic':
   t=time.monotonic();await router._ensure_semantic_routelayer();state['semantic_setup_seconds']=time.monotonic()-t
  for cid,pair in sorted(pairs.items()):
   q=pair['eval-nano']['turns'][0]['question'];t=time.monotonic();score=None;signals=[];collisions=[]
   if mode=='semantic':
    # Direct method lets embedding failures fail visibly instead of silently scoring heuristically.
    tier=await router._semantic_tier_override(q,{})
    cause='semantic_match' if tier is not None else 'no_match_heuristic'
   elif mode=='keyword':
    hit=router._lexical_tier_override(q);tier=hit.tier if hit else None;signals=[hit.matched_keyword] if hit else []
    cause='keyword_match' if hit else 'no_match_heuristic'
    collisions=[{'tier':rule['tier'],'keyword':kw} for rule in config['keyword_rules'] for kw in rule['keywords'] if router._keyword_matches(q.lower(),kw)]
   else:tier=None;cause='heuristic'
   if tier is None:tier,score,signals=router.classify(q)
   tier=getattr(tier,'value',tier)
   state['decisions'].append({'method':mode,'case':cid,'tier':tier,'selected':config['tiers'][tier],'score':score,'signals':signals,'cause':cause,'matches':collisions,'seconds':time.monotonic()-t})
   save();print(mode,cid,tier,flush=True)
 if len(state['decisions'])!=54:raise RuntimeError('Incomplete replay')
 save()
asyncio.run(main())
