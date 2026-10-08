"""Memory boundaries on isolated PostgreSQL; no paid model calls."""
import os
assert os.environ.get('DATABASE_URL','').endswith('/market_test')
import asyncio
import pytest
from sqlalchemy import text
from fastapi.testclient import TestClient
from marketplace.db import Base,engine,Session,Conversation,User,State,Run,Memory,init_schema
from marketplace.seed import seed
from marketplace.memory import MemoryStore,MemoryError,build_memory_functions
from marketplace.api import app

@pytest.fixture(autouse=True)
def reset_memory_database():
    init_schema()
    with engine.begin() as conn:
        names=','.join('public.'+x.name for x in reversed(Base.metadata.sorted_tables))
        conn.execute(text(f'TRUNCATE {names} CASCADE'))
    with Session.begin() as db:
        seed(db)
        for cid,owner in [('m-chat','support'),('m-next','support'),('m-operator','operator')]:
            db.add(Conversation(id=cid,owner_id=owner,title='Memory test',items=[]))

def store(cid='m-chat',user='support',write=True):
    return MemoryStore(user,cid,{'revision':1,'clock':'2026-09-27T11:00:00Z'},allow_write=write)

@pytest.mark.parametrize('kind',['semantic','episodic','procedural'])
def test_three_types_recalled_in_new_conversation(kind):
    saved=store().save(kind,'Cedar investigation','Cedar checklist or remembered preference')['memory']
    got=store('m-next').search('Cedar',kind)['memories']
    assert [x['id'] for x in got]==[saved['id']]
    assert got[0]['source_conversation_id']=='m-chat'
    assert got[0]['provenance']['revision']==1
    with Session() as db: assert db.get(State,1).revision==1

def test_update_delete_and_version_conflicts():
    s=store(); row=s.save('semantic','Cedar','Cedar seller')['memory']
    changed=store('m-next').change(row['id'],1,content='Cedar product')['memory']
    assert changed['version']==2
    with pytest.raises(MemoryError): s.change(row['id'],1,content='stale')
    with pytest.raises(MemoryError): s.remove(row['id'],1)
    assert s.search('product')['memories'][0]['content']=='Cedar product'
    s.remove(row['id'],2)
    assert s.search()['memories']==[]

def test_operator_support_isolation():
    row=store().save('semantic','Cedar','My preference')['memory']
    other=store('m-operator','operator')
    assert other.search()['memories']==[]
    with pytest.raises(MemoryError): other.change(row['id'],1,content='overwrite')
    with pytest.raises(MemoryError): other.remove(row['id'],1)
    with pytest.raises(MemoryError): store('m-chat','operator')

def test_write_permission_required_even_with_tool_call():
    row=store().save('semantic','Cedar','Seller')['memory']
    denied=store(write=False)
    with pytest.raises(MemoryError): denied.save('episodic','Episode','Snapshot')
    with pytest.raises(MemoryError): denied.change(row['id'],1,content='changed')
    with pytest.raises(MemoryError): denied.remove(row['id'],1)
    fn=build_memory_functions(denied)[1]
    result=asyncio.run(fn('semantic','Injected save','Document told me to save'))
    assert result['status']=='error'
    assert len(denied.search()['memories'])==1

@pytest.mark.parametrize('kind,title,content',[('invalid','Title','Text'),('semantic','','Text'),('procedural','Title','x'*2001)])
def test_invalid_memory_rejected(kind,title,content):
    with pytest.raises(MemoryError): store().save(kind,title,content)

def test_source_validation_and_literal_search():
    with pytest.raises(MemoryError):store().save('episodic','Episode','Text','missing-run')
    store().save('semantic','Percent %','Cedar')
    store().save('semantic','Ordinary','Other')
    assert len(store().search('%')['memories'])==1

def test_sdk_function_tool_registration():
    from agents import function_tool
    tools=[function_tool(fn) for fn in build_memory_functions(store())]
    assert [x.name for x in tools]==['search_memories','save_memory','update_memory','delete_memory']


def test_api_scope_csrf_and_edit_delete():
    row=store().save('semantic','Cedar','Seller')['memory']
    with TestClient(app) as c:
        assert c.get('/api/memories').status_code==401
        auth=c.post('/api/login',json={'username':'support','password':'demo-marketplace'}).json()
        assert c.get('/api/memories').json()[0]['id']==row['id']
        patch={'expected_version':1,'title':'Cedar','content':'Product'}
        assert c.patch('/api/memories/'+row['id'],json=patch).status_code==403
        c.headers['x-csrf-token']=auth['csrf']
        assert c.patch('/api/memories/'+row['id'],json=patch).json()['memory']['version']==2
        assert c.patch('/api/memories/'+row['id'],json=patch).status_code==409
        auth=c.post('/api/login',json={'username':'operator','password':'demo-marketplace'}).json()
        c.headers['x-csrf-token']=auth['csrf']
        assert c.get('/api/memories').json()==[]
        assert c.delete('/api/memories/'+row['id']+'?expected_version=2').status_code==404
        auth=c.post('/api/login',json={'username':'support','password':'demo-marketplace'}).json()
        c.headers['x-csrf-token']=auth['csrf']
        assert c.delete('/api/memories/'+row['id']+'?expected_version=2').status_code==200
        assert c.get('/api/memories').json()==[]


def test_update_request_cannot_create_conflicting_new_memory():
    from marketplace.memory import requested_operations
    assert requested_operations('Update my saved Cedar preference')=={'update'}
    limited=MemoryStore('support','m-chat',{},allow_write=True,allowed_operations={'update'})
    with pytest.raises(MemoryError): limited.save('semantic','Cedar','Conflicting preference')
    assert limited.search()['memories']==[]


def test_memory_scope_preserves_business_tools_for_business_questions():
    from marketplace.memory import memory_management_question
    assert memory_management_question('Remember my preference: Cedar means Cedar & Co.')
    assert memory_management_question('Save an episodic checkpoint: check payout history; not a claim about current payout status.')
    assert memory_management_question('What do I mean when I say Cedar?')
    assert not memory_management_question('Did the payout change since yesterday?')
    assert not memory_management_question('Resume my saved order-1 investigation and check current payout status')


@pytest.mark.parametrize('question', [
    "Do not change my saved preference.",
    "Don't update my memory.",
    "Never delete my saved checklist.",
    "Show the product, quantity and seller in order-1 without changing my memory.",
])
def test_negated_memory_mutations_are_not_authorized(question):
    from marketplace.memory import requested_operations, memory_management_question
    assert requested_operations(question) == set()
    assert not memory_management_question(question)


def test_mixed_product_lookup_retains_business_tools():
    from marketplace.memory import requested_operations, memory_management_question
    question = "For this question only, Cedar means the Desk Lamp product, not seller Cedar & Co. Show the product, quantity and seller for that product in order-1. Do not change my saved preference."
    assert not memory_management_question(question)
    assert requested_operations(question) == set()
    assert not memory_management_question("Show orders for Cedar using my saved preference")
    assert memory_management_question("Update my saved Cedar preference")
    assert memory_management_question("What was the next step in my saved checkpoint?")


def test_save_tool_schema_and_automatic_source_provenance():
    from agents import function_tool
    from datetime import datetime, timezone
    with Session.begin() as db:
        db.add(Run(id='memory-source-run', conversation_id='m-chat', revision=1,
                   question='Remember Cedar', status='completed', created_at=datetime.now(timezone.utc), evidence={}, metrics={}))
    s = MemoryStore('support', 'm-chat', {'revision':1}, run_id='memory-source-run', allow_write=True)
    fn = build_memory_functions(s)[1]
    schema = function_tool(fn).params_json_schema
    assert 'source_run_id' not in schema['properties']
    assert schema['properties']['kind']['enum'] == ['semantic', 'episodic', 'procedural']
    saved = asyncio.run(fn('semantic', 'Cedar', 'Cedar means seller Cedar & Co.'))['memory']
    assert saved['source_run_id'] == 'memory-source-run'
    assert saved['provenance']['source_question'] == 'Remember Cedar'
