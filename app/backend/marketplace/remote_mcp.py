"""Authenticated HTTP MCP for the synthetic marketplace lab; no agent runtime."""
import asyncio
import hmac
import json
import os
import secrets
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount
from .tools import ReadContext
from .tool_contracts import build_tool_functions

@dataclass
class Investigation:
    context: object
    expires: float
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)

class Investigations:
    def __init__(self, factory=ReadContext, ttl=180, limit=8, clock=time.monotonic):
        self.factory=factory; self.ttl=ttl; self.limit=limit; self.clock=clock; self.runs={}
    def reap(self):
        for key, run in list(self.runs.items()):
            if run.expires <= self.clock() and not run.lock.locked():
                run.context.close(); del self.runs[key]
    def begin(self):
        self.reap()
        if len(self.runs)>=self.limit:
            return {'status':'error','code':'CAPACITY','message':'End an investigation or wait for its expiry.'}
        ctx=self.factory(); key=secrets.token_urlsafe(24)
        self.runs[key]=Investigation(ctx,self.clock()+self.ttl)
        return {'status':'ok','investigation_id':key,'snapshot':ctx.snapshot,
                'document_revision':ctx.doc_hash,'expires_in_seconds':self.ttl,
                'instruction':'Use this ID for all tools in this question. Start a new investigation for the next question.'}
    async def call(self, key, name, **arguments):
        self.reap(); run=self.runs.get(key)
        if not run: return {'status':'error','code':'INVESTIGATION_UNAVAILABLE','message':'Start a new investigation; never invent missing evidence.'}
        async with run.lock:
            if self.runs.get(key) is not run or run.expires <= self.clock():
                return {'status':'error','code':'INVESTIGATION_EXPIRED','message':'Start a new investigation and retrieve fresh evidence.'}
            functions={fn.__name__:fn for fn in build_tool_functions(run.context)}
            result = await functions[name](**arguments)
            if name == 'get_order_history' and 'current_records' in result:
                # The original history contract focuses on settlements. Supply the
                # order/payment fields explicitly instead of inviting inference.
                result['order_summary'] = await functions['query_business_data'](
                    sql='SELECT o.id AS order_id, o.status AS order_status, o.created_at, '
                        'p.status AS payment_status, p.amount AS payment_amount_paise, p.currency '
                        'FROM orders o LEFT JOIN payments p ON p.order_id = o.id '
                        'WHERE o.id = %(order_id)s',
                    parameters_json=json.dumps({'order_id': arguments['order_id']}),
                    purpose='Order and payment summary for the requested order history',
                )
            return result
    async def end(self,key):
        run=self.runs.get(key)
        if not run: return {'status':'error','code':'INVESTIGATION_UNAVAILABLE'}
        async with run.lock:
            if self.runs.pop(key,None) is run: run.context.close()
        return {'status':'ok','closed':True}
    def close(self):
        for run in self.runs.values(): run.context.close()
        self.runs.clear()

class ApiKeyBoundary:
    def __init__(self, app, token): self.app=app; self.token=token
    async def __call__(self, scope, receive, send):
        if scope['type']=='http':
            headers=dict(scope.get('headers',[]))
            supplied=headers.get(b'x-api-key',b'').decode('latin1')
            authorization=headers.get(b'authorization',b'').decode('latin1')
            if authorization.startswith('Bearer '): supplied=authorization[7:]
            if not hmac.compare_digest(supplied.encode('utf-8'),self.token.encode('utf-8')):
                await JSONResponse({'error':'Unauthorized'},status_code=401)(scope,receive,send); return
        await self.app(scope,receive,send)

def create_app(token=None, *, registry=None, allowed_hosts=None):
    token=token or os.environ.get('REMOTE_MCP_API_KEY','')
    if len(token)<32: raise ValueError('REMOTE_MCP_API_KEY must contain at least 32 characters')
    if registry is None:
        if os.getenv('MCP_REGISTRY_DATABASE_URL'):
            from .cloud_registry import DurableInvestigations
            registry=DurableInvestigations()
        else:
            registry=Investigations()
    server=MCPServer('Marketplace support read tools',instructions='Start one investigation per question. Use its investigation_id for every business tool. Tools are read-only; memory and business mutations are unavailable.')

    @server.tool(structured_output=False)
    async def begin_investigation() -> dict:
        """Begin one question: freeze business snapshot and return ID, revision, clock and document revision."""
        return registry.begin()
    @server.tool(structured_output=False)
    async def end_investigation(investigation_id: str) -> dict:
        """Close the question's snapshot after answering; remaining evidence handles then expire."""
        return await registry.end(investigation_id)
    @server.tool(structured_output=False)
    async def get_catalog(investigation_id: str) -> dict:
        """Get entity/field definitions, joins, types and metrics before constructing SQL."""
        return await registry.call(investigation_id,'get_catalog')
    @server.tool(structured_output=False)
    async def query_business_data(investigation_id: str, sql: str, parameters_json: str='{}', purpose: str='') -> dict:
        """Run one bounded read-only PostgreSQL SELECT. Bind %(name)s values in parameters_json. Money is paise."""
        return await registry.call(investigation_id,'query_business_data',sql=sql,parameters_json=parameters_json,purpose=purpose)
    @server.tool(structured_output=False)
    async def search_documents(investigation_id: str, query: str, effective_at: str|None=None, scope: str='all', top_k: int=4) -> dict:
        """Find applicable policy/runbook evidence. Default date is this investigation's demo clock."""
        return await registry.call(investigation_id,'search_documents',query=query,effective_at=effective_at,scope=scope,top_k=top_k)
    @server.tool(structured_output=False)
    async def fetch_evidence(investigation_id: str, handle: str) -> dict:
        """Fetch an exact evidence handle from this investigation only."""
        return await registry.call(investigation_id,'fetch_evidence',handle=handle)
    @server.tool(structured_output=False)
    async def get_order_history(investigation_id: str, order_id: str) -> dict:
        """Return order/payment summary, settlement records and chronological event evidence including failed attempts."""
        return await registry.call(investigation_id,'get_order_history',order_id=order_id)

    hosts=allowed_hosts or ['localhost:*','127.0.0.1:*','testserver',*[x for x in os.getenv('REMOTE_MCP_ALLOWED_HOSTS','').split(',') if x]]
    inner=server.streamable_http_app(json_response=True,stateless_http=True,max_request_body_size=65536,
        transport_security=TransportSecuritySettings(allowed_hosts=hosts,allowed_origins=[]))
    @asynccontextmanager
    async def lifespan(app):
        async def sweep():
            while True:
                await asyncio.sleep(15); registry.reap()
        async with inner.router.lifespan_context(inner):
            task=asyncio.create_task(sweep())
            try: yield
            finally:
                task.cancel()
                try: await task
                except asyncio.CancelledError: pass
                registry.close()
    return ApiKeyBoundary(Starlette(routes=[Mount('/',app=inner)],lifespan=lifespan),token)

def main():
    import uvicorn
    uvicorn.run(create_app(),host='0.0.0.0',port=int(os.getenv('REMOTE_MCP_PORT','8001')),access_log=False)
if __name__=='__main__': main()
