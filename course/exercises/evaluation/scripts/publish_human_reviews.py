"""Validate and optionally publish five learner-written grades. No model calls."""
import argparse,json
from evaluation_helpers import load_cases,validate_grade,publish_grades,save,grades_from_submission
p=argparse.ArgumentParser(description=__doc__);p.add_argument('reviews');p.add_argument('--publish',action='store_true');p.add_argument('--run-name',default='chapter14-human-five');p.add_argument('--output',default='/results/chapter-14/human-review.json');a=p.parse_args()
cases=load_cases('human-five.json');reviews=grades_from_submission(json.load(open(a.reviews)),cases)
result={'grading_source':'human','reviews':reviews,'model_calls':0}
if a.publish:result['langfuse']=publish_grades(cases,reviews,'human',a.run_name,{'answer_model':'gpt-5-nano-2025-08-07','judge_model':'none (human review)','grading_method':'learner human grades imported','model_summary':'Answer model: GPT-5 nano (2025-08-07). Grader: human reviewer.'})
save(a.output,result);print(json.dumps({'validated':5,'model_calls':0,'output':a.output,'langfuse':result.get('langfuse')}))
