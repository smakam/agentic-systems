"""Separate, authenticated simulated delivery service over A2A 1.0 JSON-RPC.

Run: uvicorn marketplace.delivery_service:app --port 8004
Only SendMessage and owner-scoped GetTask are exposed. No streaming, push,
cancellation, registry or model-controlled shipping writes are advertised.
"""
import os
import secrets
from google.protobuf.json_format import MessageToDict, ParseDict
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from a2a.auth.user import User
from a2a.server.agent_execution import AgentExecutor
from a2a.server.context import ServerCallContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes.common import ServerCallContextBuilder
from a2a.server.routes.jsonrpc_routes import create_jsonrpc_routes
from a2a.server.routes.agent_card_routes import create_agent_card_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import AgentCard, Message, Part, Role, Task, TaskStatus, TaskState
from .delivery_store import DeliveryStore, DeliveryRecordError
from .delivery_investigator import investigate


def agent_card():
    return ParseDict({
        'name':'Simulated marketplace delivery agent',
        'description':'Simulated shipment booking and manual delivery updates; a small model investigation checks recorded status and conditionally reads delivery-problem evidence. No real carriers.',
        'version':'1.0.0',
        'supportedInterfaces':[{'url':os.getenv('DELIVERY_A2A_URL','http://localhost:8004').rstrip('/')+'/',
                                'protocolBinding':'JSONRPC', 'protocolVersion':'1.0'}],
        'capabilities':{'streaming':False,'pushNotifications':False,'extendedAgentCard':False},
        'defaultInputModes':['application/json','text/plain'], 'defaultOutputModes':['application/json','text/plain'],
        'securitySchemes':{'serviceBearer':{'httpAuthSecurityScheme':{'scheme':'bearer',
            'description':'Separate service credentials: investigation is read-only; booking and manual delivery require the write credential.'}}},
        'securityRequirements':[{'schemes':{'serviceBearer':[]}}],
        'skills':[
            {'id':'investigate-shipment','name':'Investigate delivery','description':'Check current shipment status and, when needed, recorded problem reason and tracking evidence.',
             'tags':['delivery','read-only','simulated'],'examples':['Is the shipment on schedule?','Why is this shipment stuck?']},
            {'id':'simulate-shipping','name':'Simulate shipment operations','description':'Authorized marketplace backend can book a simulated shipment, change its normal/exception fixture, or manually mark it delivered. These writes are deterministic, not model decisions.',
             'tags':['simulation','shipping'],'examples':['Book a normal simulated shipment','Simulate delivery']}]
    }, AgentCard())


class ServiceUser(User):
    def __init__(self, scope): self.scope = scope
    @property
    def is_authenticated(self): return True
    @property
    def user_name(self): return 'marketplace-delivery-'+self.scope


class DeliveryContext(ServerCallContextBuilder):
    def build(self, request):
        scope = request.state.delivery_scope
        return ServerCallContext(user=ServiceUser(scope), state={'delivery_scope':scope,
                                      'headers':{'A2A-Version':request.headers.get('a2a-version','')}})


class DeliveryAuth(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path in ('/health','/.well-known/agent-card.json') and request.method == 'GET':
            return await call_next(request)
        read, write = os.getenv('DELIVERY_READ_TOKEN',''), os.getenv('DELIVERY_WRITE_TOKEN','')
        if not read or not write or secrets.compare_digest(read, write):
            return JSONResponse({'detail':'Configure distinct delivery read and write credentials'}, status_code=503)
        authorization = request.headers.get('authorization','')
        supplied = authorization[7:] if authorization.startswith('Bearer ') else ''
        scope = 'write' if supplied and secrets.compare_digest(supplied, write) else 'read' if supplied and secrets.compare_digest(supplied, read) else None
        if scope is None:
            return JSONResponse({'detail':'Delivery service credential required'},status_code=401,headers={'WWW-Authenticate':'Bearer'})
        request.state.delivery_scope = scope
        if request.method == 'POST' and request.url.path == '/':
            # The SDK owns protocol dispatch; this boundary rejects unsupported
            # features and authorizes operations before the executor sees them.
            body_bytes = await request.body()
            if len(body_bytes) > 20000:
                return JSONResponse({'detail':'Delivery request too large'}, status_code=413)
            try:
                body = await request.json()
                if not isinstance(body,dict): raise ValueError()
                method = body.get('method')
                if method not in ('SendMessage','GetTask'):
                    return JSONResponse({'jsonrpc':'2.0','id':body.get('id'),'error':{'code':-32601,'message':'Method not supported by this synchronous service'}})
                if method == 'SendMessage':
                    message = body.get('params',{}).get('message',{})
                    if message.get('taskId') or message.get('task_id'):
                        return JSONResponse({'jsonrpc':'2.0','id':body.get('id'),'error':{'code':-32602,'message':'Each delivery request creates a new task; completed tasks cannot reopen'}})
                    parts = message.get('parts',[])
                    if len(parts) != 1 or not isinstance(parts[0].get('data'),dict): raise ValueError()
                    operation = parts[0]['data'].get('operation')
                    if operation in ('book','deliver','set_fixture') and scope != 'write':
                        return JSONResponse({'detail':'Delivery write credential required'},status_code=403)
                    if operation not in ('book','deliver','set_fixture','investigate'):
                        raise ValueError()
                    config = body.get('params',{}).get('configuration',{})
                    if not isinstance(config,dict): raise ValueError()
                    if config.get('returnImmediately') or config.get('return_immediately'):
                        return JSONResponse({'detail':'Only blocking delivery requests are supported'},status_code=400)
            except (ValueError,TypeError,AttributeError,KeyError):
                return JSONResponse({'detail':'Use one delivery operation data part'},status_code=400)
        from .protocol_tracing import protocol_span, incoming_trace
        with protocol_span('A2A delivery inbound',{'transport':'a2a','operation':method if request.method=='POST' and request.url.path=='/' else request.method,'protocol_version':'1.0'},
                trace_context=incoming_trace(request.headers.get('traceparent'))) as span:
            response=await call_next(request)
            if span: span.update(output={'http_status':response.status_code},level='ERROR' if response.status_code>=400 else 'DEFAULT')
            return response


class DeliveryExecutor(AgentExecutor):
    def __init__(self, store): self.store = store

    async def execute(self, context, event_queue):
        from .protocol_tracing import protocol_span
        with protocol_span('Delivery A2A task',{'task_id':context.task_id,'context_id':context.context_id}) as span:
            return await self._execute(context,event_queue,span)

    async def _execute(self, context, event_queue, span):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await event_queue.enqueue_event(Task(id=context.task_id,context_id=context.context_id,
                                  status=TaskStatus(state=TaskState.TASK_STATE_WORKING)))
        try:
            data = MessageToDict(context.message)['parts'][0]['data']
            operation = data['operation']
            if operation in ('book','deliver','set_fixture') and context.call_context.state.get('delivery_scope') != 'write':
                raise DeliveryRecordError('Delivery write credential required')
            if operation == 'book':
                result = self.store.book(data.get('shipment_id'),data.get('fixture','normal'),data.get('clock'))
            elif operation == 'deliver':
                result = self.store.deliver(data.get('reference'),data.get('clock'))
            elif operation == 'set_fixture':
                result = self.store.set_fixture(data.get('reference'),data.get('fixture'),data.get('clock'),data.get('operation_key'))
            elif operation == 'investigate':
                result = await investigate(self.store,data.get('reference'),data.get('question'),data.get('as_of'))
            else:
                raise DeliveryRecordError('Unknown delivery operation')
            await updater.add_artifact([ParseDict({'data':result},Part())],name='Delivery result')
            await updater.complete()
            if span: span.update(output={'state':'completed','operation':operation})
        except Exception as exc:
            if span: span.update(output={'state':'failed'},level='ERROR',status_message='Delivery task failed')
            # Failure is a terminal failed Task, never a completed canned answer.
            message = str(exc) if isinstance(exc,DeliveryRecordError) else 'Delivery investigation failed; no verified conclusion is available'
            await updater.failed(Message(role=Role.ROLE_AGENT, parts=[Part(text=message)]))

    async def cancel(self, context, event_queue):
        raise NotImplementedError('Cancellation is not supported')


def create_app(store=None):
    service = FastAPI(title='Simulated delivery A2A service')
    service.add_middleware(DeliveryAuth)
    @service.get('/health')
    def health(): return {'status':'ok','simulated':True}
    card = agent_card()
    handler = DefaultRequestHandler(DeliveryExecutor(store or DeliveryStore()),InMemoryTaskStore(),agent_card=card)
    service.router.routes.extend(create_agent_card_routes(card))
    service.router.routes.extend(create_jsonrpc_routes(handler,'/',DeliveryContext()))
    return service


app = create_app()
