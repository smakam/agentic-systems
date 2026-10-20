import test from 'node:test';
import assert from 'node:assert/strict';
import {executionCounts} from './execution-counts.js';
test('older run with order history shows three tools and four evidence saves',()=>{
  assert.deepEqual(executionCounts({tool_calls:4,business_tool_calls:4,tool_attempts:[{name:'get_order_history'},{name:'get_catalog'},{name:'query_business_data'}]}),{toolInvocations:3,evidenceSaveAttempts:4});
});
test('legacy evidence counter alone cannot establish a tool invocation count',()=>{
  assert.deepEqual(executionCounts({tool_calls:4}),{toolInvocations:null,evidenceSaveAttempts:null});
});
test('explicit new counters preserve zero and keep memory calls separate',()=>{
  assert.deepEqual(executionCounts({actual_tool_invocations:1,evidence_save_attempts:0,tool_calls:1}),{toolInvocations:1,evidenceSaveAttempts:0});
});
