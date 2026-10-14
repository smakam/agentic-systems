import test from 'node:test';
import assert from 'node:assert/strict';
import {request,memoryResourcePath,memoryEditBody,memoryJobLabel,keepPreviousMemoryJob} from './api.js';
for(const path of ['/market','/logout','/conversations'])test(`expired session on ${path} resets the UI`,async()=>{
 const original=global.fetch;let resets=0;global.fetch=async()=>new Response(JSON.stringify({detail:'Session expired'}),{status:401});
 try{await assert.rejects(request(path,undefined,undefined,'',()=>resets++),e=>e.status===401);assert.equal(resets,1)}finally{global.fetch=original}
});
for(const status of [401,403])test(`login failure ${status} does not reset login feedback`,async()=>{
 const original=global.fetch;let resets=0;global.fetch=async()=>new Response(JSON.stringify({detail:'Invalid credentials'}),{status});
 try{await assert.rejects(request('/login',{},undefined,'',()=>resets++),/Invalid credentials/);assert.equal(resets,0)}finally{global.fetch=original}
});
test('successful request preserves data and CSRF header',async()=>{
 const original=global.fetch;let resets=0;global.fetch=async(url,options)=>{assert.equal(options.headers['X-CSRF-Token'],'csrf-test');return new Response(JSON.stringify({ok:true}))};
 try{assert.deepEqual(await request('/market',undefined,undefined,'csrf-test',()=>resets++),{ok:true});assert.equal(resets,0)}finally{global.fetch=original}
});

test('remote memory mutations preserve provider and never invent optimistic versions',()=>{
 assert.equal(memoryResourcePath('remote/id','mem0',undefined),'/memories/remote%2Fid?provider=mem0');
 assert.equal(memoryResourcePath('remote/id','mem0',9),'/memories/remote%2Fid?provider=mem0');
 assert.deepEqual(memoryEditBody({title:'Preference',version:9},'New preference','mem0'),{title:'Preference',content:'New preference'});
});
test('internal memory mutations retain the existing optimistic concurrency contract',()=>{
 assert.equal(memoryResourcePath('local-id','internal',4),'/memories/local-id?provider=internal&expected_version=4');
 assert.deepEqual(memoryEditBody({title:'Preference',version:4},'New preference'),{title:'Preference',content:'New preference',expected_version:4});
});
test('memory save failures and queued work are distinguished from completion',()=>{
 assert.equal(memoryJobLabel('pending'),'Memory save queued');
 assert.equal(memoryJobLabel('failed'),'Memory save failed');
 assert.equal(memoryJobLabel('complete'),'Memory save complete');
 assert.equal(memoryJobLabel('noop'),'No new memories to save');
});

test('a new answer does not hide the previous conversation’s pending memory save',()=>{
 for(const status of ['queued','pending','processing'])assert.equal(keepPreviousMemoryJob('ended','new',status),true);
 for(const status of ['complete','failed','noop'])assert.equal(keepPreviousMemoryJob('ended','new',status),false);
 assert.equal(keepPreviousMemoryJob('same','same','processing'),false);
 assert.equal(keepPreviousMemoryJob('','new',undefined),false);
});
