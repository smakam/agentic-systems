"""Frozen core18 payout-v2 comparison; candidate collection only, no judge."""
import asyncio,json,os,sys
from argparse import Namespace
from pathlib import Path
from marketplace import eval_compare
os.environ['EVAL_CASES']='/eval/cases.json'
original=eval_compare.manifest
ids=json.loads(Path('/eval/core-18.json').read_text())['case_ids']
def manifest():
 return {**original(),'fixture_version':'payout-fixtures-v2','grading_plan':'assistant review; no paid judge','pricing_sources':['https://developers.openai.com/api/docs/models/gpt-5','https://developers.openai.com/api/docs/models/gpt-5-nano']}
eval_compare.manifest=manifest
async def run():
 for alias,model,ir,orr,cases,folder in [('eval-nano','gpt-5-nano-2025-08-07',.05,.4,'17','nano-v2-case17-2026-09-29'),('eval-5','gpt-5',1.25,10.,','.join(ids),'core18-gpt5-v2-2026-09-29')]:
  if '--gpt5-only' in sys.argv and alias=='eval-nano':continue
  eval_compare.MODELS=[{'alias':alias,'model':model,'input_rate':ir,'output_rate':orr,'budget':1.0}]
  await eval_compare.main(Namespace(output='/results/'+folder,dry_run=False,cases=cases,gold_file='/eval/gold-v3.json',reuse_from=None,collect_only=True,grade_only=False,repeats=1,budget=5.))
  # Closing pooled PostgreSQL connections releases session advisory locks.
  eval_compare.engine.dispose()
asyncio.run(run())
