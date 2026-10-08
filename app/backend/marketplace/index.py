import asyncio
from sqlalchemy import select
from .db import Session,Document
from .tools import client

async def index():
    with Session() as db:
        docs=db.scalars(select(Document).where(Document.embedding==None)).all()
        if not docs: return {'indexed':0}
        api=client()
        try: response=await api.embeddings.create(model='embedding',input=[x.body for x in docs])
        finally: await api.close()
        for item in response.data:
            docs[item.index].embedding=item.embedding
            docs[item.index].embedding_model='text-embedding-3-small'
        db.commit()
        return {'indexed':len(docs),'model':'text-embedding-3-small','dimensions':1536}
if __name__=='__main__': print(asyncio.run(index()))
