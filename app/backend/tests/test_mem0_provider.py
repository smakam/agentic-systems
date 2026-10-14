"""No-paid-call tests for identity boundaries and durable extraction behavior."""
import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
import pytest
from sqlalchemy import select, text
from marketplace import mem0_provider as m
from marketplace.db import Session, engine, init_schema, Conversation, User, Run, MemoryConversation, MemoryExtractionJob

SCHEMAS={
    'search_memories':{'type':'object','properties':{'query':{'type':'string'},'filters':{'type':'object'},'top_k':{'type':'integer'}},'required':['query','filters'],'additionalProperties':False},
    'get_memories':{'type':'object','properties':{'filters':{'type':'object'},'page':{'type':'integer'},'page_size':{'type':'integer'}},'additionalProperties':False},
    'add_memory':{'type':'object','properties':{'messages':{'type':'array'},'user_id':{'type':'string'},'metadata':{'type':'object'},'infer':{'type':'boolean'},'app_id':{'type':'string'}},'required':['messages','user_id'],'additionalProperties':False},
    'update_memory':{'type':'object','properties':{'memory_id':{'type':'string'},'text':{'type':'string'},'metadata':{'type':'object'}},'required':['memory_id'],'additionalProperties':False},
    'delete_memory':{'type':'object','properties':{'memory_id':{'type':'string'}},'required':['memory_id'],'additionalProperties':False},
    'get_event_status':{'type':'object','properties':{'event_id':{'type':'string'}},'required':['event_id'],'additionalProperties':False}}

class FakeMCP:
    def __init__(self, rows=None, addition=None):
        self.calls=[];self.rows=rows or [];self.addition=addition or {'results':[]}
    async def list_tools(self):
        return SimpleNamespace(tools=[SimpleNamespace(name=n,input_schema=s) for n,s in SCHEMAS.items()])
    async def call_tool(self,name,args):
        self.calls.append((name,args))
        if name in ('search_memories','get_memories'):data={'results':self.rows}
        elif name=='add_memory':data=self.addition
        elif name=='get_event_status':data={'status':'SUCCEEDED','results':[{'id':'new-memory'}]}
        elif name=='delete_memory':
            self.rows=[x for x in self.rows if x['id']!=args['memory_id']];data={'message':'ok'}
        elif name=='update_memory':
            for x in self.rows:
                if x['id']==args['memory_id']:x['memory']=args['text'];x['metadata']=args['metadata']
            data={'message':'ok'}
        else:data={'message':'ok'}
        return SimpleNamespace(isError=False,structuredContent=data)

def test_search_scope_bound_outside_model_arguments():
    fake=FakeMCP([{'id':'one','memory':'concise answers','user_id':m.namespace('support')}])
    store=m.Mem0Store('support',fake)
    result=asyncio.run(store.search('format'))
    assert fake.calls[0][1]['filters']=={'AND':[{'user_id':m.namespace('support')}]}
    assert result['memories'][0]['version'] is None
    assert result['memories'][0]['kind']=='unclassified'
    assert store.operations[0]['hit_count']==1
    assert m.namespace('support')!=m.namespace('operator')

def test_cross_owner_response_and_id_mutation_rejected():
    fake=FakeMCP([{'id':'other','memory':'private','user_id':m.namespace('operator')}])
    with pytest.raises(m.ProviderError):asyncio.run(m.Mem0Store('support',fake).search('private'))
    fake=FakeMCP([{'id':'owned','memory':'text','user_id':m.namespace('support')}])
    with pytest.raises(m.ProviderError):asyncio.run(m.Mem0Store('support',fake).mutation('other','delete'))
    assert not any(name=='delete_memory' for name,_ in fake.calls)

def test_owned_update_and_delete_do_not_invent_versions():
    fake=FakeMCP([{'id':'owned','memory':'old','user_id':m.namespace('support')}])
    store=m.Mem0Store('support',fake)
    result=asyncio.run(store.mutation('owned','update','new','Preference'))
    assert result['memory']['version'] is None
    assert any(name=='update_memory' and args['memory_id']=='owned' for name,args in fake.calls)
    asyncio.run(store.mutation('owned','delete'))
    assert any(name=='delete_memory' for name,_ in fake.calls)

def test_model_tool_is_search_only_and_failure_has_no_fallback(monkeypatch):
    from agents import function_tool
    context=m.Mem0ReadContext('support')
    tool=function_tool(context.tool())
    assert tool.name=='search_memories'
    assert set(tool.params_json_schema['properties'])=={'query'}
    @asynccontextmanager
    async def broken():
        raise RuntimeError('private provider details')
        yield
    monkeypatch.setattr(m,'connect',broken)
    result=asyncio.run(context.search('preference'))
    assert result['status']=='error' and 'private' not in result['message']
    assert context.operations[-1]['status']=='failed'

def test_event_status_and_unknown_outcome_are_distinct():
    assert m.event_outcome({'event_id':'event','status':'PENDING'})[1]=='pending'
    assert m.event_outcome({'status':'SUCCEEDED','results':[]})[1]=='complete'
    assert m.event_outcome({'message':'accepted'})[1] is None
    assert m.event_outcome({'event_id':'event','status':'FAILED'})[1]=='failed'

@pytest.fixture
def isolated_db(monkeypatch):
    # Never reset the active shared Test workspace or the main marketplace.
    if engine.url.database!='market_mem0_verify':pytest.skip('Dedicated market_mem0_verify database required')
    init_schema()
    with engine.begin() as conn:
        conn.execute(text('TRUNCATE public.memory_extraction_jobs, public.memory_conversation_settings, public.runs, public.conversations, public.users CASCADE'))
    with Session.begin() as db:
        for owner in ('support','operator'):
            db.add(User(id=owner,username=owner,password_hash='unused',role=owner))
        db.flush()
        db.add(Conversation(id='mem0-chat',owner_id='support',title='Memory test',items=[]))
        db.flush()
        db.add(MemoryConversation(conversation_id='mem0-chat',provider='mem0'))
        db.add(Run(id='r-one',conversation_id='mem0-chat',revision=1,question='I prefer concise tables',
            answer='Understood',status='completed',evidence={},metrics={'memory_provider':'mem0','memory_enabled':False},
            created_at=datetime.now(timezone.utc)-timedelta(minutes=30)))
    monkeypatch.setattr(m,'enabled',lambda:True)

def test_enqueue_duplicate_and_wrong_owner(isolated_db):
    with Session.begin() as db:
        first=m.enqueue(db,'support','mem0-chat')
        second=m.enqueue(db,'support','mem0-chat')
        assert first==second
        assert len(list(db.scalars(select(MemoryExtractionJob))))==1
        with pytest.raises(m.ProviderError):m.enqueue(db,'operator','mem0-chat')
    with Session() as db:
        job=m.latest_job(db,'mem0-chat')
        assert m.messages_for(db,job)==[{'role':'user','content':'I prefer concise tables'},{'role':'assistant','content':'Understood'}]

def test_background_pending_survives_restart_without_second_add(isolated_db,monkeypatch):
    fake=FakeMCP(addition={'event_id':'provider-event','status':'PENDING'})
    @asynccontextmanager
    async def connected():yield fake
    monkeypatch.setattr(m,'connect',connected)
    async def extraction(owner,messages,cid):
        fake.calls.append(('add_memory',m.extraction_payload(owner,messages,cid)))
        return fake.addition
    monkeypatch.setattr(m,'extract_conversation',extraction)
    with Session.begin() as db:m.enqueue(db,'support','mem0-chat')
    with Session() as db:jid=m.latest_job(db,'mem0-chat').id
    asyncio.run(m.process_job(jid))
    m.recover_interrupted()
    asyncio.run(m.process_job(jid))
    assert [name for name,_ in fake.calls].count('add_memory')==1
    assert [name for name,_ in fake.calls].count('get_event_status')==1
    with Session() as db:assert db.get(MemoryExtractionJob,jid).status=='complete'

def test_uncertain_write_is_not_resubmitted_after_restart(isolated_db,monkeypatch):
    with Session.begin() as db:
        m.enqueue(db,'support','mem0-chat')
        job=m.latest_job(db,'mem0-chat');job.status='processing';jid=job.id
    m.recover_interrupted()
    fake=FakeMCP()
    @asynccontextmanager
    async def connected():yield fake
    monkeypatch.setattr(m,'connect',connected)
    asyncio.run(m.process_job(jid))
    assert fake.calls==[]
    with Session() as db:assert db.get(MemoryExtractionJob,jid).status=='failed'

def test_running_question_cannot_finalize(isolated_db):
    with Session.begin() as db:
        db.get(Run,'r-one').status='running'
        with pytest.raises(m.ProviderError):m.enqueue(db,'support','mem0-chat')

def test_idle_end_queues_once_and_uses_answer_completion(isolated_db):
    m.queue_idle();m.queue_idle()
    with Session() as db:assert len(list(db.scalars(select(MemoryExtractionJob))))==1

def test_recovery_does_not_change_another_live_worker_claim(isolated_db):
    with Session.begin() as db:
        m.enqueue(db,'support','mem0-chat');job=m.latest_job(db,'mem0-chat');job.status='processing';jid=job.id
    with engine.connect() as lock:
        lock.execute(text('SELECT pg_advisory_lock(hashtext(:key))'),{'key':jid})
        m.recover_interrupted()
        with Session() as db:assert db.get(MemoryExtractionJob,jid).status=='processing'
        lock.execute(text('SELECT pg_advisory_unlock(hashtext(:key))'),{'key':jid})

def test_api_provider_binding_ownership_and_validation(isolated_db,monkeypatch):
    from fastapi.testclient import TestClient
    from marketplace import api
    from marketplace import agent
    user=SimpleNamespace(id='support',role='support')
    api.app.dependency_overrides[api.identity]=lambda:user
    monkeypatch.setenv('INITIALIZE_ON_STARTUP','false')
    async def idle_worker(): await asyncio.sleep(3600)
    monkeypatch.setattr(m,'worker',idle_worker)
    monkeypatch.setattr(api,'runtime_configured',lambda runtime:True)
    async def answer(*args,**kwargs):return {'status':'completed','metrics':{'memory_provider':kwargs['memory_provider']}}
    monkeypatch.setattr(agent,'answer',answer)
    try:
        with TestClient(api.app) as client:
            response=client.post('/api/conversations',json={'runtime':'sdk','memory_provider':'mem0'})
            assert response.status_code==200
            cid=response.json()['id']
            assert response.json()['memory_provider']=='mem0'
            assert client.post('/api/conversations/'+cid+'/ask',json={'question':'hello','memory_provider':'internal'}).status_code==400
            assert client.post('/api/conversations/'+cid+'/ask',json={'question':'hello','memory_provider':'mem0','memory_write':True}).status_code==400
            got=client.post('/api/conversations/'+cid+'/ask',json={'question':'hello','memory_provider':'mem0','memory_enabled':False})
            assert got.status_code==200 and got.json()['metrics']['memory_provider']=='mem0'
            assert client.post('/api/conversations/'+cid+'/memory/finalize').json()['status']=='noop'
            assert client.get('/api/conversations').json()[-1]['memory_provider']=='mem0'
            @asynccontextmanager
            async def wrapped():
                try:yield FakeMCP()
                except m.ProviderError as exc:raise ExceptionGroup('MCP transport',[exc]) from None
            monkeypatch.setattr(m,'connect',wrapped)
            assert client.patch('/api/memories/foreign',params={'provider':'mem0'},json={'title':'No','content':'No'}).status_code==404
            assert client.delete('/api/memories/foreign',params={'provider':'mem0'}).status_code==404
            user.id='operator'
            assert client.get('/api/conversations/'+cid+'/memory/status').status_code==404
    finally:api.app.dependency_overrides.clear()


def test_extraction_retains_full_context_and_binds_policy_and_scope():
    messages=[{'role':'user','content':'I prefer brief tables'},
              {'role':'assistant','content':'I will keep using tables'}]
    payload=m.extraction_payload('support',messages,'chat-fixture')
    assert payload['messages']==messages
    assert payload['user_id']==m.namespace('support')
    assert payload['metadata']['owner_scope']==payload['user_id']
    assert payload['metadata']['conversation_id']=='chat-fixture'
    assert payload['metadata']['retention_policy']==m.RETENTION_POLICY_VERSION
    assert payload['infer'] is True
    assert payload['custom_instructions']==m.RETENTION_POLICY
    assert 'assistant acknowledgements' in payload['custom_instructions']
    assert 'current\norder, payment, shipment, payout and refund states' in payload['custom_instructions']


def test_extraction_uses_request_specific_rest_policy_without_project_write(monkeypatch):
    import httpx2
    calls=[]
    class FakeHTTP:
        def __init__(self,**kwargs):self.options=kwargs
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,url,**kwargs):
            calls.append((url,kwargs,self.options))
            return SimpleNamespace(status_code=200,json=lambda:{'event_id':'policy-event','status':'PENDING'})
    monkeypatch.setattr(httpx2,'AsyncClient',FakeHTTP)
    monkeypatch.setattr(m,'enabled',lambda:True)
    monkeypatch.setenv('MEM0_API_KEY','synthetic-test-key')
    messages=[{'role':'user','content':'I prefer compact tables'},{'role':'assistant','content':'context'}]
    result=asyncio.run(m.extract_conversation('support',messages,'chat-fixture'))
    assert result['event_id']=='policy-event' and len(calls)==1
    url,args,options=calls[0]
    assert url=='https://api.mem0.ai/v3/memories/add/'
    assert options['headers']['Authorization']=='Token synthetic-test-key'
    assert options['follow_redirects'] is False
    assert args['json']==m.extraction_payload('support',messages,'chat-fixture')


def test_extraction_failure_is_sanitized(monkeypatch):
    import httpx2
    class FakeHTTP:
        def __init__(self,**kwargs):pass
        async def __aenter__(self):return self
        async def __aexit__(self,*args):pass
        async def post(self,*args,**kwargs):return SimpleNamespace(status_code=403)
    monkeypatch.setattr(httpx2,'AsyncClient',FakeHTTP)
    monkeypatch.setattr(m,'enabled',lambda:True)
    monkeypatch.setenv('MEM0_API_KEY','synthetic-test-key')
    with pytest.raises(m.ProviderError,match='^Mem0 rejected extraction$'):
        asyncio.run(m.extract_conversation('support',[{'role':'user','content':'I prefer tables'}],'chat-fixture'))


@pytest.mark.parametrize('question',[
    'What is the payout status of order-2?',
    'What is my preference for payout explanations?',
    'I would like to know the current payout status of order-2.',
    'I like to know the current payout status before explanations.',
    'For this answer use a table with Finding, Evidence and Next action.',
    'What do you remember about my preferences?',
])
def test_business_recall_and_temporary_requests_cannot_submit(question,monkeypatch):
    import httpx2
    def forbidden_http(**kwargs):raise AssertionError('Ineligible messages must never reach the provider')
    monkeypatch.setattr(httpx2,'AsyncClient',forbidden_http)
    monkeypatch.setattr(m,'enabled',lambda:True)
    messages=[{'role':'user','content':question},
              {'role':'assistant','content':'I will remember a table preference with Finding, Evidence and Next action.'}]
    assert not m.extraction_eligibility(messages)['eligible']
    response=asyncio.run(m.extract_conversation('support',messages,'business-only'))
    assert response['application_skipped'] and response['results']==[]

@pytest.mark.parametrize('question',[
    'I prefer payout explanations in a compact table with Finding, Evidence and Next action.',
    'I like payout explanations in a compact table with Finding, Evidence and Next action.',
    'My payout explanation preference is a compact table.',
    'Use this checklist for all my investigations: check records and policy.',
    'For all my investigations follow this checklist: verify shipment and policy.',
    'Remember this historical investigation checkpoint so I can resume later: eligibility was unresolved; next check fresh delivery evidence.',
])
def test_durable_user_intent_authorizes_full_context(question):
    messages=[{'role':'user','content':question},{'role':'assistant','content':'Context remains available.'}]
    gate=m.extraction_eligibility(messages)
    assert gate['eligible'] and gate['source_quotes']==[question]
    assert m.extraction_payload('support',messages,'eligible')['messages']==messages
    assert m.extraction_payload('support',messages,'eligible')['metadata']['eligibility_gate']==m.ELIGIBILITY_GATE_VERSION

def test_skipped_job_is_durable_and_not_retried(isolated_db,monkeypatch):
    with Session.begin() as db:
        db.get(Run,'r-one').question='What is the payout status of order-2?'
        db.get(Run,'r-one').answer='The current status is held.'
        m.enqueue(db,'support','mem0-chat')
        jid=m.latest_job(db,'mem0-chat').id
    import httpx2
    monkeypatch.setattr(httpx2,'AsyncClient',lambda **kwargs: (_ for _ in ()).throw(AssertionError('No provider submission')))
    asyncio.run(m.process_job(jid));asyncio.run(m.process_job(jid))
    with Session() as db:
        job=db.get(MemoryExtractionJob,jid)
        assert job.status=='noop' and job.event_id is None and job.result_ids==[]
        assert m.job_record(job,'mem0-chat')['memory_count']==0
        assert m.enqueue(db,'support','mem0-chat')['status']=='noop'


def test_both_enabled_providers_share_preference_first_rule_and_authority():
    from marketplace.memory import MEMORY_INSTRUCTIONS,MEMORY_RETRIEVAL_INSTRUCTIONS
    assert MEMORY_INSTRUCTIONS.startswith(MEMORY_RETRIEVAL_INSTRUCTIONS)
    assert m.MEM0_INSTRUCTIONS.startswith(MEMORY_RETRIEVAL_INSTRUCTIONS)
    assert 'EVERY business question' in MEMORY_RETRIEVAL_INSTRUCTIONS
    assert 'instead of the default Field/Details layout' in MEMORY_RETRIEVAL_INSTRUCTIONS
    assert 'CURRENT user asks for a different' in MEMORY_RETRIEVAL_INSTRUCTIONS
    assert 'collect current business and' in MEMORY_RETRIEVAL_INSTRUCTIONS
    assert 'citation requirements' in MEMORY_RETRIEVAL_INSTRUCTIONS
