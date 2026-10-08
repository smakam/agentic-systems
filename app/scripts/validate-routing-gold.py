"""Independent checks of material gold facts against evaluator-only pre-run snapshots."""
import json
from pathlib import Path
from datetime import datetime
APP=Path(__file__).resolve().parents[1];OUT=APP/'results/routing-granularity-2026-09-30'
def load(s,t):return json.loads((OUT/f'oracle-{s}-{t}.json').read_text())
def byid(d,k):return {r['id']:r for r in d[k]}
def items(d,order):
 listings=byid(d,'listings');products=byid(d,'products');sellers=byid(d,'sellers')
 return [{'product':products[listings[i['listing_id']]['product_id']]['name'],'quantity':i['quantity'],'seller':sellers[i['seller_id']]['name'],'unit_price_paise':i['unit_price'],'gross_paise':i['unit_price']*i['quantity']} for i in d['order_items'] if i['order_id']==order]
d=load('S1',1);assert items(d,'order-2')==[{'product':'Ceramic Mug Set','quantity':2,'seller':'Everyday Studio','unit_price_paise':89900,'gross_paise':179800}]
assert byid(d,'shipments')['shipment-3']['status']=='pending' and byid(d,'payouts')['payout-3']['amount']==161820
assert byid(d,'payments')['payment-2']['status']=='captured'
d=load('S2',1);assert byid(d,'payouts')['payout-1']['status']=='failed' and byid(d,'payouts')['payout-1']['amount']==449820
assert byid(d,'events')['event-payout-failed']['details']['reason']=='simulated provider timeout'
assert (datetime.fromisoformat(d['state'][0]['clock'])-datetime.fromisoformat(byid(d,'shipments')['shipment-1']['delivered_at'])).total_seconds()==48*3600
assert items(d,'order-1')[0]['product']=='Canvas Weekender'
d=load('S3',1);assert byid(d,'products')['product-cedar-desk']['name']=='Cedar Desk';assert byid(d,'sellers')['seller-1']['name']=='Cedar & Co.'
cedar=[i for i in d['order_items'] if i['seller_id']=='seller-1'];assert len(cedar)==1 and cedar[0]['order_id']=='order-1'
assert all(h['status']=='delivered' for h in d['shipments'] if h['item_id']==cedar[0]['id'])
for t,expected in [(1,449820),(2,674730),(3,674730)]:
 d=load('S4',t);ids={i['id'] for i in d['order_items'] if i['seller_id']=='seller-1'};alloc={a['id'] for a in d['allocations'] if a['item_id'] in ids};assert sum(p['amount'] for p in d['payouts'] if p['allocation_id'] in alloc and p['status']!='completed')==expected
for t,hours in [(1,23),(2,24.5),(3,24.5)]:
 d=load('S5',t);h=next(h for h in d['shipments'] if not h['id'].startswith('shipment-'));assert (datetime.fromisoformat(d['state'][0]['clock'])-datetime.fromisoformat(h['delivered_at'])).total_seconds()==hours*3600
 a=next(a for a in d['allocations'] if a['item_id']==h['item_id']);p=next(p for p in d['payouts'] if p['allocation_id']==a['id']);assert p['amount']==116910 and p['status']=='held'
d=load('S6',1);rs=items(d,'order-1');assert [(r['product'],r['quantity']) for r in rs]==[('Canvas Weekender',2),('Desk Lamp',2)];assert rs[1]['seller']=='Northstar Goods' and rs[1]['unit_price_paise']==129900 and rs[1]['gross_paise']==259800
# Verify the 24-hour policy from the frozen app document, not from model answers.
settlement=APP/'data/docs/settlement-settlement-v1.md';assert '24' in settlement.read_text()
(OUT/'gold-validation.json').write_text(json.dumps({'status':'passed','sessions':6,'basis':'Independent snapshot arithmetic, joins, event reason and policy source. Not a check of model prose.','policy_source':str(settlement.relative_to(APP))},indent=2));print('Gold facts verified across all six scenarios')
