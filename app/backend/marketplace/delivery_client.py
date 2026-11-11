"""Small A2A 1.0 client. No caller-supplied endpoints or credentials."""
import os
import uuid
import httpx


class DeliveryUnavailable(RuntimeError):
    """A remote error must never masquerade as fresh delivery evidence."""


def configured(write=False):
    return bool(os.getenv('DELIVERY_A2A_URL') and os.getenv('DELIVERY_WRITE_TOKEN' if write else 'DELIVERY_READ_TOKEN'))


async def delivery_request(operation, payload, *, write=False, http_client=None):
    url = os.getenv('DELIVERY_A2A_URL', '').rstrip('/')
    token = os.getenv('DELIVERY_WRITE_TOKEN' if write else 'DELIVERY_READ_TOKEN', '')
    if not url or not token:
        raise DeliveryUnavailable('Simulated delivery service is not configured')
    timeout = float(os.getenv('DELIVERY_A2A_TIMEOUT_SECONDS', '100' if not write else '15'))
    request = {'jsonrpc':'2.0', 'id':uuid.uuid4().hex, 'method':'SendMessage', 'params':{
        'message':{'messageId':uuid.uuid4().hex, 'role':'ROLE_USER',
                   'parts':[{'data':{**payload, 'operation':operation}}]},
        'configuration':{'returnImmediately':False}}}
    async def send(client):
        from .protocol_tracing import protocol_span
        with protocol_span('A2A delivery outbound',{'transport':'a2a','operation':'SendMessage','delivery_operation':operation,'protocol_version':'1.0','request_id':request['id']}) as span:
            return await exchange(client,span)
    async def exchange(client,span):
        try:
            from .protocol_tracing import outgoing_headers
            response = await client.post(url, json=request, headers={'Authorization':'Bearer '+token, 'A2A-Version':'1.0',**outgoing_headers()}, timeout=timeout)
            response.raise_for_status()
            body = response.json()
            if body.get('jsonrpc') != '2.0' or body.get('id') != request['id']:
                raise DeliveryUnavailable('Delivery service response did not match this request')
            task = body.get('result', {}).get('task', {})
            if span: span.update(output={'task_id':task.get('id'),'context_id':task.get('contextId'),'state':task.get('status',{}).get('state'),'http_status':response.status_code})
            if body.get('error') or task.get('status', {}).get('state') != 'TASK_STATE_COMPLETED':
                raise DeliveryUnavailable('Delivery service did not complete the request; marketplace state was not advanced')
            for artifact in task.get('artifacts', []):
                for part in artifact.get('parts', []):
                    result = part.get('data')
                    if isinstance(result, dict):
                        if result.get('source') != 'simulated-delivery-service' or result.get('simulated') is not True:
                            raise DeliveryUnavailable('Delivery service result has no verified simulation source')
                        expected_reference = payload.get('reference')
                        if expected_reference and result.get('reference') != expected_reference:
                            raise DeliveryUnavailable('Delivery service returned a different shipment reference')
                        if operation in ('book','deliver','set_fixture'):
                            if not isinstance(result.get('reference'),str) or not result['reference'] or result.get('status') not in ('in_transit','exception','delivered'):
                                raise DeliveryUnavailable('Delivery service returned an invalid shipment receipt')
                        if operation == 'investigate' and (not isinstance(result.get('findings'),str) or not isinstance(result.get('tool_trace'),list)):
                            raise DeliveryUnavailable('Delivery service returned no investigated findings')
                        return result
            raise DeliveryUnavailable('Delivery service returned no verified result')
        except (httpx.HTTPError, ValueError, TypeError, AttributeError):
            # Never reflect request headers, URLs with secrets, or raw provider
            # errors into the UI/model evidence.
            raise DeliveryUnavailable('Simulated delivery service is unavailable; no fresh delivery result is available') from None
    if http_client is not None:
        return await send(http_client)
    async with httpx.AsyncClient(follow_redirects=False) as client:
        return await send(client)
