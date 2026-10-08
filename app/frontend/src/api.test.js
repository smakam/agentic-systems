import test from 'node:test';
import assert from 'node:assert/strict';
import {request} from './api.js';
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
