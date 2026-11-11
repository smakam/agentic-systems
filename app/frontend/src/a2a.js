export const supportModes=[
 {id:'standard',label:'Standard API'},
 {id:'a2a_support',label:'Marketplace A2A'},
 {id:'a2a_delivery',label:'Multi-agent A2A'},
];

export function isA2AMode(mode){return mode==='a2a_support'||mode==='a2a_delivery';}
export function supportModeLabel(mode){return supportModes.find(m=>m.id===mode)?.label||'Standard API';}

export function supportMessage(conversation,question,questionOptions,{requestId,messageId}){
 if(!conversation?.id||!conversation?.a2a_context_id)throw new Error('This conversation has no A2A context. Start a new A2A conversation.');
 return {jsonrpc:'2.0',id:requestId,method:'SendMessage',params:{
  message:{messageId,role:'ROLE_USER',contextId:conversation.a2a_context_id,parts:[{text:question}]},
  metadata:{conversation_id:conversation.id,question_options:questionOptions},
 }};
}

export function supportTask(reply,requestId,contextId){
 if(reply?.jsonrpc!=='2.0'||reply.id!==requestId)throw new Error('The A2A server returned an invalid response.');
 if(reply.error)throw new Error(reply.error.code===-32603?'The A2A service could not complete this request. Check service readiness and retry.':reply.error.message||'The A2A request failed.');
 const task=reply.result?.task;
 if(!task?.id||task.contextId!==contextId)throw new Error('The A2A task did not match this conversation.');
 if(!['TASK_STATE_COMPLETED','TASK_STATE_FAILED'].includes(task.status?.state))throw new Error('The A2A task did not finish. This interface supports completed or failed question tasks only.');
 if(!task.metadata?.run_id){
  if(task.status.state==='TASK_STATE_FAILED'){
   const explanation=(task.artifacts||[]).flatMap(a=>a.parts||[]).map(p=>p.text||'').filter(Boolean).join('\n');
   throw new Error(explanation||'The A2A investigation failed before a marketplace run could be recorded.');
  }
  throw new Error('The A2A task returned no marketplace run reference.');
 }
 return task;
}

export async function askA2ASupport(api,conversation,question,questionOptions,ids){
 const body=supportMessage(conversation,question,questionOptions,ids);
 return supportTask(await api('/a2a/support',body),body.id,conversation.a2a_context_id);
}

// Agent Cards describe authentication mechanisms, never the browser's credentials.
// Redact accidental secrets before displaying even a server-provided raw card.
export function safeCard(value){
 if(Array.isArray(value))return value.map(safeCard);
 if(value&&typeof value==='object')return Object.fromEntries(Object.entries(value).map(([key,item])=>[
  key,/^(authorization|password|secret|client[_-]?secret|api[_-]?key|access[_-]?token|refresh[_-]?token|cookie)$/i.test(key)?'[redacted]':safeCard(item),
 ]));
 if(typeof value==='string'&&/^https?:\/\//i.test(value)){
  try{const u=new URL(value);if(u.username||u.password){u.username='';u.password='';}for(const name of [...u.searchParams.keys()])if(/token|secret|password|api[_-]?key|authorization/i.test(name))u.searchParams.set(name,'[redacted]');return u.toString();}catch{return value;}
 }
 return value;
}

export function cardInterfaces(card){
 const interfaces=card?.supportedInterfaces||card?.additionalInterfaces||[];
 const result=interfaces.map(i=>({url:i.url||i.endpoint||'Address not supplied',transport:i.protocolBinding||i.transport||'Binding not supplied',version:i.protocolVersion||card.protocolVersion}));
 if(card?.url&&!result.some(i=>i.url===card.url))result.unshift({url:card.url,transport:card.preferredTransport||'Binding not supplied',version:card.protocolVersion});
 return result;
}

export function dispatchData(shipmentId,mode='local',fixture='normal'){
 return {id:shipmentId,delivery_mode:mode==='a2a'?'a2a':'local',...(mode==='a2a'?{delivery_fixture:fixture==='exception'?'exception':'normal'}:{})};
}

export function shipmentDeliveryAction(shipment){
 if(!shipment||shipment.status==='delivered')return null;
 if(shipment.status==='pending')return {action:'dispatch',label:'Dispatch'};
 if(shipment.status==='dispatched')return {action:'deliver',label:shipment.delivery_service?'Simulate delivery':'Mark delivered'};
 return null;
}

export function shipmentFixtureChange(shipment,role,fixture){
 if(!['operator','seller'].includes(role)||shipment?.status!=='dispatched'||!shipment.delivery_service||!['normal','exception'].includes(fixture))return null;
 return {action:'delivery_fixture',data:{id:shipment.id,delivery_fixture:fixture}};
}
