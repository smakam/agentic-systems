import React from 'react';
export function ShipmentDelivery({shipment}){
 const link=shipment?.delivery_service;
 if(!link)return null;
 return <div className="shipment-delivery"><strong>Simulated A2A delivery</strong><small>Delivery reference: <code>{link.reference}</code></small><small>Scenario saved at purchase: {link.fixture==='exception'?'depot exception':'normal transit'}</small></div>;
}
