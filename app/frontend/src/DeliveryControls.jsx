import React,{useEffect,useState} from 'react';
import {shipmentFixtureChange} from './a2a.js';

export function DeliveryEnrollment({mode,fixture,onMode,onFixture,disabled}){
 return <section className="panel delivery-enrollment" aria-label="Simulated delivery enrollment">
  <h2>Delivery for new dispatches</h2><div className="delivery-settings"><label>Dispatch route<select aria-label="Dispatch route" value={mode} disabled={disabled} onChange={e=>onMode(e.target.value)}><option value="local">Local marketplace</option><option value="a2a">A2A delivery service</option></select></label><label>Simulated delivery fixture<select aria-label="Simulated delivery fixture" value={fixture} disabled={disabled||mode!=='a2a'} onChange={e=>onFixture(e.target.value)}><option value="normal">Normal transit — on schedule</option><option value="exception">Delivery exception — stuck at depot</option></select></label></div>
  <p>These settings enroll new dispatches only. A linked shipment continues through its delivery service even if you switch back to local. Support access mode is selected separately in the Support workspace.</p>
 </section>;
}

export function ShipmentDelivery({shipment,role,disabled,onApply}){
 const link=shipment?.delivery_service;
 const [fixture,setFixture]=useState(link?.fixture||'normal');
 useEffect(()=>{setFixture(link?.fixture||'normal')},[shipment?.id,link?.fixture]);
 if(!link)return null;
 const change=shipmentFixtureChange(shipment,role,fixture);
 return <div className="shipment-delivery"><strong>Simulated A2A delivery</strong><small>Delivery reference: <code>{link.reference}</code></small><small>Saved simulator scenario: {link.fixture==='exception'?'depot exception':link.fixture==='normal'?'normal transit':link.fixture||'not supplied'}</small><small>This is the saved service link. A support investigation fetches the current external status and recorded reasons.</small>{change&&<div className="delivery-scenario-control"><label>Change this shipment’s scenario<select aria-label={`Delivery scenario for ${shipment.id}`} value={fixture} disabled={disabled} onChange={e=>setFixture(e.target.value)}><option value="normal">Normal transit — on schedule</option><option value="exception">Delivery exception — stuck at depot</option></select></label><button type="button" disabled={disabled||fixture===link.fixture} onClick={()=>onApply?.(change.action,change.data)}>Apply delivery scenario</button><small>Manual simulation only. Changing the scenario leaves this shipment dispatched; use Simulate delivery to complete it.</small></div>}</div>;
}
