import React from 'react';
import {createComponentImplementation} from '@a2ui/react';
import {CommonSchemas,basicCatalog} from '@a2ui/web_core/v1_0';
import {z} from 'zod';
import {displayCatalogId} from './a2ui.js';

const label=value=>value.replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
function shownValue(name,value){
 if(/paise/i.test(name)&&/^-?\d+$/.test(value))return new Intl.NumberFormat('en-IN',{style:'currency',currency:'INR'}).format(Number(value)/100);
 if(/(?: at|date|time)$/.test(name)&&/^\d{4}-\d{2}-\d{2}[T ]/.test(value)){
  const date=new Date(value.replace(' ','T'));
  if(!Number.isNaN(date.valueOf()))return new Intl.DateTimeFormat('en-GB',{dateStyle:'medium',timeStyle:'short',timeZone:'UTC'}).format(date)+' UTC';
 }
 return value;
}
const fieldLabel=name=>label(name.replace(/\s*\(paise\)|\s+paise$/gi,''));
const Header=({kind,title,children})=><header className="a2ui-widget-header"><div className="a2ui-widget-brand"><span aria-hidden="true">◈</span><span>FIELDWORK <small>{kind}</small></span></div><h3>{title}</h3>{children}</header>;
const Source=({value})=><footer className="a2ui-source"><span>{value.scope}</span><details><summary>Source details</summary><span>{value.title}</span><small>Reference: {value.source}. Open the answer's source links to inspect the evidence.</small></details>{value.notice&&<strong>{value.notice}</strong>}</footer>;
function OrderSummary({props:{record}}){
 const order=record.fields.find(f=>f.label==='order id');
 const statuses=record.fields.filter(f=>/status$/.test(f.label)&&f.value!=='—');
 const fields=record.fields.filter(f=>f!==order&&!statuses.includes(f)&&f.value!=='—');
 return <section className="a2ui-record a2ui-order" aria-label="Order summary"><Header kind="ORDER SUMMARY" title={order?`Order ${order.value.replace(/^order-/, '')}`:'Order details'}><div className="a2ui-statuses">{statuses.map((f,i)=><div className="a2ui-status" key={i}><span>{fieldLabel(f.label)}</span><strong>{label(f.value)}</strong></div>)}</div></Header><dl className="a2ui-facts">{fields.map((field,index)=><div key={index}><dt>{fieldLabel(field.label)}</dt><dd>{shownValue(field.label,field.value)}</dd></div>)}</dl><Source value={record}/></section>;
}
function RecordTable({props:{dataset}}){
 const headers=dataset.headers;
 const title=headers.includes('product name')&&headers.includes('shipment status')?'Items and delivery':headers.includes('payout status')&&headers.includes('refund status')?'Returns, refunds and seller payouts':dataset.title;
 return <section className="a2ui-record" aria-label="Record table"><Header kind="RECORDS" title={title}><p className="a2ui-widget-count">{dataset.rows.length} source {dataset.rows.length===1?'record':'records'}</p></Header><div className="a2ui-table-scroll" tabIndex={0} role="region" aria-label="Scrollable marketplace records"><table><thead><tr>{dataset.headers.map((h,i)=><th key={i} scope="col">{fieldLabel(h)}</th>)}</tr></thead><tbody>{dataset.rows.map((r,i)=><tr key={i}>{r.map((v,j)=><td key={j}>{shownValue(dataset.headers[j],v)}</td>)}</tr>)}</tbody></table></div><Source value={dataset}/></section>;
}
function EventTimeline({props:{dataset}}){
 const kind=dataset.headers.indexOf('kind');
 const time=dataset.headers.indexOf('occurred at');
 const detail=dataset.headers.indexOf('details');
 return <section className="a2ui-record" aria-label="Event timeline"><Header kind="EVENT TIMELINE" title={`${dataset.rows.length} recorded ${dataset.rows.length===1?'event':'events'}`}/><ol className="a2ui-timeline">{dataset.rows.map((row,index)=><li key={index}><span className="a2ui-event-dot" aria-hidden="true"/><div className="a2ui-event-card">{time>=0&&<time>{shownValue('occurred at',row[time])}</time>}<h4>{kind>=0?label(row[kind]):`Event ${index+1}`}</h4>{detail>=0&&<p className="a2ui-event-detail">{row[detail]}</p>}<details><summary>Event record</summary><dl>{dataset.headers.map((header,j)=>j===kind||j===detail||j===time?null:<div key={j}><dt>{fieldLabel(header)}</dt><dd>{shownValue(header,row[j])}</dd></div>)}</dl></details></div></li>)}</ol><Source value={dataset}/></section>;
}
const domain=(name,prop,view)=>createComponentImplementation({name,schema:z.object({[prop]:CommonSchemas.DynamicValue})},view);
export const marketplaceCatalog=basicCatalog.derive({catalogId:displayCatalogId,components:['Column','Row','Card','Text','Divider','Button',domain('OrderSummary','record',OrderSummary),domain('RecordTable','dataset',RecordTable),domain('EventTimeline','dataset',EventTimeline)],functions:[]});
