#!/usr/bin/env python3
"""Install the combined local review build in Test; preserve rollback containers."""
import json
from pathlib import Path
import shlex
import subprocess
import tempfile
from datetime import datetime, timezone

APP=Path(__file__).resolve().parents[1]
TARGETS=['marketplace-lab-test-backend-1','marketplace-lab-test-frontend-1']
PROTECTED=['marketplace-lab-backend-1','marketplace-lab-frontend-1']


def docker(*args):
    r=subprocess.run(['docker',*args],capture_output=True,text=True)
    if r.returncode:raise RuntimeError(f'Docker {args[0]} failed: {r.stderr[:400]}')
    return r.stdout.strip()


def state():
    return docker('exec','marketplace-lab-postgres-1','psql','-U','postgres','-d','market_test','-Atc',
                  'SELECT revision,clock,(SELECT COUNT(*) FROM orders),(SELECT COUNT(*) FROM runs) FROM state WHERE id=1')


def update():
    configs=json.loads(docker('inspect',*TARGETS))
    protected=json.loads(docker('inspect',*PROTECTED))
    fingerprints=[(x['Id'],x['State']['StartedAt']) for x in protected]
    before=state()
    running=docker('exec','marketplace-lab-postgres-1','psql','-U','postgres','-d','market_test','-Atc',
                   "SELECT COUNT(*) FROM runs WHERE status='running'")
    if running!='0':raise RuntimeError('Wait for the active Test investigation before updating')
    directory=Path(tempfile.mkdtemp(prefix='a2ui-common-rollback-'));directory.chmod(0o700)
    snapshot=directory/'containers.json';snapshot.write_text(json.dumps(configs));snapshot.chmod(0o600)
    backup=directory/'market-test.dump'
    with backup.open('wb') as out:
        subprocess.run(['docker','exec','marketplace-lab-postgres-1','pg_dump','-U','postgres','-Fc','market_test'],stdout=out,check=True)
    backup.chmod(0o600)
    suffix='-before-a2ui-'+datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
    changed=[]
    try:
        for config in configs:
            name=config['Name'].lstrip('/');backend=name==TARGETS[0]
            env=dict(x.split('=',1) for x in config['Config']['Env'])
            if backend:
                if not env['DATABASE_URL'].endswith('/market_test'):raise RuntimeError('Refusing non-Test target')
                env.update(A2UI_DEMO='true',INITIALIZE_ON_STARTUP='false')
                env.pop('MARKETPLACE_SESSION_COOKIE',None)
            envfile=directory/(name+'.env');envfile.write_text('\n'.join(f'{k}={v}' for k,v in env.items())+'\n');envfile.chmod(0o600)
            network=next(iter(config['NetworkSettings']['Networks']))
            docker('stop',name);docker('rename',name,name+suffix);changed.append(name)
            args=['create','--name',name,'--network',network,'--env-file',str(envfile)]
            for alias in config['NetworkSettings']['Networks'][network].get('Aliases') or []:
                if alias!=name:args+=['--network-alias',alias]
            for mount in config['Mounts']:
                source=mount['Source']
                if backend and mount['Destination']=='/app/marketplace':source=str(APP/'backend/marketplace')
                if not backend and mount['Destination']=='/etc/nginx/conf.d/default.conf':source=str(APP/'infra/nginx-memory.conf')
                args+=['--mount',f"type={mount['Type']},source={source},target={mount['Destination']}"+(',readonly' if not mount['RW'] else '')]
            for port,bindings in (config['HostConfig']['PortBindings'] or {}).items():
                for binding in bindings:args+=['-p',f"{binding['HostIp']}:{binding['HostPort']}:{port}"]
            health=config['Config'].get('Healthcheck')
            if health and health.get('Test',[None])[0]=='CMD':
                args+=['--health-cmd',shlex.join(health['Test'][1:]),'--health-interval','5s','--health-timeout','3s','--health-retries','30']
            args+=['marketplace-a2ui-common-backend:local' if backend else 'marketplace-a2ui-common-frontend:local']
            docker(*args);docker('start',name);envfile.unlink()
        if state()!=before:raise RuntimeError('Test business state changed during preview update')
        after=json.loads(docker('inspect',*PROTECTED))
        assert fingerprints==[(x['Id'],x['State']['StartedAt']) for x in after]
    except Exception:
        for name in reversed(changed):
            present=set(docker('ps','-a','--format','{{.Names}}').splitlines())
            if name in present:docker('rm','-f',name)
            docker('rename',name+suffix,name);docker('start',name)
        raise
    print('Combined A2A/A2UI Test preview installed on port 5179. Test business state and production containers unchanged during this update.')
    print('Rollback snapshot:',directory)


if __name__=='__main__':update()
