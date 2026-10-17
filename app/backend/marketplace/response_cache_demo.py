"""Request-scoped opt-in cache evidence for the normal Test SDK flow."""
from contextlib import contextmanager
from contextvars import ContextVar
import hashlib
from opentelemetry import trace

_calls=ContextVar('response_cache_demo_calls',default=None)
def validate(selected, *, available, runtime, routing, design, memory, guardrail, loop):
    if selected and (not available or runtime!='sdk' or routing!='off' or design!='off' or memory or guardrail!='off' or loop!='normal'):
        raise ValueError('Response caching requires normal Test SDK support, memory off and guardrails off')
def controls(selected, scope, revision, document_revision):
    if not selected:return {'no-cache':True,'no-store':True}
    namespace=hashlib.sha256(f'{scope}:{revision}:{document_revision}'.encode()).hexdigest()[:32]
    return {'use-cache':True,'ttl':120,'namespace':'marketplace-test-'+namespace}
@contextmanager
def capture():
    calls=[];token=_calls.set(calls)
    try:yield calls
    finally:_calls.reset(token)
def observed():return list(_calls.get() or [])
async def record(response):
    calls=_calls.get()
    if calls is None or response.status_code!=200 or not response.request.url.path.endswith('/chat/completions'):return
    if 'application/json' not in response.headers.get('content-type','').lower():return
    try:
        await response.aread();value=response.json()
        # This gateway emits its cache-key header on a response-cache hit.
        # Provider prompt-cache tokens are deliberately not used as this signal.
        hit=bool(response.headers.get('x-litellm-cache-key'))
        item={'cache_hit':hit,'response_id':value.get('id'),'model':value.get('model')}
        calls.append(item)
        span=trace.get_current_span()
        if span.is_recording():
            span.set_attribute('langfuse.observation.metadata.gateway_response_cache_hit',hit)
            span.set_attribute('langfuse.observation.metadata.gateway_response_id',str(value.get('id','')))
            span.set_attribute('langfuse.observation.metadata.gateway_cache_evidence','x-litellm-cache-key response header')
    except Exception:return
