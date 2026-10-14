"""Read only correlated native telemetry; no inference or deployment changes."""
import json
from datetime import datetime,timezone,timedelta
from pathlib import Path

HERE=Path(__file__).resolve().parent

def input_fragments(node):
    found=[]
    if isinstance(node,dict):
        for key,value in node.items():
            if any(word in key.lower() for word in ('input','prompt','llm_request','request')):
                found.append(json.dumps(value,default=str))
            found.extend(input_fragments(value))
    elif isinstance(node,list):
        for child in node:found.extend(input_fragments(child))
    return found

def preload_evidence(records):
    # Require a memory-context marker and the stored columns in an INPUT field.
    # An answer/output mentioning columns cannot satisfy this predicate.
    for record in records:
        for text in input_fragments(record):
            low=text.lower()
            if 'past_conversations' in low and all(x in low for x in ('finding','evidence','next action')):return True
    return False

def main():
    settings=json.loads((HERE/'support-basics-deployment.json').read_text())
    if settings.get('app_name')!='support_agent_basics':raise SystemExit('Only the Basics manifest is accepted.')
    receipt=json.loads((HERE/'basics-verification-results.json').read_text())
    import google.auth
    from google.auth.transport.requests import AuthorizedSession
    credentials,_=google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    transport=AuthorizedSession(credentials)
    now=datetime.now(timezone.utc)
    params={'startTime':receipt['started_at'],'endTime':now.isoformat(),'view':'COMPLETE','pageSize':100,'orderBy':'start desc'}
    traces=[];partial=False
    for page in range(5):
        response=transport.get('https://cloudtrace.googleapis.com/v1/projects/'+settings['project']+'/traces',params=params,timeout=45)
        response.raise_for_status();data=response.json();traces.extend(data.get('traces',[]))
        if not data.get('nextPageToken'):break
        params['pageToken']=data['nextPageToken']
    else:partial=True
    cases=[];matched=[]
    for case in receipt['cases']:
        hits=[t for t in traces if any(s.get('labels',{}).get('gen_ai.conversation.id')==case['session'] for s in t.get('spans',[]))]
        matched.extend(hits)
        row={'label':case['label'],'session':case['session'],'trace_ids':[t['traceId'] for t in hits],'span_names':sorted({s['name'] for t in hits for s in t.get('spans',[])})}
        cases.append(row);print(json.dumps(row),flush=True)
    unique={x['traceId']:x for x in matched}
    # Cloud Logging can contain EVENT_ONLY model-input content omitted by spans.
    logs=[]
    for trace_id in unique:
        response=transport.post('https://logging.googleapis.com/v2/entries:list',json={'resourceNames':['projects/'+settings['project']],'filter':'trace="projects/'+settings['project']+'/traces/'+trace_id+'"','pageSize':100,'orderBy':'timestamp desc'},timeout=45)
        if response.status_code==200:logs.extend(response.json().get('entries',[]))
    fresh_sessions={x['session'] for x in receipt['cases'] if x['label']=='fresh_session_business_memory'}
    fresh_traces=[t for t in unique.values() if any(s.get('labels',{}).get('gen_ai.conversation.id') in fresh_sessions for s in t.get('spans',[]))]
    fresh_ids={x['traceId'] for x in fresh_traces}
    fresh_logs=[x for x in logs if x.get('trace','').rsplit('/',1)[-1] in fresh_ids]
    result={'cases':cases,'trace_scan_partial':partial,'all_sessions_correlated':all(x['trace_ids'] for x in cases),'model_input_preload_verified':preload_evidence(fresh_traces+fresh_logs),'matched_traces':list(unique.values()),'correlated_logs':logs}
    (HERE/'basics-trace-verification-results.json').write_text(json.dumps(result,indent=2,default=str))
    print(json.dumps({k:v for k,v in result.items() if k not in ('cases','matched_traces','correlated_logs')}),flush=True)
    if not result['model_input_preload_verified']:
        print('Inspect the fresh business session in native Session detail: model input must contain PAST_CONVERSATIONS and the saved preference. No automatic proof was found in the bounded telemetry read.',flush=True)

if __name__=='__main__':main()
