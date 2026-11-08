"""Operator controls for persistent, default-off Test payout automation."""
import os
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, StrictBool
from sqlalchemy import select, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base, State, Session, Event


class PayoutAutomation(Base):
    __tablename__ = 'payout_automation'
    id: Mapped[int] = mapped_column(primary_key=True)
    enabled: Mapped[bool] = mapped_column(default=False)
    heartbeat_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_run_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_result: Mapped[dict | None] = mapped_column(JSON)
    service_policy: Mapped[dict | None] = mapped_column(JSON)


def is_test():
    return os.environ.get('DATABASE_URL', '').endswith('/market_test')


def enabled(db):
    row = db.get(PayoutAutomation, 1)
    return bool(is_test() and row and row.enabled)


def status(db):
    row = db.get(PayoutAutomation, 1) if is_test() else None
    now = datetime.now(timezone.utc)
    recent = db.scalars(select(Event).where(Event.kind == 'service_payout_run')
        .order_by(Event.recorded_at.desc()).limit(10)).all() if is_test() else []
    return {'enabled': bool(row and row.enabled), 'workspace': 'test' if is_test() else 'main',
        'can_configure': is_test(), 'interval_seconds': 60,
        'worker_running': bool(row and row.heartbeat_at and row.heartbeat_at >= now - timedelta(seconds=90)),
        'last_run_at': row.last_run_at.isoformat() if row and row.last_run_at else None,
        'last_result': row.last_result if row else None,
        'recent_runs': [event.details for event in recent],
        'policy': (row.service_policy if row and row.service_policy else
                   {'simulation_only': True, 'seller_ids': ['seller-1'], 'max_payout_paise': 1000000,
                    'max_run_paise': 2000000, 'max_run_count': 10, 'max_payouts_per_run': 10})}


class Toggle(BaseModel):
    model_config = ConfigDict(extra='forbid')
    enabled: StrictBool


def create_router(identity, db_session):
    router = APIRouter()

    @router.get('/api/payout-automation')
    def get_status(user=Depends(identity), db=Depends(db_session)):
        if user.role != 'operator':
            raise HTTPException(403, 'Operator access required')
        return status(db)

    @router.post('/api/payout-automation')
    def toggle(body: Toggle, user=Depends(identity), db=Depends(db_session)):
        if user.role != 'operator':
            raise HTTPException(403, 'Operator access required')
        if not is_test():
            raise HTTPException(403, 'Automation is available only in the simulated Test workspace')
        db.execute(select(State).where(State.id == 1).with_for_update()).scalar_one()
        row = db.get(PayoutAutomation, 1)
        if row is None:
            row = PayoutAutomation(id=1, enabled=False)
            db.add(row)
        row.enabled = body.enabled
        from .business import emit
        emit(db, db.get(State, 1), 'payout-automation', 'payout_automation_toggle',
             {'actor': user.id, 'enabled': body.enabled, 'simulation': True})
        db.commit()
        return status(db)

    return router
