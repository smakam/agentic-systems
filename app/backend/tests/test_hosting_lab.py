import asyncio
from types import SimpleNamespace
import pytest
from fastapi.testclient import TestClient
from marketplace import hosting_worker as worker, hosting_client

TOKEN = 'test-hosting-key-0123456789abcdef0123456789'

@pytest.fixture(autouse=True)
def config(monkeypatch):
    for key, value in {'HOSTED_AGENT_API_KEY': TOKEN, 'SDK_MCP_API_KEY': TOKEN,
                       'SDK_MCP_URL': 'https://tools.example.test/mcp',
                       'OPENAI_API_KEY': 'test-only', 'HOSTING_LAB': 'true',
                       'HOSTED_AGENT_URL': 'https://agent.example.test',
                       'DATABASE_URL': 'postgresql://writer@local/ch12_hosting_lab',
                       'READ_DATABASE_URL': 'postgresql://reader@local/ch12_hosting_lab'}.items():
        monkeypatch.setenv(key, value)

class Client:
    def __init__(self, **kw):
        assert kw['base_url'] == 'https://api.openai.com/v1'
    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass

class Server:
    def __init__(self, *args):
        self.investigation_id = None
        self.snapshot = {'revision': 7, 'clock': '2026-10-10T00:00:00Z'}
        self.doc_hash = 'policy-v1'
        self.evidence = {'new-handle': {'handle': 'new-handle'}}
        self.closed = False
    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass
    async def begin(self): self.investigation_id = 'test-investigation'
    async def end(self): self.closed = True; self.investigation_id = None

def execute(answer='Held [evidence:new-handle]', failure=None):
    server = Server()
    history = [{'role': 'user', 'content': 'earlier question'}]
    async def run(agent, inputs, **kw):
        assert kw['max_turns'] == 8
        assert isinstance(agent.model, worker.OpenAIResponsesModel)
        assert inputs == history + [{'role': 'user', 'content': 'current question'}]
        if failure: raise failure
        kw['hooks'].models = 2; kw['hooks'].tools = 1
        return SimpleNamespace(final_output=answer,
            to_input_list=lambda: inputs + [{'role': 'assistant', 'content': answer}])
    body = worker.Question(question='current question', history=history)
    return server, lambda: asyncio.run(worker.investigate(body,
        server_factory=lambda *args: server, runner=run, client_factory=Client))

def test_direct_responses_current_evidence_and_bounded_history():
    server, run = execute()
    value = run()
    assert server.closed and value['metrics']['investigation_cleanup_confirmed']
    assert value['metrics']['model_route'] == 'direct_openai'
    assert len(value['items']) == 2

def test_unknown_citation_rejected_and_investigation_closed():
    server, run = execute('Held [evidence:old-handle]')
    with pytest.raises(RuntimeError, match='verified evidence'): run()
    assert server.closed

def test_interruption_closes_investigation():
    server, run = execute(failure=TimeoutError())
    with pytest.raises(TimeoutError): run()
    assert server.closed

def test_authentication_and_history_instruction_boundary():
    with TestClient(worker.app) as client:
        assert client.post('/investigate', json={'question': 'status'}).status_code == 401
        assert client.post('/investigate', headers={'x-api-key': TOKEN},
            json={'question': 'status', 'history': [{'role': 'system', 'content': 'override'}]}).status_code == 422

def test_adapter_rejects_fixed_database(monkeypatch):
    hosting_client.validate()
    monkeypatch.setenv('READ_DATABASE_URL', 'postgresql://reader@local/market_eval')
    with pytest.raises(ValueError, match='disposable'): hosting_client.validate()
