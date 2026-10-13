"""Observe gateway model-call messages after pre-call filtering, without copying headers or keys.

This uses LiteLLM's success callback; it is not a raw HTTP wire capture. Only support requests carrying an explicit investigation link are logged.
"""
import asyncio
import copy
import logging
import os
import re
import json
import secrets
import time
from litellm.integrations.custom_logger import CustomLogger


class ProviderInputAudit(CustomLogger):
    def __init__(self):
        super().__init__()

    async def async_log_success_event(self, kwargs, response_obj, start_time, end_time):
        # Success callbacks run on LiteLLM's asynchronous logging worker. Move
        # the bounded synchronous exporter off the request event loop.
        await asyncio.to_thread(self.log_request_audit, kwargs)

    async def async_post_call_success_hook(self, data, user_api_key_dict, response):
        # In the pinned gateway version, the provider-call success event is
        # queued before this awaited proxy hook. Finish queued audit exports
        # while request-based Cloud Run still allocates CPU. Do not use `data`
        # as audit input: only the success callback supplies the checked,
        # post-filter model-call messages.
        try:
            from litellm.litellm_core_utils.logging_worker import GLOBAL_LOGGING_WORKER
            await asyncio.wait_for(GLOBAL_LOGGING_WORKER.flush(), timeout=8)
        except Exception:
            # Timeout/export failures must not turn a valid answer into an
            # error, and warnings must never include request data or secrets.
            logging.getLogger(__name__).warning('Gateway audit queue drain unavailable')
        return response

    def log_request_audit(self, kwargs):
        metadata = (kwargs.get('litellm_params') or {}).get('metadata') or {}
        trace_id = metadata.get('marketplace_trace_id', '')
        parent_id = metadata.get('marketplace_parent_id', '')
        if not re.fullmatch(r'[0-9a-f]{32}', trace_id):
            return
        # Callback request messages are checked in end-to-end masking tests.
        body = {'messages': kwargs.get('messages'), 'model': kwargs.get('model')}
        if not isinstance(body.get('messages'), list):
            logging.getLogger(__name__).warning('Gateway audit: provider message body unavailable')
            return
        try:
            import httpx
            now = str(time.time_ns())
            attrs = {
                'langfuse.observation.type': 'span',
                'langfuse.observation.input': json.dumps(copy.deepcopy(body['messages'])),
                'langfuse.observation.metadata': json.dumps({
                    'boundary': 'gateway model-call request messages in success callback, after pre-call filtering',
                    'model': body.get('model'),
                    'run_id': metadata.get('marketplace_run_id'),
                    'selected_guardrails': metadata.get('marketplace_guardrails', []),
                    'routing_policy': metadata.get('marketplace_routing_policy'),
                    'routing_scope': metadata.get('marketplace_routing_scope'),
                    'routing_classifier': metadata.get('marketplace_routing_classifier'),
                    'routing_decision': {k: v for k, v in (metadata.get('routing_decision') or {}).items() if k in ('router_model_name', 'routed_model', 'cause', 'tier', 'score', 'classifier_model', 'classifier_cost', 'conversation_continuing')},
                    'note': 'Input audit only; not another model generation or proof of provider receipt. Original app trace is not scrubbed.',
                }),
            }
            span = {
                'traceId': trace_id, 'spanId': secrets.token_hex(8),
                'name': 'Gateway routing decision → Model input' if metadata.get('routing_decision') else 'Gateway output → Model input', 'kind': 1,
                'startTimeUnixNano': now, 'endTimeUnixNano': now,
                'attributes': [{'key': k, 'value': {'stringValue': v}} for k, v in attrs.items()],
                'status': {'code': 1},
            }
            if re.fullmatch(r'[0-9a-f]{16}', parent_id):
                span['parentSpanId'] = parent_id
            payload = {'resourceSpans': [{
                'resource': {'attributes': [{'key': 'service.name', 'value': {'stringValue': 'marketplace-gateway'}}]},
                'scopeSpans': [{'scope': {'name': 'marketplace.gateway-audit'}, 'spans': [span]}],
            }]}
            response = httpx.post(
                os.environ['LANGFUSE_HOST'].rstrip('/') + '/api/public/otel/v1/traces',
                auth=(os.environ['LANGFUSE_PUBLIC_KEY'], os.environ['LANGFUSE_SECRET_KEY']),
                json=payload, headers={'x-langfuse-ingestion-version': '4'}, timeout=3,
            )
            response.raise_for_status()
        except Exception:
            # Observability must not change whether the provider request succeeds.
            logging.getLogger(__name__).warning('Gateway provider-input audit unavailable')


provider_input_audit = ProviderInputAudit()
