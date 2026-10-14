"""Select prepared native gateway routes in the disposable test UI; never classify here."""
from contextlib import contextmanager
from contextvars import ContextVar
import math
import os
from opentelemetry import trace

POLICIES = {
    'off': {'label': 'Normal support model'},
    'fixed_nano': {'label': 'Fixed GPT-5 Nano', 'alias': 'eval-nano', 'model': 'gpt-5-nano'},
    'fixed_gpt5': {'label': 'Fixed GPT-5', 'alias': 'eval-5', 'model': 'gpt-5'},
}
for classifier in ('keyword', 'heuristic', 'llm'):
    for scope in (('question',) if classifier != 'llm' else ('conversation', 'question')):
        POLICIES[classifier + '_' + scope] = {
            'label': {'keyword': 'Keyword rules', 'heuristic': 'Built-in heuristic v2', 'llm': 'LLM classifier'}[classifier] + ' / per ' + scope,
            'alias': 'ch16-' + classifier + '-' + scope,
            'model': 'native gateway router', 'classifier': classifier, 'scope': scope,
            'classifier_model': 'eval-nano' if classifier == 'llm' else None,
        }

_calls = ContextVar('routing_demo_calls', default=None)

def enabled():
    from .security_demo import is_test
    return is_test() and bool(os.getenv('EVAL_GATEWAY_KEY'))

def validate(policy, runtime='sdk', available=None):
    if policy not in POLICIES:
        raise ValueError('Unknown routing policy')
    if policy != 'off' and (runtime != 'sdk' or not (enabled() if available is None else available)):
        raise ValueError('Routing comparisons require the configured test workspace and SDK runtime')

def configuration(policy, conversation_id):
    p = POLICIES[policy]
    if policy == 'off':
        return None
    # Conservatively stop on the stronger model's uncached rate; classifier
    # overhead is gateway-side and excluded from this app estimate.
    return {'alias': p['alias'], 'model': p['model'], 'input_rate': 2.5, 'output_rate': 15.0,
            'budget': 1.0, 'routing': {'policy': policy, **p,
                'session_id': 'chapter16:' + conversation_id + ':' + policy}}

@contextmanager
def capture_calls():
    calls = []
    token = _calls.set(calls)
    try:
        yield calls
    finally:
        _calls.reset(token)

def observed_calls():
    return list(_calls.get() or [])

async def record_routing_call(response):
    calls = _calls.get()
    if calls is None or response.status_code != 200 or not response.request.url.path.endswith('/chat/completions'):
        return
    if 'application/json' not in response.headers.get('content-type', '').lower():
        return
    try:
        await response.aread()
        value = response.json()
        model = value.get('model')
        if not isinstance(model, str) or not model or len(model) > 200:
            return
        item = {'answer_model': model}
        try:
            cost = float(response.headers.get('x-litellm-response-cost'))
            if math.isfinite(cost) and cost >= 0:
                item['gateway_answer_cost_usd'] = cost
        except (TypeError, ValueError):
            pass
        calls.append(item)
        span = trace.get_current_span()
        if span.is_recording():
            span.set_attribute('langfuse.observation.model.name', model)
            span.set_attribute('langfuse.observation.metadata.actual_answer_model', model)
    except Exception:
        # Optional evidence collection must never break a successful answer.
        return
