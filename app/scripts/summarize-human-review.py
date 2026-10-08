"""Summarize exported human grades without changing them or the automated baseline."""
import json,sys,hashlib,shutil
from pathlib import Path
from collections import Counter
results_path,review_path=map(Path,sys.argv[1:3]);data=json.loads(results_path.read_text());human=json.loads(review_path.read_text());reviews=human['reviews'];records=data['results']
assert human['experiment']==data['experiment'],'Wrong experiment'
assert set(reviews)=={r['key'] for r in records},'Missing or extra review keys'
values={'incorrect':0,'partially_correct':1,'correct':2};labels={0:'Incorrect',1:'Partial',2:'Correct'}
assert all(h.get('decision') in values for h in reviews.values()),'Incomplete grades'
out=results_path.parent
source=out/'human-review.json'
if source.exists() and source.read_bytes()!=review_path.read_bytes():
 prior=json.loads(source.read_text());stamp=prior['reviewed_at'].replace(':','-')
 archive=out/('human-review-'+stamp+'.json')
 if archive.exists() and archive.read_bytes()!=source.read_bytes():raise RuntimeError('Archive conflict')
 archive.write_bytes(source.read_bytes())
if source.resolve()!=review_path.resolve():shutil.copyfile(review_path,source)
summary=[];disagreements=[];inconsistencies=[]
for model in sorted({r['model'] for r in records}):
 rs=[r for r in records if r['model']==model];hc=Counter(reviews[r['key']]['decision'] for r in rs);jc=Counter(r['judge']['grade']['correctness'] for r in rs)
 summary.append({'model':model,'cases':len(rs),'human':dict(hc),'judge':dict(jc),'exact_grade_agreement':sum(values[reviews[r['key']]['decision']]==r['judge']['grade']['correctness'] for r in rs)})
for r in records:
 h=reviews[r['key']];j=r['judge']['grade']['correctness'];same=values[h['decision']]==j
 if not same:disagreements.append({'case':r['case']['id'],'model':r['model'],'human':h['decision'],'judge':labels[j],'agreement_selection':h.get('judge_agreement'),'notes':h.get('notes','')})
 if h.get('judge_agreement')=='yes' and not same:inconsistencies.append(r['key'])
receipt={'experiment':data['experiment'],'reviewed_at':human['reviewed_at'],'human_review_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'results_sha256':hashlib.sha256(results_path.read_bytes()).hexdigest(),'summary':summary,'disagreements':disagreements,'agreement_field_conflicts':inconsistencies,'method':'Count decision as the human answer grade. Do not infer grades from notes or judge_agreement. One scenario per model; multi-turn cases count once.'}
(out/'human-summary.json').write_text(json.dumps(receipt,indent=2)+'\n')
lines=['# Human and Claude evaluation summary','',f"Review: {human['reviewed_at']}. Experiment: {data['experiment']}.",'','All 36 scenario answers have human grades: 18 cases for each model, including two multi-turn cases. Counts below preserve the exported decisions exactly; no adjudication or model rerun was performed.','','| Model | Human correct | Human partial | Human incorrect | Claude correct | Claude partial | Claude incorrect | Exact grade agreement |','|---|---:|---:|---:|---:|---:|---:|---:|']
for s in summary:
 h,j=s['human'],s['judge'];name='GPT-5 nano' if 'nano' in s['model'] else 'GPT-5.4';lines.append(f"| {name} | {h.get('correct',0)} | {h.get('partially_correct',0)} | {h.get('incorrect',0)} | {j.get(2,0)} | {j.get(1,0)} | {j.get(0,0)} | {s['exact_grade_agreement']}/18 |")
lines+=['','Human fully-correct rates: '+ '; '.join(f"{s['model']}: {s['human'].get('correct',0)}/{s['cases']} ({100*s['human'].get('correct',0)/s['cases']:.1f}%)" for s in summary)+'. This is a descriptive comparison on selected synthetic cases with one run per model, not a general model ranking.','','## Grade disagreements','',f"There are {len(disagreements)} grade differences; {len(records)-len(disagreements)}/{len(records)} grades match exactly ({100*(len(records)-len(disagreements))/len(records):.1f}%). Differences are retained, not automatically adjudicated.",'','| Case | Model | Human | Claude | Exported “agree with judge” |','|---|---|---|---|---|']
for d in disagreements:lines.append(f"| {d['case']} | {'nano' if 'nano' in d['model'] else 'GPT-5.4'} | {d['human'].replace('_',' ')} | {d['judge']} | {d['agreement_selection']} |")
missing=[r['key'] for r in records if any(not reviews[r['key']].get(k) for k in ('decision','judge_agreement','checks_agreement'))]
lines+=['','## Review consistency checks','',
 ('Agreement-field conflicts: '+', '.join(inconsistencies)) if inconsistencies else 'No entries say “agree with judge: yes” while assigning a different answer grade.',
 ('Missing selections: '+', '.join(missing)) if missing else 'All three selections are filled for all 36 answers.',
 'Remaining differences marked no or uncertain are legitimate review disagreements, not missing data.',
 '', '## Human notes (verbatim)']

for r in records:
 note=reviews[r['key']].get('notes','').strip()
 if note:lines+=['',f"### Case {r['case']['id']} / {'nano' if 'nano' in r['model'] else 'GPT-5.4'}",'',note]
lines+=['','## Interpretation and next steps','','- Case 8 notes call for open clarification without unsupported seller guesses; nano should avoid the product dump and demo-clock detail.','- The case 14 nano note identifies omission of the provider-timeout cause, and the revised exported answer grade is partially correct.','- Cases 11 and 14 are candidates for reviewing overly strict gold criteria, as discussed. Any rubric change should be versioned and applied consistently, not used to rewrite the saved baseline silently.','- After resolving any flagged review ambiguities, investigate confirmed failures using tool/evidence traces and controlled correct-evidence tests. These grades alone do not isolate model versus context causes.','','## Sources and boundaries','','- [Original human export](human-review.json): authoritative for the human decisions and notes; copied byte-for-byte from Downloads.','- [Saved evaluation results](results.json): authoritative for model outputs, evidence, and original Claude grades.','- [Machine-readable summary and source hashes](human-summary.json).','- Claude grades include direct Anthropic and OpenRouter routes with the same configured Claude model/rubric; provenance is retained in results.json.','- Human review followed viewing judge scores and discussing selected cases; agreement is not a blinded, independent judge-validation measurement.','- No human scores were uploaded to Langfuse in this summary step.']
(out/'HUMAN-REVIEW-SUMMARY.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'reviewed':len(reviews),'summary':summary,'disagreements':len(disagreements),'agreement_field_conflicts':len(inconsistencies)},indent=2))
