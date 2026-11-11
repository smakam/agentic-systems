import React,{useEffect,useState} from 'react';
import {cardInterfaces,isA2AMode,safeCard,supportModes} from './a2a.js';

export default function A2AAccess({api,mode,onMode,fixture,onFixture,disabled}){
 const [open,setOpen]=useState(false),[cards,setCards]=useState([]),[error,setError]=useState(''),[loading,setLoading]=useState(false),[attempt,setAttempt]=useState(0);
 useEffect(()=>{setOpen(false);setCards([]);setError('')},[mode]);
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
 return <section className="a2a-access" aria-label="A2A workspace options">
  <h4>A2A</h4><label>Mode<select aria-label="A2A mode" value={mode} disabled={disabled} onChange={e=>onMode(e.target.value)}>{supportModes.map(m=><option key={m.id} value={m.id}>{m.label}</option>)}</select></label>
  <p>Saved for this test workspace across account switching. Changing mode starts a new support conversation.</p>
  {mode==='a2a_delivery'&&<><label>Delivery scenario<select aria-label="Delivery scenario" value={fixture} disabled={disabled} onChange={e=>onFixture(e.target.value)}><option value="normal">Normal transit — on schedule</option><option value="exception">Depot exception</option></select></label><p>Applies to shipments created by new purchases. Dispatch creates their delivery records. Basic order status stays in the marketplace; detailed tracking can use the delivery agent.</p></>}
  {isA2AMode(mode)&&<button type="button" disabled={disabled} onClick={()=>setOpen(x=>!x)}>{open?'Hide Agent Cards':'View Agent Card'}</button>}
  {open&&<div className="a2a-card">
   {loading&&<p role="status">Fetching Agent Cards…</p>}
   {error&&<div role="alert">{error}<button type="button" onClick={()=>setAttempt(x=>x+1)}>Retry Agent Cards</button></div>}
   {cards.map(card=><section key={card.name}><h4>{card.name}</h4><p>{card.description}</p><h5>Endpoints</h5>{cardInterfaces(card).map((item,index)=><p key={index}><code>{item.url}</code><br/>{item.transport} · {item.version}</p>)}<h5>Skills</h5><ul>{card.skills.map((skill,index)=><li key={skill.id||index}><strong>{skill.name}</strong> — {skill.description}</li>)}</ul><h5>Capabilities</h5><pre>{JSON.stringify(card.capabilities||{},null,2)}</pre><details><summary>Details · Raw Agent Card JSON</summary><pre>{JSON.stringify(card,null,2)}</pre></details></section>)}
  </div>}
 </section>;
}
