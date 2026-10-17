// Presentation helpers resolve existing records without changing business history.
export function newestEvents(events){
  return [...events].sort((a,b)=>Number(b.revision)-Number(a.revision)
    || Date.parse(b.occurred_at)-Date.parse(a.occurred_at)
    || Date.parse(b.recorded_at||b.occurred_at)-Date.parse(a.recorded_at||a.occurred_at)
    || String(a.id).localeCompare(String(b.id)));
}

export function eventOrderIds(event,data){
  const find=(collection,id)=>(data[collection]||[]).find(row=>row.id===id);
  const orderIds=new Set();
  const addItem=id=>{const item=find('items',id);if(item)orderIds.add(item.order_id)};
  for(const id of [event.entity_id,event.details?.id,event.details?.order_id]){
    if(!id)continue;
    if(find('orders',id))orderIds.add(id);
    addItem(id);
    const shipment=find('shipments',id);if(shipment)addItem(shipment.item_id);
    const returned=find('returns',id);if(returned)addItem(returned.item_id);
    const refund=find('refunds',id);
    if(refund){const request=find('returns',refund.return_id);if(request)addItem(request.item_id)}
    const payout=find('payouts',id);
    const allocation=find('allocations',payout?.allocation_id||id);
    if(allocation)addItem(allocation.item_id);
  }
  return [...orderIds];
}
