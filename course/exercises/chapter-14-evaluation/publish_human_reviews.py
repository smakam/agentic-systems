"""Validate and optionally publish five learner-written grades. No model calls."""
import argparse,json
from evaluation_helpers import load_cases,validate_grade,publish_grades,save
p=argparse.ArgumentParser(description=__doc__);p.add_argument('reviews');p.add_argument('--publish',action='store_true');p.add_argument('--run-name',default='chapter14-human-five');p.add_argument('--output',default='/results/chapter-14/human-review.json');a=p.parse_args()
cases=load_cases('human-five.json');reviews=json.load(open(a.reviews))
if set(reviews)!=set(c['case_id'] for c in cases):raise SystemExit('Provide exactly one review for each of the five supplied cases')
for grade in reviews.values():validate_grade(grade)
result={'grading_source':'human','reviews':reviews,'model_calls':0}
if a.publish:result['langfuse']=publish_grades(cases,reviews,'human',a.run_name)
save(a.output,result);print(json.dumps({'validated':5,'model_calls':0,'output':a.output,'langfuse':result.get('langfuse')}))
