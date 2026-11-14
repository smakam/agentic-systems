#!/usr/bin/env python3
"""Create/restart only the isolated Agentic UI review; never reset Test/main."""
import json,secrets,subprocess,tempfile,time
from pathlib import Path
from urllib.parse import urlsplit,urlunsplit
root=Path(__file__).resolve().parents[2]
def docker(*args):return subprocess.check_output(['docker',*args],text=True).strip()
c=json.loads(docker('inspect','marketplace-lab-test-backend-1'))[0]
network=next(iter(c['NetworkSettings']['Networks']))
env=dict(x.split('=',1) for x in c['Config']['Env'])
assert env['DATABASE_URL'].endswith('/market_test')
name='marketplace-agentic-ui-db'
if name not in docker('ps','-a','--format','{{.Names}}').splitlines():
 if docker('exec','marketplace-lab-postgres-1','psql','-U','postgres','-d','market_test','-Atc',"SELECT COUNT(*) FROM runs WHERE status='running'")!='0':
  raise SystemExit('Wait for the current Test investigation before taking its snapshot')
 image=json.loads(docker('inspect','marketplace-lab-postgres-1'))[0]['Config']['Image']
 directory=Path(tempfile.mkdtemp(prefix='agentic-ui-db-'));directory.chmod(0o700)
 f=directory/'db.env';f.write_text('POSTGRES_PASSWORD='+secrets.token_urlsafe(32)+'\nPOSTGRES_DB=market_test\n');f.chmod(0o600)
 docker('run','-d','--name',name,'--network',network,'--network-alias','agentic-ui-db','--env-file',str(f),image);f.unlink()
 for _ in range(40):
  if subprocess.run(['docker','exec',name,'pg_isready','-U','postgres'],capture_output=True).returncode==0:break
  time.sleep(.5)
 def literal(s):return "'"+s.replace("'","''")+"'"
 sql=''
 for key in ['DATABASE_URL','READ_DATABASE_URL']:
  url=urlsplit(env[key]);user=url.username;password=url.password
  assert user in ('market','agent_reader')
  sql+=f'CREATE ROLE "{user}" LOGIN PASSWORD {literal(password)};\n'
 subprocess.run(['docker','exec','-i',name,'psql','-U','postgres','-d','market_test','-v','ON_ERROR_STOP=1'],input=sql.encode(),capture_output=True,check=True)
 dump=subprocess.check_output(['docker','exec','marketplace-lab-postgres-1','pg_dump','-U','postgres','-Fc','market_test'])
 subprocess.run(['docker','exec','-i',name,'pg_restore','-U','postgres','-d','market_test'],input=dump,check=True,capture_output=True)
docker('exec',name,'psql','-U','postgres','-d','postgres','-c',"ALTER ROLE agent_reader SET default_transaction_read_only=on; ALTER ROLE agent_reader SET statement_timeout='3000ms'; ALTER ROLE agent_reader SET search_path=analytics;")
for key in ['DATABASE_URL','READ_DATABASE_URL']:
 url=urlsplit(env[key]);env[key]=urlunsplit((url.scheme,url.netloc.replace(url.hostname,'agentic-ui-db'),url.path,url.query,url.fragment))
env.update(INITIALIZE_ON_STARTUP='false',A2UI_DEMO='true',MEM0_ENABLED='false',ALLOWED_ORIGINS='http://127.0.0.1:5181,http://localhost:5181')
private=Path(tempfile.mkdtemp(prefix='agentic-ui-config-'));private.chmod(0o700)
p=private/'backend.env';p.write_text('\n'.join(f'{k}={v}' for k,v in env.items())+'\n');p.chmod(0o600)
backend='marketplace-agentic-ui-backend'
if backend in docker('ps','-a','--format','{{.Names}}').splitlines():
 busy=docker('exec',name,'psql','-U','postgres','-d','market_test','-Atc',"SELECT (SELECT COUNT(*) FROM runs WHERE status='running')+(SELECT COUNT(*) FROM pg_locks WHERE locktype='advisory' AND database=(SELECT oid FROM pg_database WHERE datname=current_database()))")
 if busy!='0':raise SystemExit('Wait for the active review investigation or presentation before restarting')
 docker('rm','-f',backend)
args=['create','--name',backend,'--network',network,'--env-file',str(p),'-p','127.0.0.1:58010:8000']
for mount in c['Mounts']:
 source=str(root/'app/backend/marketplace') if mount['Destination']=='/app/marketplace' else mount['Source']
 args+=['--mount',f"type=bind,source={source},target={mount['Destination']},readonly"]
args+=['marketplace-a2ui-common-backend:local'];docker(*args);p.unlink();docker('start',backend)
print('Isolated Agentic UI database and backend ready. Existing Test and production databases and containers untouched.')
