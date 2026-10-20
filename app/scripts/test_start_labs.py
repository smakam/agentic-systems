"""Retirement regression: ordinary startup uses main/Test, never the old chapter labs."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPTS=Path(__file__).parent
FAKE_DOCKER='''#!/usr/bin/env python3
import json,os,sys
with open(os.environ['DOCKER_LOG'],'a') as f:f.write(json.dumps(sys.argv[1:])+'\\n')
if 'psql' in sys.argv and 'pg_database' in sys.argv[-1]: print(os.environ.get('TEST_DB_EXISTS','1'))
'''

class RetiredLabsTests(unittest.TestCase):
    def run_script(self, name, google=False, exists=True):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'scripts').mkdir();(root/'infra').mkdir();(root/'bin').mkdir()
            for file in ('start.sh','stop.sh','start-labs.sh'):shutil.copy(SCRIPTS/file,root/'scripts'/file)
            for file in ('configure-inference.py','provision-gateway-keys.py'):(root/'scripts'/file).write_text('# offline stub\n')
            (root/'infra/ensure-litellm.sql').write_text('-- offline bootstrap fixture\n')
            (root/'.env').write_text('# existing setup\n')
            if google:(root/'compose.google.local.yaml').touch()
            docker=root/'bin/docker';docker.write_text(FAKE_DOCKER);docker.chmod(0o755)
            log=root/'calls.jsonl';env={**os.environ,'PATH':str(root/'bin')+os.pathsep+os.environ['PATH'],'DOCKER_LOG':str(log),'TEST_DB_EXISTS':'1' if exists else '0'}
            result=subprocess.run(['sh',str(root/'scripts'/name)],env=env,text=True,capture_output=True)
            calls=[json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
            return result,calls

    def test_deprecated_entry_point_starts_nothing(self):
        result,calls=self.run_script('start-labs.sh')
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(calls,[])
        self.assertIn('retired',result.stdout)

    def test_normal_start_preserves_test_and_never_launches_chapter_overlays(self):
        for google in (False,True):
            with self.subTest(google=google):
                result,calls=self.run_script('start.sh',google=google)
                self.assertEqual(result.returncode,0,result.stderr)
                self.assertTrue(any('up' in c and '--build' in c for c in calls))
                self.assertTrue(any(c[-2:]==['restart','memory-frontend'] for c in calls))
                combined=' '.join(' '.join(c) for c in calls)
                for old in ('ch11','ch12','compose.course-','dropdb','--volumes','marketplace.seed'):
                    self.assertNotIn(old,combined)
                self.assertNotIn('CREATE DATABASE market_test',combined)
                self.assertEqual('compose.google.local.yaml' in combined,google)

    def test_missing_test_database_is_created_without_legacy_databases(self):
        result,calls=self.run_script('start.sh',exists=False)
        self.assertEqual(result.returncode,0,result.stderr)
        creates=[c[-1] for c in calls if c[-1].startswith('CREATE DATABASE')]
        self.assertEqual(creates,['CREATE DATABASE market_test OWNER market'])

    def test_stop_never_removes_volumes_or_uses_retired_profiles(self):
        result,calls=self.run_script('stop.sh',google=True)
        self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(len(calls),1)
        self.assertEqual(calls[0][-1],'stop')
        self.assertNotIn('--profile',calls[0]);self.assertNotIn('--volumes',calls[0])

if __name__=='__main__':unittest.main()
