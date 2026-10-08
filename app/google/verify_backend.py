"""Check deployed MCP configuration and one fresh business investigation."""
import asyncio
import json
import re
import subprocess
import urllib.request
from pathlib import Path
import agentplatform

async def main():
    settings=json.loads(Path('deployment.json').read_text())
    profile=json.loads(Path('backend_profiles.json').read_text())['cloud']
    name=settings['resource_name']
    token=subprocess.check_output(['gcloud','auth','print-access-token'],text=True).strip()
    request=urllib.request.Request('https://us-central1-aiplatform.googleapis.com/v1/'+name,
        headers={'Authorization':'Bearer '+token})
    with urllib.request.urlopen(request) as response:
        metadata=json.load(response)
    spec=metadata['spec']['deploymentSpec']
    env={x['name']:x for x in spec['env']}
    secrets={x['name']:x for x in spec['secretEnv']}
    assert env['REMOTE_MCP_URL']['value']==profile['url'], 'Deployed URL differs from cloud profile'
    ref=secrets['REMOTE_MCP_API_KEY']['secretRef']
    assert ref['secret']==profile['secret'] and ref['version']==profile['version'], 'Deployed secret reference differs'
    print('DEPLOYED_CLOUD_PROFILE_VERIFIED',flush=True)
    client=agentplatform.Client(project=settings['project'],location=settings['location'])
    runtime=client.runtimes.get(name=name)
    user='course-cloud-profile-check'
    session=await runtime.async_create_session(user_id=user,state={'memory_enabled':False})
    events=[]
    async for event in runtime.async_stream_query(user_id=user,session_id=session['id'],
        message='Why is the payout for order-2 held? Check current records and the applicable payout policy.',
        state_delta={'memory_enabled':False},run_config={'max_llm_calls':12}):
        events.append(event)
        if event.get('error_code') or event.get('error_message'):
            raise RuntimeError('Hosted query returned an error')
        for part in (event.get('content') or {}).get('parts',[]):
            call=part.get('function_call')
            if call: print('TOOL',call['name'],flush=True)
            if part.get('text'): print('ANSWER',part['text'],flush=True)
    result={'backend':'cloud','mcp_url':profile['url'],'session':session['id'],'events':events}
    Path('cloud-profile-acceptance.json').write_text(json.dumps(result,indent=2,default=str)+'\n')
    responses=[p['function_response'] for e in events for p in (e.get('content') or {}).get('parts',[]) if p.get('function_response')]
    assert responses and all(r.get('response', {}).get('isError') is False for r in responses), 'MCP tool response failed'
    calls=[p['function_call']['name'] for e in events for p in (e.get('content') or {}).get('parts',[]) if p.get('function_call')]
    required={'begin_investigation','get_order_history','search_documents','end_investigation'}
    assert required.issubset(calls), 'Required investigation tools missing'
    texts=[p['text'] for e in events for p in (e.get('content') or {}).get('parts',[]) if p.get('text')]
    assert any('[evidence:' in t for t in texts), 'No cited answer returned'
    # Grade the model's snapshot claim against actual tool metadata, not a fixed fixture.
    snapshots=[]
    for response in responses:
        if response.get('name') != 'begin_investigation':
            continue
        for content in response.get('response', {}).get('content', []):
            if content.get('type') == 'text':
                payload=json.loads(content['text'])
                if payload.get('status') == 'ok':
                    snapshots.append(payload['snapshot'])
    assert snapshots, 'No authoritative investigation snapshot returned'
    snapshot=snapshots[-1]
    answer=re.sub(r'[*_`]', '', texts[-1])
    revisions=re.findall(r'\brevision\s*[:#]?\s*(\d+)\b', answer, re.I)
    assert revisions and all(int(value)==snapshot['revision'] for value in revisions), 'Answer revision differs from tool snapshot'
    assert snapshot['clock'][:10] in answer, 'Answer omits current tool snapshot date'
    print('ANSWER_SNAPSHOT_VERIFIED', json.dumps(snapshot), flush=True)
    print('CLOUD_BACKEND_ACCEPTANCE_FINISHED',flush=True)

if __name__=='__main__':
    try: asyncio.run(main())
    except Exception as error:
        print('VERIFICATION_FAILED',type(error).__name__,flush=True)
        raise SystemExit(1)
