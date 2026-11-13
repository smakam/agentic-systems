"""Read-only local helper through which support delegates a delivery question."""
import json
import uuid
from agents import function_tool
from sqlalchemy import select
from .db import Session, Shipment, ShipmentDeliveryLink
from .delivery_client import DeliveryUnavailable, delivery_request
from .delivery_store import aware_time


def has_delivery_links():
    with Session() as db:
        return db.scalar(select(ShipmentDeliveryLink.shipment_id).limit(1)) is not None


def _verify_findings(findings, shipment_id, reference, clock):
    """Bind read evidence to the requested shipment and question's demo clock."""
    def require(condition):
        if not condition: raise ValueError('Unverified delivery findings')
    require(isinstance(findings,dict))
    require(findings.get('reference')==reference and findings.get('source')=='simulated-delivery-service' and findings.get('simulated') is True)
    require(isinstance(findings.get('findings'),str) and 0 < len(findings['findings'].strip()) <= 12000)
    status=findings.get('shipment_status')
    require(isinstance(status,dict))
    require(status.get('reference')==reference and status.get('marketplace_shipment_id')==shipment_id)
    require(status.get('source')=='simulated-delivery-service' and status.get('simulated') is True)
    require(status.get('status') in ('in_transit','exception','delivered') and status.get('fixture') in ('normal','exception'))
    when=aware_time(clock)
    require(aware_time(status.get('simulation_as_of'))==when)
    aware_time(status.get('observed_at'))
    expected=aware_time(status.get('expected_delivery_at'))
    require(type(status.get('overdue')) is bool and status['overdue']==(status['status']!='delivered' and when>expected))
    require(type(status.get('on_schedule')) is bool and status['on_schedule']==(status['status']=='in_transit' and when<=expected))
    if status['status']=='delivered': require(aware_time(status.get('delivered_at'))<=when)
    else: require(status.get('delivered_at') is None)
    trace=findings.get('tool_trace')
    require(isinstance(trace,list) and 1 <= len(trace) <= 12)
    require(isinstance(trace[0],dict) and trace[0].get('tool')=='get_current_shipment_status' and trace[0].get('result')==status)
    for call in trace:
        require(isinstance(call,dict) and call.get('tool') in ('get_current_shipment_status','get_delivery_problem_details'))
        evidence=call.get('result')
        require(isinstance(evidence,dict) and evidence.get('reference')==reference and evidence.get('source')=='simulated-delivery-service' and evidence.get('simulated') is True)
        aware_time(evidence.get('observed_at'))
        if call['tool']=='get_current_shipment_status':
            require(evidence.get('marketplace_shipment_id')==shipment_id and aware_time(evidence.get('simulation_as_of'))==when)
    if status['status']=='exception' or status['overdue']:
        require(any(call['tool']=='get_delivery_problem_details' for call in trace))


def build_delivery_tool(ctx):
    ctx.delivery_evidence = {}
    calls = 0

    async def investigate_delivery(shipment_id:str, question:str) -> dict:
        """Investigate a shipment with the remote delivery agent. Use its reference/evidence for linked shipments; unlinked shipments retain local marketplace status. Find the shipment ID using marketplace read tools first. Read-only: cannot book, dispatch or deliver."""
        nonlocal calls
        calls += 1
        if calls > 4:
            return {'status':'error', 'code':'DELIVERY_BUDGET_EXHAUSTED', 'message':'Limit delivery delegation to four calls per support question.'}
        if not isinstance(shipment_id, str) or len(shipment_id) > 120 or not question.strip() or len(question) > 4000:
            return {'status':'error', 'code':'DELIVERY_REQUEST_REJECTED', 'message':'Use one shipment ID and a short delivery question.'}
        with Session() as db:
            shipment = db.get(Shipment, shipment_id)
            link = db.get(ShipmentDeliveryLink, shipment_id)
            if shipment is None:
                return {'status':'error', 'code':'SHIPMENT_NOT_FOUND', 'message':'Shipment not found'}
            if link is None:
                payload = {'type':'delivery', 'shipment_id':shipment_id, 'source':'marketplace-local',
                           'status':'ok', 'linked':False, 'shipment_status':shipment.status,
                           'delivered_at':shipment.delivered_at, 'note':'This shipment is not enrolled with the delivery service; these are local marketplace records.'}
            else:
                reference = link.reference
                payload = None
        if payload is None:
            clock = ctx.snapshot['clock']
            try:
                findings = await delivery_request('investigate', {'reference':reference, 'question':question,
                        'as_of':clock.isoformat() if hasattr(clock,'isoformat') else str(clock)})
                _verify_findings(findings,shipment_id,reference,clock)
                payload = {'type':'delivery', 'shipment_id':shipment_id, 'status':'ok', 'linked':True,
                           'source':'simulated-delivery-service', 'result':findings,
                           'note':'Fresh remote simulated delivery findings; marketplace snapshot may precede this remote observation.'}
            except DeliveryUnavailable:
                payload = {'type':'delivery', 'shipment_id':shipment_id, 'status':'error', 'linked':True,
                           'source':'simulated-delivery-service', 'code':'DELIVERY_UNAVAILABLE',
                           'message':'Delivery service is unavailable; no fresh remote status or reason was verified. Do not present local status as a new delivery-service result.'}
            except (ValueError,TypeError,KeyError):
                payload = {'type':'delivery', 'shipment_id':shipment_id, 'status':'error', 'linked':True,
                           'source':'simulated-delivery-service', 'code':'DELIVERY_UNVERIFIED',
                           'message':'Delivery service returned mismatched or incomplete evidence. No remote delivery conclusion was verified; do not substitute local status as a fresh remote result.'}
        # Use the existing citation contract so links in the support answer
        # resolve through the same evidence viewer as database/MCP results.
        handle = 'evidence-' + uuid.uuid4().hex[:12]
        envelope = json.loads(json.dumps({'contract_version':'1.0', 'handle':handle,
                 'snapshot':ctx.snapshot, 'document_revision':ctx.doc_hash, **payload},default=str))
        if len(json.dumps(envelope)) > 60000:
            return {'status':'error', 'code':'DELIVERY_RESULT_TOO_LARGE', 'message':'Delivery evidence exceeded the response limit.'}
        ctx.delivery_evidence[handle] = envelope
        ctx.evidence[handle] = envelope
        return envelope

    return function_tool(investigate_delivery)
