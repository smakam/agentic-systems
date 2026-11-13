import test from 'node:test';
import assert from 'node:assert/strict';
import {deliveryEvidenceView,formatEvidence,sourceLabel} from './evidence.js';

const evidence = {'evidence-ab12': {type:'query',sql:'SELECT * FROM analytics.events'}};
test('canonical, legacy and bare citations resolve to the same readable source', () => {
  for (const text of ['[evidence:evidence-ab12]', '[evidence-ab12]', 'evidence-ab12', '[source](#evidence-ab12)']) {
    assert.equal(formatEvidence(text,evidence), '[View event timeline](#evidence-ab12)');
  }
});
test('unknown citations cannot become working evidence links', () => {
  assert.equal(formatEvidence('[evidence:evidence-dead]',evidence),'[Source unavailable]');
});
test('ordinary Markdown links remain unchanged and rendering is idempotent', () => {
  const text='[Documentation](https://example.com/evidence-ab12)';
  assert.equal(formatEvidence(text,evidence),text);
  const formatted=formatEvidence('Evidence handle: evidence-ab12',evidence);
  assert.equal(formatted,'Source: [View event timeline](#evidence-ab12)');
  assert.equal(formatEvidence(formatted,evidence),formatted);
});
test('shortened model citations resolve only to recorded evidence', () => {
  const records={'evidence-ab123456':{type:'documents'}};
  assert.equal(formatEvidence('[evidence:ab123456]',records),'[View policy passages](#evidence-ab123456)');
  assert.equal(formatEvidence('[evidence:dead1234]',records),'[Source unavailable]');
});

test('policy-conflict citations with shortened handles all resolve to their recorded sources', () => {
  const records={
    'evidence-f925b92c3fb0':{type:'documents'},
    'evidence-ce9b87017198':{type:'query',sql:'SELECT * FROM analytics.shipments'},
    'evidence-1a7de01c1077':{type:'query',sql:'SELECT * FROM analytics.events'},
  };
  const answer='Hold policy [evidence:f925b92c3fb0], delivery [evidence:ce9b87017198], history [evidence:1a7de01c1077].';
  assert.equal(formatEvidence(answer,records),'Hold policy [View policy passages](#evidence-f925b92c3fb0), delivery [View database records](#evidence-ce9b87017198), history [View event timeline](#evidence-1a7de01c1077).');
});

import {withCitationEvidence} from './evidence.js';
test('follow-up links resolve original records and retain original snapshot', () => {
  const evidence={'evidence-ab12':{type:'query',rows:[{quantity:2}],snapshot:{revision:1}}};
  const runs=withCitationEvidence([
    {id:'first',conversation_id:'one',question:'Products?',evidence},
    {id:'second',conversation_id:'one',question:'Total?',evidence:{}},
    {id:'third',conversation_id:'two',evidence:{}},
  ]);
  assert.equal(formatEvidence('[evidence:evidence-ab12]',runs[1].citationEvidence),'[View database records (earlier question)](#evidence-ab12)');
  assert.equal(runs[1].citationEvidence['evidence-ab12'].snapshot.revision,1);
  assert.equal(runs[1].citationEvidence['evidence-ab12'].source_run_id,'first');
  assert.deepEqual(runs[1].evidence,{});
  assert.deepEqual(runs[2].citationEvidence,{});
  assert.equal(evidence['evidence-ab12'].source_run_id,undefined);
  assert.equal(formatEvidence('[evidence:evidence-dead]',runs[1].citationEvidence),'[Source unavailable]');
});
test('citations cannot resolve evidence from a later answer', () => {
  const runs=withCitationEvidence([{id:'a',conversation_id:'one',evidence:{}},{id:'b',conversation_id:'one',evidence}]);
  assert.deepEqual(runs[0].citationEvidence,{});
});

test('RAG citations resolve only the saved passages and order in their own answer', () => {
  const make=(id,body)=>({id,conversation_id:'same',metrics:{rag_demo:{indexed_version:id,passages:[{id:'passage-2',source:'policy.md',line_start:3,line_end:3,body}],order:{order_id:id}}}});
  const runs=withCitationEvidence([make('v1','Wait 24 hours'),make('v2','Wait 48 hours'),{conversation_id:'same',evidence:{}}]);
  for (let i=0;i<2;i++) {
    const text=formatEvidence('[passage-2] [order-record]',runs[i].citationEvidence);
    assert.equal(text,'[View passage-2](#evidence-rag-passage-2) [View order records](#evidence-rag-order-record)');
    assert.equal(formatEvidence(text,runs[i].citationEvidence),text);
    assert.equal(formatEvidence('(passage-2) order-record',runs[i].citationEvidence),text);
    assert.equal(runs[i].citationEvidence['evidence-rag-order-record'].rows[0].value,i?'v2':'v1');
  }
  assert.equal(runs[0].citationEvidence['evidence-rag-passage-2'].chunks[0].body,'Wait 24 hours');
  assert.equal(runs[1].citationEvidence['evidence-rag-passage-2'].chunks[0].body,'Wait 48 hours');
  assert.equal(formatEvidence('[passage-2] [order-record]',runs[2].citationEvidence),'[Source unavailable] [Source unavailable]');
  assert.equal(formatEvidence('[passage-99]',runs[0].citationEvidence),'[Source unavailable]');
  assert.equal(formatEvidence('[Docs](https://example.com/passage-2)',runs[0].citationEvidence),'[Docs](https://example.com/passage-2)');
});

test('delivery citations distinguish fresh remote findings, local records and an unavailable source',()=>{
 assert.equal(sourceLabel({type:'delivery',status:'ok',linked:true}),'View delivery findings');
 assert.equal(sourceLabel({type:'delivery',status:'ok',linked:false}),'View local shipment records');
 assert.equal(sourceLabel({type:'delivery',status:'error',linked:true}),'View unavailable delivery source');
 assert.equal(formatEvidence('[evidence:evidence-ab12]',{'evidence-ab12':{type:'delivery',status:'ok',linked:true}}),'[View delivery findings](#evidence-ab12)');
});

test('delivery inspector renders actual status and conditional detail evidence without inventing promises',()=>{
 const evidence={type:'delivery',status:'ok',linked:true,shipment_id:'ship-1',result:{reference:'delivery-1',findings:'Parcel held at the depot.',shipment_status:{status:'exception',overdue:true,on_schedule:false,observed_at:'2026-11-10T12:00:00Z'},tool_trace:[{tool:'get_current_shipment_status',result:{status:'exception'}},{tool:'get_delivery_problem_details',result:{reason:'Sorting scanner failed.',tracking_events:[{event:'exception',detail:'Manual rerouting'}]}}]}};
 const view=deliveryEvidenceView(evidence);
 assert.equal(view.source,'Simulated delivery service');assert.equal(view.reason,'Sorting scanner failed.');assert.equal(view.problemChecked,true);
 assert.deepEqual(view.fields,[['Delivery reference','delivery-1'],['Recorded status','exception'],['Overdue','Yes'],['On schedule','No'],['Observed at','2026-11-10T12:00:00Z']]);
 assert.equal(view.fields.some(([label])=>label==='Expected delivery at'),false);assert.equal(view.trace.length,2);assert.equal(view.events.length,1);
 const normal=deliveryEvidenceView({...evidence,result:{shipment_status:{status:'in_transit'},tool_trace:[evidence.result.tool_trace[0]]}});
 assert.equal(normal.problemChecked,false);assert.equal(normal.reason,null);assert.equal(normal.fields.some(([label])=>label==='On schedule'),false,'in-transit alone cannot establish schedule health');
});

test('unavailable remote evidence cannot display stale status or present local data as remote verification',()=>{
 const view=deliveryEvidenceView({type:'delivery',linked:true,status:'error',message:'No fresh remote status was verified.',shipment_status:'dispatched',result:{shipment_status:{status:'delivered'},findings:'Stale answer'}});
 assert.equal(view.error,'No fresh remote status was verified.');assert.deepEqual(view.fields,[]);assert.deepEqual(view.trace,[]);assert.equal(view.findings,undefined);
 const local=deliveryEvidenceView({type:'delivery',linked:false,status:'ok',shipment_status:'dispatched',source_run_id:'older'});
 assert.equal(local.source,'Marketplace local records');assert.equal(local.historical,true);assert.deepEqual(local.fields,[['Shipment status','dispatched']]);
});
