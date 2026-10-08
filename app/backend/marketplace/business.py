"""All simulated business writes serialize on the demo state row.

This keeps the demo understandable and prevents stock/money races. It is not
intended as a high-throughput commerce architecture.
"""
import hashlib, json, uuid
from datetime import timedelta, datetime, timezone
from sqlalchemy import select, func
from .db import *

class BusinessError(ValueError): pass

def uid(prefix): return f'{prefix}-{uuid.uuid4().hex[:10]}'
def require(condition, message):
    if not condition: raise BusinessError(message)
def own_item(db, actor, item):
    require(item is not None, 'Item not found')
    require(actor.role == 'operator' or (actor.role == 'seller' and actor.seller_id == item.seller_id), 'Not authorized for this item')
def emit(db, state, entity, kind, details):
    db.add(Event(id=uid('evt'), entity_id=entity, kind=kind, occurred_at=state.clock, recorded_at=datetime.now(timezone.utc), revision=state.revision, details=details))

def execute(db, actor, key, action, data):
    require(8 <= len(key) <= 120, 'An idempotency key of 8–120 characters is required')
    state = db.execute(select(State).where(State.id == 1).with_for_update()).scalar_one()
    command_id = f'{actor.id}:{key}'
    fingerprint = hashlib.sha256(json.dumps([action, data], sort_keys=True).encode()).hexdigest()
    previous = db.get(Command, command_id)
    if previous:
        require(previous.fingerprint == fingerprint, 'Idempotency key already used for a different request')
        return previous.result
    state.revision += 1
    result = _apply(db, actor, state, action, data)
    db.flush()
    result.update(revision=state.revision, as_of=state.clock.isoformat())
    db.add(Command(id=command_id, actor_id=actor.id, fingerprint=fingerprint, result=result))
    emit(db, state, result.get('id', 'marketplace'), action, {'actor':actor.id, **data})
    return result

def _apply(db, actor, state, action, data):
    if action == 'purchase':
        require(actor.role == 'buyer', 'Only buyers can purchase')
        lines = data.get('items', [])
        require(isinstance(lines, list) and 0 < len(lines) <= 10, 'Choose 1–10 distinct listings')
        require(len({x.get('listing_id') for x in lines}) == len(lines), 'Merge duplicate listings')
        order = Order(id=uid('ord'), customer_id=actor.id, status='paid', created_at=state.clock)
        db.add(order); db.flush()
        payment = Payment(id=uid('pay'), order_id=order.id, amount=0, status='captured', currency='INR')
        db.add(payment); db.flush()
        for line in lines:
            listing = db.get(Listing, line.get('listing_id'))
            qty = line.get('quantity')
            require(type(qty) is int and 1 <= qty <= 20, 'Quantity must be 1–20')
            require(listing is not None and listing.stock >= qty, 'Insufficient inventory')
            listing.stock -= qty
            item = Item(id=uid('item'), order_id=order.id, listing_id=listing.id, seller_id=listing.seller_id, quantity=qty, unit_price=listing.price)
            db.add(item); db.flush()
            gross = qty * listing.price
            allocation = Allocation(id=uid('alloc'), item_id=item.id, payment_id=payment.id, gross=gross, fee=gross//10, refunded=0, policy='settlement-v1')
            db.add(allocation); db.flush()
            db.add(Payout(id=uid('payout'), allocation_id=allocation.id, amount=gross-gross//10, status='held'))
            db.add(Shipment(id=uid('ship'), item_id=item.id, quantity=qty, status='pending'))
            payment.amount += gross
        return {'id':order.id, 'amount':payment.amount}
    if action == 'stock':
        listing = db.get(Listing, data.get('id'))
        require(listing is not None, 'Listing not found')
        require(actor.role == 'operator' or (actor.role == 'seller' and listing.seller_id == actor.seller_id), 'Not authorized')
        require(type(data.get('stock')) is int and 0 <= data['stock'] <= 10000, 'Invalid stock')
        listing.stock = data['stock']; return {'id':listing.id}
    if action in ('dispatch','deliver'):
        shipment = db.get(Shipment, data.get('id'))
        require(shipment is not None, 'Shipment not found')
        item = db.get(Item, shipment.item_id); own_item(db, actor, item)
        expected, target = ('pending','dispatched') if action == 'dispatch' else ('dispatched','delivered')
        require(shipment.status == expected, f'Shipment must be {expected}')
        shipment.status = target
        if action == 'deliver': shipment.delivered_at = state.clock
        return {'id':shipment.id}
    if action == 'advance_clock':
        require(actor.role == 'operator', 'Only operator can advance the clock')
        hours = data.get('hours')
        require(type(hours) is int and 1 <= hours <= 720, 'Choose 1–720 hours')
        state.clock += timedelta(hours=hours)
        return {'id':'demo-clock'}
    if action == 'request_return':
        item = db.get(Item, data.get('id')); require(item is not None, 'Item not found')
        order = db.get(Order,item.order_id)
        require(actor.role == 'buyer' and order.customer_id == actor.id, 'Not authorized')
        shipment = db.scalar(select(Shipment).where(Shipment.item_id == item.id))
        require(shipment.status == 'delivered', 'Return requires delivery')
        require(state.clock <= shipment.delivered_at + timedelta(days=30), 'Return window expired')
        qty = data.get('quantity')
        used = db.scalar(select(func.coalesce(func.sum(Return.quantity),0)).where(Return.item_id == item.id, Return.status != 'rejected'))
        require(type(qty) is int and qty > 0 and used + qty <= item.quantity, 'Invalid return quantity')
        payout = db.scalar(select(Payout).join(Allocation).where(Allocation.item_id == item.id))
        status = 'manual_review' if payout.status == 'completed' else 'requested'
        ret = Return(id=uid('ret'),item_id=item.id,quantity=qty,status=status); db.add(ret)
        return {'id':ret.id, 'status':status}
    if action in ('approve_return','receive_return','reject_return','refund'):
        ret = db.get(Return,data.get('id')); require(ret is not None,'Return not found')
        item = db.get(Item,ret.item_id); own_item(db,actor,item)
        if action != 'refund':
            previous,target = {'approve_return':('requested','approved'),'receive_return':('approved','received'),'reject_return':('requested','rejected')}[action]
            require(ret.status == previous, f'Return must be {previous}'); ret.status=target
            return {'id':ret.id}
        require(actor.role == 'operator', 'Only operator can simulate a refund')
        require(ret.status == 'received', 'Return must be received')
        allocation = db.scalar(select(Allocation).where(Allocation.item_id == item.id))
        payout = db.scalar(select(Payout).where(Payout.allocation_id == allocation.id))
        require(payout.status != 'completed', 'Post-payout refunds require manual review')
        refund = db.scalar(select(Refund).where(Refund.return_id == ret.id))
        require(refund is None or refund.status == 'failed','Refund already processed')
        amount = item.unit_price * ret.quantity
        require(allocation.refunded + amount <= allocation.gross, 'Refund exceeds capture')
        outcome = data.get('outcome','completed'); require(outcome in ('completed','failed'),'Invalid outcome')
        if refund is None:
            refund=Refund(id=uid('refund'),return_id=ret.id,payment_id=allocation.payment_id,amount=amount,status=outcome); db.add(refund)
        else: refund.status=outcome
        if outcome == 'completed':
            allocation.refunded += amount
            allocation.fee = (allocation.gross-allocation.refunded)//10
            payout.amount = allocation.gross-allocation.refunded-allocation.fee
            ret.status='refunded'
            db.get(Listing,item.listing_id).stock += ret.quantity
        return {'id':refund.id,'status':outcome}
    if action == 'payout':
        require(actor.role == 'operator','Only operator can simulate a payout')
        payout=db.get(Payout,data.get('id')); require(payout is not None,'Payout not found')
        require(payout.status in ('held','failed'), 'Payout already completed')
        allocation=db.get(Allocation,payout.allocation_id)
        shipment=db.scalar(select(Shipment).where(Shipment.item_id == allocation.item_id))
        require(shipment.status == 'delivered' and state.clock >= shipment.delivered_at + timedelta(hours=24), 'Delivery and 24-hour hold required')
        active=db.scalar(select(func.count()).select_from(Return).where(Return.item_id==allocation.item_id, Return.status.in_(['requested','approved','received'])))
        require(active == 0,'An active return blocks payout')
        outcome=data.get('outcome','completed'); require(outcome in ('completed','failed'),'Invalid outcome')
        payout.status=outcome
        return {'id':payout.id,'status':outcome,'amount':payout.amount}
    raise BusinessError('Unknown command')
