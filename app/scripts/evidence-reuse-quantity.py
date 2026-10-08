"""Small full-agent reuse/refresh checks on isolated evaluation fixtures."""
import asyncio,json,os
from pathlib import Path
from sqlalchemy import text
from marketplace import agent
from marketplace.db import Session,Conversation,engine,init_schema,State
from marketplace.eval_fixtures import guard_database,fixture,fingerprint,Factory
alias=os.environ['CHECK_MODEL']
out=Path('/results/core18-history-v3-quantity-reuse-'+alias+'-2026-10-01');out.mkdir(exist_ok=True)
resume=os.getenv('RESUME')=='1'
assert resume or not (out/'results.json').exists()
state={'turns':[],'model':'gpt-5-nano-2025-08-07' if alias=='eval-nano' else 'gpt-5.4-2026-03-05','prompt_version':agent.PROMPT_VERSION}
config={'alias':alias,'model':state['model'],'input_rate':.05 if alias=='eval-nano' else 2.5,'output_rate':.4 if alias=='eval-nano' else 15.,'budget':.05 if alias=='eval-nano' else 1.,'tool_transport':'mcp'}
if resume: state=json.loads((out/'results.json').read_text())
original=agent.BudgetHooks.on_llm_start
async def capture(self,context,instance,system_prompt,input_items):
 await original(self,context,instance,system_prompt,input_items)
 with (out/'model-inputs.jsonl').open('a') as f:f.write(json.dumps({'instructions':system_prompt,'input_items':input_items},default=str)+'\n')
agent.BudgetHooks.on_llm_start=capture
async def ask(convo,question,label):
 if any(t['label']==label for t in state['turns']):return
 before=fingerprint();r=await agent.answer(convo,question,evaluation_config=config)
 state['turns'].append({'label':label,'question':question,'business_unchanged':fingerprint()==before,'run':r})
 (out/'results.json').write_text(json.dumps(state,indent=2,default=str))
 print(label,r['status'],'tools',[t['name'] for t in r['metrics']['tool_attempts']],flush=True)
 # Preserve failed turns and continue; do not silently replace with retries.
async def main():
 guard_database();init_schema();lock=engine.connect();assert lock.execute(text('SELECT pg_try_advisory_lock(938271)')).scalar()
 cache=json.loads(Path('/results/embedding-cache.json').read_text())
 fixture('02',cache)
 with Session.begin() as db:db.add(Conversation(id='reuse-quantity',owner_id='support',title='Quantity reuse',items=[]))
 await ask('reuse-quantity','What products and quantities are in order-1, and who sells them?','initial_records')
 await ask('reuse-quantity','What is the total quantity in that order now?','unchanged_quantity')
 lock.close()
asyncio.run(main())
