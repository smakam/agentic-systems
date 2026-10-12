"""Exercise regional host selection without contacting Google or storing real keys."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'configure-langfuse.sh'


class RegionalHostTests(unittest.TestCase):
    def run_helper(self, host):
        with tempfile.TemporaryDirectory() as tmp:
            work = Path(tmp)
            mock = work / 'gcloud'
            mock.write_text('#!/bin/sh\ncat >/dev/null\nprintf "call\\n" >> gcloud-calls\n')
            mock.chmod(0o755)
            env = {**os.environ, 'PATH': str(work) + os.pathsep + os.environ['PATH'],
                   'MARKETPLACE_GCP_PROJECT': 'synthetic-lab-project'}
            env.pop('MARKETPLACE_LF_HOST', None)
            if host is not None:
                env['MARKETPLACE_LF_HOST'] = host
            result = subprocess.run(['bash', str(SCRIPT)], cwd=tmp, env=env,
                                    input='pk-lf-synthetic\nsk-lf-synthetic\n',
                                    text=True, capture_output=True)
            config = work / 'langfuse-public.env'
            calls = work / 'gcloud-calls'
            return result, config.read_text() if config.exists() else None, calls.read_text() if calls.exists() else ''

    def test_selected_regions_are_saved_without_secret(self):
        for host in ['https://cloud.langfuse.com', 'https://us.cloud.langfuse.com',
                     'https://jp.cloud.langfuse.com/', 'https://hipaa.cloud.langfuse.com']:
            with self.subTest(host=host):
                result, config, calls = self.run_helper(host)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('LANGFUSE_HOST=' + host.rstrip('/'), config)
                self.assertNotIn('sk-lf-synthetic', config + result.stdout + result.stderr)
                self.assertEqual(calls.count('call'), 2)

    def test_invalid_hosts_fail_before_any_secret_write(self):
        for host in ['http://cloud.langfuse.com', 'https://example.com', 'https://jp.cloud.langfuse.com/path']:
            with self.subTest(host=host):
                result, config, calls = self.run_helper(host)
                self.assertNotEqual(result.returncode, 0)
                self.assertIsNone(config)
                self.assertEqual(calls, '')

    def test_missing_host_requires_explicit_configuration(self):
        result, config, calls = self.run_helper(None)
        self.assertNotEqual(result.returncode, 0)
        self.assertIsNone(config)
        self.assertEqual(calls, '')


if __name__ == '__main__':
    unittest.main()
