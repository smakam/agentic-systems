"""Catalog v2 metadata and question-scoped prompt regression coverage."""
import asyncio
import copy
from datetime import timedelta
from marketplace.tools import ReadContext
from marketplace.db import Session, Conversation
from marketplace.agent import DatabaseSession, build_question_input
from test_integration import reset


def test_catalog_metadata_and_no_record_samples():
    ctx=ReadContext()
    try:
        envelope=ctx.catalog()
        assert envelope['status']=='ok'
        c=envelope['catalog']
        assert c['validation']['status']=='ok'
        assert c['catalog_version']=='2.0'
        assert not {'ontology','schema','business_names','relationships'} & envelope.keys()
        assert 'rows' not in envelope
        assert c['entities']['order_items']['fields']['quantity']['data_type']=='integer'
        assert c['entities']['shipments']['fields']['delivered_at']['nullable'] is True
        assert c['entities']['order_items']['fields']['quantity']['nullable'] is False
        checks=c['entities']['order_items']['constraints']
        assert any(x['kind']=='check' and 'quantity > 0' in x['definition'] for x in checks)
        assert any(x['kind']=='unique' for x in c['entities']['payouts']['constraints'])
        assert c['entities']['seller_balances']['fields']['unpaid']['nullable'] is None
        assert c['entities']['seller_balances']['constraints']==[]
        assert 'password_hash' not in str(c)
        assert 'snapshot' in envelope and 'snapshot' not in c
        assert c['catalog_hash']==ctx.catalog()['catalog']['catalog_hash']
    finally:ctx.close()


def test_catalog_drift_is_explicit_error():
    ctx=ReadContext()
    try:
        ctx.ontology=copy.deepcopy(ctx.ontology)
        ctx.ontology['entities']['order_items']['fields']['missing_field']='Stale definition'
        del ctx.ontology['entities']['orders']['fields']['status']
        ctx.ontology['relationships'].append({'from':'orders.missing','to':'customers.id','cardinality':'many-to-one'})
        result=ctx.catalog()
        assert result['status']=='error' and result['code']=='CATALOG_DRIFT'
        issues=result['catalog']['validation']['issues']
        assert any('missing_field' in x for x in issues)
        assert any('orders.status' in x for x in issues)
        assert any('orders.missing' in x for x in issues)
    finally:ctx.close()


def test_three_questions_keep_metadata_and_complete_tool_history():
    async def run():
        with Session.begin() as db:
            db.add(Conversation(id='prompt-three',owner_id='support',title='Prompt test',items=[]))
        session=DatabaseSession('prompt-three')
        ctx=ReadContext()
        snapshot=dict(ctx.snapshot); ctx.close()
        expected=[]
        for n in range(3):
            current={**snapshot,'revision':snapshot['revision']+n,'clock':snapshot['clock']+timedelta(hours=n)}
            message={'role':'user','content':build_question_input(f'Question {n+1}',current)}
            assert await session.get_items()==expected
            answer={'role':'assistant','content':f'Answer {n+1}'}
            call={'type':'function_call','name':'query_business_data','call_id':f'call-{n}','arguments':'{}'}
            result={'type':'function_call_output','call_id':f'call-{n}','output':'old rows'}
            await session.add_items([message,call,result,answer])
            expected.extend([message,call,result,answer])
        assert await session.get_items()==expected
        assert 'Question 1' in expected[0]['content'] and str(snapshot['clock']) in expected[0]['content']
    asyncio.run(run())


def test_question_metadata_follows_prefetched_evidence():
    text=build_question_input('Explain history',{'revision':7,'clock':'2026-10-01T12:00:00Z'},[{'current_records':{'rows':[]}}])
    assert text.index('current_records') < text.index('Application investigation metadata')
    assert text.endswith('"revision": 7}')


def test_transformed_view_does_not_inherit_base_constraints():
    from sqlalchemy import text
    from marketplace.db import init_schema
    with Session.begin() as db:
        db.execute(text('CREATE OR REPLACE VIEW analytics.orders AS SELECT id,customer_id,CAST(upper(status) AS varchar) AS status,created_at FROM public.orders'))
    ctx=ReadContext()
    try:
        result=ctx.catalog()
        assert result['code']=='CATALOG_DRIFT'
        entity=result['catalog']['entities']['orders']
        assert entity['constraints']==[]
        assert entity['fields']['status']['nullable'] is None
    finally:
        ctx.close()
        init_schema()


def test_session_window_keeps_complete_question_blocks_and_isolation():
    async def run():
        with Session.begin() as db:
            db.add(Conversation(id='window',owner_id='support',title='Window',items=[]))
            db.add(Conversation(id='other',owner_id='support',title='Other',items=[]))
        session=DatabaseSession('window')
        blocks=[]
        for n in range(8):
            block=[{'role':'user','content':f'Q{n}'},
                   {'type':'function_call','name':'get_catalog','call_id':str(n),'arguments':'{}'},
                   {'type':'function_call_output','call_id':str(n),'output':'{}'},
                   {'role':'assistant','content':f'A{n}'}]
            blocks.append(block); await session.add_items(block)
        assert await session.get_items()==sum(blocks[-6:],[])
        assert await session.get_items(limit=2)==blocks[-1]
        assert await session.get_items(limit=0)==[]
        assert await DatabaseSession('other').get_items()==[]
        assert await session.pop_item()==blocks[-1][-1]
        await session.clear_session()
        assert await session.get_items()==[]
    asyncio.run(run())
