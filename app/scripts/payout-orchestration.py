"""Isolated three-topology experiment; no support app behavior changes."""
import asyncio,ast,hashlib,importlib.util,json,os,time,shutil,re
from pathlib import Path
from contextlib import nullcontext
from sqlalchemy import text
from agents import Agent,Runner,RunHooks,ModelSettings,function_tool,OpenAIChatCompletionsModel
from openai.types.shared import Reasoning
from marketplace import agent as baseline
from marketplace.db import engine,init_schema
from marketplace.eval_fixtures import guard_database,fingerprint
from marketplace.mcp_client import open_mcp,RemoteReadContext
from marketplace.tools import client
spec=importlib.util.spec_from_file_location('fixture_module',Path(__file__).with_name('payout-orchestration-fixture.py'));fm=importlib.util.module_from_spec(spec);spec.loader.exec_module(fm)
OUT=Path(os.getenv('ORCHESTRATION_OUT','/results/payout-orchestration-v2-2026-10-01'))
MODES=['serial','parallel','workers']
QUESTION='Which sellers still have money payable? Investigate every payout, including zero-due and completed controls. For each, explain the supported reason for its current outcome and what remains unknown; summarize unpaid totals by seller. Do not execute business actions.'
FORMAT='''Return JSON only, without Markdown fences: {"payouts":[{"payout_id":"...","seller_id":"...","seller_name":"...","order_id":"...","payable_paise":0,"reason":"plain-language supported explanation","evidence_handles":["evidence-..."]}],"sellers":[{"seller_id":"...","unpaid_paise":0}],"unknowns":[]}. Include every payout, including completed and zero-due controls; unpaid totals exclude completed payouts. Explanations distinguish a past failed attempt from the latest successful result. Use actual records and applicable policies; no invented failure causes. This JSON is an experimental reporting contract, not a new support UI format.'''
source=Path(baseline.__file__).read_text();tree=ast.parse(source);fn=next(n for n in tree.body if isinstance(n,ast.AsyncFunctionDef) and n.name=='_answer')
BASE=next(ast.literal_eval(n.value) for n in fn.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='instructions' for t in n.targets))
# Same business rules as baseline; override only the simple-lookups output format.
COMMON=BASE+'\nThis is a broad investigation. '+FORMAT
class Limit(RuntimeError):pass
class Metrics(RunHooks):
    def __init__(self):self.calls=0;self.input=0;self.output=0;self.cached=0;self.active=0;self.tools=[];self.inputs=[];self.model_intervals=[];self.pending={};self.started=time.monotonic();self.evidence={};self.worker_outputs=[];self.trace_id=None
    @property
    def cost(self):return (2.5*self.input+15*self.output)/1e6
    async def on_llm_start(self,ctx,a,system_prompt,input_items):
        if self.calls>=32 or self.cost+self.active*.3>=2.5:raise Limit('Aggregate model-call or dollar guard')
        self.calls+=1;self.active+=1
        self.pending[id(a)]=time.monotonic()-self.started
        self.inputs.append({'agent':a.name,'instructions':system_prompt,'input_items':input_items,'at_seconds':time.monotonic()-self.started})
    async def on_llm_end(self,ctx,a,response):
        self.active-=1;self.input+=response.usage.input_tokens;self.output+=response.usage.output_tokens
        self.cached+=getattr(getattr(response.usage,'input_tokens_details',None),'cached_tokens',0) or 0
        self.model_intervals.append({'agent':a.name,'start':self.pending.pop(id(a),None),'end':time.monotonic()-self.started,'usage':response.usage.model_dump() if hasattr(response.usage,'model_dump') else str(response.usage)})
        if self.cost>2.5:raise Limit('Aggregate dollar guard')
    def export(self):return {'model_calls':self.calls,'input_tokens':self.input,'output_tokens':self.output,'cached_input_tokens':self.cached,'estimated_uncached_model_usd':self.cost,'tool_intervals':self.tools,'model_intervals':self.model_intervals,'worker_outputs':self.worker_outputs,'trace_id':self.trace_id}

def make_tools(server,metrics,label):
    async def invoke(name,args):
        row={'agent':label,'name':name,'arguments':args,'start':time.monotonic()-metrics.started};metrics.tools.append(row)
        try:
            result=await server.call_tool(name,args)
            value=json.loads(result.content[0].text)
            row['result']=value;row['status']='error' if result.is_error or value.get('status')=='error' else 'completed'
            if value.get('handle'):metrics.evidence[value['handle']]=value
            return value
        except Exception as e:row.update(status='error',error=type(e).__name__);return {'status':'error','message':type(e).__name__}
        finally:row['end']=time.monotonic()-metrics.started
    async def get_catalog()->dict:
        """Get unified definitions and SQL types before SQL; contains no business records."""
        return await invoke('get_catalog',{})
    async def query_business_data(sql:str,parameters_json:str='{}',purpose:str='')->dict:
        """One bounded read-only analytics SELECT. Bind values; money is integer paise."""
        return await invoke('query_business_data',{'sql':sql,'parameters_json':parameters_json,'purpose':purpose})
    async def search_documents(query:str,effective_at:str|None=None,scope:str='all',top_k:int=4)->dict:
        """Find applicable dated policies/runbooks; default date is demo clock."""
        return await invoke('search_documents',{'query':query,'effective_at':effective_at,'scope':scope,'top_k':top_k})
    async def fetch_evidence(handle:str)->dict:
        """Fetch evidence already returned in this investigation."""
        return await invoke('fetch_evidence',{'handle':handle})
    async def get_order_history(order_id:str)->dict:
        """Retrieve current order facts and chronological attempts, failures and retries."""
        return await invoke('get_order_history',{'order_id':order_id})
    return [function_tool(t) for t in [get_catalog,query_business_data,search_documents,fetch_evidence,get_order_history]]

def parse_answer(s):
    s=s.strip()
    if s.startswith('```'):s=re.sub(r'^```(?:json)?\s*|\s*```$','',s)
    return json.loads(s)

def validate_records(answer,oracle,evidence):
    try:d=parse_answer(answer)
    except Exception:return {'parse_valid':False,'record_pass':False,'semantic_review':'pending','errors':['Output is not JSON']}
    actual=d.get('payouts',[]);expected={x['payout_id']:x for x in oracle};seen=[x.get('payout_id') for x in actual];errors=[]
    if len(seen)!=len(set(seen)):errors.append('Duplicate payout rows')
    if set(seen)!=set(expected):errors.append({'missing':sorted(set(expected)-set(seen)),'extra':sorted(set(seen)-set(expected))})
    for x in actual:
        y=expected.get(x.get('payout_id'))
        if not y:continue
        for key in ['seller_id','seller_name','order_id','payable_paise']:
            if type(x.get(key))!=type(y[key]) or x.get(key)!=y[key]:errors.append({'payout':y['payout_id'],'field':key,'expected':y[key],'actual':x.get(key)})
        hs=x.get('evidence_handles',[])
        if not hs or any(h not in evidence for h in hs):errors.append({'payout':y['payout_id'],'citation_error':hs})
    totals={}
    for x in oracle:totals[x['seller_id']]=totals.get(x['seller_id'],0)+(x['payable_paise'] if x['status']!='completed' else 0)
    sellers=d.get('sellers',[])
    if len(sellers)!=len(totals) or {x.get('seller_id'):x.get('unpaid_paise') for x in sellers}!=totals:errors.append({'seller_totals_expected':totals,'actual':sellers})
    return {'parse_valid':True,'record_pass':not errors,'errors':errors,'semantic_review':'pending; deterministic amount/scope checks do not grade prose explanation','parsed':d}

async def execute(mode,snapshot,doc_hash):
    metrics=Metrics();api=client().with_options(timeout=120);model=OpenAIChatCompletionsModel(model='eval-54',openai_client=api)
    def instance(name,prompt,tools,parallel):return Agent(name=name,instructions=prompt,model=model,tools=tools,model_settings=ModelSettings(max_tokens=4096,reasoning=Reasoning(effort='low'),parallel_tool_calls=parallel))
    span=baseline.lf.start_as_current_observation(name='payout-orchestration-experiment',as_type='span',input=QUESTION,metadata={'variant':mode,'fixture_version':fm.VERSION}) if baseline.lf else nullcontext()
    async with open_mcp() as server:
        state=await RemoteReadContext.create(server);assert state.snapshot==snapshot and state.doc_hash==doc_hash
        tools=make_tools(server,metrics,mode)
        if mode=='workers':
            used=set()
            async def investigate_seller(seller_id:str,task:str)->dict:
                """Delegate one discovered seller's payouts to an independent investigator with read-only tools; returns findings and evidence."""
                if seller_id in used:return {'status':'error','message':'Seller already delegated; use returned evidence'}
                if len(used)>=3:return {'status':'error','message':'Three-worker experiment limit reached'}
                used.add(seller_id)
                async with open_mcp() as ws:
                    wstate=await RemoteReadContext.create(ws);assert wstate.snapshot==snapshot and wstate.doc_hash==doc_hash
                    worker=instance('worker-'+seller_id,COMMON+'\nInvestigate only seller_id '+seller_id+'. Ignore other sellers in shared order-history results. Finish all payouts for this seller.',make_tools(ws,metrics,'worker-'+seller_id),True)
                    question=baseline.build_question_input(task+'\nSeller scope: '+seller_id,{**snapshot,'document_revision':doc_hash})
                    try:
                        result=await Runner.run(worker,question,max_turns=12,hooks=metrics)
                        output={'seller_id':seller_id,'answer':str(result.final_output),'sources':[t['result'] for t in metrics.tools if t['agent']=='worker-'+seller_id and t['name']!='get_catalog' and t.get('status')=='completed']}
                    except Exception as e:output={'seller_id':seller_id,'status':'failed','error':type(e).__name__}
                    metrics.worker_outputs.append(output);return output
            tools=[*tools,function_tool(investigate_seller)]
            instructions=COMMON+'\nYou coordinate seller investigations. Discover seller IDs using the catalog and business data; delegate each seller once via investigate_seller, concurrently when independent. Workers have the same five read-only tools and model. Synthesize their results; do not redo their full investigations. Preserve exact worker evidence handles.'
        else:instructions=COMMON+'\n'+('Use independent tool calls in the same response when their arguments are already known. Keep dependent steps sequential.' if mode=='parallel' else 'Use one tool call at a time.')
        a=instance(mode,instructions,tools,mode!='serial')
        with span as obs:
            if obs:metrics.trace_id=obs.trace_id
            try:
                result=await asyncio.wait_for(Runner.run(a,baseline.build_question_input(QUESTION,{**snapshot,'document_revision':doc_hash}),max_turns=20,hooks=metrics),timeout=300)
                answer=str(result.final_output);status='completed';error=None
            except Exception as e:answer='';status='failed';error=type(e).__name__
            if obs:obs.update(output=answer,metadata={'status':status,'metrics':metrics.export()})
        await api.close()
    return {'variant':mode,'status':status,'error':error,'answer':answer,'metrics':metrics.export(),'elapsed_seconds':time.monotonic()-metrics.started,'evidence':metrics.evidence,'model_inputs':metrics.inputs}

async def main():
    guard_database();init_schema();OUT.mkdir(parents=True,exist_ok=True)
    lock=engine.connect();assert lock.execute(text('SELECT pg_try_advisory_lock(938271)')).scalar()
    cache=json.loads(Path('/results/embedding-cache.json').read_text())
    dry=os.getenv('ORCHESTRATION_DRY')=='1'
    f=fm.build(cache);again=fm.build(cache);assert f['hash']==again['hash']
    (OUT/'fixture.json').write_text(json.dumps(f,indent=2,default=str))
    state={'experiment':OUT.name,'model':'gpt-5.4-2026-03-05','alias':'eval-54','fixture_version':fm.VERSION,'results':[],'estimated_usd':0,'status':'running','judge':'none; assistant semantic review after deterministic checks','limits':{'per_variant_usd':2.5,'aggregate_model_calls':32,'seconds':300,'batch_usd':15},'common_prompt':COMMON}
    if (OUT/'results.json').exists():
        state=json.loads((OUT/'results.json').read_text());assert state['common_prompt']==COMMON
    source_dir=OUT/'source';source_dir.mkdir(exist_ok=True)
    for p in [Path(__file__),Path(__file__).with_name('payout-orchestration-fixture.py')]:
        target=source_dir/p.name
        if target.exists():assert target.read_bytes()==p.read_bytes(),'New source needs a new experiment path'
        else:shutil.copy2(p,target)
    def save():(OUT/'results.json').write_text(json.dumps(state,indent=2,default=str))
    if dry:
        save();print(json.dumps({'fixture_repeatable':True,'payouts':len(f['expected']),'paid_calls':0,'hash':f['hash']}),flush=True);lock.close();return
    trials=int(os.getenv('ORCHESTRATION_TRIALS','1'))
    for trial in range(1,trials+1):
        order=MODES[(trial-1)%3:]+MODES[:(trial-1)%3]
        for mode in order:
            key=str(trial)+'-'+mode
            if any(x['key']==key for x in state['results']):continue
            if state['estimated_usd']+2.5>15:state['status']='budget_stopped';save();lock.close();return
            f=fm.build(cache);before=fingerprint()
            async with open_mcp() as server:ctx=await RemoteReadContext.create(server);snap=ctx.snapshot;doc=ctx.doc_hash
            print('START',key,flush=True)
            r=await execute(mode,snap,doc);r.update(key=key,trial=trial,fixture_hash=before,business_unchanged=fingerprint()==before,checks=validate_records(r['answer'],f['expected'],r['evidence']))
            state['results'].append(r);state['estimated_usd']+=r['metrics']['estimated_uncached_model_usd'];save()
            print('END',key,r['status'],'records',r['checks']['record_pass'],'usd',round(r['metrics']['estimated_uncached_model_usd'],4),'seconds',round(r['elapsed_seconds'],1),flush=True)
    state['status']='collected_semantic_review_pending';save();lock.close()
asyncio.run(main())
