"""Real local memory MCP boundaries; isolated PostgreSQL and no model charges."""
import asyncio
import json
from datetime import datetime, timezone
from types import SimpleNamespace
import pytest
from test_memory import reset_memory_database
from marketplace.db import Session,Run
from marketplace.mcp_client import open_memory_mcp,LocalMemoryContext

async def call(server,name,args):
    result=await server.call_tool(name,args)
    assert not result.is_error
    return json.loads(result.content[0].text)

@pytest.mark.parametrize('kind',['semantic','episodic','procedural'])
def test_stdio_save_recall_isolation_permissions_and_versions(kind):
    with Session.begin() as db:
        db.add(Run(id='memory-mcp-source',conversation_id='m-chat',revision=1,
            question='Remember Cedar',status='running',created_at=datetime.now(timezone.utc),evidence={},metrics={}))
    async def run():
        async with open_memory_mcp('support','m-chat',{'revision':1},run_id='memory-mcp-source',allow_write=True,allowed_operations={'save'}) as server:
            tools={x.name:x for x in await server.list_tools()}
            assert set(tools)=={'search_memories','save_memory','update_memory','delete_memory'}
            assert 'owner_id' not in tools['search_memories'].input_schema['properties']
            assert 'source_run_id' not in tools['save_memory'].input_schema['properties']
            saved=(await call(server,'save_memory',{'kind':kind,'title':'Cedar','content':'Cedar means seller Cedar & Co.'}))['memory']
            assert saved['source_run_id']=='memory-mcp-source'
            audit=LocalMemoryContext(server);await audit.refresh()
            assert audit.operations[0]['operation']=='save'
        async with open_memory_mcp('support','m-next',{},allow_write=False) as server:
            got=await call(server,'search_memories',{'query':'Cedar'})
            assert got['memories'][0]['id']==saved['id']
            assert (await call(server,'save_memory',{'kind':'semantic','title':'Forbidden','content':'Should not persist'}))['status']=='error'
        async with open_memory_mcp('operator','m-operator',{},allow_write=True,allowed_operations={'update','delete'}) as server:
            assert (await call(server,'search_memories',{}))['memories']==[]
            assert (await call(server,'delete_memory',{'memory_id':saved['id'],'expected_version':1}))['status']=='error'
        async with open_memory_mcp('support','m-next',{},allow_write=True,allowed_operations={'update'}) as server:
            changed=await call(server,'update_memory',{'memory_id':saved['id'],'expected_version':1,'title':'Cedar','content':'Corrected preference'})
            assert changed['memory']['version']==2
            assert (await call(server,'update_memory',{'memory_id':saved['id'],'expected_version':1,'title':'Cedar','content':'Stale overwrite'}))['status']=='error'
            assert (await call(server,'delete_memory',{'memory_id':saved['id'],'expected_version':2}))['status']=='error'
        async with open_memory_mcp('support','m-next',{},allow_write=True,allowed_operations={'delete'}) as server:
            assert (await call(server,'delete_memory',{'memory_id':saved['id'],'expected_version':2}))['status']=='ok'
            assert (await call(server,'search_memories',{}))['memories']==[]
    asyncio.run(run())

@pytest.mark.parametrize('business_transport',['mcp','direct'])
def test_agent_memory_uses_stdio_and_retains_business_scope(monkeypatch,business_transport):
    from marketplace import agent
    async def invoke(instance,*args,**kwargs):
        assert not any(x.name in ('search_memories','save_memory','update_memory','delete_memory') for x in instance.tools)
        server=next(x for x in instance.mcp_servers if x.name=='Marketplace personal memory')
        assert await call(server,'search_memories',{'query':'Cedar'})
        business=[x for x in instance.mcp_servers if x.name=='Marketplace read tools']
        assert bool(business)==(business_transport=='mcp')
        return SimpleNamespace(final_output='Checked',context_wrapper=SimpleNamespace(usage=SimpleNamespace(requests=0,input_tokens=0,output_tokens=0,total_tokens=0)))
    monkeypatch.setattr(agent.Runner,'run',invoke)
    result=asyncio.run(agent.answer('m-chat','Show orders for Cedar using my saved preference',memory_enabled=True,evaluation_config={'tool_transport':business_transport,'model':'test'}))
    assert result['status']=='completed'
    assert result['metrics']['memory_tool_transport']=='mcp'
    assert result['metrics']['memory_operations'][0]['operation']=='search'
    assert not result['metrics']['memory_management_scope']


def test_memory_only_scope_and_start_failure_are_recorded(monkeypatch):
    from marketplace import agent
    async def invoke(instance,*args,**kwargs):
        assert [x.name for x in instance.mcp_servers]==['Marketplace personal memory']
        assert instance.tools==[]
        await call(instance.mcp_servers[0],'search_memories',{})
        return SimpleNamespace(final_output='No saved memory',context_wrapper=SimpleNamespace(usage=SimpleNamespace(requests=0,input_tokens=0,output_tokens=0,total_tokens=0)))
    monkeypatch.setattr(agent.Runner,'run',invoke)
    config={'tool_transport':'mcp','model':'test'}
    result=asyncio.run(agent.answer('m-chat','What do I mean when I say Cedar?',memory_enabled=True,evaluation_config=config))
    assert result['status']=='completed'
    original=agent.open_memory_mcp
    def broken(*args,**kwargs):
        server=original(*args,**kwargs);server.params.args=['-c','raise SystemExit(17)'];return server
    monkeypatch.setattr(agent,'open_memory_mcp',broken)
    result=asyncio.run(agent.answer('m-chat','What do I mean when I say Cedar?',memory_enabled=True,evaluation_config=config))
    assert result['status']=='failed'
    assert 'memory tool connection could not start' in result['answer']
    with Session() as db:assert db.get(Run,result['id']).status=='failed'


def test_memory_connection_loss_is_not_reported_as_success(monkeypatch):
    from marketplace import agent
    original=agent.open_memory_mcp
    def dying(*args,**kwargs):
        server=original(*args,**kwargs)
        server.params.args=['-c','import os; from marketplace import memory_mcp_server; memory_mcp_server.MemoryStore.search=lambda *args,**kwargs: os._exit(17); memory_mcp_server.main()']
        return server
    async def invoke(instance,*args,**kwargs):
        await instance.mcp_servers[0].call_tool('search_memories',{})
        raise AssertionError('Disconnected server must not produce a result')
    monkeypatch.setattr(agent,'open_memory_mcp',dying)
    monkeypatch.setattr(agent.Runner,'run',invoke)
    result=asyncio.run(agent.answer('m-chat','What do I mean when I say Cedar?',memory_enabled=True,evaluation_config={'tool_transport':'direct','model':'test'}))
    assert result['status']=='failed'
    assert result['metrics']['memory_operations_status']=='MCP synchronization failed'
    assert 'Memory operations could not be verified' in result['answer']
