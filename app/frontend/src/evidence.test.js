import test from 'node:test';
import assert from 'node:assert/strict';
import {formatEvidence} from './evidence.js';

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
