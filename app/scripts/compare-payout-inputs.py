import json
from pathlib import Path
from marketplace.agent import lf
root=Path('/results');out=root/'payout-input-comparison-2026-09-29';out.mkdir(exist_ok=True)
selection=[('16-correct','payout-full-agent-repeat-2026-09-29','1-16-eval-54'),('16-incorrect','payout-v2-gpt54-2026-09-29','1-16-eval-54'),('17-correct','payout-v2-gpt54-2026-09-29','2-17-eval-54'),('17-incorrect','payout-v2-gpt54-2026-09-29','1-17-eval-54')]
for label,folder,key in selection:
 r=next(r for r in json.loads((root/folder/'results.json').read_text())['results'] if r['key']==key);t=r['turns'][0];tid=t['run']['metrics']['trace_id']
 obs=lf.api.observations.get_many(trace_id=tid,fields='core,io,model,usage,metadata',limit=100).model_dump(mode='json')
 (out/f'{label}-observations.json').write_text(json.dumps(obs,indent=2))
 generations=[g for g in obs['data'] if g['type']=='GENERATION'];final=max(generations,key=lambda g:g['startTime'])
 messages=json.loads(final['input']);answer=json.loads(final['output'])[0]['content'];assert answer==t['run']['answer']
 artifact={'label':label,'source':folder,'key':key,'trace_id':tid,'question':t['question'],'fixture_hash':r['fixture_hash'],'prompt_hash':t['run']['metrics']['prompt_hash'],'settings':final['modelParameters'],'messages':messages,'answer':answer,'generation_count':len(generations)}
 (out/f'{label}.json').write_text(json.dumps(artifact,indent=2));print(label,len(messages),len(generations),flush=True)
