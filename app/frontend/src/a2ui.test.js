import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {displayMessages} from './a2ui.js';
const fixture=JSON.parse(readFileSync(new URL('../../backend/tests/fixtures/a2ui-answer.json',import.meta.url)));
const altered=fn=>{const x=structuredClone(fixture);fn(x[0].createSurface);return x};
test('official Python compiler payload passes the client boundary',()=>{
 assert.equal(displayMessages(fixture),fixture);
 assert.equal(fixture[0].createSurface.dataModel.records.r0.fields[1].value,'dispatched');
});
for(const [name,change] of Object.entries({
 'unknown component':s=>s.components[0].component='Button',
 'active property':s=>s.components[0].action={name:'refund'},
 'literal business text':s=>s.components[1].text='delivered',
 'unknown evidence':s=>s.components[0].record={'@path':'/records/missing'},
 'wrong binding type':s=>s.components[0].record={'@path':'/answer'},
 'non-event timeline':s=>{s.components[0]={id:'summary',component:'EventTimeline',dataset:{'@path':'/datasets/d0'}}},
 'data forwarding':s=>s.sendDataModel=true,
 'unknown top-level property':s=>s.theme={color:'red'},
 'broken rows':s=>s.dataModel.datasets.d0.rows=[['only one column']],
 'missing complete answer':s=>s.components.splice(1,1)
}))test(`rejects ${name} before rendering`,()=>assert.throws(()=>displayMessages(altered(change))));

test('only stored history actions become follow-up questions',async()=>{
 const {historyAction}=await import('./a2ui.js');
 assert.deepEqual(historyAction(fixture,{name:'show_order_history',context:{actionId:'a0'}}),{actionId:'a0',orderId:'order-1',question:'Show the recorded event history for order order-1.'});
 assert.throws(()=>historyAction(fixture,{name:'refund',context:{actionId:'a0'}}));
 assert.throws(()=>historyAction(fixture,{name:'show_order_history',context:{actionId:'missing'}}));
});
test('no business mutation can be injected through a button',()=>{
 const x=altered(s=>s.components.push({id:'bad',component:'Button',child:'answer',action:{event:{name:'refund',context:{actionId:'a0'}}}}));
 assert.throws(()=>displayMessages(x));
});
