import asyncio,hashlib,json,os,re,uuid
from pathlib import Path
import psycopg
from psycopg.rows import dict_row
from sqlalchemy import select
from marketplace import agent
from marketplace.db import Session,Conversation,engine,State,User,Listing,Item,Shipment
from marketplace.business import execute

OUT=Path(os.getenv('CH10_OUTPUT', '/tmp/ch10-demo-results.json'))
LABEL='cedar-window-731'
record={'turns':[],'model_inputs':[],'provider_route':os.getenv('CH10_PROVIDER_ROUTE','direct OpenAI through normal gateway'),'validation_scope':'real SDK/model calls, shared marketplace command handler; UI clicks not rehearsed'}
config={'alias':'support-model','model':os.getenv('OPENAI_MODEL'),'tool_transport':'mcp'}
current=''
original=agent.BudgetHooks.on_llm_start
async def capture(self,context,instance,system_prompt,input_items):
 await original(self,context,instance,system_prompt,input_items)
 # Export only user-message text and item types; no provider reasoning or credentials.
 users=[x.get('content') for x in input_items if isinstance(x,dict) and x.get('role')=='user']
 record['model_inputs'].append({'case':current,'user_messages':users,'item_types':[x.get('type',x.get('role')) for x in input_items if isinstance(x,dict)],'contains_marker':LABEL in json.dumps(users)})
agent.BudgetHooks.on_llm_start=capture

def fixed_fingerprint():
 url=os.environ['READ_DATABASE_URL'].rsplit('/',1)[0]+'/market_eval'
 with psycopg.connect(url,row_factory=dict_row) as db:
  db.execute('BEGIN READ ONLY')
  data={name:db.execute('SELECT * FROM analytics.'+name+' ORDER BY 1').fetchall() for name in ('freshness','sellers','products','listings','orders','order_items','payments','shipments','allocations','payouts','returns','refunds','events')}
 return hashlib.sha256(json.dumps(data,default=str,sort_keys=True).encode()).hexdigest()

def save(): OUT.write_text(json.dumps(record,default=str,indent=2)+'\n')
async def ask(cid,question,label):
 global current
 current=label
 run=await agent.answer(cid,question,evaluation_config=config,memory_enabled=False)
 record['turns'].append({'case':label,'question':question,'run':run})
 save()
 print(json.dumps({'case':label,'status':run['status'],'revision':run['revision'],'tool_calls':run['metrics'].get('business_tool_calls'),'evidence_count':len(run['evidence'])}),flush=True)
 assert run['status']=='completed',label
 return run

def verify_pairs(items):
 calls={x['call_id'] for x in items if x.get('type')=='function_call'}
 outputs={x['call_id'] for x in items if x.get('type')=='function_call_output'}
 assert calls==outputs

async def main():
 assert engine.url.database=='ch10_session_lab','Only the disposable Chapter 10 lab database is allowed'
 record['evaluation_fingerprint_before']=fixed_fingerprint()
 tag=uuid.uuid4().hex[:10]
 with Session.begin() as db:
  listing=db.scalar(select(Listing).where(Listing.stock>=2).order_by(Listing.id))
  assert listing is not None
  purchase=execute(db,db.get(User,'buyer'),'ch10-purchase-'+tag,'purchase',{'items':[{'listing_id':listing.id,'quantity':2}]})
  order=purchase['id']; item=db.scalar(select(Item).where(Item.order_id==order)); shipment=db.scalar(select(Shipment).where(Shipment.item_id==item.id))
  ship_id=shipment.id
  cid='chat-ch10-follow-'+tag
  db.add(Conversation(id=cid,owner_id='support',title='Chapter 10 continuity and freshness',items=[]))
 record['fixture']={'order_id':order,'shipment_id':ship_id,'quantity':2,'purchase_revision':purchase['revision'],'conversation_id':cid}
 first=await ask(cid,f'What is the current shipment status for {order}? Cite the evidence.','initial_status')
 assert 'pending' in first['answer'].lower()
 follow=await ask(cid,'How many units are in that order?','follow_up')
 assert re.search(r'\b2\b|\btwo\b',follow['answer'],re.I)
 inputs=[x for x in record['model_inputs'] if x['case']=='follow_up']
 assert inputs and order in json.dumps(inputs[0]['user_messages'])
 with Session.begin() as db:
  changed=execute(db,db.get(User,'operator'),'ch10-dispatch-'+tag,'dispatch',{'id':ship_id})
 record['dispatch_revision']=changed['revision']
 refreshed=await ask(cid,'What is the current shipment status of that order now? Cite current evidence.','fresh_after_dispatch')
 assert refreshed['revision']==changed['revision']>first['revision']
 assert 'dispatched' in refreshed['answer'].lower() and refreshed['evidence']
 assert all(e['snapshot']['revision']==changed['revision'] for e in refreshed['evidence'].values())
 with Session() as db: verify_pairs(db.get(Conversation,cid).items)
 wc='chat-ch10-window-'+tag
 with Session.begin() as db: db.add(Conversation(id=wc,owner_id='support',title='Chapter 10 six-block boundary',items=[]))
 await ask(wc,f'For this conversation, use the fictional label {LABEL} for my sample. Reply only: noted.','window_initial')
 for n in range(1,7): await ask(wc,f'What is {n} plus ten? Answer in one short sentence.','window_checkpoint_'+str(n))
 with Session() as db: stored=db.get(Conversation,wc).items
 selected=await agent.DatabaseSession(wc).get_items()
 starts=[i for i,x in enumerate(stored) if x.get('role')=='user']
 assert len(starts)==7
 assert LABEL in json.dumps(stored[:starts[1]])
 assert LABEL not in json.dumps(stored[starts[1]:]),'Marker repeated in later history; invalid fixture'
 assert LABEL not in json.dumps(selected) and len([x for x in selected if x.get('role')=='user'])==6
 verify_pairs(selected)
 record['window']={'conversation_id':wc,'stored_user_blocks_before_eighth':7,'selected_user_blocks_before_eighth':6,'marker_in_stored_history':True,'marker_in_selected_history':False,'complete_tool_pairs':True}
 await ask(wc,'What fictional label did I give my sample at the beginning?','window_eighth')
 captured=[x for x in record['model_inputs'] if x['case']=='window_eighth']
 assert captured and all(not x['contains_marker'] for x in captured)
 record['evaluation_fingerprint_after']=fixed_fingerprint()
 assert record['evaluation_fingerprint_after']==record['evaluation_fingerprint_before']
 record['status']='passed'
 save()
 print('All three Chapter 10 cases passed; fixed evaluation business data unchanged',flush=True)
if __name__ == '__main__':
 try:
  asyncio.run(main())
 except Exception as error:
  record.update(status='failed', error=str(error))
  save()
  raise
