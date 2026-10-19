"""Test-only recorded orders for the policy-version comparison."""
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, exists
from sqlalchemy.orm import aliased
from .db import State, Order, Item, Payment, Shipment, Allocation, Payout, Return, Seller, Product, Listing, User, Event, engine
from .business import uid

ACTIVE_RETURNS=('requested','approved','received')

def suitable(record):
    return bool(record and record['payment_status']=='captured' and record['shipment_status']=='delivered'
                and record['payout_status']=='held' and record['payout_amount_paise']>0
                and record['active_returns']==0 and record['hours_since_delivery'] is not None
                and 24 <= record['hours_since_delivery'] < 48)

def require_test():
    if engine.url.database!='market_test':raise ValueError('Demo order preparation is available only in Test')

def order_record(db,order_id):
    # One statement captures the clock and all relevant records consistently.
    active=select(Return.id).where(Return.item_id==Item.id,Return.status.in_(ACTIVE_RETURNS)).exists()
    rows=db.execute(select(Order.id.label('order_id'),Item.id.label('item_id'),Seller.name.label('seller'),
        Payment.status.label('payment_status'),Shipment.status.label('shipment_status'),Shipment.delivered_at,
        Payout.id.label('payout_id'),Payout.status.label('payout_status'),Payout.amount.label('payout_amount_paise'),
        State.clock.label('snapshot_clock'),State.revision.label('snapshot_revision'),active.label('has_active_return'))
        .select_from(Order).join(Item,Item.order_id==Order.id).join(Seller,Seller.id==Item.seller_id)
        .join(Payment,Payment.order_id==Order.id).join(Shipment,Shipment.item_id==Item.id)
        .join(Allocation,Allocation.item_id==Item.id).join(Payout,Payout.allocation_id==Allocation.id)
        .join(State,State.id==1).where(Order.id==order_id)).mappings().all()
    if len(rows)!=1:return None
    value=dict(rows[0]);value['active_returns']=int(value.pop('has_active_return'))
    value['hours_since_delivery']=(value['snapshot_clock']-value['delivered_at']).total_seconds()/3600 if value['delivered_at'] else None
    for key in ('delivered_at','snapshot_clock'):
        if value[key] is not None:value[key]=value[key].isoformat()
    return value

def prepare(db,owner):
    require_test()
    from .rag_policy_demo import locked_state
    selected=locked_state(db,owner,'versions')
    clock=db.scalar(select(State).where(State.id==1).with_for_update())
    if clock is None:raise ValueError('Test marketplace has not been initialized')
    if selected.demo_order_id:
        record=order_record(db,selected.demo_order_id)
        if suitable(record):db.commit();return {**record,'reused':True}
    other=aliased(Item)
    active=select(Return.id).where(Return.item_id==Item.id,Return.status.in_(ACTIVE_RETURNS)).exists()
    multiple=select(other.id).where(other.order_id==Order.id,other.id!=Item.id).exists()
    candidate=db.scalar(select(Order.id).join(Item,Item.order_id==Order.id).join(Payment,Payment.order_id==Order.id)
        .join(Shipment,Shipment.item_id==Item.id).join(Allocation,Allocation.item_id==Item.id)
        .join(Payout,Payout.allocation_id==Allocation.id)
        .where(Payment.status=='captured',Shipment.status=='delivered',Payout.status=='held',Payout.amount>0,
               Shipment.delivered_at<=clock.clock-timedelta(hours=24),Shipment.delivered_at>clock.clock-timedelta(hours=48),
               ~active,~multiple).order_by(Shipment.delivered_at.desc(),Order.id).limit(1))
    if candidate:
        selected.demo_order_id=candidate;record=order_record(db,candidate);db.commit();return {**record,'reused':True}
    # Dedicated fixture seller/product avoid changing existing sellers' balances or inventory.
    buyer=db.get(User,'buyer')
    if not buyer or buyer.role!='buyer':raise ValueError('Seeded Test buyer is required')
    seller=db.get(Seller,'rag-demo-seller')
    if seller and seller.name!='RAG policy demo seller':raise ValueError('Demo seller ID is already in use')
    if not seller:db.add(Seller(id='rag-demo-seller',name='RAG policy demo seller'));db.flush()
    product=db.get(Product,'rag-demo-product')
    if product and (product.name!='RAG policy demo item' or product.category!='Lab fixtures'):raise ValueError('Demo product ID is already in use')
    if not product:db.add(Product(id='rag-demo-product',name='RAG policy demo item',category='Lab fixtures'));db.flush()
    listing=db.get(Listing,'rag-demo-listing')
    if listing and (listing.seller_id!='rag-demo-seller' or listing.product_id!='rag-demo-product' or listing.price!=10000):raise ValueError('Demo listing ID is already in use')
    if not listing:db.add(Listing(id='rag-demo-listing',seller_id='rag-demo-seller',product_id='rag-demo-product',price=10000,stock=0));db.flush()
    clock.revision+=1
    order=Order(id=uid('rag-order'),customer_id=buyer.id,status='paid',created_at=clock.clock-timedelta(hours=31));db.add(order);db.flush()
    payment=Payment(id=uid('rag-payment'),order_id=order.id,amount=10000,status='captured',currency='INR');db.add(payment);db.flush()
    item=Item(id=uid('rag-item'),order_id=order.id,listing_id='rag-demo-listing',seller_id='rag-demo-seller',quantity=1,unit_price=10000);db.add(item);db.flush()
    allocation=Allocation(id=uid('rag-allocation'),item_id=item.id,payment_id=payment.id,gross=10000,fee=1000,refunded=0,policy='rag-demo-comparison');db.add(allocation);db.flush()
    db.add(Shipment(id=uid('rag-shipment'),item_id=item.id,quantity=1,status='delivered',delivered_at=clock.clock-timedelta(hours=30)))
    db.add(Payout(id=uid('rag-payout'),allocation_id=allocation.id,amount=9000,status='held'))
    db.add(Event(id=uid('rag-event'),entity_id=order.id,kind='rag_demo_order_prepared',occurred_at=clock.clock,
        recorded_at=datetime.now(timezone.utc),revision=clock.revision,details={'fixture':'rag-policy-comparison','actor':owner,'delivery_hours_ago':30,'payment_status':'captured','payout_status':'held'}))
    selected.demo_order_id=order.id;db.flush();record=order_record(db,order.id);db.commit();return {**record,'reused':False}
