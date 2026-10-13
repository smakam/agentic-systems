"""Shared I/O and result publication. No model calls in this module."""
import json, os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
LABELS = {0: 'incorrect', 1: 'partial', 2: 'correct'}
def load_cases(name, expected_count=5):
    data = json.loads((ROOT / 'fixtures' / name).read_text())
    cases = data['cases']
    ids = [c['case_id'] for c in cases]
    if len(ids) != expected_count or len(set(ids)) != expected_count:
        raise ValueError(f'Exactly {expected_count} unique cases are required')
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

def publish_grades(cases, grades, method, run_name, provenance=None):
    provenance = provenance or {}
    from langfuse.experiment import Evaluation
    import uuid
    lf = langfuse_client()
    dataset_name = 'chapter14-' + method + '-v1'
    lf.create_dataset(name=dataset_name, description='Five supplied recorded marketplace answers; grading source: '+method+'. '+provenance.get('model_summary',''))
    for c in cases:
        lf.create_dataset_item(dataset_name=dataset_name,
            id=str(uuid.uuid5(uuid.NAMESPACE_URL,dataset_name+':'+c['case_id'])),
            input={'case_id':c['case_id'],'questions':c['questions']},
            expected_output=c['gold'],metadata={**provenance,'source':'supplied saved answer','case_id':c['case_id']})
    records={c['case_id']:c for c in cases}
    def task(*, item, **kwargs):
        c=records[item.input['case_id']]
        lf.update_current_span(name='chapter14-'+method+'-answer',metadata={**provenance,'original_trace_ids':c['original_trace_ids'],'grading_source':method,'no_new_candidate_calls':True})
        return c['answers']
    def evaluator(*, input, output, **kwargs):
        g=grades[input['case_id']]
        return [Evaluation(name=method+'_correctness',value=g['correctness'],comment=g['rationale'])]
    result=lf.run_experiment(name='Chapter14 '+method+' review',run_name=run_name,
        data=lf.get_dataset(dataset_name).items,task=task,evaluators=[evaluator],max_concurrency=1,
        description='Supplied candidate outputs. Grading occurred externally; this publication does not call a model. '+provenance.get('model_summary',''),
        metadata={**provenance,'grading_source':method,'candidate_generation':'reused supplied outputs'})
    lf.flush()
    return {'dataset':dataset_name,'run_name':result.run_name,'url':result.dataset_run_url.replace('http://langfuse-web:3000','http://localhost:3000')}

def grades_from_submission(submission, cases):
    expected={c['case_id']:c for c in cases}
    if 'cases' not in submission:
        reviews=submission
    else:
        entries=submission['cases']
        ids=[e['case_id'] for e in entries]
        if len(ids)!=len(expected) or len(set(ids))!=len(ids) or set(ids)!=set(expected):
            raise ValueError('Provide exactly one review for every supplied case')
        reviews={}
        for e in entries:
            c=expected[e['case_id']]
            if e.get('questions')!=c['questions'] or e.get('golden_facts')!=c['gold'] or e.get('model_answers')!=c['answers']:
                raise ValueError('Only score and reason may be changed in the supplied worksheet')
            reviews[e['case_id']]={'correctness':e.get('score'),'rationale':e.get('reason')}
    if set(reviews)!=set(expected):raise ValueError('Provide exactly one review for every supplied case')
    return {k:validate_grade(v) for k,v in reviews.items()}
