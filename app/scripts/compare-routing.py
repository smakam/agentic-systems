"""Compare immutable offline routing replays; no model calls."""
import json
from pathlib import Path
APP=Path(__file__).resolve().parents[1]
v1=APP/'results/routing-offline-v1-2026-09-29'
v2=APP/'results/routing-offline-v2-2026-09-29'
a=json.loads((v1/'summary.json').read_text());b=json.loads((v2/'summary.json').read_text())
x={r['case_id']:r for r in a['rows']};y={r['case_id']:r for r in b['rows']};assert x.keys()==y.keys()
for cid in x:
 assert x[cid]['alternatives']==y[cid]['alternatives']
 assert x[cid]['classification']['question']==y[cid]['classification']['question']
changes=[]
for cid in x:
 p=x[cid];q=y[cid]
 if p['classification']['selected_alias']!=q['classification']['selected_alias']:
  changes.append({'case':cid,'before':p['classification']['selected_alias'],'after':q['classification']['selected_alias'],
    'grade_before':p['human_grade'],'grade_after':q['human_grade'],'reason':q['classification']['reason']})
report={'v1':{k:v for k,v in a.items() if k!='rows'},'v2':{k:v for k,v in b.items() if k!='rows'},'changed_selections':changes}
(v2/'comparison-v1-v2.json').write_text(json.dumps(report,indent=2))
lines=['# Richer-context routing: v1 versus v2','',
 'Same nano classifier, model mapping and opening questions. V2 adds detailed task rules and the full generic application ontology. Both replay whole saved sessions using unchanged human grades. This is our custom classifier through LiteLLM, not the native AutoRouter.','',
 '| Policy | Correct | Partial | Incorrect | Estimated cost |','|---|---:|---:|---:|---:|']
for name,s in [('Always nano',b['always_nano']),('Always GPT-5.4',b['always_54']),('Routing v1',a['routed']),('Routing v2',b['routed'])]:
 lines.append(f"| {name} | {s['correct']} | {s['partial']} | {s['incorrect']} | ${s['estimated_cost_usd']:.5f} |")
lines+=['',f"V2 selection: {b['selection_counts']}. New classifier cost estimate: ${b['classifier_spend_estimate_usd']:.6f}. Table costs replay historical candidate estimates plus classifier overhead; they are not new spending. No new answers or judge grades generated.",'','## Changed selections','','| Case | Before | After | Human grade before | Human grade after |','|---|---|---|---|---|']
for c in changes:lines.append('| '+' | '.join(c[k] for k in ['case','before','after','grade_before','grade_after'])+' |')
lines+=['','## Limits and lessons','',
 'Difficulty labels are not ground truth about model success. Cases 16 and 17 ask the same payout eligibility question for different order IDs. V1 classified them differently. V2 should be inspected for consistency; even a reasonable complexity label can select a model whose saved answer is worse.',
 'V2 was designed after reviewing known v1 errors. No gold, grades, case answers or follow-up questions were sent to the classifier, but results on the same cases are tuning evidence, not held-out validation. One classifier sample per case means stochastic variation may also contribute to changes. Richer context is not isolated from the revised decision rules.',
 'Session pinning still cannot anticipate unseen follow-ups. Costs use historical uncached list rates and exclude embedding, judge and hosting costs. Caching and live end-to-end latency are untested. Candidate quality is one previously observed result per model/case.',
 'All paired questions, alternative grades and costs were checked identical across replays. Prompt, raw responses, usage, model IDs and source snapshots are retained in this directory.']
(v2/'COMPARISON.md').write_text('\n'.join(lines)+'\n')
print(json.dumps(report,indent=2))
