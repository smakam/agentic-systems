import React,{useState} from 'react';
import {createRoot} from 'react-dom/client';
import {App} from '@modelcontextprotocol/ext-apps';
import A2UIAnswer from './A2UIAnswer.jsx';
import styles from './style.css?inline';
const sheet=document.createElement('style');sheet.textContent=styles.replace(/@import[^;]+;/g,'');document.head.appendChild(sheet);

const app=new App({name:'Marketplace A2UI view',version:'1.0.0'});
let receive=()=>{};
app.ontoolresult=result=>receive(result);
function View(){
 const [data,setData]=useState(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 receive=result=>{
  if(result.isError){setError('The tool could not complete. Return to the support conversation.');return}
  setData(result.structuredContent);setError('');
 };
 async function history(action){
  if(busy)return;
  setBusy(true);setError('');
  try{receive(await app.callServerTool({name:'show_order_history',arguments:{conversationId:data.conversationId,runId:data.runId,actionId:action.actionId}},{timeout:240000}))}catch{setError('History request failed. Use the support conversation.')}finally{setBusy(false)}
 }
 return <main style={{padding:'12px',maxWidth:'100%'}}>{error&&<p role="alert">{error}</p>}{data?<A2UIAnswer ui={data.ui} onAction={history} disabled={busy}><p style={{whiteSpace:'pre-wrap'}}>{data.ui.messages?.[0]?.createSurface?.dataModel?.answer}</p></A2UIAnswer>:<p role="status">Waiting for tool results from the host…</p>}</main>;
}
createRoot(document.getElementById('root')).render(<View/>);
app.connect().catch(()=>receive({isError:true}));
