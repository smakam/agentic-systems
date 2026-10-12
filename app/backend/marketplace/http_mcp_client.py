"""SDK-managed HTTP MCP, with investigation ownership outside model arguments."""
import json
import os
from datetime import datetime, timezone
from urllib.parse import urlsplit
from agents.mcp import MCPServerStreamableHttp

BUSINESS_TOOLS = frozenset(('get_catalog', 'query_business_data', 'search_documents',
                            'fetch_evidence', 'get_order_history'))
FATAL_CODES = frozenset(('REVISION_CHANGED', 'INVESTIGATION_UNAVAILABLE',
                         'INVESTIGATION_EXPIRED'))

def canonical_snapshot(value):
    """Compare the clock instant across MCP ISO and persisted JSON encodings."""
    if not isinstance(value, dict):
        raise RuntimeError('HTTP MCP returned an invalid snapshot')
    result = dict(value)
    if 'clock' in result:
        clock = datetime.fromisoformat(result['clock'].replace('Z', '+00:00'))
        if clock.tzinfo is None:
            raise RuntimeError('HTTP MCP snapshot clock requires a timezone')
        result['clock'] = clock.astimezone(timezone.utc).isoformat()
    return result

def decode_result(result):
    if result.is_error:
        raise RuntimeError('HTTP MCP protocol call failed')
    texts = [block.text for block in result.content if getattr(block, 'type', None) == 'text']
    if len(texts) != 1:
        raise RuntimeError('HTTP MCP returned an invalid result envelope')
    value = json.loads(texts[0])
    if not isinstance(value, dict):
        raise RuntimeError('HTTP MCP returned an invalid result envelope')
    return value

class InvestigationHTTPServer(MCPServerStreamableHttp):
    """Present five tools to the SDK, injecting one trusted investigation ID."""
    transport_kind = 'http'

    def __init__(self, url, token):
        parsed = urlsplit(url)
        if (parsed.scheme not in ('https', 'http') or not parsed.hostname
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or (parsed.scheme == 'http' and parsed.hostname not in ('localhost', '127.0.0.1'))):
            raise ValueError('SDK MCP endpoint requires HTTPS, or loopback HTTP for testing')
        if len(token) < 32:
            raise ValueError('SDK MCP API key is missing or invalid')
        super().__init__(name='Marketplace read tools (HTTP)',
                         params={'url': url, 'headers': {'x-api-key': token},
                                 'timeout': 60, 'sse_read_timeout': 180},
                         cache_tools_list=True, client_session_timeout_seconds=180,
                         max_retry_attempts=0)
        self.endpoint = parsed.hostname
        self.investigation_id = None
        self.snapshot = None
        self.doc_hash = None
        self.evidence = {}
        self.calls = 0
        self.invalid = False

    async def begin(self):
        if self.investigation_id is not None:
            raise RuntimeError('HTTP MCP investigation already started')
        value = decode_result(await super().call_tool('begin_investigation', {}))
        if value.get('status') != 'ok' or not value.get('investigation_id'):
            raise RuntimeError('HTTP MCP investigation could not start')
        self.investigation_id = value['investigation_id']
        self.snapshot = value['snapshot']
        self.doc_hash = value['document_revision']

    async def end(self):
        key = self.investigation_id
        if key is None:
            return
        try:
            value = decode_result(await super().call_tool('end_investigation', {'investigation_id': key}))
            if not value.get('closed'):
                raise RuntimeError('HTTP MCP investigation cleanup was not confirmed')
        finally:
            self.investigation_id = None

    async def list_tools(self, run_context=None, agent=None):
        tools = await super().list_tools(run_context, agent)
        result = []
        for tool in tools:
            if tool.name not in BUSINESS_TOOLS:
                continue
            tool = tool.model_copy(deep=True)
            tool.input_schema.get('properties', {}).pop('investigation_id', None)
            if 'required' in tool.input_schema:
                tool.input_schema['required'] = [x for x in tool.input_schema['required'] if x != 'investigation_id']
            result.append(tool)
        if {tool.name for tool in result} != BUSINESS_TOOLS:
            raise RuntimeError('HTTP MCP business tool discovery is incomplete')
        return result

    def retain(self, value):
        """Retain nested history/query envelopes for clickable citations after end."""
        if isinstance(value, dict):
            if value.get('code') in FATAL_CODES:
                self.invalid = True
            if 'handle' in value:
                if (canonical_snapshot(value.get('snapshot')) != canonical_snapshot(self.snapshot)
                        or value.get('document_revision') != self.doc_hash):
                    self.invalid = True
                    raise RuntimeError('HTTP MCP evidence snapshot changed')
                self.evidence[value['handle']] = value
                # `attempt` is a retry ordinal, not the investigation's call count.
                # ReadContext increments its budget once per new evidence envelope.
                self.calls = len(self.evidence)
            for child in value.values():
                self.retain(child)
        elif isinstance(value, list):
            for child in value:
                self.retain(child)

    async def call_tool(self, tool_name, arguments=None, meta=None):
        if tool_name not in BUSINESS_TOOLS or self.investigation_id is None or self.invalid:
            raise RuntimeError('HTTP MCP business tool unavailable')
        if 'investigation_id' in (arguments or {}):
            raise ValueError('Investigation identity is managed by the application')
        try:
            result = await super().call_tool(tool_name, {**(arguments or {}),
                                                        'investigation_id': self.investigation_id}, meta)
            self.retain(decode_result(result))
            return result
        except BaseException:
            self.invalid = True
            raise

class HTTPReadContext:
    def __init__(self, server):
        self.server = server
        self.snapshot = server.snapshot
        self.doc_hash = server.doc_hash
        self.evidence = server.evidence

    @property
    def calls(self):
        return self.server.calls

    async def refresh(self):
        if self.server.invalid:
            raise RuntimeError('HTTP MCP investigation could not be verified')

    async def order_history(self, order_id):
        return decode_result(await self.server.call_tool('get_order_history', {'order_id': order_id}))

def open_http_mcp():
    return InvestigationHTTPServer(os.getenv('SDK_MCP_URL', ''), os.getenv('SDK_MCP_API_KEY', ''))
