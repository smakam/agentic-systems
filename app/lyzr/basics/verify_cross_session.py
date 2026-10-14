"""Optional paid native Cognis lab: four synthetic calls; never directly adds memories.

Uses your explicit own-agent ID, or an existing separate Basics manifest. Restores its original memory setting in
finally. Reads LYZR_API_KEY from environment or the ignored app/.env, never prints it.
"""
import argparse,copy,json,os,time,uuid
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request,urlopen
HERE=Path(__file__).resolve().parent
AGENT_API='https://agent-prod.studio.lyzr.ai'
MEMORY_API='https://memory.studio.lyzr.ai'
RETENTION='Retain explicit durable user presentation preferences faithfully. Do not store fictional business order states, payment/shipment/payout facts, credentials, assistant acknowledgments or one-answer overrides as durable user preferences.'
UPDATE_FIELDS=('name','description','agent_role','agent_instructions','agent_goal','agent_context','agent_output','provider_id','model','llm_credential_id','features','tools','tool_configs','managed_agents','a2a_tools','store_messages','max_iterations','top_p','temperature')
def api_key():
 key=os.environ.get('LYZR_API_KEY')
 if not key:
  env=HERE.parents[1]/'.env'
  if env.exists():
   key=next((row.split('=',1)[1].strip().strip('"\'') for row in env.read_text().splitlines() if row.startswith('LYZR_API_KEY=')),None)
 if not key:raise RuntimeError('Configure LYZR_API_KEY privately in environment or ignored app/.env')
 return key

def redact(value):
 if isinstance(value,dict):return {k:redact(v) for k,v in value.items() if k not in ('org_id','api_key','access_token','authorization','credentials')}
 if isinstance(value,list):return [redact(v) for v in value]
 return value

def evaluate(receipt):
 owner=receipt['owner_id'];agent=receipt['agent_id'];session=receipt['seed_session_id'];marker=receipt['marker']
 rows=receipt.get('native_records',{}).get('memories',[]);cases=receipt.get('cases',[])
 def answer(label):return next((c['response'].get('response','') for c in cases if c['label']==label),'')
 return {'baseline_empty':receipt.get('before_seed',{}).get('total')==0,
  'native_record_source_matches':any(r.get('owner_id')==owner and r.get('agent_id')==agent and r.get('session_id')==session and marker in r.get('content','') and marker in str(r.get('original_content')) for r in rows),
  'fresh_session_recall':marker in answer('fresh_session_recall'),
  'fresh_business_applies_preference':marker in answer('fresh_session_business') and 'released' in answer('fresh_session_business').lower(),
  'other_owner_records_empty':receipt.get('other_native_records',{}).get('total')==0,
  'other_owner_answer_no_preference':marker not in answer('other_identity_recall') and any(term in answer('other_identity_recall').lower() for term in ("don't have",'don’t have','no verified','no stored'))}

class Lab:
 def __init__(self,key):self.key=key
 def request(self,base,path,payload=None,method=None):
  req=Request(base+path,data=json.dumps(payload).encode() if payload is not None else None,headers={'x-api-key':self.key,'Content-Type':'application/json'},method=method)
  with urlopen(req,timeout=60) as response:return json.load(response)
 def run(self,manifest,output,wait=35):
  agent=manifest['agent_id'];path='/v3/agents/'+agent
  original=self.request(AGENT_API,path)
  if original.get('name')!='Support Agent Basics' or original.get('tools') or original.get('tool_configs'):
   raise RuntimeError('Only the separate native-KB Basics agent without external tools is a target')
  config={k:copy.deepcopy(original[k]) for k in UPDATE_FIELDS if k in original}
  memory=next((f for f in config['features'] if f.get('type')=='MEMORY'),None)
  if not memory or memory.get('config',{}).get('provider')!='cognis':raise RuntimeError('Configure native Cognis on this Basics agent first')
  owner='basics-memory-verification-'+uuid.uuid4().hex;seed=agent+'-'+uuid.uuid4().hex;marker='cobalt-sparrow-'+uuid.uuid4().hex[:6]
  receipt={'agent_id':agent,'owner_id':owner,'seed_session_id':seed,'marker':marker,'started_at':time.time(),'cases':[],'polls':[],
   'trigger':'Native integrated Cognis extraction after conversation turns; no direct memory-add call'}
  def save():output.write_text(json.dumps(redact(receipt),indent=2)+'\n')
  def records(who):return self.request(MEMORY_API,'/v1/memories?'+urlencode({'owner_id':who,'agent_id':agent,'cross_session':'true','limit':20}))
  def ask(label,who,session,message):
   if len(receipt['cases'])>=4:raise RuntimeError('Four-call inference budget exhausted')
   start=time.time();response=self.request(AGENT_API,'/v3/inference/chat/',{'user_id':who,'agent_id':agent,'session_id':session,'message':message})
   receipt['cases'].append({'label':label,'owner_id':who,'session_id':session,'question':message,'response':response,'seconds':round(time.time()-start,2)});save()
  try:
   memory['config']['lyzr_memory']['params'].update(cross_session=True,instructions=RETENTION)
   self.request(AGENT_API,path,config,'PUT')
   read=self.request(AGENT_API,path);receipt['configuration_readback']={'name':read['name'],'features':read['features']};save()
   receipt['before_seed']=records(owner);save()
   ask('preference_seed',owner,seed,f'I have a durable support-answer preference: start each answer with the heading {marker}, followed by the headings Finding, Evidence and Next action. Please acknowledge this preference briefly.')
   deadline=time.monotonic()+wait;start=time.monotonic()
   while True:
    data=self.request(MEMORY_API,'/v1/memories/search',{'owner_id':owner,'agent_id':agent,'query':'What is the user durable answer heading preference?','limit':10,'cross_session':True})
    receipt['polls'].append({'seconds_after_seed':round(time.monotonic()-start,2),'response':data});save()
    if marker in json.dumps(data):receipt['native_records']=records(owner);break
    if time.monotonic()>=deadline:receipt['native_records']=records(owner);break
    time.sleep(min(5,max(0,deadline-time.monotonic())))
   ask('fresh_session_recall',owner,agent+'-'+uuid.uuid4().hex,'What support answer headings do I prefer?')
   ask('fresh_session_business',owner,agent+'-'+uuid.uuid4().hex,'What is the payout status of order-demo-2?')
   other=owner+'-other';receipt['other_native_records']=records(other);save()
   ask('other_identity_recall',other,agent+'-'+uuid.uuid4().hex,'What support answer headings do I prefer?')
   receipt['checks']=evaluate(receipt)
  except Exception as exc:
   receipt['failure_type']=type(exc).__name__
  finally:
   restore={k:original[k] for k in UPDATE_FIELDS if k in original}
   try:
    self.request(AGENT_API,path,restore,'PUT');read=self.request(AGENT_API,path)
    restored=next(f for f in read['features'] if f.get('type')=='MEMORY')
    receipt['restored_original_memory_configuration']=restored==next(f for f in original['features'] if f.get('type')=='MEMORY')
   except Exception as exc:receipt['restore_failure_type']=type(exc).__name__
   receipt['finished_at']=time.time();save()
  return receipt

def resolve_target(agent_id=None,manifest_path=HERE/'deployment.json'):
 if agent_id:
  if not agent_id.strip() or any(char not in '0123456789abcdefABCDEF' for char in agent_id) or len(agent_id)!=24:
   raise ValueError('Use the 24-character agent ID copied from your own Basics deployment')
  return {'agent_id':agent_id}
 if not manifest_path.exists():
  raise ValueError('Studio-created agent has no local manifest. Pass --agent-id YOUR_OWN_BASICS_AGENT_ID')
 data=json.loads(manifest_path.read_text())
 if not data.get('agent_id'):raise ValueError('Manifest has no completed agent creation; inspect Studio before proceeding')
 return data


def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--agent-id',help='Your separately created Basics agent ID; no local deployment manifest needed');parser.add_argument('--wait',type=int,default=35);parser.add_argument('--output',type=Path,default=HERE/'cross-session-latest.json');args=parser.parse_args()
 if args.wait<0 or args.wait>120:raise SystemExit('Use --wait between 0 and 120 seconds')
 try:manifest=resolve_target(args.agent_id)
 except ValueError as exc:raise SystemExit(str(exc))
 result=Lab(api_key()).run(manifest,args.output,args.wait)
 passed=bool(result.get('checks')) and all(result['checks'].values()) and result.get('restored_original_memory_configuration',False)
 print(json.dumps({'passed':passed,'inference_requests':len(result['cases']),'receipt':str(args.output),'failure_type':result.get('failure_type'),'restore_failure_type':result.get('restore_failure_type')}))
 if not passed:raise SystemExit('Inspect receipt before rerunning paid requests')
if __name__=='__main__':main()
