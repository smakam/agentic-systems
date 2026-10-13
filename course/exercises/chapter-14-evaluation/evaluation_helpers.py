"""Shared I/O and result publication. No model calls in this module."""
import json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
LABELS = {0: 'incorrect', 1: 'partial', 2: 'correct'}
def load_cases(name):
    data = json.loads((ROOT / 'fixtures' / name).read_text())
    cases = data['cases']
    ids = [c['case_id'] for c in cases]
    if len(ids) != 5 or len(set(ids)) != 5:
        raise ValueError('Exactly five unique cases are required')
    return cases

def validate_grade(grade):
    if type(grade.get('correctness')) is not int or grade['correctness'] not in LABELS:
        raise ValueError('Correctness must be integer 0, 1 or 2')
    if not isinstance(grade.get('rationale'), str) or not grade['rationale'].strip():
        raise ValueError('A grading reason is required')
    return grade

def save(path, data):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))

def langfuse_client():
    from langfuse import Langfuse
    return Langfuse()

def publish_grades(cases, grades, method, run_name):
    from langfuse.experiment import Evaluation
    import uuid
    lf = langfuse_client()
    dataset_name = 'chapter14-' + method + '-v1'
    lf.create_dataset(name=dataset_name, description='Five supplied recorded marketplace answers; grading source: '+method)
    for c in cases:
        lf.create_dataset_item(dataset_name=dataset_name,
            id=str(uuid.uuid5(uuid.NAMESPACE_URL,dataset_name+':'+c['case_id'])),
            input={'case_id':c['case_id'],'questions':c['questions']},
            expected_output=c['gold'],metadata={'source':'supplied saved answer','case_id':c['case_id']})
    records={c['case_id']:c for c in cases}
    def task(*, item, **kwargs):
        c=records[item.input['case_id']]
        lf.update_current_span(name='chapter14-'+method+'-answer',metadata={'original_trace_ids':c['original_trace_ids'],'grading_source':method,'no_new_candidate_calls':True})
        return c['answers']
    def evaluator(*, input, output, **kwargs):
        g=grades[input['case_id']]
        return [Evaluation(name=method+'_correctness',value=g['correctness'],comment=g['rationale'])]
    result=lf.run_experiment(name='Chapter14 '+method+' review',run_name=run_name,
        data=lf.get_dataset(dataset_name).items,task=task,evaluators=[evaluator],max_concurrency=1,
        description='Supplied candidate outputs. Grading occurred externally; this publication does not call a model.',
        metadata={'grading_source':method,'candidate_generation':'reused supplied outputs'})
    lf.flush()
    return {'dataset':dataset_name,'run_name':result.run_name,'url':result.dataset_run_url.replace('http://langfuse-web:3000','http://localhost:3000')}
