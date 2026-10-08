import asyncio,json
from pathlib import Path
from argparse import Namespace
from openai.resources.chat.completions import AsyncCompletions
from marketplace import eval_compare
import os
OUT=Path('/results/payout-request-capture-2026-09-29');OUT.mkdir(exist_ok=True)
original=AsyncCompletions.create
count=0
async def capture(self,*args,**kwargs):
 global count
 count+=1;path=OUT/f'request-{count:02}.json'
 # Capture API payload only, no client auth headers or env.
 def convert(v):
  if hasattr(v,'model_dump'):return v.model_dump(exclude_none=True)
  if type(v).__name__ in ('NotGiven','Omit'):return None
  raise TypeError(type(v).__name__)
 path.write_text(json.dumps(kwargs,indent=2,default=convert))
 result=await original(self,*args,**kwargs)
 (OUT/f'response-{count:02}.json').write_text(result.model_dump_json(indent=2))
 return result
AsyncCompletions.create=capture
os.environ['EVAL_CASES']='/eval/payout-v2/cases.json'
eval_compare.MODELS=[m for m in eval_compare.MODELS if m['alias']=='eval-54']
asyncio.run(eval_compare.main(Namespace(output=str(OUT),dry_run=False,cases='17',gold_file=None,reuse_from=None,collect_only=True,grade_only=False,repeats=1,budget=3.5)))
