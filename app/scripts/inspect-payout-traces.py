import json
from pathlib import Path
from marketplace.agent import lf
p=Path('/results/payout-full-agent-repeat-2026-09-29')
s=json.loads((p/'results.json').read_text())
for r in s['results']:
 if r['case']['id']!='17':continue
 tid=r['turns'][0]['run']['metrics']['trace_id']
 t=lf.api.observations.get_many(trace_id=tid,fields='core,io,model,usage,metadata',limit=100).model_dump(mode='json')
 (p/(r['key']+'-trace.json')).write_text(json.dumps(t,indent=2,default=str))
 print(r['key'],[(o.get('id'),o.get('type'),o.get('name'),len(str(o.get('input')))) for o in t.get('data',[])])
