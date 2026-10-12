"""Read back each fixture trace and compare its timing, usage and cost."""
import argparse
import base64
import json
import math
import os
from pathlib import Path
import urllib.parse
import urllib.request

def main():
    ap=argparse.ArgumentParser();ap.add_argument('manifest');ap.add_argument('--output',required=True)
    args=ap.parse_args();manifest=json.loads(Path(args.manifest).read_text())
    fixture=json.loads(Path(__file__).with_name('fixture.json').read_text())
    host=os.getenv('LANGFUSE_BASE_URL') or os.environ['LANGFUSE_HOST']
    auth=base64.b64encode((os.environ['LANGFUSE_PUBLIC_KEY']+':'+os.environ['LANGFUSE_SECRET_KEY']).encode()).decode()
    results=[]
    for case,entry in zip(fixture['cases'],manifest['cases'],strict=True):
        assert case['name']==entry['case']
        query=urllib.parse.urlencode({'traceId':entry['trace_id'],'fields':'core,model,usage,metadata','limit':100})
        req=urllib.request.Request(host.rstrip('/')+'/api/public/v2/observations?'+query,headers={'Authorization':'Basic '+auth})
        with urllib.request.urlopen(req,timeout=30) as response:data=json.load(response)['data']
        assert len(data)==len(case['steps'])+1,(case['name'],'missing or extra observations')
        roots=[d for d in data if not d.get('parentObservationId')];assert len(roots)==1
        root=roots[0];assert math.isclose(root['latency'],case['duration_ms']/1000,abs_tol=.002)
        assert root['metadata']['batch_id']==manifest['batch_id']
        assert root['metadata']['run_status']==case['status']
        gens=[d for d in data if d['type']=='GENERATION']
        tokens=sum(d['totalUsage'] for d in gens)
        expected=sum(s[5]+s[6] for s in case['steps'])
        assert tokens==expected,(case['name'],'token mismatch')
        cost=sum(d['totalCost'] for d in gens)
        expected_cost=sum(s[5]*.000001+s[6]*.000002 for s in case['steps'])
        assert math.isclose(cost,expected_cost,abs_tol=1e-8)
        sessions={d['metadata']['attributes.langfuse.session.id'] for d in data}
        assert sessions=={entry['session_id']}
        results.append({'case':case['name'],'trace_id':entry['trace_id'],'observations':len(data),
          'latency_seconds':root['latency'],'tokens':tokens,'synthetic_cost_usd':cost,'session_id':entry['session_id']})
    record={'batch_id':manifest['batch_id'],'readback_passed':True,'cases':results}
    Path(args.output).write_text(json.dumps(record,indent=2));print(json.dumps(record,indent=2))

if __name__=='__main__':main()
