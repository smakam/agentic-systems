import React,{useEffect,useRef,useState} from 'react';
import {Client} from '@modelcontextprotocol/sdk/client/index.js';
import {StreamableHTTPClientTransport} from '@modelcontextprotocol/sdk/client/streamableHttp.js';
import {AppBridge,PostMessageTransport} from '@modelcontextprotocol/ext-apps/app-bridge';
import {mcpCsp} from './agentic-ui.js';

export default function MCPAppHost({api,conversationId,runId}){
 const frame=useRef(null),[error,setError]=useState(''),[events,setEvents]=useState([]),[evidence,setEvidence]=useState({});
 useEffect(()=>{
  let disposed=false,client,bridge,transport;
  const log=text=>{if(!disposed)setEvents(e=>[...e.slice(-11),text])};
  async function start(){
   const session=await api('/me');
   if(disposed)return;
   client=new Client({name:'Marketplace teaching host',version:'1.0.0'},{capabilities:{extensions:{'io.modelcontextprotocol/ui':{mimeTypes:['text/html;profile=mcp-app']}}}});
   transport=new StreamableHTTPClientTransport(new URL('/mcp-ui',window.location.origin),{requestInit:{headers:{'X-CSRF-Token':session.csrf},credentials:'same-origin'}});
   await client.connect(transport);log('MCP initialized');
   const {tools}=await client.listTools();
   const tool=tools.find(t=>t.name==='show_order_view'),uri=tool?._meta?.ui?.resourceUri;
   if(!uri)throw new Error('Tool did not declare a UI resource');
   log('tools/list → declared UI resource');
   if(!disposed)setEvidence(e=>({...e,tool:{name:tool.name,metadata:tool._meta}}));
   const resource=await client.readResource({uri});
   const html=resource.contents.find(c=>c.mimeType==='text/html;profile=mcp-app')?.text;
   if(typeof html!=='string')throw new Error('UI resource unavailable');
   log('resources/read → bundled HTML and A2UI renderer');
   if(!disposed)setEvidence(e=>({...e,resource:{uri,mimeType:'text/html;profile=mcp-app',characters:html.length}}));
   if(disposed)return;
   bridge=new AppBridge(null,{name:'Marketplace teaching host',version:'1.0.0'},{serverTools:{}});
   bridge.oncalltool=async params=>{
    if(params.name!=='show_order_history'||params.arguments?.conversationId!==conversationId)throw new Error('Tool call outside this view is not permitted');
    log('iframe → host → MCP tools/call: recorded history');
    if(!disposed)setEvidence(e=>({...e,lastToolCall:{name:params.name,arguments:params.arguments}}));
    const result=await client.callTool(params,undefined,{timeout:240000});
    log('MCP result → iframe');return result;
   };
   bridge.oninitialized=async()=>{
    try{
     log('Embedded view initialized');
     const args={conversationId,runId};
     await bridge.sendToolInput({arguments:args});log('Host → iframe: tool inputs');
     const result=await client.callTool({name:'show_order_view',arguments:args});
     if(!disposed)setEvidence(e=>({...e,result:{generationMode:result.structuredContent?.ui?.generation_mode,components:result.structuredContent?.ui?.messages?.[0]?.createSurface?.components?.map(c=>c.component)}}));
     await bridge.sendToolResult(result);log('tools/call → host → iframe: A2UI data');
    }catch(e){if(!disposed)setError(e.message)}
   };
   await bridge.connect(new PostMessageTransport(frame.current.contentWindow,frame.current.contentWindow));
   if(disposed)return;
   bridge.setHostContext({theme:'light',displayMode:'inline'});
   frame.current.srcdoc=`<!doctype html><meta http-equiv="Content-Security-Policy" content="${mcpCsp}"><meta name="referrer" content="no-referrer">${html}`;
  }
  start().catch(e=>{if(!disposed)setError(e.message)});
  return()=>{disposed=true;bridge?.close();client?.close();transport?.close()};
 },[api,conversationId,runId]);
 return <section className="mcp-teaching-host"><p className="eyebrow">MCP APPS · LOCAL TEACHING HOST</p><p>Same declarative view, fetched as an MCP UI resource and connected through the official Apps bridge.</p>{error&&<p role="alert">{error}</p>}<iframe ref={frame} sandbox="allow-scripts" title="MCP Apps order dashboard" referrerPolicy="no-referrer" className="agentic-generated-frame"/><details open><summary>Delivery and interaction events</summary><ol>{events.map((e,i)=><li key={i}>{e}</li>)}</ol></details><details><summary>Inspect MCP protocol evidence</summary><p>These fields come from the MCP tool definition, fetched resource, and actual tool result. In browser Network, filter for mcp-ui to see the JSON-RPC requests.</p><pre>{JSON.stringify(evidence,null,2)}</pre></details></section>;
}
