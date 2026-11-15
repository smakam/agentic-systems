import {test} from 'node:test';
import assert from 'node:assert/strict';
import {isolatedHtml,generatedCsp,modeDescriptions,embeddedStyles,controlledHistoryAction} from './agentic-ui.js';
test('controlled history uses only plain application-owned actions',()=>{
 const ui={renderer:'application-prebuilt',selection:{view:'table',reference:'d0'},actions:{a0:{name:'show_order_history',order_id:'order-1'}}};
 assert.deepEqual(controlledHistoryAction(ui,'a0'),{actionId:'a0',orderId:'order-1',question:'Show the recorded event history for order order-1.'});
 assert.equal(controlledHistoryAction(ui,'a7'),null);
 assert.equal(controlledHistoryAction({...ui,renderer:'other'},'a0'),null);
 assert.equal(controlledHistoryAction({...ui,actions:{a0:{name:'refund',order_id:'order-1'}}},'a0'),null);
});
test('embedded stylesheet removes complete font imports containing semicolons',()=>{
 const rules=':root{font-family:Arial,sans-serif}.a2ui-record{padding:12px}';
 for(const resource of ['url("https://fonts.example/css?family=Sans:wght@400;500;700")','"https://fonts.example/css?family=Sans:wght@400;500;700"',"url('https://fonts.example/css?family=Sans:wght@400;500;700')"]){
  assert.equal(embeddedStyles(`@import ${resource};${rules}`),rules);
 }
 assert.equal(embeddedStyles(rules),rules);
});
test('generated document applies a no-script/no-network policy before model markup',()=>{
 const html=isolatedHtml('<html><script>fetch("https://invalid.example")</script></html>');
 assert.ok(html.indexOf('Content-Security-Policy')<html.indexOf('<html>'));
 assert.match(generatedCsp,/script-src 'none'/);
 assert.match(generatedCsp,/connect-src 'none'/);
 assert.match(generatedCsp,/form-action 'none'/);
 assert.throws(()=>isolatedHtml('x'.repeat(100001)));
 assert.equal(Object.keys(modeDescriptions).length,3);
});

test('only the application bridge receives a script nonce',()=>{
 const doc=isolatedHtml('<html><button data-history-action="a0">History</button></html>',{nonce:'a'.repeat(32),actionIds:['a0'],targetOrigin:'http://127.0.0.1:5181'});
 assert.match(doc,/script-src 'nonce-aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'/);
 assert.doesNotMatch(doc,/script-src 'unsafe-inline'/);
 assert.match(doc,/connect-src 'none'/);
 assert.match(doc,/parent.postMessage/);
 assert.throws(()=>isolatedHtml('<html></html>',{nonce:'bad',actionIds:['a0'],targetOrigin:'http://127.0.0.1:5181'}));
 assert.throws(()=>isolatedHtml('<html></html>',{nonce:'a'.repeat(32),actionIds:['refund'],targetOrigin:'http://127.0.0.1:5181'}));
});
test('generated button messages are source-bound and action-allowlisted',async()=>{
 const {generatedHistoryAction}=await import('./agentic-ui.js');
 const frame={},other={},ui={actions:{a0:{name:'show_order_history',order_id:'order-1'}}};
 const valid={source:frame,data:{type:'marketplace-history',actionId:'a0'}};
 assert.equal(generatedHistoryAction(ui,valid,frame).orderId,'order-1');
 assert.equal(generatedHistoryAction(ui,{...valid,source:other},frame),null);
 assert.equal(generatedHistoryAction(ui,{...valid,data:{...valid.data,actionId:'a7'}},frame),null);
 assert.equal(generatedHistoryAction(ui,{...valid,data:{...valid.data,url:'https://invalid.example'}},frame),null);
 assert.equal(generatedHistoryAction(ui,{...valid,data:{type:'refund',actionId:'a0'}},frame),null);
});
