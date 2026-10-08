"""Assemble saved candidate outputs and explicit assistant review; no API calls."""
import json,hashlib,html
from collections import Counter
from pathlib import Path
APP=Path(__file__).resolve().parents[1]
OUT=APP/'results/core18-gpt5-v2-2026-09-29'
def read(p):return json.loads(p.read_text())
new=read(OUT/'results.json');oldpath=APP/'results/core18-2026-09-28-03/results.json';old=read(oldpath)
nanopath=APP/'results/nano-v2-case17-2026-09-29/results.json';nano=read(nanopath)
hpath=oldpath.parent/'human-review.json';human=read(hpath)['reviews'];grades=read(OUT/'assistant-review.json')
refs=read(APP/'eval/review-references.json')['cases'];gold=read(APP/'eval/gold-v3.json')['cases']
rows=[]
for r in new['results']:
 cid=r['case']['id'];assert len(r['turns'])==len(next(x for x in old['results'] if x['case']['id']==cid)['turns'])
 for alias,record,source in [('eval-5',r,OUT/'results.json'),('eval-nano',next(x for x in (nano if cid=='17' else old)['results'] if x['case']['id']==cid and 'nano' in x['model']),nanopath if cid=='17' else oldpath)]:
  assert record['fixture_hash']==r['fixture_hash'],cid
  assert [t['question'] for t in record['turns']]==[t['question'] for t in r['turns']],cid
  for name in ['agent.py','db.py','seed.py','business.py']:
   assert new['manifest']['source_hashes'][name]==(nano if cid=='17' else old)['manifest']['source_hashes'][name],name
  review=grades[alias][cid] if cid in grades.get(alias,{}) else {'grade':human[record['key']]['decision'],'basis':'existing human review','notes':human[record['key']].get('notes',''),'uncertain':False}
  expected=refs[cid]['expected_answers']
  if cid=='17':expected=['Yes. At 2026-09-28 12:30 UTC, delivery at 2026-09-27 12:00 UTC was 24.5 hours ago. No active return blocks release. Eligible, not already paid; operator action required.']
  rows.append({'case':cid,'model':alias,'review':review,'expected_text':expected,'calibrated_requirements':gold.get(cid,record['case']['gold']),'source':str(source.relative_to(APP)), 'source_key':record['key'],'fixture_hash':record['fixture_hash'],'turns':record['turns'],'cost':sum(t['run']['metrics']['estimated_model_cost_usd'] for t in record['turns']),'seconds':sum(t['run']['metrics'].get('elapsed_seconds',0) for t in record['turns'])})
summary={}
for model in ['eval-nano','eval-5']:
 subset=[r for r in rows if r['model']==model];counts=Counter(r['review']['grade'] for r in subset)
 summary[model]={'counts':dict(counts),'fully_correct_percent':100*counts['correct']/18,'cost_of_saved_answers':sum(r['cost'] for r in subset),'uncertain_cases':[r['case'] for r in subset if r['review'].get('uncertain')]}
artifact={'purpose':'Assistant-reviewed GPT-5 versus preserved human-reviewed nano; user-confirmed adjudications override nano17/28 and GPT-5 21/28. No Claude grading.','rows':rows,'summary':summary,'new_spend_estimate_usd':new['cost_estimate_usd']+nano['cost_estimate_usd'],'source_hashes':{str(p.relative_to(APP)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT/'results.json',oldpath,nanopath,hpath,OUT/'assistant-review.json']}}
(OUT/'comparison.json').write_text(json.dumps(artifact,indent=2))
e=html.escape
body='<h1>GPT-5 versus nano: core18, payout fixture v2</h1><p>No Claude calls. GPT-5 is assistant-reviewed, with user-confirmed grades for cases21/28. Nano preserves earlier human grades except the user-confirmed v2 case17 and case28 override. Fully correct percentage excludes partial answers. This is a small diagnostic set, not a general model ranking.</p><table><tr><th>Model</th><th>Correct</th><th>Partial</th><th>Incorrect</th><th>Fully correct</th></tr>'
for model,s in summary.items():body+=f'<tr><td>{model}</td><td>{s["counts"].get("correct",0)}</td><td>{s["counts"].get("partially_correct",0)}</td><td>{s["counts"].get("incorrect",0)}</td><td>{s["fully_correct_percent"]:.1f}%</td></tr>'
body+='</table><p>New uncached-list-rate estimate: $'+f'{artifact["new_spend_estimate_usd"]:.4f}'+'; excludes embeddings and infrastructure.</p><p>Grades are not directly interchangeable reviewer measurements: nano retains earlier human decisions, GPT-5 has assistant review. The flagged grades have been adjudicated by the user; other historical nano grades have not been regraded. No paid judge was run. Historical human grades are unchanged, and automatic routing is not enabled.</p>'
for r in rows:
 review=r['review'];body+=f'<article><h2>Case {r["case"]} · {r["model"]} · {review["grade"]}'+(' · REVIEW REQUESTED' if review.get('uncertain') else '')+'</h2><p>'+e(review.get('notes',''))+'</p><h3>Expected answer</h3><pre>'+e('\n'.join(r['expected_text']))+'</pre>'
 for t in r['turns']:
  body+='<h3>'+e(t['question'])+'</h3><pre>'+e(t['run']['answer'])+'</pre><details><summary>Deterministic checks and compared records</summary><pre>'+e(json.dumps(t['deterministic'],indent=2))+'</pre></details><details><summary>Full retrieved evidence</summary><pre>'+e(json.dumps(t['run']['evidence'],indent=2))+'</pre></details>'
 body+='</article>'
(OUT/'comparison.html').write_text('<!doctype html><meta charset="utf-8"><title>GPT-5 baseline</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px;background:#f6f7fa;color:#182334}table{border-collapse:collapse}td,th{padding:12px;border:1px solid #ccd}article{background:white;padding:24px;margin:24px 0;border:1px solid #dde;border-radius:10px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px system-ui}summary{cursor:pointer;padding:12px}</style>'+body)
print(json.dumps({'summary':summary,'new_spend':artifact['new_spend_estimate_usd']},indent=2))
