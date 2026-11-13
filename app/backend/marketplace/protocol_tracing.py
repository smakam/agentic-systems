"""Credential-free protocol observations and cross-service trace correlation."""
from contextlib import contextmanager, nullcontext
import logging
import re

log = logging.getLogger(__name__)

def _client():
    # Reuse the application's configured Langfuse client and SDK instrumentation.
    from .agent import lf
    return lf

def incoming_trace(value):
    match = re.fullmatch(r'00-([0-9a-f]{32})-([0-9a-f]{16})-0[01]', value or '')
    if not match or int(match[1],16)==0 or int(match[2],16)==0: return None
    return {'trace_id':match[1], 'parent_span_id':match[2]}

def outgoing_headers():
    client = _client()
    trace = client.get_current_trace_id() if client else None
    parent = client.get_current_observation_id() if client else None
    return {'traceparent':f'00-{trace}-{parent}-01'} if trace and parent else {}

@contextmanager
def protocol_span(name, metadata, *, trace_context=None):
    client = _client()
    manager = client.start_as_current_observation(name=name, as_type='span',
        metadata=metadata, trace_context=trace_context) if client else nullcontext()
    # Only controlled protocol metadata is logged; never headers or message bodies.
    log.info('protocol_start %s %s', name, metadata)
    with manager as observation:
        try:
            yield observation
        except Exception:
            if observation: observation.update(level='ERROR',status_message='Protocol request failed')
            log.warning('protocol_failed %s',name)
            raise
        else:
            log.info('protocol_end %s',name)
