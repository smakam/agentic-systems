"""Combine saved candidate outputs, assistant grades, historical review and audits."""
import json,collections,html,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1];out=root/'results/core18-history-v3-2026-10-01'
def read(p):return json.loads(p.read_text())
new=read(out/'results.json');grades=read(out/'manual-grades.json');audit=read(out/'citation-audit.json')['rows']
original=read(root/'results/core18-2026-09-28-03/results.json');human=read(root/'results/core18-2026-09-28-03/human-review.json')['reviews']
accepted=read(root/'results/core18-gpt5-v2-2026-09-29/comparison.json')['rows']
recent=read(root/'results/catalog-v2-2026-10-01/assistant-review.json')['rows']
adjudication=read(out/'user-adjudication-v1.json') if (out/'user-adjudication-v1.json').exists() else {}
review_status='Assistant review; user-approved cases 23/24; other grades remain provisional' if adjudication else 'assistant provisional, not human accepted'
recentmap={r['case']:r for r in recent}
rows=[]
for r in new['results']:
 c=r['case']['id'];m='nano' if 'nano' in r['model'] else '54';key=c+'-'+m
 assert key in grades,key
 if m=='nano':
  prev=next(x for x in accepted if x['model']=='eval-nano' and x['case']==c);oldgrade=prev['review']['grade'];oldhash=prev['fixture_hash'];oldsource='core18-gpt5-v2-2026-09-29/comparison.json'
 else:
  prev=next(x for x in original['results'] if x['key']=='1-'+c+'-eval-54');oldgrade=human[prev['key']]['decision'];oldhash=prev['fixture_hash'];oldsource='core18-2026-09-28-03/human-review.json'
 ar=[a for a in audit if a['case']==c and a['model']==r['model']]
 row={'case':c,'model':m,'grade':grades[key]['grade'],'reason':grades[key]['reason'],'earlier_accepted_grade':oldgrade,'earlier_source':oldsource,'earlier_fixture_matches':oldhash==r['fixture_hash'],'recent_catalog_nano_grade':recentmap[c]['new_assistant_grade'] if m=='nano' else None,'turns':r['turns'],'citation_audit':ar,'reference':adjudication.get('reference_overrides',{}).get(c,r['case']['gold']),'original_reference':r['case']['gold']}
 rows.append(row)
summary={}
for m in ['nano','54']:
 rs=[r for r in rows if r['model']==m]
 summary[m]={'current':dict(collections.Counter(r['grade'] for r in rs)),'earlier_accepted':dict(collections.Counter(r['earlier_accepted_grade'] for r in rs)),'matching_fixtures':sum(r['earlier_fixture_matches'] for r in rs),'citations':sum(a['citation_count'] for r in rs for a in r['citation_audit']),'invalid_citations':sum(a['invalid_count'] for r in rs for a in r['citation_audit'])}
(out/'comparison.json').write_text(json.dumps({'review_status':review_status,'summary':summary,'rows':rows},indent=2)+'\n')
esc=lambda x:html.escape(str(x))
content=['<!doctype html><meta charset="utf-8"><title>Current history regression</title><style>body{font:16px/1.5 system-ui;max-width:1150px;margin:40px auto;padding:0 24px;color:#172331}table{border-collapse:collapse;width:100%;margin:20px 0}td,th{padding:10px;text-align:left;border-bottom:1px solid #ddd;vertical-align:top}pre{white-space:pre-wrap;background:#f4f6f8;padding:18px}details{margin:16px 0;border:1px solid #ddd;padding:16px}small{color:#526173}.incorrect{color:#ad2727}.partially_correct{color:#815a00}.correct{color:#216745}</style><h1>Nano vs GPT-5.4: current history baseline</h1><p>18 cases / 20 answers per model. Assistant-reviewed business correctness; no paid judge. Historical accepted grades are preserved. Cases 23/24 were upgraded by user-approved rubric clarification; other grades remain assistant provisional. No model rerun. Citation validity is separate from answer correctness.</p><p>Changes combine catalog, prompts and history retention. One sample per model/case; this is diagnostic, not a causal experiment or a general model ranking. Historical nano case 17 has a different timing fixture. Other grading differences can reflect reviewer judgment.</p><table><tr><th>Model</th><th>Earlier correct / partial / incorrect</th><th>Current correct / partial / incorrect</th><th>Valid citations / total</th></tr>']
def numbers(c):return ' / '.join(str(c.get(k,0)) for k in ['correct','partially_correct','incorrect'])
for m,s in summary.items():content.append(f'<tr><td>{"GPT-5 nano" if m=="nano" else "GPT-5.4"}</td><td>{numbers(s["earlier_accepted"])}</td><td>{numbers(s["current"])}</td><td>{s["citations"]-s["invalid_citations"]} / {s["citations"]}</td></tr>')
content.append('</table><p><a href="REPORT.md">Read methodology, reuse checks and limitations</a> · <a href="comparison.json">Full comparison data</a> · <a href="user-adjudication-v1.json">User adjudication</a></p>')
for c in sorted({r['case'] for r in rows}):
 pair=sorted([r for r in rows if r['case']==c],key=lambda r:r['model'],reverse=True)
 content.append(f'<details><summary><b>Case {c}</b> — '+ ' · '.join(('nano' if r['model']=='nano' else 'GPT-5.4')+': '+r['grade'].replace('_',' ') for r in pair)+'</summary>')
 content.append('<p><b>Reference requirements</b></p><pre>'+esc(json.dumps(pair[0]['reference'],indent=2) if not isinstance(pair[0]['reference'],str) else pair[0]['reference'])+'</pre>')
 for r in pair:
  content.append('<h3>'+('Nano' if r['model']=='nano' else 'GPT-5.4')+'</h3><p class="'+r['grade']+'">'+esc(r['grade'].replace('_',' '))+': '+esc(r['reason'])+'</p><small>Earlier: '+esc(r['earlier_accepted_grade'])+'; matching fixture: '+str(r['earlier_fixture_matches'])+'</small>')
  for t,a in zip(r['turns'],r['citation_audit']):content.append('<p><b>'+esc(t['question'])+'</b></p><pre>'+esc(t['run']['answer'])+'</pre><small>Citations: '+str(a['citation_count'])+'; invalid: '+str(a['invalid_count'])+'; no citations: '+str(a['no_citations'])+'</small>')
 content.append('</details>')
(out/'comparison.html').write_text('\n'.join(content))
print(json.dumps(summary,indent=2))
