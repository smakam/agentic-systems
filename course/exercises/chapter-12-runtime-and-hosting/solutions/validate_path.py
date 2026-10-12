"""Exercise the local chat -> cloud agent -> laptop MCP path, then follow up."""
import argparse,http.cookiejar,json,re,urllib.error,urllib.request
from pathlib import Path
def main():
    p=argparse.ArgumentParser();p.add_argument('--url',default='http://localhost:5192');p.add_argument('--output',required=True);a=p.parse_args()
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()));csrf=None
    def call(path,value=None):
        headers={'Origin':a.url,'Content-Type':'application/json'}
        if csrf:headers['x-csrf-token']=csrf
        request=urllib.request.Request(a.url+path,data=None if value is None else json.dumps(value).encode(),headers=headers)
        with opener.open(request,timeout=180) as r:return json.load(r)
    login=call('/api/login',{'username':'support','password':'demo-marketplace'});csrf=login['csrf']
    cid=call('/api/conversations',{'runtime':'sdk'})['id']
    result={'conversation_id':cid,'turns':[]}
    for question in ['Why is the payout for order-2 held? Cite the order facts and applicable policy.',
                     'What delivery condition must change before that payout can be released? Cite the evidence.']:
        run=call('/api/conversations/'+cid+'/ask',{'question':question,'memory_enabled':False})
        assert run['status']=='completed'
        metrics=run['metrics'];assert metrics['model_route']=='direct_openai' and metrics['tool_transport']=='mcp_http'
        assert metrics['investigation_cleanup_confirmed'] and metrics['actual_tool_invocations']>0
        handles=re.findall(r'\[evidence:([^\]]+)\]',run['answer'])
        assert handles and all(h in run['evidence'] for h in handles)
        result['turns'].append({'question':question,'run':run})
        Path(a.output).write_text(json.dumps(result,indent=2));print(json.dumps({'id':run['id'],'status':run['status'],'metrics':metrics}),flush=True)
    saved=call('/api/conversations/'+cid+'/runs');assert len(saved)==2
    result['local_history_and_runs_saved']=True
    Path(a.output).write_text(json.dumps(result,indent=2))
if __name__=='__main__':main()
