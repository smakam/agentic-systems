"""Narrow service authorization and atomic simulated settlement; amounts are paise."""
import hashlib
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from sqlalchemy import select, func
from .db import Session, State, Payout, Allocation, Item, Return, Shipment, Command, Event
from .business import BusinessError, require, apply_simulated_payout, emit
from .payout_automation import PayoutAutomation, enabled as automation_enabled


class PayoutAccess:
    def __init__(self, policy_path, session_factory=Session):
        self.policy_path = Path(policy_path)
        self.session = session_factory

    def authorize(self, principal, scope):
        policy = json.loads(self.policy_path.read_text())
        require(policy.get('simulation_only') is True, 'Only simulated payouts are enabled')
        require(principal.issuer == policy['issuer'] and principal.client_id == policy['client_id']
                and principal.subject == policy['subject'], 'Payout service identity required')
        require(scope in principal.scopes, 'Required payout permission missing')
        require(policy.get('seller_ids') and all(type(policy[k]) is int and policy[k] > 0
                for k in ('max_payout_paise', 'max_run_paise', 'max_run_count')), 'Invalid service policy')
        return policy

    @staticmethod
    def actor(principal):
        digest = hashlib.sha256(json.dumps([principal.issuer, principal.subject, principal.client_id]).encode()).hexdigest()
        return 'payout-service:' + digest

    def eligible(self, principal, limit=10, run_id=None):
        policy = self.authorize(principal, 'payouts:read')
        require(type(limit) is int and 1 <= limit <= 50, 'Limit must be 1-50')
        require(run_id is None or (isinstance(run_id, str) and 8 <= len(run_id) <= 100), 'Invalid run identifier')
        with self.session.begin() as db:
            state = db.execute(select(State).where(State.id == 1).with_for_update()).scalar_one()
            automation = db.get(PayoutAutomation, 1)
            if automation is None:
                automation = PayoutAutomation(id=1, enabled=False)
                db.add(automation)
            automation.service_policy = {k: policy[k] for k in ('simulation_only', 'seller_ids',
                'max_payout_paise', 'max_run_paise', 'max_run_count')}
            automation.service_policy['max_payouts_per_run'] = policy['max_run_count']
            automation.heartbeat_at = datetime.now(timezone.utc)
            if not automation.enabled:
                return {'simulation': True, 'enabled': False, 'candidates': [], 'revision': state.revision,
                        'as_of': state.clock.isoformat()}
            rows = db.execute(select(Payout, Allocation, Item, Shipment).join(Allocation, Payout.allocation_id == Allocation.id)
                .join(Item, Allocation.item_id == Item.id).join(Shipment, Shipment.item_id == Item.id)
                .where(Item.seller_id.in_(policy['seller_ids']), Payout.status.in_(['held', 'failed']),
                       Payout.amount > 0, Payout.amount <= policy['max_payout_paise'],
                       Shipment.status == 'delivered', Shipment.delivered_at <= state.clock - timedelta(hours=24))
                .order_by(Payout.id)).all()
            candidates = []
            for payout, allocation, item, shipment in rows:
                active = db.scalar(select(func.count()).select_from(Return).where(Return.item_id == item.id,
                    Return.status.in_(['requested', 'approved', 'received'])))
                if not active:
                    candidates.append({'payout_id': payout.id, 'seller_id': item.seller_id,
                                       'amount_paise': payout.amount, 'currency': 'INR', 'status': payout.status})
                if len(candidates) == min(limit, policy['max_run_count']):
                    break
            if run_id is not None:
                automation.last_run_at = datetime.now(timezone.utc)
                automation.last_result = {'status': 'complete', 'run_id': run_id,
                    'completed': [], 'denied': [], 'amount_paise': 0}
                emit(db, state, 'payout-automation', 'service_payout_run',
                     {'actor': self.actor(principal), 'at': automation.last_run_at.isoformat(),
                      'candidate_count': len(candidates), 'simulation': True, **automation.last_result})
            return {'simulation': True, 'enabled': True, 'candidates': candidates, 'revision': state.revision,
                    'as_of': state.clock.isoformat()}

    def release(self, principal, payout_id, idempotency_key, run_id):
        policy = self.authorize(principal, 'payouts:release')
        require(all(isinstance(x, str) for x in (payout_id, idempotency_key, run_id)), 'String identifiers required')
        require(1 <= len(payout_id) <= 100 and 8 <= len(idempotency_key) <= 120
                and 8 <= len(run_id) <= 100, 'Invalid payout, retry or run identifier')
        actor = self.actor(principal)
        details = {'actor': actor, 'issuer': principal.issuer, 'subject': principal.subject,
                   'client_id': principal.client_id, 'run_id': run_id, 'id': payout_id, 'simulation': True}
        try:
            with self.session.begin() as db:
                state = db.execute(select(State).where(State.id == 1).with_for_update()).scalar_one()
                require(automation_enabled(db), 'Automatic payout is disabled')
                payout = db.get(Payout, payout_id)
                require(payout is not None, 'Payout unavailable for this service')
                allocation = db.get(Allocation, payout.allocation_id)
                item = db.get(Item, allocation.item_id)
                require(item.seller_id in policy['seller_ids'], 'Payout unavailable for this service')
                require(0 < payout.amount <= policy['max_payout_paise'], 'Payout exceeds service amount limit')
                key = actor + ':' + idempotency_key
                fingerprint = hashlib.sha256(json.dumps(['simulated-payout', payout_id]).encode()).hexdigest()
                previous = db.get(Command, key)
                if previous:
                    require(previous.fingerprint == fingerprint, 'Idempotency key already used for a different request')
                    emit(db, state, payout_id, 'service_payout_retry', {**details, 'result': 'replayed'})
                    return previous.result
                events = db.scalars(select(Event).where(Event.kind == 'service_payout_release')).all()
                run = [e for e in events if e.details.get('actor') == actor and e.details.get('run_id') == run_id]
                require(len(run) < policy['max_run_count'], 'Run payout count limit reached')
                require(sum(e.details['amount_paise'] for e in run) + payout.amount <= policy['max_run_paise'],
                        'Run payout amount limit reached')
                state.revision += 1
                result = apply_simulated_payout(db, state, {'id': payout_id, 'outcome': 'completed'})
                result.update(simulation=True, run_id=run_id, actor=actor, revision=state.revision,
                              as_of=state.clock.isoformat())
                automation = db.get(PayoutAutomation, 1)
                summary = automation.last_result
                if summary and summary.get('run_id') == run_id:
                    automation.last_result = {**summary, 'completed': summary['completed'] + [payout_id],
                                              'amount_paise': summary['amount_paise'] + payout.amount}
                    self.update_run_event(db, run_id, automation.last_result)
                db.add(Command(id=key, actor_id=actor, fingerprint=fingerprint, result=result))
                emit(db, state, payout_id, 'service_payout_release',
                     {**details, 'result': 'completed', 'amount_paise': payout.amount})
                return result
        except BusinessError as error:
            with self.session.begin() as db:
                state = db.execute(select(State).where(State.id == 1).with_for_update()).scalar_one()
                automation = db.get(PayoutAutomation, 1)
                if automation and automation.last_result and automation.last_result.get('run_id') == run_id:
                    automation.last_result = {**automation.last_result,
                        'denied': automation.last_result.get('denied', []) + [payout_id]}
                    self.update_run_event(db, run_id, automation.last_result)
                emit(db, state, payout_id, 'service_payout_denied', {**details, 'result': 'denied', 'reason': str(error)})
            raise

    @staticmethod
    def update_run_event(db, run_id, summary):
        event = db.scalar(select(Event).where(Event.kind == 'service_payout_run',
            Event.details['run_id'].as_string() == run_id))
        if event is not None:
            event.details = {**event.details, **summary}
