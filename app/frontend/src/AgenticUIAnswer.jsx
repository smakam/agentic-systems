import React,{useState,useEffect,useMemo,useRef} from 'react';
import A2UIAnswer from './A2UIAnswer.jsx';
import ControlledAnswer from './ControlledAnswer.jsx';
import {isolatedHtml,generatedHistoryAction,modeDescriptions} from './agentic-ui.js';
import DOMPurify from 'dompurify';
import MCPAppHost from './MCPAppHost.jsx';

function GeneratedView({ui,onAction,disabled}){
 const [busy,setBusy]=useState(false),frame=useRef(null),sending=useRef(false),callback=useRef(onAction);callback.current=onAction;
 const documentHtml=useMemo(()=>{
  const markup=DOMPurify.sanitize(ui.html,{WHOLE_DOCUMENT:true,ADD_TAGS:['style'],ALLOW_DATA_ATTR:false,ADD_ATTR:['data-history-action'],FORBID_ATTR:['nonce','formaction','form','autofocus'],FORBID_TAGS:['a','form','input','meta','link','base','iframe','object','embed','script','svg','math']});
  const bytes=crypto.getRandomValues(new Uint8Array(16)),nonce=Array.from(bytes,x=>x.toString(16).padStart(2,'0')).join('');
  return isolatedHtml(markup,{nonce,actionIds:Object.keys(ui.actions||{}),targetOrigin:window.location.origin});
 },[ui]);
 useEffect(()=>{
  async function receive(event){
   const action=generatedHistoryAction(ui,event,frame.current?.contentWindow);
   if(!action||disabled||sending.current)return;
   sending.current=true;setBusy(true);
   try{await callback.current?.(action);}finally{sending.current=false;setBusy(false)}
  }
  window.addEventListener('message',receive);return()=>window.removeEventListener('message',receive);
 },[ui,disabled]);
 useEffect(()=>{frame.current?.contentWindow?.postMessage({type:'marketplace-ui-status',disabled:Boolean(disabled||busy)},'*')},[disabled,busy]);
 return <><iframe ref={frame} className="agentic-generated-frame" title="Model-generated order interface" sandbox="allow-scripts" referrerPolicy="no-referrer" srcDoc={documentHtml} inert={disabled||busy||undefined} onLoad={()=>frame.current?.contentWindow?.postMessage({type:'marketplace-ui-status',disabled:Boolean(disabled||busy)},'*')}/>{busy&&<p role="status">Loading recorded history…</p>}<small>The model generates the button; the application handles its approved history action.</small></>;
}

export default function AgenticUIAnswer({run,api,ui:initial,onAction,disabled,children,...rest}){
 const [variants,setVariants]=useState(run.metrics?.agentic_ui_variants||{}),[selected,setSelected]=useState(null),[pending,setPending]=useState(false),[error,setError]=useState(''),[embedded,setEmbedded]=useState(false);
 const ui=selected?variants[selected]:initial;
 if(!initial)return children;
 const mode=ui?.generation_mode||'declarative';
 async function compare(next,force=false){
  setError('');setEmbedded(false);
  if(!force&&variants[next]){setSelected(next);return}
  if(!force&&next===(initial.generation_mode||'declarative')){setSelected(null);return}
  setPending(true);
  try{const value=await api(`/conversations/${run.conversation_id}/runs/${run.id}/presentation`,{mode:next});setVariants(v=>({...v,[next]:value}));setSelected(next)}catch(e){setError(e.message)}finally{setPending(false)}
 }
 return <section className="agentic-comparison" aria-label="Agentic UI comparison">
  <div className="agentic-mode-tabs" role="group" aria-label="Compare generation patterns">{Object.keys(modeDescriptions).map(m=><button key={m} aria-pressed={mode===m} disabled={pending||disabled} onClick={()=>compare(m)}>{m==='open-ended'?'Open-ended':m[0].toUpperCase()+m.slice(1)}</button>)}</div>
  <p>{modeDescriptions[mode]}</p><div className="agentic-decision"><strong>Model output: </strong>{mode==='controlled'?<code>{ui.model_output}</code>:mode==='declarative'?<span>{ui.messages?.[0]?.createSurface?.components?.map(c=>c.component).join(' → ')||'No composition available'}</span>:<span>{ui.html?.length||0} characters of HTML/CSS; no registered marketplace widgets</span>}</div><small>Same completed investigation and source evidence. Switching patterns adds only a presentation call.</small>
  {(ui.status!=='completed'||mode==='open-ended'||mode==='controlled'&&!ui.selection)&&<button disabled={pending||disabled} onClick={()=>compare(mode,true)}>{ui.status==='completed'?'Regenerate view':'Retry presentation'}</button>}
  {pending&&<p role="status">Generating the alternative presentation…</p>}{error&&<p role="alert">{error}</p>}
  <div className="agentic-display-tabs" role="group" aria-label="Display destination"><strong>Display:</strong><button aria-pressed={!embedded} disabled={pending||disabled} onClick={()=>setEmbedded(false)}>Direct in marketplace</button><button aria-pressed={embedded} disabled={pending||disabled||mode!=='declarative'||ui.status!=='completed'} onClick={()=>setEmbedded(true)}>MCP Apps</button>{mode!=='declarative'&&<small>This demo embeds the declarative A2UI view. Select Declarative to use MCP Apps.</small>}</div>
  {!embedded&&<details className="agentic-render-inspector"><summary>Inspect delivery and rendering</summary><p>Custom HTTP API → {mode==='controlled'?'view selection and data → prebuilt React view in this page':mode==='open-ended'?'sanitized HTML/CSS → iframe with an application-owned action bridge':'A2UI message processor → registered React widgets in this page'}. History actions use the owned conversation's support API.</p><pre>{JSON.stringify({generationMode:mode,sourceInvestigation:run.id,evidenceHandles:Object.keys(run.evidence||{}),rendering:mode==='controlled'?'application-prebuilt':mode==='open-ended'?'generated-markup iframe':'A2UI client widget registry',modelOutputKind:mode==='controlled'?'prebuilt view selection':mode==='declarative'?'component composition':'HTML/CSS'},null,2)}</pre></details>}
  {embedded?<MCPAppHost api={api} conversationId={run.conversation_id} runId={run.id}/>:mode==='open-ended'?<>
   <p className="agentic-code-notice">Generated code: compare displayed facts with the retained answer and sources.</p>
   {ui.status==='completed'?<GeneratedView ui={ui} onAction={action=>onAction?.({...action,generationMode:mode})} disabled={disabled}/>:<p role="status">{ui.message}</p>}
   <details><summary>Text answer and sources</summary>{children}</details>
   {ui.trace_id&&<p>Presentation trace: <code>{ui.trace_id}</code>. Find this trace in Langfuse.</p>}
   <details><summary>Inspect generated UI code</summary><pre>{ui.model_output}</pre></details>
   <details><summary>Presentation instructions</summary><pre>{ui.instructions}</pre></details>
  </>:mode==='controlled'?<ControlledAnswer ui={ui} disabled={disabled||pending} onAction={action=>onAction?.({...action,generationMode:mode})}>{children}</ControlledAnswer>:<A2UIAnswer {...rest} ui={ui} disabled={disabled||pending} onAction={action=>onAction?.({...action,generationMode:mode})}>{children}</A2UIAnswer>}
  {ui.requests&&<small>{mode} presentation · {ui.requests} call · {ui.elapsed_seconds}s · {ui.input_tokens} input / {ui.output_tokens} output tokens</small>}
 </section>;
}
