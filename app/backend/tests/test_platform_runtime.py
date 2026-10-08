"""Platform boundaries without paid model calls or changes to business data."""
import asyncio
from types import SimpleNamespace

import httpx
import pytest
from pydantic import ValidationError
from marketplace import platform_runtime as rt
from marketplace.api import Question, NewConversation

RESOURCE='projects/123/locations/us-central1/reasoningEngines/456'

@pytest.fixture(autouse=True)
def settings(monkeypatch):
    for name in ('LANGFUSE_PUBLIC_KEY','LANGFUSE_SECRET_KEY','LYZR_API_KEY','LYZR_AGENT_ID','GOOGLE_RUNTIME_RESOURCE'):
        monkeypatch.delenv(name,raising=False)
    monkeypatch.setenv('MARKETPLACE_IDENTITY_NAMESPACE','test-fixture')


def test_runtime_binding_and_identity_are_stable_and_isolated(monkeypatch):
    monkeypatch.setenv('LYZR_AGENT_ID','agent-test')
    first=rt.initial_items('lyzr','operator-id','conversation-a')
    second=rt.initial_items('lyzr','operator-id','conversation-b')
    support=rt.initial_items('lyzr','support-id','conversation-a')
    assert first[0]['user_id']==second[0]['user_id']
    assert first[0]['user_id']!=support[0]['user_id']
    assert first[0]['session_id']!=second[0]['session_id']
    monkeypatch.setenv('LYZR_AGENT_ID','changed-agent')
    assert rt.binding(SimpleNamespace(items=first))['target']=='agent-test'
    assert rt.binding(SimpleNamespace(items=[]))=={'runtime':'sdk'}
    assert rt.initial_items('sdk','owner','chat')==[]


def test_client_cannot_supply_runtime_session_or_user_on_question():
    for key in ('runtime','session_id','user_id'):
        with pytest.raises(ValidationError): Question(question='hello',**{key:'override'})
    with pytest.raises(ValidationError): NewConversation(runtime='unknown')


def test_unsupported_controls_rejected():
    with pytest.raises(ValueError): rt.validate_controls('lyzr',Question(question='hello',memory_enabled=True))
    with pytest.raises(ValueError): rt.validate_controls('google',Question(question='hello',guardrail='privacy-builtin'))
    with pytest.raises(ValueError): rt.validate_controls('google',Question(question='hello',memory_write=True))
    rt.validate_controls('google',Question(question='hello',memory_enabled=True,memory_write=True))


def test_no_thoughts_tool_intermediate_or_user_text_in_google_final():
    assert rt.event_answer([
        {'content':{'role':'user','parts':[{'text':'private question'}]}},
        {'content':{'parts':[{'text':'draft'},{'functionCall':{'name':'tool'}}]}},
        {'content':{'parts':[{'text':'thought','thought':True},{'text':'final'}]}},
    ])=='final'
    with pytest.raises(ValueError): rt.event_answer([{'error_code':'blocked'}])
    with pytest.raises(ValueError): rt.event_answer([{'content':{'parts':[{'function_response':{}}]}}])


class DB:
    def add(self,value): self.run=value
    def commit(self): pass


def mock_client(monkeypatch,handler):
    original=httpx.AsyncClient
    monkeypatch.setattr(rt.httpx,'AsyncClient',lambda **kwargs:original(transport=httpx.MockTransport(handler),**kwargs))


def test_lyzr_dispatches_bound_identity_and_session(monkeypatch):
    monkeypatch.setenv('LYZR_API_KEY','synthetic-test-key')
    monkeypatch.setenv('LYZR_AGENT_ID','agent-test')
    import json
    calls=[]
    def handler(request):
        calls.append(json.loads(request.content))
        assert request.headers['x-api-key']=='synthetic-test-key'
        return httpx.Response(200,json={'response':'held'})
    mock_client(monkeypatch,handler)
    conversation=SimpleNamespace(id='chat-a',items=rt.initial_items('lyzr','owner','chat-a'))
    for question in ('status','follow-up'):
        result=asyncio.run(rt.hosted_answer(DB(),conversation,question,Question(question=question)))
        assert result['status']=='completed' and result['answer']=='held'
    assert calls[0]['session_id']==calls[1]['session_id']
    assert calls[0]['user_id']==calls[1]['user_id']==rt.platform_user('owner')


def test_google_session_created_once_and_memory_controls_stay_on_platform(monkeypatch):
    import json
    monkeypatch.setenv('GOOGLE_RUNTIME_RESOURCE',RESOURCE)
    async def headers(): return {'Authorization':'Bearer synthetic'}
    monkeypatch.setattr(rt,'google_headers',headers)
    calls=[]
    def handler(request):
        data=json.loads(request.content); calls.append(data)
        method=data['class_method']
        if method=='async_create_session': return httpx.Response(200,json={'output':{'id':'session-test'}})
        if method=='async_stream_query':
            assert data['input']['session_id']=='session-test'
            return httpx.Response(200,text='data: '+json.dumps({'content':{'role':'model','parts':[{'text':'answer'}]}})+'\n\n')
        if method=='async_get_session': return httpx.Response(200,json={'output':{'id':'session-test','user_id':rt.platform_user('owner')}})
        if method=='async_add_session_to_memory': return httpx.Response(200,json={'output':{'accepted':True}})
        raise AssertionError(method)
    mock_client(monkeypatch,handler)
    conversation=SimpleNamespace(id='chat-a',items=rt.initial_items('google','owner','chat-a'))
    first=asyncio.run(rt.hosted_answer(DB(),conversation,'one',Question(question='one',memory_enabled=True,memory_write=True)))
    second=asyncio.run(rt.hosted_answer(DB(),conversation,'two',Question(question='two',memory_enabled=False)))
    assert first['status']==second['status']=='completed'
    assert 'memory_save_status' not in first['metrics']
    assert sum(c['class_method']=='async_create_session' for c in calls)==1
    queries=[c['input'] for c in calls if c['class_method']=='async_stream_query']
    assert 'state_delta' not in queries[0]
    assert 'state_delta' not in queries[1]
    assert all('state' not in c['input'] for c in calls if c['class_method']=='async_create_session')
    assert not any(c['class_method']=='async_add_session_to_memory' for c in calls)
    assert rt.binding(conversation)['session_id']=='session-test'


def test_platform_authorization_failure_is_not_a_completed_answer(monkeypatch):
    monkeypatch.setenv('LYZR_API_KEY','synthetic')
    monkeypatch.setenv('LYZR_AGENT_ID','agent-test')
    mock_client(monkeypatch,lambda request:httpx.Response(401,json={'detail':'secret must not be returned'}))
    conversation=SimpleNamespace(id='chat-a',items=rt.initial_items('lyzr','owner','chat-a'))
    result=asyncio.run(rt.hosted_answer(DB(),conversation,'hello',Question(question='hello')))
    assert result['status']=='failed'
    assert result['metrics']['platform_http_status']==401
    assert 'secret must not' not in result['answer']


def test_authenticated_api_preserves_runtime_and_rejects_override(monkeypatch):
    from fastapi.testclient import TestClient
    from sqlalchemy import select, delete
    from marketplace import api
    from marketplace.db import Session, User, Conversation
    monkeypatch.setenv('LYZR_API_KEY','synthetic')
    monkeypatch.setenv('LYZR_AGENT_ID','synthetic-agent')
    with Session() as db:
        owner=db.scalar(select(User).where(User.username=='operator'))
        other=db.scalar(select(User).where(User.username=='support'))
        assert owner and other
    api.app.dependency_overrides[api.identity]=lambda:owner
    client=TestClient(api.app)
    created=[]
    try:
        for runtime in ('sdk','lyzr'):
            response=client.post('/api/conversations',json={'runtime':runtime})
            assert response.status_code==200
            created.append(response.json()['id'])
            assert response.json()['runtime']==runtime
        records={c['id']:c for c in client.get('/api/conversations').json()}
        assert records[created[0]]['runtime']=='sdk'
        assert records[created[1]]['runtime']=='lyzr'
        with Session() as db:
            route=rt.binding(db.get(Conversation,created[1]))
            assert route['user_id']==rt.platform_user(owner.id)
        assert client.post(f'/api/conversations/{created[0]}/ask',json={'question':'hello','runtime':'lyzr'}).status_code==422
        api.app.dependency_overrides[api.identity]=lambda:other
        assert client.get(f'/api/conversations/{created[1]}/runs').status_code==404
    finally:
        api.app.dependency_overrides.clear()
        with Session.begin() as db:
            db.execute(delete(Conversation).where(Conversation.id.in_(created)))


def test_lyzr_trace_listing_missing_agent_id_uses_bound_inference_identity(monkeypatch):
    from datetime import datetime, timezone
    monkeypatch.setenv('LYZR_API_KEY','synthetic-test-key')
    source={'contract_version':'1.0','handle':'evidence-ab1234','status':'ok','type':'query','rows':[]}
    def handler(request):
        if request.url.path.endswith('/v3/traces'):
            assert request.url.params['session_id']=='session-test'
            return httpx.Response(200,json=[{'trace_id':'trace-test','agent_id':None,'session_id':'session-test'}])
        return httpx.Response(200,json={'spans':[
            {'SpanName':'inference','SpanAttributes':{'agent_id':'agent-test','session_id':'session-test','output':'paid'}},
            {'SpanName':'mcp_tool_call','SpanAttributes':{'tool_name':'query_business_data','result':source}}]})
    async def check():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            route={'target':'agent-test','session_id':'session-test'}
            result=await rt.lyzr_evidence(client,route,'paid',datetime.now(timezone.utc))
            assert result=={'evidence-ab1234':source}
            route['target']='wrong-agent'
            # A returned trace for another agent must never become this run's evidence.
            async def no_sleep(_): pass
            monkeypatch.setattr(rt.asyncio,'sleep',no_sleep)
            assert await rt.lyzr_evidence(client,route,'paid',datetime.now(timezone.utc))=={}
    asyncio.run(check())


def test_recent_missing_lyzr_evidence_retries_without_model_call(monkeypatch):
    from datetime import datetime,timezone,timedelta
    c=SimpleNamespace(items=[{'type':'marketplace_runtime','runtime':'lyzr','target':'agent-test','session_id':'session-test'}])
    r=SimpleNamespace(status='completed',evidence={},created_at=datetime.now(timezone.utc),answer='paid')
    calls=[]
    async def fetch(client,route,answer,since):
        calls.append(route)
        return {'evidence-ab1234':{'type':'query'}}
    monkeypatch.setattr(rt,'lyzr_evidence',fetch)
    db=DB();asyncio.run(rt.refresh_lyzr_sources(db,c,r));assert r.evidence and len(calls)==1
    asyncio.run(rt.refresh_lyzr_sources(db,c,r));assert len(calls)==1
    r.evidence={};r.created_at-=timedelta(hours=1)
    asyncio.run(rt.refresh_lyzr_sources(db,c,r));assert len(calls)==1
