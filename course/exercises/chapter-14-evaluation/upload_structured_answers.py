"""Import five supplied JSON answers. Native Langfuse rules compute the grades."""
import argparse,json,uuid
from evaluation_helpers import load_cases,langfuse_client,save
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--publish',action='store_true');p.add_argument('--run-name',default='chapter14-learner-structured-five');p.add_argument('--dataset',default='chapter14-learner-structured-v1');p.add_argument('--output',default='/results/chapter-14/structured-import.json');a=p.parse_args()
cases=load_cases('structured-five.json')
if not a.publish:print(json.dumps({'cases':[c['case_id'] for c in cases],'model_calls':0,'published':False}));raise SystemExit(0)
lf=langfuse_client();lf.create_dataset(name=a.dataset,description='Five actual recorded agent JSON answers; independent expected fields. Native code evaluator grades the answer observations.')
for c in cases:
 lf.create_dataset_item(dataset_name=a.dataset,id=str(uuid.uuid5(uuid.NAMESPACE_URL,a.dataset+':'+c['case_id'])),input={'case_id':c['case_id'],'question':c['question']},expected_output=c['expected'],metadata={'case_id':c['case_id'],'authored_output':False})
records={c['case_id']:c for c in cases}
def task(*,item,**kwargs):
 c=records[item.input['case_id']]
 lf.update_current_span(name='chapter14-structured-answer',input=c['question'],metadata={'expected_output':c['expected'],'case_id':c['case_id'],'authored_output':False,'original_trace_id':c['original_trace_id'],'reference_source':'independent database query before and after original run'})
 return c['output']
r=lf.run_experiment(name='Chapter14 learner structured answers',run_name=a.run_name,data=lf.get_dataset(a.dataset).items,task=task,max_concurrency=1,description='Reuses five supplied actual outputs; no new model calls. Native evaluator rule must be configured separately.')
lf.flush();result={'items':len(r.item_results),'dataset':a.dataset,'run_name':r.run_name,'url':r.dataset_run_url.replace('http://langfuse-web:3000','http://localhost:3000'),'model_calls':0,'grading':'native rule executes asynchronously, not in this script'};save(a.output,result);print(json.dumps(result))
