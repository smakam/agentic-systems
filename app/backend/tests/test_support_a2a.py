"""A2A 1.0 protocol, browser authentication, task ownership and shared workflow."""
import asyncio
import os
from datetime import datetime, timezone
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, text

from marketplace import agent, api, index
from marketplace.db import Base, Conversation, Run, Session, User, engine, init_schema
from marketplace.seed import seed
from marketplace.support_a2a import PREFIX, SupportConversation, SupportTask

assert engine.url.database == 'market_test', 'Use the isolated market_test database'


@pytest.fixture(autouse=True)
def database(monkeypatch):
    init_schema()
    with engine.begin() as c:
        names=','.join('public.'+x.name for x in reversed(Base.metadata.sorted_tables))
        c.execute(text(f'TRUNCATE {names} CASCADE'))
    with Session.begin() as db: seed(db)
    async def noop(): pass
    monkeypatch.setattr(index,'index',noop)
    monkeypatch.delenv('HOSTING_LAB',raising=False)
    monkeypatch.delenv('CH12_HOSTING_LAB',raising=False)
    monkeypatch.delenv('EVAL_GATEWAY_KEY',raising=False)
    monkeypatch.delenv('COURSE_GATEWAY_DEMO',raising=False)
    monkeypatch.delenv('DELIVERY_A2A_URL',raising=False)
    monkeypatch.delenv('DELIVERY_READ_TOKEN',raising=False)
    return None


def signed_in(client, name='support'):
    result=client.post('/api/login',json={'username':name,'password':'demo-marketplace'})
    assert result.status_code==200
    client.headers['x-csrf-token']=result.json()['csrf']
    client.headers['A2A-Version']='1.0'
    return result.json()


def conversation(client, mode='a2a_support'):
    r=client.post('/api/conversations',json={'mode':mode})
    assert r.status_code==200, r.text
    return r.json()


def send(client, conv, question='What is the status of order-2?', **extra):
    message={'messageId':str(uuid4()),'role':'ROLE_USER','contextId':conv['a2a_context_id'],'parts':[{'text':question}]}
    message.update(extra.pop('message',{}))
    params={'message':message,'metadata':{'conversation_id':conv['id'],'question_options':extra.pop('options',{})},**extra}
    return client.post(PREFIX,json={'jsonrpc':'2.0','id':str(uuid4()),'method':'SendMessage','params':params})


def fake_answer(monkeypatch, status='completed'):
    calls=[]
    async def run(cid, question, **kwargs):
        history=await agent.DatabaseSession(cid).get_items()
        calls.append({'conversation_id':cid,'question':question,'history':history,'kwargs':kwargs})
        await agent.DatabaseSession(cid).add_items([{'role':'user','content':question},{'role':'assistant','content':'Recorded answer'}])
        rid='run-'+str(uuid4())
        result={'id':rid,'status':status,'answer':'Recorded answer','revision':1,'evidence':{},'metrics':{}}
        with Session.begin() as db:
            db.add(Run(id=rid,conversation_id=cid,status=status,question=question,answer='Recorded answer',revision=1,evidence={},metrics={},created_at=datetime.now(timezone.utc)))
        return result
    monkeypatch.setattr(agent,'answer',run)
    return calls


def test_card_requires_session_and_support_role_and_reports_real_interfaces():
    with TestClient(api.app) as c:
        assert c.get(PREFIX+'/.well-known/agent-card.json').status_code==401
        signed_in(c,'buyer')
        assert c.get(PREFIX+'/.well-known/agent-card.json').status_code==403
        signed_in(c)
        r=c.get(PREFIX+'/.well-known/agent-card.json')
        assert r.status_code==200
        card=r.json()
        assert card['name']=='Marketplace Support'
        assert card['supportedInterfaces']==[{'url':'http://testserver'+PREFIX,'protocolBinding':'JSONRPC','protocolVersion':'1.0','tenant':''}]
        assert card['capabilities']['streaming'] is False
        assert card['capabilities']['pushNotifications'] is False
        assert card['securitySchemes']['marketplaceSession']['apiKeySecurityScheme']['location']=='cookie'
        assert card['securitySchemes']['csrf']['apiKeySecurityScheme']['name']=='X-CSRF-Token'
        assert 'market_session' in r.text and 'password_hash' not in r.text


def test_each_followup_gets_new_completed_task_with_owned_context_and_stored_history(monkeypatch):
    calls=fake_answer(monkeypatch)
    with TestClient(api.app) as c:
        signed_in(c)
        conv=conversation(c)
        first=send(c,conv)
        assert first.status_code==200, first.text
        assert 'error' not in first.json(), first.text
        task=first.json()['result']['task']
        assert task['status']['state']=='TASK_STATE_COMPLETED'
        assert task['contextId']==conv['a2a_context_id']
        second=send(c,conv,'And the shipment?').json()['result']['task']
        assert second['id']!=task['id']
        assert second['contextId']==task['contextId']
        assert len(calls)==2 and calls[0]['history']==[]
        assert calls[1]['history'][0]['content']=='What is the status of order-2?'
        assert all(x['conversation_id']==conv['id'] for x in calls)
        history=c.get('/api/conversations/'+conv['id']+'/runs').json()
        assert len(history)==2
        assert history[0]['metrics']['a2a']['task_id']==task['id']
        get=c.post(PREFIX,json={'jsonrpc':'2.0','id':1,'method':'GetTask','params':{'id':task['id']}})
        assert get.json()['result']['status']['state']=='TASK_STATE_COMPLETED'
        reopen=send(c,conv,message={'taskId':task['id']}).json()
        assert reopen['error']['code']==-32602
        assert len(calls)==2
        with Session() as db:
            assert db.scalar(select(SupportTask).where(SupportTask.id==task['id'])) is not None
        assert c.get('/api/conversations').json()[0]['a2a_context_id']==conv['a2a_context_id']


def test_a2a_entrance_enforces_csrf_role_context_and_task_owner(monkeypatch):
    calls=fake_answer(monkeypatch)
    with TestClient(api.app) as c:
        signed_in(c)
        conv=conversation(c)
        original=c.headers.pop('x-csrf-token')
        assert send(c,conv).status_code==403
        c.headers['x-csrf-token']=original
        task=send(c,conv).json()['result']['task']
        signed_in(c,'operator')
        assert 'error' in send(c,conv).json()
        foreign=c.post(PREFIX,json={'jsonrpc':'2.0','id':1,'method':'GetTask','params':{'id':task['id']}}).json()
        assert 'error' in foreign and 'result' not in foreign
        own=conversation(c)
        spoof=send(c,own,metadata={'conversation_id':conv['id']}).json()
        assert 'error' in spoof
        signed_in(c,'buyer')
        assert send(c,conv).status_code==403
        assert len(calls)==1


def test_both_modes_share_validation_and_api_cannot_change_transport(monkeypatch):
    calls=fake_answer(monkeypatch)
    with TestClient(api.app) as c:
        signed_in(c)
        a2a=conversation(c,'a2a_delivery')
        standard=conversation(c,'standard')
        assert standard['a2a_context_id'] is None
        assert c.post('/api/conversations/'+a2a['id']+'/ask',json={'question':'q'}).status_code==400
        assert 'error' in send(c,{**standard,'a2a_context_id':a2a['a2a_context_id']}).json()
        invalid=send(c,a2a,options={'routing_policy':'not-a-policy'}).json()['result']['task']
        assert invalid['status']['state']=='TASK_STATE_FAILED'
        assert not calls
        valid=send(c,a2a).json()['result']['task']
        assert valid['status']['state']=='TASK_STATE_COMPLETED'
        assert calls[0]['kwargs']['evaluation_config']['delivery_enabled'] is True
        standard_r=c.post('/api/conversations/'+standard['id']+'/ask',json={'question':'same agent'})
        assert standard_r.status_code==200
        assert len(calls)==2
        assert not (calls[1]['kwargs'].get('evaluation_config') or {}).get('delivery_enabled')


def test_failures_are_failed_tasks_and_unsupported_methods_do_not_run_agent(monkeypatch):
    calls=fake_answer(monkeypatch,status='failed')
    with TestClient(api.app) as c:
        signed_in(c)
        conv=conversation(c)
        task=send(c,conv).json()['result']['task']
        assert task['status']['state']=='TASK_STATE_FAILED'
        for method in ('SendStreamingMessage','CancelTask','ListTasks','CreateTaskPushNotificationConfig'):
            r=c.post(PREFIX,json={'jsonrpc':'2.0','id':1,'method':method,'params':{}}).json()
            assert r['error']['code']==-32601
        assert len(calls)==1


def test_invalid_questions_and_nontext_parts_do_not_start_a_run(monkeypatch):
    calls=fake_answer(monkeypatch)
    with TestClient(api.app) as c:
        signed_in(c)
        conv=conversation(c)
        for q in ('','x'*4001): assert 'error' in send(c,conv,q).json()
        assert 'error' in send(c,conv,message={'parts':[{'data':{'command':'deliver'}}]}).json()
        assert 'error' in send(c,conv,configuration={'returnImmediately':True}).json()
        assert not calls


def test_completed_message_retry_replays_same_task_without_new_model_run(monkeypatch):
    calls=fake_answer(monkeypatch)
    with TestClient(api.app) as c:
        signed_in(c)
        conv=conversation(c)
        message_id=str(uuid4())
        first=send(c,conv,message={'messageId':message_id}).json()['result']['task']
        again=send(c,conv,message={'messageId':message_id}).json()['result']['task']
        assert first==again
        assert len(calls)==1
        c.headers.pop('A2A-Version')
        missing_version=send(c,conv,message={'messageId':message_id}).json()
        assert missing_version['error']['code']==-32009
        c.headers['A2A-Version']='0.3'
        wrong_version=send(c,conv,message={'messageId':message_id}).json()
        assert wrong_version['error']['code']==-32009
        c.headers['A2A-Version']='1.0'
        assert 'error' in send(c,conv,'Different content',message={'messageId':message_id}).json()
        assert len(calls)==1


def test_aliases_cannot_enable_async_tasks_or_change_context(monkeypatch):
    calls=fake_answer(monkeypatch)
    with TestClient(api.app) as c:
        signed_in(c)
        conv=conversation(c)
        assert 'error' in send(c,conv,configuration={'return_immediately':True}).json()
        assert 'error' in send(c,conv,configuration={'task_push_notification_config':{'url':'https://example.org'}}).json()
        assert 'error' in send(c,conv,message={'context_id':'forged'}).json()
        assert 'error' in send(c,conv,message={'messageId':''}).json()
        assert not calls


def test_conversation_lock_rejects_overlap_before_second_run(monkeypatch):
    from concurrent.futures import ThreadPoolExecutor
    import threading
    started=threading.Event()
    release=threading.Event()
    calls=[]
    async def slow_answer(cid, question, **kwargs):
        calls.append(question)
        started.set()
        await asyncio.to_thread(release.wait,5)
        return {'id':'no-persisted-run','status':'completed','answer':'one result','revision':1,'metrics':{},'evidence':{}}
    monkeypatch.setattr(agent,'answer',slow_answer)
    with TestClient(api.app) as c:
        signed_in(c)
        conv=conversation(c)
        with ThreadPoolExecutor(max_workers=2) as pool:
            first=pool.submit(send,c,conv)
            try:
                assert started.wait(3)
                second=send(c,conv,'overlapping question').json()['result']['task']
                assert second['status']['state']=='TASK_STATE_FAILED'
                assert 'already has a running question' in second['artifacts'][0]['parts'][0]['text']
                assert calls==['What is the status of order-2?']
            finally: release.set()
            assert first.result().json()['result']['task']['status']['state']=='TASK_STATE_COMPLETED'


def test_workspace_options_persist_across_accounts_and_are_test_only(monkeypatch):
    with TestClient(api.app) as c:
        signed_in(c)
        assert c.get('/api/a2a/workspace').json()=={'enabled':True,'mode':'standard','fixture':'normal'}
        chosen={'mode':'a2a_delivery','fixture':'exception'}
        assert c.post('/api/a2a/workspace',json=chosen).status_code==200
        signed_in(c,'buyer')
        assert c.post('/api/a2a/workspace',json={'mode':'standard'}).status_code==403
        signed_in(c,'operator')
        assert c.get('/api/a2a/workspace').json()=={'enabled':True,**chosen}
        assert c.post('/api/a2a/workspace',json={'mode':'invalid'}).status_code==422
        monkeypatch.setattr(api,'is_test',lambda:False)
        assert c.get('/api/a2a/workspace').json()['enabled'] is False
        assert c.post('/api/a2a/workspace',json=chosen).status_code==403


def test_remote_configuration_does_not_enable_delivery_in_marketplace_modes(monkeypatch):
    calls=fake_answer(monkeypatch)
    monkeypatch.setenv('DELIVERY_A2A_URL','http://configured.example')
    monkeypatch.setenv('DELIVERY_READ_TOKEN','private-test-token')
    with TestClient(api.app) as c:
        signed_in(c)
        for mode in ('standard','a2a_support','a2a_delivery'):
            conv=conversation(c,mode)
            if mode=='standard':
                assert c.post('/api/conversations/'+conv['id']+'/ask',json={'question':'track delivery'}).status_code==200
            else: assert send(c,conv,'track delivery').json()['result']['task']['status']['state']=='TASK_STATE_COMPLETED'
        assert [(call['kwargs'].get('evaluation_config') or {}).get('delivery_enabled',False) for call in calls]==[False,False,True]


def test_reset_restores_workspace_defaults_without_erasing_shipment_intents(monkeypatch):
    from marketplace.db import A2AWorkspace
    monkeypatch.setattr(api,'fixture_status',lambda:{'variant':'clean'})
    with TestClient(api.app) as c:
        signed_in(c)
        assert c.post('/api/a2a/workspace',json={'mode':'a2a_delivery','fixture':'exception'}).status_code==200
        assert c.post('/api/workspace-options/reset',json={}).status_code==200
        assert c.get('/api/a2a/workspace').json()=={'enabled':True,'mode':'standard','fixture':'normal'}
        with Session() as db:assert db.get(A2AWorkspace,1).mode=='standard'
