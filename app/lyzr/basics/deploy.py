"""Create a separate agent only after its native KB contains documents. Never updates agents."""
import argparse,json,os
from pathlib import Path
from urllib.request import Request,urlopen
HERE=Path(__file__).resolve().parent
MANIFEST=HERE/'deployment.json'
def build_agent_config(kb_id,credential,provider='OpenAI',model='gpt-5.4-mini'):
 return {'name':'Support Agent Basics','description':'Separate fictional order KB lab; no marketplace/MCP','agent_role':'Read-only fictional order investigator','agent_goal':'Answer only from supplied fictional source records','agent_instructions':(HERE/'agent-instructions.txt').read_text(),'agent_context':'','provider_id':provider,'model':model,'llm_credential_id':credential,'top_p':1.0,'temperature':0.1,'features':[{'type':'KNOWLEDGE_BASE','priority':0,'config':{'lyzr_rag':{'base_url':'https://rag-prod.studio.lyzr.ai','rag_id':kb_id,'rag_name':'support_agent_basics_orders','params':{'top_k':6,'retrieval_type':'basic','score_threshold':0}}}},{'type':'MEMORY','priority':0,'config':{'provider':'cognis','lyzr_memory':{'provider_type':'cognis','params':{'cross_session':False,'instructions':'Maintain current session context; do not retain business records as personal memory or store credentials.'}}}}],'tools':[],'tool_configs':[],'managed_agents':[],'a2a_tools':[],'store_messages':True,'max_iterations':5}
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--kb-id',required=True);args=parser.parse_args()
 if MANIFEST.exists():raise SystemExit('Existing Basics manifest: inspect it; no duplicate create or update.')
 key=os.environ['LYZR_API_KEY']
 def request(url,payload=None):
  req=Request(url,data=json.dumps(payload).encode() if payload is not None else None,headers={'x-api-key':key,'Content-Type':'application/json'})
  with urlopen(req,timeout=60) as response:return json.load(response)
 docs=request('https://rag-prod.studio.lyzr.ai/v3/rag/documents/'+args.kb_id+'/')
 if not docs:raise SystemExit('Knowledge Base has no documents. Fix training/credits before agent creation.')
 config=build_agent_config(args.kb_id,os.environ.get('LYZR_LLM_CREDENTIAL_ID','lyzr_openai'),model=os.environ.get('LYZR_BASICS_MODEL','gpt-5.4-mini'))
 # Persist intent before submission; uncertain errors must not trigger blind retries.
 MANIFEST.write_text(json.dumps({'status':'creation_submitting','kb_id':args.kb_id},indent=2))
 data=request('https://agent-prod.studio.lyzr.ai/v3/agents/',config)
 agent_id=data.get('agent_id') or data.get('_id') or data.get('id')
 if not agent_id:raise SystemExit('Creation submitted but response has no ID; inspect Studio before retrying.')
 read=request('https://agent-prod.studio.lyzr.ai/v3/agents/'+agent_id)
 MANIFEST.write_text(json.dumps({'status':'created','agent_id':agent_id,'kb_id':args.kb_id,'name':read.get('name'),'model':read.get('model'),'features':read.get('features'),'tools':read.get('tools'),'tool_configs':read.get('tool_configs')},indent=2)+'\n')
 print('Separate Basics agent created and read back; inspect deployment.json.')
if __name__=='__main__':main()
