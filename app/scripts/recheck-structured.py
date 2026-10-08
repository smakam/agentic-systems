"""Append versioned deterministic checks to saved outputs; no DB or API calls."""
import json,sys
from pathlib import Path
from marketplace.eval_structured import structured_gold,VERSION
p=Path(sys.argv[1]);data=json.loads(p.read_text())
backup=p.with_name('results.before-'+VERSION+'.json')
if not backup.exists():backup.write_bytes(p.read_bytes())
for r in data['results']:
    for idx,t in enumerate(r['turns']):
        d=t['deterministic'];d.setdefault('original_structured_gold_comparison',d['checks'].get('structured_gold_comparison'))
        result=structured_gold(r['case']['id'],t['run'],turn_index=idx,aliases=r['aliases'])
        d['structured_gold_details']=result;d['checks']['structured_gold_comparison']=result['passed']
data['structured_grading_version']=VERSION
p.write_text(json.dumps(data,indent=2)+'\n')
from collections import Counter
print(dict(Counter(t['deterministic']['structured_gold_details']['status'] for r in data['results'] for t in r['turns'])))
