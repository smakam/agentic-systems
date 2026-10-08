"""Four-case GPT-5.4 full-agent comparison against archived catalog-v2 nano."""
import asyncio, json
from argparse import Namespace
from pathlib import Path
from marketplace import eval_compare, agent
out=Path('/results/catalog-v2-gpt54-2026-10-01')
baseline=json.loads(Path('/results/catalog-v2-2026-10-01/results.json').read_text())
assert eval_compare.manifest()['source_hashes']==baseline['manifest']['source_hashes'], 'Source drift'
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
eval_compare.MODELS=[{'alias':'eval-54','model':'gpt-5.4-2026-03-05','input_rate':2.5,'output_rate':15.,'budget':1.0,'tool_transport':'mcp'}]
(out/'experiment-plan.json').write_text(json.dumps({'baseline':'../catalog-v2-2026-10-01/results.json','cases':['09','14','17','27'],'design':'one full-agent sample per case; preserve follow-up in case 27','unchanged':['source hashes','ontology hash','fixtures','prompt','MCP transport','8 agent turns','150 seconds','4096 completion tokens','low reasoning effort'],'changed':['candidate model','per-question monetary guard: nano $0.05, GPT-5.4 $1.00; price difference only'],'judge':'none; assistant review','batch_guard_usd':5.5},indent=2)+'\n')
asyncio.run(eval_compare.main(Namespace(output=str(out),dry_run=False,cases='09,14,17,27',gold_file='/eval/gold-v3.json',reuse_from=None,collect_only=True,grade_only=False,repeats=1,budget=5.5)))
