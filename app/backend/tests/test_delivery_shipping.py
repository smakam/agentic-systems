"""Real PostgreSQL/domain and A2A delivery integration, isolated market_test only."""
import asyncio
import os
from types import SimpleNamespace
import httpx
import pytest
from sqlalchemy import select,text
from marketplace import delivery_shipping, delivery_support
from marketplace.business import execute,BusinessError
from marketplace.db import Base,engine,Session,init_schema,User,State,Shipment,ShipmentDeliveryLink,A2AWorkspace,ShipmentDeliveryIntent,Item,Allocation,Payout
from marketplace.seed import seed
from marketplace.delivery_client import delivery_request,DeliveryUnavailable
from marketplace.delivery_service import create_app
from marketplace.delivery_store import DeliveryStore

assert os.environ.get('DATABASE_URL','').endswith('/market_test'), 'Delivery integration tests require isolated market_test'


@pytest.fixture(autouse=True)
def reset():
    init_schema()
    with engine.begin() as db:
        names=','.join('public.'+t.name for t in reversed(Base.metadata.sorted_tables))
        db.execute(text(f'TRUNCATE {names} CASCADE'))
    with Session.begin() as db:seed(db)


@pytest.fixture
def remote(tmp_path,monkeypatch):
    monkeypatch.setenv('DELIVERY_READ_TOKEN','delivery-read-test')
    monkeypatch.setenv('DELIVERY_WRITE_TOKEN','delivery-write-test')
    monkeypatch.setenv('DELIVERY_A2A_URL','http://delivery.test')
    store=DeliveryStore(tmp_path/'service.sqlite3')
    app=create_app(store)
    calls=[]
    async def request(op,data,**kwargs):
        calls.append((op,data))
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app)) as client:
            return await delivery_request(op,data,http_client=client,**kwargs)
    monkeypatch.setattr(delivery_shipping,'delivery_request',request)
    return store,calls


def cmd(actor,action,data,key='delivery-test-key'):
    with Session.begin() as db:
        return asyncio.run(delivery_shipping.execute_shipping_command(db,db.get(User,actor),key,action,data))


def purchased(mode='a2a_delivery',fixture='normal'):
    with Session.begin() as db:db.merge(A2AWorkspace(id=1,mode=mode,fixture=fixture))
    order=cmd('buyer','purchase',{'items':[{'listing_id':'listing-1','quantity':1}]},'buy-'+__import__('uuid').uuid4().hex)['id']
    with Session() as db:
        item=db.scalar(select(Item).where(Item.order_id==order))
        return db.scalar(select(Shipment).where(Shipment.item_id==item.id)).id,item.id


def test_enrollment_dispatch_delivery_holds_returns_and_duplicate_commands(remote):
    store,calls=remote
    sid,iid=purchased()
    booking={'id':sid,'delivery_mode':'a2a','delivery_fixture':'normal'}
    first=cmd('seller','dispatch',booking,'dispatch-linked-once')
    assert first==cmd('seller','dispatch',booking,'dispatch-linked-once')
    assert len(calls)==1
    reference=first['delivery_service']['reference']
    with Session() as db:
        assert db.get(Shipment,sid).status=='dispatched'
        assert db.get(ShipmentDeliveryLink,sid).reference==reference
    # Switching the UI enrollment default cannot bypass an existing link.
    with Session.begin() as db:
        with pytest.raises(BusinessError,match='delivery service'):
            execute(db,db.get(User,'seller'),'direct-linked-bypass','deliver',{'id':sid})
        db.rollback()
    done=cmd('seller','deliver',{'id':sid,'delivery_mode':'local'},'deliver-linked-once')
    assert done==cmd('seller','deliver',{'id':sid,'delivery_mode':'local'},'deliver-linked-once')
    assert [x[0] for x in calls]==['book','deliver']
    assert store.status(reference,'2030-01-01T00:00:00+00:00')['status']=='delivered'
    with Session() as db:
        state=db.get(State,1);ship=db.get(Shipment,sid)
        assert ship.delivered_at==state.clock
        payout=db.scalar(select(Payout).join(Allocation).where(Allocation.item_id==iid)).id
    with pytest.raises(BusinessError,match='24-hour hold'):
        cmd('operator','payout',{'id':payout},'linked-early-payout')
    cmd('operator','advance_clock',{'hours':24},'linked-advance-clock')
    cmd('operator','payout',{'id':payout},'linked-eligible-payout')
    # Existing return logic still recognizes delivered_at and settled payouts.
    returned=cmd('buyer','request_return',{'id':iid,'quantity':1},'linked-after-payout-return')
    assert returned['status']=='manual_review'


def test_legacy_shipments_do_not_require_delivery_service(monkeypatch):
    sid,_=purchased('standard')
    async def never(*a,**kw):raise AssertionError('Legacy shipment must stay local')
    monkeypatch.setattr(delivery_shipping,'delivery_request',never)
    cmd('seller','dispatch',{'id':sid},'legacy-dispatch')
    cmd('seller','deliver',{'id':sid},'legacy-deliver')
    with Session() as db:
        assert db.get(Shipment,sid).status=='delivered'
        assert delivery_shipping.link_json(db,sid) is None


def test_post_dispatch_fixture_control_validates_owner_link_and_lifecycle(remote):
    store,calls=remote
    sid,_=purchased()
    with pytest.raises(BusinessError):
        cmd('seller','delivery_fixture',{'id':sid,'delivery_fixture':'exception'},'fixture-before-dispatch')
    booked=cmd('seller','dispatch',{'id':sid,'delivery_mode':'a2a'},'fixture-linked-dispatch')
    change={'id':sid,'delivery_fixture':'exception'}
    with pytest.raises(BusinessError):cmd('seller2','delivery_fixture',change,'fixture-wrong-owner')
    first=cmd('seller','delivery_fixture',change,'fixture-change-once')
    assert first==cmd('seller','delivery_fixture',change,'fixture-change-once')
    assert [op for op,_ in calls]==['book','set_fixture']
    with Session() as db:
        assert db.get(Shipment,sid).status=='dispatched'
        assert delivery_shipping.link_json(db,sid)['fixture']=='exception'
    reference=booked['delivery_service']['reference']
    assert store.status(reference,'2030-01-01T00:00:00+00:00')['status']=='exception'
    cmd('seller','deliver',{'id':sid},'fixture-final-deliver')
    with pytest.raises(BusinessError):cmd('seller','delivery_fixture',change,'fixture-after-delivery')


def test_wrong_owner_bad_fixture_and_invalid_transition_make_no_remote_write(remote):
    _,calls=remote
    sid,_=purchased()
    for actor,data in [('buyer',{'id':sid,'delivery_mode':'a2a'}),('seller2',{'id':sid,'delivery_mode':'a2a'}),('support',{'id':sid,'delivery_mode':'a2a'})]:
        with pytest.raises(BusinessError):cmd(actor,'dispatch',data)
    with pytest.raises(BusinessError):cmd('seller','deliver',{'id':sid})
    assert not calls
    with Session() as db:assert db.get(Shipment,sid).status=='pending'


def test_remote_outage_does_not_advance_marketplace_or_erase_association(remote,monkeypatch):
    _,_=remote
    sid,_=purchased()
    original=delivery_shipping.delivery_request
    async def offline(*a,**kw):raise DeliveryUnavailable('Delivery unavailable')
    monkeypatch.setattr(delivery_shipping,'delivery_request',offline)
    with pytest.raises(DeliveryUnavailable):cmd('seller','dispatch',{'id':sid,'delivery_mode':'a2a'})
    with Session() as db:
        assert db.get(Shipment,sid).status=='pending'
        assert delivery_shipping.link_json(db,sid) is None
    monkeypatch.setattr(delivery_shipping,'delivery_request',original)
    cmd('seller','dispatch',{'id':sid,'delivery_mode':'a2a'},'book-after-outage')
    monkeypatch.setattr(delivery_shipping,'delivery_request',offline)
    with pytest.raises(DeliveryUnavailable):cmd('seller','deliver',{'id':sid},'outage-delivery')
    with Session() as db:
        assert db.get(Shipment,sid).status=='dispatched'
        assert db.get(Shipment,sid).delivered_at is None
        assert delivery_shipping.link_json(db,sid) is not None


def test_remote_success_local_rollback_retries_without_duplicate_shipment(remote):
    store,calls=remote
    sid,_=purchased()
    payload={'id':sid,'delivery_mode':'a2a','delivery_fixture':'exception'}
    with Session() as db:
        result=asyncio.run(delivery_shipping.execute_shipping_command(db,db.get(User,'seller'),'rollback-dispatch-key','dispatch',payload))
        reference=result['delivery_service']['reference']
        db.rollback()  # Simulates a lost local commit after remote accepted it.
    with Session() as db:
        assert db.get(Shipment,sid).status=='pending'
        assert db.get(ShipmentDeliveryLink,sid) is None
    retry=cmd('seller','dispatch',payload,'rollback-dispatch-key')
    assert retry['delivery_service']['reference']==reference
    assert len(store.issue(reference,'2030-01-01T00:00:00+00:00')['tracking_events'])==2
    with Session() as db:
        assert db.get(Shipment,sid).status=='dispatched'


def test_mismatched_remote_receipt_rejected(remote,monkeypatch):
    sid,_=purchased()
    async def wrong(op,data,**kwargs):return {'reference':'foreign-reference','marketplace_shipment_id':'someone-else','fixture':'normal','status':'in_transit'}
    monkeypatch.setattr(delivery_shipping,'delivery_request',wrong)
    with pytest.raises(BusinessError,match='does not match'):
        cmd('seller','dispatch',{'id':sid,'delivery_mode':'a2a'},'bad-remote-receipt')
    with Session() as db:
        assert db.get(Shipment,sid).status=='pending'
        assert db.get(ShipmentDeliveryLink,sid) is None


def test_support_helper_routes_linked_remote_and_unlinked_local_and_retains_failure(remote,monkeypatch):
    from agents import RunContextWrapper
    from agents.tool_context import ToolContext
    store,_=remote
    sid,_=purchased(fixture='exception')
    with Session() as db:clock=db.get(State,1).clock
    ctx=SimpleNamespace(snapshot={'clock':clock,'revision':1},doc_hash='test',evidence={})
    tool=delivery_support.build_delivery_tool(ctx)
    async def call(question):
        args=__import__('json').dumps({'shipment_id':sid,'question':question})
        tc=ToolContext.from_agent_context(RunContextWrapper(context=None),'call-delivery',tool_name=tool.name,tool_arguments=args)
        return await tool.on_invoke_tool(tc,args)
    local=asyncio.run(call('Where is it?'))
    assert local['source']=='marketplace-local' and not local['linked']
    cmd('seller','dispatch',{'id':sid,'delivery_mode':'a2a','delivery_fixture':'exception'},'support-linked-fixture')
    seen=[]
    async def remote_findings(op,data,**kwargs):
        seen.append((op,data))
        status=store.status(data['reference'],data['as_of'])
        return {'findings':'Recorded scanner failure','reference':data['reference'],
                'source':'simulated-delivery-service','simulated':True,'shipment_status':status,
                'tool_trace':[{'tool':'get_current_shipment_status','result':status},
                              {'tool':'get_delivery_problem_details','result':store.issue(data['reference'],data['as_of'])}]}
    monkeypatch.setattr(delivery_support,'delivery_request',remote_findings)
    linked=asyncio.run(call('Why stuck?'))
    assert linked['linked'] and linked['source']=='simulated-delivery-service'
    assert seen[0][0]=='investigate'
    async def offline(*a,**kw):raise DeliveryUnavailable('Internal details must not leak')
    monkeypatch.setattr(delivery_support,'delivery_request',offline)
    failed=asyncio.run(call('Why stuck?'))
    assert failed['status']=='error' and failed['code']=='DELIVERY_UNAVAILABLE'
    assert failed['handle'] in ctx.delivery_evidence and failed['handle'] in ctx.evidence
    assert delivery_support.has_delivery_links()


@pytest.mark.parametrize('corrupt',['reference','shipment_id','source','clock'])
def test_support_helper_rejects_wrong_or_unverified_remote_findings(remote,monkeypatch,corrupt):
    from agents import RunContextWrapper
    from agents.tool_context import ToolContext
    import json
    store,_=remote
    sid,_=purchased(fixture='exception')
    cmd('seller','dispatch',{'id':sid,'delivery_mode':'a2a'},'unverified-read-booking')
    with Session() as db:clock=db.get(State,1).clock
    ctx=SimpleNamespace(snapshot={'clock':clock,'revision':1},doc_hash='test',evidence={})
    tool=delivery_support.build_delivery_tool(ctx)
    async def wrong(op,data,**kwargs):
        status=store.status(data['reference'],data['as_of'])
        findings={'findings':'Unverified result must not appear as success','reference':data['reference'],
                  'source':'simulated-delivery-service','simulated':True,'shipment_status':status,
                  'tool_trace':[{'tool':'get_current_shipment_status','result':status}]}
        if corrupt=='reference':findings['reference']='other-reference'
        elif corrupt=='shipment_id':status['marketplace_shipment_id']='other-shipment'
        elif corrupt=='source':findings['source']='untrusted-source'
        else:status['simulation_as_of']='2000-01-01T00:00:00+00:00'
        return findings
    monkeypatch.setattr(delivery_support,'delivery_request',wrong)
    async def invoke():
        args=json.dumps({'shipment_id':sid,'question':'Where is it?'})
        tc=ToolContext.from_agent_context(RunContextWrapper(context=None),'wrong-evidence',tool_name=tool.name,tool_arguments=args)
        return await tool.on_invoke_tool(tc,args)
    result=asyncio.run(invoke())
    assert result['status']=='error' and result['code']=='DELIVERY_UNVERIFIED'
    assert 'result' not in result and 'shipment_status' not in result
    assert ctx.delivery_evidence[result['handle']]==result


def test_concurrent_shipping_and_nonshipping_api_commands_finish(remote,monkeypatch):
    from marketplace.api import app
    sid,_=purchased()
    original=delivery_shipping.delivery_request
    async def delayed(*args,**kwargs):
        await asyncio.sleep(.1)
        return await original(*args,**kwargs)
    monkeypatch.setattr(delivery_shipping,'delivery_request',delayed)
    async def run():
        transport=httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport,base_url='http://localhost') as seller, httpx.AsyncClient(transport=transport,base_url='http://localhost') as operator:
            for client,username in [(seller,'seller'),(operator,'operator')]:
                login=await client.post('/api/login',json={'username':username,'password':'demo-marketplace'})
                client.headers['x-csrf-token']=login.json()['csrf']
            async def dispatch(key):
                return await seller.post('/api/commands',json={'action':'dispatch','data':{'id':sid,'delivery_mode':'a2a'},'idempotency_key':key})
            one,two,clock=await asyncio.wait_for(asyncio.gather(dispatch('concurrent-book-one'),dispatch('concurrent-book-two'),operator.post('/api/commands',json={'action':'advance_clock','data':{'hours':1},'idempotency_key':'parallel-clock-change'})),timeout=10)
            assert sorted([one.status_code,two.status_code])==[200,409]
            assert clock.status_code==200,clock.text
    asyncio.run(run())
    with Session() as db:
        assert db.get(Shipment,sid).status=='dispatched'
        assert db.scalar(select(ShipmentDeliveryLink).where(ShipmentDeliveryLink.shipment_id==sid)) is not None


def test_purchase_intent_survives_workspace_changes_and_ignores_seller_override(remote):
    store,calls=remote
    sid,_=purchased(fixture='exception')
    with Session.begin() as db:db.get(A2AWorkspace,1).mode='standard'
    result=cmd('seller','dispatch',{'id':sid,'delivery_mode':'local','delivery_fixture':'normal'},'saved-intent-dispatch')
    assert calls[0][1]['fixture']=='exception'
    assert store.status(result['delivery_service']['reference'],'2030-01-01T00:00:00+00:00')['status']=='exception'
    local,_=purchased('standard')
    with Session.begin() as db:db.get(A2AWorkspace,1).mode='a2a_delivery'
    cmd('seller','dispatch',{'id':local,'delivery_mode':'a2a'},'local-intent-dispatch')
    assert len(calls)==1
    with Session() as db:
        assert db.get(ShipmentDeliveryLink,local) is None
        assert db.get(ShipmentDeliveryIntent,sid).fixture=='exception'
