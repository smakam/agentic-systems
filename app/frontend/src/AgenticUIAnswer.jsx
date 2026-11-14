import React,{useState} from 'react';
import A2UIAnswer from './A2UIAnswer.jsx';
import {isolatedHtml,modeDescriptions} from './agentic-ui.js';
import DOMPurify from 'dompurify';
import MCPAppHost from './MCPAppHost.jsx';

function GeneratedView({ui,onAction,disabled}){
 const [busy,setBusy]=useState(false);
 const markup=DOMPurify.sanitize(ui.html,{WHOLE_DOCUMENT:true,ADD_TAGS:['style'],FORBID_TAGS:['a','form','input','button','meta','link','base','iframe','object','embed','script','svg','math']});
 async function history(id,action){
  if(busy||disabled)return;setBusy(true);
  try{await onAction?.({actionId:id,orderId:action.order_id,question:`Show the recorded event history for order ${action.order_id}.`})}finally{setBusy(false)}
 }
 return <><iframe className="agentic-generated-frame" title="Model-generated order interface" sandbox="" referrerPolicy="no-referrer" srcDoc={isolatedHtml(markup)}/>{Object.entries(ui.actions||{}).map(([id,action])=><button key={id} disabled={disabled||busy} onClick={()=>history(id,action)}>{busy?'Loading recorded history…':action.label}</button>)}<small>History navigation is supplied by the application, outside the generated document.</small></>;
}

export default function AgenticUIAnswer({run,api,ui:initial,onAction,disabled,children,...rest}){
 const [variants,setVariants]=useState(run.metrics?.agentic_ui_variants||{}),[selected,setSelected]=useState(null),[pending,setPending]=useState(false),[error,setError]=useState(''),[embedded,setEmbedded]=useState(false);
 const ui=selected?variants[selected]:initial;
 if(!initial)return children;
 const mode=ui?.generation_mode||'declarative';
 async function compare(next,force=false){
  setError('');setEmbedded(false);
  if(!force&&next===(initial.generation_mode||'declarative')){setSelected(null);return}
  if(!force&&variants[next]){setSelected(next);return}
  setPending(true);
  try{const value=await api(`/conversations/${run.conversation_id}/runs/${run.id}/presentation`,{mode:next});setVariants(v=>({...v,[next]:value}));setSelected(next)}catch(e){setError(e.message)}finally{setPending(false)}
 }
 return <section className="agentic-comparison" aria-label="Agentic UI comparison">
  <div className="agentic-mode-tabs" role="group" aria-label="Compare generation patterns">{Object.keys(modeDescriptions).map(m=><button key={m} aria-pressed={mode===m} disabled={pending||disabled} onClick={()=>compare(m)}>{m==='open-ended'?'Open-ended':m[0].toUpperCase()+m.slice(1)}</button>)}</div>
  <p>{modeDescriptions[mode]}</p><div className="agentic-decision"><strong>Model output: </strong>{mode==='controlled'?<code>{ui.model_output}</code>:mode==='declarative'?<span>{ui.messages?.[0]?.createSurface?.components?.map(c=>c.component).join(' → ')||'No composition available'}</span>:<span>{ui.html?.length||0} characters of HTML/CSS; no registered marketplace widgets</span>}</div><small>Same completed investigation and source evidence. Switching patterns adds only a presentation call.</small>
  {ui.status!=='completed'&&<button disabled={pending||disabled} onClick={()=>compare(mode,true)}>Retry presentation</button>}
  {pending&&<p role="status">Generating the alternative presentation…</p>}{error&&<p role="alert">{error}</p>}
  <div className="agentic-display-tabs" role="group" aria-label="Display destination"><strong>Display:</strong><button aria-pressed={!embedded} disabled={pending||disabled} onClick={()=>setEmbedded(false)}>Direct in marketplace</button><button aria-pressed={embedded} disabled={pending||disabled||mode!=='declarative'||ui.status!=='completed'} onClick={()=>setEmbedded(true)}>MCP Apps</button>{mode!=='declarative'&&<small>This demo embeds the declarative A2UI view. Select Declarative to use MCP Apps.</small>}</div>
  {!embedded&&<details className="agentic-render-inspector"><summary>Inspect delivery and rendering</summary><p>Custom HTTP API → {mode==='open-ended'?'sanitized HTML/CSS → script-disabled iframe':'A2UI message processor → registered React widgets in this page'}. History actions use the owned conversation's support API.</p><pre>{JSON.stringify({generationMode:mode,sourceInvestigation:run.id,evidenceHandles:Object.keys(run.evidence||{}),rendering:mode==='open-ended'?'generated-markup sandbox':'client widget registry',modelOutputKind:mode==='controlled'?'prebuilt view selection':mode==='declarative'?'component composition':'HTML/CSS'},null,2)}</pre></details>}
  {embedded?<MCPAppHost api={api} conversationId={run.conversation_id} runId={run.id}/>:mode==='open-ended'?<>
   <p className="agentic-code-notice">Generated code: compare displayed facts with the retained answer and sources.</p>
   {ui.status==='completed'?<GeneratedView ui={ui} onAction={action=>onAction?.({...action,generationMode:mode})} disabled={disabled}/>:<p role="status">{ui.message}</p>}
   <details><summary>Text answer and sources</summary>{children}</details>
   {ui.trace_id&&<p>Presentation trace: <code>{ui.trace_id}</code>. Find this trace in Langfuse.</p>}
   <details><summary>Inspect generated UI code</summary><pre>{ui.model_output}</pre></details>
   <details><summary>Presentation instructions</summary><pre>{ui.instructions}</pre></details>
  </>:<A2UIAnswer {...rest} ui={ui} disabled={disabled||pending} onAction={action=>onAction?.({...action,generationMode:mode})}>{children}</A2UIAnswer>}
  {ui.requests&&<small>{mode} presentation · {ui.requests} call · {ui.elapsed_seconds}s · {ui.input_tokens} input / {ui.output_tokens} output tokens</small>}
 </section>;
}
