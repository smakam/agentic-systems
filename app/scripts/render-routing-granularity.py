"""Validate and render the live routing pilot and explicit assistant grades. No model calls."""
import json,html,statistics,math,hashlib
from pathlib import Path
from collections import Counter
APP=Path(__file__).resolve().parents[1];OUT=APP/'results/routing-granularity-2026-09-30';s=json.loads((OUT/'results.json').read_text())
review=json.loads((OUT/'assistant-review.json').read_text()) if (OUT/'assistant-review.json').exists() else {'grades':{}}
checks=[];rows=[]
def percentile(xs,p):return sorted(xs)[max(0,math.ceil(len(xs)*p)-1)]
for r in s['results']:
 for idx,t in enumerate(r['turns'],1):
  calls=[c for c in s['calls'] if c.get('session')==r['session'] and c.get('policy')==r['policy'] and c.get('turn')==idx and 'usage' in c]
  candidate=[c for c in calls if c['kind']=='candidate'];assert candidate
  assert all(c['requested_model']==t['selected'] for c in candidate),'Model changed within question'
  assert all('usage' in c and 'error' not in c for c in calls),'Incomplete usage'
  assert sum(c['usage']['prompt_tokens'] for c in candidate)==t['run']['metrics']['input_tokens']
  assert sum(c['usage']['completion_tokens'] for c in candidate)==t['run']['metrics']['output_tokens']
  assert sum(c['cached_tokens'] for c in candidate)==t['run']['metrics']['cached_input_tokens']
  assert t['business_unchanged'] and t['run']['status']=='completed'
  checks.append({'key':r['key']+'-'+str(idx),'same_model_for_internal_calls':True,'usage_matches_agent':True,'business_unchanged':True})
 if r['policy']=='conversation' and r['turns']:assert len({t['selected'] for t in r['turns']})==1
# Same data at each turn across all policies, irrespective of preceding answers.
for sid in {r['session'] for r in s['results']}:
 for idx in range(3):
  hashes={r['turns'][idx]['fixture_hash'] for r in s['results'] if r['session']==sid and len(r['turns'])>idx};assert len(hashes)<=1,'Fixture drift across policies'
for policy in ['always_nano','always_gpt5','conversation','question']:
 records=[r for r in s['results'] if r['policy']==policy];turns=[(r['key']+'-'+str(i+1),t) for r in records for i,t in enumerate(r['turns'])];calls=[c for c in s['calls'] if c.get('policy')==policy and 'usage' in c]
 if not turns:continue
 grades=Counter(review['grades'].get(k,{}).get('grade','pending') for k,t in turns)
 agent=[c for c in calls if c['kind']=='candidate'];classifier=[c for c in calls if c['kind']=='classifier']
 input_tokens=sum(c['usage']['prompt_tokens'] for c in agent);cached=sum(c['cached_tokens'] for c in agent);cost=sum(c['cached_price_usd'] for c in calls);lat=[t['end_to_end_seconds'] for k,t in turns]
 switches=sum(sum(a['selected']!=b['selected'] for a,b in zip(r['turns'],r['turns'][1:])) for r in records)
 rows.append({'policy':policy,'turns':len(turns),'grades':dict(grades),'fully_correct_percent':100*grades['correct']/len(turns) if not grades['pending'] else None,'sessions_all_correct':sum(len(r['turns'])==3 and all(review['grades'].get(r['key']+'-'+str(i+1),{}).get('grade')=='correct' for i in range(3)) for r in records),'full_price_usd':sum(c['full_price_usd'] for c in calls),'cached_price_usd':cost,'classifier_cost_usd':sum(c['cached_price_usd'] for c in classifier),'classifier_calls':len(classifier),'candidate_calls':len(agent),'embedding_calls':sum(c['kind']=='embedding' for c in calls),'cached_input_tokens':cached,'input_tokens':input_tokens,'cached_token_fraction':cached/input_tokens if input_tokens else 0,'requests_with_cached_tokens':sum(c['cached_tokens']>0 for c in agent),'selected_turns':dict(Counter(t['selected'] for k,t in turns)),'model_switches':switches,'p50_seconds':statistics.median(lat),'p95_seconds':percentile(lat,.95),'cost_per_correct':cost/grades['correct'] if grades['correct'] and not grades['pending'] else None})
base=next((p['cached_price_usd'] for p in rows if p['policy']=='always_gpt5'),None)
for p in rows:p['saving_vs_live_gpt5_percent']=100*(1-p['cached_price_usd']/base) if base else None
complete=len(checks)==72 and len(rows)==4 and all(p['turns']==18 for p in rows)
summary={'status':review.get('status',s['status']),'complete':complete,'policies':rows,'total_full_price_usd':sum(c.get('full_price_usd',0) for c in s['calls']),'total_cached_price_usd':sum(c.get('cached_price_usd',0) for c in s['calls']),'review_provenance':'Assistant review complete; user accepted the three previously flagged partial grades. Other grades remain assistant-reviewed. No paid LLM judge.','flagged_reviews':{k:v for k,v in review['grades'].items() if v.get('needs_user_review')},'unpriced_failed_attempts':[c for c in s['calls'] if 'usage' not in c],'scope':'One pass, six conversations x three turns x four policies. Natural shared cache; no cold-start control. No causal switch penalty or statistical superiority claim.'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2));(OUT/'validation.json').write_text(json.dumps({'complete':complete,'validated_turns':len(checks),'fixture_consistency':True,'checks':checks},indent=2))
lines=['# Live routing granularity pilot — September 30, 2026','',summary['scope'],'',summary['review_provenance'],'','| Policy | Correct / partial / incorrect | Fully correct | Cache-adjusted cost | Savings vs fixed GPT-5 | Full-price cost | p50 / p95 seconds | Cached input fraction | Switches |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
for p in rows:
 g=p['grades'];quality='pending' if p['fully_correct_percent'] is None else f"{p['fully_correct_percent']:.1f}%"
 lines.append(f"| {p['policy']} | {g.get('correct',0)} / {g.get('partial',0)} / {g.get('incorrect',0)} | {quality} | ${p['cached_price_usd']:.6f} | {p['saving_vs_live_gpt5_percent']:.1f}% | ${p['full_price_usd']:.6f} | {p['p50_seconds']:.1f} / {p['p95_seconds']:.1f} | {p['cached_token_fraction']:.1%} | {p['model_switches']} |")
lines+=['','Savings = 100 × (1 − policy cache-adjusted cost / fixed GPT-5 cache-adjusted cost), for the same 18 turns. Costs include candidate calls, classifier calls and retrieval embeddings. Cached prices are reconstructed from reported usage and frozen rates, not an invoice. Reasoning output tokens are included in completion tokens. No paid judge calls.','',f"Total new live-run estimate: ${summary['total_cached_price_usd']:.6f} cache-adjusted; ${summary['total_full_price_usd']:.6f} at full input prices.",'','## Interpretation boundaries','','- OpenAI credit exhaustion interrupted S2 conversation turn 2. Its rejected attempt and exact prior session were preserved; only that question was retried after user funding. No completed answers were regenerated. The funding pause is excluded from answer latency; cache warmth may differ after the interruption. One rejected request has no usage, so its charge is unverified.', '- Same agent, prompt, tools and bounded conversation history; app-level routing chooses one model before each question. Every internal model call for that question uses the chosen model. Production app unchanged.','- Conversation policy pins first decision; question policy includes the actual prior conversation when reclassifying. Classifier prompt is the existing frozen domain-aware nano prompt. No gold, future questions or oracle rows enter the classifier.','- Policy order randomized with seed 930. Prior conversation content can differ because each policy generates its own answers. The experiment compares whole policies; it cannot isolate a pure cache-switch penalty.','- Provider caches may already be warm across sessions/arms. Cache fraction is descriptive. P95 uses nearest rank over only 18 turns per arm and is not a stable production estimate.','- The six conversations are new multi-turn scripts over known fixtures, not independent held-out validation. One pass cannot separate every stochastic difference from policy effects.','- Correctness is assistant-reviewed against frozen expected facts; citation and source freshness issues are recorded separately unless they change material answer correctness.','- No new Langfuse dataset upload was performed. Ordinary support-investigation telemetry runs through the existing app instrumentation.','', '## Reproduce','','Run the fixture dry-run first, then the live runner; both require market_eval connections and use the evaluation virtual key. See eval/routing-final-v1/README.md. Preserve this results directory; use a new version/date for altered input or repetitions.','', '## Flagged review decisions','']
for k,v in summary['flagged_reviews'].items():lines.append('- '+k+': '+v['reason'])
if not summary['flagged_reviews']:lines.append('None pending. The user accepted the three S3 turn-3 partial grades; scores are unchanged.')
lines += ['', '## Presentation issues separate from correctness', ''] + ['- '+n for n in review.get('presentation_notes',[])]
cache_rows=[]
for policy in ['always_nano','always_gpt5','conversation','question']:
 for model in ['eval-nano','eval-5']:
  calls=[c for c in s['calls'] if c.get('policy')==policy and c.get('kind')=='candidate' and c.get('requested_model')==model and 'usage' in c]
  if not calls:continue
  total=sum(c['usage']['prompt_tokens'] for c in calls);cached=sum(c['cached_tokens'] for c in calls)
  assert all(c['cached_tokens']==c['usage']['prompt_tokens_details']['cached_tokens'] for c in calls)
  cache_rows.append({'policy':policy,'model':model,'calls':len(calls),'input_tokens':total,'cached_tokens':cached,'cached_fraction':cached/total})
for policy in rows:
 subset=[r for r in cache_rows if r['policy']==policy['policy']]
 assert sum(r['input_tokens'] for r in subset)==policy['input_tokens']
 assert sum(r['cached_tokens'] for r in subset)==policy['cached_input_tokens']
cache_notes='Candidate answer-model calls only; classifier and embedding calls excluded to match the existing cached-input metric. Percentages are token-weighted, not averages of call percentages. One rejected request had no usage and is excluded. Repeated tokens across requests are counted each time, as billed input.'
cache_interpretation='GPT-5 had a higher cached-input fraction than nano within both routing policies. However, question-level routing had a higher fraction within EACH model than conversation-level routing: nano 51.5% vs 47.8%, GPT-5 66.9% vs 61.6%. GPT-5 supplied 41.5% of question-policy input tokens versus 44.6% of conversation-policy input tokens, so a larger GPT-5 share does not explain the question policy advantage. The per-model cache fractions account for the observed aggregate difference; these data do not establish whether prompt histories, prior cache warmth, run order or the funding pause caused it.'
(OUT/'cache-by-model.json').write_text(json.dumps({'rows':cache_rows,'scope':cache_notes,'interpretation':cache_interpretation},indent=2)+'\n')
lines += ['', '## Cached input by answer model', '', '| Policy | Model | Calls | Input tokens | Cached input tokens | Cached fraction |','|---|---|---:|---:|---:|---:|']
for r in cache_rows:lines.append(f"| {r['policy']} | {r['model']} | {r['calls']} | {r['input_tokens']:,} | {r['cached_tokens']:,} | {r['cached_fraction']:.1%} |")
lines += ['',cache_notes,'',cache_interpretation]
scoring_note='The same six conversation scenarios were run under each of four policies. Each conversation has three user questions: 18 answers per policy, 72 answers across the experiment. A conversation is fully correct only when all three answers are graded correct; otherwise it is not fully correct. This is an all-turns-pass measure, not a separate holistic conversation grade.'
conclusion='Neither routing policy demonstrated a compelling quality advantage over fixed nano in this pilot: all three completed 4/6 conversations fully correctly, while routing cost about nine times as much. Routing reduced incorrect individual answers from two to one, so outcomes are not identical. Fixed GPT-5 achieved 6/6 at higher cost. Conversation and question routing tied on these quality measures; one small pass does not establish a winner.'
primary=['## Primary result: whole conversations', '', scoring_note, '', '| Policy | Fully correct conversations | Conversation success | Total cost for six conversations (cache-adjusted) | Savings vs fixed GPT-5 |','|---|---:|---:|---:|---:|']
for p in rows:
 records=[r for r in s['results'] if r['policy']==p['policy']]
 assert len(records)==6 and all(len(r['turns'])==3 for r in records)
 assert p['sessions_all_correct']==sum(all(review['grades'][r['key']+'-'+str(i+1)]['grade']=='correct' for i in range(3)) for r in records)
 primary.append(f"| {p['policy']} | {p['sessions_all_correct']} / 6 | {p['sessions_all_correct']/6:.1%} | ${p['cached_price_usd']:.6f} | {p['saving_vs_live_gpt5_percent']:.1f}% |")
primary += ['',conclusion,'','## Supporting detail: individual answers and timing','','Answer counts below are out of 18 per policy. Latency is per answer; costs cover all six conversations.','']
idx=next(i for i,line in enumerate(lines) if line.startswith('| Policy |'))
lines[idx:idx]=primary
lines=[line.replace('| Correct / partial / incorrect | Fully correct |','| Answers: correct / partial / incorrect (18) | Fully correct answers |') for line in lines]
summary['scoring_units']={'conversations_per_policy':6,'answers_per_conversation':3,'answers_per_policy':18,'answers_total':72,'primary':'All three answers correct','supporting':'Individual answer correctness'}
summary['conclusion']=conclusion
(OUT/'summary.json').write_text(json.dumps(summary,indent=2))
editorial_note='Purpose: demonstrate how to evaluate model choice, classifier policy and routing granularity for a particular application, not prescribe a winner. These small diagnostic samples illustrate the decision process; representative fresh cases and repetitions are needed before a deployment recommendation. See the user-confirmed editorial framing in EVALUATION-SPEC.md and milestone M21.'
lines[2:2]=[editorial_note,'']
(OUT/'REPORT.md').write_text('\n'.join(lines)+'\n')
e=html.escape
header='<tr><th>Policy</th><th>Answers: correct / partial / incorrect (18)</th><th>Fully correct answers</th><th>Cache-adjusted cost</th><th>Savings vs fixed GPT-5</th><th>Full-price cost</th><th>p50 / p95</th><th>Cached input</th><th>Switches</th></tr>'
tr=''
for p in rows:
 g=p['grades'];vals=[p['policy'],f"{g.get('correct',0)} / {g.get('partial',0)} / {g.get('incorrect',0)}",'pending' if p['fully_correct_percent'] is None else f"{p['fully_correct_percent']:.1f}%",f"${p['cached_price_usd']:.6f}",f"{p['saving_vs_live_gpt5_percent']:.1f}%",f"${p['full_price_usd']:.6f}",f"{p['p50_seconds']:.1f}s / {p['p95_seconds']:.1f}s",f"{p['cached_token_fraction']:.1%}",p['model_switches']];tr+='<tr>'+''.join('<td>'+e(str(x))+'</td>' for x in vals)+'</tr>'
primary_html='<h2>Primary result: whole conversations</h2><p>'+e(scoring_note)+'</p><table><tr><th>Policy</th><th>Fully correct conversations</th><th>Conversation success</th><th>Total cost for six conversations (cache-adjusted)</th><th>Savings vs fixed GPT-5</th></tr>'
for p in rows:
 primary_html+='<tr>'+''.join('<td>'+e(str(v))+'</td>' for v in [p['policy'],str(p['sessions_all_correct'])+' / 6',f"{p['sessions_all_correct']/6:.1%}",f"${p['cached_price_usd']:.6f}",f"{p['saving_vs_live_gpt5_percent']:.1f}%"])+'</tr>'
primary_html+='</table><p>'+e(conclusion)+'</p><h2>Supporting detail: individual answers and timing</h2>'
cache_html='<h2>Cached input by answer model</h2><p>'+e(cache_notes)+'</p><table><tr><th>Policy</th><th>Model</th><th>Calls</th><th>Input tokens</th><th>Cached input tokens</th><th>Cached fraction</th></tr>'
for r in cache_rows:
 cache_html+='<tr>'+''.join('<td>'+e(str(v))+'</td>' for v in [r['policy'],r['model'],r['calls'],f"{r['input_tokens']:,}",f"{r['cached_tokens']:,}",f"{r['cached_fraction']:.1%}"])+'</tr>'
cache_html+='</table><p>'+e(cache_interpretation)+'</p>'
cards=''
for r in s['results']:
 cards+='<h2>'+e(r['key'])+'</h2>'
 for i,t in enumerate(r['turns'],1):
  k=r['key']+'-'+str(i);g=review['grades'].get(k,{'grade':'pending','reason':'Not yet reviewed'})
  cards+='<article><h3>Turn '+str(i)+' · '+e(t['selected'])+' · '+e(g['grade'])+'</h3><p>'+e(t['question'])+'</p><div class="columns"><section><h4>Expected text</h4><p>'+e(t['expected']['expected_text'])+'</p><h4>Expected records</h4><pre>'+e(json.dumps(t['expected']['expected_records'],indent=2))+'</pre></section><section><h4>Actual model text</h4><pre>'+e(t['run']['answer'])+'</pre></section></div><p><b>Assistant assessment:</b> '+e(g['reason'])+'</p><details><summary>Routing decision, timing and raw evidence</summary><pre>'+e(json.dumps({'decision':t['decision'],'end_to_end_seconds':t['end_to_end_seconds'],'metrics':t['run']['metrics'],'retrieved_evidence':t['run']['evidence']},indent=2))+'</pre></details></article>'
(OUT/'comparison.html').write_text('<!doctype html><meta charset="utf-8"><title>Routing granularity pilot</title><style>body{font:16px system-ui;max-width:1300px;margin:32px auto;padding:20px;color:#19253a}table{width:100%;border-collapse:collapse}td,th{padding:10px;border-bottom:1px solid #cdd;text-align:left}article{border:1px solid #ccd;border-radius:10px;padding:18px;margin:16px 0}.columns{display:grid;grid-template-columns:1fr 1fr;gap:24px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f6fa;padding:12px;font:14px ui-monospace}summary{cursor:pointer;padding:10px}@media(max-width:800px){.columns{grid-template-columns:1fr}}</style><h1>Conversation-level vs question-level routing</h1><p><strong>How to read these results:</strong> '+e(editorial_note)+'</p><p>Six conversation scenarios × three questions × four policies = 72 answers · one pass · assistant-reviewed, no paid judge</p>'+primary_html+'<table>'+header+tr+'</table><p>End-to-end latency includes classification. Costs include classification and retrieval embeddings. Savings compare cache-adjusted costs with fixed GPT-5 for the same 18 turns. The supporting quality counts are per answer (18 per policy); the primary score is per conversation (six per policy). This is a diagnostic sample.</p><details><summary>Methods and limitations</summary><pre>'+e('\n'.join(lines))+'</pre></details>'+cache_html+cards)
print('Validated/rendered',len(checks),'turns')
