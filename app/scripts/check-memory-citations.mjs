// Grade source resolution using the same implementation as the Support UI.
// Run after a memory suite: node scripts/check-memory-citations.mjs <results-dir>
import fs from 'node:fs';
import path from 'node:path';
import {formatEvidence, withCitationEvidence} from '../frontend/src/evidence.js';

const dir = process.argv[2];
if (!dir) throw new Error('Provide the memory results directory');
const rows = JSON.parse(fs.readFileSync(path.join(dir, 'results.json'), 'utf8'));
const runs = withCitationEvidence(rows.map(row => ({...row.result,
  conversation_id: row.conversation_id, question: row.question})));
const checks = rows.map((row, index) => {
  const answer = row.result.answer;
  const rendered = formatEvidence(answer, runs[index].citationEvidence);
  const shortened = [...answer.matchAll(/\[evidence:([a-f0-9]{8,})\]/g)].map(match => match[1]);
  return {question_number: index + 1, scenario: row.scenario,
    source_resolution: rendered.includes('[Source unavailable]') ? 'fail' : 'pass',
    raw_citation_format: shortened.length ? 'noncanonical' : 'canonical_or_no_citations',
    shortened_handles: shortened, rendered_answer: rendered};
});
fs.writeFileSync(path.join(dir, 'citation-checks.json'), JSON.stringify(checks, null, 2) + '\n');
console.log(JSON.stringify({questions: checks.length,
  source_resolution_failures: checks.filter(check => check.source_resolution === 'fail').length,
  noncanonical_answers: checks.filter(check => check.shortened_handles.length).map(check => check.question_number)}, null, 2));
if (checks.some(check => check.source_resolution === 'fail')) process.exitCode = 1;
