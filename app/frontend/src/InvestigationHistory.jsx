import React,{useEffect,useId,useRef,useState} from 'react';

export default function InvestigationHistory({conversations,value,disabled,onChange}){
 const [open,setOpen]=useState(false);
 const root=useRef(null),trigger=useRef(null),list=useRef(null);
 const listId=useId();
 const selected=conversations.find(c=>c.id===value);
 useEffect(()=>{
  if(disabled)setOpen(false);
 },[disabled]);
 useEffect(()=>{
  if(!open)return;
  // Always open on the newest entry, even when an older investigation is selected.
  list.current.scrollTop=0;
  list.current.querySelector('[role="option"]')?.focus({preventScroll:true});
  const outside=e=>{if(!root.current?.contains(e.target))setOpen(false)};
  document.addEventListener('pointerdown',outside);
  return()=>document.removeEventListener('pointerdown',outside);
 },[open]);
 function close(){setOpen(false);trigger.current?.focus({preventScroll:true})}
 function navigate(e){
  if(e.key==='Escape'){e.preventDefault();close();return}
  const options=[...list.current.querySelectorAll('[role="option"]')];
  const index=options.indexOf(document.activeElement);
  let next;
  if(e.key==='ArrowDown')next=Math.min(index+1,options.length-1);
  else if(e.key==='ArrowUp')next=Math.max(index-1,0);
  else if(e.key==='Home')next=0;
  else if(e.key==='End')next=options.length-1;
  else return;
  e.preventDefault();options[next]?.focus();
 }
 return <div className="investigation-history" ref={root} onBlur={e=>{if(!e.currentTarget.contains(e.relatedTarget))setOpen(false)}}>
  <button type="button" ref={trigger} className="investigation-history-trigger" aria-label="Choose an investigation" aria-haspopup="listbox" aria-expanded={open} aria-controls={listId} disabled={disabled} onClick={()=>setOpen(x=>!x)} onKeyDown={e=>{if(e.key==='ArrowDown'){e.preventDefault();setOpen(true)}}}>
   <span>{selected?.title||'Choose an investigation'}</span><span aria-hidden="true">▾</span>
  </button>
  {open&&<div id={listId} ref={list} className="investigation-history-list" role="listbox" aria-label="Recent investigations, newest first" onKeyDown={navigate}>
   {conversations.length?conversations.map(c=><button type="button" key={c.id} role="option" aria-selected={c.id===value} tabIndex={-1} onClick={()=>{close();onChange(c.id)}}>{c.title}</button>):<p>No investigations yet.</p>}
  </div>}
 </div>;
}
