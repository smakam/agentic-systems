"""Common-policy, evaluator-only fixture/oracle. Never supplied as model context."""
from datetime import timedelta
from sqlalchemy import select
from marketplace.db import Session, State, Event, Payout, Allocation, Item, Shipment, Return, Seller
from marketplace.eval_fixtures import fixture, Factory, fingerprint, snapshot
from marketplace.seed import CLOCK

VERSION='payout-orchestration-common-v1'
def build(cache):
    fixture('01',cache)
    f=Factory(VERSION)
    cases={}
    for alias,listing in [('undelivered','listing-1'),('eligible_unattempted','listing-2'),('return_requested','listing-3'),('return_received','listing-4'),('attempt_failed','listing-5'),('fully_refunded','listing-6'),('successful_retry','listing-1')]:
        x=f.purchase(listing,alias);cases[alias]=x
        if alias!='undelivered':f.deliver(x)
    f.command('advance_clock',{'hours':24})
    f.command('request_return',{'id':cases['return_requested']['item'],'quantity':1},'buyer')
    f.receive(cases['return_received']['item'])
    ret=f.receive(cases['fully_refunded']['item']);f.command('refund',{'id':ret})
    for alias in ['attempt_failed','successful_retry']:
        x=cases[alias];r=f.command('payout',{'id':x['payout'],'outcome':'failed'})
        with Session.begin() as db:
            e=db.scalars(select(Event).where(Event.revision==r['revision'])).one()
            e.details={**e.details,'reason':'simulated provider timeout'}
    f.command('payout',{'id':cases['successful_retry']['payout'],'outcome':'completed'})
    x=f.purchase('listing-2','delivery_hold');cases['delivery_hold']=x;f.deliver(x)
    f.command('advance_clock',{'hours':23})
    with Session() as db:
        state=db.get(State,1);assert state.clock==CLOCK+timedelta(hours=47)
        oracle=[]
        for p in db.scalars(select(Payout).order_by(Payout.id)):
            a=db.get(Allocation,p.allocation_id);i=db.get(Item,a.item_id)
            sh=db.scalars(select(Shipment).where(Shipment.item_id==i.id)).one()
            returns=list(db.scalars(select(Return).where(Return.item_id==i.id)))
            events=list(db.scalars(select(Event).where(Event.entity_id==p.id).order_by(Event.revision,Event.recorded_at)))
            if p.status=='completed':reason='paid'
            elif p.amount==0:reason='no_payout_due'
            elif any(x.status in ['requested','approved','received'] for x in returns):reason='active_return'
            elif sh.status!='delivered':reason='not_delivered'
            elif state.clock<sh.delivered_at+timedelta(hours=24):reason='delivery_hold'
            elif p.status=='failed':reason='provider_failure'
            else:reason='release_not_requested'
            oracle.append({'payout_id':p.id,'seller_id':i.seller_id,'seller_name':db.get(Seller,i.seller_id).name,'order_id':i.order_id,'payable_paise':p.amount,'reason':reason,'status':p.status,'events':[{'kind':e.kind,'details':e.details} for e in events]})
    assert len(oracle)==11
    assert len({r['reason'] for r in oracle})==7
    assert next(r for r in oracle if r['payout_id']==cases['successful_retry']['payout'])['reason']=='paid'
    return {'version':VERSION,'hash':fingerprint(),'snapshot':snapshot(),'aliases':cases,'expected':oracle}
