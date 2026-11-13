export function sourceLabel(evidence) {
  if (!evidence) return 'Source unavailable';
  if (evidence.citation_label) return evidence.citation_label;
  if (evidence.source_run_id) return `${sourceLabel({...evidence,source_run_id:null})} (earlier question)`;
  if (evidence.type === 'catalog') return 'View data definitions';
  if (evidence.type === 'documents') return 'View policy passages';
  if (evidence.type === 'query') return /\bevents\b/i.test(evidence.sql || '') ? 'View event timeline' : 'View database records';
  if (evidence.type === 'delivery') return evidence.status==='error'?'View unavailable delivery source':evidence.linked?'View delivery findings':'View local shipment records';
  return 'View source';
}

// Render saved evidence only. Opening the inspector never refreshes a carrier
// status and cannot turn an unavailable remote observation into a local result.
export function deliveryEvidenceView(evidence){
 if(evidence?.type!=='delivery')return null;
 const base={shipmentId:evidence.shipment_id,source:evidence.linked?'Simulated delivery service':'Marketplace local records',historical:Boolean(evidence.source_run_id)};
 if(evidence.status!=='ok')return {...base,error:evidence.message||'Delivery evidence is unavailable; no fresh remote status was verified.',fields:[],trace:[]};
 if(!evidence.linked)return {...base,fields:[['Shipment status',evidence.shipment_status],['Delivered at',evidence.delivered_at]].filter(([,value])=>value!=null),note:evidence.note,trace:[]};
 const result=evidence.result||{},status=result.shipment_status||{},trace=Array.isArray(result.tool_trace)?result.tool_trace:[],problem=trace.find(t=>t.tool==='get_delivery_problem_details');
 const fields=[['Delivery reference',result.reference||status.reference],['Recorded status',status.status],['Overdue',typeof status.overdue==='boolean'?(status.overdue?'Yes':'No'):null],['On schedule',typeof status.on_schedule==='boolean'?(status.on_schedule?'Yes':'No'):null],['Expected delivery at',status.expected_delivery_at],['Delivered at',status.delivered_at],['Observed at',status.observed_at],['Simulation as of',status.simulation_as_of]].filter(([,value])=>value!=null);
 return {...base,fields,findings:result.findings,note:evidence.note,trace,problemChecked:Boolean(problem),reason:problem?(problem.result?.reason||'No specific reason was recorded.'):null,events:problem?.result?.tracking_events||[],modelRequests:result.llm_requests};
}

// Resolve display citations only; never feed old records into a new model call.
// The runs endpoint authorizes one conversation. Group explicitly as defense in depth.
export function withCitationEvidence(runs) {
  const previous = new Map();
  return runs.map(run => {
    const key = run.conversation_id;
    const prior = key ? previous.get(key) || {} : {};
    const current = run.evidence || {};
    // Lab IDs repeat across runs: resolve them only against this answer's saved evidence.
    const demo = run.metrics?.rag_demo;
    const lab = {};
    for (const passage of demo?.passages || []) {
      if (!/^passage-\d+$/.test(passage.id)) continue;
      lab[`evidence-rag-${passage.id}`] = {type:'documents',
        citation_label:`View ${passage.id}`, policy_version:passage.version || demo.indexed_version,
        chunks:[{...passage, title:passage.id}]};
    }
    if (demo?.order) lab['evidence-rag-order-record'] = {type:'query',
      citation_label:'View order records', columns:['field','value'],
      rows:Object.entries(demo.order).map(([field,value])=>({field,value}))};
    const result = {...run, citationEvidence: {...prior, ...current, ...lab}};
    if (key) previous.set(key, {...prior, ...Object.fromEntries(
      Object.entries(current).map(([handle, value]) => [handle, {...value,
        source_run_id: run.id, source_question: run.question}]))});
    return result;
  });
}

// Support canonical citations, existing Markdown links and older bare IDs.
// Only recorded evidence can become a source link.
export function formatEvidence(answer, evidence = {}) {
  const labLinked = answer.replace(/\[[^\]\n]*\]\([^\)\n]*\)|\[(passage-\d+|order-record)\]|\((passage-\d+|order-record)\)|\b(passage-\d+|order-record)\b/g, (match, bracketed, parenthesized, bare) => {
    const id = bracketed || parenthesized || bare;
    if (!id) return match;
    const handle = `evidence-rag-${id}`;
    return evidence[handle] ? `[${sourceLabel(evidence[handle])}](#${handle})` : '[Source unavailable]';
  });
  return labLinked.replace(/\[[^\]\n]*\]\([^\)\n]*\)|\[(?:evidence:\s*)?(evidence-[a-f0-9]+|[a-f0-9]{8,})\]|\b(evidence-[a-f0-9]+)\b/g, (match, bracketed, bare) => {
    const linked = match.match(/\]\(#(evidence-[a-f0-9]+)\)$/)?.[1];
    const raw = linked || bracketed || bare;
    const handle = raw && (raw.startsWith('evidence-') ? raw : `evidence-${raw}`);
    if (!handle) return match;
    return evidence[handle] ? `[${sourceLabel(evidence[handle])}](#${handle})` : '[Source unavailable]';
  }).replace(/Evidence handle:\s*/gi, 'Source: ');
}
