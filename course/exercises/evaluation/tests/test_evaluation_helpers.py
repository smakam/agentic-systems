import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from evaluation_helpers import load_cases,validate_grade
from run_claude_demo import blind_payload
class GradingContractTests(unittest.TestCase):
 def test_blind_payload_excludes_candidate_and_human_grades(self):
  c=load_cases('instructor-five.json')[0]
  payload=blind_payload({**c,'human_score':2,'model':'candidate','judge_grade':2})
  self.assertEqual(set(payload),{'question_sequence','gold_requirements','candidate_answers','retrieved_evidence'})
 def test_bool_and_out_of_range_scores_are_rejected(self):
  for value in (True,-1,3,'2'):
   with self.assertRaises(ValueError):validate_grade({'correctness':value,'rationale':'reason'})
 def test_missing_reason_is_not_a_completed_grade(self):
  with self.assertRaises(ValueError):validate_grade({'correctness':2,'rationale':''})
 def test_structured_fixture_has_real_answers_and_independent_references(self):
  cases=load_cases('structured-five.json')
  for c in cases:
   self.assertEqual(c['output']['shipment_status'],c['expected']['shipment_status'])
   self.assertEqual(c['output']['quantity'],c['expected']['quantity'])
   self.assertTrue(c['original_trace_id'])
   self.assertTrue(c['output']['evidence'])
if __name__=='__main__':unittest.main()
