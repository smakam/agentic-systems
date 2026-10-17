import test from 'node:test';
import assert from 'node:assert/strict';
import {newestEvents,eventOrderIds} from './market-view.js';

test('fixed-clock events follow committed sequence, not random IDs, without mutating input',()=>{
 const events=[{id:'event-z',revision:2,occurred_at:'2026-09-28T12:00:00Z'},{id:'event-a',revision:3,occurred_at:'2026-09-28T12:00:00Z'}];
 assert.deepEqual(newestEvents(events).map(e=>e.revision),[3,2]);
 assert.equal(events[0].revision,2);
});
test('seed events at the same revision use business time as a secondary sort',()=>{
 assert.deepEqual(newestEvents([{id:'later',revision:1,occurred_at:'2026-09-27T12:00:00Z'},{id:'earlier',revision:1,occurred_at:'2026-09-24T12:00:00Z'}]).map(e=>e.id),['later','earlier']);
});
const data={orders:[{id:'order-demo'}],items:[{id:'item-demo',order_id:'order-demo'}],shipments:[{id:'ship-demo',item_id:'item-demo'}],returns:[{id:'return-demo',item_id:'item-demo'}],refunds:[{id:'refund-demo',return_id:'return-demo'}],allocations:[{id:'allocation-demo',item_id:'item-demo'}],payouts:[{id:'payout-demo',allocation_id:'allocation-demo'}]};
test('one order is discoverable through purchase, shipment, return, refund and payout references',()=>{
 for(const entity_id of ['order-demo','ship-demo','return-demo','refund-demo','payout-demo'])assert.deepEqual(eventOrderIds({entity_id},data),['order-demo']);
 // Refund retries also carry the return reference; do not duplicate the order label.
 assert.deepEqual(eventOrderIds({entity_id:'refund-demo',details:{id:'return-demo'}},data),['order-demo']);
});
test('clock events and unresolved references never acquire an unrelated order',()=>{
 assert.deepEqual(eventOrderIds({entity_id:'demo-clock'},data),[]);
 assert.deepEqual(eventOrderIds({entity_id:'deleted-refund'},data),[]);
 assert.deepEqual(eventOrderIds({entity_id:'payout-demo'},{}),[]);
});
