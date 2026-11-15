/** Local, authenticated MCP Apps server for the teaching host.
 * Uses the official MCP and MCP Apps SDKs. No model or session credential is
 * ever sent to the embedded document. Existing API ownership checks apply.
 */
import {readFile} from 'node:fs/promises';
import {McpServer} from '@modelcontextprotocol/sdk/server/mcp.js';
import {StreamableHTTPServerTransport} from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import {registerAppResource,registerAppTool,RESOURCE_MIME_TYPE} from '@modelcontextprotocol/ext-apps/server';
import {z} from 'zod';

export const resourceUri='ui://marketplace/order-view.html';
export function createPresentationServer({api,html}){
 const server=new McpServer({name:'Marketplace declarative UI',version:'1.0.0'});
 const ids={conversationId:z.string().min(1).max(100),runId:z.string().min(1).max(100)};
 async function findRun({conversationId,runId}){
  const runs=await api(`/conversations/${encodeURIComponent(conversationId)}/runs`);
  const run=runs.find(r=>r.id===runId);
  if(!run||run.status!=='completed')throw new Error('Completed owned investigation required');
  const ui=run.metrics?.agentic_ui_variants?.declarative||run.metrics?.a2ui;
  if(!ui||ui.status!=='completed'||(ui.generation_mode&&ui.generation_mode!=='declarative'))throw new Error('Generate a declarative view first');
  return {run,ui};
 }
 function result(run,ui,conversationId){return {content:[{type:'text',text:run.answer}],structuredContent:{ui,conversationId,runId:run.id}}}
 const common={annotations:{readOnlyHint:true,destructiveHint:false,openWorldHint:false},_meta:{ui:{resourceUri}}};
 registerAppTool(server,'show_order_view',{...common,description:'Show an owned, completed marketplace investigation as a declarative A2UI view.',inputSchema:ids},async args=>{
  const {run,ui}=await findRun(args);return result(run,ui,args.conversationId);
 });
 registerAppTool(server,'show_order_history',{...common,description:'Request recorded order history using an action offered by the source investigation.',inputSchema:{...ids,actionId:z.string().regex(/^a[0-7]$/)}},async args=>{
  const {ui}=await findRun(args);
  const action=ui.messages?.[0]?.createSurface?.dataModel?.actions?.[args.actionId];
  if(!action||action.name!=='show_order_history')throw new Error('Unknown history action');
  const run=await api(`/conversations/${encodeURIComponent(args.conversationId)}/ask`,{
   question:`Show the recorded event history for order ${action.order_id}.`,
   a2ui_enabled:true,agentic_ui_mode:'declarative',a2ui_action:{run_id:args.runId,action_id:args.actionId}
  });
  if(run.status!=='completed'||run.metrics?.a2ui?.status!=='completed')throw new Error('History view unavailable; inspect the support conversation');
  return result(run,run.metrics.a2ui,args.conversationId);
 });
 registerAppResource(server,'order-view',resourceUri,{mimeType:RESOURCE_MIME_TYPE},async()=>({contents:[{
  uri:resourceUri,mimeType:RESOURCE_MIME_TYPE,text:await html(),
  _meta:{ui:{prefersBorder:true,csp:{connectDomains:[],resourceDomains:[]}}}
 }]}));
 return server;
}

export function mcpMiddleware({backend=process.env.MARKETPLACE_API_PROXY||'http://127.0.0.1:58000',htmlPath=new URL('./dist-mcp/mcp-app.html',import.meta.url)}={}){
 return async(req,res,next)=>{
  if(req.url?.split('?')[0]!=='/mcp-ui'){next();return}
  res.setHeader('Cache-Control','no-store');
  // This demonstration is intentionally loopback-only and session scoped.
  const host=req.headers.host||'';
  if(!/^(localhost|127\.0\.0\.1):\d+$/.test(host)||req.headers.origin&&req.headers.origin!==`http://${host}`){res.writeHead(403).end('Loopback same-origin host required');return}
  if(req.method!=='POST'){res.writeHead(405).end();return}
  const headers={'Content-Type':'application/json',Cookie:req.headers.cookie||'','X-CSRF-Token':req.headers['x-csrf-token']||''};
  const api=async(path,body)=>{
   const r=await fetch(backend+'/api'+path,{method:body===undefined?'GET':'POST',headers,body:body===undefined?undefined:JSON.stringify(body)});
   if(!r.ok)throw new Error(`Marketplace request failed (${r.status})`);
   return r.json();
  };
  let server,transport;
  try{
   const me=await api('/me');
   if(!me.csrf||headers['X-CSRF-Token']!==me.csrf){res.writeHead(403).end('CSRF validation failed');return}
   if(!(await api('/a2ui-demo')).enabled){res.writeHead(403).end('Test preview required');return}
   let body='',size=0;
   for await(const chunk of req){size+=chunk.length;if(size>32000){res.writeHead(413).end();return}body+=chunk}
   const parsed=JSON.parse(body);
   server=createPresentationServer({api,html:()=>readFile(htmlPath,'utf8')});
   transport=new StreamableHTTPServerTransport({sessionIdGenerator:undefined,enableJsonResponse:true});
   await server.connect(transport);
   res.on('close',()=>{transport.close();server.close()});
   await transport.handleRequest(req,res,parsed);
  }catch{if(!res.headersSent)res.writeHead(400).end('MCP request unavailable; check sign-in, Test preview and UI bundle')}
 };
}
