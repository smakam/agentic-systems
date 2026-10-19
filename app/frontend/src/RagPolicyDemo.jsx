import React,{useEffect,useState} from 'react';

export default function RagPolicyDemo({api,disabled=false,experiment,onExperiment,topK,onTopK,onReady,onBusy,onQuestion,resetKey=0}){
 const [state,setState]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState('');
 useEffect(()=>{onBusy(busy)},[busy]);
 useEffect(()=>{let active=true;setState(null);setError('');onReady(experiment==='off');
  if(experiment==='off')return;
  setBusy(true);
  api(`/rag-policy-demo/${experiment}/index`,{}).then(s=>{if(active){setState(s);onReady(s.ready);}}).catch(e=>{if(active){setError(e.message);onReady(false)}}).finally(()=>{if(active)setBusy(false)});
  return()=>{active=false};
 },[experiment,resetKey]);
 async function action(path,body={}){setBusy(true);setError('');onReady(false);try{const s=await api(`/rag-policy-demo/${experiment}/${path}`,body);setState(s);onReady(s.ready)}catch(e){setError(e.message);try{setState(await api(`/rag-policy-demo/${experiment}`))}catch{}}finally{setBusy(false)}}
 const locked=disabled||busy;
 return <section className="workspace-subsection">
  <label>RAG experiment<select aria-label="RAG experiment" value={experiment} disabled={locked} onChange={e=>{onReady(false);onExperiment(e.target.value)}}><option value="off">Off — marketplace documents</option><option value="versions">Policy versions and reindexing</option><option value="chunking">Chunking and passage limit</option></select></label>
  {experiment==='off'?<p>Normal Support questions use marketplace documents. Indexing is managed automatically.</p>:<>
   <p>Ask in the main question box. This experiment uses isolated lab documents and fixed facts. Start a new conversation for each comparison.</p>
   {busy&&<p role="status">Preparing documents…</p>}
   {error&&<p role="alert">{error} <button disabled={disabled||busy} onClick={()=>action('index')}>Retry preparation</button></p>}
   {state?.experiment===experiment&&<>
    <p><strong>Fixed facts:</strong> {state.facts}</p>
    {experiment==='versions'?<label>Policy version<select aria-label="RAG source version" value={state.source_version} disabled={locked} onChange={e=>action('source',{version:e.target.value,strategy:'paragraph'})}><option value="v1">V1 — 24-hour wait</option><option value="v2">V2 — 48-hour wait</option></select></label>:<>
     <label>Chunking strategy<select aria-label="RAG chunking strategy" value={state.strategy} disabled={locked} onChange={e=>action('source',{version:'expanded',strategy:e.target.value})}><option value="paragraph">Paragraph</option><option value="overlap">Two-paragraph overlap</option></select></label>
     <label>Maximum passages (top K)<select aria-label="RAG maximum passages" value={topK} disabled={locked} onChange={e=>onTopK(Number(e.target.value))}><option value={1}>1</option><option value={4}>4</option></select></label>
    </>}
    <p role="status"><strong>{error?'Preparation failed':busy?'Preparing documents':state.ready?'Ready':'Not ready'}</strong> · Selected {state.source_version.toUpperCase()} / {state.strategy} · Indexed {state.indexed_version?.toUpperCase()||'none'} / {state.indexed_strategy||'none'}</p>
    {state.stale&&<p className="rag-stale">{error?'Preparation pending: ':'Intentional stale-index demonstration: '} the selected source differs from the index. Questions still retrieve the indexed policy.</p>}
    {experiment==='versions'&&<><button disabled={locked||state.source_version!=='v1'||state.indexed_version!=='v1'} onClick={()=>action('source',{version:'v2',strategy:'paragraph',demonstrate_stale:true})}>Demonstrate source change without reindexing</button>{state.stale&&<button disabled={locked} onClick={()=>action('index')}>Apply changed source</button>}</>}
    <button disabled={locked} onClick={()=>action('restore')}>{experiment==='versions'?'Restore V1':'Restore paragraph baseline'}</button>
    <button disabled={locked||!state.ready} onClick={()=>onQuestion(state.question)}>Use example question</button>
    <details><summary>Selected source document</summary><pre>{state.source_text}</pre></details>
    <p>Unchanged chunks reuse stored embeddings. Changing top K needs no document indexing. Questions still use query-embedding and model API calls.</p>
   </>}
  </>}
 </section>
}
