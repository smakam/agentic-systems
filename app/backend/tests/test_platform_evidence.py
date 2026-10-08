from marketplace.platform_evidence import google_sources, lyzr_sources, source_envelopes
import json

SOURCE = {'contract_version':'1.0', 'handle':'evidence-ab1234', 'status':'ok',
          'type':'query', 'snapshot':{'revision':24}, 'columns':['order_status'],
          'rows':[{'order_status':'paid'}], 'sql':'SELECT order_status FROM orders'}


def test_google_keeps_tool_records_but_not_model_claims():
    tool = {'content':{'parts':[{'function_response':{'name':'get_order_history',
        'response':{'content':[{'type':'text','text':json.dumps({'current_records':SOURCE})}]}}}]}}
    invented = {'content':{'parts':[{'text':json.dumps({**SOURCE,'handle':'evidence-dead'})}]}}
    assert google_sources([tool,invented]) == {'evidence-ab1234':SOURCE}


def test_trace_metadata_does_not_enter_source_records():
    assert source_envelopes({**SOURCE,'Authorization':'private','email':'private'}) == {'evidence-ab1234':SOURCE}


def test_lyzr_requires_matching_final_answer_and_business_tool():
    spans = [{'SpanName':'inference','SpanAttributes':{'output':'paid'}},
        {'SpanName':'mcp_tool_call','SpanAttributes':{'tool_name':'marketplace_get_order_history',
            'result':repr({'response':[{'type':'text','text':json.dumps({'order_summary':SOURCE})}]})}}]
    assert lyzr_sources({'spans':spans},'paid') == {'evidence-ab1234':SOURCE}
    assert lyzr_sources({'spans':spans},'a different answer') == {}
    spans[1]['SpanAttributes']['tool_name']='unrelated_tool'
    assert lyzr_sources({'spans':spans},'paid') == {}


def test_literal_wrapper_never_executes_code():
    assert source_envelopes("{'response': __import__('os').system('false')}") == {}


def test_unknown_contracts_and_oversized_records_are_unavailable():
    assert source_envelopes({**SOURCE,'contract_version':'unrecognized'}) == {}
    assert source_envelopes({**SOURCE,'rows':[{'data':'x'*60001}]}) == {}


def test_catalog_definitions_are_preserved_as_business_evidence():
    catalog={**SOURCE,'type':'catalog','catalog':{'entities':{'orders':{'fields':['status']}}}}
    assert source_envelopes(catalog)['evidence-ab1234']['catalog']==catalog['catalog']
