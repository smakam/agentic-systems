import React,{useRef,useState} from 'react';
import {OrderSummary,RecordTable,EventTimeline} from './MarketplaceViews.jsx';
import {controlledHistoryAction} from './agentic-ui.js';

const views={summary:OrderSummary,table:RecordTable,timeline:EventTimeline};

export default function ControlledAnswer({ui,onAction,disabled,children}){
 const [busy,setBusy]=useState(false),sending=useRef(false);
 const current=ui.renderer==='application-prebuilt'&&ui.selection;
 const View=current&&views[ui.selection.view];
 async function activate(id){
  const action=controlledHistoryAction(ui,id);
  if(!action||disabled||sending.current)return;
  sending.current=true;setBusy(true);
  try{await onAction?.(action);}finally{sending.current=false;setBusy(false)}
 }
 return <>
  <section className="a2ui-answer" aria-label="Controlled prebuilt answer" aria-busy={busy||undefined}>
   <p className="eyebrow">MODEL-SELECTED PREBUILT VIEW</p>
   {ui.status!=='completed'?<p role="status">{ui.message||'The selected view is unavailable. Use the text answer below.'}</p>:!current?<p role="status">This saved presentation uses the older renderer. Regenerate the view to use direct rendering.</p>:<>
    {View?<View {...(ui.selection.view==='summary'?{record:ui.data}:{dataset:ui.data})}/>:<p>The model selected the text answer below.</p>}
    {Object.entries(ui.actions||{}).map(([id,action])=><button key={id} disabled={disabled||busy} onClick={()=>activate(id)}>{busy?'Loading order history…':action.label}</button>)}
   </>}
  </section>
  {busy&&<p role="status">Loading order history and preparing the selected view…</p>}
  <details open={ui.status!=='completed'||ui.selection?.view==='answer'}><summary>Text answer and sources</summary>{children}</details>
  <details className="a2ui-inspector"><summary>Inspect UI composition</summary>
   <p>Available prebuilt views: {ui.components?.join(', ')}. The model selects a view and data reference; application code owns its layout and history control.</p>
   {ui.trace_id&&<p>Presentation trace: <code>{ui.trace_id}</code>. Find this trace in Langfuse; it is separate from the business investigation.</p>}
   <details><summary>Presentation instructions</summary><pre>{ui.instructions}</pre></details>
   <details><summary>Model view selection</summary><pre>{ui.model_output}</pre></details>
   {current&&<details><summary>Prebuilt view data received by the application</summary><p>The backend resolves the selected data reference. The frontend already contains the view code; no A2UI messages or model-generated layout are used.</p><pre>{JSON.stringify({selection:ui.selection,data:ui.data,actions:ui.actions},null,2)}</pre></details>}
  </details>
 </>;
}
