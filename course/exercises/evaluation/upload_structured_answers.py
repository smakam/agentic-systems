"""Import supplied JSON answers (three by default). Native Langfuse rules compute the grades."""
import argparse,json,uuid
from evaluation_helpers import load_cases,langfuse_client,save
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--publish',action='store_true');p.add_argument('--limit',type=int,choices=range(1,6));p.add_argument('--fixture',choices=['structured-three.json','structured-five.json'],default='structured-three.json');p.add_argument('--run-name',default='chapter14-learner-structured-three');p.add_argument('--dataset',default='chapter14-learner-structured-three-v1');p.add_argument('--output',default='/results/chapter-14/structured-import.json');a=p.parse_args()
cases=load_cases(a.fixture,expected_count=3 if a.fixture=='structured-three.json' else 5)[:a.limit]
if not a.publish:print(json.dumps({'cases':[c['case_id'] for c in cases],'model_calls':0,'published':False}));raise SystemExit(0)
provenance={'answer_model':'gpt-5.4-2026-03-05','judge_model':'none (code evaluator)','grading_method':'native TypeScript in Langfuse worker','model_summary':'Answer model: GPT-5.4 (2026-03-05). Grader: native TypeScript; no judge model.'}
lf=langfuse_client();lf.create_dataset(name=a.dataset,description=f'{len(cases)} actual recorded agent JSON answers; independent expected fields. Native code evaluator grades the answer observations. '+provenance['model_summary'])
for c in cases:
 lf.create_dataset_item(dataset_name=a.dataset,id=str(uuid.uuid5(uuid.NAMESPACE_URL,a.dataset+':'+c['case_id'])),input={'case_id':c['case_id'],'question':c['question']},expected_output=c['expected'],metadata={**provenance,'case_id':c['case_id'],'authored_output':False})
records={c['case_id']:c for c in cases}
def task(*,item,**kwargs):
 c=records[item.input['case_id']]
 lf.update_current_span(name='chapter14-structured-answer',input=c['question'],metadata={**provenance,'expected_output':c['expected'],'case_id':c['case_id'],'authored_output':False,'original_trace_id':c['original_trace_id'],'reference_source':'independent database query before and after original run'})
 return c['output']
r=lf.run_experiment(name='Chapter14 supplied structured answers',run_name=a.run_name,data=lf.get_dataset(a.dataset).items,task=task,max_concurrency=1,description=f'Reuses {len(cases)} supplied actual outputs; no new model calls. '+provenance['model_summary'],metadata=provenance)
lf.flush();result={'items':len(r.item_results),'dataset':a.dataset,'run_name':r.run_name,'url':r.dataset_run_url.replace('http://langfuse-web:3000','http://localhost:3000'),'model_calls':0,'grading':'native rule executes asynchronously, not in this script'};save(a.output,result);print(json.dumps(result))
