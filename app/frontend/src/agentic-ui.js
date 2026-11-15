// Generated code gets no same-origin capability, credentials or network access.
export const mcpCsp="default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; img-src data:; font-src 'none'; connect-src 'none'; form-action 'none'; base-uri 'none'; frame-src 'none'; object-src 'none'";
export const generatedCsp=mcpCsp.replace("script-src 'unsafe-inline'", "script-src 'none'");
export function isolatedHtml(html,{nonce,actionIds=[],targetOrigin}={}){
 if(typeof html!=='string'||html.length>100000)throw new Error('Invalid generated document');
 let policy=generatedCsp,bridge='';
 if(nonce){
  if(!/^[a-f0-9]{32}$/.test(nonce)||actionIds.some(id=>!/^a[0-7]$/.test(id))||new URL(targetOrigin).origin!==targetOrigin)throw new Error('Invalid action bridge');
  policy=generatedCsp.replace("script-src 'none'",`script-src 'nonce-${nonce}'`);
  // Only this application-authored script runs. Model scripts/handlers are removed.
  bridge=`<script nonce="${nonce}">(()=>{const allowed=${JSON.stringify(actionIds)},origin=${JSON.stringify(targetOrigin)};function buttons(){return [...document.querySelectorAll('button[data-history-action]')].filter(b=>allowed.includes(b.dataset.historyAction))}document.addEventListener('click',e=>{const b=e.target.closest('button[data-history-action]');if(!b||b.disabled||!allowed.includes(b.dataset.historyAction))return;e.preventDefault();buttons().forEach(x=>x.disabled=true);parent.postMessage({type:'marketplace-history',actionId:b.dataset.historyAction},origin)});addEventListener('message',e=>{if(e.source===parent&&e.origin===origin&&e.data?.type==='marketplace-ui-status'&&typeof e.data.disabled==='boolean')buttons().forEach(b=>b.disabled=e.data.disabled)})})();<\/script>`;
 }
 return `<!doctype html><meta http-equiv="Content-Security-Policy" content="${policy}"><meta name="referrer" content="no-referrer">${html}${bridge}`;
}
export function generatedHistoryAction(ui,event,frameWindow){
 if(event.source!==frameWindow||event.data?.type!=='marketplace-history'||Object.keys(event.data).sort().join(',')!=='actionId,type')return null;
 const id=event.data.actionId,action=ui.actions?.[id];
 if(!/^a[0-7]$/.test(id)||action?.name!=='show_order_history'||!/^[-A-Za-z0-9_]{1,100}$/.test(action.order_id))return null;
 return {actionId:id,orderId:action.order_id,question:`Show the recorded event history for order ${action.order_id}.`};
}
export const modeDescriptions={
 controlled:'The model selects one prebuilt view and its data. The application fixes the arrangement.',
 declarative:'The model composes registered components and data references. The client draws the widgets.',
 'open-ended':'The model writes HTML and CSS without a widget catalog. Generated buttons use an approved history-action bridge; model scripts and network access are disabled.'
};
