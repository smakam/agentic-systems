"""Authenticated A2A 1.0 adapter for the existing support workflow.

The browser is an A2A client. This module adds protocol/state mapping, not a
second reasoning agent. Ordinary follow-ups create new tasks in one owned
marketplace conversation. The existing support workflow remains authoritative.
"""
import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from google.protobuf.json_format import MessageToDict, ParseDict
from pydantic import ValidationError
from sqlalchemy import ForeignKey, JSON, String, select, text
from sqlalchemy.orm import Mapped, mapped_column
from starlette.responses import JSONResponse

from a2a.auth.user import User as ProtocolUser
from a2a.server.agent_execution import AgentExecutor
from a2a.server.context import ServerCallContext
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes.common import ServerCallContextBuilder
from a2a.server.routes.jsonrpc_dispatcher import JsonRpcDispatcher
from a2a.server.tasks import TaskStore
from a2a.types import (AgentCapabilities, AgentCard, AgentInterface, AgentSkill,
    APIKeySecurityScheme, SecurityScheme, SecurityRequirement, StringList,
    Task, TaskStatus, TaskState, Artifact, Part, ListTasksResponse)
from a2a.utils.errors import UnsupportedOperationError

from .db import Base, Conversation, Run, Session, User, engine

PREFIX = '/api/a2a/support'
MODES = ('standard', 'a2a_support', 'a2a_delivery')


class SupportConversation(Base):
    __tablename__ = 'support_conversation_modes'
    conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id'), primary_key=True)
    mode: Mapped[str] = mapped_column(String)
    context_id: Mapped[str] = mapped_column(String, unique=True)


class SupportTask(Base):
    __tablename__ = 'support_a2a_tasks'
    id: Mapped[str] = mapped_column(String, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey('conversations.id'), index=True)
    payload: Mapped[dict] = mapped_column(JSON)


class SupportMessage(Base):
    """A durable receipt prevents a lost-response retry from running twice."""
    __tablename__ = 'support_a2a_messages'
    context_id: Mapped[str] = mapped_column(ForeignKey('support_conversation_modes.context_id'), primary_key=True)
    message_id: Mapped[str] = mapped_column(String, primary_key=True)
    request_hash: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON)


def conversation_fields(db, conversation_id):
    binding = db.get(SupportConversation, conversation_id)
    return {'mode': binding.mode if binding else 'standard',
            'a2a_context_id': binding.context_id if binding else None}


def add_conversation_binding(db, conversation_id, mode):
    if mode != 'standard':
        db.add(SupportConversation(conversation_id=conversation_id, mode=mode,
                                   context_id=str(uuid4())))
        db.flush()


def _owned_context(db, user_id, context_id):
    binding = db.scalar(select(SupportConversation).join(Conversation).where(
        SupportConversation.context_id == context_id, Conversation.owner_id == user_id))
    return binding


class _BrowserUser(ProtocolUser):
    def __init__(self, user_id): self.user_id = user_id
    @property
    def is_authenticated(self): return True
    @property
    def user_name(self): return self.user_id


class _BrowserContext(ServerCallContextBuilder):
    def build(self, request):
        user_id = request.state.support_a2a_user_id
        return ServerCallContext(user=_BrowserUser(user_id), state={'user_id': user_id,'headers':{'A2A-Version':request.headers.get('a2a-version','')}})


class DatabaseTaskStore(TaskStore):
    """Task lookup always joins the owning marketplace conversation."""
    async def save(self, task, context):
        with Session.begin() as db:
            binding = _owned_context(db, context.state['user_id'], task.context_id)
            if not binding: raise PermissionError('Conversation not found')
            row = db.get(SupportTask, task.id)
            if row and row.conversation_id != binding.conversation_id:
                raise PermissionError('Task not found')
            payload = MessageToDict(task)
            if row: row.payload = payload
            else: db.add(SupportTask(id=task.id, conversation_id=binding.conversation_id, payload=payload))

    async def get(self, task_id, context):
        with Session() as db:
            row = db.scalar(select(SupportTask).join(Conversation).where(
                SupportTask.id == task_id, Conversation.owner_id == context.state['user_id']))
            return ParseDict(row.payload, Task()) if row else None

    async def list(self, params, context):
        # This adapter deliberately exposes only SendMessage and GetTask.
        raise UnsupportedOperationError(message='Task listing is not supported')

    async def delete(self, task_id, context):
        raise UnsupportedOperationError(message='Task deletion is not supported')


def agent_card(base_url):
    return AgentCard(
        name='Marketplace Support',
        description='Read-only marketplace investigations using the existing support agent, tools and conversation history. Delivery-enabled conversations can delegate shipment investigations to the simulated delivery service.',
        version='1.0.0',
        supported_interfaces=[AgentInterface(url=base_url.rstrip('/') + PREFIX,
            protocol_binding='JSONRPC', protocol_version='1.0')],
        default_input_modes=['text/plain'], default_output_modes=['text/plain'],
        capabilities=AgentCapabilities(streaming=False, push_notifications=False),
        security_schemes={
            'marketplaceSession': SecurityScheme(api_key_security_scheme=APIKeySecurityScheme(
                location='cookie', name='market_session', description='Existing signed-in support/operator marketplace session.')),
            'csrf': SecurityScheme(api_key_security_scheme=APIKeySecurityScheme(
                location='header', name='X-CSRF-Token', description='Existing session CSRF token for all POST requests.')),
        },
        security_requirements=[SecurityRequirement(schemes={
            'marketplaceSession': StringList(), 'csrf': StringList()})],
        skills=[AgentSkill(id='marketplace-investigation', name='Investigate marketplace records',
            description='Answer order, shipment, return, refund and payout questions using read-only business records and policy evidence.',
            tags=['marketplace','support','read-only'], examples=['What is the status of order-2?']),
            AgentSkill(id='delivery-investigation', name='Investigate linked delivery shipments',
            description='Delegate linked shipment questions to the simulated delivery service and return its recorded evidence. Available only in Multi-agent A2A mode for detailed tracking or delivery-problem questions; basic order status uses marketplace records. Does not dispatch or deliver shipments.',
            tags=['delivery','simulation','read-only'])])


def _rpc_error(payload, message, code=-32602):
    return JSONResponse({'jsonrpc':'2.0','id':payload.get('id'), 'error':{'code':code,'message':message}})


class SupportExecutor(AgentExecutor):
    def __init__(self, run_question, question_model):
        self.run_question = run_question
        self.question_model = question_model

    async def execute(self, context, event_queue):
        user_id = context.call_context.state['user_id']
        # The HTTP wrapper has validated context ownership and mode before the SDK
        # creates a task. Repeat it here as defense against non-HTTP callers.
        with Session() as db:
            user = db.get(User, user_id)
            binding = _owned_context(db, user_id, context.context_id)
            if not binding or not user or user.role not in ('support','operator'):
                raise PermissionError('Conversation not found')
            cid = binding.conversation_id
            options = dict(context.metadata.get('question_options', {}))
            options['question'] = context.get_user_input()
            body = self.question_model.model_validate(options)
            try:
                from .protocol_tracing import protocol_span
                with protocol_span('A2A marketplace request',{'transport':'a2a','endpoint':PREFIX,'operation':'SendMessage','protocol_version':'1.0',
                        'task_id':context.task_id,'context_id':context.context_id,'mode':binding.mode,'conversation_id':cid}) as span:
                    result = await self.run_question(cid, body, user, db, transport='a2a')
                    if span: span.update(output={'run_id':result.get('id'),'status':result.get('status')},level='ERROR' if result.get('status')=='failed' else 'DEFAULT')
                state = TaskState.TASK_STATE_COMPLETED if result['status'] == 'completed' else TaskState.TASK_STATE_FAILED
                text = result['answer']
                run_id = result['id']
                # Keep provenance with the normal run so UI history survives reload.
                saved = db.get(Run, run_id)
                a2a = {'task_id':context.task_id,'context_id':context.context_id,'protocol_version':'1.0','mode':binding.mode}
                if saved:
                    db.refresh(saved)
                    saved.metrics = {**(saved.metrics or {}), 'a2a':a2a}
                    db.commit()
            except HTTPException as exc:
                state = TaskState.TASK_STATE_FAILED
                text = str(exc.detail)
                run_id = None
            except Exception:
                # Do not leak provider credentials, SQL details or exception strings.
                state = TaskState.TASK_STATE_FAILED
                text = 'The support investigation failed. No complete result is available; retry after checking service readiness.'
                run_id = None
            metadata = {'conversation_id':cid}
            if run_id: metadata['run_id'] = run_id
            task = Task(id=context.task_id, context_id=context.context_id,
                status=TaskStatus(state=state), metadata=metadata,
                artifacts=[Artifact(artifact_id=str(uuid4()), name='Support answer', parts=[Part(text=text)])])
            task.status.timestamp.FromDatetime(datetime.now(timezone.utc))
            await event_queue.enqueue_event(task)

    async def cancel(self, context, event_queue):
        raise UnsupportedOperationError(message='Cancellation is not supported')


def create_router(identity, db_session, role, run_question, question_model):
    router = APIRouter()
    handler = DefaultRequestHandler(SupportExecutor(run_question, question_model),
        DatabaseTaskStore(), agent_card('http://localhost'))
    dispatcher = JsonRpcDispatcher(handler, context_builder=_BrowserContext())

    @router.get(PREFIX + '/.well-known/agent-card.json')
    def card(request: Request):
        # Public service metadata describes how to authenticate work requests;
        # fetching it never executes an investigation or grants data access.
        # Include false capabilities, so the UI can show the actual supported set.
        return MessageToDict(agent_card(str(request.base_url)), always_print_fields_with_no_presence=True)

    @router.post(PREFIX)
    async def rpc(request: Request, user=Depends(identity), db=Depends(db_session)):
        role(user, 'support', 'operator')
        request.state.support_a2a_user_id = user.id
        try: payload = await request.json()
        except Exception: return await dispatcher.handle_requests(request)
        if not isinstance(payload, dict): return await dispatcher.handle_requests(request)
        if request.headers.get('a2a-version')!='1.0':
            return _rpc_error(payload,'A2A-Version: 1.0 is required by this endpoint',-32009)
        method = payload.get('method')
        if method not in ('SendMessage','GetTask'):
            return _rpc_error(payload, 'Only SendMessage and GetTask are supported', -32601)
        if method == 'SendMessage':
            params = payload.get('params')
            if not isinstance(params,dict): return _rpc_error(payload,'Message parameters are required')
            message = params.get('message')
            if not isinstance(message,dict): return _rpc_error(payload,'A user text message is required')
            if any(k in message for k in ('context_id','message_id','task_id')):
                return _rpc_error(payload,'Use the advertised JSON field names: contextId, messageId and taskId')
            message_id=message.get('messageId')
            if not isinstance(message_id,str) or not message_id.strip() or len(message_id)>200:
                return _rpc_error(payload,'A nonempty messageId of at most 200 characters is required')
            if message.get('taskId') or message.get('task_id'):
                return _rpc_error(payload,'Follow-ups use a new task in the same context; do not supply taskId')
            binding = _owned_context(db, user.id, message.get('contextId') or message.get('context_id'))
            if not binding: return _rpc_error(payload,'Conversation not found')
            metadata = params.get('metadata', {})
            if not isinstance(metadata,dict): return _rpc_error(payload,'Invalid metadata')
            if metadata.get('conversation_id',binding.conversation_id) != binding.conversation_id:
                return _rpc_error(payload,'Conversation not found')
            if message.get('role') not in ('ROLE_USER',1): return _rpc_error(payload,'A user text message is required')
            parts = message.get('parts',[])
            if not isinstance(parts,list) or not parts or any(not isinstance(p,dict) or set(p)-{'text','mediaType'} or not isinstance(p.get('text'),str) for p in parts):
                return _rpc_error(payload,'Only text message parts are supported')
            config = params.get('configuration',{})
            if not isinstance(config,dict) or any(config.get(k) for k in ('returnImmediately','return_immediately','taskPushNotificationConfig','task_push_notification_config')):
                return _rpc_error(payload,'Only blocking messages without push notifications are supported')
            options = metadata.get('question_options',{})
            if not isinstance(options,dict): return _rpc_error(payload,'Invalid question options')
            try: question_model.model_validate({**options,'question':'\n'.join(p['text'] for p in parts)})
            except ValidationError: return _rpc_error(payload,'Invalid question or support settings')
        if method=='GetTask': return await dispatcher.handle_requests(request)
        # Keep the receipt lock until the blocking SDK response is persisted.
        # The conversation's own existing lock still protects distinct questions.
        context_id=binding.context_id
        digest=hashlib.sha256(json.dumps(params,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        with engine.connect() as lock:
            lock_key='support-a2a-message:'+context_id+':'+message_id
            if not lock.execute(text('SELECT pg_try_advisory_lock(hashtext(:key))'),{'key':lock_key}).scalar():
                return _rpc_error(payload,'This message is still processing; retry the same messageId later',-32000)
            try:
                receipt=db.get(SupportMessage,(context_id,message_id))
                if receipt:
                    if receipt.request_hash!=digest:
                        return _rpc_error(payload,'This messageId was already used with different content')
                    return JSONResponse({'jsonrpc':'2.0','id':payload.get('id'),'result':{'task':receipt.payload}})
                result=await dispatcher.handle_requests(request)
                if isinstance(result,JSONResponse):
                    data=json.loads(result.body)
                    task=data.get('result',{}).get('task')
                    if task and task.get('status',{}).get('state') in ('TASK_STATE_COMPLETED','TASK_STATE_FAILED'):
                        db.add(SupportMessage(context_id=context_id,message_id=message_id,request_hash=digest,payload=task))
                        db.commit()
                return result
            finally:
                lock.execute(text('SELECT pg_advisory_unlock(hashtext(:key))'),{'key':lock_key})

    return router
