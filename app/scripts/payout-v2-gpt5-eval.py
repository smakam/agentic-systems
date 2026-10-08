"""Versioned seed-only variation: 23h and 24h30m, full GPT-5 agent."""
import asyncio,os,sys
from argparse import Namespace
from marketplace import eval_compare
os.environ['EVAL_CASES']='/eval/payout-v2/cases.json'
eval_compare.MODELS=[{'alias':'eval-5','model':'gpt-5','input_rate':1.25,'output_rate':10.,'budget':1.0}]
original_manifest=eval_compare.manifest
def manifest():
    return {**original_manifest(),'candidate_model':'gpt-5','pricing_sources':['https://developers.openai.com/api/docs/models/gpt-5'],'pricing_checked':'2026-09-29','fixture_version':'payout-fixtures-v2','fixture_override':'eval/payout-v2/eval_fixtures.py','case_16_elapsed_hours':23,'case_17_elapsed_hours':24.5}
eval_compare.manifest=manifest
dry='--dry-run' in sys.argv
asyncio.run(eval_compare.main(Namespace(output='/results/payout-v2-validation-2026-09-29' if dry else '/results/payout-v2-gpt5-2026-09-29',dry_run=dry,cases='16,17',gold_file=None,reuse_from=None,collect_only=True,grade_only=False,repeats=3,budget=3.5)))
