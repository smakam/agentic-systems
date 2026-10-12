import json,os,pathlib,subprocess,time,urllib.request,http.cookiejar,uuid,base64
APP=pathlib.Path(__file__).resolve().parents[1];D=pathlib.Path(os.getenv('CHAPTER06_LAB_DIR',str(APP/'test-output/chapter-06-lab')));D.mkdir(exist_ok=True);ROOT='http://127.0.0.1:58006';G='http://127.0.0.1:4006';MASTER='sk-chapter6-isolated-local'
GW='ghcr.io/berriai/litellm@sha256:87f34979b9f8cb274fac90ca8a4fdda07d8480de22755562a26adeb95ce20d02'
def run(a,**kw):return subprocess.run(a,cwd=APP,check=True,**kw)
def start(name,image,extra):run(['docker','run','-d','--rm','--name',name,'--network','marketplace-lab_default']+extra+[image],stdout=subprocess.DEVNULL)
def api(path,data=None,key=MASTER):
 q=urllib.request.Request(G+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json','Authorization':'Bearer '+key});r=urllib.request.urlopen(q,timeout=180);return json.load(r),dict(r.headers)
def wait(url):
 for i in range(60):
  try:urllib.request.urlopen(url,timeout=2);return
  except Exception:time.sleep(1)
 raise RuntimeError('Local lab startup timed out')
def gateway(model='openai/gpt-5.4-2026-03-05',cache=False,new=False):
 subprocess.run(['docker','rm','-f','course-ch6-gateway'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
 aliases=[('support-model',model),('embedding','openai/text-embedding-3-small')]
 if new:aliases.append(('learner-model','openai/gpt-5.4-2026-03-05'))
 cfg={'model_list':[{'model_name':a,'litellm_params':{'model':m,'api_key':'os.environ/OPENAI_API_KEY'}} for a,m in aliases], 'litellm_settings':{'request_timeout':60,'num_retries':0},'general_settings':{'master_key':MASTER}}
 if cache:cfg['litellm_settings'].update(cache=True,cache_params={'type':'redis','host':'course-ch6-redis','port':6379,'ttl':30})
 (D/'config.yaml').write_text(json.dumps(cfg,indent=2))
 run(['docker','run','-d','--rm','--name','course-ch6-gateway','--network','marketplace-lab_default','--env-file',str(D/'gateway.env'),'-p','127.0.0.1:4006:4000','-v',str(D/'config.yaml')+':/app/config.yaml:ro',GW,'--config','/app/config.yaml','--port','4000'],stdout=subprocess.DEVNULL);wait(G+'/health/liveliness')
def setup():
 run(['docker','build','-t','course-ch6-validation-backend','backend'],stdout=subprocess.DEVNULL)
 env={}
 for line in (APP/'.env').read_text().splitlines():
  if '=' in line and not line.startswith('#'):
   k,v=line.split('=',1)
   if k=='OPENAI_API_KEY':env[k]=v.strip().strip('"\'')
 if not env.get('OPENAI_API_KEY'):raise RuntimeError('This rehearsed isolated lab requires OPENAI_API_KEY. The main application separately supports OpenRouter.')
 start('course-ch6-db','pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f',['-e','POSTGRES_PASSWORD=local-lab-only','-v',str(APP/'infra/init.sql')+':/docker-entrypoint-initdb.d/01-init.sql:ro'])
 for _ in range(40):
  if subprocess.run(['docker','exec','course-ch6-db','pg_isready','-U','postgres'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:break
  time.sleep(1)
 for sql in ['CREATE DATABASE market_test OWNER market']:
  run(['docker','exec','course-ch6-db','psql','-U','postgres','-c',sql],stdout=subprocess.DEVNULL)
 run(['docker','exec','course-ch6-db','psql','-U','postgres','-d','market_test','-c','CREATE EXTENSION vector'],stdout=subprocess.DEVNULL)
 env.update(DATABASE_URL='postgresql://litellm:litellm-local@course-ch6-db:5432/litellm',LITELLM_MASTER_KEY=MASTER)
 f=D/'gateway.env';f.touch(mode=0o600);f.write_text('\n'.join(k+'='+v for k,v in env.items())+'\n')
 start('course-ch6-redis','redis@sha256:c6eabf748fc7a61dbb5a705c78bcf3d6377b1127a97d0ce965c11c44ba46896f',[])
 gateway()
 keys={}
 for role in ['support','operator']:
  r,_=api('/key/generate',{'key_alias':'chapter6-'+role,'models':['support-model','embedding','learner-model']});keys[role]=r['key']
 b={'DATABASE_URL':'postgresql+psycopg://market:market-local@course-ch6-db:5432/market_test','READ_DATABASE_URL':'postgresql://agent_reader:reader-local@course-ch6-db:5432/market_test','DATA_DIR':'/data','LITELLM_URL':'http://course-ch6-gateway:4000/v1','LITELLM_API_KEY':keys['support'],'OPERATOR_GATEWAY_KEY':keys['operator'],'AGENT_TOOL_TRANSPORT':'mcp','OPENAI_MODEL':'gpt-5.4-2026-03-05','AGENT_INPUT_RATE':'2.5','AGENT_OUTPUT_RATE':'15','AGENT_MAX_ESTIMATED_COST_USD':'1','LANGFUSE_BASE_URL':'http://langfuse-web:3000','LANGFUSE_PUBLIC_KEY':'pk-lf-marketplace-local','LANGFUSE_SECRET_KEY':'sk-lf-marketplace-local','ALLOWED_ORIGINS':'http://127.0.0.1:5179','MARKETPLACE_IDENTITY_NAMESPACE':'course-ch6-validation'}
 f=D/'backend.env';f.touch(mode=0o600);f.write_text('\n'.join(k+'='+v for k,v in b.items())+'\n')
 start('course-ch6-backend','course-ch6-validation-backend',['--env-file',str(f),'-p','127.0.0.1:58006:8000','-v',str(APP/'data')+':/data:ro']);wait(ROOT+'/api/health');run(['docker','exec','course-ch6-backend','python','-m','marketplace.index'],stdout=subprocess.DEVNULL)
 (D/'keys.json').touch(mode=0o600);(D/'keys.json').write_text(json.dumps(keys));print('Isolated gateway, database, MCP backend and distinct keys ready.',flush=True)
def user(role):
 op=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));csrf=None
 def req(path,data=None):
  h={'Content-Type':'application/json','Origin':'http://127.0.0.1:5179'}
  if csrf:h['x-csrf-token']=csrf
  q=urllib.request.Request(ROOT+path,data=json.dumps(data).encode() if data is not None else None,headers=h);return json.load(op.open(q,timeout=240))
 csrf=req('/api/login',{'username':role,'password':'demo-marketplace'})['csrf'];return req
Q=["What are Cedar & Co.'s captured amount and unpaid balance?",'What must happen before a seller payout can be released?']
def question(role,q,label):
 u=user(role);cid=u('/api/conversations',{'runtime':'sdk'})['id'];r=u('/api/conversations/'+cid+'/ask',{'question':q});(D/(label+'.json')).write_text(json.dumps(r,indent=2));assert r['status']=='completed',label+' failed';print(label+' completed',flush=True);return r
def cache_challenge():
 # Use different public aliases for model A/B: cache identity includes the requested alias.
 gateway(cache=True,new=True)
 cfg=json.loads((D/'config.yaml').read_text());cfg['model_list'].append({'model_name':'cache-nano','litellm_params':{'model':'openai/gpt-5-nano-2025-08-07','api_key':'os.environ/OPENAI_API_KEY'}})
 (D/'config.yaml').write_text(json.dumps(cfg,indent=2));run(['docker','restart','course-ch6-gateway'],stdout=subprocess.DEVNULL)
 wait(G+'/health/liveliness')
 prompt='Return the word READY. Fixture '+uuid.uuid4().hex
 rows=[]
 def call(model,label):
  r,h=api('/v1/chat/completions',{'model':model,'messages':[{'role':'user','content':prompt}],'max_completion_tokens':1000});row={'label':label,'alias':model,'response_id':r['id'],'content':r['choices'][0]['message'].get('content'),'headers':{k:v for k,v in h.items() if k.lower().startswith('x-litellm')}};rows.append(row);print(label,{k:v for k,v in row['headers'].items() if 'cache' in k.lower()},flush=True);return row
 first=call('learner-model','A miss');second=call('learner-model','A repeat');third=call('cache-nano','B miss');fourth=call('cache-nano','B repeat')
 assert first['response_id']==second['response_id'];assert third['response_id']==fourth['response_id'];assert first['response_id']!=third['response_id']
 cache_key=next(v for k,v in fourth['headers'].items() if k.lower()=='x-litellm-cache-key')
 api('/cache/delete',{'keys':[cache_key]})
 run(['docker','exec','course-ch6-redis','redis-cli','FLUSHDB'],stdout=subprocess.DEVNULL)
 run(['docker','restart','course-ch6-gateway'],stdout=subprocess.DEVNULL)
 wait(G+'/health/liveliness')
 fifth=call('cache-nano','B after clear');assert fifth['response_id']!=fourth['response_id']
 (D/'cache-checks.json').write_text(json.dumps({'passed':True,'rows':rows,'clearing':'Delete recorded entry, clear only isolated Redis, restart only isolated gateway to clear in-process cache'},indent=2));gateway();print('Cache sequence passed and original GPT-5.4 alias mapping restored.',flush=True)

if __name__=='__main__':
 import sys
 if len(sys.argv)<2 or sys.argv[1] in ['--help','-h']:
  print('Commands: setup; questions LABEL; operator; model gpt54|nano; new; cache; usage; cleanup');raise SystemExit(0)
 mode=sys.argv[1]
 if mode=='setup':setup()
 elif mode=='model':
  choices={'gpt54':'openai/gpt-5.4-2026-03-05','nano':'openai/gpt-5-nano-2025-08-07'}
  gateway(choices.get(sys.argv[2],sys.argv[2]))
 elif mode=='questions':
  label=sys.argv[2]
  for i,q in enumerate(Q):question('support',q,label+'-'+str(i+1))
 elif mode=='operator':question('operator',Q[0],'operator')
 elif mode=='new':
  gateway(new=True);key=json.loads((D/'keys.json').read_text())['support'];r,h=api('/v1/chat/completions',{'model':'learner-model','messages':[{'role':'user','content':'Return the word READY.'}],'max_completion_tokens':1000},key);assert r['choices'][0]['message'].get('content');(D/'new-alias.json').write_text(json.dumps({'model':'openai/gpt-5.4-2026-03-05','returned_model':r['model'],'content':r['choices'][0]['message']['content']},indent=2));print('New alias call passed',flush=True)
 elif mode=='cache':cache_challenge()
 elif mode=='usage':
  keys=json.loads((D/'keys.json').read_text());logs,_=api('/spend/logs');out={}
  for role in keys:
   rows=[x for x in logs if x.get('metadata',{}).get('user_api_key_alias')=='chapter6-'+role]
   out[role]={'requests':len(rows),'tokens':sum(x['total_tokens'] for x in rows),'estimated_cost_usd':sum(x['spend'] for x in rows)}
  (D/'role-usage.json').write_text(json.dumps(out,indent=2));print(json.dumps(out,indent=2))
 elif mode=='cleanup':
  for n in ['course-ch6-backend','course-ch6-gateway','course-ch6-redis','course-ch6-db']:subprocess.run(['docker','stop',n],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  for n in ['gateway.env','backend.env','keys.json']:(D/n).unlink(missing_ok=True)
  print('Isolated lab services and credentials removed.')
