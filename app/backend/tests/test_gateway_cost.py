import asyncio
import json
import unittest

import httpx
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from marketplace.gateway_cost import record_gateway_cost


class GatewayCostTests(unittest.TestCase):
    def setUp(self):
        self.exporter = InMemorySpanExporter()
        self.provider = TracerProvider()
        self.provider.add_span_processor(SimpleSpanProcessor(self.exporter))
        self.tracer = self.provider.get_tracer('gateway-cost-test')

    def tearDown(self):
        self.provider.shutdown()

    def invoke(self, cost, *, kind='LLM', status=200, mime='application/json', path='/v1/chat/completions'):
        async def check():
            headers={'content-type':mime}
            if cost is not None: headers['x-litellm-response-cost']=cost
            response=httpx.Response(status,headers=headers,json={'model':'gpt-5.4','choices':[]},request=httpx.Request('POST','http://gateway'+path))
            with self.tracer.start_as_current_span('generation',attributes={'openinference.span.kind':kind,'llm.token_count.total':100}):
                await record_gateway_cost(response)
            return self.exporter.get_finished_spans()
        return asyncio.run(check())

    def test_enriches_one_existing_generation_without_duplicate_tokens(self):
        spans=self.invoke('0.01234')
        self.assertEqual(len(spans),1)
        a=spans[0].attributes
        self.assertEqual(json.loads(a['langfuse.observation.cost_details']),{'total':0.01234})
        self.assertEqual(a['langfuse.observation.model.name'],'gpt-5.4')
        self.assertEqual(a['llm.token_count.total'],100)
        self.assertNotIn('langfuse.observation.usage_details',a)

    def test_missing_invalid_and_negative_costs_are_not_zero(self):
        for cost in (None,'None','nan','inf','-1'):
            with self.subTest(cost=cost):
                self.exporter.clear()
                spans=self.invoke(cost)
                self.assertNotIn('langfuse.observation.cost_details',spans[0].attributes)

    def test_explicit_zero_cost_is_preserved(self):
        spans=self.invoke('0')
        self.assertEqual(json.loads(spans[0].attributes['langfuse.observation.cost_details']),{'total':0.0})

    def test_other_spans_endpoints_errors_and_streams_are_not_enriched(self):
        for options in ({'kind':'TOOL'},{'status':500},{'mime':'text/event-stream'},{'path':'/v1/embeddings'}):
            with self.subTest(options=options):
                self.exporter.clear()
                spans=self.invoke('0.01',**options)
                self.assertNotIn('langfuse.observation.cost_details',spans[0].attributes)

    def test_http_hook_preserves_the_response_body(self):
        async def check():
            transport=httpx.MockTransport(lambda request:httpx.Response(200,headers={'x-litellm-response-cost':'0.003'},json={'model':'gpt-5.4','choices':[{'message':{'content':'answer'}}]}))
            async with httpx.AsyncClient(transport=transport,event_hooks={'response':[record_gateway_cost]}) as client:
                with self.tracer.start_as_current_span('generation',attributes={'openinference.span.kind':'LLM'}):
                    result=await client.post('http://gateway/v1/chat/completions',json={})
                    self.assertEqual(result.json()['choices'][0]['message']['content'],'answer')
            self.assertEqual(len(self.exporter.get_finished_spans()),1)
        asyncio.run(check())

    def test_real_sdk_instrumentation_exports_cost_once_with_mock_model(self):
        from agents import Agent, Runner, OpenAIChatCompletionsModel, set_trace_processors, set_tracing_disabled
        from openai import AsyncOpenAI
        from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
        set_trace_processors([])
        set_tracing_disabled(False)
        instrumentor=OpenAIAgentsInstrumentor()
        instrumentor.instrument(tracer_provider=self.provider)
        async def check():
            transport=httpx.MockTransport(lambda request:httpx.Response(200,headers={'x-litellm-response-cost':'0.004'},json={'id':'chatcmpl-test','object':'chat.completion','created':0,'model':'gpt-5.4','choices':[{'index':0,'finish_reason':'stop','message':{'role':'assistant','content':'done'}}],'usage':{'prompt_tokens':12,'completion_tokens':3,'total_tokens':15}}))
            http_client=httpx.AsyncClient(transport=transport,event_hooks={'response':[record_gateway_cost]})
            api=AsyncOpenAI(api_key='test',base_url='http://gateway/v1',http_client=http_client,max_retries=0)
            try:
                result=await Runner.run(Agent(name='test',model=OpenAIChatCompletionsModel(model='test-alias',openai_client=api)),'test',max_turns=1)
                self.assertEqual(result.final_output,'done')
            finally:
                await api.close()
        try:
            asyncio.run(check())
            generations=[span for span in self.exporter.get_finished_spans() if span.attributes.get('openinference.span.kind')=='LLM']
            self.assertEqual(len(generations),1)
            attributes=generations[0].attributes
            self.assertEqual(json.loads(attributes['langfuse.observation.cost_details']),{'total':0.004})
            self.assertEqual(attributes['langfuse.observation.model.name'],'gpt-5.4')
            self.assertEqual(attributes['llm.token_count.prompt'],12)
            self.assertEqual(attributes['llm.token_count.completion'],3)
        finally:
            instrumentor.uninstrument()
            set_trace_processors([])


if __name__=='__main__':unittest.main()
