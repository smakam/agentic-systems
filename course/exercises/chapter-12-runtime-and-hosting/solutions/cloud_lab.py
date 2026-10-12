"""Deploy only the agent to Cloud Run; keep middleware and history on laptop."""
import argparse,json,os,secrets,shutil,subprocess,tempfile
from pathlib import Path
from urllib.parse import urlsplit
ROOT=Path(__file__).resolve().parents[4];APP=ROOT/'app'
def env_read(path):
    return dict(line.split('=',1) for line in path.read_text().splitlines() if '=' in line and not line.startswith('#'))
def write_env(path,values):
    path.write_text('\n'.join(k+'='+v for k,v in values.items())+'\n');path.chmod(0o600)
def command(args,stdin=None):
    r=subprocess.run(args,input=stdin,text=True,capture_output=True)
    if r.returncode:raise RuntimeError('Command failed: '+args[0]+' '+r.stderr[-2000:])
    return r.stdout
def google(args,stdin=None):
    if shutil.which('gcloud'):return command(['gcloud',*args,'--quiet'],stdin)
    return command(['docker','run','--rm','-i','--pull=never','-v',str(APP/'.google-auth/application_default_credentials.json')+':/credentials/adc.json:ro',
      '-e','CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE=/credentials/adc.json',
      'gcr.io/google.com/cloudsdktool/google-cloud-cli:stable','gcloud',*args,'--quiet'],stdin)
def finish_deploy(a,record,e,state,envfile):
    service=record['service']
    bindings=','.join([f'CH12_AGENT_API_KEY={service}-agent:latest',f'SDK_MCP_API_KEY={service}-mcp:latest',f'OPENAI_API_KEY={a.openai_secret}:latest'])
    result=json.loads(google(['run','deploy',service,'--project',a.project,'--region',a.region,'--image',record['image'],
       '--service-account',a.service_account,'--allow-unauthenticated','--cpu','1','--memory','1Gi','--timeout','180',
       '--concurrency','1','--min-instances','0','--max-instances','1','--set-env-vars','SDK_MCP_URL='+a.mcp_url+',CH12_MODEL=gpt-5.4-2026-03-05',
       '--set-secrets',bindings,'--format','json']))
    record['url']=result['status']['url'];state.write_text(json.dumps(record,indent=2))
    e['CH12_AGENT_URL']=record['url'];write_env(envfile,e);print(json.dumps(record,indent=2))
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','deploy','cleanup'])
    p.add_argument('--project');p.add_argument('--region',default='asia-south1');p.add_argument('--repository',default='marketplace')
    p.add_argument('--service-account');p.add_argument('--mcp-url');p.add_argument('--openai-secret');p.add_argument('--resume',action='store_true');a=p.parse_args()
    state=APP/'.ch12-cloud-state.json';envfile=APP/'.ch12.env'
    if a.action=='prepare':
        if envfile.exists():raise SystemExit('Existing .ch12.env preserved; reuse its keys.')
        write_env(envfile,{'CH12_AGENT_API_KEY':secrets.token_urlsafe(32),'REMOTE_MCP_API_KEY':secrets.token_urlsafe(32),
          'REMOTE_MCP_ALLOWED_HOSTS':'localhost:*,127.0.0.1:*','CH12_AGENT_URL':'https://not-deployed.invalid'})
        print('Created private lab credentials in app/.ch12.env');return
    if a.action=='cleanup':
        s=json.loads(state.read_text())
        existing=google(['run','services','list','--region',s['region'],'--project',s['project'],
          '--filter','metadata.name='+s['service'],'--format','value(metadata.name)']).strip()
        if existing:google(['run','services','delete',s['service'],'--region',s['region'],'--project',s['project']])
        secret_names={x.rsplit('/',1)[-1] for x in google(['secrets','list','--project',s['project'],'--format','value(name)']).splitlines()}
        for name in s['secrets']:
            if name in secret_names:google(['secrets','delete',name,'--project',s['project']])
        repository=s['image'].split('/')[2]
        packages=google(['artifacts','packages','list','--project',s['project'],'--location',s['region'],
          '--repository',repository,'--format','value(name)']).splitlines()
        if any(x.rsplit('/',1)[-1]==s['service'] for x in packages):
            google(['artifacts','packages','delete',s['service'],'--repository',repository,
              '--location',s['region'],'--project',s['project']])
        s['cleaned_up']=True;state.write_text(json.dumps(s,indent=2));print('Deleted recorded Chapter 12 cloud service and secrets.');return
    if not all((a.project,a.service_account,a.mcp_url,a.openai_secret)):
        raise SystemExit('Supply project, service account, tunnel MCP URL and an existing OpenAI Secret Manager secret.')
    url=urlsplit(a.mcp_url)
    if url.scheme!='https' or url.path!='/mcp' or url.username or url.query:raise SystemExit('Use authenticated HTTPS tunnel URL ending /mcp.')
    if a.resume:
        record=json.loads(state.read_text())
        if record['project']!=a.project or record['region']!=a.region or record.get('cleaned_up'):
            raise SystemExit('Resume must target the recorded active lab project and region.')
        for name in record['secrets']:
            google(['secrets','add-iam-policy-binding',name,'--member','serviceAccount:'+a.service_account,
              '--role','roles/secretmanager.secretAccessor','--project',a.project])
        e=env_read(envfile);e['REMOTE_MCP_ALLOWED_HOSTS']='localhost:*,127.0.0.1:*,'+url.hostname;write_env(envfile,e)
        finish_deploy(a,record,e,state,envfile);return
    if state.exists() and not json.loads(state.read_text()).get('cleaned_up'):raise SystemExit('An earlier deployment is recorded. Clean it up before deploying a new lab.')
    e=env_read(envfile);e['REMOTE_MCP_ALLOWED_HOSTS']='localhost:*,127.0.0.1:*,'+url.hostname;write_env(envfile,e)
    service='ch12-hosting-'+secrets.token_hex(4);image=f'{a.region}-docker.pkg.dev/{a.project}/{a.repository}/{service}:v1'
    # Reuse an already provisioned cloud provider secret; never upload laptop provider keys.
    secret_values={service+'-agent':e['CH12_AGENT_API_KEY'],service+'-mcp':e['REMOTE_MCP_API_KEY']}
    record={'service':service,'project':a.project,'region':a.region,'image':image,'secrets':[],'cleaned_up':False}
    state.write_text(json.dumps(record,indent=2))
    token=google(['auth','application-default','print-access-token']).strip()
    command(['docker','login','-u','oauth2accesstoken','--password-stdin',a.region+'-docker.pkg.dev'],token)
    with tempfile.TemporaryDirectory(prefix='ch12-build-') as td:
        d=Path(td);(d/'backend/marketplace').mkdir(parents=True)
        shutil.copy(APP/'backend/requirements.txt',d/'backend/requirements.txt')
        for f in ['http_mcp_client.py','hosting_worker.py']:shutil.copy(APP/'backend/marketplace'/f,d/'backend/marketplace'/f)
        shutil.copy(APP/'cloud/Dockerfile.hosting-lab',d/'Dockerfile')
        print('Building and pushing isolated agent image...',flush=True)
        command(['docker','buildx','build','--platform','linux/amd64','--push','-t',image,td])
    for name,value in secret_values.items():
        google(['secrets','create',name,'--replication-policy','automatic','--project',a.project])
        record['secrets'].append(name);state.write_text(json.dumps(record,indent=2))
        google(['secrets','versions','add',name,'--data-file=-','--project',a.project],value)
        google(['secrets','add-iam-policy-binding',name,'--member','serviceAccount:'+a.service_account,
          '--role','roles/secretmanager.secretAccessor','--project',a.project])
    finish_deploy(a,record,e,state,envfile)
if __name__=='__main__':main()
