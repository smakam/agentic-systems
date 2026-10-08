import json,math
from pathlib import Path
from collections import Counter
app=Path(__file__).resolve().parents[1];out=app/'results/semantic-scenarios-v2-2026-09-30';n=json.loads((out/'native.json').read_text());old=json.loads((app/'results/routing-classifiers-2026-09-30/native.json').read_text());cfg=json.loads((out/'frozen-config.json').read_text());base=json.loads((app/'eval/routing-final-v1/classifiers.json').read_text());vectors={}
for record in n['embedding_records']:
 for text,v in zip(record['inputs'],record['vectors']):vectors[text]=v
pairs={}
for r in json.loads((app/'results/core18-gpt5-v2-2026-09-29/comparison.json').read_text())['rows']:pairs.setdefault(r['case'],{})[r['model']]=r
olddec={d['case']:d for d in old['decisions'] if d['method']=='semantic'}
def cosine(a,b):return sum(x*y for x,y in zip(a,b))/math.sqrt(sum(x*x for x in a)*sum(x*x for x in b))
def nearest(q,config):return sorted([{'tier':rule['tier'],'text':text,'similarity':cosine(vectors[q],vectors[text])} for rule in config['semantic_rules'] for text in rule['keywords']],key=lambda x:x['similarity'],reverse=True)[:3]
rows=[]
for d in n['decisions']:
 cid=d['case'];q=pairs[cid]['eval-nano']['turns'][0]['question'];rows.append({'case':cid,'question':q,'old':olddec[cid],'new':d,'old_nearest':nearest(q,base),'new_nearest':nearest(q,cfg),'old_grade':pairs[cid][olddec[cid]['selected']]['review']['grade'],'new_grade':pairs[cid][d['selected']]['review']['grade']})
g=Counter(r['new_grade'] for r in rows);cost=sum(pairs[d['case']][d['selected']]['cost'] for d in n['decisions']);overhead=sum(c['estimated_cost'] for c in n['embedding_calls']);summary={'grades':dict(g),'selections':dict(Counter(d['selected'] for d in n['decisions'])),'fallbacks':sum(d['cause']=='no_match_heuristic' for d in n['decisions']),'embedding_cost_usd':overhead,'replay_full_price_usd':cost+overhead,'rows':rows}
(out/'analysis.json').write_text(json.dumps(summary,indent=2)+'\n')
print({k:v for k,v in summary.items() if k!='rows'})
for r in rows:
 if r['old']['cause']=='no_match_heuristic' or r['old']['selected']!=r['new']['selected']:
  print(r['case'],r['question'],'OLD',r['old_nearest'][0]['similarity'],'NEW',r['new_nearest'][0]['similarity'],r['new']['selected'],r['new']['cause'],r['old_grade'],r['new_grade']);print('nearest',r['new_nearest'][0]['text'])
