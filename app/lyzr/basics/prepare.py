"""Derive native KB content from the shared Google fictional JSON, without hosting tools."""
import hashlib
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
FIXTURE=HERE.parents[1]/'google/basics/support_agent_basics/orders.json'
def render_fixture(data):
    if data.get('fictional') is not True:raise ValueError('Only fictional data is allowed')
    rows=data['orders'];ids=[row['order_id'] for row in rows]
    if len(ids)!=len(set(ids)):raise ValueError('Duplicate fixture IDs')
    header=f"FICTIONAL COURSE DATA. Dataset: {data['dataset_id']}. As of: {data['as_of']}.\nComplete order ID catalogue: {', '.join(ids)}. Only these three orders exist in this fixture.\nDo not invent records, dates, policies or eligibility. No live marketplace connection."
    blocks=[]
    for row in rows:
        blocks.append(header+'\n\nSOURCE RECORD '+row['order_id']+'\n'+json.dumps(row,indent=2,ensure_ascii=False))
    return '\n\n--- RECORD BOUNDARY ---\n\n'.join(blocks)+'\n'
def main():
    raw=FIXTURE.read_bytes();data=json.loads(raw)
    (HERE/'orders-knowledge.txt').write_text(render_fixture(data))
    (HERE/'fixture-manifest.json').write_text(json.dumps({'source':'app/google/basics/support_agent_basics/orders.json','sha256':hashlib.sha256(raw).hexdigest(),'dataset_id':data['dataset_id'],'order_ids':[r['order_id'] for r in data['orders']],'grounding':'native Lyzr Knowledge Base retrieval, not Python lookup_order'},indent=2)+'\n')
    print('Generated fictional native-KB upload and source manifest.')
if __name__=='__main__':main()
