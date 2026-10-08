"""Read-only business diagnostic on actual marketplace; no fixture reset or memory writes."""
import asyncio,json,os
from pathlib import Path
from sqlalchemy import text,select
from marketplace.db import Session,Conversation,Memory,State
from marketplace.business import uid
from marketplace import agent
assert os.environ['DATABASE_URL'].endswith('/market')
out=Path('/results/memory-refunded-order-gpt54-2026-10-03');out.mkdir(exist_ok=True)
assert not (out/'results.json').exists()
config={'alias':'eval-54','model':'gpt-5.4-2026-03-05','input_rate':2.5,'output_rate':15.,'budget':1.,'tool_transport':'mcp'}
def ground_truth():
 with Session() as db:
  return {'revision':db.get(State,1).revision,'rows':[dict(x) for x in db.execute(text("SELECT i.id AS item, p.id AS payout, p.status, p.amount, a.gross, a.fee, a.refunded FROM order_items i JOIN allocations a ON a.item_id=i.id JOIN payouts p ON p.allocation_id=a.id WHERE i.order_id=:oid"),{'oid':'ord-a9f9496711'}).mappings()], 'memories':[{'id':m.id,'kind':m.kind,'title':m.title,'content':m.content,'version':m.version} for m in db.scalars(select(Memory).where(Memory.owner_id=='support').order_by(Memory.id)).all()]}
original=agent.BudgetHooks.on_llm_start
async def capture(self,context,instance,system_prompt,input_items):
 await original(self,context,instance,system_prompt,input_items)
 with (out/'model-inputs.jsonl').open('a') as f:f.write(json.dumps({'instructions':system_prompt,'input_items':input_items},default=str)+'\n')
agent.BudgetHooks.on_llm_start=capture
async def main():
 before=ground_truth();assert any(m['kind']=='procedural' and 'payout' in m['content'].lower() for m in before['memories'])
 state={'model':config,'prompt_version':agent.PROMPT_VERSION,'before':before,'results':[],'judge':'none; assistant review'}
 for label,q in [('original','Investigate the payout for order ord-a9f9496711'),('explicit-checklist','Investigate the payout for order ord-a9f9496711 using my saved payout investigation checklist.')]:
  cid=uid('chat')
  with Session.begin() as db:db.add(Conversation(id=cid,owner_id='support',title='GPT-5.4 refunded-order memory diagnostic',items=[]))
  result=await agent.answer(cid,q,evaluation_config=config,memory_enabled=True,memory_write=False)
  state['results'].append({'label':label,'question':q,'conversation_id':cid,'run':result})
  state['after']=ground_truth();state['business_and_memory_unchanged']=state['before']==state['after']
  (out/'results.json').write_text(json.dumps(state,indent=2,default=str))
  print(label,result['status'],result['answer'],flush=True)
  assert result['status']=='completed'
 assert state['business_and_memory_unchanged']
asyncio.run(main())
