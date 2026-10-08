"""Real stdio transport tests against the isolated seeded test database."""
import asyncio
import json
from marketplace.mcp_client import open_mcp, RemoteReadContext
from marketplace.tools import ReadContext
from marketplace.tool_contracts import build_tool_functions
from test_integration import reset


def normalize(value):
    if isinstance(value, dict):
        return {k: normalize(v) for k,v in value.items() if k not in ('handle','elapsed_ms')}
    if isinstance(value,list): return [normalize(v) for v in value]
    return json.loads(json.dumps(value,default=str))


def test_mcp_contracts_evidence_and_rejections():
    async def run():
        direct=ReadContext()
        try:
            funcs={f.__name__:f for f in build_tool_functions(direct)}
            async with open_mcp() as server:
                assert {t.name for t in await server.list_tools()}==set(funcs)
                remote=await RemoteReadContext.create(server)
                assert normalize(remote.snapshot)==normalize(direct.snapshot)
                for name,args in [
                    ('get_catalog',{}),
                    ('query_business_data',{'sql':'SELECT id,status FROM orders ORDER BY id'}),
                    ('get_order_history',{'order_id':'order-1'}),
                    ('search_documents',{'query':'refund return policy'}),
                    ('query_business_data',{'sql':'DELETE FROM orders'}),
                    ('query_business_data',{'sql':'SELECT * FROM orders','parameters_json':'[]'}),
                    ('fetch_evidence',{'handle':'unknown'}),
                ]:
                    expected=await funcs[name](**args)
                    result=await server.call_tool(name,args)
                    assert not result.is_error
                    actual=json.loads(result.content[0].text)
                    assert normalize(actual)==normalize(expected),name
                    if 'handle' in actual:
                        fetched=await server.call_tool('fetch_evidence',{'handle':actual['handle']})
                        assert json.loads(fetched.content[0].text)==actual
                await remote.refresh()
                assert remote.evidence
                handle=next(iter(remote.evidence))
            async with open_mcp() as other:
                result=await other.call_tool('fetch_evidence',{'handle':handle})
                assert json.loads(result.content[0].text)['status']=='error'
        finally:
            direct.close()
    asyncio.run(run())


def test_mcp_snapshot_and_budget():
    from marketplace.db import Session, State
    async def run():
        async with open_mcp() as server:
            remote=await RemoteReadContext.create(server)
            revision=remote.snapshot['revision']
            with Session.begin() as db:
                db.get(State,1).revision+=1
            result=await server.call_tool('query_business_data',{'sql':'SELECT revision FROM freshness'})
            assert json.loads(result.content[0].text)['rows'][0]['revision']==revision
            for _ in range(23):
                await server.call_tool('query_business_data',{'sql':'SELECT revision FROM freshness'})
            result=await server.call_tool('query_business_data',{'sql':'SELECT revision FROM freshness'})
            assert json.loads(result.content[0].text)['status']=='error'
    asyncio.run(run())


def test_concurrent_mcp_runs_are_isolated():
    async def run():
        ready=asyncio.Event()
        handles=[]
        async def one():
            async with open_mcp() as server:
                result=await server.call_tool('get_catalog',{})
                handle=json.loads(result.content[0].text)['handle']
                handles.append(handle)
                if len(handles)==2: ready.set()
                await asyncio.wait_for(ready.wait(),10)
                other=next(h for h in handles if h!=handle)
                rejected=await server.call_tool('fetch_evidence',{'handle':other})
                assert json.loads(rejected.content[0].text)['status']=='error'
                own=await server.call_tool('fetch_evidence',{'handle':handle})
                assert json.loads(own.content[0].text)['handle']==handle
        await asyncio.gather(one(),one())
    asyncio.run(run())


def test_interrupted_mcp_run_reports_failure_and_next_run_recovers(monkeypatch):
    from marketplace import agent
    from marketplace.db import Session,Conversation,Run
    from types import SimpleNamespace
    with Session.begin() as db:
        db.add(Conversation(id='mcp-disconnect',owner_id='support',title='Test',items=[]))
    original=agent.open_mcp
    def dying_server():
        server=original()
        server.params.args=['-c',
            'import os; from marketplace import mcp_server; '
            'mcp_server.ReadContext.catalog=lambda self: os._exit(17); mcp_server.main()']
        return server
    async def invoke(instance,*args,**kwargs):
        await instance.mcp_servers[0].call_tool('get_catalog',{})
        return SimpleNamespace(final_output='Recovered',context_wrapper=SimpleNamespace(usage=SimpleNamespace(requests=0,input_tokens=0,output_tokens=0,total_tokens=0)))
    monkeypatch.setattr(agent.Runner,'run',invoke)
    monkeypatch.setattr(agent,'open_mcp',dying_server)
    async def run():
        result=await agent.answer('mcp-disconnect','Test',evaluation_config={'tool_transport':'mcp','model':'test'})
        assert result['status']=='failed'
        assert 'interrupted' in result['answer']
        with Session() as db: assert db.get(Run,result['id']).status=='failed'
        monkeypatch.setattr(agent,'open_mcp',original)
        result=await agent.answer('mcp-disconnect','Retry',evaluation_config={'tool_transport':'mcp','model':'test'})
        assert result['status']=='completed'
        assert result['evidence']
    asyncio.run(run())
