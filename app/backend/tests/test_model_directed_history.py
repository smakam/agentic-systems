"""Agent-loop regression checks with isolated SQLite and a fake model runner."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from marketplace import agent as module
from marketplace.db import Conversation,Run

@pytest.mark.parametrize('question',[
    'What is the status of order-2?',
    'Show the chronological history and payout attempts for order-1.',
    'For ord-abc123, explain failed payout retries and the applicable policy.',
])
def test_model_starts_without_keyword_triggered_history(monkeypatch,question):
    engine=create_engine('sqlite://')
    for model in (Conversation,Run):model.__table__.create(engine)
    factory=sessionmaker(engine)
    with factory.begin() as db:
        db.add(Conversation(id='isolated',owner_id='support',title='test',items=[]))
    monkeypatch.setattr(module,'Session',factory)
    monkeypatch.setattr(module,'lf',None)
    api=SimpleNamespace(close=AsyncMock())
    monkeypatch.setattr(module,'client',lambda:api)
    ctx=SimpleNamespace(snapshot={'revision':2,'clock':'2026-09-27T12:00:00Z'},
                        doc_hash='policy-v1',evidence={},calls=0,
                        order_history=AsyncMock(side_effect=AssertionError('Application must not preload history')))
    observed=[]
    async def model_run(agent,input,**kwargs):
        assert ctx.order_history.call_count==0 and ctx.evidence=={}
        assert input.startswith(question+'\n\nApplication investigation metadata')
        assert 'Application-provided order-history evidence' not in input
        assert 'get_order_history' in {t.name for t in agent.tools}
        assert 'For histories, timelines or retries, use get_order_history' in agent.instructions
        observed.append(input)
        return SimpleNamespace(final_output='Model runner reached with no preloaded evidence')
    monkeypatch.setattr(module.Runner,'run',model_run)
    result=asyncio.run(module._answer('isolated',question,ctx,None,
                                     evaluation_config={'model':'test','alias':'test'}))
    assert result['status']=='completed' and len(observed)==1
    assert result['metrics']['preloaded_history'] is False
    assert result['evidence']=={}
    ctx.order_history.assert_not_called()
    api.close.assert_awaited_once()
    engine.dispose()
