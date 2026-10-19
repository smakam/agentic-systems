import asyncio, os
from sqlalchemy import select, text
from .db import Session, Document
from .embedding_cache import initialize, vectors, namespace, cache_key, CachedEmbedding

async def index():
    initialize()
    with Session() as db:
        if not db.scalar(text("SELECT pg_try_advisory_xact_lock(hashtext('marketplace-document-index'))")):
            raise RuntimeError('Document preparation is already running')
        docs=db.scalars(select(Document).where((Document.embedding==None) | (Document.embedding_model==None) | (Document.embedding_model!=namespace()))).all()
        if not docs:return {'indexed':0}
        # Adopt compatible pre-cache embeddings; the first upgrade must not charge for them again.
        if os.getenv('EMBEDDING_MODEL_REVISION','text-embedding-3-small:1536:v1')=='text-embedding-3-small:1536:v1':
            with Session.begin() as cache_db:
                from sqlalchemy.dialects.postgresql import insert
                for doc in docs:
                    if doc.embedding is not None and doc.embedding_model=='text-embedding-3-small':
                        cache_db.execute(insert(CachedEmbedding).values(key=cache_key(doc.body),body=doc.body,embedding=doc.embedding).on_conflict_do_nothing())
        embeddings=await vectors([x.body for x in docs])
        for doc,vector in zip(docs,embeddings):
            doc.embedding=vector;doc.embedding_model=namespace()
        db.commit()
        return {'indexed':len(docs),'dimensions':1536}
if __name__=='__main__':print(asyncio.run(index()))
