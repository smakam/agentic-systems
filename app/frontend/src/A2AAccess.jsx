import React,{useEffect,useRef,useState} from 'react';
import {cardInterfaces,isA2AMode,safeCard,supportModes} from './a2a.js';

export default function A2AAccess({api,mode,onMode,fixture,onFixture,disabled}){
 const dialog=useRef(null);
 const [open,setOpen]=useState(false),[cards,setCards]=useState([]),[error,setError]=useState(''),[loading,setLoading]=useState(false),[attempt,setAttempt]=useState(0);
 useEffect(()=>{setOpen(false);setCards([]);setError('')},[mode]);
 useEffect(()=>{const viewer=dialog.current;if(open&&!viewer.open)viewer.showModal();else if(!open&&viewer.open)viewer.close()},[open]);
 useEffect(()=>{
  let active=true;
  if(!open||!isA2AMode(mode))return()=>{active=false};
  setLoading(true);setError('');setCards([]);
  const paths=['/a2a/support/.well-known/agent-card.json',...(mode==='a2a_delivery'?['/a2a/delivery/.well-known/agent-card.json']:[])];
  Promise.all(paths.map(path=>api(path).then(value=>{
   if(!value||typeof value.name!=='string'||!Array.isArray(value.skills))throw new Error('The server did not return a valid Agent Card.');
   return safeCard(value);
  }))).then(value=>{if(active)setCards(value)}).catch(e=>{if(active)setError(e.message)}).finally(()=>{if(active)setLoading(false)});
  return()=>{active=false};
 },[api,mode,open,attempt]);
 return <details className="panel workspace-option a2a-access" aria-label="A2A workspace options">
  <summary>A2A</summary><label>Experiment<select aria-label="A2A mode" value={isA2AMode(mode)?mode:''} disabled={disabled} onChange={e=>onMode(e.target.value)}><option value="" disabled hidden>Choose an A2A experiment</option>{supportModes.filter(m=>isA2AMode(m.id)).map(m=><option key={m.id} value={m.id}>{m.label}</option>)}</select></label>
  <p>{isA2AMode(mode)?'Saved for this test workspace across account switching. Changing experiment starts a new support conversation.':'A2A is off. Choose an experiment to enable it.'} Reset to defaults turns A2A off.</p>
  {mode==='a2a_delivery'&&<><label>Delivery scenario<select aria-label="Delivery scenario" value={fixture} disabled={disabled} onChange={e=>onFixture(e.target.value)}><option value="normal">Normal transit — on schedule</option><option value="exception">Depot exception</option></select></label><p>Applies to shipments created by new purchases. Dispatch creates their delivery records. Basic order status stays in the marketplace; detailed tracking can use the delivery agent.</p></>}
  {isA2AMode(mode)&&<button type="button" disabled={disabled} onClick={()=>setOpen(true)}>View Agent Card</button>}
  <dialog ref={dialog} className="a2a-modal" aria-label="Agent Cards" onCancel={()=>setOpen(false)} onClose={()=>setOpen(false)} onClick={e=>{if(e.target===e.currentTarget){const bounds=e.currentTarget.getBoundingClientRect();if(e.clientX<bounds.left||e.clientX>bounds.right||e.clientY<bounds.top||e.clientY>bounds.bottom)setOpen(false)}}}><header><h3>Agent Cards</h3><button type="button" onClick={()=>setOpen(false)} aria-label="Close Agent Cards">Close</button></header><div className="a2a-card">
   {loading&&<p role="status">Fetching Agent Cards…</p>}
   {error&&<div role="alert">{error}<button type="button" onClick={()=>setAttempt(x=>x+1)}>Retry Agent Cards</button></div>}
   {cards.map(card=><section key={card.name}><h4>{card.name}</h4><p>{card.description}</p><h5>Endpoints</h5>{cardInterfaces(card).map((item,index)=><p key={index}><code>{item.url}</code><br/>{item.transport} · {item.version}</p>)}<h5>Skills</h5><ul>{card.skills.map((skill,index)=><li key={skill.id||index}><strong>{skill.name}</strong> — {skill.description}</li>)}</ul><h5>Capabilities</h5><pre>{JSON.stringify(card.capabilities||{},null,2)}</pre><details><summary>Details · Raw Agent Card JSON</summary><pre>{JSON.stringify(card,null,2)}</pre></details></section>)}
  </div></dialog>
 </details>;
}
