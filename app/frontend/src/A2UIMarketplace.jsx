import React from 'react';
import {createComponentImplementation} from '@a2ui/react';
import {CommonSchemas,basicCatalog} from '@a2ui/web_core/v1_0';
import {z} from 'zod';
import {displayCatalogId} from './a2ui.js';

const Source=({value})=><footer className="a2ui-source"><span>{value.scope}</span><span>Source: {value.source}. See Text answer and sources below.</span>{value.notice&&<strong>{value.notice}</strong>}</footer>;
function OrderSummary({props:{record}}){
 return <section className="a2ui-record" aria-label="Order summary"><h3>{record.title}</h3><dl>{record.fields.map((field,index)=><div key={index}><dt>{field.label}</dt><dd>{field.value}</dd></div>)}</dl><Source value={record}/></section>;
}
function RecordTable({props:{dataset}}){
 return <section className="a2ui-record" aria-label="Record table"><h3>{dataset.title}</h3><div className="a2ui-table-scroll" tabIndex={0} role="region" aria-label="Scrollable marketplace records"><table><thead><tr>{dataset.headers.map((h,i)=><th key={i} scope="col">{h}</th>)}</tr></thead><tbody>{dataset.rows.map((r,i)=><tr key={i}>{r.map((v,j)=><td key={j}>{v}</td>)}</tr>)}</tbody></table></div><Source value={dataset}/></section>;
}
function EventTimeline({props:{dataset}}){
 const kind=dataset.headers.indexOf('kind');
 return <section className="a2ui-record" aria-label="Event timeline"><h3>{dataset.title}</h3><ol className="a2ui-timeline">{dataset.rows.map((row,index)=><li key={index}><strong>{kind>=0?row[kind]:`Event ${index+1}`}</strong><dl>{dataset.headers.map((header,j)=>j===kind?null:<div key={j}><dt>{header}</dt><dd>{row[j]}</dd></div>)}</dl></li>)}</ol><Source value={dataset}/></section>;
}
const domain=(name,prop,view)=>createComponentImplementation({name,schema:z.object({[prop]:CommonSchemas.DynamicValue})},view);
export const marketplaceCatalog=basicCatalog.derive({catalogId:displayCatalogId,components:['Column','Row','Card','Text','Divider','Button',domain('OrderSummary','record',OrderSummary),domain('RecordTable','dataset',RecordTable),domain('EventTimeline','dataset',EventTimeline)],functions:[]});
