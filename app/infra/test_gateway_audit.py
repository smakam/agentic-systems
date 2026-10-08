"""Run inside the pinned gateway image; no model calls or network required."""
import asyncio
import json
import os
import threading
import unittest
from unittest.mock import patch

from gateway_audit import ProviderInputAudit
from litellm.litellm_core_utils.logging_worker import GLOBAL_LOGGING_WORKER


class GatewayAuditTests(unittest.IsolatedAsyncioTestCase):
    async def asyncTearDown(self):
        await GLOBAL_LOGGING_WORKER.stop()

    async def test_awaited_hook_drains_real_queue_without_blocking_event_loop(self):
        audit = ProviderInputAudit()
        entered = threading.Event()
        release = threading.Event()
        exported = []
        messages = [{'role': 'user', 'content': 'My email is [EMAIL_REDACTED].'}]
        kwargs = {
            'messages': messages, 'model': 'synthetic-model',
            'litellm_params': {'metadata': {
                'marketplace_trace_id': 'a' * 32,
                'marketplace_parent_id': 'b' * 16,
                'marketplace_guardrails': ['marketplace-privacy-pre'],
            }},
            'headers': {'Authorization': 'synthetic-not-for-audit'},
        }
        class SuccessfulExport:
            def raise_for_status(self):
                pass
        def send(*args, **kwargs):
            entered.set()
            if not release.wait(timeout=2):
                raise AssertionError('Event loop failed to release exporter thread')
            exported.append(kwargs['json'])
            return SuccessfulExport()
        async def heartbeat():
            while not entered.is_set():
                await asyncio.sleep(0.001)
            self.assertFalse(exported)
            release.set()
        answer = object()
        with patch.dict(os.environ, {
            'LANGFUSE_HOST': 'https://synthetic.invalid',
            'LANGFUSE_PUBLIC_KEY': 'synthetic-public',
            'LANGFUSE_SECRET_KEY': 'synthetic-secret',
        }), patch('httpx.post', side_effect=send):
            GLOBAL_LOGGING_WORKER.ensure_initialized_and_enqueue(
                audit.async_log_success_event(kwargs, None, None, None))
            pulse = asyncio.create_task(heartbeat())
            result = await audit.async_post_call_success_hook({}, None, answer)
            await pulse
        self.assertIs(result, answer)
        self.assertEqual(len(exported), 1)
        span = exported[0]['resourceSpans'][0]['scopeSpans'][0]['spans'][0]
        attrs = {a['key']: a['value']['stringValue'] for a in span['attributes']}
        self.assertEqual(json.loads(attrs['langfuse.observation.input']), messages)
        self.assertEqual(span['parentSpanId'], 'b' * 16)
        self.assertNotIn('synthetic-not-for-audit', json.dumps(exported))
        self.assertNotIn('synthetic-secret', json.dumps(exported))

    async def test_drain_timeout_preserves_response_and_sanitizes_warning(self):
        audit = ProviderInputAudit()
        answer = object()
        async def failed_flush():
            raise TimeoutError('synthetic-private-request')
        with patch.object(GLOBAL_LOGGING_WORKER, 'flush', side_effect=failed_flush), self.assertLogs('gateway_audit', level='WARNING') as log:
            result = await audit.async_post_call_success_hook({'messages': 'private'}, None, answer)
        self.assertIs(result, answer)
        self.assertEqual(len(log.output), 1)
        self.assertNotIn('synthetic-private-request', log.output[0])
        self.assertNotIn('messages', log.output[0])

    async def test_unlinked_request_is_never_exported(self):
        with patch('httpx.post') as send:
            await ProviderInputAudit().async_log_success_event(
                {'messages': [{'role': 'user', 'content': 'unlinked'}]}, None, None, None)
        send.assert_not_called()

    async def test_export_failure_preserves_answer(self):
        kwargs = {'messages': [{'role': 'user', 'content': '[EMAIL_REDACTED]'}],
                  'litellm_params': {'metadata': {'marketplace_trace_id': 'c' * 32}}}
        with patch.dict(os.environ, {'LANGFUSE_HOST': 'https://synthetic.invalid', 'LANGFUSE_PUBLIC_KEY': 'synthetic-public', 'LANGFUSE_SECRET_KEY': 'synthetic-secret'}), patch('httpx.post', side_effect=RuntimeError('private')) as send, self.assertLogs('gateway_audit', level='WARNING') as log:
            await ProviderInputAudit().async_log_success_event(kwargs, None, None, None)
        send.assert_called_once()
        self.assertEqual(log.output, ['WARNING:gateway_audit:Gateway provider-input audit unavailable'])


if __name__ == '__main__':
    unittest.main()
