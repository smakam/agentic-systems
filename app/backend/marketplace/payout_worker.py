"""Deterministic payout worker. No LLM and no real payment-provider calls."""
import argparse
import fcntl
import json
import signal
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
import httpx


def rpc(client, url, token, name, arguments):
    for attempt in range(3):
        try:
            response = client.post(url, headers={'Authorization': 'Bearer ' + token,
                'Accept': 'application/json, text/event-stream'}, json={
                'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                'params': {'name': name, 'arguments': arguments}})
            response.raise_for_status()
            payload = response.json()
            if 'error' in payload or payload.get('result', {}).get('isError'):
                raise ValueError('Payout tool rejected request')
            result = payload['result']
            return result.get('structuredContent') or json.loads(result['content'][0]['text'])
        except (httpx.TransportError, httpx.HTTPStatusError):
            if attempt == 2:
                raise
            time.sleep(0.5 * (attempt + 1))


def run_once(config, client=None):
    run_id = 'run-' + uuid.uuid4().hex
    own_client = client is None
    client = client or httpx.Client(timeout=20)
    try:
        response = client.post(config['token_url'], data={'grant_type': 'client_credentials',
            'client_id': config['client_id'], 'client_secret': config['client_secret'],
            'scope': 'payouts:read payouts:release'})
        response.raise_for_status()
        token = response.json()['access_token']
        scan = rpc(client, config['mcp_url'], token, 'list_eligible_payouts',
                   {'limit': config['max_run_count'], 'run_id': run_id})
        if scan.get('enabled') is False:
            return {'run_id': run_id, 'at': datetime.now(timezone.utc).isoformat(), 'simulation': True,
                    'completed': [], 'denied': [], 'amount_paise': 0, 'status': 'disabled'}
        candidates = scan['candidates']
        completed, denied, spent = [], [], 0
        for candidate in candidates:
            if spent + candidate['amount_paise'] > config['max_run_paise']:
                continue
            payout_id = candidate['payout_id']
            try:
                result = rpc(client, config['mcp_url'], token, 'request_payout_release',
                    {'payout_id': payout_id, 'idempotency_key': 'simulated-payout:' + payout_id, 'run_id': run_id})
                completed.append(result['id'])
                spent += result['amount']
            except ValueError:
                denied.append(payout_id)
        return {'run_id': run_id, 'at': datetime.now(timezone.utc).isoformat(), 'simulation': True,
                'completed': completed, 'denied': denied, 'amount_paise': spent, 'status': 'complete'}
    finally:
        if own_client:
            client.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', default='/config/payout-worker.json')
    parser.add_argument('--state-dir', default='/state')
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--once', action='store_true')
    mode.add_argument('--interval', type=int, help='Explicit interval in seconds, at least 10; demo default 60')
    args = parser.parse_args()
    if args.interval is not None and args.interval < 10:
        parser.error('Scheduled interval must be at least 10 seconds')
    config = json.loads(Path(args.config).read_text())
    if config.get('simulation_only') is not True or config.get('workspace') != 'Test':
        parser.error('Worker requires explicit simulated Test configuration')
    state = Path(args.state_dir)
    state.mkdir(parents=True, exist_ok=True)
    lock = (state / 'worker.lock').open('a')
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        parser.error('A payout worker or one-shot is already running')
    stop = threading.Event()
    for sig in (signal.SIGTERM, signal.SIGINT):
        signal.signal(sig, lambda *_: stop.set())
    while not stop.is_set():
        try:
            result = run_once(config)
        except Exception as error:
            # Never log tokens, credentials or HTTP request bodies.
            result = {'at': datetime.now(timezone.utc).isoformat(), 'status': 'failed',
                      'error_type': type(error).__name__, 'simulation': True}
        with (state / 'runs.jsonl').open('a') as log:
            log.write(json.dumps(result) + '\n')
        print(json.dumps(result), flush=True)
        if args.once:
            if result['status'] == 'failed':
                raise SystemExit(1)
            break
        stop.wait(args.interval)


if __name__ == '__main__':
    main()
