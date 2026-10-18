"""RAG demo boundaries and API access; no fixture reset or provider calls."""
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from marketplace import api, rag_policy_demo as demo

def test_paragraph_and_overlap_keep_adjacent_rules_and_source_ranges():
    body=demo.DOCUMENTS['expanded']
    paragraphs=demo.chunk_document(body,'paragraph')
    overlap=demo.chunk_document(body,'overlap')
    rule=next(p for p in paragraphs if 'waiting period is 24 hours' in p['body'])
    extra=next(p for p in paragraphs if 'add a further 48 hours' in p['body'])
    assert rule['line_end'] < extra['line_start']
    assert not any('waiting period is 24 hours' in p['body'] and 'add a further 48 hours' in p['body'] for p in paragraphs)
    together=next(p for p in overlap if 'waiting period is 24 hours' in p['body'] and 'add a further 48 hours' in p['body'])
    assert together['line_start']==rule['line_start'] and together['line_end']==extra['line_end']
    assert len(paragraphs)==len(overlap)

@pytest.mark.parametrize('experiment,version,strategy',[
    ('versions','expanded','paragraph'),('versions','v1','overlap'),('chunking','v2','paragraph')])
def test_invalid_combinations_rejected_before_storage(experiment,version,strategy):
    with pytest.raises(demo.DemoError): demo.select_source(None,'owner',experiment,version,strategy)

@pytest.mark.parametrize('path,method,body',[
    ('versions','get',None),('versions/source','post',{'version':'v2'}),
    ('versions/index','post',{}),('versions/restore','post',{}),
    ('chunking/ask','post',{'question':'Eligible?','top_k':1})])
def test_demo_unavailable_outside_test(monkeypatch,path,method,body):
    monkeypatch.setattr(demo,'enabled',lambda:False)
    api.app.dependency_overrides[api.identity]=lambda:SimpleNamespace(id='operator',role='operator')
    try:
        client=TestClient(api.app)
        result=getattr(client,method)('/api/rag-policy-demo/'+path,**({'json':body} if body is not None else {}))
        assert result.status_code==404
    finally: api.app.dependency_overrides.clear()

@pytest.mark.parametrize('user_role',['buyer','seller'])
def test_non_support_roles_cannot_use_demo(monkeypatch,user_role):
    monkeypatch.setattr(demo,'enabled',lambda:True)
    api.app.dependency_overrides[api.identity]=lambda:SimpleNamespace(id='user',role=user_role)
    try: assert TestClient(api.app).get('/api/rag-policy-demo/versions').status_code==403
    finally: api.app.dependency_overrides.clear()


def test_embedding_failure_does_not_replace_working_index(monkeypatch):
    import asyncio
    from unittest.mock import AsyncMock
    row=SimpleNamespace(source_version='v2',strategy='paragraph',indexed_version='v1',indexed_strategy='paragraph')
    monkeypatch.setattr(demo,'locked_state',lambda *args:row)
    api_client=SimpleNamespace(embeddings=SimpleNamespace(create=AsyncMock(side_effect=RuntimeError('provider unavailable'))),close=AsyncMock())
    monkeypatch.setattr(demo,'client',lambda:api_client)
    db=SimpleNamespace(query=lambda *args:pytest.fail('Previous chunks must not be deleted before embedding succeeds'))
    with pytest.raises(RuntimeError):asyncio.run(demo.index_selected(db,'owner','versions'))
    assert row.indexed_version=='v1' and row.indexed_strategy=='paragraph'
    api_client.close.assert_awaited_once()
