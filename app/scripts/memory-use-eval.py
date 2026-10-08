"""Three controlled memory-use pairs, isolated fixtures, fresh conversations; no judge."""
import os,asyncio,json,hashlib
from pathlib import Path
from datetime import datetime,timezone
assert os.environ['DATABASE_URL'].endswith('/market_test')
from sqlalchemy import text,select
from marketplace.db import Session,Base,engine,init_schema,Conversation,Memory,User,State,Payout,Item,Listing,Product,Shipment,Return,Event
from marketplace.seed import seed
from marketplace.business import uid,execute
from marketplace.agent import answer,PROMPT_VERSION

out=Path('/results/memory-use-v1-2026-10-02');out.mkdir(parents=True,exist_ok=True)
assert not (out/'results.json').exists(),'Preserve previous artifacts'
config={'alias':'support-model','model':'gpt-5-nano-2025-08-07','input_rate':.05,'output_rate':.4,'budget':.05,'tool_transport':'mcp'}
rows=[];fixtures=[]
def reset_fixture(name):
    init_schema()
    with engine.begin() as conn:
        tables=','.join('public.'+t.name for t in reversed(Base.metadata.sorted_tables))
        conn.execute(text(f'TRUNCATE {tables} CASCADE'))
    with Session.begin() as db:seed(db)
    fixtures.append({'scenario':name,'reset':'isolated market_test seeded revision 1','baseline_clock':'2026-09-27T12:00:00Z'})
def chat():
    cid=uid('memory-use')
    with Session.begin() as db:db.add(Conversation(id=cid,owner_id='support',title='Controlled memory-use test',items=[]))
    return cid
async def ask(case,question,enabled=True,write=False):
    cid=chat()
    result=await answer(cid,question,evaluation_config=config,memory_enabled=enabled,memory_write=write)
    with Session() as db:
        memories=[{'id':m.id,'kind':m.kind,'content':m.content,'version':m.version,'provenance':m.provenance} for m in db.scalars(select(Memory)).all()]
    row={'case':case,'question':question,'memory_enabled':enabled,'memory_write':write,'conversation_id':cid,'result':result,'memories_after':memories}
    rows.append(row);(out/'results.json').write_text(json.dumps(rows,indent=2,default=str))
    print(case,result['status'],result['answer'],flush=True)
    if result['status']!='completed':raise RuntimeError('Incomplete model run: '+case)
    return row
async def pair(name,question):
    await ask(name+'-on',question)
    await ask(name+'-off',question,enabled=False)
async def main():
    reset_fixture('stale-checkpoint')
    await ask('stale-save','Save an episodic checkpoint: Cedar & Co. payout-1 for order-1 was failed at business revision 1. Next step: inspect payout attempts and check whether a retry has completed. This is historical, not current status.',write=True)
    with Session.begin() as db:
        mutation=execute(db,db.get(User,'operator'),uid('memory-retry'),'payout',{'id':'payout-1','outcome':'completed'})
    fixtures[-1].update(mutation=mutation,expected={'payout-1':'completed','payout-2':'held','revision':2,'old_checkpoint_status':'failed','old_checkpoint_revision':1})
    await pair('stale','Resume my saved investigation for order-1. Is Cedar & Co. payout-1 still failed, or has it completed now? Explain what changed using current payout records and attempt history.')
    reset_fixture('procedural-application')
    await ask('procedure-save','Remember this procedural checklist for payout investigations: check delivery and the 24-hour hold, check active returns, then inspect payout failure events. Use current business records and current policy, and report which check explains the unpaid payout.',write=True)
    fixtures[-1]['expected']={'seller':'Cedar & Co.','payout-1':'failed','delivery_hold':'elapsed (delivered two days before clock)','active_returns':0,'recorded_failure':'simulated provider timeout','next_step':'operator retry, not another 24-hour wait'}
    await pair('procedure','Investigate why Cedar & Co. has not been paid for order-1. Use my saved investigation checklist if available, and explain delivery hold, active returns and the recorded payout failure with supporting evidence.')
    reset_fixture('current-instruction-precedence')
    await ask('preference-save','Remember this semantic preference: when I say Cedar, I mean seller Cedar & Co.',write=True)
    fixtures[-1]['expected']={'product':'Desk Lamp','product_id':'product-2','quantity':2,'seller':'Northstar Goods','preference_unchanged':'Cedar means seller Cedar & Co.'}
    await pair('precedence','For this question only, Cedar means the Desk Lamp product, not seller Cedar & Co. Show the product, quantity and seller for that product in order-1. Do not change my saved preference.')
    summary={'model':config,'prompt_version':PROMPT_VERSION,'questions':len(rows),'paired_answers':6,'estimated_uncached_model_cost_usd':sum(r['result']['metrics']['estimated_model_cost_usd'] for r in rows),'fixtures':fixtures,'grading':'assistant review pending; no paid judge','scope':'single sample per variant; not a general quality/latency benchmark'}
    (out/'summary.json').write_text(json.dumps(summary,indent=2,default=str))
asyncio.run(main())
