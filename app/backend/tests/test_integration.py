"""Real PostgreSQL tests, isolated in a disposable test database by scripts/test.sh."""
import os
assert os.environ.get('DATABASE_URL','').endswith('/market_test'), 'Tests require the isolated market_test database'
import asyncio,pytest
from fastapi.testclient import TestClient
from sqlalchemy import text,select
from marketplace.db import *
from marketplace.seed import seed
from marketplace.api import app
from marketplace.business import execute,BusinessError
from marketplace.tools import validate_sql,ReadContext

@pytest.fixture(autouse=True)
def reset():
    init_schema()
    with engine.begin() as c:
        names=','.join('public.'+x.name for x in reversed(Base.metadata.sorted_tables))
        c.execute(text(f'TRUNCATE {names} CASCADE'))
    with Session.begin() as db: seed(db)

def cmd(actor,action,data,key='test-command-123'):
    with Session.begin() as db: return execute(db,db.get(User,actor),key,action,data)

def test_idempotent_purchase_and_conflict():
    d={'items':[{'listing_id':'listing-1','quantity':1},{'listing_id':'listing-2','quantity':2}]}
    a=cmd('buyer','purchase',d); b=cmd('buyer','purchase',d)
    assert a==b
    with Session() as db:
        assert db.get(Listing,'listing-1').stock==17
        assert db.get(Listing,'listing-2').stock==16
        assert db.get(State,1).revision==2
    with pytest.raises(BusinessError):cmd('buyer','purchase',{'items':[{'listing_id':'listing-1','quantity':2}]})

def test_failed_purchase_rolls_back():
    with pytest.raises(BusinessError):cmd('buyer','purchase',{'items':[{'listing_id':'listing-1','quantity':1},{'listing_id':'listing-2','quantity':99}]})
    with Session() as db:
        assert db.get(Listing,'listing-1').stock==18
        assert db.get(State,1).revision==1

def test_partial_refund_and_payout_conserve_money():
    ret=cmd('buyer','request_return',{'id':'item-1','quantity':1})['id']
    cmd('operator','approve_return',{'id':ret},'approve-123')
    cmd('operator','receive_return',{'id':ret},'receive-123')
    with pytest.raises(BusinessError):cmd('operator','payout',{'id':'payout-1'},'blocked-payout')
    cmd('operator','refund',{'id':ret,'outcome':'failed'},'refund-failed')
    with Session() as db: assert db.get(Allocation,'allocation-1').refunded==0
    cmd('operator','refund',{'id':ret,'outcome':'completed'},'refund-success')
    cmd('operator','payout',{'id':'payout-1'},'payout-success')
    with Session() as db:
        a=db.get(Allocation,'allocation-1'); p=db.get(Payout,'payout-1')
        assert a.gross==a.refunded+a.fee+p.amount
        assert a.refunded==249900 and a.fee==24990 and p.amount==224910
        assert db.get(Listing,'listing-1').stock==19
    with pytest.raises(BusinessError):cmd('operator','refund',{'id':ret},'refund-duplicate')

def test_delivery_hold_and_seller_scope():
    with pytest.raises(BusinessError):cmd('seller','dispatch',{'id':'shipment-3'})
    cmd('operator','dispatch',{'id':'shipment-3'},'dispatch-123')
    cmd('operator','deliver',{'id':'shipment-3'},'deliver-123')
    with pytest.raises(BusinessError):cmd('operator','payout',{'id':'payout-3'},'early-payout')
    cmd('operator','advance_clock',{'hours':24},'advance-123')
    cmd('operator','payout',{'id':'payout-3'},'release-123')

def test_read_snapshot_and_database_permissions():
    ctx=ReadContext()
    try:
        before=ctx.query('SELECT captured FROM seller_balances WHERE seller_id = %(seller)s',{'seller':'seller-1'})['rows'][0]['captured']
        cmd('buyer','purchase',{'items':[{'listing_id':'listing-1','quantity':1}]})
        assert ctx.query("SELECT captured FROM seller_balances WHERE seller_id='seller-1'")['rows'][0]['captured']==before
        with pytest.raises(Exception):ctx.conn.execute('SELECT * FROM public.users')
    finally:ctx.close()
    fresh=ReadContext()
    try:assert fresh.query("SELECT captured FROM seller_balances WHERE seller_id='seller-1'")['rows'][0]['captured']==before+249900
    finally:fresh.close()

@pytest.mark.parametrize('sql',["SELECT * FROM public.users","SELECT pg_read_file('/etc/passwd')","SELECT pg_sleep(1)","SELECT * FROM users","DELETE FROM orders","SELECT 1; SELECT 2","WITH x AS (DELETE FROM orders RETURNING *) SELECT * FROM x","SELECT * INTO hacked FROM orders","SELECT * FROM orders FOR UPDATE"])
def test_unsafe_sql_rejected(sql):
    with pytest.raises(ValueError):validate_sql(sql)

def test_document_effective_dates():
    ctx=ReadContext()
    try:
        result=asyncio.run(ctx.search('returns days policy',top_k=8))
        assert all(c['version']!='v0' for c in result['chunks'])
        old=asyncio.run(ctx.search('returns days policy','2025-06-01T00:00:00+00:00',top_k=8))
        assert any(c['version']=='v0' for c in old['chunks'])
    finally:ctx.close()

def test_api_identity_csrf_and_conversation_ownership():
    with TestClient(app) as client:
        assert client.get('/api/market').status_code==401
        result=client.post('/api/login',json={'username':'buyer','password':'demo-marketplace'}).json()
        assert client.post('/api/commands',json={'action':'purchase','data':{},'idempotency_key':'csrf-test-key'}).status_code==403
        client.headers['x-csrf-token']=result['csrf']
        assert client.get('/api/conversations').status_code==403
        market=client.get('/api/market').json()
        assert all(o['customer_id']=='buyer' for o in market['orders'])
        assert not market['payouts']
        support=client.post('/api/login',json={'username':'support','password':'demo-marketplace'}).json();client.headers['x-csrf-token']=support['csrf']
        cid=client.post('/api/conversations',json={}).json()['id']
        denied=client.post('/api/commands',json={'action':'stock','data':{'id':'listing-1','stock':1},'idempotency_key':'support-cant-write'})
        assert denied.status_code==409
        operator=client.post('/api/login',json={'username':'operator','password':'demo-marketplace'}).json();client.headers['x-csrf-token']=operator['csrf']
        assert client.get('/api/conversations/'+cid+'/runs').status_code==404

def test_vector_search_with_restricted_reader(monkeypatch):
    from types import SimpleNamespace
    from marketplace import tools
    vector=[1.0]+[0.0]*1535
    with Session.begin() as db:
        for doc in db.scalars(select(Document)).all():doc.embedding=vector;doc.embedding_model='test-fixture'
    class FakeEmbeddings:
        async def create(self,**kwargs):return SimpleNamespace(data=[SimpleNamespace(embedding=vector)])
    class FakeClient:
        embeddings=FakeEmbeddings()
        async def close(self):pass
    monkeypatch.setattr(tools,'client',lambda:FakeClient())
    ctx=ReadContext()
    try:
        result=asyncio.run(ctx.search('return policy'))
        assert result['method']=='pgvector_cosine'
        assert result['chunks'] and all(c['version']!='v0' for c in result['chunks'])
    finally:ctx.close()

def test_concurrent_duplicate_purchase_commits_once():
    from concurrent.futures import ThreadPoolExecutor
    payload={'items':[{'listing_id':'listing-1','quantity':1}]}
    with ThreadPoolExecutor(max_workers=2) as pool:
        results=list(pool.map(lambda _:cmd('buyer','purchase',payload,'same-concurrent-key'),range(2)))
    assert results[0]==results[1]
    with Session() as db:
        assert db.get(Listing,'listing-1').stock==17
        assert db.get(State,1).revision==2

def test_eval_numeric_terms_ignore_formatting_not_units():
    from marketplace.evaluate import expected_terms
    assert expected_terms('INR 4998.00, fees 499.8 and unpaid 4,498.20',['4,998','499.80','4,498.20'])
    assert not expected_terms('499800 paise',['4,998'])

def test_estimated_cost_budget_stops_further_turns(monkeypatch):
    from types import SimpleNamespace
    from marketplace import agent
    monkeypatch.setattr(agent,'MAX_ESTIMATED_COST',0.000001)
    with pytest.raises(agent.CostBudgetExceeded):
        asyncio.run(agent.BudgetHooks().on_llm_end(None,None,SimpleNamespace(usage=SimpleNamespace(input_tokens=1000,output_tokens=1000))))

@pytest.mark.parametrize('account,expected_listings',[('seller',{'listing-1','listing-4'}),('operator',{f'listing-{i}' for i in range(1,7)}),('buyer',{f'listing-{i}' for i in range(1,7)})])
def test_catalog_visibility_matches_role(account,expected_listings):
    with TestClient(app) as client:
        result=client.post('/api/login',json={'username':account,'password':'demo-marketplace'}).json()
        client.headers['x-csrf-token']=result['csrf']
        data=client.get('/api/market').json()
        assert {listing['id'] for listing in data['listings']}==expected_listings
        if account=='seller':
            assert {seller['id'] for seller in data['sellers']}=={'seller-1'}
            assert {product['id'] for product in data['products']}=={'product-1','product-4'}
            allowed=client.post('/api/commands',json={'action':'stock','data':{'id':'listing-1','stock':12},'idempotency_key':'own-stock-update'})
            assert allowed.status_code==200
            denied=client.post('/api/commands',json={'action':'stock','data':{'id':'listing-2','stock':12},'idempotency_key':'other-stock-update'})
            assert denied.status_code==409


def test_order_history_preserves_failed_refund_after_retry():
    ret=cmd('buyer','request_return',{'id':'item-1','quantity':1},'history-request')['id']
    cmd('seller','approve_return',{'id':ret},'history-approve')
    cmd('seller','receive_return',{'id':ret},'history-receive')
    cmd('operator','refund',{'id':ret,'outcome':'failed'},'history-failure')
    cmd('operator','refund',{'id':ret,'outcome':'completed'},'history-success')
    ctx=ReadContext()
    try:
        history=ctx.order_history('order-1')
        attempts=[r for r in history['event_timeline']['rows'] if r['kind']=='refund']
        assert [r['details']['outcome'] for r in attempts]==['failed','completed']
        assert attempts[0]['revision']<attempts[1]['revision']
        current=[r for r in history['current_records']['rows'] if r['return_id']==ret][0]
        assert current['refund_status']=='completed'
        assert current['refund_amount_paise']==249900
        # A partial refund leaves the other unit payable.
        assert current['payout_amount_paise']==224910
        other=ctx.order_history('order-2')
        assert not any(r['kind']=='refund' for r in other['event_timeline']['rows'])
        missing=ctx.order_history('order-does-not-exist')
        assert missing['current_records']['rows']==[]
        assert missing['event_timeline']['rows']==[]
    finally: ctx.close()


@pytest.mark.parametrize('sql,params',[
    ("SELECT id FROM sellers WHERE name ILIKE '%cedar%'",None),
    ("SELECT id FROM sellers WHERE name ILIKE '%cedar%'",{}),
    ("SELECT id FROM sellers WHERE name ILIKE %(name)s",{'name':'%cedar%'}),
    ("SELECT id FROM sellers WHERE name ILIKE '%cedar%' AND id=%(id)s",{'id':'seller-1'}),
])
def test_wildcard_queries_with_and_without_parameters(sql,params):
    ctx=ReadContext()
    try:
        assert ctx.query(sql,params)['rows']==[{'id':'seller-1'}]
        assert ctx.query('SELECT id FROM sellers WHERE name ILIKE %(name)s',{'name':"%'; DROP TABLE sellers; --"})['rows']==[]
    finally: ctx.close()


def test_name_collision_requires_targeted_query():
    with Session.begin() as db:
        db.add(Product(id='ambiguous-product',name='Cedar Desk',category='Home'))
    ctx=ReadContext()
    try:
        catalog=ctx.catalog()
        assert 'business_names' not in catalog
        assert 'Cedar Desk' not in str(catalog)
        names=ctx.query("SELECT 'seller' AS entity_type,id,name FROM sellers WHERE name ILIKE %(name)s UNION ALL SELECT 'product' AS entity_type,id,name FROM products WHERE name ILIKE %(name)s", {'name':'%cedar%'})['rows']
        matches=[n for n in names if 'cedar' in n['name'].lower()]
        assert {n['entity_type'] for n in matches}=={'seller','product'}
    finally:ctx.close()


@pytest.mark.parametrize('role',['buyer','seller','operator'])
def test_market_orders_newest_first_with_fixed_clock_and_role_scope(monkeypatch,role):
    from marketplace import business
    original_uid=business.uid
    ids=iter(['ord-a-older','ord-z-newer','ord-m-other-buyer'])
    monkeypatch.setattr(business,'uid',lambda prefix:next(ids) if prefix=='ord' else original_uid(prefix))
    first=cmd('buyer','purchase',{'items':[{'listing_id':'listing-1','quantity':1}]},'purchase-older')
    second=cmd('buyer','purchase',{'items':[{'listing_id':'listing-1','quantity':1}]},'purchase-newer')
    other=cmd('buyer2','purchase',{'items':[{'listing_id':'listing-3','quantity':1}]},'purchase-other')
    with TestClient(app) as client:
        assert client.post('/api/login',json={'username':role,'password':'demo-marketplace'}).status_code==200
        orders=client.get('/api/market').json()['orders']
    ids=[order['id'] for order in orders]
    assert ids.index(second['id'])<ids.index(first['id'])
    if role=='operator':assert ids[:3]==[other['id'],second['id'],first['id']]
    else:
        assert ids[:2]==[second['id'],first['id']]
        assert other['id'] not in ids


def test_secondary_seller_login_is_scoped_to_northstar_goods():
    with TestClient(app) as client:
        login=client.post('/api/login',json={'username':'seller2','password':'demo-marketplace'})
        assert login.status_code==200
        client.headers['x-csrf-token']=login.json()['csrf']
        data=client.get('/api/market').json()
        assert data['sellers']==[{'id':'seller-2','name':'Northstar Goods'}]
        assert data['listings'] and all(row['seller_id']=='seller-2' for row in data['listings'])
        assert data['items'] and all(row['seller_id']=='seller-2' for row in data['items'])
        denied=client.post('/api/commands',json={'action':'stock','data':{'id':'listing-1','stock':1},'idempotency_key':'northstar-not-cedar'})
        assert denied.status_code==409
        allowed=client.post('/api/commands',json={'action':'stock','data':{'id':'listing-2','stock':11},'idempotency_key':'northstar-own-stock'})
        assert allowed.status_code==200


def test_secondary_seller_backfill_preserves_existing_market():
    purchase=cmd('buyer','purchase',{'items':[{'listing_id':'listing-1','quantity':1}]},'before-seller-backfill')
    with Session.begin() as db:
        state=db.get(State,1);before=(state.revision,state.clock)
        db.delete(db.get(User,'seller2'));db.flush()
        seed(db);db.flush()
        account=db.get(User,'seller2')
        assert account.role=='seller' and account.seller_id=='seller-2'
        original_hash=account.password_hash
        seed(db);db.flush()
        assert db.get(User,'seller2').password_hash==original_hash
        assert (state.revision,state.clock)==before
        assert db.get(Order,purchase['id']) is not None
        assert db.get(Listing,'listing-1').stock==17
