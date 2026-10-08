"""Compare a regrade with immutable baseline answers and human decisions; no model calls."""
import json,sys,hashlib,html
from pathlib import Path
from collections import Counter
base,new=map(Path,sys.argv[1:3])
b=json.loads((base/'results.json').read_text());n=json.loads((new/'results.json').read_text());h=json.loads((base/'human-review.json').read_text())['reviews']
assert len(n['results'])==len(b['results'])==36
old={r['key']:r for r in b['results']};labels={0:'Incorrect',1:'Partial',2:'Correct'};human={'incorrect':0,'partially_correct':1,'correct':2}
rows=[]
for r in n['results']:
 o=old[r['key']]
 assert len(r['turns'])==len(o['turns'])
 for t,previous in zip(r['turns'],o['turns']):
  assert t['run']==previous['run'] and t['question']==previous['question'], 'Saved answers/evidence changed'
  assert t['deterministic']['checks']==previous['deterministic']['checks'], 'Check verdicts changed'
 a=o['judge']['grade']['correctness'];c=r['judge']['grade']['correctness'];v=human[h[r['key']]['decision']]
 rows.append(dict(key=r['key'],case=r['case']['id'],model='nano' if 'nano' in r['model'] else 'GPT-5.4',human=v,old=a,new=c,changed=a!=c,disagrees=c!=v,uncertain=r['judge']['grade']['uncertain'],old_rationale=o['judge']['grade']['rationale'],new_rationale=r['judge']['grade']['rationale'],answers=[t['run']['answer'] for t in r['turns']],questions=[t['question'] for t in r['turns']],gold=r['case']['gold']))
summary={'baseline_agreement':sum(r['old']==r['human'] for r in rows),'revised_agreement':sum(r['new']==r['human'] for r in rows),'total':36,'changed':sum(r['changed'] for r in rows),'new_cost_estimate_usd':n['cost_estimate_usd']-b['cost_estimate_usd'],'rows':rows,'human_source_sha256':hashlib.sha256((base/'human-review.json').read_bytes()).hexdigest(),'baseline_sha256':hashlib.sha256((base/'results.json').read_bytes()).hexdigest()}
(new/'calibration-comparison.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=['# Judge calibration v3 comparison','',f"Exact agreement with unchanged human grades: **{summary['baseline_agreement']}/36 → {summary['revised_agreement']}/36** ({summary['baseline_agreement']/36:.1%} → {summary['revised_agreement']/36:.1%}).",'',f"Changed grades: {summary['changed']}. Incremental recorded cost estimate: ${summary['new_cost_estimate_usd']:.4f}; excludes embeddings and unreported charges, not an invoice.",'','| Model | Old agreement | Revised agreement | Revised correct / partial / incorrect |','|---|---:|---:|---|']
for m in ['nano','GPT-5.4']:
 rr=[r for r in rows if r['model']==m];counts=Counter(r['new'] for r in rr)
 lines.append(f"| {m} | {sum(r['old']==r['human'] for r in rr)}/18 | {sum(r['new']==r['human'] for r in rr)}/18 | {counts[2]} / {counts[1]} / {counts[0]} |")
lines+=['','## Exceptions: changed grade or remaining disagreement','','| Case | Model | Human | Old Claude | Revised Claude |','|---|---|---|---|---|']
for r in rows:
 if r['changed'] or r['disagrees']:lines.append(f"| {r['case']} | {r['model']} | {labels[r['human']]} | {labels[r['old']]} | {labels[r['new']]} |")
falsepasses=[r['key'] for r in rows if r['human']==0 and r['new']==2]
lines+=['',f'Human-incorrect answers marked fully correct by revised judge: {len(falsepasses)} ({falsepasses}).','','This is calibration on the same reviewed answers, not independent validation or general judge accuracy. Human grades were not supplied to Claude and were not changed. Candidate turns, evidence and checks were verified identical. No candidate-model calls. Original baseline remains unchanged. Gold and rubric both changed, so this run cannot isolate their individual contributions. No scores published to Langfuse.','','[Focused review](calibration-review.html) · [Full comparison data](calibration-comparison.json)']
(new/'CALIBRATION-SUMMARY.md').write_text('\n'.join(lines)+'\n')
esc=html.escape
cards=[]
for r in rows:
 if not(r['changed'] or r['disagrees']):continue
 cards.append(f"<article><h2>Case {r['case']} · {r['model']}</h2><p>Human: <b>{labels[r['human']]}</b> · Claude v2: {labels[r['old']]} → v3: <b>{labels[r['new']]}</b></p><p>{'Remaining disagreement' if r['disagrees'] else 'Now agrees with human'} · Judge uncertainty: {r['uncertain']}</p>"+''.join(f'<h3>{esc(q)}</h3><pre>{esc(a)}</pre>' for q,a in zip(r['questions'],r['answers']))+f"<h3>Revised judge reasoning</h3><p>{esc(r['new_rationale'])}</p><details><summary>Previous judge reasoning</summary><p>{esc(r['old_rationale'])}</p></details><details><summary>Revised gold requirements</summary><pre>{esc(json.dumps(r['gold'],indent=2))}</pre></details></article>")
(new/'calibration-review.html').write_text('<!doctype html><meta charset="utf-8"><title>Judge calibration review</title><style>body{font:16px system-ui;max-width:1000px;margin:32px auto;padding:20px;background:#f4f6f8;color:#172331}article{background:white;padding:24px;margin:20px 0;border:1px solid #ccd;border-radius:10px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:15px system-ui}summary{cursor:pointer}</style><h1>Judge calibration: focused review</h1><p>Agreement: '+str(summary['baseline_agreement'])+'/36 → '+str(summary['revised_agreement'])+'/36. Existing human decisions remain unchanged. This page is read-only; it shows every changed grade or remaining disagreement.</p>'+''.join(cards))
print(json.dumps({k:v for k,v in summary.items() if k!='rows'},indent=2))
