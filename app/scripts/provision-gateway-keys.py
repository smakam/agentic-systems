"""Create/reuse model-scoped local virtual keys; never print credentials."""
import json,os,time,urllib.request,urllib.error,urllib.parse
from pathlib import Path
p=Path('.env');contents=p.read_text() if p.exists() else ''
values={line.split('=',1)[0]:line.split('=',1)[1] for line in contents.splitlines() if '=' in line and not line.startswith('#')}
base='http://localhost:4000'
master=os.getenv('LITELLM_MASTER_KEY','sk-marketplace-local')
def call(path,method='GET',body=None,key=master):
 req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method=method)
 with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
for attempt in range(20):
 try:call('/health/liveliness');break
 except (OSError,ValueError):time.sleep(2)
else:raise SystemExit('Gateway not ready')
for name,alias,models in [('SUPPORT_GATEWAY_KEY','marketplace-support',['support-model','embedding']),('OPERATOR_GATEWAY_KEY','marketplace-operator',['support-model','embedding']),('EVAL_GATEWAY_KEY','marketplace-evaluation',['eval-nano','eval-54','eval-5','support-model','embedding']+['ch16-keyword-question','ch16-heuristic-question','ch16-llm-conversation','ch16-llm-question']),('JUDGE_GATEWAY_KEY','marketplace-judge',['eval-judge'])]:
 key=values.get(name)
 if key:
  import urllib.parse
  info=call('/key/info?'+urllib.parse.urlencode({'key':key}))['info']
  if set(info['models'])!=set(models):
   additions=set(models)-set(info['models'])
   native_routes=set(['ch16-keyword-conversation','ch16-keyword-question','ch16-heuristic-question','ch16-llm-conversation','ch16-llm-question'])
   if name=='EVAL_GATEWAY_KEY' and (set(info['models']) ^ set(models)) <= native_routes and (set(info['models']) - native_routes) == (set(models) - native_routes):
    call('/key/update','POST',{'key':key,'models':models})
   else:raise SystemExit('Existing '+name+' has different permissions; review before updating')
 else:
  key=call('/key/generate','POST',{'key_alias':alias,'models':models,'metadata':{'purpose':alias,'project':'marketplace-lab'}})['key']
  lines=[l for l in contents.splitlines() if not l.startswith(name+'=')];lines.append(name+'='+key)
  contents='\n'.join(lines)+'\n'
  p.touch(mode=0o600,exist_ok=True);p.chmod(0o600);p.write_text(contents)
 print(alias+': ready (credential withheld)')

# One database-managed alias for all normal Test workspace SDK questions.
# Keep its selected model across startup; keys only grant support + embedding.
TEST_ALIAS='support-model-test'
TEST_MODEL_ID='marketplace-test-support-model'
registered=[m for m in call('/model/info')['data'] if m.get('model_name')==TEST_ALIAS]
if not registered:
    provider=os.environ.get('INFERENCE_PROVIDER',values.get('INFERENCE_PROVIDER','openai'))
    model='openrouter/openai/gpt-5.4' if provider=='openrouter' else 'openai/gpt-5.4-2026-03-05'
    credential='os.environ/OPENROUTER_API_KEY' if provider=='openrouter' else 'os.environ/OPENAI_API_KEY'
    call('/model/new','POST',{'model_name':TEST_ALIAS,'litellm_params':{'model':model,'api_key':credential},'model_info':{'id':TEST_MODEL_ID,'description':'Test workspace support model; editable independently of the main support alias'}})
elif len(registered)!=1 or registered[0].get('model_info',{}).get('id')!=TEST_MODEL_ID or not registered[0].get('model_info',{}).get('db_model'):
    raise SystemExit('Unexpected Test support alias; review before changing it')
for name,alias in [('TEST_SUPPORT_GATEWAY_KEY','marketplace-test-support'),('TEST_OPERATOR_GATEWAY_KEY','marketplace-test-operator')]:
    models=[TEST_ALIAS,'embedding']
    key=values.get(name)
    if key:
        info=call('/key/info?'+urllib.parse.urlencode({'key':key}))['info']
        old_models={'eval-54','eval-nano','eval-5','embedding','support-model'}
        old_aliases=info.get('aliases') or {}
        if info.get('key_alias')==alias and set(info.get('models') or [])==old_models and set(old_aliases)=={'support-model'} and old_aliases['support-model'] in ('eval-54','eval-nano','eval-5'):
            # Migrate only the narrowly identified prior Test experiment.
            call('/key/update','POST',{'key':key,'models':models,'aliases':{}})
        elif info.get('key_alias')!=alias or set(info.get('models') or [])!=set(models) or old_aliases:
            raise SystemExit('Existing '+name+' has unexpected identity or permissions; review before updating')
    else:
        key=call('/key/generate','POST',{'key_alias':alias,'models':models,'metadata':{'purpose':alias,'project':'marketplace-lab'}})['key']
        contents='\n'.join(l for l in contents.splitlines() if not l.startswith(name+'='))+'\n'+name+'='+key+'\n'
        p.touch(mode=0o600,exist_ok=True);p.chmod(0o600);p.write_text(contents)
    print(alias+': ready (credential withheld)')
