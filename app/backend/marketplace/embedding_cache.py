"""Persistent content-addressed document embeddings; query embeddings are not cached here."""
import hashlib, os
from sqlalchemy import String, Text, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from .db import engine, Session
from .tools import client

class CacheBase(DeclarativeBase): pass
class CachedEmbedding(CacheBase):
    __tablename__='document_embedding_cache'
    key: Mapped[str]=mapped_column(String,primary_key=True)
    body: Mapped[str]=mapped_column(Text)
    embedding: Mapped[list[float]]=mapped_column(Vector(1536))

def initialize(): CacheBase.metadata.create_all(engine)
def namespace():
    # Bump EMBEDDING_MODEL_REVISION when changing the gateway's embedding mapping.
    return os.getenv('LITELLM_URL','http://localhost:4000/v1')+'|'+os.getenv('EMBEDDING_MODEL_REVISION','text-embedding-3-small:1536:v1')
def cache_key(body): return hashlib.sha256((namespace()+'\0'+body).encode()).hexdigest()

async def vectors(bodies):
    # Serialize cache fills across processes. A competing request retries rather than paying twice.
    with Session.begin() as db:
        if not db.scalar(text("SELECT pg_try_advisory_xact_lock(hashtext('document-embedding-cache'))")):
            raise RuntimeError('Document preparation is already running; retry shortly')
        keys=[cache_key(b) for b in bodies]
        found={row.key:row.embedding for row in db.scalars(select(CachedEmbedding).where(CachedEmbedding.key.in_(keys))).all()}
        missing={k:b for k,b in zip(keys,bodies) if k not in found}
        if missing:
            api=client()
            try: response=await api.embeddings.create(model='embedding',input=list(missing.values()))
            finally: await api.close()
            data=sorted(response.data,key=lambda item:item.index)
            if [i.index for i in data]!=list(range(len(missing))) or any(len(i.embedding)!=1536 for i in data):
                raise ValueError('Embedding response does not match document batch')
            for (key,body),item in zip(missing.items(),data):
                db.add(CachedEmbedding(key=key,body=body,embedding=item.embedding));found[key]=item.embedding
        return [found[k] for k in keys]
