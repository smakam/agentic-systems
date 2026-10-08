"""Summarize frozen-draft reviewer ablation; no model calls."""
import json,html,re,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];B=ROOT/'results'
base=json.loads((B/'core18-history-v3-2026-10-01/results.json').read_text())
original=json.loads((B/'core18-history-v3-2026-10-01/manual-grades.json').read_text())
variants={name:json.loads((B/path/'results.json').read_text()) for name,path in [('nano reviewer','reviewer-nano-core18-2026-10-01'),('GPT-5.4 reviewer','reviewer-54-core18-2026-10-01')]}
grades={name:json.loads((B/path/'assistant-grades.json').read_text()) for name,path in [('nano reviewer','reviewer-nano-core18-2026-10-01'),('GPT-5.4 reviewer','reviewer-54-core18-2026-10-01')]}
ids=variants['nano reviewer']['cases'];assert all(len(s['results'])==18 and all(r['status']=='completed' and r['business_unchanged'] for r in s['results']) for s in variants.values())
out=B/'reviewer-ablation-core18-2026-10-01';out.mkdir(exist_ok=True)
def count(vals):
 c=collections.Counter(vals);return [c[x] for x in ['correct','partially_correct','incorrect']]
def baseline_cost(alias):return sum(t['run']['metrics']['estimated_model_cost_usd'] for r in base['results'] if r['key'].endswith(alias) for t in r['turns'])
nano_cost=baseline_cost('eval-nano');strong_cost=baseline_cost('eval-54');stats={}
for n,s in variants.items():
 stats[n]={'grades':count(g['final'] for g in grades[n].values()),'revision_requests':sum(r['correction_performed'] for r in s['results']),'reviewer_calls':sum(r['reviewer_metrics']['model_calls'] for r in s['results']),'correction_calls':sum(r['correction_metrics']['model_calls'] for r in s['results']),'incremental_uncached_usd':s['incremental_uncached_usd'],'assembled_total_usd':nano_cost+s['incremental_uncached_usd'],'savings_vs_gpt54_pct':100*(1-(nano_cost+s['incremental_uncached_usd'])/strong_cost),'unchanged_business':True}
summary={'nano_alone':{'grades':count(original[c+'-nano']['grade'] for c in ids),'historical_cost_usd':nano_cost},'gpt54_alone':{'grades':count(original[c+'-54']['grade'] for c in ids),'historical_cost_usd':strong_cost},'workflows':stats,'grading':'Independent provisional assistant; prior accepted adjudications preserved','method':'18 frozen cases / 20 saved generation turns. Final-turn review for two follow-up cases with frozen prior history. Eight rows reused per reviewer variant. No paid external judge.'}
(out/'summary.json').write_text(json.dumps(summary,indent=2))
def h(v):return html.escape(str(v))
parts=['<h1>Reviewer capability versus review pattern: core18</h1><p>'+h(summary['method'])+'</p><p>Expected references, model drafts, reviewer feedback, corrected text and independent grades remain separate. Reviewer approval is not correctness. Cost includes original nano generation plus review/correction; these are assembled uncached estimates, not fresh end-to-end measurements.</p><table><tr><th>Approach</th><th>Correct / partial / incorrect</th><th>Model cost USD</th></tr>']
for name,cost,gs in [('Nano alone',nano_cost,summary['nano_alone']['grades']),('Nano reviewer + correction',stats['nano reviewer']['assembled_total_usd'],stats['nano reviewer']['grades']),('GPT-5.4 reviewer + correction',stats['GPT-5.4 reviewer']['assembled_total_usd'],stats['GPT-5.4 reviewer']['grades']),('GPT-5.4 alone',strong_cost,summary['gpt54_alone']['grades'])]:parts.append('<tr><td>'+h(name)+'</td><td>'+h(gs)+'</td><td>'+h(round(cost,5))+'</td></tr>')
parts.append('</table>')
for c in ids:
 ref=next(r for r in base['results'] if r['key']=='1-'+c+'-eval-nano')
 parts.append('<h2>Case '+c+' — '+h(ref['case']['question'])+'</h2><h3>Expected reference</h3><pre>'+h(ref['case']['gold'])+'</pre><h3>Frozen Nano conversation</h3><pre>'+h(json.dumps([{'question':t['question'],'answer':t['run']['answer']} for t in ref['turns']],indent=2))+'</pre>')
 for n,s in variants.items():
  r=next(r for r in s['results'] if r['case_id']==c)
  parts.append('<h3>'+h(n)+' — final grade: '+h(grades[n][c]['final'])+'</h3><pre>'+h(r['answer'])+'</pre><details><summary>Reviewer feedback</summary><pre>'+h(json.dumps(r['review'],indent=2))+'</pre></details><p>'+h(grades[n][c]['reason'])+'</p><details><summary>Original review input, retrieved records, correction tools and usage</summary><pre>'+h(json.dumps(r,indent=2))+'</pre></details>')
  if grades[n][c].get('invalid_citations'):parts.append('<p>Unresolved citation references: '+h(grades[n][c]['invalid_citations'])+'</p>')
(out/'comparison.html').write_text('<!doctype html><meta charset="utf-8"><title>Reviewer ablation core18</title><style>body{font:16px system-ui;max-width:1100px;margin:40px auto;padding:20px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd;padding:10px;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f2f4f7;padding:16px}summary{cursor:pointer}</style>'+''.join(parts))
print(json.dumps(summary,indent=2))
