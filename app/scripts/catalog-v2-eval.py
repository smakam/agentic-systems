"""Core18 nano regression collection, no paid judge; saves model-visible input captures."""
import asyncio, json
from argparse import Namespace
from pathlib import Path
from marketplace import eval_compare, agent

out=Path('/results/catalog-v2-2026-10-01')
out.mkdir(parents=True,exist_ok=True)
original=agent.BudgetHooks.on_llm_start
async def capture(self, context, instance, system_prompt, input_items):
    await original(self,context,instance,system_prompt,input_items)
    with (out/'model-inputs.jsonl').open('a') as f:
        f.write(json.dumps({'prompt_version':agent.PROMPT_VERSION,'instructions':system_prompt,
            'input_items':input_items},default=str)+'\n')
agent.BudgetHooks.on_llm_start=capture
# One baseline only. The existing harness reserves $2.50 before each scenario;
# $3 batch cap plus $0.05 per-question candidate limit keeps this run bounded.
eval_compare.MODELS=[{'alias':'eval-nano','model':'gpt-5-nano-2025-08-07',
                     'input_rate':.05,'output_rate':.4,'budget':.05,'tool_transport':'mcp'}]
ids=json.loads(Path('/eval/core-18.json').read_text())['case_ids']
asyncio.run(eval_compare.main(Namespace(output=str(out),dry_run=False,cases=','.join(ids),
    gold_file='/eval/gold-v3.json',reuse_from=None,collect_only=True,grade_only=False,repeats=1,budget=3.)))
