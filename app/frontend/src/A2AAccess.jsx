import React,{useEffect,useState} from 'react';
import {cardInterfaces,isA2AMode,safeCard,supportModes,supportModeLabel} from './a2a.js';

export default function A2AAccess({api,mode,onMode,disabled,conversationId}){
 const [card,setCard]=useState(null),[error,setError]=useState(''),[loading,setLoading]=useState(false),[attempt,setAttempt]=useState(0);
 useEffect(()=>{
  let active=true;setCard(null);setError('');
  if(!isA2AMode(mode)){setLoading(false);return()=>{active=false};}
  setLoading(true);
  api('/a2a/support/.well-known/agent-card.json').then(value=>{
   if(!value||typeof value.name!=='string'||!Array.isArray(value.skills))throw new Error('The server did not return a valid Agent Card.');
   if(active)setCard(safeCard(value));
  }).catch(e=>{if(active)setError(e.message)}).finally(()=>{if(active)setLoading(false)});
  return()=>{active=false};
 },[api,mode,attempt]);
 const interfaces=cardInterfaces(card);
 return <section className="panel a2a-access" aria-label="Support access mode">
  <div className="a2a-access-heading"><div><span className="eyebrow">SUPPORT ACCESS</span><h2>{supportModeLabel(mode)}</h2></div><label>Demo mode<select aria-label="Support access mode" value={mode} disabled={disabled} onChange={e=>onMode(e.target.value)}>{supportModes.map(m=><option key={m.id} value={m.id}>{m.label}</option>)}</select></label></div>
  <p>{isA2AMode(mode)?'Your browser sends this question through A2A to the existing marketplace support agent. Each question creates a new task; follow-ups keep this conversation’s history.':'Questions use the existing marketplace API and support agent.'} {conversationId?'Changing mode starts a new conversation.':'The selected mode is saved when the conversation starts.'}</p>
  {mode==='a2a_delivery'&&<p className="a2a-delivery-note">Support can delegate shipment investigations to the simulated delivery agent. To enroll a new shipment, the seller chooses A2A delivery in Orders &amp; fulfillment before dispatch. Existing shipment links are preserved across mode changes.</p>}
  {isA2AMode(mode)&&<details className="a2a-card" open><summary>Actual support Agent Card</summary>
   {loading&&<p role="status">Fetching the Agent Card from this marketplace…</p>}
   {error&&<div role="alert" className="error">Agent Card unavailable: {error}<div><button type="button" disabled={loading} onClick={()=>setAttempt(x=>x+1)}>Retry Agent Card</button></div></div>}
   {card&&<><h3>{card.name}</h3><p>{card.description||'No description supplied.'}</p>
    <h4>Business skills</h4>{card.skills.length?<ul>{card.skills.map((skill,index)=><li key={skill.id||index}><strong>{skill.name||skill.id||'Unnamed skill'}</strong>{skill.description&&<> — {skill.description}</>}</li>)}</ul>:<p>No skills advertised.</p>}
    <dl><dt>Protocol version</dt><dd>{card.protocolVersion||interfaces.map(i=>i.version).filter(Boolean).join(', ')||'Not supplied'}</dd><dt>Interfaces</dt><dd>{interfaces.length?<ul>{interfaces.map((item,index)=><li key={index}><strong>{item.transport}</strong><code>{item.url}</code>{item.version&&<small>Protocol {item.version}</small>}</li>)}</ul>:'No interface advertised.'}</dd><dt>Capabilities</dt><dd><pre>{JSON.stringify(card.capabilities||{},null,2)}</pre></dd><dt>Security declarations</dt><dd><pre>{JSON.stringify({schemes:card.securitySchemes||{},requirements:card.security||card.securityRequirements||[]},null,2)}</pre></dd></dl>
    <details><summary>Raw Agent Card JSON</summary><pre>{JSON.stringify(card,null,2)}</pre></details>
   </>}
  </details>}
 </section>;
}
