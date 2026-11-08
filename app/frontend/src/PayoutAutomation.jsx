import React,{useEffect,useState} from 'react';

const timestamp=value=>value?new Date(value).toLocaleString():'No run yet';
const rupees=value=>new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR'}).format(Number(value||0)/100);

export default function PayoutAutomation({api,onChange,sellers=[]}){
  const [status,setStatus]=useState(null),[error,setError]=useState(''),[saving,setSaving]=useState(false);
  useEffect(()=>{
    let active=true;
    async function refresh(){try{const result=await api('/payout-automation');if(active){setStatus(result);onChange(Boolean(result.enabled));setError('')}}catch(e){if(active)setError(e.message)}}
    refresh();const timer=setInterval(refresh,10000);
    return()=>{active=false;clearInterval(timer)};
  },[api,onChange]);
  async function toggle(){
    setSaving(true);setError('');
    try{const result=await api('/payout-automation',{enabled:!status.enabled});setStatus(result);onChange(Boolean(result.enabled))}
    catch(e){setError(e.message)}finally{setSaving(false)}
  }
  return <section className="payout-admin" aria-label="Automatic payout settings">
    <div className="intro"><h2>Automatic seller payouts</h2><p>Let the payout worker release eligible simulated seller payments. Buying, shipping, and confirming delivery remain separate marketplace actions.</p></div>
    {error&&<p className="error" role="alert">{error}</p>}
    {!status?<p>Checking payout automation…</p>:<>
      <article className="panel">
        <div className="row"><div><span className="eyebrow">{status.workspace==='test'?'TEST WORKSPACE':'MAIN WORKSPACE'}</span><h3>Scheduled payout worker</h3></div><span className="badge">{status.enabled?'Enabled':'Disabled'}</span></div>
        <p>Checks every {status.interval_seconds||60} seconds while enabled. All payments are simulated.</p>
        {status.can_configure?<label className="payout-toggle"><input type="checkbox" checked={Boolean(status.enabled)} disabled={saving} onChange={toggle}/><span>Enable automatic payouts</span></label>:<p className="muted">Automatic payouts are available in the Test workspace on port 5179. Main workspace payouts remain manual.</p>}
        <p className="muted">Disabling stops new releases. A transaction already being committed may finish. While automation is enabled, payout release is handled by the worker.</p>
      </article>
      <article className="panel"><h3>A payout must pass all checks</h3><ul><li>Delivery is confirmed.</li><li>The 24-hour hold has passed on the demo clock.</li><li>No active return blocks settlement.</li><li>The seller and amount are within the payout service’s permissions.</li></ul><p className="muted">Use “Advance demo clock 24h” in Seller settlement to test the hold. The scheduler interval uses real time.</p>{status.policy&&<p className="muted">Allowed sellers: {status.policy.seller_ids?.map(id=>sellers.find(seller=>seller.id===id)?.name||id).join(', ')||'None'}. Maximum {rupees(status.policy.max_payout_paise)} per payout and {rupees(status.policy.max_run_paise)} per run, up to {status.policy.max_payouts_per_run||status.policy.max_run_count} payouts.</p>}</article>
      <article className="panel"><h3>Worker activity</h3><div className="payout-activity"><div><small>Worker</small><strong>{status.worker_running?'Online':'Not reporting'}</strong></div><div><small>Last run</small><strong>{timestamp(status.last_run_at)}</strong></div></div>
        {status.enabled&&!status.worker_running&&<p className="error" role="status">Automation is enabled, but the worker is not reporting. No scheduled payout is confirmed until a run appears here.</p>}
        {status.last_result&&<div className="payout-result"><p>Last result: <strong>{status.last_result.status||'Recorded'}</strong></p>{Array.isArray(status.last_result.completed)&&status.last_result.completed.length>0&&<small>Released: {status.last_result.completed.join(', ')}</small>}<p>{Array.isArray(status.last_result.completed)?status.last_result.completed.length:Number(status.last_result.completed||0)} released · {Array.isArray(status.last_result.denied)?status.last_result.denied.length:Number(status.last_result.denied||0)} denied · {rupees(status.last_result.amount_paise)} paid</p></div>}
      </article>
    </>}
  </section>;
}
