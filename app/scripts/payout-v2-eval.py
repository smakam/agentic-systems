"""Versioned seed-only variation: 23h and 24h30m, full GPT-5.4 agent."""
import asyncio,os,sys
from argparse import Namespace
from marketplace import eval_compare
os.environ['EVAL_CASES']='/eval/payout-v2/cases.json'
eval_compare.MODELS=[m for m in eval_compare.MODELS if m['alias']=='eval-54']
original_manifest=eval_compare.manifest
def manifest():
    return {**original_manifest(),'fixture_version':'payout-fixtures-v2','fixture_override':'eval/payout-v2/eval_fixtures.py','case_16_elapsed_hours':23,'case_17_elapsed_hours':24.5}
eval_compare.manifest=manifest
dry='--dry-run' in sys.argv
asyncio.run(eval_compare.main(Namespace(output='/results/payout-v2-validation-2026-09-29' if dry else '/results/payout-v2-gpt54-2026-09-29',dry_run=dry,cases='16,17',gold_file=None,reuse_from=None,collect_only=True,grade_only=False,repeats=2,budget=3.5)))
