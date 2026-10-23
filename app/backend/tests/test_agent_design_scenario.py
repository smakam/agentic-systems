"""Scenario preparation checks use rollback-only transactions; no resets or model calls."""
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select,func
from marketplace import api,agent_design_scenario as scenario,security_demo
from marketplace.db import Session,State,Order,Listing,Event,Item,Allocation,Payout,Return,Payment,Shipment

@pytest.mark.parametrize('role',['buyer','seller'])
def test_other_roles_cannot_prepare(role,monkeypatch):
    monkeypatch.setattr(security_demo,'is_test',lambda:True)
    api.app.dependency_overrides[api.identity]=lambda:SimpleNamespace(id='other',role=role)
    try:assert TestClient(api.app).post('/api/agent-design-demo/prepare-scenario',json={}).status_code==403
    finally:api.app.dependency_overrides.clear()

def test_unavailable_outside_test(monkeypatch):
    monkeypatch.setattr(security_demo,'is_test',lambda:False)
    api.app.dependency_overrides[api.identity]=lambda:SimpleNamespace(id='support',role='support')
    try:assert TestClient(api.app).post('/api/agent-design-demo/prepare-scenario',json={}).status_code==404
    finally:api.app.dependency_overrides.clear()

def test_prepare_is_reusable_and_preserves_existing_state(monkeypatch):
    monkeypatch.setattr(scenario,'require_test',lambda:None)
    with Session() as db:
        try:
            state=db.get(State,1);clock,revision=state.clock,state.revision
            original_orders=set(db.scalars(select(Order.id)))
            original_stock=dict(db.execute(select(Listing.id,Listing.stock)).all())
            first=scenario.prepare(db,'test-rehearsal-owner')
            assert not first['reused']
            assert first['payout_status']=='completed' and first['return_status']=='manual_review'
            assert first['shipment_status']=='delivered'
            assert first['order_id'] in first['question']
            assert state.clock==clock and state.revision==revision+1
            assert original_orders <= set(db.scalars(select(Order.id)))
            for key,value in original_stock.items():assert db.get(Listing,key).stock==value
            second=scenario.prepare(db,'test-rehearsal-owner')
            assert second['reused'] and second['order_id']==first['order_id']
            assert state.revision==revision+1
            item=db.scalar(select(Item).where(Item.order_id==first['order_id']))
            allocation=db.scalar(select(Allocation).where(Allocation.item_id==item.id))
            payout=db.scalar(select(Payout).where(Payout.allocation_id==allocation.id))
            payment=db.scalar(select(Payment).where(Payment.order_id==first['order_id']))
            shipment=db.scalar(select(Shipment).where(Shipment.item_id==item.id))
            assert payment.amount==allocation.gross==item.unit_price*item.quantity
            assert allocation.gross==allocation.fee+payout.amount and allocation.refunded==0
            events=db.scalars(select(Event).where(Event.entity_id.in_([payout.id,first['return_id']]))).all()
            paid=next(e for e in events if e.kind=='payout');returned=next(e for e in events if e.kind=='request_return')
            assert (paid.occurred_at-shipment.delivered_at).total_seconds()>=24*3600
            assert paid.occurred_at<returned.occurred_at<=clock
        finally:db.rollback()
