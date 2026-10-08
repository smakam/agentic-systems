"""30-case paired diagnostic. Gold stays in evaluator files and Langfuse, not agent tools."""
import argparse,asyncio,hashlib,json,os,time,uuid
from pathlib import Path
from datetime import datetime,timezone
from sqlalchemy import select,text
from .db import *
from .seed import DATA
from .eval_fixtures import guard_database,fixture,snapshot,fingerprint,questions
from .eval_grading import checks,judge_payload,parse_judge,JUDGE_PROMPT,RUBRIC_VERSION
from .tools import client

JUDGE={'alias':'eval-judge','model':'claude-opus-5-5','route':'anthropic/claude-opus-5-5','input_rate':4.,'output_rate':20.}
MODELS=[{'alias':'eval-nano','model':'gpt-5-nano-2025-08-07','input_rate':.05,'output_rate':.40,'budget':1.0},
        {'alias':'eval-54','model':'gpt-5.4-2026-03-05','input_rate':2.5,'output_rate':15.,'budget':1.0}]

def dump(path,value):
    path=Path(path);temp=path.with_suffix(path.suffix+'.tmp')
    temp.write_text(json.dumps(value,indent=2,default=str));temp.replace(path)

def manifest():
    root=Path(__file__).parent
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*.py')}
    return {'source_hashes':hashes,'ontology_hash':hashlib.sha256((DATA/'ontology.json').read_bytes()).hexdigest(),
            'limits':{'turns':8,'seconds':150,'completion_tokens':4096,'reasoning':'low'},
            'pricing_sources':['https://developers.openai.com/api/docs/models/gpt-5.4','https://developers.openai.com/api/docs/models/gpt-5-nano','https://platform.claude.com/docs/en/models/opus-5-5/overview'],
            'pricing_checked':'2026-09-28','judge_model':JUDGE['model'],'judge_route':JUDGE['route'],'judge_rubric':RUBRIC_VERSION,
            'human_review':'pending for every answer; automated scores are provisional'}

async def prepare_embeddings(out,dry):
    from .index import index
    cachefile=out.parent/'embedding-cache.json'
    cache=json.loads(cachefile.read_text()) if cachefile.exists() else {}
    fixture('01',cache)
    if not dry:await index()
    with Session() as db:
        cache={d.id:{'hash':d.content_hash,'model':d.embedding_model,'vector':list(d.embedding)} for d in db.scalars(select(Document)) if d.embedding is not None}
    if cache:dump(cachefile,cache)
    return cache

async def judge(case,turns,oracle,policies):
    payload=judge_payload(case,turns,oracle,policies)
    api=client(judge=True);started=time.monotonic()
    # Hard character cap is well below the 272k input-token pricing boundary.
    body=json.dumps(payload,default=str)
    if len(body)>650000:raise ValueError('Judge context too large; do not silently truncate evidence')
    try:
        r=await api.chat.completions.create(model=JUDGE['alias'],messages=[{'role':'system','content':JUDGE_PROMPT},{'role':'user','content':body}],
            max_tokens=4096,timeout=190,response_format={'type':'json_object'})
        cost=(r.usage.prompt_tokens*JUDGE['input_rate']+r.usage.completion_tokens*JUDGE['output_rate'])/1e6
        result={'usage':r.usage.model_dump(),'estimated_usd':cost,'gateway_returned_model':r.model,'configured_judge_model':JUDGE['model'],'judge_route':JUDGE['route'],'rubric_version':RUBRIC_VERSION,'elapsed_seconds':time.monotonic()-started,'raw':r.choices[0].message.content,'finish_reason':r.choices[0].finish_reason}
        try:result['grade']=parse_judge(result['raw'])
        except Exception as e:result['grading_error']=type(e).__name__
        return result
    finally:await api.close()

async def main(args):
    guard_database();init_schema()
    # Session advisory lock held for the entire benchmark. Prevent competing resets.
    lock=engine.connect();assert lock.execute(text('SELECT pg_try_advisory_lock(938271)')).scalar(),'Another evaluation is running'
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    cases=json.loads(Path(os.getenv('EVAL_CASES','/eval/cases.json')).read_text())
    if args.gold_file:
        gold=json.loads(Path(args.gold_file).read_text())
        for c in cases:
            if c['id'] in gold['cases']: c['gold']=gold['cases'][c['id']]
    if args.cases:cases=[c for c in cases if c['id'] in args.cases.split(',')]
    experiment=out.name
    archive=out/'source';archive.mkdir(exist_ok=True)
    for source in Path(__file__).parent.glob('*.py'):
        target=archive/source.name
        if not target.exists():target.write_bytes(source.read_bytes())
    if not (out/'cases.json').exists():dump(out/'cases.json',cases)
    state={'experiment':experiment,'manifest':manifest(),'results':[],'setup':{},'cost_estimate_usd':0.,'budget_usd':args.budget,'status':'running'}
    if (out/'results.json').exists():
        state=json.loads((out/'results.json').read_text())
        if state['manifest']['source_hashes']!=manifest()['source_hashes']:raise RuntimeError('Source changed: use new output directory, not mixed experiment resume')
    reuse={}
    if args.reuse_from:
        for source_path in args.reuse_from.split(','):
            previous=json.loads(Path(source_path).read_text())
            for name in ('agent.py','tools.py','db.py','seed.py','business.py','eval_fixtures.py'):
                if previous['manifest']['source_hashes'][name]!=manifest()['source_hashes'][name]:
                    raise RuntimeError('Cannot reuse answers after candidate/fixture change: '+name)
            reuse.update({r['key']:r for r in previous['results'] if r['turns']})
            if not (out/'results.json').exists():
                state['cost_estimate_usd']=max(state['cost_estimate_usd'],previous['cost_estimate_usd'])
                state['setup']['carried_forward_cost_usd']=state['cost_estimate_usd']
                state['setup']['reuse_from']=str(args.reuse_from)
    cache=await prepare_embeddings(out,args.dry_run)
    if args.dry_run:
        validations=[]
        for c in cases:
            f=fixture(c['id'],cache);before=fingerprint();oracle=snapshot()
            f2=fixture(c['id'],cache);assert fingerprint()==before,'Fixture not repeatable'
            validations.append({'case':c['id'],'hash':before,'questions':questions(c,f2),'validated':True})
        dump(out/'fixtures.json',validations);print(json.dumps({'validated_fixtures':len(validations),'paid_calls':0}),flush=True);return
    from .agent import answer,lf
    if not lf:raise RuntimeError('Langfuse configuration is required for this comparison')
    dataset='marketplace-30-v1'
    # Publish dataset associations after collection with native v4 run_experiment.
    # A telemetry endpoint must not block or lose paid candidate answers.
    policies=[{'source':p.name,'text':p.read_text()} for p in (DATA/'docs').glob('*.md')]
    # Account/model availability verification uses tiny real calls; record spend too.
    if not state['setup'].get('models'):
        api=client();judge_api=client(judge=True) if not args.collect_only else None;available=[]
        try:
            for m in ([JUDGE] if args.grade_only else MODELS if args.collect_only else [*MODELS,JUDGE]):
                r=await judge_api.chat.completions.create(model=m['alias'],messages=[{'role':'user','content':'Reply OK.'}],max_tokens=256) if m is JUDGE else await api.chat.completions.create(model=m['alias'],messages=[{'role':'user','content':'Reply OK.'}],max_completion_tokens=128,reasoning_effort='low')
                cost=(r.usage.prompt_tokens*m['input_rate']+r.usage.completion_tokens*m['output_rate'])/1e6
                available.append({'requested':m['model'],'returned':r.model,'usage':r.usage.model_dump(),'estimated_usd':cost})
                state['cost_estimate_usd']+=cost
        finally:
            await api.close()
            if judge_api:await judge_api.close()
        state['setup']['models']=available;dump(out/'results.json',state)
    for trial in range(1,args.repeats+1):
        for case in cases:
            item_id=str(uuid.uuid5(uuid.NAMESPACE_URL,dataset+case['id']))
            order=MODELS if (int(case['id'])+trial)%2==0 else list(reversed(MODELS))
            for model in order:
                key=f"{trial}-{case['id']}-{model['alias']}"
                existing=next((r for r in state['results'] if r['key']==key),None)
                if existing and existing.get('status')=='complete':continue
                # Reserve conservatively before starting a scenario; no unbounded full-batch launch.
                if state['cost_estimate_usd']+state.get('unknown_usage_reserve_usd',0)+2.5>args.budget:
                    state['status']='budget_stopped';dump(out/'results.json',state);print('Budget reserve reached',flush=True);return
                f=fixture(case['id'],cache);oracle=snapshot();qs=questions(case,f)
                convo='eval-'+key
                with Session.begin() as db:db.add(Conversation(id=convo,owner_id='support',title=case['id'],items=[]))
                record={'key':key,'case':case,'model':model['model'],'trial':trial,'fixture_hash':fingerprint(),'aliases':f.aliases,'turns':[],
                        'human_review':{'status':'pending','correctness':None,'agree_with_judge':None,'notes':''},'status':'running'}
                if existing:raise RuntimeError('Interrupted scenario requires a new experiment directory; preserve partial cost/history')
                saved=reuse.get(key)
                if saved and (len(saved['turns'])!=len(qs) or saved['fixture_hash']!=record['fixture_hash']):saved=None
                if args.grade_only and not saved:raise RuntimeError('Grade-only requires saved answers for every requested case')
                if saved:
                    record['reused_from']=str(args.reuse_from)
                    record['previous_judge']=saved.get('judge')
                state['results'].append(record);dump(out/'results.json',state)
                for idx,q in enumerate(qs):
                    if case['id']=='28' and idx==1:
                        f.purchase('listing-1','NEW');oracle=snapshot()
                        with Session() as db:assert db.execute(text("SELECT unpaid FROM analytics.seller_balances WHERE seller_id='seller-1'")).scalar()==674730
                    before=fingerprint();r=saved['turns'][idx]['run'] if saved else await answer(convo,q,evaluation_config=model)
                    turn={'question':q,'run':r,'deterministic':checks(r,before,fingerprint(),case['id'],turn_index=idx,aliases=f.aliases)}
                    record['turns'].append(turn)
                    if not saved:state['cost_estimate_usd']+=r['metrics']['estimated_model_cost_usd']
                    if r['status']!='completed':state['unknown_usage_reserve_usd']=state.get('unknown_usage_reserve_usd',0)+.5
                    dump(out/'results.json',state)
                # Same judge for both candidates, blind to candidate identity.
                try:
                    previous_judge=(saved or {}).get('judge') or {}
                    if previous_judge.get('grade') and previous_judge.get('configured_judge_model')==JUDGE['model'] and previous_judge.get('rubric_version')==RUBRIC_VERSION:
                        record['judge']={**previous_judge,'judge_route':previous_judge.get('judge_route','anthropic/claude-opus-5-5'),'reused_grade':True}
                    elif args.collect_only:
                        record['judge']={'grade':None,'status':'pending_judge','estimated_usd':0}
                    else:
                        record['judge']=await judge(case,record['turns'],oracle,policies)
                        state['cost_estimate_usd']+=record['judge']['estimated_usd']
                except Exception as e:
                    record['judge']={'error':type(e).__name__,'grade':None,'usage_status':'unknown; inspect provider before retry'}
                    state['unknown_usage_reserve_usd']=state.get('unknown_usage_reserve_usd',0)+.5
                record['status']='complete';dump(out/'results.json',state)
                if not args.collect_only and not record['judge'].get('grade'):
                    state['status']='judge_blocked';dump(out/'results.json',state)
                    print('Judge failed; stopping before more paid calls',flush=True);return
                print(json.dumps({'case':case['id'],'model':model['alias'],'answers':len(record['turns']),'judge':(record['judge'].get('grade') or {}).get('correctness'),'cost_so_far':round(state['cost_estimate_usd'],4)}),flush=True)
    state['status']='answers_complete_judge_pending' if any(not r['judge'].get('grade') for r in state['results']) else 'automated_complete_human_review_pending';dump(out/'results.json',state)
    lf.flush();lock.close()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--dry-run',action='store_true');p.add_argument('--cases');p.add_argument('--gold-file');p.add_argument('--reuse-from');mode=p.add_mutually_exclusive_group();mode.add_argument('--collect-only',action='store_true');mode.add_argument('--grade-only',action='store_true');p.add_argument('--repeats',type=int,default=1);p.add_argument('--budget',type=float,default=15)
    asyncio.run(main(p.parse_args()))
