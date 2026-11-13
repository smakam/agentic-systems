#!/usr/bin/env python3
"""Run regressions on the disposable database, never on shared Test/production."""
import json
from pathlib import Path
import subprocess

app=Path(__file__).resolve().parents[1]
container='marketplace-a2a-test-db'
info=json.loads(subprocess.check_output(['docker','inspect',container]))[0]
if info['Name']!='/'+container or set(info['NetworkSettings']['Networks'])!={'bridge'}:
    raise SystemExit('Expected the dedicated regression database on Docker bridge')
host=info['NetworkSettings']['Networks']['bridge']['IPAddress']
if not host.startswith('172.17.'):
    raise SystemExit('Unexpected regression database address')
command=['docker','run','--rm','--network','bridge',
         '-e',f'DATABASE_URL=postgresql+psycopg://market:market-local@{host}:5432/market_test',
         '-e',f'READ_DATABASE_URL=postgresql://agent_reader:reader-local@{host}:5432/market_test',
         '-e','DATA_DIR=/data','-e','LITELLM_API_KEY=test-only-not-a-real-key',
         '-e','LITELLM_URL=http://127.0.0.1:1/v1']
for source,target in ((app/'backend/marketplace','/app/marketplace'),(app/'backend/tests','/app/tests'),(app/'data','/data')):
    command+=['--mount',f'type=bind,source={source},target={target},readonly']
command+=['marketplace-a2ui-common-backend:local','python','-m','pytest','-q','--tb=short','tests']
raise SystemExit(subprocess.run(command).returncode)
