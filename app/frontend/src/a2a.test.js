import test from 'node:test';
import assert from 'node:assert/strict';
import {request} from './api.js';
import {askA2ASupport,cardInterfaces,dispatchData,isA2AMode,safeCard,shipmentDeliveryAction,shipmentFixtureChange,supportMessage,supportModeLabel,supportTask} from './a2a.js';

const conversation={id:'chat-owned',a2a_context_id:'context-owned',mode:'a2a_support'};
const task={id:'task-new',contextId:conversation.a2a_context_id,status:{state:'TASK_STATE_COMPLETED'},metadata:{run_id:'run-new'}};
const envelope={jsonrpc:'2.0',id:'rpc-1',result:{task}};

test('A2A browser request uses pinned v1 wire schema and preserves question options',()=>{
 const options={question:'Where is my shipment?',guardrail:'builtin-privacy',memory_enabled:false};
 const body=supportMessage(conversation,options.question,options,{requestId:'rpc-1',messageId:'message-1'});
 assert.deepEqual(body,{jsonrpc:'2.0',id:'rpc-1',method:'SendMessage',params:{message:{messageId:'message-1',role:'ROLE_USER',contextId:'context-owned',parts:[{text:options.question}]},metadata:{conversation_id:'chat-owned',question_options:options}}});
 assert.equal('taskId' in body.params.message,false,'a completed task must never be resumed for a follow-up');
 assert.throws(()=>supportMessage({id:'old-api-conversation'},'Question',{},{}),/no A2A context/);
});

test('follow-ups create distinct messages on one context and never reuse completed task IDs',()=>{
 const first=supportMessage(conversation,'First question',{}, {requestId:'first',messageId:'message-first'});
 const followup=supportMessage(conversation,'Why?',{}, {requestId:'followup',messageId:'message-followup'});
 assert.equal(first.params.message.contextId,followup.params.message.contextId);
 assert.notEqual(first.params.message.messageId,followup.params.message.messageId);
 assert.notEqual(first.id,followup.id);
 assert.equal(followup.params.message.taskId,undefined);
});

test('completed and failed tasks retain exact run references; no success guessed from text',()=>{
 assert.deepEqual(supportTask(envelope,'rpc-1','context-owned'),task);
 const failed={...task,status:{state:'TASK_STATE_FAILED'}};
 assert.deepEqual(supportTask({...envelope,result:{task:failed}},'rpc-1','context-owned'),failed);
 for(const state of ['TASK_STATE_WORKING','TASK_STATE_INPUT_REQUIRED',undefined])assert.throws(()=>supportTask({...envelope,result:{task:{...task,status:{state}}}},'rpc-1','context-owned'),/did not finish/);
 assert.throws(()=>supportTask({...envelope,result:{task:{...task,metadata:{}}}},'rpc-1','context-owned'),/no marketplace run/);
});

test('invalid envelopes, cross-context responses and protocol errors are honest failures',()=>{
 assert.throws(()=>supportTask({...envelope,id:'other-request'},'rpc-1','context-owned'),/invalid response/);
 assert.throws(()=>supportTask({...envelope,result:{task:{...task,contextId:'other-context'}}},'rpc-1','context-owned'),/did not match/);
 assert.throws(()=>supportTask({jsonrpc:'2.0',id:'rpc-1',error:{code:-32001,message:'Context unavailable'}},'rpc-1','context-owned'),/Context unavailable/);
 assert.throws(()=>supportTask({jsonrpc:'2.0',id:'rpc-1',error:{code:-32603,message:'Internal driver or connection details'}},'rpc-1','context-owned'),e=>e.message.includes('Check service readiness')&&!e.message.includes('driver'));
 assert.throws(()=>supportTask({...envelope,result:{message:{parts:[{text:'All done'}]}}},'rpc-1','context-owned'),/did not match/);
});

test('a failed task before model execution shows the server explanation without claiming a saved run',()=>{
 const failed={...task,status:{state:'TASK_STATE_FAILED'},metadata:{conversation_id:'chat-owned'},artifacts:[{parts:[{text:'This conversation already has a running question'}]}]};
 assert.throws(()=>supportTask({...envelope,result:{task:failed}},'rpc-1','context-owned'),/already has a running question/);
 assert.throws(()=>supportTask({...envelope,result:{task:{...failed,artifacts:[]}}},'rpc-1','context-owned'),/failed before a marketplace run/);
});

test('browser posts A2A to same-origin endpoint through existing session/CSRF request helper',async()=>{
 const calls=[];const api=async(...args)=>{calls.push(args);return envelope;};
 assert.deepEqual(await askA2ASupport(api,conversation,'Where is it?',{guardrail:'off'},{requestId:'rpc-1',messageId:'message-1'}),task);
 assert.equal(calls.length,1);assert.equal(calls[0][0],'/a2a/support');assert.equal(calls[0][1].method,'SendMessage');
});

test('actual request helper sends A2A JSON-RPC and CSRF to the same-origin route',async()=>{
 const original=global.fetch;let resets=0;
 global.fetch=async(url,options)=>{
  assert.equal(url,'/api/a2a/support');assert.equal(options.method,'POST');
  assert.equal(options.headers['X-CSRF-Token'],'owned-session-csrf');
  assert.equal(options.headers['Content-Type'],'application/json');
  assert.equal(options.headers['A2A-Version'],'1.0');
  const sent=JSON.parse(options.body);assert.equal(sent.method,'SendMessage');assert.equal(sent.params.message.contextId,'context-owned');
  return new Response(JSON.stringify(envelope));
 };
 try{const api=(path,body)=>request(path,body,undefined,'owned-session-csrf',()=>resets++);assert.equal((await askA2ASupport(api,conversation,'Why?',{},{requestId:'rpc-1',messageId:'message-1'})).id,'task-new');assert.equal(resets,0);}
 finally{global.fetch=original;}
});

test('Agent Card shows actual v1 interfaces and preserves false capability declarations',()=>{
 const card={protocolVersion:'1.0',supportedInterfaces:[{url:'http://localhost:8000/api/a2a/support',protocolBinding:'JSONRPC',protocolVersion:'1.0'}],capabilities:{streaming:false,pushNotifications:false}};
 assert.deepEqual(cardInterfaces(card),[{url:'http://localhost:8000/api/a2a/support',transport:'JSONRPC',version:'1.0'}]);
 assert.deepEqual(safeCard(card).capabilities,{streaming:false,pushNotifications:false});
 assert.deepEqual(cardInterfaces(null),[]);
});

test('displayed raw card cannot expose accidental credentials and input is not mutated',()=>{
 const original={name:'Support',securitySchemes:{session:{apiKeySecurityScheme:{in:'cookie',name:'marketplace_session'}}},clientSecret:'secret-value',nested:{access_token:'private-token'},url:'https://name:password@example.com/a2a?token=private&version=1'};
 const safe=safeCard(original);
 assert.equal(safe.clientSecret,'[redacted]');assert.equal(safe.nested.access_token,'[redacted]');
 assert.equal(safe.securitySchemes.session.apiKeySecurityScheme.name,'marketplace_session');
 assert.equal(safe.url,'https://example.com/a2a?token=%5Bredacted%5D&version=1');
 assert.equal(original.clientSecret,'secret-value');
});

test('dispatch enrollment and support transport are independent choices',()=>{
 assert.deepEqual(dispatchData('ship-1','a2a','exception'),{id:'ship-1',delivery_mode:'a2a',delivery_fixture:'exception'});
 assert.deepEqual(dispatchData('ship-1','local','exception'),{id:'ship-1',delivery_mode:'local'});
 assert.deepEqual(dispatchData('ship-1'),{id:'ship-1',delivery_mode:'local'});
 assert.equal(isA2AMode('a2a_delivery'),true);assert.equal(isA2AMode('standard'),false);
 assert.equal(supportModeLabel('a2a_delivery'),'A2A Support + Delivery');
});

test('existing delivery associations route the manual control regardless of new-dispatch defaults',()=>{
 assert.deepEqual(shipmentDeliveryAction({status:'pending'}),{action:'dispatch',label:'Dispatch'});
 assert.deepEqual(shipmentDeliveryAction({status:'dispatched',delivery_service:{reference:'delivery-1'}}),{action:'deliver',label:'Simulate delivery'});
 assert.deepEqual(shipmentDeliveryAction({status:'dispatched'}),{action:'deliver',label:'Mark delivered'});
 assert.equal(shipmentDeliveryAction({status:'delivered',delivery_service:{reference:'delivery-1'}}),null);
 assert.equal(shipmentDeliveryAction(undefined),null);
 assert.equal(shipmentDeliveryAction({status:'unknown'}),null);
});

test('post-dispatch scenario control is limited to linked dispatched shipments and seller/operator roles',()=>{
 const shipment={id:'ship-linked',status:'dispatched',delivery_service:{reference:'delivery-1',fixture:'normal'}};
 for(const role of ['seller','operator'])for(const fixture of ['normal','exception'])assert.deepEqual(shipmentFixtureChange(shipment,role,fixture),{action:'delivery_fixture',data:{id:'ship-linked',delivery_fixture:fixture}});
 for(const role of ['support','buyer',undefined])assert.equal(shipmentFixtureChange(shipment,role,'exception'),null);
 for(const status of ['pending','delivered',undefined])assert.equal(shipmentFixtureChange({...shipment,status},'seller','exception'),null);
 assert.equal(shipmentFixtureChange({...shipment,delivery_service:null},'seller','exception'),null);
 assert.equal(shipmentFixtureChange(shipment,'seller','unexpected'),null);
});
