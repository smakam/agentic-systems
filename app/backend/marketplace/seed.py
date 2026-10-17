import hashlib, json, os
from pathlib import Path
from datetime import datetime, timezone, timedelta
from argon2 import PasswordHasher
from sqlalchemy import select, text
from .db import *

DATA = Path(os.getenv('DATA_DIR', str(Path(__file__).resolve().parents[2] / 'data')))
CLOCK = datetime(2026,9,27,12,tzinfo=timezone.utc)

def seed(db):
    if db.get(State,1):
        # Add the second demo seller to existing installations without reseeding
        # purchases, balances, business history or the stored simulation clock.
        if not db.get(User,'seller2'):
            db.add(User(id='seller2',username='seller2',role='seller',seller_id='seller-2',password_hash=PasswordHasher().hash(os.getenv('DEMO_PASSWORD','demo-marketplace'))))
        return
    db.add(State(id=1,revision=1,clock=CLOCK))
    ph=PasswordHasher()
    for name,role,seller in [('buyer','buyer',None),('buyer2','buyer',None),('seller','seller','seller-1'),('seller2','seller','seller-2'),('operator','operator',None),('support','support',None)]:
        db.add(User(id=name,username=name,role=role,seller_id=seller,password_hash=ph.hash(os.getenv('DEMO_PASSWORD','demo-marketplace'))))
    for i,name in enumerate(['Cedar & Co.','Northstar Goods','Everyday Studio'],1): db.add(Seller(id=f'seller-{i}',name=name))
    db.flush()
    for i,(name,category,price) in enumerate([('Canvas Weekender','Travel',249900),('Desk Lamp','Home',129900),('Ceramic Mug Set','Home',89900),('Trail Backpack','Travel',189900),('Wireless Keyboard','Electronics',299900),('Linen Notebook','Stationery',39900)],1):
        db.add(Product(id=f'product-{i}',name=name,category=category)); db.flush()
        db.add(Listing(id=f'listing-{i}',product_id=f'product-{i}',seller_id=f'seller-{(i-1)%3+1}',price=price,stock=20))
    db.flush()
    # Two captured orders: a delivered unpaid order and an undelivered order.
    for n,listing_ids,delivered in [(1,[1,2],True),(2,[3],False)]:
        order=Order(id=f'order-{n}',customer_id='buyer' if n==1 else 'buyer2',status='paid',created_at=CLOCK-timedelta(days=3))
        db.add(order); db.flush()
        payment=Payment(id=f'payment-{n}',order_id=order.id,amount=0,status='captured',currency='INR'); db.add(payment); db.flush()
        for i in listing_ids:
            listing=db.get(Listing,f'listing-{i}'); listing.stock-=2
            item=Item(id=f'item-{i}',order_id=order.id,listing_id=listing.id,seller_id=listing.seller_id,quantity=2,unit_price=listing.price); db.add(item); db.flush()
            gross=2*listing.price; payment.amount+=gross
            allocation=Allocation(id=f'allocation-{i}',item_id=item.id,payment_id=payment.id,gross=gross,fee=gross//10,refunded=0,policy='settlement-v1'); db.add(allocation); db.flush()
            db.add(Payout(id=f'payout-{i}',allocation_id=allocation.id,amount=gross-gross//10,status='failed' if i==1 else 'held'))
            db.add(Shipment(id=f'shipment-{i}',item_id=item.id,quantity=2,status='delivered' if delivered else 'pending',delivered_at=CLOCK-timedelta(days=2) if delivered else None))
        db.add(Event(id=f'event-capture-{n}',entity_id=order.id,kind='payment_captured',occurred_at=order.created_at,recorded_at=order.created_at,revision=1,details={'payment_id':payment.id,'amount':payment.amount,'simulated':True}))
    db.add(Event(id='event-payout-failed',entity_id='payout-1',kind='payout_failed',occurred_at=CLOCK-timedelta(hours=3),recorded_at=CLOCK-timedelta(hours=3),revision=1,details={'reason':'simulated provider timeout','provider_event_id':'demo-provider-1'}))
    db.add(Ticket(id='ticket-1',order_id='order-1',subject='Buyer paid, seller not paid',status='open',message='Cedar & Co. asks why settlement has not arrived.'))
    db.add(Incident(id='incident-1',title='Simulated payout provider timeout',status='confirmed',affected_ids=['payout-1'],evidence='event-payout-failed confirms one failure; broader impact is unproven.'))
    ingest(db)

def ingest(db):
    manifest=json.loads((DATA/'documents.json').read_text())
    for doc in manifest:
        lines=(DATA/'docs'/doc['file']).read_text().splitlines()
        # Paragraph chunks keep source line locations; retain immutable versions.
        start=0
        for end in range(len(lines)+1):
            if end<len(lines) and lines[end].strip(): continue
            body='\n'.join(lines[start:end]).strip()
            if body:
                chunk_id=f"{doc['id']}:{doc['version']}:{start+1}"
                digest=hashlib.sha256(body.encode()).hexdigest()
                old=db.get(Document,chunk_id)
                if old and old.content_hash!=digest: raise ValueError('Document changed without a new version')
                if not old: db.add(Document(id=chunk_id,title=doc['title'],version=doc['version'],scope=doc.get('scope','all'),effective_from=datetime.fromisoformat(doc['from']),effective_to=datetime.fromisoformat(doc['to']) if doc.get('to') else None,source=doc['file'],line_start=start+1,line_end=end,body=body,content_hash=digest))
            start=end+1

if __name__=='__main__':
    init_schema()
    with Session.begin() as db: seed(db)
