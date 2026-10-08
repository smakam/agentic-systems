import asyncio,json,time,hashlib
from pathlib import Path
import httpx
from openai import AsyncOpenAI
APP=Path(__file__).resolve().parents[1];OUT=APP/'results/payout-identical-input-2026-09-29'
async def main():
 OUT.mkdir(exist_ok=True)
 capture=APP/'results/payout-request-capture-2026-09-29'
 # Preserve SDK settings and schemas. Omitted SDK sentinel values were serialized as null;
 # restore omission for optional kwargs before constructing the frozen request.
 template=json.loads((capture/'request-04.json').read_text());template={k:v for k,v in template.items() if v is not None}
 old=APP/'results/payout-full-agent-repeat-2026-09-29'
 env={}
 for l in (APP/'.env').read_text().splitlines():
  if '=' in l and not l.lstrip().startswith('#'):
   k,v=l.split('=',1);env[k.strip()]=v.strip().strip('\"\'')
 async def log(request):
  if request.url.path.endswith('/chat/completions'):
   body=json.loads(request.content);(OUT/f'{key}-http-body.json').write_text(json.dumps(body,indent=2))
 api=AsyncOpenAI(base_url='http://localhost:4000/v1',api_key=env['EVAL_GATEWAY_KEY'],max_retries=0,timeout=80,http_client=httpx.AsyncClient(event_hooks={'request':[log]}))
 results=[]
 try:
  for trial in ['1','2']:
   g=json.loads((old/f'{trial}-17-final-generation.json').read_text());req={**template,'messages':json.loads(g['input'])}
   (OUT/f'condition-{trial}-request.json').write_text(json.dumps(req,indent=2))
   for repeat in range(1,4):
    key=f'condition-{trial}-repeat-{repeat}'
    if (OUT/f'{key}.json').exists():raise RuntimeError('Do not overwrite or rerun paid results')
    start=time.monotonic();r=await api.chat.completions.create(**req);u=r.usage
    row={'key':key,'source_original_outcome':'incorrect' if trial=='1' else 'correct eligibility','answer':r.choices[0].message.content,'tool_calls':[x.model_dump() for x in r.choices[0].message.tool_calls or []],'finish_reason':r.choices[0].finish_reason,'usage':u.model_dump(),'estimated_usd':(u.prompt_tokens*2.5+u.completion_tokens*15)/1e6,'seconds':time.monotonic()-start}
    (OUT/f'{key}.json').write_text(json.dumps(row,indent=2));results.append(row);print(key,row['answer'],flush=True)
 finally:await api.close()
 for trial in ['1','2']:
  bodies=[json.loads((OUT/f'condition-{trial}-repeat-{i}-http-body.json').read_text()) for i in range(1,4)];assert bodies[0]==bodies[1]==bodies[2]
 (OUT/'results.json').write_text(json.dumps(results,indent=2));print('Cost',sum(r['estimated_usd'] for r in results))
if __name__=='__main__':asyncio.run(main())
