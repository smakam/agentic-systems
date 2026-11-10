"""Seller shipping writes coordinated across marketplace and delivery service.

The state lock preserves existing command serialization. A remote success may
precede local commit, so remote booking/update operations are repeat-safe. This
is a demo recovery boundary, not an atomic distributed transaction.
"""
import hashlib
import json
import asyncio
from sqlalchemy import select
from .business import BusinessError, execute, own_item, require
from .db import Command, Item, Shipment, ShipmentDeliveryLink, State
from .delivery_client import DeliveryUnavailable, delivery_request
from .delivery_store import aware_time, DeliveryRecordError


def link_json(db, shipment_id):
    link = db.get(ShipmentDeliveryLink, shipment_id)
    return None if link is None else {'reference':link.reference, 'service':link.service,
                                      'fixture':link.fixture, 'status_source':'fetch from delivery service'}


def _validate_receipt(receipt, shipment_id, clock, statuses, *, reference=None, fixture=None):
    require(isinstance(receipt,dict),'Invalid delivery receipt')
    require(receipt.get('marketplace_shipment_id') == shipment_id,'Delivery receipt does not match this shipment')
    require(isinstance(receipt.get('reference'),str) and 1 <= len(receipt['reference']) <= 120,'Invalid delivery reference')
    require(reference is None or receipt['reference'] == reference,'Delivery receipt does not match this reference')
    require(receipt.get('source') == 'simulated-delivery-service' and receipt.get('simulated') is True,'Delivery receipt source could not be verified')
    require(receipt.get('status') in statuses,'Delivery service has not confirmed this transition')
    require(receipt.get('fixture') in ('normal','exception') and (fixture is None or receipt['fixture']==fixture),'Delivery fixture does not match this request')
    try:
        require(aware_time(receipt.get('simulation_as_of')) == clock,'Delivery receipt uses a different simulation time')
        aware_time(receipt.get('observed_at'))
        expected=aware_time(receipt.get('expected_delivery_at'))
        require(type(receipt.get('overdue')) is bool and receipt['overdue'] == (receipt['status']!='delivered' and clock>expected),'Delivery receipt has inconsistent lateness evidence')
        require(type(receipt.get('on_schedule')) is bool and receipt['on_schedule'] == (receipt['status']=='in_transit' and clock<=expected),'Delivery receipt has inconsistent schedule evidence')
        if receipt['status']=='delivered':
            require(aware_time(receipt.get('delivered_at')) <= clock,'Delivery receipt is dated after the simulation clock')
        else:
            require(receipt.get('delivered_at') is None,'Undelivered shipment has a delivery timestamp')
    except DeliveryRecordError:
        raise BusinessError('Delivery receipt has invalid timestamps') from None
    return receipt


async def execute_shipping_command(db, actor, key, action, data):
    # A second seller request can wait on the state row while the first awaits
    # the carrier. Keep that synchronous PostgreSQL wait off the ASGI loop, or
    # the first request could never receive its network response and commit.
    # A request's Session is used sequentially by this worker, never in parallel.
    return await asyncio.to_thread(_execute_shipping_command, db, actor, key, action, data)


def _execute_shipping_command(db, actor, key, action, data):
    if action not in ('dispatch', 'deliver', 'delivery_fixture'):
        return execute(db, actor, key, action, data)
    require(8 <= len(key) <= 120, 'An idempotency key of 8–120 characters is required')
    state = db.execute(select(State).where(State.id == 1).with_for_update()).scalar_one()
    # Check existing command before an HTTP request; retries after local commit
    # must return the same result even if delivery service is now unavailable.
    previous = db.get(Command, f'{actor.id}:{key}')
    if previous:
        fingerprint = hashlib.sha256(json.dumps([action, data], sort_keys=True).encode()).hexdigest()
        require(previous.fingerprint == fingerprint, 'Idempotency key already used for a different request')
        return previous.result
    shipment = db.get(Shipment, data.get('id'))
    require(shipment is not None, 'Shipment not found')
    own_item(db, actor, db.get(Item, shipment.item_id))
    expected = 'pending' if action == 'dispatch' else 'dispatched'
    require(shipment.status == expected, f'Shipment must be {expected}')
    mode = data.get('delivery_mode', 'local')
    require(mode in ('local', 'a2a'), 'Choose local or A2A delivery')
    link = db.get(ShipmentDeliveryLink, shipment.id)
    if action == 'delivery_fixture':
        require(link is not None, 'Only linked shipments have delivery-service fixtures')
        fixture = data.get('delivery_fixture')
        require(fixture in ('normal','exception'), 'Choose normal or exception delivery fixture')
        receipt = asyncio.run(delivery_request('set_fixture', {'reference':link.reference,
                 'fixture':fixture, 'clock':state.clock.isoformat(),
                 'operation_key':hashlib.sha256(f'{actor.id}:{key}'.encode()).hexdigest()}, write=True))
        _validate_receipt(receipt,shipment.id,state.clock,('in_transit',) if fixture=='normal' else ('exception',),reference=link.reference,fixture=fixture)
        result = execute(db, actor, key, action, data, delivery_result=receipt)
        result['delivery_service'] = link_json(db, shipment.id)
        return result
    if link is None and (action != 'dispatch' or mode == 'local'):
        return execute(db, actor, key, action, data)
    if action == 'dispatch':
        fixture = data.get('delivery_fixture', 'normal')
        require(fixture in ('normal', 'exception'), 'Choose normal or exception delivery fixture')
        receipt = asyncio.run(delivery_request('book', {'shipment_id':shipment.id, 'fixture':fixture, 'clock':state.clock.isoformat()}, write=True))
        _validate_receipt(receipt,shipment.id,state.clock,('in_transit',) if fixture=='normal' else ('exception',),fixture=fixture)
        if link is None:
            link = ShipmentDeliveryLink(shipment_id=shipment.id, reference=receipt['reference'], fixture=fixture)
            db.add(link)
            db.flush()
    else:
        receipt = asyncio.run(delivery_request('deliver', {'reference':link.reference, 'clock':state.clock.isoformat()}, write=True))
        _validate_receipt(receipt,shipment.id,state.clock,('delivered',),reference=link.reference)
        link.fixture = receipt['fixture']
    result = execute(db, actor, key, action, data, delivery_result=receipt)
    result['delivery_service'] = link_json(db, shipment.id)
    return result
