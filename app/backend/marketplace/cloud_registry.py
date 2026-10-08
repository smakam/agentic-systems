"""HTTP MCP state survives replicas; reject revision drift instead of mixing evidence.

Local MCP retains a held repeatable-read snapshot. Cloud calls open fresh read
transactions and require the same revision, clock and document hashes. Any drift
requires a new investigation; evidence and budgets live in PostgreSQL.
"""
import hashlib
import json
import os
import secrets
import time
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
from .tools import ReadContext
from .tool_contracts import build_tool_functions

DDL='''CREATE TABLE IF NOT EXISTS public.mcp_investigations (
 token_hash text PRIMARY KEY, expires double precision NOT NULL,
 snapshot jsonb NOT NULL, document_revision text NOT NULL,
 evidence jsonb NOT NULL DEFAULT '{}', calls integer NOT NULL DEFAULT 0
)'''


def token_hash(key):
    return hashlib.sha256(key.encode()).hexdigest()


def normalized(value):
    return json.loads(json.dumps(value,default=str))


class DurableInvestigations:
    def __init__(self, url=None, factory=ReadContext, ttl=180, limit=8, clock=time.time):
        self.url=url or os.environ['MCP_REGISTRY_DATABASE_URL']
        self.factory=factory; self.ttl=ttl; self.limit=limit; self.clock=clock

    def connection(self):
        return psycopg.connect(self.url,row_factory=dict_row)

    async def async_connection(self):
        return await psycopg.AsyncConnection.connect(self.url,row_factory=dict_row)

    def reap(self):
        # Cleanup also happens during begin; no background CPU is required.
        pass

    def begin(self):
        ctx=self.factory()
        try:
            with self.connection() as db:
                db.execute("SELECT pg_advisory_xact_lock(713024)")
                db.execute('DELETE FROM public.mcp_investigations WHERE expires <= %s',(self.clock(),))
                if db.execute('SELECT COUNT(*) AS n FROM public.mcp_investigations').fetchone()['n'] >= self.limit:
                    return {'status':'error','code':'CAPACITY','message':'End an investigation or wait for expiry.'}
                key=secrets.token_urlsafe(24)
                db.execute('INSERT INTO public.mcp_investigations(token_hash,expires,snapshot,document_revision) VALUES (%s,%s,%s,%s)',
                           (token_hash(key),self.clock()+self.ttl,Jsonb(normalized(ctx.snapshot)),ctx.doc_hash))
            return {'status':'ok','investigation_id':key,'snapshot':ctx.snapshot,'document_revision':ctx.doc_hash,
                    'expires_in_seconds':self.ttl,'consistency':'revision-guarded',
                    'instruction':'Use this ID for this question; start again if evidence revision changes.'}
        finally:
            ctx.close()

    async def call(self,key,name,**arguments):
        async with await self.async_connection() as db:
            cursor=await db.execute('SELECT * FROM public.mcp_investigations WHERE token_hash=%s FOR UPDATE',(token_hash(key),))
            row=await cursor.fetchone()
            if not row or row['expires'] <= self.clock():
                return {'status':'error','code':'INVESTIGATION_UNAVAILABLE','message':'Start a new investigation.'}
            ctx=self.factory()
            try:
                if normalized(ctx.snapshot)!=row['snapshot'] or ctx.doc_hash!=row['document_revision']:
                    await db.execute('DELETE FROM public.mcp_investigations WHERE token_hash=%s',(token_hash(key),))
                    return {'status':'error','code':'REVISION_CHANGED','message':'Business or policy evidence changed. Start a new investigation and retrieve all evidence again.'}
                ctx.calls=row['calls']; ctx.evidence=row['evidence']
                functions={fn.__name__:fn for fn in build_tool_functions(ctx)}
                result=await functions[name](**arguments)
                if name=='get_order_history' and 'current_records' in result:
                    result['order_summary']=await functions['query_business_data'](
                        sql='SELECT o.id AS order_id,o.status AS order_status,o.created_at,p.status AS payment_status,p.amount AS payment_amount_paise,p.currency FROM orders o LEFT JOIN payments p ON p.order_id=o.id WHERE o.id=%(order_id)s',
                        parameters_json=json.dumps({'order_id':arguments['order_id']}),
                        purpose='Order and payment summary for the requested order history')
                await db.execute('UPDATE public.mcp_investigations SET calls=%s,evidence=%s WHERE token_hash=%s',
                           (ctx.calls,Jsonb(normalized(ctx.evidence)),token_hash(key)))
                return result
            finally:
                ctx.close()

    async def end(self,key):
        async with await self.async_connection() as db:
            cursor=await db.execute('DELETE FROM public.mcp_investigations WHERE token_hash=%s RETURNING token_hash',(token_hash(key),))
            removed=await cursor.fetchone()
        return {'status':'ok','closed':True} if removed else {'status':'error','code':'INVESTIGATION_UNAVAILABLE'}

    def close(self):
        # A replica shutdown must not delete other replicas' active investigations.
        pass
