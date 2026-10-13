"""Enrich the active SDK model span with LiteLLM's response cost.

No new spans or usage records are emitted. Missing cost stays missing; the
gateway's configured pricing estimate is not a provider invoice.
"""
import json
import math

from opentelemetry import trace


async def record_gateway_cost(response):
    if response.status_code != 200 or not response.request.url.path.endswith('/chat/completions'):
        return
    span = trace.get_current_span()
    if not span.is_recording() or getattr(span, 'attributes', {}).get('openinference.span.kind') != 'LLM':
        return
    raw_cost = response.headers.get('x-litellm-response-cost')
    try:
        cost = float(raw_cost)
    except (TypeError, ValueError):
        return
    if not math.isfinite(cost) or cost < 0:
        return
    # The app uses non-streaming chat completions. Do not consume an SSE stream.
    if 'application/json' not in response.headers.get('content-type', '').lower():
        return
    try:
        await response.aread()
        result = response.json()
    except Exception:
        # Optional telemetry must not replace a valid model response with an error.
        return
    model = result.get('model') if isinstance(result, dict) else None
    if isinstance(model, str) and model and len(model) <= 200:
        span.set_attribute('langfuse.observation.model.name', model)
    span.set_attribute('langfuse.observation.cost_details', json.dumps({'total': cost}))
    span.set_attribute('langfuse.observation.metadata.cost_source', 'litellm_response_header')
    span.set_attribute('langfuse.observation.metadata.cost_basis', 'gateway configured pricing estimate; not a provider invoice')
