"""Offline evidence-vs-gold checks. No model calls, SQL execution, or answer parsing."""
from collections import Counter
from decimal import Decimal, InvalidOperation
import json

VERSION = 'evidence-gold-v1'


def normalize(value):
    if value is None or isinstance(value, bool):
        return value
    try:
        number = Decimal(str(value))
        if number.is_finite():
            return str(number.normalize())
    except InvalidOperation:
        pass
    return value


def compare_rows(expected, actual):
    """Multiset equality: order is irrelevant, duplicates are not."""
    def keyed(rows):
        return Counter(json.dumps({k: normalize(v) for k, v in row.items()}, sort_keys=True) for row in rows)
    want, got = keyed(expected), keyed(actual)
    expand = lambda counts: [json.loads(key) for key, n in counts.items() for _ in range(n)]
    return {'passed': want == got, 'missing': expand(want - got), 'unexpected': expand(got - want)}


def contract(case_id, turn_index, aliases):
    if case_id == '02':
        return [{'product_name':'Canvas Weekender','quantity':2,'seller_name':'Cedar & Co.'},
                {'product_name':'Desk Lamp','quantity':2,'seller_name':'Northstar Goods'}], 'Products, quantities and sellers for order-1'
    if case_id == '04' and aliases.get('TODAY'):
        return [{'order_id':aliases['TODAY']['order'],'shipment_status':'pending'}], 'Today’s matching order and shipment state'
    if case_id == '27' and turn_index == 1:
        return [{'order_id':'order-1','product_name':'Canvas Weekender','quantity':2}], 'Seller-scoped order items after clarification'
    if case_id == '24':
        return [{'unpaid':224910}], 'Remaining payable in paise only; refund explanation is judged separately'
    if case_id == '28':
        return [{'unpaid':449820 if turn_index == 0 else 674730}], 'Current Cedar unpaid balance in paise for this turn'
    if case_id == '26':
        return [{'captured':939400,'refunded':0,'fees':93940,'paid_out':0,'unpaid':845460}], 'Marketplace reconciliation totals in paise'
    return None, 'No deterministic record contract for this case/turn; use evidence and semantic review'


def structured_gold(case_id, run, *, turn_index=0, aliases=None):
    expected, scope = contract(case_id, turn_index, aliases or {})
    result = {'version':VERSION,'scope':scope,'expected':expected,'passed':None,'status':'not_applicable','comparisons':[]}
    if expected is None:
        return result
    fields = list(expected[0])
    names = {'unpaid':('unpaid','remaining_payable'), 'product_name':('product_name','product'),
             'seller_name':('seller_name','seller'), 'quantity':('quantity','qty')}
    for handle, evidence in run.get('evidence', {}).items():
        if evidence.get('type') != 'query' or evidence.get('status') not in ('ok','empty'):
            continue
        rows = evidence.get('rows', [])
        columns = set(evidence.get('columns', [])) or {k for r in rows for k in r}
        mapping = {field: next((name for name in names.get(field,(field,)) if name in columns), None) for field in fields}
        if not all(mapping.values()):
            continue
        if evidence.get('truncated'):
            result['comparisons'].append({'handle':handle,'passed':None,'reason':'Truncated evidence cannot establish the complete result set'})
            continue
        if any(any(key not in row for key in mapping.values()) for row in rows):
            result['comparisons'].append({'handle':handle,'passed':None,'reason':'Missing fields in returned rows'})
            continue
        actual = [{field:row[key] for field,key in mapping.items()} for row in rows]
        # Require explicit Cedar identity in returned rows or the bound seller parameter.
        if case_id in ('24','28') and not (evidence.get('params',{}).get('seller_id')=='seller-1' or
                rows and all(r.get('seller_id')=='seller-1' or r.get('name')=='Cedar & Co.' or r.get('seller_name')=='Cedar & Co.' for r in rows)):
            continue
        if case_id == '26' and rows and any(k in columns for k in ('seller_id','name','seller_name')):
            # Validate seller-level grain before summing; never count duplicate sellers.
            identity = next(k for k in ('seller_id','name','seller_name') if k in columns)
            expected_ids = {'seller-1','seller-2','seller-3'} if identity=='seller_id' else {'Cedar & Co.','Northstar Goods','Everyday Studio'}
            ids = [r.get(identity) for r in rows]
            if len(ids)!=3 or set(ids)!=expected_ids:
                result['comparisons'].append({'handle':handle,'passed':False,'actual':actual,'reason':'Missing, extra or duplicate sellers in reconciliation'})
                continue
            try:
                actual = [{field:sum(Decimal(str(row[field])) for row in actual) for field in fields}]
            except (InvalidOperation, TypeError):
                result['comparisons'].append({'handle':handle,'passed':False,'reason':'Invalid numeric reconciliation values'})
                continue
        comparison = compare_rows(expected, actual)
        result['comparisons'].append({'handle':handle,'actual':json.loads(json.dumps(actual,default=str)),**comparison})
    assessed = [c['passed'] for c in result['comparisons'] if c['passed'] is not None]
    if assessed:
        result['passed'] = all(assessed)
        result['status'] = 'pass' if result['passed'] else 'fail'
    else:
        result['status'] = 'not_assessable'
    result['limits'] = 'Compares named fields in each compatible query result, not prose. All assessed retrievals must match; unsupported shapes and truncated results are not automatic passes. A pass covers only the stated scope.'
    return result
