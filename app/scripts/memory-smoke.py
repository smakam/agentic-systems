"""Small live memory experiment on isolated market_test; no judge; preserve artifacts."""
import os,asyncio,json
from pathlib import Path
assert os.environ['DATABASE_URL'].endswith('/market_test')
from marketplace.db import Session,Conversation,Memory,State,engine
from marketplace.business import uid
from marketplace.agent import answer
from marketplace.memory import MemoryStore

out=Path(os.getenv('MEMORY_RESULTS_DIR','/results/memory-v1-2026-10-02'));out.mkdir(parents=True,exist_ok=True)
assert not (out/'results.json').exists(), 'Choose a fresh output directory rather than overwrite evidence'
config={'alias':'support-model','model':'gpt-5-nano-2025-08-07','input_rate':.05,'output_rate':.4,'budget':.05,'tool_transport':'mcp'}
rows=[]
def chat(owner='support'):
    cid=uid('memory-test')
    with Session.begin() as db: db.add(Conversation(id=cid,owner_id=owner,title='Memory smoke test',items=[]))
    return cid
async def ask(name,question,*,write=False,enabled=True,owner='support'):
    result=await answer(chat(owner),question,evaluation_config=config,memory_enabled=enabled,memory_write=write)
    row={'case':name,'question':question,'result':result};rows.append(row)
    (out/'results.json').write_text(json.dumps(rows,indent=2,default=str))
    print(name,result['status'],result['answer'],flush=True)
    if result['status']!='completed':raise RuntimeError(name+' run failed')
    return result
async def main():
    from sqlalchemy import delete
    # Isolated fixture only: reset long-term records between independent experiment versions.
    with Session.begin() as db: db.execute(delete(Memory))
    await ask('semantic-save','Remember this semantic preference: When I say Cedar, I mean seller Cedar & Co.',write=True)
    await ask('semantic-recall','What do I mean when I say Cedar?')
    await ask('episodic-save','Save an episodic investigation checkpoint: I investigated order-1. The next step is to check payout attempt history. This checkpoint is historical, not a claim about current payout status.',write=True)
    await ask('episodic-recall','What was the next step in my saved order-1 investigation?')
    await ask('procedural-save','Remember this procedural checklist for payout investigations: check delivery hold, then active returns, then payout failure events. Always use current policy and business records.',write=True)
    await ask('procedural-recall','What payout investigation checklist did I ask you to remember?')
    if not os.getenv('MEMORY_QUICK'):
        await ask('instruction-precedence','For this question Cedar means Cedar Desk product, not the seller. What product do I mean?')
        await ask('current-facts','Resume my saved order-1 investigation: check the CURRENT payout status and events, not just the saved checkpoint.')
    await ask('other-user','What preference have I saved about Cedar?',owner='operator')
    await ask('memory-off','What preference have I saved about Cedar?',enabled=False)
    await ask('write-denied','Remember this semantic preference: call me Captain.',write=False)
    await ask('update','Update my saved Cedar preference: When I say Cedar, I now mean Cedar Desk product.',write=True)
    await ask('updated-recall','What do I mean by Cedar according to my saved preference?')
    await ask('delete','Forget my saved Cedar preference.',write=True)
    await ask('deleted-recall','What preference have I saved about Cedar?')
    costs=sum(x['result']['metrics']['estimated_model_cost_usd'] for x in rows)
    (out/'summary.json').write_text(json.dumps({'runs':len(rows),'estimated_uncached_model_cost_usd':costs,'model':config,'grading':'manual review pending; no LLM judge','note':'isolated market_test; no interactive memories or business data modified'},indent=2))
asyncio.run(main())
