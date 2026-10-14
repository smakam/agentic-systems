"""Create/reuse model-scoped local virtual keys; never print credentials."""
import json,os,time,urllib.request,urllib.error
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
