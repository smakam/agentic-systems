"""Native read-only lookup over packaged fictional records; no network or database."""
from copy import deepcopy
import json
from pathlib import Path
import re

FIXTURE_PATH = Path(__file__).with_name('orders.json')

def load_fixture():
    data = json.loads(FIXTURE_PATH.read_text())
    if data.get('fictional') is not True or not data.get('dataset_id') or not data.get('as_of'):
        raise ValueError('A versioned fictional fixture is required')
    orders = data.get('orders')
    if not isinstance(orders,list) or not orders:
        raise ValueError('The fixture needs order records')
    ids = set()
    for order in orders:
        oid = order.get('order_id')
        if not isinstance(oid,str) or not re.fullmatch(r'order-demo-[1-9][0-9]*',oid) or oid in ids:
            raise ValueError('Fixture order identifiers must be valid and unique')
        ids.add(oid)
        for key in ('order_status','payment_status','shipment_status','payout_status'):
            if not isinstance(order.get(key),str) or not order[key]:
                raise ValueError('Each fixture order needs explicit statuses')
        if not isinstance(order.get('items'),list) or not order['items']:
            raise ValueError('Each fixture order needs items')
        for item in order['items']:
            if not isinstance(item.get('product'),str) or not item['product'] or not isinstance(item.get('seller'),str) or not item['seller']:
                raise ValueError('Each fixture item needs a product and seller')
            if type(item.get('quantity')) is not int or item['quantity']<1:
                raise ValueError('Each fixture item needs a positive integer quantity')
    return data

def lookup_order(order_id: str) -> dict:
    """Read one fictional order by exact ID, for example order-demo-1.

    Returns recorded products, quantities and statuses, or found=false. The
    packaged fixture is shared demonstration data, not private customer records.
    No user identity, memory scope, path, query or mutation arguments are accepted.
    """
    if not isinstance(order_id,str) or not re.fullmatch(r'order-demo-[1-9][0-9]*',order_id.strip().lower()):
        return {'found':False,'error':'Use a fictional order ID such as order-demo-1.'}
    oid=order_id.strip().lower()
    data=load_fixture()
    order=next((x for x in data['orders'] if x['order_id']==oid),None)
    source={'dataset_id':data['dataset_id'],'as_of':data['as_of'],'fictional':True}
    if order is None:
        return {'found':False,'order_id':oid,'source':source,'error':'No such order exists in the packaged fixture.'}
    return {'found':True,'order':deepcopy(order),'source':source}
