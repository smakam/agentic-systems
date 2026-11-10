"""Real A2A transport and durable simulator tests; no provider credentials needed."""
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor
from types import SimpleNamespace
import httpx
import pytest
from fastapi.testclient import TestClient
from agents import RunContextWrapper
from agents.tool_context import ToolContext
from marketplace import delivery_investigator
from marketplace.delivery_client import delivery_request, DeliveryUnavailable
from marketplace.delivery_service import create_app
from marketplace.delivery_store import DeliveryStore, DeliveryRecordError

NOW = '2026-11-10T12:00:00+00:00'
READ = 'read-only-test-credential'
WRITE = 'write-only-test-credential'


@pytest.fixture
def service(tmp_path,monkeypatch):
    monkeypatch.setenv('DELIVERY_READ_TOKEN',READ)
    monkeypatch.setenv('DELIVERY_WRITE_TOKEN',WRITE)
    monkeypatch.setenv('DELIVERY_A2A_URL','http://delivery.test')
    store=DeliveryStore(tmp_path/'delivery.sqlite3')
    return create_app(store),store


def rpc(client,operation,data,token=WRITE,**message_extra):
    return client.post('/',headers={'Authorization':'Bearer '+token,'A2A-Version':'1.0'},json={
        'jsonrpc':'2.0','id':'request-1','method':'SendMessage','params':{
            'message':{'messageId':'message-1','role':'ROLE_USER','parts':[{'data':{'operation':operation,**data}}],**message_extra},
            'configuration':{'returnImmediately':False}}})


def task(response):
    assert response.status_code==200,response.text
    return response.json()['result']['task']


def result(response):
    value=task(response)
    assert value['status']['state']=='TASK_STATE_COMPLETED',value
    return value['artifacts'][0]['parts'][0]['data']


def test_real_a2a_card_and_repeated_booking_and_delivery(service):
    app,store=service
    with TestClient(app) as client:
        card=client.get('/.well-known/agent-card.json').json()
        assert card['supportedInterfaces'][0]['protocolVersion']=='1.0'
        assert card['capabilities']['streaming'] is False
        assert card['securitySchemes']['serviceBearer']['httpAuthSecurityScheme']['scheme']=='bearer'
        booking={'shipment_id':'shipment-one','fixture':'normal','clock':NOW}
        first=rpc(client,'book',booking);second=rpc(client,'book',booking)
        one,two=result(first),result(second)
        assert one['reference']==two['reference']
        assert one['on_schedule'] and not one['overdue']
        assert task(first)['id']!=task(second)['id']
        # Task retrieval is owner scoped to the read/write service principal.
        tid=task(first)['id']
        get={'jsonrpc':'2.0','id':'get','method':'GetTask','params':{'id':tid}}
        headers={'Authorization':'Bearer '+WRITE,'A2A-Version':'1.0'}
        assert client.post('/',headers=headers,json=get).json()['result']['id']==tid
        headers['Authorization']='Bearer '+READ
        assert 'error' in client.post('/',headers=headers,json=get).json()
        delivered=result(rpc(client,'deliver',{'reference':one['reference'],'clock':NOW}))
        assert delivered['status']=='delivered'
        rpc(client,'deliver',{'reference':one['reference'],'clock':NOW})
        assert [e['event'] for e in store.issue(one['reference'],NOW)['tracking_events']].count('delivered')==1


def test_post_dispatch_fixture_control_is_write_only_repeat_safe_and_not_for_delivered(service):
    app,store=service
    with TestClient(app) as client:
        row=result(rpc(client,'book',{'shipment_id':'fixture-control','fixture':'normal','clock':NOW}))
        change={'reference':row['reference'],'fixture':'exception','clock':NOW,'operation_key':'fixture-to-exception'}
        assert rpc(client,'set_fixture',change,token=READ).status_code==403
        assert result(rpc(client,'set_fixture',change))['status']=='exception'
        result(rpc(client,'set_fixture',change))
        assert len(store.issue(row['reference'],NOW)['tracking_events'])==3
        assert 'scanner failed' in store.issue(row['reference'],NOW)['reason']
        assert result(rpc(client,'set_fixture',{**change,'fixture':'normal','operation_key':'fixture-back-normal'}))['on_schedule']
        # An orphaned old command replay must not undo a later scenario update.
        assert task(rpc(client,'set_fixture',change))['status']['state']=='TASK_STATE_FAILED'
        assert store.status(row['reference'],NOW)['status']=='in_transit'
        result(rpc(client,'deliver',{'reference':row['reference'],'clock':NOW}))
        failed=task(rpc(client,'set_fixture',change))
        assert failed['status']['state']=='TASK_STATE_FAILED'
        assert store.status(row['reference'],NOW)['status']=='delivered'


@pytest.mark.parametrize('field,value',[
    ('reference',''),('marketplace_shipment_id','other-shipment'),('source','unverified'),
    ('simulated',False),('status','delivered'),('fixture','invalid'),
    ('simulation_as_of','2026-11-10T12:01:00+00:00'),('observed_at','2026-11-10T12:00:00'),
    ('expected_delivery_at','not-a-date'),('overdue',True),('on_schedule',False),
    ('delivered_at',NOW),
])
def test_shipping_receipt_validation_rejects_mismatched_identity_state_and_clock(service,field,value):
    from datetime import datetime
    from marketplace.delivery_shipping import _validate_receipt
    from marketplace.business import BusinessError
    _,store=service
    receipt=store.book('validated-shipment','normal',NOW)
    receipt[field]=value
    with pytest.raises(BusinessError):
        _validate_receipt(receipt,'validated-shipment',datetime.fromisoformat(NOW),('in_transit','exception'),fixture='normal')


def test_write_authority_and_protocol_bounds(service):
    app,store=service
    with TestClient(app) as client:
        booking={'shipment_id':'ship-unauthorized','fixture':'normal','clock':NOW}
        assert rpc(client,'book',booking,token=READ).status_code==403
        assert rpc(client,'book',booking,token='not-a-key').status_code==401
        with pytest.raises(DeliveryRecordError):store.status('missing',NOW)
        resumed=rpc(client,'book',booking,taskId='completed-task')
        assert resumed.json()['error']['code']==-32602
        bad=rpc(client,'book',{**booking,'fixture':'invalid'})
        assert task(bad)['status']['state']=='TASK_STATE_FAILED'
        assert client.post('/',headers={'Authorization':'Bearer '+WRITE},json={'jsonrpc':'2.0','id':'x','method':'SendStreamingMessage'}).json()['error']['code']==-32601
        assert client.post('/',headers={'Authorization':'Bearer '+WRITE},content='x'*20001).status_code==413


def test_service_not_open_when_credentials_missing_or_equal(service,monkeypatch):
    app,_=service
    monkeypatch.setenv('DELIVERY_WRITE_TOKEN',READ)
    with TestClient(app) as client:
        assert rpc(client,'book',{'shipment_id':'s','fixture':'normal','clock':NOW},token=READ).status_code==503
        assert client.get('/health').status_code==200


def test_sqlite_state_survives_restart_and_concurrent_booking(tmp_path):
    path=tmp_path/'durable.sqlite3'
    store=DeliveryStore(path)
    def book(_):return store.book('same-shipment','exception',NOW)
    with ThreadPoolExecutor(max_workers=4) as pool: rows=list(pool.map(book,range(4)))
    assert len({r['reference'] for r in rows})==1
    restarted=DeliveryStore(path)
    reference=rows[0]['reference']
    assert restarted.status(reference,NOW)['status']=='exception'
    assert 'scanner failed' in restarted.issue(reference,NOW)['reason']
    with pytest.raises(DeliveryRecordError):restarted.book('same-shipment','normal',NOW)
    assert len(restarted.issue(reference,NOW)['tracking_events'])==2
    normal=restarted.book('normal-shipment','normal',NOW)
    late=restarted.status(normal['reference'],'2026-11-13T12:00:00+00:00')
    assert late['overdue'] and not late['on_schedule']


def test_client_real_protocol_and_failure_boundary(service):
    app,_=service
    async def run():
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) as client:
            record=await delivery_request('book',{'shipment_id':'client-shipment','fixture':'normal','clock':NOW},write=True,http_client=client)
            assert record['status']=='in_transit'
            with pytest.raises(DeliveryUnavailable):
                await delivery_request('book',{'shipment_id':'denied','fixture':'normal','clock':NOW},http_client=client)
        async def broken(request):raise httpx.ConnectError('private-internal-url-with-secret',request=request)
        async with httpx.AsyncClient(transport=httpx.MockTransport(broken)) as client:
            with pytest.raises(DeliveryUnavailable) as error:
                await delivery_request('investigate',{},http_client=client)
            assert 'secret' not in str(error.value)
    asyncio.run(run())


def controlled_model(monkeypatch, *, skip_details=False, skip_status=False):
    """Exercise actual SDK tool wrappers; only the model decision is controlled."""
    class FakeApi:
        async def close(self):pass
    monkeypatch.setattr(delivery_investigator,'client',lambda:FakeApi())
    async def run(agent,question,**kwargs):
        tools={t.name:t for t in agent.tools}
        context=RunContextWrapper(context=None)
        async def call(name):
            tool_context=ToolContext.from_agent_context(context,'test-'+name,tool_name=name,tool_arguments='{}')
            return await tools[name].on_invoke_tool(tool_context,'{}')
        if skip_status:return SimpleNamespace(final_output='Unsupported guess')
        status=await call('get_current_shipment_status')
        if isinstance(status,str):status=json.loads(status)
        if (status['status']=='exception' or status['overdue']) and not skip_details:
            await call('get_delivery_problem_details')
        return SimpleNamespace(final_output='Controlled model findings from recorded evidence')
    monkeypatch.setattr(delivery_investigator.Runner,'run',run)


@pytest.mark.parametrize('fixture,expected_count',[('normal',1),('exception',2)])
def test_actual_tool_wrappers_follow_conditional_investigation(service,monkeypatch,fixture,expected_count):
    _,store=service
    controlled_model(monkeypatch)
    row=store.book('conditional-'+fixture,fixture,NOW)
    findings=asyncio.run(delivery_investigator.investigate(store,row['reference'],'What is happening?',NOW))
    assert len(findings['tool_trace'])==expected_count
    assert findings['tool_trace'][0]['tool']=='get_current_shipment_status'
    if fixture=='exception':
        assert 'scanner failed' in findings['tool_trace'][1]['result']['reason']


def test_missing_model_evidence_does_not_become_completed_findings(service,monkeypatch):
    _,store=service
    row=store.book('must-check-details','exception',NOW)
    controlled_model(monkeypatch,skip_details=True)
    with pytest.raises(DeliveryRecordError,match='problem details'):
        asyncio.run(delivery_investigator.investigate(store,row['reference'],'Why stuck?',NOW))
    controlled_model(monkeypatch,skip_status=True)
    with pytest.raises(DeliveryRecordError,match='status evidence'):
        asyncio.run(delivery_investigator.investigate(store,row['reference'],'Why stuck?',NOW))


def test_overdue_in_transit_requires_details_and_records_absent_reason(service,monkeypatch):
    _,store=service
    row=store.book('overdue-normal','normal',NOW)
    controlled_model(monkeypatch)
    findings=asyncio.run(delivery_investigator.investigate(store,row['reference'],'Is it healthy?','2026-11-13T12:00:00+00:00'))
    assert findings['shipment_status']['status']=='in_transit'
    assert findings['shipment_status']['overdue']
    assert not findings['shipment_status']['on_schedule']
    assert len(findings['tool_trace'])==2
    assert findings['tool_trace'][1]['result']['reason'] is None
    assert findings['tool_trace'][1]['result']['note']=='No specific delay reason is recorded'


def test_investigation_failure_returns_failed_a2a_task(service,monkeypatch):
    app,store=service
    row=store.book('exception-task','exception',NOW)
    controlled_model(monkeypatch,skip_details=True)
    with TestClient(app) as client:
        failed=task(rpc(client,'investigate',{'reference':row['reference'],'question':'Why stuck?','as_of':NOW},token=READ))
        assert failed['status']['state']=='TASK_STATE_FAILED'
        assert 'problem details' in failed['status']['message']['parts'][0]['text']
