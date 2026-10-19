export function sourceLabel(evidence) {
  if (!evidence) return 'Source unavailable';
  if (evidence.citation_label) return evidence.citation_label;
  if (evidence.source_run_id) return `${sourceLabel({...evidence,source_run_id:null})} (earlier question)`;
  if (evidence.type === 'catalog') return 'View data definitions';
  if (evidence.type === 'documents') return 'View policy passages';
  if (evidence.type === 'query') return /\bevents\b/i.test(evidence.sql || '') ? 'View event timeline' : 'View database records';
  return 'View source';
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
  const labLinked = answer.replace(/\[[^\]\n]*\]\([^\)\n]*\)|\[(passage-\d+|order-record)\]/g, (match, id) => {
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
