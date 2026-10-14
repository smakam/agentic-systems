// Authentication failures on protected requests return the UI to sign-in.
export async function request(path,body,method,csrf,onSessionExpired){
  const response=await fetch('/api'+path,{method:method||(body===undefined?'GET':'POST'),headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:body===undefined?undefined:JSON.stringify(body)});
  if(response.status===401 && path!=='/login' && path!=='/me')onSessionExpired();
  const value=await response.json();
  if(!response.ok){const error=new Error(typeof value.detail==='string'?value.detail:'Request failed');error.status=response.status;throw error;}
  return value;
}

export function memoryResourcePath(id,provider='internal',version){
 const query=new URLSearchParams({provider});
 if(provider==='internal'&&version!=null)query.set('expected_version',String(version));
 return `/memories/${encodeURIComponent(id)}?${query}`;
}
export function memoryEditBody(memory,content,provider='internal'){
 const body={title:memory.title||'Saved memory',content};
 if(provider==='internal'&&memory.version!=null)body.expected_version=memory.version;
 return body;
}
export function memoryJobLabel(status){
 return {pending:'Memory save queued',queued:'Memory save queued',processing:'Saving memories in the background',running:'Saving memories in the background',complete:'Memory save complete',completed:'Memory save complete',failed:'Memory save failed',noop:'No new memories to save',skipped:'No new memories to save',idle:'Waiting for the conversation to end or become idle',not_started:'No memory save requested'}[status]||'Memory save status unavailable';
}

export function keepPreviousMemoryJob(monitoredId,currentId,status){
 return Boolean(monitoredId&&monitoredId!==currentId&&!['complete','completed','failed','noop','skipped'].includes(status));
}
