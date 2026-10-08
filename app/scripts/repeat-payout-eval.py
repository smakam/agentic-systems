"""Full-agent repeat of payout cases, GPT-5.4 only; original runner and agent unchanged."""
import asyncio
from argparse import Namespace
from marketplace import eval_compare
# Filter only the candidate set; do not modify prompts, settings, tools or fixtures.
eval_compare.MODELS=[m for m in eval_compare.MODELS if m['alias']=='eval-54']
asyncio.run(eval_compare.main(Namespace(output='/results/payout-full-agent-repeat-2026-09-29',dry_run=False,cases='16,17',gold_file=None,reuse_from=None,collect_only=True,grade_only=False,repeats=2,budget=3.5)))
