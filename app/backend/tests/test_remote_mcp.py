"""Real HTTP MCP protocol and PostgreSQL isolation tests; no paid model calls."""
import json
from starlette.testclient import TestClient
from marketplace.remote_mcp import create_app, Investigations
from test_integration import reset

TOKEN='test-only-remote-mcp-key-0123456789abcdef'
HEADERS={'x-api-key':TOKEN,'accept':'application/json, text/event-stream','content-type':'application/json'}
def rpc(client,method,params=None):
    response=client.post('/mcp',headers=HEADERS,json={'jsonrpc':'2.0','id':1,'method':method,'params':params or {}})
    assert response.status_code==200,response.text
    body=response.json(); assert 'error' not in body,body
    return body['result']
def tool(client,name,**arguments):
    value=rpc(client,'tools/call',{'name':name,'arguments':arguments})
    assert not value.get('isError'),value
    return json.loads(value['content'][0]['text'])

def test_http_auth_and_tool_surface():
    with TestClient(create_app(TOKEN)) as client:
        for headers in ({},{'x-api-key':'wrong'}):
            assert client.post('/mcp',headers=headers,json={}).status_code==401
        initialized=rpc(client,'initialize',{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'test','version':'1'}})
        assert initialized['serverInfo']['name']=='Marketplace support read tools'
        tools=rpc(client,'tools/list')['tools']
        assert {t['name'] for t in tools}=={'begin_investigation','end_investigation','get_catalog','query_business_data','search_documents','fetch_evidence','get_order_history'}
        assert client.post('/mcp',headers={**HEADERS,'host':'untrusted.example'},json={'jsonrpc':'2.0','id':1,'method':'tools/list'}).status_code==421
        assert client.post('/mcp',headers={**HEADERS,'origin':'https://untrusted.example'},json={'jsonrpc':'2.0','id':1,'method':'tools/list'}).status_code==403

def test_http_snapshot_evidence_isolation_rejections_and_cleanup():
    from marketplace.db import Session,State
    registry=Investigations()
    with TestClient(create_app(TOKEN,registry=registry)) as client:
        first=tool(client,'begin_investigation'); a=first['investigation_id']
        catalog=tool(client,'get_catalog',investigation_id=a)
        assert catalog['status']=='ok'
        with Session.begin() as db: db.get(State,1).revision+=1
        second=tool(client,'begin_investigation'); b=second['investigation_id']
        assert second['snapshot']['revision']==first['snapshot']['revision']+1
        rows=tool(client,'query_business_data',investigation_id=a,sql='SELECT revision FROM freshness')
        assert rows['rows'][0]['revision']==first['snapshot']['revision']
        assert tool(client,'fetch_evidence',investigation_id=a,handle=catalog['handle'])==catalog
        assert tool(client,'fetch_evidence',investigation_id=b,handle=catalog['handle'])['status']=='error'
        assert tool(client,'query_business_data',investigation_id=a,sql='DELETE FROM orders')['status']=='error'
        history=tool(client,'get_order_history',investigation_id=a,order_id='order-1')
        assert history['event_timeline']['status'] in ('ok','empty')
        assert history['order_summary']['rows'][0]['order_status']=='paid'
        assert history['order_summary']['rows'][0]['payment_status']=='captured'
        assert tool(client,'fetch_evidence',investigation_id=a,handle=history['order_summary']['handle'])==history['order_summary']
        missing=tool(client,'get_order_history',investigation_id=a,order_id='does-not-exist')
        assert missing['order_summary']['status']=='empty'
        documents=tool(client,'search_documents',investigation_id=a,query='refund policy')
        assert documents['status']=='ok' and documents['chunks']
        assert tool(client,'end_investigation',investigation_id=a)['closed']
        assert tool(client,'fetch_evidence',investigation_id=a,handle=catalog['handle'])['code']=='INVESTIGATION_UNAVAILABLE'
    assert not registry.runs

def test_expiry_capacity_and_restart():
    now=[0]; registry=Investigations(ttl=5,limit=1,clock=lambda:now[0])
    with TestClient(create_app(TOKEN,registry=registry)) as client:
        first=tool(client,'begin_investigation')
        assert tool(client,'begin_investigation')['code']=='CAPACITY'
        now[0]=6
        assert tool(client,'get_catalog',investigation_id=first['investigation_id'])['code']=='INVESTIGATION_UNAVAILABLE'
        assert tool(client,'begin_investigation')['status']=='ok'
