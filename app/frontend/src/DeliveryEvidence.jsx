import React from 'react';
import {deliveryEvidenceView} from './evidence.js';

export default function DeliveryEvidence({evidence}){
 const view=deliveryEvidenceView(evidence);
 if(!view)return null;
 return <section className="delivery-evidence" aria-label="Delivery evidence findings"><h4>{view.source}</h4>{view.shipmentId&&<small>Shipment: {view.shipmentId}</small>}
  {view.error?<p role="alert" className="error">{view.error}</p>:<>
   {view.fields.length>0&&<dl>{view.fields.map(([label,value])=><React.Fragment key={label}><dt>{label}</dt><dd>{String(value).replaceAll('_',' ')}</dd></React.Fragment>)}</dl>}
   {view.findings&&<><h4>Delivery agent findings</h4><p className="delivery-findings">{view.findings}</p></>}
   {evidence.linked&&<><h4>Recorded checks</h4><ol>{view.trace.map((step,index)=><li key={index}><strong>{{get_current_shipment_status:'Read current shipment status',get_delivery_problem_details:'Read recorded delivery problem details'}[step.tool]||step.tool}</strong></li>)}</ol>{view.problemChecked?<p><strong>Recorded reason:</strong> {view.reason}</p>:<p>Problem details were not requested in this investigation.</p>}{view.events?.length>0&&<details><summary>Recorded tracking events ({view.events.length})</summary><ul>{view.events.map((event,index)=><li key={index}><strong>{event.event?.replaceAll('_',' ')||'Tracking event'}</strong>{event.at&&<small>{event.at}</small>}{event.detail&&<p>{event.detail}</p>}</li>)}</ul></details>}{view.modelRequests!=null&&<small>{view.modelRequests} delivery model response(s) recorded.</small>}</>}
   <p className="muted">{view.note||'This panel shows evidence saved with the investigation.'} Opening this panel does not fetch a new status.</p>
  </>}
 </section>;
}
