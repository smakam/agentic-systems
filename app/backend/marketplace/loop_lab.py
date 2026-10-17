"""Agent Loop controls, restricted to an explicitly enabled disposable database."""
import json
import os
from .course_config import setting
from urllib.parse import urlparse

MODES = ('normal', 'tool_error', 'turn_limit')

def enabled():
    from .db import engine
    reader = urlparse(os.getenv('READ_DATABASE_URL', '')).path.lstrip('/')
    return (setting('AGENT_LOOP_LAB') == 'true'
            and engine.url.database == 'ch11_loop_lab' and reader == 'ch11_loop_lab')

def validate(mode, runtime='sdk'):
    if mode not in MODES:
        raise ValueError('Unknown agent-loop mode')
    if mode != 'normal' and (not enabled() or runtime != 'sdk'):
        raise ValueError('Agent-loop experiments require the Agent Loop SDK lab')

def inject_once(server):
    """Fail the first SQL attempt before execution; retain subsequent real MCP calls."""
    from mcp.types import CallToolResult, TextContent
    original = server.call_tool
    state = {'injected': False, 'attempts': []}
    async def call_tool(tool_name, arguments):
        if tool_name == 'query_business_data' and not state['injected']:
            state['injected'] = True
            payload = {'status': 'error', 'code': 'LAB_TEMPORARY_READ_FAILURE',
                       'retryable': True, 'message': 'Simulated temporary read failure. SQL was not executed. Retry this read once; never interpret this error as no records.'}
            state['attempts'].append({'name': tool_name, 'arguments': arguments, 'injected': True})
            return CallToolResult(content=[TextContent(type='text', text=json.dumps(payload))], is_error=False)
        state['attempts'].append({'name': tool_name, 'arguments': arguments, 'injected': False})
        return await original(tool_name, arguments)
    server.call_tool = call_tool
    return state
