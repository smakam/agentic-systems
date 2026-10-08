"""Align demo business/state/policy tables; preserve cloud auth, chats and memory.
Run inside the local backend with its existing ADC. --apply submits a one-off
Cloud Run job using the initializer's existing identity and network settings.
"""
import argparse,base64,hashlib,json,time,zlib
from datetime import datetime
from sqlalchemy import select
from marketplace import db
import google.auth
from google.auth.transport.requests import AuthorizedSession
PROJECT='marketplace-app-511005'
NAME='marketplace-business-snapshot-sync'
TABLES={m.__tablename__:m.__table__ for m in [*db.BUSINESS_TABLES,db.Command,db.Document,db.State]}
def encode(v):
 if isinstance(v,datetime): return v.isoformat()
 if hasattr(v,'tolist'): return v.tolist()
 raise TypeError(type(v).__name__)
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');opts=parser.parse_args()
 with db.engine.connect().execution_options(isolation_level='REPEATABLE READ') as conn:
  with conn.begin(): data={n:[dict(r) for r in conn.execute(select(t).order_by(*t.primary_key.columns)).mappings()] for n,t in TABLES.items()}
 payload=json.dumps(data,default=encode,sort_keys=True,separators=(',',':'))
 print('SOURCE',data['state'],'COUNTS',{n:len(r) for n,r in data.items()},'SHA256',hashlib.sha256(payload.encode()).hexdigest(),flush=True)
 creds,_=google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
 if hasattr(creds,'with_quota_project'): creds=creds.with_quota_project(PROJECT)
 http=AuthorizedSession(creds)
 root=f'https://run.googleapis.com/v2/projects/{PROJECT}/locations/asia-south1/jobs'
 r=http.get(root+'/marketplace-initialize');r.raise_for_status();original=r.json()
 if not opts.apply:
  print('DRY RUN: initializer accessible; no cloud data changed.');return
 program='''import os,json,hashlib
from datetime import datetime
from sqlalchemy import create_engine,select,text,DateTime
from sqlalchemy.engine import make_url
from marketplace import db
incoming=json.loads(SNAPSHOT_JSON)
tables={m.__tablename__:m.__table__ for m in [*db.BUSINESS_TABLES,db.Command,db.Document,db.State]}
engine=create_engine(make_url(os.environ['BOOTSTRAP_DATABASE_URL']).set(database='market'))
def encode(v):
 if isinstance(v,datetime): return v.isoformat()
 if hasattr(v,'tolist'): return v.tolist()
 raise TypeError(type(v).__name__)
def canonical(v): return json.dumps(v,default=encode,sort_keys=True,separators=(',',':'))
def snapshot(c): return {n:[dict(r) for r in c.execute(select(t).order_by(*t.primary_key.columns)).mappings()] for n,t in tables.items()}
with engine.begin() as conn:
 conn.execute(text("SET LOCAL lock_timeout = '10s'"))
 conn.execute(text('LOCK TABLE '+','.join('public.'+n for n in tables)+' IN ACCESS EXCLUSIVE MODE'))
 old=json.loads(canonical(snapshot(conn)))
 if old['state'][0]['revision']!=1: raise RuntimeError('Cloud changed from expected revision 1; refusing overwrite')
 users=set(conn.execute(select(db.User.__table__.c.id)).scalars())
 if any(r['customer_id'] not in users for r in incoming['orders']): raise RuntimeError('Missing cloud customer identities')
 conn.execute(text('CREATE TABLE IF NOT EXISTS public.business_snapshot_backups (id TEXT PRIMARY KEY,captured_at TIMESTAMPTZ DEFAULT now(),snapshot JSONB NOT NULL,sha256 TEXT NOT NULL)'))
 conn.execute(text('REVOKE ALL ON public.business_snapshot_backups FROM PUBLIC,market,agent_reader,mcp_registry'))
 backup_id='before-local-alignment-'+hashlib.sha256(canonical(old).encode()).hexdigest()[:16]
 conn.execute(text('INSERT INTO public.business_snapshot_backups(id,snapshot,sha256) VALUES (:id,CAST(:payload AS JSONB),:hash) ON CONFLICT(id) DO NOTHING'),{'id':backup_id,'payload':canonical(old),'hash':hashlib.sha256(canonical(old).encode()).hexdigest()})
 ordered=[t for t in db.Base.metadata.sorted_tables if t.name in tables]
 for t in reversed(ordered): conn.execute(t.delete())
 for t in ordered:
  rows=incoming[t.name]
  for row in rows:
   for col in t.columns:
    if isinstance(col.type,DateTime) and row.get(col.name): row[col.name]=datetime.fromisoformat(row[col.name])
  if rows: conn.execute(t.insert(),rows)
 actual=json.loads(canonical(snapshot(conn)))
 if actual!=json.loads(canonical(incoming)): raise RuntimeError('Readback mismatch; transaction rolls back')
 print('ALIGNED',actual['state'],'COUNTS',{n:len(r) for n,r in actual.items()},'SHA256',hashlib.sha256(canonical(actual).encode()).hexdigest(),'BACKUP',backup_id,flush=True)
engine.dispose()
'''
 program='SNAPSHOT_JSON='+repr(payload)+'\n'+program
 packed=base64.b64encode(zlib.compress(program.encode(),9)).decode()
 loader="import sys,base64,zlib;exec(zlib.decompress(base64.b64decode(''.join(sys.argv[1:]))))"
 template=original['template'];template['taskCount']=1;template['parallelism']=1
 container=template['template']['containers'][0];container['command']=['python'];container['args']=['-c',loader]+[packed[i:i+24000] for i in range(0,len(packed),24000)]
 template['template']['maxRetries']=0
 def wait(operation):
  while not operation.get('done'):
   time.sleep(3);r=http.get('https://run.googleapis.com/v2/'+operation['name']);r.raise_for_status();operation=r.json()
  if operation.get('error'): raise RuntimeError(operation['error'])
  return operation.get('response',{})
 existing=http.get(root+'/'+NAME)
 if existing.status_code==404: r=http.post(root,params={'jobId':NAME},json={'template':template})
 else:
  existing.raise_for_status();r=http.patch(root+'/'+NAME,json={'template':template})
 r.raise_for_status();wait(r.json())
 r=http.post(root+'/'+NAME+':run',json={});r.raise_for_status();print('JOB SUBMITTED',NAME,'PAYLOAD_BYTES',len(packed),flush=True)
 execution=wait(r.json());print('EXECUTION',execution['name'],'SUCCEEDED',execution.get('succeededCount'),'FAILED',execution.get('failedCount'),flush=True)
 r=http.post('https://logging.googleapis.com/v2/entries:list',json={'resourceNames':['projects/'+PROJECT],'filter':f'resource.type="cloud_run_job" AND resource.labels.job_name="{NAME}"','orderBy':'timestamp desc','pageSize':30})
 if not r.ok:
  print('Job completed; log readback unavailable. Inspect this execution in Cloud Logging.',flush=True)
  if execution.get('succeededCount')!=1: raise RuntimeError('Migration job did not succeed')
  return
 for e in reversed(r.json().get('entries',[])):
  message=e.get('textPayload','')
  if message.startswith(('ALIGNED','RuntimeError','Traceback')): print(message,flush=True)
 if execution.get('succeededCount')!=1: raise RuntimeError('Migration job did not succeed')
if __name__=='__main__': main()
