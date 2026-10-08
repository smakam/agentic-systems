from marketplace.eval_structured import compare_rows,structured_gold

def run(rows, columns=None, **kwargs):
    return {'evidence':{'e1':{'type':'query','status':'ok','rows':rows,'columns':columns or list(rows[0]) if rows else columns or [],**kwargs}}}

def test_order_independent_but_duplicates_and_wrong_values_fail():
    expected=[{'quantity':2,'product':'Lamp'},{'quantity':1,'product':'Bag'}]
    assert compare_rows(expected,list(reversed(expected)))['passed']
    assert compare_rows(expected,[{'quantity':'2.0','product':'Lamp'},expected[1]])['passed']
    assert not compare_rows(expected,expected+[expected[0]])['passed']
    assert not compare_rows(expected,[{'quantity':3,'product':'Lamp'},expected[1]])['passed']

def test_products_compare_missing_extra_and_empty():
    rows=[{'product_name':'Canvas Weekender','quantity':2,'seller_name':'Cedar & Co.'},{'product_name':'Desk Lamp','quantity':2,'seller_name':'Northstar Goods'}]
    assert structured_gold('02',run(rows))['passed'] is True
    assert structured_gold('02',run(rows[:1]))['passed'] is False
    assert structured_gold('02',run([],list(rows[0])))['passed'] is False
    assert structured_gold('02',run(rows,truncated=True))['passed'] is None
    assert structured_gold('02',run([{'irrelevant':2}]))['status']=='not_assessable'

def test_fresh_balance_and_scope():
    evidence=run([{'unpaid':449820}],params={'seller_id':'seller-1'})
    assert structured_gold('28',evidence,turn_index=0)['passed'] is True
    assert structured_gold('28',evidence,turn_index=1)['passed'] is False
    assert structured_gold('28',run([{'unpaid':449820}],params={'seller_id':'seller-2'}))['passed'] is None

def test_reconciliation_aggregates_unique_seller_rows():
    rows=[dict(seller_id=s,captured=c,fees=f,unpaid=u,refunded=0,paid_out=0) for s,c,f,u in [('seller-1',499800,49980,449820),('seller-2',259800,25980,233820),('seller-3',179800,17980,161820)]]
    assert structured_gold('26',run(rows))['passed'] is True
    assert structured_gold('26',run(rows+[rows[0]]))['passed'] is False
    assert structured_gold('26',run(rows[:2]))['passed'] is False

def test_semantic_only_case_is_not_an_automatic_pass():
    assert structured_gold('10',run([]))['status']=='not_applicable'
