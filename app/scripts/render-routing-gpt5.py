"""Summarize routing selections against frozen saved grades; no API calls."""
import json,html,hashlib
from collections import Counter
from pathlib import Path
APP=Path(__file__).resolve().parents[1];OUT=APP/'results/routing-gpt5-llm-jev-2026-09-29'
state=json.loads((OUT/'decisions.json').read_text());auto=json.loads((OUT/'openrouter-decisions.json').read_text());source=APP/'results/core18-gpt5-v2-2026-09-29/comparison.json';data=json.loads(source.read_text());pairs={}
assert hashlib.sha256(source.read_bytes()).hexdigest()==state['manifest']['source_sha256']
for r in data['rows']:pairs.setdefault(r['case'],{})[r['model']]=r
policies={'Always nano':[{'case':c,'selected':'eval-nano'} for c in sorted(pairs)],'Always GPT-5':[{'case':c,'selected':'eval-5'} for c in sorted(pairs)],'Nano LLM classifier':state['llm'],'JEV classifier':state['jev'],'OpenRouter Auto (low)':auto['decisions']}
summary=[];details={}
for name,ds in policies.items():
 if len(ds)!=18:continue
 rows=[pairs[x['case']][x['selected']] for x in ds];counts=Counter(r['review']['grade'] for r in rows);overhead=sum(x.get('cost',0) for x in ds);candidate=sum(r['cost'] for r in rows)
 summary.append({'policy':name,'correct':counts['correct'],'partial':counts['partially_correct'],'incorrect':counts['incorrect'],'fully_correct_percent':100*counts['correct']/18,'candidate_replay_cost':candidate,'routing_overhead':overhead,'replay_total_cost':candidate+overhead,'nano_selections':sum(x['selected']=='eval-nano' for x in ds),'gpt5_selections':sum(x['selected']=='eval-5' for x in ds)})
 details[name]=[{'case':x['case'],'selected':x['selected'],'grade':pairs[x['case']][x['selected']]['review']['grade'],'decision':x} for x in ds]
base=next(s for s in summary if s['policy']=='Always GPT-5')['replay_total_cost']
for s in summary:s['savings_vs_gpt5_percent']=100*(1-s['replay_total_cost']/base)
new_spend=sum(x['cost'] for x in state['llm']+state['jev'])+sum(x['probe_cost'] for x in auto['decisions'])
report={'source_hash':state['manifest']['source_sha256'],'policies':summary,'new_classifier_and_probe_spend':new_spend,'openrouter_probe_spend':sum(x['probe_cost'] for x in auto['decisions']),'details':details,'errors':state['errors']+auto['errors']}
(OUT/'comparison.json').write_text(json.dumps(report,indent=2))
lines=['# Offline routing: nano / GPT-5','', '| Policy | Correct | Partial | Incorrect | Fully correct | Replay cost | Savings vs GPT-5 | Nano / GPT-5 |','|---|---:|---:|---:|---:|---:|---:|---:|']
for s in summary:lines.append(f"| {s['policy']} | {s['correct']} | {s['partial']} | {s['incorrect']} | {s['fully_correct_percent']:.1f}% | ${s['replay_total_cost']:.5f} | {s['savings_vs_gpt5_percent']:.1f}% | {s['nano_selections']} / {s['gpt5_selections']} |")
lines+=['',f'New classifier/probe spend: ${new_spend:.6f}. OpenRouter capped probe spend ${report["openrouter_probe_spend"]:.6f} is experimental observation cost, excluded from its deployment replay estimate. Auto Router has no separate routing surcharge. Other totals reuse saved uncached candidate list-rate estimates and add classifier overhead; they are not new spending or invoices. Embeddings, judge and infrastructure excluded. JEV overhead is API-reported usage cost; nano classifier overhead is an uncached estimate.','', '## What this tests','', 'Opening question selects one model for the whole saved session, including follow-ups. All grades and answers come from the current versioned nano/GPT-5 comparison, with its mixed human/assistant provenance and accepted adjudications. No answer or judge reruns. LLM uses nano via local LiteLLM and the prior domain-aware v2 rubric. JEV uses TypeSafe Choice through OpenRouter Decisions with equivalent tier descriptions and the same domain guidance; it does not generate a prose reason. These are custom offline classifiers, not native LiteLLM AutoRouter executions.','', 'OpenRouter Auto uses native market-based routing, low cost tier, allowed_models restricted exactly to openai/gpt-5-nano and openai/gpt-5. It sees the same opening question and generic application/tool/ontology context, not the hand-written tier classifier instructions (which would turn its task into classification). Requests enable routing metadata and allow only16 completion tokens. Generated probe content is not evaluated. Selected model is mapped to its saved answer. Metadata and actual returned model must be inspected for routing fallbacks. No unrestricted model is scored.','', '## Limitations','', 'Retrospective18-case working set, not held-out validation. One classifier sample per case. Generic v2 rules were written after earlier experiments. First-question routing cannot see later user turns or future database changes. OpenRouter market rankings change over time and cost-tier choice matters; these results are only for low and this two-model restriction. A capped completion probe may differ from a real agent request with tools and output requirements. End-to-end quality, latency, cache hit rates and per-call switching have not been measured. Native OpenRouter conversation affinity may switch models; replay explicitly pins the first selected model instead.','', '## Per-case decisions','', '| Case | LLM | JEV | OpenRouter | Nano grade | GPT-5 grade |','|---|---|---|---|---|---|']
for c in sorted(pairs):
 selects=[next((x['selected'] for x in ds if x['case']==c),'not available') for ds in [state['llm'],state['jev'],auto['decisions']]]
 lines.append('| '+' | '.join([c,*selects,pairs[c]['eval-nano']['review']['grade'],pairs[c]['eval-5']['review']['grade']])+' |')
lines+=['','## Sources','', '- [OpenRouter Auto Router documentation](https://openrouter.ai/docs/guides/routing/routers/auto-router)', '- [JEV Decisions API example](https://openrouter.ai/blog/insights/what-is-jev/)', '- [Source comparison](../core18-gpt5-v2-2026-09-29/comparison.html)', '- Raw requests, responses, classifier prompt, decision manifests and grade-source hash are archived in this folder.']
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
e=html.escape
body='<h1>Routing cost versus quality</h1><p>Offline replay of18 cases. One model pinned per whole session. Grades come from the saved nano/GPT-5 baseline.</p><table><tr><th>Policy</th><th>Correct / Partial / Incorrect</th><th>Fully correct</th><th>Replay cost</th><th>Savings</th><th>Nano / GPT-5</th></tr>'
for s in summary:body+=f'<tr><td>{e(s["policy"])}</td><td>{s["correct"]} / {s["partial"]} / {s["incorrect"]}</td><td>{s["fully_correct_percent"]:.1f}%</td><td>${s["replay_total_cost"]:.5f}</td><td>{s["savings_vs_gpt5_percent"]:.1f}%</td><td>{s["nano_selections"]} / {s["gpt5_selections"]}</td></tr>'
body+='</table><p>Costs above reuse saved candidate estimates, plus classification overhead. New experiment spend: $'+f'{new_spend:.6f}'+'</p><h2>Per-case selections and grades</h2>'
for c in sorted(pairs):
 body+=f'<article><h3>Case {c}</h3><p>'+e(pairs[c]['eval-nano']['turns'][0]['question'])+'</p>'
 for name,ds in details.items():
  r=next(x for x in ds if x['case']==c);body+='<p><b>'+e(name)+'</b>: '+e(r['selected'])+' → '+e(r['grade'])+'</p>'
 body+='</article>'
body+='<details><summary>Method, limitations and full report</summary><pre>'+e('\n'.join(lines))+'</pre></details>'
(OUT/'comparison.html').write_text('<!doctype html><meta charset="utf-8"><title>Routing comparison</title><style>body{font:16px system-ui;max-width:1200px;margin:40px auto;padding:20px;color:#182334;background:#f6f7fa}table{border-collapse:collapse;background:white}td,th{border:1px solid #ccd;padding:12px}article{background:white;padding:16px;margin:12px 0;border:1px solid #dde}pre{white-space:pre-wrap}summary{cursor:pointer}</style>'+body)
print(json.dumps({'policies':summary,'new_spend':new_spend},indent=2))
