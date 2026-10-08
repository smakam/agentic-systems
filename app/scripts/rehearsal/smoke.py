"""Paid clean-install checks against localhost; outputs no credentials/cookies."""
import http.cookiejar, json, time, urllib.request
from pathlib import Path
base='http://localhost:58000'
cookies=http.cookiejar.CookieJar(); http=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookies)); csrf=''
def call(path,body=None):
    headers={'Content-Type':'application/json','Origin':'http://localhost:5178'}
    if csrf: headers['x-csrf-token']=csrf
    req=urllib.request.Request(base+path,data=json.dumps(body).encode() if body is not None else None,headers=headers)
    with http.open(req,timeout=210) as r:return json.load(r)
def fresh():return call('/api/conversations',{'runtime':'sdk'})['id']
def ask(cid,q,**controls):
    r=call('/api/conversations/'+cid+'/ask',{'question':q,**controls})
    assert r['status']=='completed',r['answer']
    assert r['metrics'].get('trace_id'),'Missing trace reference'
    return r
report={'host':'fresh Ubuntu VM','checks':[],'runs':[]}
assert call('/api/health')['status']=='ok'
x=call('/api/login',{'username':'operator','password':'demo-marketplace'}); csrf=x['csrf']
ready=call('/api/readiness'); assert ready['indexed']==ready['documents']>0,ready
report['readiness']=ready
cid=fresh(); r=ask(cid,'What products, quantities and sellers are in order-1?'); low=r['answer'].lower()
assert all(x in low for x in ['canvas','desk','cedar','northstar']),r['answer']
report['runs'].append(r); report['checks'].append('seeded order question and evidence')
r=ask(cid,'What is the total quantity of those items?'); assert '4' in r['answer'] or 'four' in r['answer'].lower(),r['answer']
report['runs'].append(r); report['checks'].append('same-conversation follow-up')
r=ask(fresh(),'What does the payout policy require before a seller can be paid?')
assert '24' in r['answer'] and 'deliver' in r['answer'].lower() and r['evidence'],r['answer']
assert any(x.get('type')=='documents' and x.get('method')=='pgvector_cosine' for x in r['evidence'].values()), 'Policy run did not provide vector retrieval evidence'
report['runs'].append(r); report['checks'].append('policy question with vector retrieval and citations')
run_id=report['runs'][0]['id']
call('/api/conversations/'+cid+'/runs/'+run_id+'/feedback',{'rating':'down'})
rows=call('/api/conversations/'+cid+'/runs'); assert next(x for x in rows if x['id']==run_id)['feedback']=='down'
call('/api/conversations/'+cid+'/runs/'+run_id+'/feedback',{'rating':'up'})
rows=call('/api/conversations/'+cid+'/runs'); assert next(x for x in rows if x['id']==run_id)['feedback']=='up'
report['checks'].append('feedback persists and vote changes')
p=Path('/tmp/learner-rehearsal-smoke.json'); p.write_text(json.dumps(report,indent=2))
print(json.dumps({'checks':report['checks'],'runs':len(report['runs']),'retrieval':ready['retrieval'],'receipt':str(p)}))
