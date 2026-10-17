"""Offline startup checks: preserve seeded labs and avoid implicit cloud operations."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).with_name('start-labs.sh')
FAKE_DOCKER = r'''#!/usr/bin/env python3
import json,os,sys,re
from pathlib import Path
args=sys.argv[1:]
with open(os.environ['DOCKER_LOG'],'a') as f:f.write(json.dumps(args)+'\n')
p=Path(os.environ['FAKE_DATABASES']);dbs=json.loads(p.read_text())
if 'createdb' in args:
    if os.environ.get('FAIL_CREATE')=='yes':sys.exit(23)
    dbs[args[-1]]=False;p.write_text(json.dumps(dbs))
elif 'psql' in args:
    sql=args[-1]
    if 'pg_database' in sql:
        name=re.search("datname='([^']+)'",sql).group(1);print(int(name in dbs))
    elif 'to_regclass' in sql:
        name=args[args.index('-d')+1];print('state' if dbs.get(name) else '')
    elif 'FROM public.state' in sql:
        name=args[args.index('-d')+1];print(int(dbs.get(name,False)))
elif 'run' in args:
    name=re.search("engine.url.database == '([^']+)'",args[-1]).group(1)
    dbs[name]=True;p.write_text(json.dumps(dbs))
'''

class StartLabsTests(unittest.TestCase):
    def run_start(self, databases, key=False, fail=False):
        with tempfile.TemporaryDirectory() as directory:
            app=Path(directory);(app/'scripts').mkdir();(app/'bin').mkdir()
            shutil.copy(SCRIPT,app/'scripts/start-labs.sh')
            docker=app/'bin/docker';docker.write_text(FAKE_DOCKER);docker.chmod(0o755)
            state=app/'databases.json';state.write_text(json.dumps(databases));log=app/'calls.jsonl'
            if key:(app/'.course-runtime-and-hosting.env').write_text('REMOTE_MCP_API_KEY='+'a'*32+'\n')
            env={**os.environ,'PATH':str(app/'bin')+os.pathsep+os.environ['PATH'],'DOCKER_LOG':str(log),'FAKE_DATABASES':str(state),'FAIL_CREATE':'yes' if fail else 'no'}
            result=subprocess.run(['sh',str(app/'scripts/start-labs.sh')],env=env,capture_output=True,text=True)
            calls=[json.loads(line) for line in log.read_text().splitlines()]
            return result,calls,json.loads(state.read_text())

    def test_seeded_labs_are_not_initialized_or_indexed(self):
        original={'ch11_loop_lab':True,'ch12_hosting_lab':True,'market':True,'market_test':True,'market_eval':True}
        result,calls,state=self.run_start(original)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(state,original)
        self.assertFalse(any('createdb' in c or 'run' in c or 'marketplace.index' in c for c in calls))
        up=[c for c in calls if 'up' in c]
        self.assertEqual(len(up),1)
        self.assertEqual(up[0][-4:],['ch11-backend','ch11-frontend','ch12-backend','ch12-frontend'])
        self.assertIn('--no-deps',up[0]);self.assertIn('--wait',up[0])
        self.assertFalse(any('dropdb' in c or 'pg_restore' in c for c in calls))

    def test_missing_labs_are_initialized_once_without_touching_main(self):
        result,calls,state=self.run_start({'market':True,'market_test':True,'market_eval':True})
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual([c[-1] for c in calls if 'createdb' in c],['ch11_loop_lab','ch12_hosting_lab'])
        self.assertEqual(len([c for c in calls if 'run' in c]),2)
        self.assertEqual(len([c for c in calls if 'marketplace.index' in c]),2)
        self.assertTrue(all(state.values()));self.assertEqual(len(state),5)

    def test_existing_empty_lab_is_recoverable_without_drop(self):
        result,calls,state=self.run_start({'ch11_loop_lab':False,'ch12_hosting_lab':True})
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(any('createdb' in c for c in calls))
        self.assertEqual(len([c for c in calls if 'run' in c]),1)
        self.assertTrue(all(state.values()))

    def test_http_mcp_is_started_only_when_auth_configuration_exists(self):
        result,calls,_=self.run_start({'ch11_loop_lab':True,'ch12_hosting_lab':True},key=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertTrue(any('up' in c and c[-1]=='ch12-mcp' for c in calls))
        self.assertFalse(any('gcloud' in c or 'tunnel' in c for c in calls))

    def test_database_creation_failure_does_not_claim_startup_success(self):
        result,calls,_=self.run_start({},fail=True)
        self.assertEqual(result.returncode,23)
        self.assertFalse(any('up' in c for c in calls))
        self.assertNotIn('Existing lab data preserved',result.stdout)

if __name__ == '__main__':
    unittest.main()
