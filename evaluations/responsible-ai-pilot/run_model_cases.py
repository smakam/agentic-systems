"""Direct model probes through the existing gateway; no agent, tools or paid judge."""
import argparse
import collections
import datetime
import hashlib
import json
import os
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parent
MODELS = [
    {"name": "GPT-5.4", "alias": "eval-54", "snapshot": "gpt-5.4-2026-03-05", "input_rate": 2.5, "output_rate": 15.0},
    {"name": "GPT-5 nano", "alias": "eval-nano", "snapshot": "gpt-5-nano-2025-08-07", "input_rate": .05, "output_rate": .40},
]
MAX_OUTPUT = 4096
BUDGET = 1.0

def read_env(path):
    values = {}
    for line in Path(path).read_text().splitlines():
        if line.strip() and not line.lstrip().startswith('#') and '=' in line:
            k, v = line.split('=', 1)
            values[k.strip()] = v.strip().strip('\"\'')
    return values

def save(path, data):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2))
    temp.replace(path)

def request(base, key, path, body=None):
    headers = {'Authorization': 'Bearer '+key, 'Content-Type': 'application/json', 'Cache-Control': 'no-cache, no-store'}
    req = urllib.request.Request(base+path, data=json.dumps(body).encode() if body is not None else None, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r), {k:v for k,v in r.headers.items() if k.lower() in ('x-litellm-model-id','x-litellm-response-cost','x-litellm-cache-key','x-litellm-cache-hit','x-request-id')}

def validate(fixture):
    cases = fixture['cases']
    assert len(cases) == 6 and len({c['id'] for c in cases}) == 6
    assert collections.Counter(c['category'] for c in cases) == {'security':2, 'safety':2, 'values':2}
    assert all([m['role'] for m in c['messages']] == ['system','user'] for c in cases)
    assert all(len(json.dumps(c['messages']).encode()) < 8000 for c in cases)
    # Conservative character-based input allowance, and all capped output charged.
    bound = sum((10000*m['input_rate'] + MAX_OUTPUT*m['output_rate'])/1e6 for m in MODELS for _ in cases)
    assert bound < BUDGET
    return bound

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--env-file')
    ap.add_argument('--base-url', default='http://127.0.0.1:4000')
    ap.add_argument('--execute', action='store_true')
    ap.add_argument('--preflight', action='store_true')
    ap.add_argument('--output', type=Path)
    ap.add_argument('--resume', action='store_true')
    args = ap.parse_args()
    fixture = json.loads((ROOT/'model-cases.json').read_text())
    bound = validate(fixture)
    if not (args.preflight or args.execute):
        print(json.dumps({'validated_cases':6, 'planned_calls':12, 'conservative_estimated_usd_bound':bound, 'paid_calls':0}))
        return
    env = read_env(args.env_file) if args.env_file else {}
    key = os.environ.get('EVAL_GATEWAY_KEY') or env.get('EVAL_GATEWAY_KEY')
    if not key:
        raise SystemExit('Evaluation gateway credential unavailable; no calls sent.')
    info, _ = request(args.base_url, key, '/model/info')
    routes = []
    for model in MODELS:
        matches = [x for x in info.get('data',[]) if x.get('model_name')==model['alias']]
        if len(matches)!=1:
            raise SystemExit('Selected model route missing or ambiguous; no calls sent.')
        params = matches[0].get('litellm_params',{})
        route = params.get('model','')
        if route not in ('openai/'+model['snapshot'], model['snapshot']):
            raise SystemExit('Selected route differs from the pinned model; no calls sent.')
        if any(params.get(k) for k in ('fallbacks','guardrails','mock_response')):
            raise SystemExit('Unexpected model-route behavior; no calls sent.')
        routes.append({'alias':model['alias'],'provider_model':route,'model_id':matches[0].get('model_info',{}).get('id')})
    keyinfo, _ = request(args.base_url,key,'/key/info?'+urllib.parse.urlencode({'key':key}))
    ki=keyinfo.get('info',{})
    if ki.get('guardrails') or (ki.get('metadata') or {}).get('guardrails') or ki.get('aliases'):
        raise SystemExit('Key overrides require review; no calls sent.')
    if args.preflight and not args.execute:
        print(json.dumps({'preflight':'passed','routes':routes,'key_overrides':False,'paid_calls':0}))
        return
    if args.output is None:
        raise SystemExit('An explicit new output directory is required.')
    args.output.mkdir(parents=True,exist_ok=args.resume)
    save(args.output/'fixtures.json',fixture)
    state={'started_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'running','models':MODELS,'routes':routes,
           'fixture_sha256':hashlib.sha256((ROOT/'model-cases.json').read_bytes()).hexdigest(),'reasoning_effort':'low','max_completion_tokens':MAX_OUTPUT,
           'budget_usd':BUDGET,'conservative_estimated_usd_bound':bound,'pricing_checked':'2026-11-04','pricing_source':'https://developers.openai.com/api/docs/pricing',
           'configuration':{'agent':False,'tools':False,'guardrails_requested':[],'response_cache':'no-cache/no-store','retries':0,'judges':False},'results':[]}
    if args.resume:
        previous=json.loads((args.output/'results.json').read_text())
        if previous['fixture_sha256']!=state['fixture_sha256'] or previous['models']!=MODELS:
            raise SystemExit('Resume configuration changed; no calls sent.')
        state['results']=previous['results']
        state['started_at']=previous['started_at']
        for row in state['results']:
            route=next(x for x in routes if x['provider_model']=='openai/'+row['expected_model'])
            recorded_id=next((v for k,v in row.get('response_headers',{}).items() if k.lower()=='x-litellm-model-id'),None)
            if row['status']=='model_mismatch' and row['returned_model']==route['alias'] and recorded_id==route['model_id'] and recorded_id:
                row['status']='completed'
                row['identity_verification']='Gateway alias response; response model ID matches live pinned route.'
            if row['status'] not in ('completed','incomplete'):
                raise SystemExit('Unresolved prior run requires review; no calls sent.')
    save(args.output/'results.json',state)
    for model in MODELS:
        for case in fixture['cases']:
            if any(r['case_id']==case['id'] and r['expected_model']==model['snapshot'] for r in state['results']):
                continue
            row={'case_id':case['id'],'category':case['category'],'model':model['name'],'expected_model':model['snapshot'],'status':'started','manual_review':'pending'}
            state['results'].append(row)
            save(args.output/'results.json',state)
            start=time.monotonic()
            body={'model':model['alias'],'messages':case['messages'],'max_completion_tokens':MAX_OUTPUT,'reasoning_effort':'low','stream':False,'store':False,
                  'guardrails':[],'caching':False,'cache':{'no-cache':True,'no-store':True}}
            try:
                response,headers=request(args.base_url,key,'/v1/chat/completions',body)
                save(args.output/(case['id']+'__'+model['alias']+'.json'),{'request':body,'response':response,'response_headers':headers})
                choice=response['choices'][0]
                usage=response.get('usage',{})
                row.update(status='completed',returned_model=response.get('model'),finish_reason=choice.get('finish_reason'),response=choice['message'].get('content'),usage=usage,response_headers=headers)
                row['estimated_usd']=(usage.get('prompt_tokens',0)*model['input_rate']+usage.get('completion_tokens',0)*model['output_rate'])/1e6
                route=next(x for x in routes if x['alias']==model['alias'])
                returned_id=next((v for k,v in headers.items() if k.lower()=='x-litellm-model-id'),None)
                if response.get('model')==model['alias'] and returned_id and returned_id==route['model_id']:
                    row['identity_verification']='Gateway alias response; response model ID matches live pinned route.'
                elif response.get('model') != model['snapshot']:
                    row['status']='model_mismatch'
                if choice.get('finish_reason')=='length' or not choice['message'].get('content'):
                    row['status']='incomplete'
            except urllib.error.HTTPError as e:
                # Retain diagnostic body privately; do not print it or credentials.
                save(args.output/(case['id']+'__'+model['alias']+'__error.json'),{'http_status':e.code,'body':e.read().decode(errors='replace')})
                row.update(status='http_error',http_status=e.code)
            except Exception as e:
                row.update(status='transport_or_parse_error',error_type=type(e).__name__)
            row['elapsed_seconds']=round(time.monotonic()-start,2)
            save(args.output/'results.json',state)
            print(json.dumps({'case':case['id'],'model':model['name'],'status':row['status']}),flush=True)
            if row['status'] not in ('completed','incomplete'):
                state['status']='stopped_for_review'
                save(args.output/'results.json',state)
                return
    state['status']='collection_complete_manual_review_pending'
    state['estimated_usd']=sum(r.get('estimated_usd',0) for r in state['results'])
    save(args.output/'results.json',state)
    print(json.dumps({'completed_calls':len(state['results']),'estimated_usd':state['estimated_usd']}))

if __name__=='__main__':
    main()
