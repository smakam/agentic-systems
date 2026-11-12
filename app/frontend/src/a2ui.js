export const displayCatalogId='urn:marketplace:a2ui:display:1';
export const displayComponents=['Column','Row','Card','Text','Divider','OrderSummary','EventTimeline','RecordTable','Button'];
const properties={Column:['children','align','justify'],Row:['children','align','justify'],Card:['child'],Text:['text','variant'],Divider:['axis'],OrderSummary:['record'],EventTimeline:['dataset'],RecordTable:['dataset'],Button:['child','action','variant']};
const own=(value,key)=>Object.prototype.hasOwnProperty.call(value,key);
const object=value=>value&&typeof value==='object'&&!Array.isArray(value);
const strings=value=>Array.isArray(value)&&value.every(x=>typeof x==='string');

// Retained answers cross a persistence boundary, so check them again before
// handing the payload to the official SDK's schema and tree validation.
export function displayMessages(value){
 if(!Array.isArray(value)||value.length!==1)throw new Error('Expected one display surface');
 const message=value[0],surface=message?.createSurface;
 if(message.version!=='1.0'||!object(surface)||surface.catalogId!==displayCatalogId)throw new Error('Unsupported display surface');
 if(Object.keys(message).some(k=>!['version','createSurface'].includes(k))||Object.keys(surface).some(k=>!['surfaceId','catalogId','components','root','dataModel'].includes(k)))throw new Error('Unsupported display operation');
 if(!Array.isArray(surface.components)||surface.components.length<1||surface.components.length>60)throw new Error('Display limit exceeded');
 const data=surface.dataModel;
 if(!object(data)||typeof data.answer!=='string'||!object(data.records)||!object(data.datasets)||!object(data.actions)||JSON.stringify(data).length>100000)throw new Error('Invalid display data');
 if(Object.keys(data.actions).length>8)throw new Error('Too many actions');
 for(const [id,action] of Object.entries(data.actions)){
  if(!/^a[0-7]$/.test(id)||!object(action)||action.name!=='show_order_history'||typeof action.label!=='string'||!/^[-A-Za-z0-9_]{1,100}$/.test(action.order_id))throw new Error('Invalid history action');
 }
 if(Object.keys(data.records).length>24||Object.keys(data.datasets).length>8)throw new Error('Too many records');
 for(const record of Object.values(data.records)){
  if(!object(record)||typeof record.title!=='string'||typeof record.source!=='string'||typeof record.scope!=='string'||typeof record.notice!=='string'||!Array.isArray(record.fields)||record.fields.length>20||record.fields.some(f=>!object(f)||typeof f.label!=='string'||typeof f.value!=='string'))throw new Error('Invalid record');
 }
 for(const dataset of Object.values(data.datasets)){
  if(!object(dataset)||typeof dataset.title!=='string'||typeof dataset.source!=='string'||typeof dataset.scope!=='string'||typeof dataset.notice!=='string'||typeof dataset.timeline!=='boolean'||!strings(dataset.headers)||dataset.headers.length>20||!Array.isArray(dataset.rows)||dataset.rows.length>12||dataset.rows.some(r=>!strings(r)||r.length!==dataset.headers.length))throw new Error('Invalid dataset');
 }
 let answer=false;
 for(const node of surface.components){
  if(!object(node)||!own(properties,node.component))throw new Error('Unsupported display component');
  if(Object.keys(node).some(k=>!['id','component',...properties[node.component]].includes(k)))throw new Error('Unsupported display property');
  if(['Column','Row'].includes(node.component)&&!strings(node.children))throw new Error('Explicit children required');
  if(node.component==='Button'){
   const action=node.action,event=action?.event;
   if(!object(action)||Object.keys(action).length!==1||!object(event)||Object.keys(event).sort().join(',')!=='context,name'||event.name!=='show_order_history'||!object(event.context)||Object.keys(event.context).join(',')!=='actionId'||!own(data.actions,event.context.actionId))throw new Error('Unknown history action');
  }
  if(['Text','OrderSummary','EventTimeline','RecordTable'].includes(node.component)){
   const prop=node.component==='Text'?'text':node.component==='OrderSummary'?'record':'dataset';
   const binding=node[prop];
   if(!object(binding)||Object.keys(binding).length!==1||typeof binding['@path']!=='string')throw new Error('Evidence binding required');
   const path=binding['@path'];
   if(node.component==='Text'){
    if(path!=='/answer'&&!Object.keys(data.actions).some(k=>path===`/actions/${k}/label`))throw new Error('Text must bind to the answer');
    answer=answer||path==='/answer';
   }else{
    const parts=path.split('/'),group=node.component==='OrderSummary'?'records':'datasets';
    if(parts.length!==3||parts[0]!==''||parts[1]!==group||!own(data[group],parts[2]))throw new Error('Unknown evidence');
    if(node.component==='EventTimeline'&&!data.datasets[parts[2]].timeline)throw new Error('Timeline requires events');
   }
  }
 }
 if(!answer)throw new Error('Complete answer required');
 return value;
}

export function historyAction(messages,event){
 displayMessages(messages);
 const actions=messages[0].createSurface.dataModel.actions;
 if(event?.name!=='show_order_history'||!own(actions,event.context?.actionId))throw new Error('Unknown history action');
 const actionId=event.context.actionId,orderId=actions[actionId].order_id;
 return {actionId,orderId,question:`Show the recorded event history for order ${orderId}.`};
}
