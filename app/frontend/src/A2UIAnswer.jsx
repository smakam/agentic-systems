import React,{useMemo,useEffect,useRef} from 'react';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {A2uiSurface,MarkdownComponentContext} from '@a2ui/react';
import {MessageProcessor,injectBasicCatalogStyles} from '@a2ui/web_core/v1_0';
import {displayMessages,historyAction} from './a2ui.js';

injectBasicCatalogStyles();
import {formatEvidence} from './evidence.js';
import {marketplaceCatalog as catalog} from './A2UIMarketplace.jsx';
function ReadOnlyMarkdown({markdown,evidence,onEvidence}){
 return <Markdown remarkPlugins={[remarkGfm]} components={{a:({href,children})=>href?.startsWith('#evidence-')&&evidence?.[href.slice(1)]?<button className="citation" onClick={()=>onEvidence?.(evidence[href.slice(1)])}>{children}</button>:<span>{children}</span>,img:()=>null}}>{formatEvidence(markdown,evidence)}</Markdown>;
}

class DisplayBoundary extends React.Component{
 state={failed:false};
 static getDerivedStateFromError(){return {failed:true};}
 render(){return this.state.failed?<p role="status">The generated view could not be rendered. Use the text answer below.</p>:this.props.children;}
}

function Surface({messages,onAction,evidence,onEvidence}){
 const handler=useRef(onAction);handler.current=onAction;
 const MarkdownView=useMemo(()=>({markdown})=><ReadOnlyMarkdown markdown={markdown} evidence={evidence} onEvidence={onEvidence}/>,[evidence,onEvidence]);
 const result=useMemo(()=>{
  const processor=new MessageProcessor([catalog],event=>handler.current?.(historyAction(messages,event)));
  try{
   const errors=processor.processMessagesWithErrors(displayMessages(messages));
   if(errors.length)throw new Error('Invalid display');
   const surfaces=Array.from(processor.model.surfacesMap.values());
   if(surfaces.length!==1)throw new Error('Display unavailable');
   return {surfaces,processor};
  }catch{processor.dispose();return {error:true};}
 },[messages]);
 useEffect(()=>()=>result.processor?.dispose(),[result]);
 if(result.error)return <p role="status">The generated view could not be rendered. Use the text answer below.</p>;
 return <MarkdownComponentContext.Provider value={MarkdownView}>{result.surfaces.map(surface=><A2uiSurface key={surface.id} surface={surface}/>)}</MarkdownComponentContext.Provider>;
}

export default function A2UIAnswer({ui,onAction,disabled,evidence,onEvidence,children}){
 if(!ui)return children;
 return <>
  <section className="a2ui-answer" aria-label="Agent-composed answer" inert={disabled||undefined}>
   <p className="eyebrow">AGENT-COMPOSED VIEW</p>
   {ui.status==='completed'?<DisplayBoundary><Surface messages={ui.messages} onAction={onAction} evidence={evidence} onEvidence={onEvidence}/></DisplayBoundary>:<p role="status">{ui.message||'The generated view is unavailable. Use the text answer below.'}</p>}
  </section>
  <details open={ui.status!=='completed'}><summary>Text answer and sources</summary>{children}</details>
  <details className="a2ui-inspector"><summary>Inspect UI composition</summary>
   <p>Components: {ui.components?.join(', ')}. Order history navigation only. Layout uses a separate model call after the support investigation.</p>
   {ui.requests&&<p>UI composition: {ui.requests} call · {ui.input_tokens} input tokens · {ui.output_tokens} output tokens · {ui.elapsed_seconds}s. These are separate from the support totals below.</p>}
   <details><summary>Presentation instructions</summary><pre>{ui.instructions}</pre></details>
   <details><summary>Model layout output</summary><pre>{ui.model_output}</pre></details>
   <details><summary>A2UI messages received by the renderer</summary><pre>{JSON.stringify(ui.messages,null,2)}</pre></details>
  </details>
 </>;
}
