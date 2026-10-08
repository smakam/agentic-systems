"""Non-destructive feedback checks; synthetic runs only, no model calls/reset."""
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, delete
from marketplace import api, feedback
from marketplace.db import Session, User, Conversation, Run, AnswerFeedback, init_schema

@pytest.fixture
def sample(monkeypatch):
    init_schema()
    with Session() as db:
        owner=db.scalar(select(User).where(User.username=='operator'))
        other=db.scalar(select(User).where(User.username=='support'))
        assert owner and other
        cid='feedback-check-'+uuid4().hex; rid='feedback-run-'+uuid4().hex
        db.add(Conversation(id=cid,owner_id=owner.id,title='Synthetic feedback check',items=[]))
        db.flush()
        db.add(Run(id=rid,conversation_id=cid,revision=24,question='Synthetic feedback check',answer='Synthetic answer',status='completed',evidence={},metrics={'trace_id':'synthetic-not-exported'},created_at=datetime.now(timezone.utc)))
        db.commit()
    exports=[]
    monkeypatch.setattr(feedback,'export_rating',lambda run,rating,user_id:exports.append((run.id,rating,user_id)))
    client=TestClient(api.app)
    try: yield client,owner,other,cid,rid,exports
    finally:
        api.app.dependency_overrides.clear()
        with Session.begin() as db:
            db.execute(delete(AnswerFeedback).where(AnswerFeedback.run_id==rid))
            db.execute(delete(Run).where(Run.id==rid))
            db.execute(delete(Conversation).where(Conversation.id==cid))


def test_rating_persists_and_changes_without_double_counting(sample):
    client,owner,other,cid,rid,exports=sample
    url=f'/api/conversations/{cid}/runs/{rid}/feedback'
    assert client.post(url,json={'rating':'up'}).status_code==401
    api.app.dependency_overrides[api.identity]=lambda:owner
    assert client.post(url,json={'rating':'up'}).json()['rating']=='up'
    assert client.get(f'/api/conversations/{cid}/runs').json()[0]['feedback']=='up'
    assert client.post(url,json={'rating':'down'}).status_code==200
    with Session() as db:
        rows=db.scalars(select(AnswerFeedback).where(AnswerFeedback.run_id==rid)).all()
        assert len(rows)==1 and rows[0].rating=='down' and rows[0].user_id==owner.id
    assert exports==[(rid,'up',owner.id),(rid,'down',owner.id)]


def test_other_user_invalid_rating_and_missing_run_rejected(sample):
    client,owner,other,cid,rid,exports=sample
    api.app.dependency_overrides[api.identity]=lambda:other
    assert client.post(f'/api/conversations/{cid}/runs/{rid}/feedback',json={'rating':'up'}).status_code==404
    api.app.dependency_overrides[api.identity]=lambda:owner
    assert client.post(f'/api/conversations/{cid}/runs/{rid}/feedback',json={'rating':'great'}).status_code==422
    assert client.post(f'/api/conversations/{cid}/runs/missing/feedback',json={'rating':'up'}).status_code==404
    with Session.begin() as db: db.get(Run,rid).status='running'
    assert client.post(f'/api/conversations/{cid}/runs/{rid}/feedback',json={'rating':'up'}).status_code==409
    assert not exports


def test_trace_export_uses_stable_score_and_failure_is_nonfatal(monkeypatch):
    import langfuse
    scores=[]
    class FakeClient:
        def create_score(self,**kwargs):scores.append(kwargs)
        def flush(self):raise RuntimeError('synthetic unavailable')
    monkeypatch.setattr(langfuse,'Langfuse',FakeClient)
    monkeypatch.setenv('LANGFUSE_PUBLIC_KEY','synthetic');monkeypatch.setenv('LANGFUSE_SECRET_KEY','synthetic')
    run=SimpleNamespace(id='synthetic-run',metrics={'trace_id':'synthetic-trace'})
    feedback.export_rating(run,'up','synthetic-user');feedback.export_rating(run,'down','synthetic-user')
    assert scores[0]['score_id']==scores[1]['score_id']
    assert [s['value'] for s in scores]==[1,0]
    assert all(s['trace_id']=='synthetic-trace' and s['name']=='user_feedback' for s in scores)
