export function sourceLabel(evidence) {
  if (!evidence) return 'Source unavailable';
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
    const result = {...run, citationEvidence: {...prior, ...current}};
    if (key) previous.set(key, {...prior, ...Object.fromEntries(
      Object.entries(current).map(([handle, value]) => [handle, {...value,
        source_run_id: run.id, source_question: run.question}]))});
    return result;
  });
}

// Support canonical citations, existing Markdown links and older bare IDs.
// Only recorded evidence can become a source link.
export function formatEvidence(answer, evidence = {}) {
  return answer.replace(/\[[^\]\n]*\]\([^\)\n]*\)|\[(?:evidence:\s*)?(evidence-[a-f0-9]+|[a-f0-9]{8,})\]|\b(evidence-[a-f0-9]+)\b/g, (match, bracketed, bare) => {
    const linked = match.match(/\]\(#(evidence-[a-f0-9]+)\)$/)?.[1];
    const raw = linked || bracketed || bare;
    const handle = raw && (raw.startsWith('evidence-') ? raw : `evidence-${raw}`);
    if (!handle) return match;
    return evidence[handle] ? `[${sourceLabel(evidence[handle])}](#${handle})` : '[Source unavailable]';
  }).replace(/Evidence handle:\s*/gi, 'Source: ');
}
