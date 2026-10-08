"""Render saved experiment evidence; no model calls or grading inferred from records."""
import json,sys,html,statistics
from pathlib import Path
p=Path(sys.argv[1]);s=json.loads((p/'results.json').read_text());f=json.loads((p/'fixture.json').read_text())
def h(x):return html.escape(str(x))
def overlap(rows):
 events=[]
 for t in rows:
  if t.get('start') is not None and t.get('end') is not None:events.extend([(t['start'],1),(t['end'],-1)])
 n=peak=0
 for _,v in sorted(events):n+=v;peak=max(n,peak)
 return peak
reason_text={'not_delivered':'Delivery has not happened, so payout is not eligible.','delivery_hold':'Only 23 hours have elapsed after delivery; the 24-hour hold still blocks release.','active_return':'An active return blocks payout release until resolved.','provider_failure':'The latest payout attempt failed with a simulated provider timeout; no later success is recorded.','no_payout_due':'A completed full refund leaves zero seller payout due.','paid':'A failed attempt was followed by a successful payout; exclude it from unpaid totals.','release_not_requested':'Delivery and the 24-hour hold prerequisites are met and there is no active return. No release attempt is recorded; the operator motive is unknown.'}
review=json.loads((p/'assistant-review.json').read_text()) if (p/'assistant-review.json').exists() else {}
body=['<h1>Payout orchestration: GPT-5.4</h1><p>Same fixed synthetic task, three sellers, eleven payouts. Record matching and explanation review are separate. Costs below are uncached model estimates; embeddings and timed-out calls without usage are excluded.</p>']
body+=['<table><tr><th>Run</th><th>Execution</th><th>Record match</th><th>Explanation review</th><th>Seconds</th><th>Uncached USD estimate</th><th>Cache-adjusted USD estimate</th><th>Calls</th><th>Cached input</th><th>Peak tool requests</th></tr>']
for r in s['results']:
 m=r['metrics'];g=review.get(r['key'],{});body.append('<tr>'+''.join('<td>'+h(x)+'</td>' for x in [r['key'],r['status'],r['checks']['record_pass'],g.get('summary','pending'),round(r['elapsed_seconds'],1),round(m['estimated_uncached_model_usd'],4),round(m.get('estimated_cache_adjusted_model_usd',m['estimated_uncached_model_usd']),4),m['model_calls'],m['cached_input_tokens'],overlap(m['tool_intervals'])])+'</tr>')
body.append('</table><p>Peak request overlap does not prove physical database parallelism. This small task and repeat count do not establish a general architecture winner.</p>')
body.append('<h2>Variant averages</h2><table><tr><th>Variant</th><th>Runs</th><th>Completed</th><th>Record passes</th><th>Mean seconds</th><th>Mean estimated USD</th></tr>')
for mode in ['serial','parallel','workers']:
 rs=[r for r in s['results'] if r['variant']==mode]
 if rs:body.append('<tr>'+''.join('<td>'+h(x)+'</td>' for x in [mode,len(rs),sum(r['status']=='completed' for r in rs),sum(r['checks']['record_pass'] for r in rs),round(statistics.mean(r['elapsed_seconds'] for r in rs),1),round(statistics.mean(r['metrics']['estimated_uncached_model_usd'] for r in rs),4)])+'</tr>')
body.append('</table>')
for r in s['results']:
 body.append('<h2>'+h(r['key'])+'</h2>')
 if r['error']:body.append('<p>Execution error: '+h(r['error'])+'</p>')
 body.append('<h3>Expected explanation</h3><ul>'+''.join('<li>'+h(x['payout_id'])+': '+h(reason_text[x['reason']])+'</li>' for x in f['expected'])+'</ul>')
 body.append('<details><summary>Expected records and outcome reasons</summary><pre>'+h(json.dumps(f['expected'],indent=2))+'</pre></details>')
 body.append('<h3>Actual answer</h3><pre>'+h(r['answer'])+'</pre>')
 body.append('<details><summary>Record comparison</summary><pre>'+h(json.dumps(r['checks'],indent=2))+'</pre></details>')
 body.append('<details><summary>Assistant explanation review (provisional)</summary><pre>'+h(json.dumps(review.get(r['key'],{'status':'pending'}),indent=2))+'</pre></details>')
 body.append('<details><summary>Tool sequence and returned evidence</summary><pre>'+h(json.dumps(r['metrics']['tool_intervals'],indent=2))+'</pre></details>')
(p/'comparison.html').write_text('<!doctype html><meta charset="utf-8"><title>Payout orchestration</title><style>body{max-width:1200px;margin:40px auto;font:16px system-ui;padding:20px;color:#182536}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd5df;padding:10px;text-align:left}pre{white-space:pre-wrap;background:#f1f4f7;padding:16px;overflow-wrap:anywhere}details{margin:14px 0}summary{cursor:pointer}</style>'+''.join(body))
print(p/'comparison.html')
