"""Runtime and Hosting stateless agent host. No database, gateway or personal memory.

The authenticated local chat backend owns history; this service receives a bounded
SDK transcript and returns the new items plus retained HTTP MCP evidence.
"""
import asyncio
import hmac
import json
import os
from .course_config import setting
import re
import logging
import traceback
from contextlib import asynccontextmanager
from urllib.parse import urlsplit

from agents import Agent, ModelSettings, OpenAIResponsesModel, Runner, RunHooks, set_tracing_disabled
from agents.exceptions import MaxTurnsExceeded
from fastapi import Depends, FastAPI, Header, HTTPException
from openai import AsyncOpenAI
from pydantic import BaseModel, Field, model_validator
from .http_mcp_client import InvestigationHTTPServer

set_tracing_disabled(True)
MAX_SECONDS = 150
INSTRUCTIONS = """You investigate a synthetic marketplace using read-only tools.
Get catalog definitions before writing SQL. Use bound SQL parameters and only
the returned tables and relationships. For an order status use get_order_history.
For payout explanations use order history and applicable policy from search_documents.
Tool errors are unavailable evidence, never empty records. Retry recoverable requests
within the run limit. Never invent failure causes. Money is integer paise; divide by
100 to display rupees. Cite claims with [evidence:HANDLE] using exact returned handles.
Use the current snapshot for current questions; prior prose alone is not current truth.
On EVERY question, including a follow-up with an unchanged revision, call tools again
to obtain current evidence. History resolves references such as 'that payout'; it does
not supply citeable evidence for this run. Never cite a handle from earlier history.
For payout follow-ups call get_order_history and search_documents again, and cite only
handles those calls return during the current investigation.
Return a concise answer and distinguish unknowns. Do not change data or expose secrets.
"""

class Question(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    history: list[dict] = Field(default_factory=list, max_length=200)

    @model_validator(mode='after')
    def bounded_history(self):
        if len(json.dumps(self.history).encode()) > 200_000:
            raise ValueError('History exceeds the lab input limit')
        # The trusted backend sends SDK items, not user-supplied system instructions.
        if any(item.get('role') in ('system', 'developer') for item in self.history):
            raise ValueError('History may not override instructions')
        return self

def configuration():
    token = setting('HOSTED_AGENT_API_KEY', '')
    if len(token) < 32:
        raise RuntimeError('HOSTED_AGENT_API_KEY must contain at least 32 characters')
    url = os.getenv('SDK_MCP_URL', '')
    key = os.getenv('SDK_MCP_API_KEY', '')
    # Validate with the shared HTTPS-only adapter before accepting traffic.
    InvestigationHTTPServer(url, key)
    if not os.getenv('OPENAI_API_KEY'):
        raise RuntimeError('OPENAI_API_KEY is required for the direct provider route')
    return token

async def authenticate(x_api_key: str = Header(default='')):
    expected = setting('HOSTED_AGENT_API_KEY', '')
    if len(expected) < 32 or not hmac.compare_digest(x_api_key, expected):
        raise HTTPException(401, 'Unauthorized')

class Counts(RunHooks):
    def __init__(self): self.models = 0; self.tools = 0
    async def on_llm_end(self, context, agent, response): self.models += 1
    async def on_tool_start(self, context, agent, tool): self.tools += 1

async def investigate(body, *, server_factory=InvestigationHTTPServer, runner=Runner.run, client_factory=AsyncOpenAI):
    configuration()
    hooks = Counts()
    # Explicit URL prevents OPENAI_BASE_URL from silently selecting a gateway.
    async with client_factory(api_key=os.environ['OPENAI_API_KEY'],
                              base_url='https://api.openai.com/v1', max_retries=0, timeout=60) as client:
        async with server_factory(os.environ['SDK_MCP_URL'], os.environ['SDK_MCP_API_KEY']) as server:
            cleanup_confirmed = False
            try:
                await server.begin()
                snapshot = json.loads(json.dumps(server.snapshot, default=str))
                agent = Agent(name='Runtime and Hosting hosted investigator',
                    instructions=INSTRUCTIONS + '\nCurrent snapshot: ' + json.dumps(snapshot)
                        + '\nDocument revision: ' + server.doc_hash,
                    model=OpenAIResponsesModel(model=setting('HOSTED_AGENT_MODEL', 'gpt-5.4'), openai_client=client),
                    mcp_servers=[server], model_settings=ModelSettings(
                        parallel_tool_calls=False, max_tokens=4096, reasoning={'effort': 'low'}))
                inputs = [*body.history, {'role': 'user', 'content': body.question}]
                result = await asyncio.wait_for(runner(agent, inputs, max_turns=8, hooks=hooks), MAX_SECONDS)
                output = str(result.final_output)
                evidence = server.evidence
                handles = re.findall(r'\[evidence:([^\]]+)\]', output)
                # This lab refreshes records; old evidence is not sent independently.
                if not evidence or not handles or any(handle not in evidence for handle in handles):
                    raise RuntimeError('Answer lacks verified evidence from this investigation')
                new_items = result.to_input_list()[len(body.history):]
                response = {'status': 'completed', 'answer': output, 'items': new_items,
                    'evidence': evidence, 'revision': snapshot['revision'],
                    'metrics': {'model_requests': hooks.models, 'actual_tool_invocations': hooks.tools,
                        'model': setting('HOSTED_AGENT_MODEL', 'gpt-5.4'), 'model_route': 'direct_openai',
                        'execution_host': 'remote_agent', 'tool_transport': 'mcp_http',
                        'mcp_hostname': urlsplit(os.environ['SDK_MCP_URL']).hostname,
                        'document_revision': server.doc_hash, 'snapshot': snapshot}}
            finally:
                if server.investigation_id is not None:
                    await asyncio.wait_for(server.end(), 10)
                    cleanup_confirmed = True
            response['metrics']['investigation_cleanup_confirmed'] = cleanup_confirmed
            return response

@asynccontextmanager
async def lifespan(app):
    configuration()
    yield

app = FastAPI(lifespan=lifespan)

@app.get('/health')
def health(): return {'status': 'ok', 'component': 'hosted-agent', 'model_route': 'direct_openai'}

@app.post('/investigate', dependencies=[Depends(authenticate)])
async def ask(body: Question):
    try:
        return await investigate(body)
    except (MaxTurnsExceeded, TimeoutError):
        raise HTTPException(504, 'Investigation interrupted or exceeded its execution limit; retry the question') from None
    except Exception as exc:
        # Log type and source locations only; exception messages can contain secrets.
        frames = traceback.extract_tb(exc.__traceback__)
        logging.getLogger(__name__).error('Agent dependency failure: %s at %s',
            type(exc).__name__, ' > '.join(f'{f.name}:{f.lineno}' for f in frames))
        # Do not serialize provider exceptions, URLs or credential-bearing headers.
        raise HTTPException(502, 'Agent dependencies or evidence verification unavailable') from None
