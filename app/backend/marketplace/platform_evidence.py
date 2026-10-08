"""Keep business source envelopes, never provider trace metadata or credentials."""
import ast
import json
import re

BUSINESS_TOOLS = {'begin_investigation', 'end_investigation', 'get_catalog',
                  'query_business_data', 'search_documents', 'fetch_evidence', 'get_order_history'}
FIELDS = {'contract_version', 'status', 'handle', 'snapshot', 'document_revision', 'attempt',
          'type', 'purpose', 'sql', 'params', 'rows', 'columns', 'truncated', 'row_count',
          'elapsed_ms', 'query_hash', 'chunks', 'method', 'effective_at', 'warning', 'tables', 'catalog'}


def source_envelopes(value):
    records = {}
    budget = 0
    def walk(node, depth=0):
        nonlocal budget
        if depth > 12 or len(records) >= 32:
            return
        if isinstance(node, str):
            if len(node) > 1_000_000 or not node.lstrip().startswith(('{', '[')):
                return
            try:
                decoded = json.loads(node)
            except (ValueError, RecursionError):
                try:
                    # Lyzr serializes its MCP result wrapper as a Python literal.
                    decoded = ast.literal_eval(node)
                except (ValueError, SyntaxError, RecursionError):
                    return
            walk(decoded, depth + 1)
        elif isinstance(node, dict):
            handle = node.get('handle', '')
            if (node.get('contract_version') == '1.0' and isinstance(handle, str)
                    and re.fullmatch(r'evidence-[a-f0-9]+', handle)
                    and node.get('type') in {'query', 'documents', 'catalog'}
                    and node.get('status') in {'ok', 'empty'}):
                source = {k: v for k, v in node.items() if k in FIELDS}
                size = len(json.dumps(source))
                if size <= 60_000 and budget + size <= 512_000 and handle not in records:
                    records[handle] = source
                    budget += size
                return
            for item in node.values():
                walk(item, depth + 1)
        elif isinstance(node, list):
            for item in node[:1000]:
                walk(item, depth + 1)
    walk(value)
    return records


def google_sources(events):
    records = {}
    for event in events:
        for part in (event.get('content') or {}).get('parts', []):
            response = part.get('function_response') or part.get('functionResponse') or {}
            if response.get('name') in BUSINESS_TOOLS:
                records.update(source_envelopes(response.get('response')))
    return records


def lyzr_sources(trace, answer):
    spans = trace.get('spans', [])
    # Only the trace that produced this exact answer may supply this run's records.
    if not any(s.get('SpanName') == 'inference' and
               str(s.get('SpanAttributes', {}).get('output', '')).strip() == answer.strip()
               for s in spans):
        return {}
    records = {}
    for span in spans:
        attrs = span.get('SpanAttributes') or {}
        tool = attrs.get('tool_name', '')
        if span.get('SpanName') == 'mcp_tool_call' and any(str(tool).endswith(name) for name in BUSINESS_TOOLS):
            records.update(source_envelopes(attrs.get('result')))
    return records
