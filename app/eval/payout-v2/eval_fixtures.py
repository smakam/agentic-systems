"""Isolated, deterministic fixtures. Expected facts are evaluator-only, never agent context."""
import hashlib,json,os
from datetime import timedelta
from urllib.parse import urlparse
from unittest.mock import patch
from sqlalchemy import select,text
import psycopg
from .db import *
from .seed import CLOCK
from .reset import reset
from . import business


def guard_database():
    write=os.environ.get('DATABASE_URL',''); read=os.environ.get('READ_DATABASE_URL','')
    if any(urlparse(x).path!='/market_eval' for x in (write,read)):
        raise RuntimeError('Both connections must target market_eval')
    if (urlparse(write).hostname,urlparse(write).port)!=(urlparse(read).hostname,urlparse(read).port):
        raise RuntimeError('Evaluation connection hosts differ')
    with engine.connect() as c:
        assert c.execute(text('select current_database()')).scalar()=='market_eval'
    with psycopg.connect(read,connect_timeout=5) as c:
        assert c.execute('select current_database()').fetchone()[0]=='market_eval'


def snapshot():
    """Business records only; no logins, passwords, conversations or gold exposed."""
    with Session() as db:
        result={m.__tablename__:[dict(r) for r in db.execute(text(f'SELECT * FROM public.{m.__tablename__} ORDER BY id')).mappings()] for m in [State,*BUSINESS_TABLES]}
    return json.loads(json.dumps(result,default=str))


def fingerprint():
    return hashlib.sha256(json.dumps(snapshot(),sort_keys=True).encode()).hexdigest()

class Factory:
    def __init__(self,case): self.case=case;self.n=0;self.aliases={}
    def uid(self,prefix):
        self.n+=1
        return prefix+'-'+hashlib.sha256(f'{self.case}:{self.n}:{prefix}'.encode()).hexdigest()[:10]
    def command(self,action,data,actor='operator'):
        key=self.uid('eval-command')
        with patch.object(business,'uid',self.uid),Session.begin() as db:
            result=business.execute(db,db.get(User,actor),key,action,data)
            # Event recording clock is deterministic too; revisions preserve command order.
            db.flush()
            event=db.scalars(select(Event).where(Event.revision==result['revision'])).one()
            event.recorded_at=CLOCK+timedelta(microseconds=result['revision'])
            return result
    def purchase(self,listing,alias):
        order=self.command('purchase',{'items':[{'listing_id':listing,'quantity':1}]},'buyer')['id']
        with Session() as db:
            item=db.scalars(select(Item).where(Item.order_id==order)).one()
            ship=db.scalars(select(Shipment).where(Shipment.item_id==item.id)).one()
            alloc=db.scalars(select(Allocation).where(Allocation.item_id==item.id)).one()
            payout=db.scalars(select(Payout).where(Payout.allocation_id==alloc.id)).one()
            values={'order':order,'item':item.id,'shipment':ship.id,'allocation':alloc.id,'payout':payout.id}
        self.aliases[alias]=values
        return values
    def deliver(self,x):
        self.command('dispatch',{'id':x['shipment']});self.command('deliver',{'id':x['shipment']})
    def receive(self,item):
        ret=self.command('request_return',{'id':item,'quantity':1},'buyer')['id']
        self.command('approve_return',{'id':ret});self.command('receive_return',{'id':ret})
        self.aliases['RETURN']={'return':ret};return ret


def restore_embeddings(cache):
    with Session.begin() as db:
        for id,entry in cache.items():
            doc=db.get(Document,id)
            if doc and doc.content_hash==entry['hash']:
                doc.embedding=entry['vector'];doc.embedding_model=entry['model']


def fixture(case_id,cache=None):
    guard_database();reset(True);restore_embeddings(cache or {})
    f=Factory(case_id)
    if case_id in ('07','27'):
        with Session.begin() as db:
            db.add(Product(id='product-cedar-desk',name='Cedar Desk',category='Home'));db.flush()
            db.add(Listing(id='listing-cedar-desk',product_id='product-cedar-desk',seller_id='seller-2',price=99900,stock=20))
    elif case_id=='04':
        with Session.begin() as db:db.get(State,1).clock=CLOCK.replace(hour=0)-timedelta(seconds=1)
        f.purchase('listing-1','YESTERDAY')
        with Session.begin() as db:db.get(State,1).clock=CLOCK
        f.purchase('listing-1','TODAY');f.purchase('listing-2','OTHER')
    elif case_id in ('15','16','17'):
        x=f.purchase('listing-2','LAMP');f.deliver(x)
        f.command('advance_clock',{'hours':23 if case_id=='16' else 24})
        if case_id=='17':
            # Versioned fixture override only: clear the hold boundary by 30 minutes.
            with Session.begin() as db: db.get(State,1).clock += timedelta(minutes=30)
        if case_id=='15':
            f.command('payout',{'id':x['payout']})
            ret=f.command('request_return',{'id':x['item'],'quantity':1},'buyer')['id']
            f.aliases['RETURN']={'return':ret}
    elif case_id=='18':
        f.command('request_return',{'id':'item-2','quantity':1},'buyer')
    elif case_id in ('19','20','21','25','30'):
        x=f.purchase('listing-4','TRAIL');f.deliver(x);ret=f.receive(x['item'])
        if case_id in ('20','21'):f.command('refund',{'id':ret,'outcome':'failed'})
        if case_id in ('21','25'):f.command('refund',{'id':ret,'outcome':'completed'})
    elif case_id=='22':f.command('payout',{'id':'payout-1'})
    elif case_id=='24':f.command('refund',{'id':f.receive('item-1')})
    validate(case_id,f)
    return f


def validate(case,f):
    with Session() as db:
        # Independent arithmetic invariants for all cases.
        for a in db.scalars(select(Allocation)):
            i=db.get(Item,a.item_id);p=db.scalars(select(Payout).where(Payout.allocation_id==a.id)).one()
            assert a.gross==i.quantity*i.unit_price
            assert a.fee==(a.gross-a.refunded)//10
            assert p.amount==a.gross-a.refunded-a.fee
            amounts=db.execute(text("SELECT COALESCE(SUM(f.amount),0) FROM refunds f JOIN returns r ON r.id=f.return_id WHERE r.item_id=:id AND f.status='completed'"),{'id':i.id}).scalar()
            assert amounts==a.refunded
        if case in ('15','16','17'):
            x=f.aliases['LAMP'];p=db.get(Payout,x['payout']);ship=db.get(Shipment,x['shipment']);state=db.get(State,1)
            assert p.amount==116910 and (state.clock-ship.delivered_at).total_seconds()==(23 if case=='16' else 24.5 if case=='17' else 24)*3600
            assert p.status==('completed' if case=='15' else 'held')
            if case=='15':assert db.get(Return,f.aliases['RETURN']['return']).status=='manual_review'
        if case in ('19','20','21','25','30'):
            ret=db.get(Return,f.aliases['RETURN']['return']);x=f.aliases['TRAIL'];a=db.get(Allocation,x['allocation'])
            assert ret.status==('refunded' if case in ('21','25') else 'received')
            assert a.refunded==(189900 if case in ('21','25') else 0)
        if case=='24':
            a=db.get(Allocation,'allocation-1');assert (a.refunded,a.fee)==(249900,24990)
            assert db.get(Payout,'payout-1').amount==224910
        if case=='22':assert db.get(Payout,'payout-1').status=='completed'
        if case=='18':assert db.scalars(select(Return)).one().status=='requested'
        if case in ('07','27'):assert db.get(Product,'product-cedar-desk').name=='Cedar Desk'
        if case=='04':
            today=db.scalars(select(Order).where(Order.created_at>=CLOCK.replace(hour=0))).all()
            assert {o.id for o in today}=={f.aliases['TODAY']['order'],f.aliases['OTHER']['order']}
        # Baseline arithmetic independent of analytics seller_balances implementation.
        if case in ('01','26'):
            assert sum(a.gross for a in db.scalars(select(Allocation)))==939400
            assert sum(a.fee for a in db.scalars(select(Allocation)))==93940


def questions(case,f):
    q=case['question']
    if case['id']=='19':q='Can the return for TRAIL be refunded now, and has the buyer already received a refund?'
    if case['id']=='27':return ['Show orders for Cedar.','I mean the seller.']
    if case['id']=='28':return ["What is Cedar's unpaid balance?",'What is it now?']
    for alias,x in f.aliases.items():
        if 'order' in x:q=q.replace(alias,x['order'])
    return [q]
