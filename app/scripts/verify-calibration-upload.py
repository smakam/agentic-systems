import json
from pathlib import Path
from datetime import datetime,timezone
from marketplace.agent import lf
p=Path('/results/calibration-v3-2026-09-29')
local={r['key']:r for r in json.loads((p/'results.json').read_text())['results']}
human=json.loads(Path('/results/core18-2026-09-28-03/human-review.json').read_text())['reviews']
values={'correct':2,'partially_correct':1,'incorrect':0};summary=[]
for ex in json.loads((p/'langfuse-experiments.json').read_text()):
 response=lf.api.experiments.list_items(from_start_time=datetime(2026,9,29,tzinfo=timezone.utc),experiment_id=ex['experiment_id'],fields='core,io,scores',limit=100)
 assert len(response.data)==18
 seen=set();agreement=0
 for item in response.data:
  d=item.model_dump(mode='json');out=json.loads(d['output']);key=out['source_record'];assert key not in seen;seen.add(key)
  r=local[key];assert out['answer_turns']==[{'question':t['question'],'answer':t['run']['answer']} for t in r['turns']]
  assert json.loads(d['expectedOutput'])==r['case']
  scores={s['name']:s['value'] for s in d['scores']}
  assert scores['judge_correctness_provisional']==r['judge']['grade']['correctness']
  assert scores['human_correctness']==values[human[key]['decision']]
  assert bool(scores['judge_human_agreement'])==(scores['human_correctness']==scores['judge_correctness_provisional'])
  agreement+=bool(scores['judge_human_agreement'])
 summary.append({'model':ex['model'],'experiment_id':ex['experiment_id'],'verified_items':len(seen),'verified_human_judge_agreements':agreement,'answers_gold_and_scores_verified':True})
assert sum(r['verified_human_judge_agreements'] for r in summary)==31
(p/'langfuse-verification.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary))
