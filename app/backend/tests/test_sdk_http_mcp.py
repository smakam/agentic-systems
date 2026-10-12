"""Real SDK HTTP protocol tests with disposable in-memory records; no model calls."""
import asyncio
import socket
import threading
import time
from contextlib import contextmanager
import pytest
import uvicorn
from marketplace.http_mcp_client import InvestigationHTTPServer, HTTPReadContext, BUSINESS_TOOLS, decode_result
from marketplace.remote_mcp import create_app, Investigations
from marketplace.tools import validate_sql

TOKEN = 'test-only-sdk-http-mcp-key-0123456789abcdef'

class FixtureContext:
    def __init__(self):
        self.snapshot = {'revision': 1, 'clock': '2026-09-28T12:00:00Z'}
        self.doc_hash = 'test-policy-revision'
        self.evidence = {}
        self.calls = 0
        self.closed = False
    def save(self, data):
        self.calls += 1
        handle = f'evidence-{id(self)}-{self.calls}'
        result = {'status': 'ok', 'handle': handle, 'snapshot': self.snapshot,
                  'document_revision': self.doc_hash, 'attempt': self.calls, **data}
        self.evidence[handle] = result
        return result
    def catalog(self):
        return self.save({'catalog': {'entities': {'orders': {}}}})
    def query(self, sql, params=None, purpose=''):
        validate_sql(sql)
        return self.save({'rows': [{'order_id': 'order-1', 'order_status': 'paid'}]})
    async def search(self, *args):
        return self.save({'chunks': [{'text': 'Test policy passage'}]})
    def fetch(self, handle):
        if handle not in self.evidence:
            raise ValueError('Unknown evidence handle')
        return self.evidence[handle]
    def order_history(self, order_id):
        return {'current_records': self.query('SELECT id FROM orders'),
                'event_timeline': self.save({'rows': [{'kind': 'purchase'}]})}
    def close(self):
        self.closed = True

@contextmanager
def endpoint():
    registry = Investigations(factory=FixtureContext)
    sock = socket.socket()
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(create_app(TOKEN, registry=registry),
                                          log_level='critical', access_log=False))
    thread = threading.Thread(target=server.run, kwargs={'sockets': [sock]}, daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 5
        while not server.started and thread.is_alive() and time.monotonic() < deadline:
            time.sleep(.01)
        assert server.started
        yield f'http://127.0.0.1:{port}/mcp', registry
    finally:
        server.should_exit = True
        thread.join(timeout=5)
        sock.close()
        assert not thread.is_alive()

def test_http_tools_bind_identity_and_retain_nested_evidence():
    with endpoint() as (url, registry):
        async def run():
            async with InvestigationHTTPServer(url, TOKEN) as server:
                await server.begin()
                ctx = HTTPReadContext(server)
                tools = await server.list_tools()
                assert {t.name for t in tools} == BUSINESS_TOOLS
                assert all('investigation_id' not in t.input_schema['properties'] for t in tools)
                with pytest.raises(ValueError):
                    await server.call_tool('get_catalog', {'investigation_id': 'other'})
                catalog = decode_result(await server.call_tool('get_catalog', {}))
                assert ctx.evidence[catalog['handle']] == catalog
                assert decode_result(await server.call_tool('fetch_evidence', {'handle': catalog['handle']})) == catalog
                rejected = decode_result(await server.call_tool('query_business_data', {'sql': 'DELETE FROM orders'}))
                assert rejected['status'] == 'error'
                history = await ctx.order_history('order-1')
                assert history['order_summary']['handle'] in ctx.evidence
                assert history['event_timeline']['handle'] in ctx.evidence
                await ctx.refresh()
                assert ctx.calls == 4
                await server.end()
                assert ctx.evidence[catalog['handle']] == catalog
            assert not registry.runs
        asyncio.run(run())

def test_http_runs_are_isolated_and_expiry_fails_closed():
    with endpoint() as (url, registry):
        async def run():
            async with InvestigationHTTPServer(url, TOKEN) as a, InvestigationHTTPServer(url, TOKEN) as b:
                await a.begin(); await b.begin()
                assert a.investigation_id != b.investigation_id
                catalog = decode_result(await a.call_tool('get_catalog', {}))
                wrong = decode_result(await b.call_tool('fetch_evidence', {'handle': catalog['handle']}))
                assert wrong['status'] == 'error' and not b.evidence
                registry.runs[b.investigation_id].expires = 0
                expired = decode_result(await b.call_tool('get_catalog', {}))
                assert expired['code'] == 'INVESTIGATION_UNAVAILABLE'
                with pytest.raises(RuntimeError): await HTTPReadContext(b).refresh()
                with pytest.raises(RuntimeError): await b.call_tool('get_catalog', {})
                await a.end()
            assert not registry.runs
        asyncio.run(run())

def test_http_auth_failure_has_no_fallback():
    with endpoint() as (url, registry):
        async def run():
            with pytest.raises(Exception):
                async with InvestigationHTTPServer(url, 'wrong-key-0123456789abcdefghijklmnopqrst') as server:
                    await server.begin()
            assert not registry.runs
        asyncio.run(run())

def test_snapshot_mismatch_invalidates_retained_evidence():
    server = InvestigationHTTPServer('https://example.test/mcp', TOKEN)
    server.snapshot = {'revision': 1}
    server.doc_hash = 'v1'
    with pytest.raises(RuntimeError):
        server.retain({'handle': 'foreign', 'snapshot': {'revision': 2}, 'document_revision': 'v1'})
    assert server.invalid and not server.evidence

def test_durable_json_clock_encoding_retains_same_instant():
    server = InvestigationHTTPServer('https://example.test/mcp', TOKEN)
    server.snapshot = {'revision': 24, 'clock': '2026-09-28T12:00:00Z'}
    server.doc_hash = 'v1'
    # Durable registry stores datetimes using json.dumps(default=str).
    value = {'handle': 'retained', 'snapshot': {'revision': 24, 'clock': '2026-09-28 12:00:00+00:00'},
             'document_revision': 'v1', 'attempt': 1}
    server.retain(value)
    assert server.evidence['retained'] == value and not server.invalid
    server.retain({**value, 'handle': 'second'})
    server.retain(value)  # fetch/replay must not count the same retained envelope twice.
    assert server.calls == 2

@pytest.mark.parametrize('snapshot,doc', [
    ({'revision': 24, 'clock': '2026-09-28 12:00:01+00:00'}, 'v1'),
    ({'revision': 25, 'clock': '2026-09-28 12:00:00+00:00'}, 'v1'),
    ({'revision': 24, 'clock': '2026-09-28 12:00:00+00:00'}, 'v2')])
def test_durable_clock_normalization_still_rejects_real_drift(snapshot, doc):
    server = InvestigationHTTPServer('https://example.test/mcp', TOKEN)
    server.snapshot = {'revision': 24, 'clock': '2026-09-28T12:00:00Z'}
    server.doc_hash = 'v1'
    with pytest.raises(RuntimeError):
        server.retain({'handle': 'foreign', 'snapshot': snapshot, 'document_revision': doc})
    assert server.invalid and not server.evidence

def test_sdk_http_answer_lifecycle_and_cancellation(monkeypatch):
    from marketplace import agent
    with endpoint() as (url, registry):
        monkeypatch.setattr(agent, 'open_http_mcp', lambda: InvestigationHTTPServer(url, TOKEN))
        ids = []
        async def answer(conversation, question, ctx, server, **kwargs):
            ids.append(server.investigation_id)
            value = decode_result(await server.call_tool('get_catalog', {}))
            assert ctx.evidence[value['handle']]
            if question == 'cancel':
                raise asyncio.CancelledError()
            return {'status': 'completed', 'evidence': ctx.evidence}
        monkeypatch.setattr(agent, '_answer', answer)
        async def run():
            for question in ('first', 'follow-up'):
                result = await agent.answer('test', question, evaluation_config={'tool_transport': 'mcp_http'})
                assert result['evidence'] and not registry.runs
            with pytest.raises(asyncio.CancelledError):
                await agent.answer('test', 'cancel', evaluation_config={'tool_transport': 'mcp_http'})
            assert not registry.runs and len(set(ids)) == 3
        asyncio.run(run())

@pytest.mark.parametrize('url', ['http://remote.example/mcp', 'https://user:pass@example.test/mcp',
                                'https://example.test/mcp?key=secret', ''])
def test_endpoint_config_rejects_unsafe_urls(url):
    with pytest.raises(ValueError): InvestigationHTTPServer(url, TOKEN)
