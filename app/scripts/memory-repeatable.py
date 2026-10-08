"""Versioned memory-use fixtures. Always restore disposable market_test on exit.

Default: validate fixtures twice, no inference. --live: execute prompts, no judge.
Run through memory-repeatable.sh; never concurrently with another test runner.
"""
import argparse
import asyncio
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from sqlalchemy import select, text
from sqlalchemy.engine import make_url

# Check both connections before importing any application module or resetting.
for key in ('DATABASE_URL', 'READ_DATABASE_URL'):
    if make_url(os.environ[key]).database != 'market_test':
        raise RuntimeError(f'{key} must target disposable market_test')

from marketplace.db import Base, engine, Session, init_schema, Conversation, Memory, State, Payout, Shipment, User
from marketplace.seed import seed
from marketplace.business import execute, uid
from marketplace.memory import MemoryStore
from marketplace.agent import answer, PROMPT_VERSION

parser = argparse.ArgumentParser()
parser.add_argument('--live', action='store_true')
parser.add_argument('--model', choices=['nano', '54'], default='54')
parser.add_argument('--scenario', help='Run only one scenario ID from cases.json')
mode = parser.add_mutually_exclusive_group()
mode.add_argument('--prepare', help='Prepare one scenario for manual UI testing; leave it loaded')
mode.add_argument('--reset', action='store_true', help='Restore the clean seeded baseline only')
args = parser.parse_args()
spec_path = Path('/eval/memory-v2/cases.json')
spec = json.loads(spec_path.read_text())
by_id = {s['id']: s for s in spec['scenarios']}
for selected in (args.scenario, args.prepare):
    if selected and selected not in by_id:
        parser.error('Unknown scenario: ' + selected)
if args.live and (args.prepare or args.reset):
    parser.error('--live cannot be combined with --prepare or --reset')
out = Path('/results') / ('memory-repeatable-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
out.mkdir()
rows = []

def reset():
    init_schema()
    with engine.begin() as conn:
        names = ','.join('public.' + t.name for t in reversed(Base.metadata.sorted_tables))
        conn.execute(text(f'TRUNCATE {names} CASCADE'))
    with Session.begin() as db:
        seed(db)

def fingerprint():
    with Session() as db:
        state = db.get(State, 1)
        return {'revision': state.revision, 'clock': state.clock.isoformat(),
                'payouts': [[p.id, p.status, p.amount] for p in db.scalars(select(Payout).order_by(Payout.id))],
                'shipments': [[s.id, s.status, str(s.delivered_at)] for s in db.scalars(select(Shipment).order_by(Shipment.id))],
                'memories': [[m.owner_id, m.kind, m.title, m.content, m.version] for m in db.scalars(select(Memory).order_by(Memory.title))]}

def chat():
    cid = uid('memory-repeat')
    with Session.begin() as db:
        db.add(Conversation(id=cid, owner_id='support', title='Repeatable memory lab', items=[]))
    return cid

def prepare(scenario):
    reset()
    cid = chat()
    with Session() as db:
        state = db.get(State, 1)
        snapshot = {'revision': state.revision, 'clock': state.clock.isoformat()}
    if scenario['memory']:
        MemoryStore('support', cid, snapshot, allow_write=True).save(**scenario['memory'])
    with Session.begin() as db:
        actor = db.get(User, 'operator')
        if scenario['mutation'] == 'complete_payout_1':
            execute(db, actor, uid('retry'), 'payout', {'id': 'payout-1', 'outcome': 'completed'})
        elif scenario['mutation'] == 'deliver_order_2':
            execute(db, actor, uid('dispatch'), 'dispatch', {'id': 'shipment-3'})
            execute(db, actor, uid('deliver'), 'deliver', {'id': 'shipment-3'})
    actual = fingerprint()
    if scenario['id'] == 'checkpoint':
        assert actual['revision'] == 2
        assert next(p for p in actual['payouts'] if p[0] == 'payout-1')[1] == 'completed'
    if scenario['id'] == 'policy-conflict':
        assert next(s for s in actual['shipments'] if s[0] == 'shipment-3')[1] == 'delivered'
        with Session() as db:
            assert db.get(Shipment, 'shipment-3').delivered_at == db.get(State, 1).clock
            assert db.get(Payout, 'payout-3').status == 'held'
    return actual

config = ({'alias': 'eval-54', 'model': 'gpt-5.4-2026-03-05', 'input_rate': 2.5, 'output_rate': 15., 'budget': 1.}
          if args.model == '54' else
          {'alias': 'eval-nano', 'model': 'gpt-5-nano-2025-08-07', 'input_rate': .05, 'output_rate': .4, 'budget': .05})
config['tool_transport'] = 'mcp'

async def ask(scenario, cid, turn, enabled):
    result = await answer(cid, turn['question'], evaluation_config=config, memory_enabled=enabled, memory_write=False)
    operations = result.get('metrics', {}).get('memory_operations', [])
    retrieved = any(op.get('operation') == 'search' and op.get('ids') for op in operations)
    row = {'scenario': scenario['id'], 'conversation_id': cid, 'memory_enabled': enabled,
           'question': turn['question'], 'expected': turn['expected'], 'result': result,
           'checks': {'completed': result['status'] == 'completed',
                      'required_memory_retrieved': retrieved if turn.get('must_retrieve') else None,
                      'no_memory_writes': all(op.get('operation') == 'search' for op in operations),
                      'memory_off_no_operations': not operations if not enabled else None},
           'answer_grade': 'review_required'}
    rows.append(row)
    (out / 'results.json').write_text(json.dumps(rows, indent=2, default=str))
    print(scenario['id'], result['status'], row['checks'], flush=True)

async def main():
    if args.prepare or args.reset:
        fixture = prepare(by_id[args.prepare]) if args.prepare else None
        if args.reset:
            reset()
            fixture = fingerprint()
        (out / 'manifest.json').write_text(json.dumps({'suite': spec['version'], 'mode': 'prepare' if args.prepare else 'reset', 'scenario': args.prepare, 'fixture': fixture, 'model_calls': 0}, indent=2))
        print('Results:', out, 'Fixture left loaded for UI testing.' if args.prepare else 'Baseline restored.', flush=True)
        return
    reset()
    baseline = fingerprint()
    fixture_checks = []
    try:
        for scenario in ([by_id[args.scenario]] if args.scenario else spec['scenarios']):
            first = prepare(scenario)
            second = prepare(scenario)
            assert first == second, 'Scenario reset must reproduce semantic fixture'
            fixture_checks.append({'scenario': scenario['id'], 'repeatable': True, 'fixture': second})
            if args.live:
                before = fingerprint()
                cid = chat()
                for turn in scenario['turns']:
                    await ask(scenario, cid, turn, scenario['id'] != 'short-history-memory-off')
                await ask(scenario, chat(), {'question': scenario['control'], 'expected': scenario['control_expected']}, False)
                assert fingerprint() == before, 'Answer runs must not mutate memories or business state'
    finally:
        reset()
        restored = fingerprint()
        assert restored == baseline, 'Baseline restoration failed'
        manifest = {'suite': spec['version'], 'spec_sha256': hashlib.sha256(spec_path.read_bytes()).hexdigest(),
                    'seed_sha256': hashlib.sha256(Path('/app/marketplace/seed.py').read_bytes()).hexdigest(),
                    'runner_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    'prompt_version': PROMPT_VERSION, 'mode': 'live' if args.live else 'fixture-only',
                    'model': config if args.live else None, 'fixtures': fixture_checks,
                    'baseline_restored': True, 'baseline': restored, 'questions_run': len(rows),
                    'estimated_model_cost_usd': sum(r['result'].get('metrics', {}).get('estimated_model_cost_usd', 0) for r in rows),
                    'grading': 'Tool checks are deterministic; text correctness requires review. No paid judge.'}
        (out / 'manifest.json').write_text(json.dumps(manifest, indent=2, default=str))
        (out / 'cases.json').write_bytes(spec_path.read_bytes())
        print('Results:', out, 'Baseline restored.', flush=True)

asyncio.run(main())
