"""Presentation endpoints retain Test, session, role and ownership boundaries."""
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient

from test_integration import reset
from marketplace.api import app
from marketplace.db import Conversation, Run, Session
from marketplace import agentic_ui_demo as demo, security_demo


def setup_run(owner='operator'):
    with Session.begin() as db:
        db.add(Conversation(id='presentation-chat', owner_id=owner, title='Comparison', items=[]))
        db.flush()
        db.add(Run(id='presentation-run', conversation_id='presentation-chat', revision=1,
                   question='Order status?', answer='Order is dispatched.', status='completed',
                   evidence={}, metrics={}, created_at=datetime.now(timezone.utc)))


def login(client):
    return client.post('/api/login', json={'username':'operator','password':'demo-marketplace'}).json()['csrf']


def test_compare_requires_session_csrf_test_gate_and_ownership(monkeypatch):
    setup_run(owner='support')
    monkeypatch.setenv('A2UI_DEMO','true')
    client=TestClient(app)
    path='/api/conversations/presentation-chat/runs/presentation-run/presentation'
    assert client.post(path,json={'mode':'controlled'}).status_code==401
    csrf=login(client)
    assert client.post(path,json={'mode':'controlled'}).status_code==403
    assert client.post(path,json={'mode':'controlled'},headers={'X-CSRF-Token':csrf}).status_code==404
    monkeypatch.setenv('A2UI_DEMO','false')
    assert client.post(path,json={'mode':'controlled'},headers={'X-CSRF-Token':csrf}).status_code==403


def test_comparison_preserves_investigation_and_closes_client(monkeypatch):
    setup_run()
    monkeypatch.setenv('A2UI_DEMO','true')
    from marketplace import tools, agent
    api=SimpleNamespace(close=AsyncMock())
    monkeypatch.setattr(tools,'client',lambda:api)
    monkeypatch.setattr(agent,'lf',None)
    generate=AsyncMock(return_value={'status':'completed','generation_mode':'controlled','model_output':'selection'})
    monkeypatch.setattr(demo,'compose',generate)
    client=TestClient(app);csrf=login(client)
    path='/api/conversations/presentation-chat/runs/presentation-run/presentation'
    response=client.post(path,json={'mode':'controlled'},headers={'X-CSRF-Token':csrf})
    assert response.status_code==200
    assert response.json()['generation_mode']=='controlled'
    generate.assert_awaited_once();api.close.assert_awaited_once()
    with Session() as db:
        run=db.get(Run,'presentation-run')
        assert run.question=='Order status?' and run.answer=='Order is dispatched.' and run.evidence=={}
        assert run.metrics['agentic_ui_variants']['controlled']['status']=='completed'
    assert client.post(path,json={'mode':'controlled','extra':True},headers={'X-CSRF-Token':csrf}).status_code==422
