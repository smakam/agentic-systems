"""Offline check correction: order-history envelopes contain nested evidence handles."""
import ast,json,re,sys
from pathlib import Path
p=Path(sys.argv[1]);s=json.loads((p/'results.json').read_text());f=json.loads((p/'fixture.json').read_text())
t=ast.parse((p/'source/payout-orchestration.py').read_text())
ns={'json':json,'re':re}
exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef) and n.name in ['parse_answer','validate_records']],type_ignores=[]),'checks','exec'),ns)
def collect(v,e):
 if isinstance(v,dict):
  if v.get('handle') and v.get('contract_version'):e[v['handle']]=v
  for x in v.values():collect(x,e)
 elif isinstance(v,list):
  for x in v:collect(x,e)
for r in s['results']:
 if 'initial_checks' not in r:r['initial_checks']=r['checks']
 e=dict(r['evidence'])
 for tool in r['metrics']['tool_intervals']:collect(tool.get('result'),e)
 m=r['metrics'];m['estimated_cache_adjusted_model_usd']=((m['input_tokens']-m['cached_input_tokens'])*2.5+m['cached_input_tokens']*.25+m['output_tokens']*15)/1e6
 r['evidence']=e;r['checks']=ns['validate_records'](r['answer'],f['expected'],e)
 r['check_correction']='Offline recursive handle registration for nested get_order_history results; no inference rerun or answer edits.'
(p/'results.json').write_text(json.dumps(s,indent=2))
# Negative controls establish the checker catches missing, duplicate and wrong-value records.
expected=f['expected'];e={'test-handle':{}}
a={'payouts':[{**{k:x[k] for k in ['payout_id','seller_id','seller_name','order_id','payable_paise']},'evidence_handles':['test-handle']} for x in expected],'sellers':[]}
totals={}
for x in expected:totals[x['seller_id']]=totals.get(x['seller_id'],0)+(x['payable_paise'] if x['status']!='completed' else 0)
a['sellers']=[{'seller_id':k,'unpaid_paise':v} for k,v in totals.items()]
assert ns['validate_records'](json.dumps(a),expected,e)['record_pass']
for change in ['missing','duplicate','wrong_value','unknown_handle']:
 d=json.loads(json.dumps(a))
 if change=='missing':d['payouts'].pop()
 elif change=='duplicate':d['payouts'].append(d['payouts'][0])
 elif change=='wrong_value':d['payouts'][0]['payable_paise']+=1
 else:d['payouts'][0]['evidence_handles']=['unknown']
 assert not ns['validate_records'](json.dumps(d),expected,e)['record_pass'],change
print('Checker positive control and four negative controls passed')
