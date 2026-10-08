"""Isolated live routing pilot. No support edits, no paid judge, no gold in model inputs."""
import asyncio,hashlib,json,os,time,random,sys
from pathlib import Path
from datetime import timedelta
from sqlalchemy import text
from openai.resources.chat.completions import AsyncCompletions
from openai.resources.embeddings import AsyncEmbeddings
from marketplace import agent,tools
from marketplace.db import Session,Conversation,State,engine,init_schema
from marketplace.eval_fixtures import guard_database,fixture,fingerprint,snapshot

OUT=Path('/results/routing-granularity-2026-09-30');OUT.mkdir(exist_ok=True)
SPEC=Path('/eval/routing-final-v1/conversations.json');spec=json.loads(SPEC.read_text())
PROMPT=Path('/eval/routing-v2-prompt.txt').read_text()
CONFIGS={'eval-nano':{'alias':'eval-nano','model':'gpt-5-nano-2025-08-07','input_rate':.05,'cached_rate':.005,'output_rate':.4,'budget':.5},'eval-5':{'alias':'eval-5','model':'gpt-5','input_rate':1.25,'cached_rate':.125,'output_rate':10.,'budget':.5}}
POLICIES=['always_nano','always_gpt5','conversation','question']
SCHEMA={'type':'object','properties':{'tier':{'type':'string','enum':['SIMPLE','COMPLEX']},'reason':{'type':'string'}},'required':['tier','reason'],'additionalProperties':False}
manifest={'spec_sha256':hashlib.sha256(SPEC.read_bytes()).hexdigest(),'classifier_prompt_sha256':hashlib.sha256(PROMPT.encode()).hexdigest(),'source_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('/app/marketplace').glob('*.py')},'runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'candidates':CONFIGS,'policy':'Single fixed model per question, same DatabaseSession across all turns. Classifier sees current question plus prior user/assistant messages, never gold or future turns. No fallback if classifier fails.','budget_usd':3.0,'order_seed':930,'grading':'Assistant review against frozen expected records/text; no paid judge.','cache':'Natural shared provider cache, randomized policy order. No claimed cold-start or causal switch penalty.','prices_checked':'2026-09-30','pricing_sources':['https://developers.openai.com/api/docs/models/gpt-5','https://developers.openai.com/api/docs/models/gpt-5-nano'],'fixture_version':'payout-v2'}
def dump(path,data):
 p=Path(path);tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2,default=str));tmp.replace(p)
state={'manifest':manifest,'results':[],'calls':[],'status':'prepared'}
if (OUT/'results.json').exists():
 state=json.loads((OUT/'results.json').read_text());assert state['manifest']==manifest,'Frozen input changed; do not mix results'
def save():dump(OUT/'results.json',state)
current={};counter=len(state['calls'])
def spend():return sum(x.get('full_price_usd',0) for x in state['calls'])+sum(.2 for x in state['calls'] if 'usage' not in x)
def cost(usage,model):
 if model=='embedding':i=usage.get('prompt_tokens',usage.get('total_tokens',0));return i*.02/1e6,i*.02/1e6,0
 p=CONFIGS[model];i=usage['prompt_tokens'];o=usage['completion_tokens'];c=(usage.get('prompt_tokens_details') or {}).get('cached_tokens',0) or 0
 assert 0<=c<=i
 return (i*p['input_rate']+o*p['output_rate'])/1e6,((i-c)*p['input_rate']+c*p['cached_rate']+o*p['output_rate'])/1e6,c
orig=AsyncCompletions.create;origemb=AsyncEmbeddings.create
async def capture(self,*args,**kwargs):
 global counter
 assert spend()+.2<manifest['budget_usd'],'Experiment budget reserve reached'
 counter+=1;name=f'call-{counter:04d}';rec={**current,'name':name,'requested_model':kwargs['model'],'kind':current.get('kind','candidate')};state['calls'].append(rec);save()
 def convert(v):
  if hasattr(v,'model_dump'):return v.model_dump(exclude_none=True)
  if type(v).__name__ in ('NotGiven','Omit'):return None
  raise TypeError(type(v).__name__)
 (OUT/(name+'-request.json')).write_text(json.dumps(kwargs,indent=2,default=convert));t=time.monotonic()
 try:
  result=await orig(self,*args,**kwargs);dump(OUT/(name+'-response.json'),result.model_dump())
  u=result.usage.model_dump();full,cached,c=cost(u,kwargs['model']);rec.update(usage=u,returned_model=result.model,seconds=time.monotonic()-t,full_price_usd=full,cached_price_usd=cached,cached_tokens=c,finish_reason=result.choices[0].finish_reason)
  save();return result
 except BaseException as ex:rec.update(error=type(ex).__name__,seconds=time.monotonic()-t);save();raise
async def capture_emb(self,*args,**kwargs):
 t=time.monotonic();r=await origemb(self,*args,**kwargs);u=r.usage.model_dump();full,cached,c=cost(u,'embedding')
 state['calls'].append({**current,'kind':'embedding','requested_model':'embedding','returned_model':r.model,'usage':u,'full_price_usd':full,'cached_price_usd':cached,'seconds':time.monotonic()-t});save();return r
AsyncCompletions.create=capture;AsyncEmbeddings.create=capture_emb
async def classify(cid,q):
 with Session() as db:history=db.get(Conversation,cid).items[-12:]
 # Prior answers are available conversation context, not benchmark answers from another policy.
 req={'model':'eval-nano','messages':[{'role':'system','content':PROMPT},{'role':'user','content':json.dumps({'prior_conversation':history,'current_question':q})}],'reasoning_effort':'low','max_completion_tokens':1024,'response_format':{'type':'json_schema','json_schema':{'name':'routing_decision','strict':True,'schema':SCHEMA}}}
 api=tools.client();current['kind']='classifier'
 try:
  r=await api.chat.completions.create(**req);assert r.choices[0].finish_reason=='stop';d=json.loads(r.choices[0].message.content);assert d['tier'] in ('SIMPLE','COMPLEX');return {**d,'selected':'eval-nano' if d['tier']=='SIMPLE' else 'eval-5'}
 finally:await api.close();current['kind']='candidate'
def mutate(f,turn):
 if turn.get('before')=='purchase_canvas':f.purchase('listing-1','NEW')
 if turn.get('before')=='advance_90_minutes':
  # Clock progression is a scripted fixture mutation, identical across all policies.
  with Session.begin() as db:db.get(State,1).clock+=timedelta(minutes=90)
def validate(sid,idx):
 with Session() as db:
  if sid=='S4':assert db.execute(text("SELECT unpaid FROM analytics.seller_balances WHERE seller_id='seller-1'")).scalar()==(449820 if idx==0 else 674730)
  if sid=='S5':
   elapsed=db.execute(text("SELECT EXTRACT(EPOCH FROM (s.clock-h.delivered_at))/3600 FROM state s,shipments h WHERE h.id NOT LIKE 'shipment-%' AND h.delivered_at IS NOT NULL")).scalar()
   assert float(elapsed)==(23 if idx==0 else 24.5),elapsed
async def main():
 guard_database();init_schema();lock=engine.connect();assert lock.execute(text('SELECT pg_try_advisory_lock(938271)')).scalar(),'Another evaluator holds the lock'
 cache=json.loads(Path('/results/embedding-cache.json').read_text());assert cache
 dry='--dry-run' in sys.argv
 rng=random.Random(930);orders={s['id']:rng.sample(POLICIES,len(POLICIES)) for s in spec['sessions']}
 state['policy_order']=orders;save()
 if dry:
  checks=[]
  for s in spec['sessions']:
   fingerprints=[]
   for repeat in range(2):
    f=fixture(s['fixture'],cache);seq=[]
    for idx,turn in enumerate(s['turns']):
     mutate(f,turn);validate(s['id'],idx);seq.append(fingerprint())
     if repeat==0:dump(OUT/f"oracle-{s['id']}-{idx+1}.json",snapshot())
    fingerprints.append(seq)
   assert fingerprints[0]==fingerprints[1];checks.append({'session':s['id'],'fingerprints':fingerprints[0],'repeatable':True})
  dump(OUT/'fixture-validation.json',checks);state['status']='fixtures_validated';save();print('Six repeatable scenarios validated; no paid calls',flush=True);return
 assert (OUT/'fixture-validation.json').exists(),'Dry-run fixtures first'
 archive=OUT/'source';archive.mkdir(exist_ok=True)
 for p in Path('/app/marketplace').glob('*.py'):(archive/p.name).write_bytes(p.read_bytes())
 (OUT/'conversations.json').write_bytes(SPEC.read_bytes());(OUT/'classifier-prompt.txt').write_text(PROMPT)
 state['status']='running';save()
 for s in spec['sessions']:
  for policy in orders[s['id']]:
   key=s['id']+'-'+policy;existing=next((r for r in state['results'] if r['key']==key),None)
   if existing:
    assert existing['status']=='complete','Interrupted scenario: preserve it and use a new run rather than overwrite';continue
   f=fixture(s['fixture'],cache);cid='routing-'+key
   with Session.begin() as db:db.add(Conversation(id=cid,owner_id='support',title=key,items=[]))
   record={'key':key,'session':s['id'],'policy':policy,'conversation_id':cid,'turns':[],'status':'running'};state['results'].append(record);save();pinned=None
   for idx,turn in enumerate(s['turns']):
    mutate(f,turn);validate(s['id'],idx);before=fingerprint();q=turn['question']
    for alias,x in f.aliases.items():
     if 'order' in x:q=q.replace(alias,x['order'])
    current.clear();current.update(session=s['id'],policy=policy,turn=idx+1,kind='candidate');start=time.monotonic()
    if policy in ('conversation','question'):
     if pinned is None or policy=='question':decision=await classify(cid,q);pinned=decision
     else:decision={**pinned,'reused_session_pin':True}
     selected=decision['selected']
    else:selected='eval-nano' if policy=='always_nano' else 'eval-5';decision={'selected':selected,'reason':'fixed control'}
    result=await agent.answer(cid,q,evaluation_config=CONFIGS[selected]);assert fingerprint()==before,'Unexpected business mutation'
    record['turns'].append({'question':q,'decision':decision,'selected':selected,'run':result,'end_to_end_seconds':time.monotonic()-start,'fixture_hash':before,'business_unchanged':True,'expected':turn})
    save();print(key,idx+1,selected,result['status'],'full-price spend',round(spend(),4),flush=True)
    if result['status']!='completed':state['status']='candidate_failure_stopped';save();return
   record['status']='complete';save()
 state['status']='collected_pending_assistant_review';save()
 if agent.lf:agent.lf.flush()
 lock.close();engine.dispose()
asyncio.run(main())
