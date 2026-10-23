"""Recorded Test-only post-payout return, prepared without changing the demo clock."""
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from .db import engine, State, User, Seller, Product, Listing, Order, Item, Payment, Allocation, Shipment, Payout, Return, Refund, Event
from .business import uid

SELLER='design-demo-seller'
PRODUCT='design-demo-product'
LISTING='design-demo-listing'
KIND='agent_design_return_scenario'

def require_test():
    if engine.url.database != 'market_test':
        raise ValueError('Scenario preparation is available only in Test')

def record(db, order_id):
    row=db.execute(select(Order.id.label('order_id'), Payout.status.label('payout_status'),
        Return.status.label('return_status'), Return.id.label('return_id'), Shipment.status.label('shipment_status'))
        .join(Item,Item.order_id==Order.id).join(Allocation,Allocation.item_id==Item.id)
        .join(Payout,Payout.allocation_id==Allocation.id).join(Return,Return.item_id==Item.id)
        .join(Shipment,Shipment.item_id==Item.id).where(Order.id==order_id)).mappings().one_or_none()
    return dict(row) if row else None

def prepare(db, owner):
    require_test()
    state=db.scalar(select(State).where(State.id==1).with_for_update(nowait=True))
    if state is None: raise ValueError('Test marketplace has not been initialized')
    previous=db.scalars(select(Event).where(Event.kind==KIND,Event.details['actor'].as_string()==owner)
        .order_by(Event.revision.desc(),Event.recorded_at.desc())).first()
    if previous:
        existing=record(db,previous.entity_id)
        if existing and existing['payout_status']=='completed' and existing['return_status']=='manual_review':
            return {**existing,'reused':True,'question':question(existing['order_id'])}
    buyer=db.get(User,'buyer')
    if not buyer or buyer.role!='buyer':raise ValueError('Seeded Test buyer is required')
    # Dedicated fixture entities leave existing inventory and seller balances unchanged.
    for cls,key,values in [
        (Seller,SELLER,dict(name='Design patterns demo seller')),
        (Product,PRODUCT,dict(name='Return demo item',category='Lab fixtures')),
        (Listing,LISTING,dict(seller_id=SELLER,product_id=PRODUCT,price=10000,stock=0))]:
        current=db.get(cls,key)
        if current and any(getattr(current,k)!=v for k,v in values.items()):raise ValueError('Scenario entity ID is already in use')
        if not current:db.add(cls(id=key,**values));db.flush()
    state.revision+=1
    clock=state.clock; recorded=datetime.now(timezone.utc)
    order=Order(id=uid('design-order'),customer_id=buyer.id,status='paid',created_at=clock-timedelta(hours=27));db.add(order);db.flush()
    payment=Payment(id=uid('design-payment'),order_id=order.id,amount=10000,status='captured',currency='INR');db.add(payment);db.flush()
    item=Item(id=uid('design-item'),order_id=order.id,listing_id=LISTING,seller_id=SELLER,quantity=1,unit_price=10000);db.add(item);db.flush()
    allocation=Allocation(id=uid('design-allocation'),item_id=item.id,payment_id=payment.id,gross=10000,fee=1000,refunded=0,policy='settlement-v1');db.add(allocation);db.flush()
    shipment=Shipment(id=uid('design-shipment'),item_id=item.id,quantity=1,status='delivered',delivered_at=clock-timedelta(hours=26))
    payout=Payout(id=uid('design-payout'),allocation_id=allocation.id,amount=9000,status='completed')
    ret=Return(id=uid('design-return'),item_id=item.id,quantity=1,status='manual_review')
    db.add_all([shipment,payout,ret]);db.flush()
    events=[(payment.id,'payment_captured',27,{'order_id':order.id,'amount':10000}),
        (shipment.id,'dispatch',26.5,{'id':shipment.id}),
        (shipment.id,'deliver',26,{'id':shipment.id}),
        (payout.id,'payout',2,{'id':payout.id,'outcome':'completed'}),
        (ret.id,'request_return',1,{'id':item.id,'quantity':1})]
    for idx,(entity,kind,hours,details) in enumerate(events):
        db.add(Event(id=uid('design-event'),entity_id=entity,kind=kind,occurred_at=clock-timedelta(hours=hours),
            recorded_at=recorded+timedelta(microseconds=idx),revision=state.revision,
            details={**details,'simulated':True,'fixture':KIND}))
    db.add(Event(id=uid('design-event'),entity_id=order.id,kind=KIND,occurred_at=clock,recorded_at=recorded+timedelta(microseconds=5),
        revision=state.revision,details={'actor':owner,'simulated':True,'prepared_history':True}))
    db.flush()
    return {**record(db,order.id),'reused':False,'question':question(order.id)}

def question(order_id):
    return f'Why is the return for {order_id} in manual review? Did the seller reject it?'
