"""Conversation history order with isolated in-memory records; no model calls."""
from datetime import datetime,timedelta,timezone
from types import SimpleNamespace
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
import pytest
from marketplace.api import conversations
from marketplace.db import Seller,User,Conversation,Run,MemoryConversation

@pytest.fixture
def history():
    engine=create_engine('sqlite://')
    for model in (Seller,User,Conversation,Run,MemoryConversation):model.__table__.create(engine)
    with Session(engine) as db:
        db.add_all([User(id=u,username=u,password_hash='unused-test-hash',role='support') for u in ['owner','other']])
        db.add_all([Conversation(id=cid,owner_id=owner,title=cid,items=[]) for cid,owner in [('newest','owner'),('old','owner'),('empty','owner'),('foreign','other')]])
        start=datetime(2026,10,18,tzinfo=timezone.utc)
        db.add_all([Run(id=cid,conversation_id=cid,revision=1,question='q',answer='a',status='completed',created_at=start+timedelta(hours=hour)) for cid,hour in [('newest',2),('old',1),('foreign',3)]])
        db.commit()
        yield db,start
    engine.dispose()


def test_newest_activity_first_and_empty_conversations_last(history):
    db,_=history
    assert [c['id'] for c in conversations(SimpleNamespace(id='owner',role='support'),db)] == ['newest','old','empty']


def test_followup_moves_an_older_conversation_to_the_top(history):
    db,start=history
    db.add(Run(id='follow-up',conversation_id='old',revision=1,question='again',answer='a',status='completed',created_at=start+timedelta(hours=4)))
    db.commit()
    assert [c['id'] for c in conversations(SimpleNamespace(id='owner',role='support'),db)] == ['old','newest','empty']


def test_history_keeps_owner_isolation_and_runtime_provider_metadata(history):
    db,_=history
    db.add(MemoryConversation(conversation_id='old',provider='mem0'));db.commit()
    rows=conversations(SimpleNamespace(id='other',role='support'),db)
    assert [c['id'] for c in rows] == ['foreign']
    rows=conversations(SimpleNamespace(id='owner',role='support'),db)
    assert all(c['runtime']=='sdk' for c in rows)
    assert next(c for c in rows if c['id']=='old')['memory_provider']=='mem0'


def test_history_limits_to_50_latest_owned_conversations(history):
    db,start=history
    for index in range(60):
        cid=f'history-{index:02}'
        db.add(Conversation(id=cid,owner_id='owner',title=cid,items=[]))
        db.add(Run(id=cid,conversation_id=cid,revision=1,question='q',answer='a',status='completed',created_at=start+timedelta(days=1,minutes=index)))
    # A newer question in an older investigation determines its position.
    db.add(Run(id='latest-followup',conversation_id='old',revision=1,question='again',answer='a',status='completed',created_at=start+timedelta(days=2)))
    db.commit()
    rows=conversations(SimpleNamespace(id='owner',role='support'),db)
    assert [c['id'] for c in rows] == ['old']+[f'history-{i:02}' for i in range(59,10,-1)]
    # The display limit does not delete any saved conversations or questions.
    assert db.get(Conversation,'history-00') is not None
    assert db.get(Run,'history-00') is not None
