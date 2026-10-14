"""Bounded native hosted acceptance; five synthetic-user questions, no redeploy.

Run in the prepared Cloud Shell directory. Saves receipts after each operation.
Model/tool events prove fixture use; native model-input memory evidence is checked
separately with verify_traces.py or the platform Session detail view.
"""
import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import time
import uuid

HERE=Path(__file__).resolve().parent
COLUMNS=('finding','evidence','next action')

def unwrap_order(value):
    if isinstance(value,dict):
        if 'found' in value:return value
        for child in value.values():
            got=unwrap_order(child)
            if got is not None:return got
    if isinstance(value,list):
        for child in value:
            got=unwrap_order(child)
            if got is not None:return got
    return None

def summarize(events):
    calls=[];responses=[];answers=[];errors=[];safe_events=[]
    for event in events:
        if event.get('error_code') or event.get('error_message'):
            errors.append({'code':str(event.get('error_code') or 'provider_error')})
        content=event.get('content') or {}
        parts=content.get('parts') or []
        for part in parts:
            if part.get('function_call'):
                calls.append(part['function_call'])
            if part.get('function_response'):
                responses.append(part['function_response'])
            if part.get('text'):answers.append(part['text'])
        # Only this synthetic suite's native content, not provider error bodies.
        safe_events.append({k:event[k] for k in ('id','author','invocation_id','content','timestamp') if k in event})
    order_results=[unwrap_order(x.get('response')) for x in responses if x.get('name')=='lookup_order']
    return {'tool_calls':calls,'order_results':[x for x in order_results if x is not None],
            'answer':'\n'.join(answers),'errors':errors,'events':safe_events}

def check_case(label,result):
    answer=result['answer'].lower();rows=result['order_results']
    if result['errors']:return False
    if label=='known_order':
        return any(x.get('found') and x.get('order',{}).get('order_id')=='order-demo-1' and x['order']['items'][0]['quantity']==2 for x in rows) and 'ceramic mug' in answer and ('2' in answer or 'two' in answer)
    if label=='same_session_followup':
        return any(x.get('found') and x.get('order',{}).get('order_id')=='order-demo-1' and x['order'].get('payout_status')=='held' for x in rows) and 'held' in answer
    if label=='unknown_order':
        return any(x.get('found') is False and x.get('order_id')=='order-demo-999' for x in rows) and any(x in answer for x in ('no such','not found','does not exist','cannot find',"can't find",'no order','not in','no record'))
    if label=='fresh_session_business_memory':
        return any(x.get('found') and x.get('order',{}).get('order_id')=='order-demo-2' and x['order'].get('payout_status')=='released' for x in rows) and 'released' in answer and all(x in answer for x in COLUMNS)
    return bool(result['answer'])

async def verify(runtime,receipt,output,memory_wait=120,memory_only=False):
    user='verification-basics-'+uuid.uuid4().hex
    receipt.update(user=user,started_at=datetime.now(timezone.utc).isoformat(),cases=[],memory={},inference_requests=0)
    def persist():output.write_text(json.dumps(receipt,indent=2,default=str))
    async def create():
        session=await runtime.async_create_session(user_id=user,state={})
        return session['id']
    async def ask(label,sid,question):
        if receipt['inference_requests']>=5:raise RuntimeError('Hosted request budget exhausted')
        receipt['inference_requests']+=1;persist();events=[];started=time.monotonic()
        try:
            async for event in runtime.async_stream_query(user_id=user,session_id=sid,message=question,run_config={'max_llm_calls':3}):events.append(event)
            result=summarize(events)
        except Exception as exc:
            result=summarize(events);result['errors'].append({'type':type(exc).__name__})
        result.update(label=label,session=sid,question=question,seconds=round(time.monotonic()-started,2))
        result['passed']=check_case(label,result);receipt['cases'].append(result);persist()
        print(json.dumps({'case':label,'passed':result['passed'],'tools':[x.get('name') for x in result['tool_calls']],'seconds':result['seconds']}),flush=True)
        return result
    receipt['scope']='memory_only' if memory_only else 'full_suite'
    if not memory_only:
        short=await create()
        await ask('known_order',short,'What products and quantities are in order-demo-1?')
        await ask('same_session_followup',short,'What is its payout status?')
        await ask('unknown_order',await create(),'What is the payment status of order-demo-999?')
    pref=await create()
    await ask('preference_seed',pref,'I prefer support answers in a compact table with Finding, Evidence and Next action. Please acknowledge this preference briefly.')
    saved=await runtime.async_get_session(user_id=user,session_id=pref)
    await runtime.async_add_session_to_memory(session=saved)
    receipt['memory'].update(generation_requested=True,source_session=pref);persist()
    deadline=time.monotonic()+memory_wait
    while time.monotonic()<deadline:
        data=await runtime.async_search_memory(user_id=user,query='preferred support answer format')
        rows=data.get('memories',[]) if isinstance(data,dict) else []
        text=json.dumps(rows,default=str).lower()
        if rows and all(x in text for x in COLUMNS):
            receipt['memory'].update(stored_preference_verified=True,memories=rows);break
        await asyncio.sleep(5)
    else:receipt['memory']['stored_preference_verified']=False
    persist()
    if receipt['memory'].get('stored_preference_verified'):
        await ask('fresh_session_business_memory',await create(),'What is the payout status of order-demo-2?')
        other=await runtime.async_search_memory(user_id=user+'-other',query='preferred support answer format')
        receipt['memory']['other_user_empty']=not bool(other.get('memories',[]) if isinstance(other,dict) else [])
    receipt['memory']['model_input_preload_verified']=False
    receipt['memory']['model_input_note']='Pending native trace/Session model-input inspection; format and scoped memory retrieval alone do not prove preload input.'
    receipt['bounded_checks_passed']=len(receipt['cases'])==(2 if memory_only else 5) and all(x['passed'] for x in receipt['cases']) and receipt['memory'].get('stored_preference_verified',False) and receipt['memory'].get('other_user_empty',False)
    receipt['native_trace_verification_pending']=True
    receipt['finished_at']=datetime.now(timezone.utc).isoformat();persist()
    print(json.dumps({'bounded_checks_passed':receipt['bounded_checks_passed'],'native_trace_verification_pending':True,'inference_requests':receipt['inference_requests'],'receipt':str(output)}),flush=True)
    return receipt

async def main():
    parser=argparse.ArgumentParser();parser.add_argument('--memory-wait',type=int,default=120);parser.add_argument('--memory-only',action='store_true');args=parser.parse_args()
    settings=json.loads((HERE/'support-basics-deployment.json').read_text())
    if settings.get('app_name')!='support_agent_basics':raise SystemExit('Use the separate Basics manifest; existing marketplace runtime is not a target.')
    import agentplatform
    runtime=agentplatform.Client(project=settings['project'],location=settings['location']).runtimes.get(name=settings['resource_name'])
    receipt={'runtime':settings['resource_name'],'project':settings['project'],'app_name':settings['app_name'],'fixture':'support-agent-basics-fictional-v1'}
    result=await verify(runtime,receipt,HERE/'basics-verification-results.json',memory_wait=args.memory_wait,memory_only=args.memory_only)
    if not result['bounded_checks_passed']:raise SystemExit('One or more bounded checks failed; inspect the receipt before rerunning paid requests.')

if __name__=='__main__':asyncio.run(main())
