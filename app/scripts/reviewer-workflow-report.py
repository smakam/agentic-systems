import json,html,sys
from pathlib import Path
p=Path(sys.argv[1]);s=json.load(open(p/'results.json'));g=json.load(open(p/'assistant-grades.json'))
def h(v):return html.escape(str(v))
out=['<h1>Nano → GPT-5.4 reviewer → one nano correction</h1><p>Eight diagnostic cases, five earlier problem cases and three correct controls. Drafts and GPT-5.4 baseline are reused from the same frozen fixture. Reviewer sees full evidence but no golden answer. Final grades are independent provisional assistant review.</p><table><tr><th>Case</th><th>Nano initial</th><th>Revision requested</th><th>Workflow final</th><th>GPT-5.4 baseline</th><th>Incremental USD estimate</th></tr>']
for r in s['results']:
 c=r['case_id'];v=g[c];out.append('<tr>'+''.join('<td>'+h(x)+'</td>' for x in [c,v['initial'],r.get('review',{}).get('needs_revision'),v['final'],v['gpt54'],round(r['incremental_uncached_usd'],4)])+'</tr>')
out.append('</table><p>Expected reference, model answer, reviewer feedback and final verdict are separate. Reference text is an evaluator requirement, not an input to reviewer/generator.</p>')
base=json.load(open(Path(__file__).resolve().parents[1] / 'results/core18-history-v3-2026-10-01/results.json'))
for r in s['results']:
 c=r['case_id'];reference=next(x for x in base['results'] if x['key']=='1-'+c+'-eval-nano')['case']['gold']
 out.append('<h2>Case '+c+': '+h(r['question'])+'</h2><h3>Expected reference</h3><pre>'+h(json.dumps(reference,indent=2))+'</pre><h3>Original nano answer</h3><pre>'+h(r['initial']['answer'])+'</pre><h3>Reviewer feedback</h3><pre>'+h(json.dumps(r.get('review'),indent=2))+'</pre><h3>Final workflow answer</h3><pre>'+h(r.get('answer'))+'</pre><h3>Independent assessment</h3><pre>'+h(json.dumps(g[c],indent=2))+'</pre><details><summary>Full workflow inputs, evidence, tools and usage</summary><pre>'+h(json.dumps(r,indent=2))+'</pre></details>')
(p/'comparison.html').write_text('<!doctype html><meta charset="utf-8"><title>Reviewer workflow</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd;padding:10px;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f4f7;padding:16px}summary{cursor:pointer}</style>'+''.join(out))
