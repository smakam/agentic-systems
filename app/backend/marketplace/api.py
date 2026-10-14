import asyncio, hashlib, os, secrets
from typing import Literal
from sqlalchemy.dialects.postgresql import insert
from contextlib import asynccontextmanager
from datetime import datetime,timedelta,timezone
from fastapi import FastAPI,Depends,HTTPException,Request,Response,Body
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel,Field
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from sqlalchemy import select,text,func
from .db import *
from .seed import seed
from .business import execute,BusinessError,uid

@asynccontextmanager
async def lifespan(app):
    # Cloud replicas must not reseed or invalidate work owned by another instance.
    # The deployment initialization job performs schema creation and seeding.
    if os.getenv('INITIALIZE_ON_STARTUP','true') == 'true':
        init_schema()
        with Session.begin() as db:
            seed(db)
            for interrupted in db.scalars(select(Run).where(Run.status=='running')).all():
                interrupted.status='failed'
                interrupted.answer='The backend restarted during this investigation. Please retry; no business state was changed by the agent.'

    yield
app=FastAPI(title='Marketplace Lab',lifespan=lifespan)

def db_session():
    with Session() as db: yield db

def identity(request:Request,db=Depends(db_session)):
    cookie=request.cookies.get('market_session','')
    login=db.get(Login,hashlib.sha256(cookie.encode()).hexdigest())
    if not login or login.expires<datetime.now(timezone.utc): raise HTTPException(401,'Sign in required')
    if request.method not in ('GET','HEAD') and not secrets.compare_digest(request.headers.get('x-csrf-token',''),login.csrf): raise HTTPException(403,'Invalid CSRF token')
    return db.get(User,login.user_id)
def role(user,*roles):
    if user.role not in roles: raise HTTPException(403,'Not authorized for this workspace')
def user_json(user): return {'id':user.id,'username':user.username,'role':user.role,'seller_id':user.seller_id}
class Credentials(BaseModel):
    username:str=Field(max_length=100)
    password:str=Field(max_length=200)
@app.post('/api/login')
def login(data:Credentials,request:Request,response:Response,db=Depends(db_session)):
    # Same-origin JSON + Origin validation prevent login CSRF in the local app.
    origin=request.headers.get('origin')
    if origin and origin not in os.getenv('ALLOWED_ORIGINS','http://localhost:5178,http://127.0.0.1:5178').split(','): raise HTTPException(403,'Origin rejected')
    user=db.scalar(select(User).where(User.username==data.username))
    try:
        if not user: raise VerificationError('Invalid credentials')
        PasswordHasher().verify(user.password_hash,data.password)
    except VerificationError: raise HTTPException(401,'Invalid username or password')
    token=secrets.token_urlsafe(32); csrf=secrets.token_urlsafe(24)
    db.add(Login(token_hash=hashlib.sha256(token.encode()).hexdigest(),user_id=user.id,csrf=csrf,expires=datetime.now(timezone.utc)+timedelta(hours=12))); db.commit()
    response.set_cookie('market_session',token,httponly=True,samesite='strict',max_age=43200,secure=os.getenv('SECURE_COOKIES')=='true')
    return {'user':user_json(user),'csrf':csrf}
@app.get('/api/me')
def me(request:Request,user=Depends(identity),db=Depends(db_session)):
    login=db.get(Login,hashlib.sha256(request.cookies['market_session'].encode()).hexdigest())
    return {'user':user_json(user),'csrf':login.csrf}
@app.post('/api/logout')
def logout(request:Request,response:Response,user=Depends(identity),db=Depends(db_session)):
    db.delete(db.get(Login,hashlib.sha256(request.cookies['market_session'].encode()).hexdigest())); db.commit(); response.delete_cookie('market_session'); return {'ok':True}
@app.get('/api/health')
def health(db=Depends(db_session)):
    db.execute(text('SELECT 1')); return {'status':'ok','service':'marketplace'}
@app.get('/api/market')
def market(user=Depends(identity),db=Depends(db_session)):
    def rows(model,stmt=None): return [jsonable_encoder(x) for x in db.scalars((stmt if stmt is not None else select(model)).order_by(model.id)).all()]
    listings=select(Listing)
    sellers=select(Seller)
    products=select(Product)
    if user.role=='seller':
        listings=listings.where(Listing.seller_id==user.seller_id)
        sellers=sellers.where(Seller.id==user.seller_id)
        products=products.where(Product.id.in_(select(Listing.product_id).where(Listing.seller_id==user.seller_id)))
    orders=select(Order)
    if user.role=='buyer': orders=orders.where(Order.customer_id==user.id)
    if user.role=='seller': orders=orders.where(Order.id.in_(select(Item.order_id).where(Item.seller_id==user.seller_id)))
    order_data=rows(Order,orders); ids=[x['id'] for x in order_data]
    items=select(Item).where(Item.order_id.in_(ids))
    if user.role=='seller': items=items.where(Item.seller_id==user.seller_id)
    item_data=rows(Item,items); item_ids=[x['id'] for x in item_data]
    allocations=rows(Allocation,select(Allocation).where(Allocation.item_id.in_(item_ids)))
    alloc_ids=[x['id'] for x in allocations]
    returns=rows(Return,select(Return).where(Return.item_id.in_(item_ids)))
    # Buyers do not see seller settlement amounts; sellers do not see sibling payments.
    internal=user.role in ('operator','support','seller')
    balances=db.execute(text('SELECT * FROM analytics.seller_balances'+(' WHERE seller_id=:seller' if user.role=='seller' else '')),{'seller':user.seller_id}).mappings().all() if internal else []
    return {'state':jsonable_encoder(db.get(State,1)),'sellers':rows(Seller,sellers),'products':rows(Product,products),'listings':rows(Listing,listings),'orders':order_data,'items':item_data,'shipments':rows(Shipment,select(Shipment).where(Shipment.item_id.in_(item_ids))),'returns':returns,'refunds':rows(Refund,select(Refund).where(Refund.return_id.in_([x['id'] for x in returns]))),'allocations':allocations if internal else [],'payouts':rows(Payout,select(Payout).where(Payout.allocation_id.in_(alloc_ids))) if internal else [],'balances':[dict(x) for x in balances],'events':rows(Event) if user.role in ('operator','support') else []}
class Action(BaseModel):
    action:str
    data:dict=Field(default_factory=dict)
    idempotency_key:str
@app.post('/api/commands')
def command(body:Action,user=Depends(identity),db=Depends(db_session)):
    try:
        result=execute(db,user,body.idempotency_key,body.action,body.data); db.commit(); return result
    except BusinessError as e:
        db.rollback(); raise HTTPException(409,str(e))
@app.get('/api/conversations')
def conversations(user=Depends(identity),db=Depends(db_session)):
    role(user,'support','operator')
    return [{'id':c.id,'title':c.title,'runtime':runtime_binding(c)['runtime']} for c in db.scalars(select(Conversation).where(Conversation.owner_id==user.id)).all()]
from .platform_runtime import binding as runtime_binding, configured as runtime_configured, initial_items, options as runtime_options, validate_controls, hosted_answer

class NewConversation(BaseModel):
    runtime:Literal['sdk','lyzr','google']='sdk'
    model_config={'extra':'forbid'}

@app.get('/api/runtimes')
def available_runtimes(user=Depends(identity)):
    role(user,'support','operator')
    return runtime_options()

@app.post('/api/conversations')
def create_conversation(body:NewConversation=Body(default=NewConversation()),user=Depends(identity),db=Depends(db_session)):
    role(user,'support','operator')
    if not runtime_configured(body.runtime): raise HTTPException(503,'Selected runtime is not configured')
    cid=uid('chat')
    c=Conversation(id=cid,owner_id=user.id,title='New investigation',items=initial_items(body.runtime,user.id,cid))
    db.add(c); db.commit()
    return {'id':c.id,'title':c.title,'runtime':body.runtime}
def owned(db,user,cid):
    role(user,'support','operator'); conv=db.get(Conversation,cid)
    if not conv or conv.owner_id!=user.id: raise HTTPException(404,'Conversation not found')
    return conv
@app.get('/api/conversations/{cid}/runs')
async def runs(cid:str,user=Depends(identity),db=Depends(db_session)):
    conversation=owned(db,user,cid)
    records=db.scalars(select(Run).where(Run.conversation_id==cid).order_by(Run.created_at)).all()
    if records:
        from .platform_runtime import refresh_lyzr_sources
        await refresh_lyzr_sources(db,conversation,records[-1])
    ratings={f.run_id:f.rating for f in db.scalars(select(AnswerFeedback).join(Run).where(Run.conversation_id==cid)).all()}
    return [{**jsonable_encoder(r),'feedback':ratings.get(r.id)} for r in records]

class FeedbackChange(BaseModel):
    rating:Literal['up','down']

@app.post('/api/conversations/{cid}/runs/{run_id}/feedback')
def rate_answer(cid:str,run_id:str,body:FeedbackChange,user=Depends(identity),db=Depends(db_session)):
    owned(db,user,cid)
    run=db.get(Run,run_id)
    if not run or run.conversation_id!=cid: raise HTTPException(404,'Answer not found')
    if run.status!='completed' or not run.answer: raise HTTPException(409,'Only completed answers can be rated')
    now=datetime.now(timezone.utc)
    statement=insert(AnswerFeedback).values(run_id=run_id,user_id=user.id,rating=body.rating,updated_at=now)
    db.execute(statement.on_conflict_do_update(index_elements=['run_id'],set_={'rating':body.rating,'updated_at':now}))
    db.commit()
    from .feedback import export_rating
    export_rating(run,body.rating,user.id)
    return {'run_id':run_id,'rating':body.rating}

from .security_demo import Guardrail, PROFILES, PAYLOADS, validate_settings, is_test, fixture_status, set_fixture, LOCK
from .security_marker import MARKER_PROMPTS

@app.get("/api/security-demo")
def security_demo(user=Depends(identity)):
    role(user,"support","operator")
    return {"workspace":"test" if is_test() else "main", "profiles":list(PROFILES), "prompt_toggle_allowed":is_test(), "fixture":fixture_status(), "variants":list(PAYLOADS) if is_test() else [], "marker_prompts":MARKER_PROMPTS if is_test() else {}}

class FixtureChange(BaseModel):
    variant:str

@app.post("/api/security-demo/fixture")
async def security_fixture(body:FixtureChange,user=Depends(identity)):
    role(user,"support","operator")
    if not is_test(): raise HTTPException(403,"Fixtures are only available in the test workspace")
    try: return await set_fixture(body.variant)
    except ValueError as exc: raise HTTPException(400,str(exc))
    except RuntimeError as exc: raise HTTPException(409,str(exc))
    except Exception: raise HTTPException(503,"Fixture preparation failed; check embedding gateway readiness. Previous fixture retained.")

class Question(BaseModel):
    model_config={'extra':'forbid'}
    question:str=Field(min_length=1,max_length=4000)
    memory_enabled:bool=False
    memory_write:bool=False
    guardrail:Guardrail="off"
    suppress_catalog:bool=False
    suppress_documents:bool=False
    source_authority:bool=True
    marker_mode:str="off"
    loop_mode:Literal['normal','tool_error','turn_limit']='normal'
    routing_policy:str='off'
    design_mode:Literal['off','single','review']='off'
    generator_model:Literal['nano','gpt54']='nano'
    reviewer_model:Literal['nano','gpt54']='gpt54'

@app.get('/api/agent-design-demo')
def agent_design_demo_options(user=Depends(identity)):
    role(user, 'support', 'operator')
    from .agent_design_demo import enabled, MODELS
    return {'enabled': enabled(), 'models': MODELS if enabled() else {}}

@app.get('/api/routing-demo')
def routing_demo_options(user=Depends(identity)):
    role(user, 'support', 'operator')
    from .routing_demo import enabled, POLICIES
    available = enabled()
    return {'enabled': available, 'profiles': [{'id': k, **v} for k, v in POLICIES.items()] if available else []}

@app.get('/api/hosting-lab')
def hosting_lab_options(user=Depends(identity)):
    role(user,'support','operator')
    from .hosting_client import enabled, validate
    validate()
    return {'enabled':enabled()}

@app.get('/api/loop-lab')
def loop_lab_options(user=Depends(identity)):
    role(user,'support','operator')
    from .loop_lab import enabled, MODES
    return {'enabled':enabled(),'modes':list(MODES) if enabled() else []}
@app.post('/api/conversations/{cid}/ask')
async def ask(cid:str,body:Question,user=Depends(identity),db=Depends(db_session)):
    conv=owned(db,user,cid)
    runtime=runtime_binding(conv)['runtime']
    from .routing_demo import validate as validate_routing, configuration as routing_configuration, capture_calls
    try: validate_routing(body.routing_policy, runtime)
    except ValueError as exc: raise HTTPException(403, str(exc))
    from .agent_design_demo import validate as validate_design, configuration as design_configuration
    try: validate_design(body.design_mode, body.generator_model, body.reviewer_model, runtime)
    except ValueError as exc: raise HTTPException(403, str(exc))
    if body.design_mode != 'off' and (body.routing_policy != 'off' or body.memory_enabled or body.memory_write or body.loop_mode != 'normal' or body.marker_mode != 'off' or body.suppress_catalog or body.suppress_documents or body.guardrail != 'off' or not body.source_authority):
        raise HTTPException(400, 'Agent design demo requires routing off, memory off, clean context, source authority on, guardrail off and normal loop mode')
    from .loop_lab import validate as validate_loop, enabled as loop_enabled
    try: validate_loop(body.loop_mode,runtime)
    except ValueError as exc: raise HTTPException(403,str(exc))
    try: validate_controls(runtime,body)
    except ValueError as exc: raise HTTPException(400,str(exc))
    if (body.suppress_catalog or body.suppress_documents) and not is_test(): raise HTTPException(403,'Context comparison is available only in the test workspace')
    if (body.suppress_catalog or body.suppress_documents) and runtime!='sdk': raise HTTPException(400,'Context comparison requires the local SDK runtime')
    if (body.suppress_catalog or body.suppress_documents) and conv.items: raise HTTPException(400,'Start a fresh conversation for a context comparison')
    if not runtime_configured(runtime): raise HTTPException(503,'Selected runtime is not configured')
    from .security_marker import MARKER_PROMPTS
    if body.marker_mode not in MARKER_PROMPTS: raise HTTPException(400, 'Unknown private-instruction mode')
    if body.marker_mode != 'off' and not is_test(): raise HTTPException(403, 'Private-instruction tests require the test workspace')
    try: validate_settings(body.guardrail,body.source_authority)
    except ValueError as exc: raise HTTPException(403,str(exc))
    # Database advisory lock works across backend processes and is released on exit.
    with engine.connect() as lock:
        acquired=lock.execute(text('SELECT pg_try_advisory_lock(hashtext(:cid))'),{'cid':cid}).scalar()
        if not acquired: raise HTTPException(409,'This conversation already has a running question')
        corpus_locked=False
        try:
            prior = db.scalars(select(Run).where(Run.conversation_id == cid).order_by(Run.created_at)).first()
            if prior and (prior.metrics or {}).get('routing', {}).get('policy', 'off') != body.routing_policy:
                raise HTTPException(400, 'Start a fresh conversation before changing the routing policy')
            if prior:
                old=(prior.metrics or {}).get('workflow', {})
                expected={'mode':body.design_mode,'generator':body.generator_model,'reviewer':body.reviewer_model}
                if old.get('mode','off') != body.design_mode or (body.design_mode != 'off' and any(old.get(k) != v for k,v in expected.items())):
                    raise HTTPException(400, 'Start a fresh conversation before changing agent design settings')
            if is_test() and runtime=='sdk':
                corpus_locked=lock.execute(text('SELECT pg_try_advisory_lock_shared(hashtext(:key))'),{'key':LOCK}).scalar()
                if not corpus_locked: raise HTTPException(409,'A document fixture is changing; wait and retry')
            if conv.title=='New investigation': conv.title=body.question[:70]; db.commit()
            if runtime!='sdk':
                return await hosted_answer(db,conv,body.question,body)
            from . import hosting_client
            if hosting_client.enabled():
                try:
                    hosting_client.validate()
                    if body.design_mode != 'off' or body.memory_enabled or body.memory_write or body.guardrail != 'off' or body.loop_mode != 'normal' or body.marker_mode != 'off' or body.suppress_catalog or body.suppress_documents:
                        raise ValueError('Chapter 12 remote agent uses memory off, guardrail off and normal mode')
                    return await hosting_client.answer(cid,body.question)
                except ValueError as exc:
                    raise HTTPException(400,str(exc)) from None
                except RuntimeError as exc:
                    raise HTTPException(502,str(exc)) from None
            from .agent import answer
            lab_config={'loop_mode':body.loop_mode,'tool_transport':'mcp','model':os.getenv('OPENAI_MODEL','gpt-5.4')} if loop_enabled() else None
            from .gateway_identity import for_role, for_key
            route_config = routing_configuration(body.routing_policy, cid)
            if route_config:
                if lab_config: raise HTTPException(400, 'Routing and loop-lab comparisons require separate conversations')
                lab_config = route_config
            design_config = design_configuration(body.design_mode, body.generator_model, body.reviewer_model)
            if design_config:
                if lab_config: raise HTTPException(400, 'Agent design and other lab comparisons require separate conversations')
                lab_config = design_config
            key_context = for_key(os.environ['EVAL_GATEWAY_KEY']) if (route_config or design_config) else for_role(user.role)
            with key_context, capture_calls():
                return await answer(cid,body.question,evaluation_config=lab_config,memory_enabled=body.memory_enabled,memory_write=body.memory_write,guardrail=body.guardrail,source_authority=body.source_authority,marker_mode=body.marker_mode,suppress_catalog=body.suppress_catalog,suppress_documents=body.suppress_documents)
        finally:
            if corpus_locked: lock.execute(text('SELECT pg_advisory_unlock_shared(hashtext(:key))'),{'key':LOCK})
            lock.execute(text('SELECT pg_advisory_unlock(hashtext(:cid))'),{'cid':cid})
class MemoryChange(BaseModel):
    expected_version:int=Field(ge=1)
    title:str=Field(min_length=1,max_length=120)
    content:str=Field(min_length=1,max_length=2000)

@app.get('/api/memories')
def memories(user=Depends(identity),db=Depends(db_session)):
    role(user,'support','operator')
    from .memory import record
    return [record(x) for x in db.scalars(select(Memory).where(Memory.owner_id==user.id).order_by(Memory.updated_at.desc())).all()]

@app.patch('/api/memories/{mid}')
def edit_memory(mid:str,body:MemoryChange,user=Depends(identity),db=Depends(db_session)):
    role(user,'support','operator')
    row=db.scalar(select(Memory).where(Memory.id==mid,Memory.owner_id==user.id))
    if not row: raise HTTPException(404,'Memory not found')
    from .memory import MemoryStore,MemoryError
    store=MemoryStore(user.id,row.source_conversation_id,{},allow_write=True)
    try: return store.change(mid,body.expected_version,body.title,body.content)
    except MemoryError as exc: raise HTTPException(409,str(exc))

@app.delete('/api/memories/{mid}')
def forget_memory(mid:str,expected_version:int,user=Depends(identity),db=Depends(db_session)):
    role(user,'support','operator')
    row=db.scalar(select(Memory).where(Memory.id==mid,Memory.owner_id==user.id))
    if not row: raise HTTPException(404,'Memory not found')
    from .memory import MemoryStore,MemoryError
    store=MemoryStore(user.id,row.source_conversation_id,{},allow_write=True)
    try: return store.remove(mid,expected_version)
    except MemoryError as exc: raise HTTPException(409,str(exc))

@app.post('/api/index')
async def index(user=Depends(identity)):
    role(user,'operator')
    from .index import index
    try: return await index()
    except Exception: raise HTTPException(503,'Embedding service unavailable; check gateway/API credentials')
@app.get('/api/readiness')
def readiness(user=Depends(identity),db=Depends(db_session)):
    role(user,'support','operator')
    total=db.scalar(select(func.count()).select_from(Document)); indexed=db.scalar(select(func.count()).select_from(Document).where(Document.embedding!=None))
    return {'documents':total,'indexed':indexed,'retrieval':'pgvector' if total and indexed==total else 'lexical fallback; index documents to enable vectors','cross_session_memory':'explicit user-scoped function tools','agent':'single','model_alias':'support-model'}
