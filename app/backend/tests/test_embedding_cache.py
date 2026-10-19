"""Document cache cost boundaries; no provider or application database calls."""
import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock
import pytest
from marketplace import embedding_cache as cache

@pytest.fixture
def cached(monkeypatch):
    rows={}
    class DB:
        def __enter__(self):self.pending={};return self
        def __exit__(self,kind,*args):
            if kind is None:rows.update(self.pending)
        def scalar(self,statement):return True
        def scalars(self,statement):
            keys=next(iter(statement.compile().params.values()))
            return SimpleNamespace(all=lambda:[SimpleNamespace(key=k,embedding=rows[k]) for k in keys if k in rows])
        def add(self,row):self.pending[row.key]=row.embedding
    monkeypatch.setattr(cache,'Session',SimpleNamespace(begin=DB))
    calls=[]
    async def embed(**kwargs):
        calls.append(kwargs['input'])
        return SimpleNamespace(data=[SimpleNamespace(index=i,embedding=[float(i)]*1536) for i,_ in enumerate(kwargs['input'])])
    api=SimpleNamespace(embeddings=SimpleNamespace(create=AsyncMock(side_effect=embed)),close=AsyncMock())
    monkeypatch.setattr(cache,'client',lambda:api)
    return rows,calls,api

def test_repeated_text_and_return_to_prior_version_do_not_pay_again(cached):
    rows,calls,api=cached
    first=asyncio.run(cache.vectors(['standard','exception','standard']))
    assert len(calls)==1 and calls[0]==['standard','exception'] and first[0]==first[2]
    asyncio.run(cache.vectors(['changed policy']))
    asyncio.run(cache.vectors(['standard','exception']))
    assert len(calls)==2

def test_only_changed_chunk_is_embedded(cached):
    rows,calls,api=cached
    asyncio.run(cache.vectors(['unchanged','old']))
    asyncio.run(cache.vectors(['unchanged','new']))
    assert calls[-1]==['new']

def test_model_revision_invalidates_cache(cached,monkeypatch):
    rows,calls,api=cached
    asyncio.run(cache.vectors(['same']))
    monkeypatch.setenv('EMBEDDING_MODEL_REVISION','new-model:1536:v2')
    asyncio.run(cache.vectors(['same']))
    assert len(calls)==2

def test_provider_failure_does_not_publish_partial_cache(cached):
    rows,calls,api=cached
    asyncio.run(cache.vectors(['working']))
    before=dict(rows)
    api.embeddings.create.side_effect=RuntimeError('unavailable')
    with pytest.raises(RuntimeError):asyncio.run(cache.vectors(['new']))
    assert rows==before

def test_malformed_provider_batch_is_not_cached(cached):
    rows,calls,api=cached
    api.embeddings.create.side_effect=None
    api.embeddings.create.return_value=SimpleNamespace(data=[SimpleNamespace(index=2,embedding=[0.0]*1536)])
    with pytest.raises(ValueError):asyncio.run(cache.vectors(['new']))
    assert not rows
