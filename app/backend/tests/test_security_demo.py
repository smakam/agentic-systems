"""Non-destructive tests: no seed/reset and no paid model calls."""
import asyncio, json
from types import SimpleNamespace
import httpx, pytest
from openai import AsyncOpenAI, BadRequestError
from agents import Agent, Runner, ModelSettings, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from marketplace import security_demo as demo


def test_main_cannot_weaken_prompt_or_change_documents(monkeypatch):
    monkeypatch.setattr(demo,'engine',SimpleNamespace(url=SimpleNamespace(database='market')))
    with pytest.raises(ValueError,match='only be disabled'): demo.validate_settings('off',False)
    with pytest.raises(ValueError,match='restricted'): asyncio.run(demo.set_fixture('clean'))
    assert demo.validate_settings('lakera',True)['source_authority']


def test_test_workspace_allows_prompt_comparison_and_rejects_unknown_profile(monkeypatch):
    monkeypatch.setattr(demo,'engine',SimpleNamespace(url=SimpleNamespace(database='market_test')))
    assert demo.validate_settings('off',False)['source_authority'] is False
    with pytest.raises(ValueError,match='Unknown'): demo.validate_settings('unknown',True)


def test_detector_block_distinct_from_setup_failure():
    request=httpx.Request('POST','http://gateway/v1/chat/completions')
    def error(status,body):
        return BadRequestError('gateway error',response=httpx.Response(status,request=request),body=body)
    assert demo.guardrail_error(error(400,{'message':'Violated guardrail policy','provider_specific_fields':{'guardrail_name':'marketplace-lakera-pre'}}))['name']=='marketplace-lakera-pre'
    assert demo.guardrail_error(error(400,{'message':'Content blocked: secret'}))
    assert demo.guardrail_error(error(400,{'message':'Blocked entity detected: CREDIT_CARD by Guardrail: marketplace-presidio-pre. This entity is not allowed.'}))
    assert demo.guardrail_error(error(400,{'message':'Unknown guardrail name'})) is None
    assert demo.guardrail_error(error(403,{'message':'Violated guardrail policy'})) is None
    assert demo.guardrail_error(RuntimeError('Content blocked: not a gateway response')) is None


def test_guardrail_settings_reach_every_request_in_tool_loop():
    seen=[]
    @function_tool
    def sample_records() -> str:
        return 'Retrieved record: order-2 is held.'
    def respond(request):
        body=json.loads(request.content);seen.append(body)
        message={'role':'assistant','content':'Recorded payout is held.'}
        finish='stop'
        if len(seen)==1:
            message={'role':'assistant','content':None,'tool_calls':[{'id':'call-records','type':'function','function':{'name':'sample_records','arguments':'{}'}}]};finish='tool_calls'
        return httpx.Response(200,json={'id':'chat-test','object':'chat.completion','created':1,'model':'test','choices':[{'index':0,'message':message,'finish_reason':finish}],'usage':{'prompt_tokens':10,'completion_tokens':5,'total_tokens':15}})
    async def run():
        client=AsyncOpenAI(api_key='test-only',base_url='http://gateway/v1',http_client=httpx.AsyncClient(transport=httpx.MockTransport(respond)))
        try:
            agent=Agent(name='test',model=OpenAIChatCompletionsModel(model='test',openai_client=client),tools=[sample_records],model_settings=ModelSettings(extra_body={'guardrails':demo.PROFILES['lakera']}))
            result=await Runner.run(agent,'Check payout')
            assert 'held' in result.final_output
        finally: await client.close()
    set_tracing_disabled(True)
    asyncio.run(run())
    assert len(seen)==2
    assert all(x['guardrails']==['marketplace-lakera-pre'] for x in seen)
    assert any(x['role']=='tool' for x in seen[1]['messages'])


def test_private_instruction_mode_is_enforced_outside_model(monkeypatch):
    from marketplace.security_marker import marker_instructions
    monkeypatch.setattr(demo, 'engine', SimpleNamespace(url=SimpleNamespace(database='market')))
    assert marker_instructions('off') == ''
    for mode in ('without_privacy_rule', 'with_privacy_rule'):
        with pytest.raises(ValueError, match='test workspace'):
            marker_instructions(mode)
    with pytest.raises(ValueError, match='Unknown'):
        marker_instructions('invented')
    monkeypatch.setattr(demo, 'engine', SimpleNamespace(url=SimpleNamespace(database='market_test')))
    assert marker_instructions('without_privacy_rule')
    assert marker_instructions('with_privacy_rule')
