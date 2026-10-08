"""Paired citation-prompt diagnostic; nano and GPT-5.4; no paid judge."""
import asyncio, json
from argparse import Namespace
from pathlib import Path
from marketplace import eval_compare, agent
out=Path('/results/citation-prompt-v2-2026-10-01')
baseline=json.loads(Path('/results/catalog-v2-2026-10-01/results.json').read_text())
assert {k:v for k,v in eval_compare.manifest()['source_hashes'].items() if k!='agent.py'}=={k:v for k,v in baseline['manifest']['source_hashes'].items() if k!='agent.py'}, 'Unexpected source drift'
assert agent.PROMPT_VERSION=='catalog-v2-question-context-v2-citations'
assert eval_compare.manifest()['ontology_hash']==baseline['manifest']['ontology_hash'], 'Ontology drift'
assert (agent.MAX_TURNS,agent.MAX_SECONDS,agent.MAX_COMPLETION_TOKENS)==(8,150,4096)
out.mkdir(parents=True,exist_ok=True)
assert not (out/'results.json').exists(), 'Preserve previous run; use a new experiment path'
original=agent.BudgetHooks.on_llm_start
async def capture(self, context, instance, system_prompt, input_items):
    await original(self,context,instance,system_prompt,input_items)
    with (out/'model-inputs.jsonl').open('a') as f:
        f.write(json.dumps({'prompt_version':agent.PROMPT_VERSION,'instructions':system_prompt,'input_items':input_items},default=str)+'\n')
agent.BudgetHooks.on_llm_start=capture
eval_compare.MODELS=[{'alias':'eval-nano','model':'gpt-5-nano-2025-08-07','input_rate':.05,'output_rate':.4,'budget':.05,'tool_transport':'mcp'},{'alias':'eval-54','model':'gpt-5.4-2026-03-05','input_rate':2.5,'output_rate':15.,'budget':1.0,'tool_transport':'mcp'}]
(out/'experiment-plan.json').write_text(json.dumps({'cases':['09','14','17','27'],'design':'one sample per model per case; case 27 includes follow-up','change':'citation instruction and prompt version only; unchanged business instructions, fixtures, tools and operational limits','models':eval_compare.MODELS,'judge':'none; assistant review plus strict citation audit','batch_guard_usd':5.5},indent=2)+'\n')
asyncio.run(eval_compare.main(Namespace(output=str(out),dry_run=False,cases='09,14,17,27',gold_file='/eval/gold-v3.json',reuse_from=None,collect_only=True,grade_only=False,repeats=1,budget=5.5)))
