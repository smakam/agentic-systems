import React,{useEffect,useState,useRef} from 'react';
import Markdown from 'react-markdown';

export default function RagPolicyDemo({api,disabled=false}){
 const dialog=useRef(null);
 const [experiment,setExperiment]=useState('versions'),[state,setState]=useState(null),[question,setQuestion]=useState(''),[topK,setTopK]=useState(4),[busy,setBusy]=useState(false),[error,setError]=useState(''),[results,setResults]=useState([]);
 useEffect(()=>{let active=true;setState(null);setResults([]);setError('');setTopK(4);api(`/rag-policy-demo/${experiment}`).then(s=>{if(active){setState(s);setQuestion(s.question)}}).catch(e=>{if(active)setError(e.message)});return()=>{active=false}},[experiment]);
 async function action(path,body={}){setBusy(true);setError('');try{const s=await api(`/rag-policy-demo/${experiment}/${path}`,body);setState(s);if(path==='restore')setResults([])}catch(e){setError(e.message)}finally{setBusy(false)}}
 async function ask(){setBusy(true);setError('');try{const result=await api(`/rag-policy-demo/${experiment}/ask`,{question,top_k:experiment==='versions'?4:topK});setResults(previous=>[...previous,result])}catch(e){setError(e.message)}finally{setBusy(false)}}
 const locked=disabled||busy;
 return <section className="workspace-subsection"><button disabled={disabled} onClick={()=>dialog.current.showModal()}>Open RAG experiments</button><dialog ref={dialog} className="rag-policy-demo rag-policy-demo-dialog" aria-label="RAG experiments"><header><h3>RAG experiments</h3><button onClick={()=>dialog.current.close()}>Close</button></header>
  <p>Isolated demo documents and fixed facts. These controls do not change marketplace policies or records. Questions use model and embedding API calls.</p>
  <label>Experiment<select aria-label="RAG experiment" value={experiment} disabled={locked} onChange={e=>setExperiment(e.target.value)}><option value="versions">Policy versions and reindexing</option><option value="chunking">Chunking and passage limit</option></select></label>
  {error&&<p role="alert" className="error">{error}</p>}
  {state?.experiment===experiment&&<>
   <p><strong>Fixed facts:</strong> {state.facts}</p>
   {experiment==='versions'?<label>Source document<select aria-label="RAG source version" value={state.source_version} disabled={locked} onChange={e=>action('source',{version:e.target.value,strategy:'paragraph'})}><option value="v1">V1 — 24-hour wait</option><option value="v2">V2 — 48-hour wait</option></select></label>:<>
    <p><strong>Source:</strong> Expanded policy with the standard rule and adjacent Amber Review extension.</p>
    <label>Chunking strategy<select aria-label="RAG chunking strategy" value={state.strategy} disabled={locked} onChange={e=>action('source',{version:'expanded',strategy:e.target.value})}><option value="paragraph">Paragraph</option><option value="overlap">Two-paragraph overlap</option></select></label>
    <label>Maximum passages (top K)<select aria-label="RAG maximum passages" value={topK} disabled={locked} onChange={e=>setTopK(Number(e.target.value))}><option value={1}>1</option><option value={4}>4</option></select></label>
   </>}
   <p><strong>Selected:</strong> {state.source_version.toUpperCase()} · {state.strategy}<br/><strong>Indexed:</strong> {state.ready?`${state.indexed_version.toUpperCase()} · ${state.indexed_strategy} · ${state.chunk_count} chunks`:'Not prepared'}</p>
   {state.stale&&<p role="status" className="rag-stale">Source settings changed. Questions still search the previous index until you index the selection.</p>}
   <div className="rag-actions"><button disabled={locked} onClick={()=>action('index')}>{state.ready?'Index selected settings':experiment==='versions'?'Prepare V1 index':'Prepare paragraph index'}</button>{state.ready&&<button disabled={locked} onClick={()=>action('restore')}>{experiment==='versions'?'Restore V1':'Restore paragraph baseline'}</button>}</div>
   <details><summary>Selected source document</summary><pre>{state.source_text}</pre></details>
   <label>Demo question<textarea aria-label="RAG demo question" value={question} disabled={locked} onChange={e=>setQuestion(e.target.value)} maxLength={2000}/></label>
   <button disabled={locked||!state.ready||!question.trim()} onClick={ask}>{busy?'Working…':'Ask the demo question'}</button>
   <p>The demo question searches only this experiment’s indexed passages. Each ask is independent; it does not use chat history or long-term memory. Changing top K does not require indexing.</p>
   {results.map((r,index)=><article className="rag-demo-result" key={index}>
    <h4>Run {index+1}: {r.indexed_version.toUpperCase()} · {r.indexed_strategy} · top K {r.top_k}</h4>
    <p>{r.stale?'Source differs from this index. ':''}{r.passages.length} passages · {r.retrieved_characters} characters · cosine vector search</p>
    <p><strong>Question:</strong> {r.question}</p><div className="answer"><Markdown>{r.answer}</Markdown></div>
    <details><summary>Retrieved passages and source lines</summary>{r.passages.map(p=><section key={p.id}><strong>{p.id} · {p.source} · lines {p.line_start}–{p.line_end}</strong><p>{p.body}</p></section>)}</details>
   </article>)}
  </>}
 </dialog></section>
}
