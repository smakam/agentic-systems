import {test} from 'node:test';
import assert from 'node:assert/strict';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {InMemoryTransport} from '@modelcontextprotocol/sdk/inMemory.js';
import {createPresentationServer,resourceUri} from './mcp-app-server.mjs';
import {readFile} from 'node:fs/promises';

const messages=JSON.parse(await readFile('../backend/tests/fixtures/a2ui-answer.json','utf8'));
const ui={status:'completed',generation_mode:'declarative',messages};
const run={id:'run-1',status:'completed',answer:'Order is dispatched.',metrics:{a2ui:ui}};
test('MCP discovery, resource fetch, owned run, and history are separate protocol calls',async()=>{
 const calls=[];
 const server=createPresentationServer({api:async(path,body)=>{calls.push({path,body});return body?{...run,id:'history'}:[run]},html:async()=>'<html>Renderer bundle</html>'});
 const [a,b]=InMemoryTransport.createLinkedPair();
 const client=new Client({name:'test-host',version:'1'});
 await server.connect(a);await client.connect(b);
 try{
  const {tools}=await client.listTools();
  assert.equal(tools.find(t=>t.name==='show_order_view')._meta.ui.resourceUri,resourceUri);
  const resource=await client.readResource({uri:resourceUri});
  assert.equal(resource.contents[0].mimeType,'text/html;profile=mcp-app');
  assert.equal(calls.length,0);
  const result=await client.callTool({name:'show_order_view',arguments:{conversationId:'c1',runId:'run-1'}});
  assert.equal(result.structuredContent.ui.generation_mode,'declarative');
  const bad=await client.callTool({name:'show_order_history',arguments:{conversationId:'c1',runId:'run-1',actionId:'a7'}});
  assert.equal(bad.isError,true);
  assert.equal(calls.filter(c=>c.body).length,0);
  const history=await client.callTool({name:'show_order_history',arguments:{conversationId:'c1',runId:'run-1',actionId:'a0'}});
  assert.equal(history.structuredContent.runId,'history');
  assert.equal(calls.find(c=>c.body).body.a2ui_action.run_id,'run-1');
  const missing=await client.callTool({name:'show_order_view',arguments:{conversationId:'c1',runId:'other'}});
  assert.equal(missing.isError,true);
 }finally{await client.close();await server.close()}
});
