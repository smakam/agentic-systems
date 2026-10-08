#!/usr/bin/env python3
"""Render a local review page; human decisions are never filled automatically."""
import json,sys,html
from pathlib import Path
p=Path(sys.argv[1]);data=json.loads(p.read_text());rows=[]
references=json.loads((Path(__file__).resolve().parents[1]/'eval/review-references.json').read_text())['cases']
def reference_for(record):
 ref=json.loads(json.dumps(references[record['case']['id']]))
 for group in ('expected_answers','evidence_requirements'):
  for i,value in enumerate(ref[group]):
   for alias,values in record.get('aliases',{}).items():
    for field,actual in values.items():value=value.replace('{'+alias+'.'+field+'}',str(actual))
   if '{' in value:raise ValueError('Unresolved reference for '+record['key'])
   ref[group][i]=value
 return ref
for r in data['results']:
 judge=r.get('judge',{});grade=judge.get('grade') or {};ts=r['turns']
 rows.append({'key':r['key'],'case':r['case']['id'],'model':r['model'],'question':r['case']['question'],
 'reference':reference_for(r),'aliases':r.get('aliases',{}),'gold':r['case']['gold'],'turns':[{'question':t['question'],'answer':t['run']['answer'],'checks':t['deterministic'],'evidence':t['run']['evidence'],'tool_attempts':t['run']['metrics'].get('tool_attempts',[]),'status':t['run']['status']} for t in ts],
 'judge':grade,'human':r['human_review'],'seconds':round(sum(t['run']['metrics']['elapsed_seconds'] for t in ts),1),
 'candidate_cost':sum(t['run']['metrics'].get('estimated_model_cost_usd',0) for t in ts),'judge_cost':judge.get('estimated_usd',0)})
encoded=json.dumps(rows).replace('<','\\u003c')
page='''<!doctype html><html><head><meta charset="utf-8"><title>Marketplace evaluation review</title><style>
body{font:16px system-ui;max-width:1150px;margin:32px auto;padding:0 20px;color:#172331;background:#f4f6f8}h1{font-size:28px}article{background:white;border:1px solid #d3dce3;border-radius:10px;margin:16px 0;padding:20px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:14px ui-monospace;max-height:450px;overflow:auto}button,select,input{padding:8px;margin:4px}label{display:inline-block}summary{cursor:pointer;margin:10px 0}aside{background:#fff4ce;padding:14px} .gold{border-left:4px solid #1a796f;padding-left:12px}.answer{white-space:pre-wrap;line-height:1.5}.record-grid{display:grid;grid-template-columns:1fr 1fr;gap:16px}.records{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #d3dce3;padding:8px;text-align:left;overflow-wrap:anywhere}th{background:#edf3f5}.comparison{background:#f7fafb;padding:16px;margin:16px 0;border-radius:8px}.verdict{font-weight:700}.pass{color:#17633c}.fail{color:#a12b24}@media(max-width:800px){.record-grid{grid-template-columns:1fr}}nav{position:sticky;top:0;background:#f4f6f8;padding:10px 0;border-bottom:1px solid #ccd}textarea{width:96%;height:65px}small{color:#536170}.judge-heading{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}.judge-heading::before{content:"▸"}.judge-panel[open] .judge-heading::before{content:"▾"}.judge-title{flex:1}.judge-score{font-size:14px;border:1px solid #ccd;padding:6px 10px;border-radius:6px;background:#f4f6f8}.judge-score.partial{color:#754c00;background:#fff4ce}</style></head><body>
<h1>Marketplace model comparison</h1><aside>Automated results are provisional. Review every answer against the gold facts and evidence. Blank human decisions mean not reviewed. Saving downloads a review file; it does not change the benchmark or send scores to Langfuse.</aside>
<p id="stats"></p><nav><select id="filter"><option value="all">All answers</option><option value="pending">Human review pending</option><option value="failed">Judge score below 2 / unavailable</option></select><button id="save">Download human review JSON</button><span id="count"></span></nav><main id="list"></main>
<script>const rows=ROWS;const storageKey='market-eval-review-'+EXPERIMENT;let reviews={};try{reviews=JSON.parse(localStorage.getItem(storageKey)||'{}')}catch(e){};
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const details=(title,value)=>`<details><summary>${esc(title)}</summary><pre>${esc(JSON.stringify(value,null,2))}</pre></details>`;
const judgeAssessment=grade=>{
 const score=grade.correctness;
 const labels={0:'Incorrect',1:'Partially correct',2:'Fully correct'};
 const known=Number.isInteger(score)&&score>=0&&score<=2;
 const label=known?`Correctness ${score}/2 · ${labels[score]}`:'Not graded';
 const style=known?(score===2?'pass':score===1?'partial':'fail'):'';
 return `<details class="judge-panel"><summary class="judge-heading"><span class="judge-title">Provisional LLM judge assessment</span><span class="judge-score ${style}">${esc(label)}${grade.uncertain?' · Uncertain':''}</span></summary><p><small>Saved Claude assessment, not a human-reviewed score. Correctness: 0 = incorrect, 1 = partial, 2 = fully correct. ${Number.isInteger(grade.readability)?`Readability: ${grade.readability}/2.`:''}</small></p>${grade.rationale?`<p>${esc(grade.rationale)}</p>`:''}<pre>${esc(JSON.stringify(grade,null,2))}</pre></details>`;
};
const recordTable=records=>{
 if(!Array.isArray(records))return '<p>No comparable records available.</p>';
 if(!records.length)return '<p><b>No rows returned (empty result).</b></p>';
 const columns=[...new Set(records.flatMap(row=>Object.keys(row)))];
 return `<div class="records"><table><thead><tr>${columns.map(c=>`<th>${esc(c.replaceAll('_',' '))}</th>`).join('')}</tr></thead><tbody>${records.map(row=>`<tr>${columns.map(c=>`<td>${esc(row[c]===null?'null':typeof row[c]==='object'?JSON.stringify(row[c]):row[c])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
};
const evidenceRequirements=r=>`<details><summary>Evidence requirements — what should support the answer</summary><ul>${r.reference.evidence_requirements.map(f=>`<li>${esc(f)}</li>`).join('')}</ul><p><small>The saved judge grades use the original rubric below.</small></p>${details('Original grading criteria (audit reference)',r.gold)}</details>`;
const expectedView=(r,t,i)=>{
 const d=t.checks.structured_gold_details;
 const notApplicable=['10','11','30'].includes(r.case)||(r.case==='27'&&i===0);
 const missing=notApplicable?'Not applicable: this turn requires a policy answer, clarification, or permission response rather than a fixed set of database rows.':'Not yet defined for this turn. The expected text is available, but an explicit structured-record comparison has not been implemented. This is not an automatic pass.';
 return `<section class="gold"><h4>Expected answer</h4><h5>Expected text response</h5><p>${esc(r.reference.expected_answers[i]||r.reference.expected_answers[0])}</p><p><small>Equivalent wording is acceptable.</small></p><h5>Expected structured records</h5>${d?.expected?`<p><small>${esc(d.scope)}</small></p>${recordTable(d.expected)}`:`<p>${missing}</p>`}</section>`;
};
const actualRecords=t=>{
 const comparisons=t.checks.structured_gold_details?.comparisons||[];
 return `<section><h5>Agent’s structured output — retrieved records</h5><p><small>Selected fields or calculated totals from tool results, not a separate model-generated JSON answer.</small></p>${comparisons.length?comparisons.map((c,i)=>`<section><p><b>Retrieved result ${i+1}</b></p>${recordTable(c.actual)}${details('Source query and full records',t.evidence[c.handle]||{handle:c.handle})}</section>`).join(''):'<p>No records have been selected for a structured comparison. See the full retrieved evidence below for any tool results.</p>'}</section>`;
};
const comparisonView=t=>{
 const d=t.checks.structured_gold_details;
 if(!d||d.expected===null||d.expected===undefined)return `<section class="comparison"><h4>Record comparison — Not evaluated</h4><p>No structured expectation is defined for this turn; this is not a pass.</p></section>`;
 const label=d.passed===true?'Match':d.passed===false?'Mismatch':'Not assessable';
 return `<section class="comparison"><h4>Record comparison — <span class="verdict ${d.passed===true?'pass':d.passed===false?'fail':''}">${label}</span></h4><p>${esc(d.scope)}</p>${d.comparisons.map((c,i)=>`<section><p><b>Retrieved result ${i+1}: ${c.passed===true?'Matches the expected records':c.passed===false?'Does not match the expected records':'Cannot be assessed'}</b></p>${c.reason?`<p>${esc(c.reason)}</p>`:''}${c.missing?.length?`<p>Missing expected records:</p>${recordTable(c.missing)}`:''}${c.unexpected?.length?`<p>Unexpected or differing records:</p>${recordTable(c.unexpected)}`:''}</section>`).join('')}<p><small>This checks the records above, not the correctness of the model’s text response.</small></p>${details('Technical comparison details',d)}</section>`;
};
function render(){const filter=document.querySelector('#filter').value;document.querySelector('#list').innerHTML=rows.filter(r=>filter==='all'||(filter==='pending'&&!reviews[r.key]?.decision)||(filter==='failed'&&r.judge.correctness!==2)).map(r=>{const h=reviews[r.key]||{};return `<article><h2>Case ${r.case} · ${esc(r.model)}</h2><small>${r.seconds}s · candidate estimate $${r.candidate_cost.toFixed(4)} · judge $${r.judge_cost.toFixed(4)}</small>${r.turns.map((t,i)=>`<h3>Turn ${i+1} — User question</h3><p>${esc(t.question)}</p><div class="record-grid">${expectedView(r,t,i)}<section><h4>Actual result</h4><h5>Model’s text response</h5><div class="answer">${esc(t.answer)}</div>${actualRecords(t)}</section></div>${comparisonView(t)}${details('Other automated checks',t.checks.checks)}${details('Full retrieved evidence — including intermediate lookups',t.evidence)}${details('Tool attempts, including errors',t.tool_attempts)}`).join('')}${evidenceRequirements(r)}${judgeAssessment(r.judge)}<label>Your answer grade <select data-key="${r.key}" data-field="decision"><option value="">Not reviewed</option>${['correct','partially_correct','incorrect'].map(v=>`<option ${h.decision===v?'selected':''}>${v}</option>`).join('')}</select></label><label>Agree with judge? <select data-key="${r.key}" data-field="judge_agreement"><option value="">Not reviewed</option>${['yes','no','uncertain'].map(v=>`<option ${h.judge_agreement===v?'selected':''}>${v}</option>`).join('')}</select></label><label>Structured checks valid? <select data-key="${r.key}" data-field="checks_agreement"><option value="">Not reviewed</option>${['yes','no','not_applicable','uncertain'].map(v=>`<option ${h.checks_agreement===v?'selected':''}>${v}</option>`).join('')}</select></label><textarea placeholder="Review notes / corrected facts / suspected cause" data-key="${r.key}" data-field="notes">${esc(h.notes||'')}</textarea></article>`}).join('');document.querySelector('#count').textContent=Object.values(reviews).filter(x=>x.decision).length+' / '+rows.length+' reviewed';}
document.querySelector('#list').addEventListener('change',e=>{let {key,field}=e.target.dataset;if(!key)return;reviews[key]={...(reviews[key]||{}),[field]:e.target.value};localStorage.setItem(storageKey,JSON.stringify(reviews));document.querySelector('#count').textContent=Object.values(reviews).filter(x=>x.decision).length+' / '+rows.length+' reviewed';});document.querySelector('#filter').onchange=render;
document.querySelector('#save').onclick=()=>{const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([JSON.stringify({experiment:EXPERIMENT,reviewed_at:new Date().toISOString(),reviews},null,2)],{type:'application/json'}));a.download='human-review.json';a.click();URL.revokeObjectURL(a.href)};
document.querySelector('#stats').textContent=rows.length+' scenario answers · total recorded estimate $'+TOTAL+' · provider caching discounts and unreported failed-call charges are not reconciled.';render();</script></body></html>'''.replace('ROWS',encoded).replace('EXPERIMENT',json.dumps(data['experiment'])).replace('TOTAL',json.dumps(f"{data['cost_estimate_usd']:.4f}"))
(p.parent/'review.html').write_text(page)
summary=['# Automated model comparison — provisional','',f"Experiment: {data['experiment']}. Status: {data['status']}.",'','Human review is pending; judge scores are not final accuracy.','', '| Model | Cases | Judge fully correct | Partial | Incorrect | Judge unavailable | Estimated candidate cost |','|---|---:|---:|---:|---:|---:|---:|']
for model in sorted({r['model'] for r in rows}):
 rs=[r for r in rows if r['model']==model];scores=[r['judge'].get('correctness') for r in rs]
 summary.append(f"| {model} | {len(rs)} | {scores.count(2)} | {scores.count(1)} | {scores.count(0)} | {scores.count(None)} | ${sum(r['candidate_cost'] for r in rs):.4f} |")
summary+=['',f"Total recorded estimate including judge and preflight: ${data['cost_estimate_usd']:.4f}. Embedding and any unreported failed-call charges excluded; not an invoice.",'','[Open review page](review.html). Full evidence and tool attempts are in results.json. Human decisions are blank until a person records them.']
(p.parent/'SUMMARY.md').write_text('\n'.join(summary)+'\n');print(p.parent/'review.html')
