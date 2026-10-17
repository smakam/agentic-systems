"""Manage one dedicated database-backed Test support alias, never main routes."""
import os
import httpx

ALIAS='support-model-test'
MODEL_ID='marketplace-test-support-model'
MODELS={
 'gpt54':{'label':'GPT-5.4 (default)','model':'gpt-5.4-2026-03-05','input_rate':2.5,'output_rate':15.0},
 'nano':{'label':'GPT-5 Nano','model':'gpt-5-nano-2025-08-07','input_rate':.05,'output_rate':.40},
 'gpt5':{'label':'GPT-5','model':'gpt-5','input_rate':1.25,'output_rate':10.0},
}
PROVIDERS={
 'openai':{'gpt54':'openai/gpt-5.4-2026-03-05','nano':'openai/gpt-5-nano-2025-08-07','gpt5':'openai/gpt-5'},
 'openrouter':{'gpt54':'openrouter/openai/gpt-5.4','nano':'openrouter/openai/gpt-5-nano','gpt5':'openrouter/openai/gpt-5'},
}
KEYS=(('LITELLM_API_KEY','marketplace-test-support'),('OPERATOR_GATEWAY_KEY','marketplace-test-operator'))
class Unavailable(RuntimeError):pass

def enabled():
 from .security_demo import is_test
 return is_test() and os.getenv('GATEWAY_MODEL_DEMO_ENABLED')=='true' and all(os.getenv(k) for k in ('GATEWAY_MODEL_DEMO_ADMIN_KEY','LITELLM_API_KEY','OPERATOR_GATEWAY_KEY'))
def require_enabled():
 if not enabled():raise ValueError('Support model mapping is available only in the configured Test workspace')
def client():
 return httpx.AsyncClient(base_url=os.getenv('LITELLM_URL','http://gateway:4000/v1').removesuffix('/v1').rstrip('/'),headers={'Authorization':'Bearer '+os.environ['GATEWAY_MODEL_DEMO_ADMIN_KEY']},timeout=8)
async def inspect(api):
 seen=[]
 for name,expected in KEYS:
  key=os.environ[name];r=await api.get('/key/info',params={'key':key});r.raise_for_status();v=r.json()['info']
  if v.get('key_alias')!=expected or set(v.get('models') or [])!={ALIAS,'embedding'} or v.get('aliases'):
   raise Unavailable('Test gateway keys have unexpected identity or permissions; model was not changed')
  seen.append(key)
 if seen[0]==seen[1]:raise Unavailable('Test gateway identities must be distinct')
 r=await api.get('/model/info');r.raise_for_status();rows=[v for v in r.json()['data'] if v.get('model_name')==ALIAS]
 if len(rows)!=1 or rows[0].get('model_info',{}).get('id')!=MODEL_ID or not rows[0].get('model_info',{}).get('db_model'):
  raise Unavailable('The dedicated Test support alias is missing or is not database-managed')
 model=rows[0]['litellm_params']['model']
 matches=[(p,k) for p,choices in PROVIDERS.items() for k,v in choices.items() if v==model]
 if len(matches)!=1:raise Unavailable('Test alias uses an unrecognized model; restore it to a supported model before continuing')
 provider,choice=matches[0]
 return {'provider':provider,'choice':choice,'model':model}
def public_state(value):
 return {'enabled':True,'choice':value['choice'],'label':MODELS[value['choice']]['label'],'requested_alias':ALIAS,'target_alias':ALIAS,'model':value['model'],'models':[{'id':k,'label':v['label']} for k,v in MODELS.items()]}
async def current():
 require_enabled()
 try:
  async with client() as api:return public_state(await inspect(api))
 except Unavailable:raise
 except Exception:raise Unavailable('Could not verify the Test gateway model mapping') from None
async def update(api,model):
 r=await api.post('/model/update',json={'model_info':{'id':MODEL_ID},'litellm_params':{'model':model}});r.raise_for_status()
async def set_model(choice):
 require_enabled()
 if choice not in MODELS:raise ValueError('Choose one of the configured support models')
 try:
  async with client() as api:
   previous=await inspect(api)
   try:
    await update(api,PROVIDERS[previous['provider']][choice]);value=await inspect(api)
    if value['choice']!=choice:raise Unavailable('Gateway did not confirm the selected Test model')
    return public_state(value)
   except Exception:
    try:
     await update(api,previous['model']);restored=await inspect(api)==previous
    except Exception:restored=False
    if not restored:raise Unavailable('Test alias update could not be confirmed or restored. Stop the demo and restore its model before continuing') from None
    raise Unavailable('Model update failed; previous Test alias mapping was restored') from None
 except Unavailable:raise
 except Exception:raise Unavailable('Test gateway is unavailable; model change was not confirmed') from None
def configuration(state):
 m=MODELS[state['choice']]
 return {'alias':ALIAS,'model':m['model'],'input_rate':m['input_rate'],'output_rate':m['output_rate'],'budget':1.0,'gateway_model_mapping':{'choice':state['choice'],'requested_alias':ALIAS,'target_alias':ALIAS,'model':m['model']}}
