"""Publish saved results with Langfuse's native v4 experiment context. No model calls."""
import argparse,json,uuid
from pathlib import Path
from datetime import datetime,timezone
from marketplace.agent import lf
from langfuse.experiment import Evaluation
p=argparse.ArgumentParser();p.add_argument('results');p.add_argument('--preview',action='store_true');p.add_argument('--dataset',default='marketplace-30-v1');p.add_argument('--human-review');p.add_argument('--run-suffix',default='');args=p.parse_args()
path=Path(args.results);data=json.loads(path.read_text())
if not args.preview and data['status']!='automated_complete_human_review_pending':raise RuntimeError('Wait for completed automated batch')
reviews=json.loads(Path(args.human_review).read_text()) if args.human_review else None
human_values={'incorrect':0,'partially_correct':1,'correct':2}
if reviews:
    assert set(reviews['reviews'])=={r['key'] for r in data['results']}, 'Human review keys do not match'
    assert all(v['decision'] in human_values for v in reviews['reviews'].values())
    assert all(reviews['experiment'] in r.get('reused_from','') for r in data['results']), 'Human review source differs'
dataset_name=args.dataset
if any(isinstance(r['case']['gold'],dict) for r in data['results']) and dataset_name=='marketplace-30-v1':
    raise RuntimeError('Use a versioned dataset to preserve original gold')
lf.create_dataset(name=dataset_name)
for case in json.loads((path.parent/'cases.json').read_text()):
    lf.create_dataset_item(dataset_name=dataset_name,id=str(uuid.uuid5(uuid.NAMESPACE_URL,dataset_name+case['id'])),input={'case_id':case['id'],'case':case},expected_output=case)
dataset=lf.get_dataset(dataset_name)
outputs=[]
for model in sorted({r['model'] for r in data['results']}):
    records={r['case']['id']:r for r in data['results'] if r['model']==model and r['status']=='complete'}
    if args.preview:records={k:v for k,v in records.items() if k=='01'}
    items=[i for i in dataset.items if i.input['case_id'] in records]
    if not items:continue
    def task(*,item,**kwargs):
        record=records[item.input['case_id']]
        return {'answer_turns':[{'question':t['question'],'answer':t['run']['answer']} for t in record['turns']],
                'original_trace_ids':[t['run']['metrics'].get('trace_id') for t in record['turns']],
                'judge_assessment':record['judge'].get('grade'),'human_review':reviews['reviews'][record['key']] if reviews else None,
                'source_record':record['key'],'judge_route':record['judge'].get('judge_route'),'judge_rubric':record['judge'].get('rubric_version'),'execution':'import of saved candidate output; no new model calls'}
    def evaluator(*,input,output,**kwargs):
        record=records[input['case_id']];grade=record['judge'].get('grade')
        scores=[]
        if reviews:
            human=reviews['reviews'][record['key']]
            value=human_values[human['decision']]
            scores.append(Evaluation(name='human_correctness',value=value,comment='Original human assessment, unchanged. '+human.get('notes','')))
            if grade:scores.append(Evaluation(name='judge_human_agreement',value=value==grade['correctness'],data_type='BOOLEAN'))
            agreement=human.get('checks_agreement')
            if agreement in ('yes','no'):scores.append(Evaluation(name='human_structured_checks_valid',value=agreement=='yes',data_type='BOOLEAN'))
        if grade:scores.append(Evaluation(name='judge_correctness_provisional',value=grade['correctness'],comment=grade['rationale']))
        for idx,t in enumerate(record['turns']):
            for name,value in t['deterministic']['checks'].items():
                if value is not None:scores.append(Evaluation(name=f'turn{idx+1}_{name}',value=value,data_type='BOOLEAN'))
        scores.append(Evaluation(name='candidate_estimated_usd',value=sum(t['run']['metrics']['estimated_model_cost_usd'] for t in record['turns'])))
        return scores
    name=data['experiment']+'-native-'+('preview-' if args.preview else '')+model+args.run_suffix
    result=lf.run_experiment(name=name,run_name=name,data=items,task=task,evaluators=[evaluator],max_concurrency=1,
        description='Imported saved answers and versioned Claude grades. '+('Original human assessments included unchanged; agreement compares them with this judge version. ' if reviews else 'Human review pending. ')+'See original trace IDs for model/tool execution; no new model calls.',
        metadata={'source_experiment':data['experiment'],'candidate_model':model,'judge_model':'claude-opus-5-5','review_status':'original_human_review_included' if reviews else 'pending','human_review_source':reviews['experiment'] if reviews else None,'judge_rubric':data['manifest']['judge_rubric'],'dataset':dataset_name,'no_new_model_calls':'true'})
    outputs.append({'model':model,'items':len(result.item_results),'experiment_id':result.experiment_id,'run_name':result.run_name,'url':result.dataset_run_url})
lf.flush()
(path.parent/('langfuse-preview.json' if args.preview else 'langfuse-experiments.json')).write_text(json.dumps(outputs,indent=2,default=str))
print(json.dumps(outputs,default=str))
