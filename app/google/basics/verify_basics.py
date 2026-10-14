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

def safe_event(value):
    """Preserve synthetic native diagnostics, excluding credential-bearing fields."""
    if hasattr(value,'model_dump'):value=value.model_dump(mode='json')
    if isinstance(value,dict):
        return {str(k):('[redacted]' if any(secret in str(k).lower() for secret in
                ('authorization','credential','access_token','api_key','private_key')) else safe_event(v))
                for k,v in value.items()}
    if isinstance(value,(list,tuple)):return [safe_event(v) for v in value]
    if value is None or isinstance(value,(str,int,float,bool)):return value
    return {'unsupported_event_type':type(value).__name__}

def event_nodes(value):
    if not isinstance(value,dict):return
    yield value
    # Some SDK transports wrap an ADK event rather than returning it directly.
    for key in ('event','result','output','response'):
        child=value.get(key)
        if isinstance(child,dict):yield from event_nodes(child)
        elif isinstance(child,list):
            for item in child:yield from event_nodes(item)

def summarize(events):
    calls=[];responses=[];answers=[];errors=[];safe_events=[];diagnostics=[]
    for raw in events:
        event=safe_event(raw);safe_events.append(event)
        recognized=False
        for node in event_nodes(event):
            if any(node.get(k) for k in ('error_code','error_message','error','err')):
                errors.append({k:node[k] for k in ('error_code','error_message','error','err','detail','details','message') if k in node})
            content=node.get('content') or {}
            if not isinstance(content,dict):continue
            for part in content.get('parts') or []:
                if not isinstance(part,dict):continue
                if part.get('function_call'):
                    calls.append(part['function_call']);recognized=True
                if part.get('function_response'):
                    responses.append(part['function_response']);recognized=True
                if part.get('text'):
                    answers.append(part['text']);recognized=True
        if not recognized:
            diagnostics.append({'event_index':len(safe_events)-1,
                                'top_level_keys':sorted(event) if isinstance(event,dict) else [],
                                'note':'No recognized answer or tool content; inspect preserved event.'})
    order_results=[unwrap_order(x.get('response')) for x in responses if x.get('name')=='lookup_order']
    return {'tool_calls':calls,'order_results':[x for x in order_results if x is not None],
            'answer':'\n'.join(answers),'errors':errors,'events':safe_events,'diagnostics':diagnostics}

def check_case(label,result):
    answer=result['answer'].lower();rows=result['order_results']
    if label=='same_session_followup':
        prior=result.get('retained_lookup_evidence',{})
        if prior.get('session')==result.get('session') and prior.get('source_case')=='known_order':
            rows=rows+prior.get('order_results',[])
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
        if label=='same_session_followup':
            prior=next((case for case in reversed(receipt['cases']) if case['session']==sid and case['label']=='known_order' and case['passed']),None)
            if prior:
                result['retained_lookup_evidence']={'session':sid,'source_case':'known_order','order_results':prior['order_results']}
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
    # Keep the SDK client alive for the full async verification lifetime.
    # A temporary constructor can finalize its HTTP transport during streaming.
    client=agentplatform.Client(project=settings['project'],location=settings['location'])
    runtime=client.runtimes.get(name=settings['resource_name'])
    receipt={'runtime':settings['resource_name'],'project':settings['project'],'app_name':settings['app_name'],'fixture':'support-agent-basics-fictional-v1'}
    result=await verify(runtime,receipt,HERE/'basics-verification-results.json',memory_wait=args.memory_wait,memory_only=args.memory_only)
    if not result['bounded_checks_passed']:raise SystemExit('One or more bounded checks failed; inspect the receipt before rerunning paid requests.')

if __name__=='__main__':asyncio.run(main())
