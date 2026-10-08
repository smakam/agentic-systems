// Authentication failures on protected requests return the UI to sign-in.
export async function request(path,body,method,csrf,onSessionExpired){
  const response=await fetch('/api'+path,{method:method||(body===undefined?'GET':'POST'),headers:{'Content-Type':'application/json','X-CSRF-Token':csrf},body:body===undefined?undefined:JSON.stringify(body)});
  if(response.status===401 && path!=='/login' && path!=='/me')onSessionExpired();
  const value=await response.json();
  if(!response.ok){const error=new Error(typeof value.detail==='string'?value.detail:'Request failed');error.status=response.status;throw error;}
  return value;
}
