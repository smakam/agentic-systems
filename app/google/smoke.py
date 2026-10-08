"""Hosted acceptance sequence; prints evidence, never declares correctness automatically."""
import asyncio,json,time
from pathlib import Path
import agentplatform

async def main():
    config=json.loads(Path('deployment.json').read_text())
    client=agentplatform.Client(project=config['project'],location=config['location'])
    runtime=client.runtimes.get(name=config['resource_name'])
    records=[]
    async def session(user='course-operator',memory=True):
        result=await runtime.async_create_session(user_id=user,state={'memory_enabled':memory})
        print('SESSION',result,flush=True)
        return result['id']
    async def ask(label,sid,question,user='course-operator',memory=True):
        start=time.monotonic();events=[]
        async for event in runtime.async_stream_query(user_id=user,session_id=sid,message=question,state_delta={'memory_enabled':memory},run_config={'max_llm_calls':12}):
            events.append(event)
        entry={'label':label,'session':sid,'user':user,'question':question,'seconds':round(time.monotonic()-start,2),'events':events}
        records.append(entry)
        Path('smoke-results.json').write_text(json.dumps(records,indent=2,default=str))
        print('RESULT',label,'seconds',entry['seconds'],flush=True)
        errors=[event for event in events if event.get('error_code') or event.get('error_message')]
        if errors:
            raise RuntimeError(f'Hosted call {label} failed: {errors}')
        for event in events:
            for part in (event.get('content') or {}).get('parts',[]):
                if part.get('function_call'): print('TOOL',part['function_call'].get('name'),flush=True)
                if part.get('text'): print('TEXT',part['text'],flush=True)
        return entry
    first=await session(memory=False)
    await ask('sql',first,'Which sellers have unpaid funds, and how much?',memory=False)
    await ask('policy',first,'What is the current payout policy?',memory=False)
    await ask('items',first,'Show the items and quantities for order-2.',memory=False)
    await ask('followup',first,'What is their total quantity?',memory=False)
    seed=await session()
    await ask('preference',seed,'For payout investigations, I prefer every answer to start with Payout snapshot, followed by status, reason and next step.')
    saved=await runtime.async_get_session(user_id='course-operator',session_id=seed)
    print('MEMORY_GENERATION',await runtime.async_add_session_to_memory(session=saved),flush=True)
    memories={}
    for attempt in range(12):
        memories=await runtime.async_search_memory(user_id='course-operator',query='payout investigation response preference')
        if memories.get('memories'): break
        await asyncio.sleep(10)
    Path('memory-result.json').write_text(json.dumps(memories,indent=2,default=str))
    print('MEMORIES',json.dumps(memories,default=str),flush=True)
    if not memories.get('memories'):
        print('MEMORY_NOT_READY: recall checks deferred',flush=True);return
    fresh=await session()
    await ask('recall',fresh,'Why is the payout for order-2 held?')
    off=await session(memory=False)
    await ask('memory_off',off,'Why is the payout for order-2 held?',memory=False)
    other=await session(user='course-support')
    await ask('other_user',other,'What response format do I prefer for payout investigations?',user='course-support')
    print('ACCEPTANCE_RUN_FINISHED: review answers and native traces',flush=True)

if __name__=='__main__': asyncio.run(main())
