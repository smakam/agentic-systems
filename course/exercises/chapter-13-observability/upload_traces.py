"""Upload a fixed synthetic cohort using supported OTLP/HTTP JSON ingestion.

No model calls, database changes or additional Python dependencies. A saved
manifest prevents accidental duplicate upload; use a new output for a new cohort.
"""
import argparse
import base64
import json
import os
from pathlib import Path
import time
import urllib.request
import uuid

def attributes(values):
    return [{'key':k,'value':{'stringValue':str(v)}} for k,v in values.items()]

def payload(fixture, batch, epoch):
    spans=[]; manifest=[]
    for index,case in enumerate(fixture['cases']):
        trace=uuid.uuid4().hex; root=uuid.uuid4().hex[:16]
        start=epoch+index*10_000_000_000
        shared={'langfuse.trace.name':'ch13-'+case['name'],
            'langfuse.session.id':batch+'-'+case['session'],
            'langfuse.environment':'ch13-synthetic',
            'langfuse.trace.metadata.batch_id':batch,
            'langfuse.trace.metadata.synthetic':'true'}
        def span(name,kind,left,right,level,extra=None,parent=None):
            obj={'traceId':trace,'spanId':uuid.uuid4().hex[:16] if parent else root,
                'name':name,'kind':1,'startTimeUnixNano':str(start+left*1_000_000),
                'endTimeUnixNano':str(start+right*1_000_000),
                'attributes':attributes({**shared,'langfuse.observation.type':kind,
                    'langfuse.observation.level':level,**(extra or {})}),
                'status':{'code':2 if level=='ERROR' else 1}}
            if parent:obj['parentSpanId']=parent
            return obj
        spans.append(span('ch13-'+case['name'],'span',0,case['duration_ms'],
            'ERROR' if case['status']=='failed' else 'DEFAULT',
            {'langfuse.trace.metadata.run_status':case['status'],
             'langfuse.observation.output':json.dumps({'status':case['status'],'synthetic':True})}))
        for name,kind,left,right,level,inputs,outputs in case['steps']:
            extra={'langfuse.observation.input':json.dumps({'example':name,'synthetic':True}),
                'langfuse.observation.output':json.dumps({'result':'simulated error' if level=='ERROR' else 'supplied example'})}
            if kind=='generation':
                extra.update({'langfuse.observation.model.name':'ch13-synthetic-model',
                  'langfuse.observation.usage_details':json.dumps({'input':inputs,'output':outputs,'total':inputs+outputs}),
                  'langfuse.observation.cost_details':json.dumps({'input':inputs*0.000001,'output':outputs*0.000002,'total':inputs*0.000001+outputs*0.000002})})
            spans.append(span(name,kind,left,right,level,extra,root))
        manifest.append({'case':case['name'],'trace_id':trace,'session_id':batch+'-'+case['session'],
            'status':case['status'],'duration_ms':case['duration_ms']})
    return {'resourceSpans':[{'resource':{'attributes':attributes({'service.name':'ch13-fixture-loader'})},
        'scopeSpans':[{'scope':{'name':'ch13-teaching-fixture','version':'1.0'},'spans':spans}]}]},manifest

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',required=True)
    ap.add_argument('--fixture',default=str(Path(__file__).with_name('fixture.json')))
    args=ap.parse_args(); out=Path(args.output)
    if out.exists():raise SystemExit('Output already exists. Keep the manifest; choose a new filename for a new batch.')
    host=os.getenv('LANGFUSE_BASE_URL') or os.getenv('LANGFUSE_HOST')
    pub=os.getenv('LANGFUSE_PUBLIC_KEY'); secret=os.getenv('LANGFUSE_SECRET_KEY')
    if not all((host,pub,secret)):raise SystemExit('Set Langfuse URL, public key and secret key.')
    fixture=json.loads(Path(args.fixture).read_text()); batch='ch13-'+uuid.uuid4().hex[:12]
    body,entries=payload(fixture,batch,time.time_ns()-120_000_000_000)
    record={'batch_id':batch,'synthetic':True,'state':'prepared','cases':entries}
    out.write_text(json.dumps(record,indent=2))
    auth=base64.b64encode((pub+':'+secret).encode()).decode()
    request=urllib.request.Request(host.rstrip('/')+'/api/public/otel/v1/traces',
      data=json.dumps(body).encode(),headers={'Content-Type':'application/json',
      'Authorization':'Basic '+auth,'x-langfuse-ingestion-version':'4'},method='POST')
    # A timeout can have an unknown outcome. Never retry blindly with new IDs.
    with urllib.request.urlopen(request,timeout=30) as response:
        result=json.loads(response.read() or b'{}')
    if int(result.get('partialSuccess',{}).get('rejectedSpans',0)):
        record['state']='partial';out.write_text(json.dumps(record,indent=2))
        raise SystemExit('Partial ingestion; inspect the batch before retrying.')
    record['state']='accepted';out.write_text(json.dumps(record,indent=2))
    print(json.dumps(record,indent=2))

if __name__=='__main__':main()
