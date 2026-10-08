import asyncio
from types import SimpleNamespace
import pytest
from marketplace.agent import BudgetHooks,CostBudgetExceeded
from marketplace.eval_grading import validate_judge,judge_payload
from marketplace.eval_fixtures import guard_database


def response(i,o):
    return SimpleNamespace(usage=SimpleNamespace(input_tokens=i,output_tokens=o,input_tokens_details=SimpleNamespace(cached_tokens=0)))


def test_cost_rates_and_usage_retained_on_budget_failure():
    hooks=BudgetHooks(2.5,15.,.01)
    with pytest.raises(CostBudgetExceeded):asyncio.run(hooks.on_llm_end(None,None,response(1000,1000)))
    assert hooks.cost==.0175 and hooks.input_tokens==1000 and hooks.output_tokens==1000
    nano=BudgetHooks(.05,.40,1)
    asyncio.run(nano.on_llm_end(None,None,response(1000,1000)))
    assert nano.cost==.00045


def test_guard_rejects_test_and_interactive_databases(monkeypatch):
    for name in ('market','market_test','market_eval_typo'):
        monkeypatch.setenv('DATABASE_URL','postgresql+psycopg://x@postgres/'+name)
        monkeypatch.setenv('READ_DATABASE_URL','postgresql://x@postgres/'+name)
        with pytest.raises(RuntimeError):guard_database()


def test_guard_rejects_mismatched_host(monkeypatch):
    monkeypatch.setenv('DATABASE_URL','postgresql+psycopg://x@a/market_eval')
    monkeypatch.setenv('READ_DATABASE_URL','postgresql://x@b/market_eval')
    with pytest.raises(RuntimeError):guard_database()


def test_judge_input_blinds_model_and_cost():
    payload=judge_payload({'gold':'30 days'},[{'question':'Window?','run':{'answer':'30 days','evidence':{},'metrics':{'model':'nano','cost':1}}}],{},[])
    assert 'metrics' not in payload['candidate_turns'][0]
    assert 'model' not in payload['candidate_turns'][0]
    assert payload['gold_requirements']=='30 days'


def test_malformed_judge_does_not_become_pass():
    with pytest.raises((KeyError,AssertionError)):validate_judge({'correctness':True})


def test_failed_tool_attempt_is_recorded():
    hooks=BudgetHooks();tool=SimpleNamespace(name='query_business_data');ctx=SimpleNamespace(tool_arguments='{"sql":"bad"}')
    asyncio.run(hooks.on_tool_start(ctx,None,tool))
    asyncio.run(hooks.on_tool_end(ctx,None,tool,'{"status":"error","code":"QUERY_REJECTED"}'))
    assert hooks.tool_attempts[0]['status']=='error'
    assert hooks.tool_attempts[0]['result']['code']=='QUERY_REJECTED'


def test_judge_fences_and_malformed_outputs():
    import json
    from marketplace.eval_grading import parse_judge
    value={'correctness':2,'readability':2,'required_facts':[],'unsupported_claims':[],'evidence_sufficient':True,'uncertain':False,'rationale':'Matches gold'}
    assert parse_judge('```json\n'+json.dumps(value)+'\n```')==value
    with pytest.raises((ValueError,AssertionError)):parse_judge('```json\n{"correctness":2')
