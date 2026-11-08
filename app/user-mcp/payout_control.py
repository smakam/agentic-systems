#!/usr/bin/env python3
"""Control the isolated simulated payout worker; explicit start required for scheduling."""
import argparse
import json
import os
from pathlib import Path
import subprocess
APP = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['service', 'once', 'start', 'stop', 'status'])
    parser.add_argument('--interval', type=int, default=60)
    args = parser.parse_args()
    if args.interval < 10:
        parser.error('Interval must be at least 10 seconds')
    command = ['docker', 'compose', '--env-file', str(APP / '.env.user-mcp'),
        '-f', str(APP / 'compose.user-mcp.yaml'), '-f', str(APP / 'compose.payout-mcp.yaml')]
    env = {**os.environ, 'PAYOUT_INTERVAL_SECONDS': str(args.interval)}
    operation = {'service': ['up', '-d', '--no-deps', 'payouts'],
        'once': ['run', '--rm', '--no-deps', 'payout-worker', '--once'],
        'start': ['up', '-d', '--no-deps', 'payout-worker'],
        'stop': ['stop', 'payout-worker'],
        'status': ['ps', '-a', 'payouts', 'payout-worker']}[args.action]
    subprocess.run(command + operation, cwd=APP, env=env, check=True)
    if args.action == 'status':
        path = APP / '.user-mcp/payout-runs/runs.jsonl'
        if path.exists():
            rows = path.read_text().splitlines()
            print('Recorded runs:', len(rows))
            if rows:
                print('Latest run:', rows[-1])


if __name__ == '__main__':
    main()
