import asyncio
import unittest
import httpx
from marketplace.routing_demo import validate, configuration, capture_calls, record_routing_call

class RoutingBoundaries(unittest.TestCase):
    def test_main_workspace_and_hosted_runtimes_cannot_select_demo_route(self):
        for available, runtime in [(False, 'sdk'), (True, 'google'), (True, 'lyzr')]:
            with self.assertRaises(ValueError):
                validate('llm_question', runtime, available=available)
        validate('off', 'google', available=False)
        with self.assertRaises(ValueError):
            validate('arbitrary_model', available=True)
        with self.assertRaises(ValueError):
            validate('keyword_conversation', available=True)
        with self.assertRaises(ValueError):
            validate('heuristic_conversation', available=True)
        with self.assertRaises(ValueError):
            validate('heuristic_question', available=False)
        validate('heuristic_question', available=True)

    def test_scope_session_is_stable_and_policy_scoped(self):
        a = configuration('llm_conversation', 'owned-conversation')
        b = configuration('llm_question', 'owned-conversation')
        self.assertNotEqual(a['routing']['session_id'], b['routing']['session_id'])
        self.assertEqual(a, configuration('llm_conversation', 'owned-conversation'))
        self.assertEqual(a['routing']['classifier_model'], b['routing']['classifier_model'])

class RoutingEvidence(unittest.IsolatedAsyncioTestCase):
    async def test_concurrent_requests_do_not_mix_model_evidence(self):
        async def call(model):
            with capture_calls() as calls:
                await asyncio.sleep(0)
                response = httpx.Response(200, json={'model': model}, headers={'x-litellm-response-cost': '0.025'}, request=httpx.Request('POST', 'http://gateway/v1/chat/completions'))
                await record_routing_call(response)
                await asyncio.sleep(0)
                return calls
        first, second = await asyncio.gather(call('model-one'), call('model-two'))
        self.assertEqual([c['answer_model'] for c in first], ['model-one'])
        self.assertEqual([c['answer_model'] for c in second], ['model-two'])
        self.assertEqual(first[0]['gateway_answer_cost_usd'], 0.025)

    async def test_failed_calls_do_not_become_completed_model_evidence(self):
        with capture_calls() as calls:
            response = httpx.Response(400, json={'error': 'blocked'}, request=httpx.Request('POST', 'http://gateway/v1/chat/completions'))
            await record_routing_call(response)
            self.assertEqual(calls, [])

if __name__ == '__main__': unittest.main()
