import ast,json,html,difflib
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'results/payout-input-comparison-2026-09-29'
esc=lambda x:html.escape(str(x))
blocks=[];audits=[]
for cid in ['16','17']:
 pair={k:json.loads((p/f'{cid}-{k}.json').read_text()) for k in ['correct','incorrect']}
 assert pair['correct']['fixture_hash']==pair['incorrect']['fixture_hash']
 assert pair['correct']['messages'][0]==pair['incorrect']['messages'][0]
 assert pair['correct']['question']==pair['incorrect']['question']
 views=[];facts=[]
 for outcome,a in pair.items():
  tools={};calls=[]
  for m in a['messages']:
   if m['role']=='assistant':
    for t in m.get('tool_calls',[]):tools[t['id']]=t['function']['name'];calls.append(t['function']['name'])
   elif m['role']=='tool':
    name=tools[m['tool_call_id']];v=ast.literal_eval(m['content'])
    if name=='get_order_history':hist=v
    elif name=='search_documents':docs=v
  event=next(e for e in hist['event_timeline']['rows'] if e['kind']=='deliver');rec=hist['current_records']['rows'][0]
  fact={'snapshot':hist['current_records']['snapshot'],'delivery_occurred_at':event['occurred_at'],'delivery_recorded_at':event['recorded_at'],'records':hist['current_records']['rows'],'policy':next(c['body'] for c in docs['chunks'] if c['id']=='settlement:settlement-v1:5')}
  facts.append(fact)
  panels=''.join('<details><summary>'+esc(str(i+1)+'. '+m['role'])+'</summary><pre>'+esc(json.dumps(m,indent=2))+'</pre></details>' for i,m in enumerate(a['messages']))
  views.append('<section><h3>'+esc(outcome.title())+'</h3><p>'+esc(a['source']+' / '+a['key'])+'</p><h4>Actual answer</h4><pre>'+esc(a['answer'])+'</pre><h4>Tool sequence</h4><p>'+esc(' → '.join(calls))+'</p><h4>Relevant input facts (extracted verbatim)</h4><pre>'+esc(json.dumps(fact,indent=2))+'</pre><h4>Retrieved passage IDs, in order</h4><pre>'+esc('\n'.join(c['id'] for c in docs['chunks']))+'</pre><h4>Full captured messages</h4>'+panels+'</section>')
  audits.append({'case':cid,'outcome':outcome,'source':a['source'],'key':a['key'],'tool_sequence':calls,'message_characters':sum(len(str(m)) for m in a['messages']),'facts':fact,'passage_ids':[c['id'] for c in docs['chunks']]})
 assert facts[0]==facts[1], 'Core business facts differ'
 lines={k:json.dumps(a['messages'],indent=2).splitlines() for k,a in pair.items()}
 diff='\n'.join(difflib.unified_diff(lines['correct'],lines['incorrect'],fromfile='correct-input',tofile='incorrect-input',lineterm=''))
 (p/f'case-{cid}-messages.diff').write_text(diff)
 blocks.append('<h2>Case '+cid+(' — 23 hours' if cid=='16' else ' — v2: 24 hours 30 minutes')+'</h2><p>Verified identical: question, system prompt, fixture fingerprint, core business records, timestamps and required policy. Other context differs below.</p><main>'+''.join(views)+'</main><details><summary>Full message diff</summary><pre>'+esc(diff)+'</pre></details>')
page='''<!doctype html><meta charset="utf-8"><title>Payout cases 16 and 17: captured inputs</title><style>body{font:16px system-ui;margin:24px;background:#f4f6fa;color:#172434}main{display:grid;grid-template-columns:1fr 1fr;gap:18px}section{padding:20px;background:white;border:1px solid #ccd5e0;border-radius:8px;min-width:0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px;line-height:1.5}summary{cursor:pointer;padding:10px;background:#e9eef6;margin-top:8px}h4{margin-bottom:8px}@media(max-width:850px){main{grid-template-columns:1fr}}</style><h1>Correct versus incorrect: what reached the model?</h1><p>Case 16 compares two runs with identical 23-hour data. Case 17 compares only v2 24h30m runs. Captured SDK messages are shown; these are not downstream provider wire captures. Correct/incorrect labels refer to eligibility, not a full human grade. No model calls were made for this audit.</p>'''+''.join(blocks)
(p/'comparison.html').write_text(page);(p/'audit.json').write_text(json.dumps(audits,indent=2))
print('Verified both pairs: same core records, timestamps, policy, fixture and system prompt. HTML and diffs generated.')
