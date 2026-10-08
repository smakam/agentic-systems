"""Shared callable contracts for direct SDK and MCP access."""
import json, logging

def build_tool_functions(ctx):
    # Wrappers return actionable errors without leaking connection credentials.
    def safe(fn,*args):
        try: return fn(*args)
        except Exception as e: return {'status':'error','code':'TOOL_REJECTED','retryable':False,'message':str(e).split('\n')[0][:200]}
    async def get_catalog() -> dict:
        """Get unified entity/field definitions, SQL types, nullability, constraints, relationships and metrics before SQL. Contains no business records. If validation fails, stop SQL."""
        return safe(ctx.catalog)
    async def query_business_data(sql:str,parameters_json:str='{}',purpose:str='') -> dict:
        """Run one bounded PostgreSQL SELECT over analytics tables. Bind values using %(name)s placeholders and JSON parameters. Money is in paise."""
        try:
            parameters=json.loads(parameters_json)
            if not isinstance(parameters,dict): raise ValueError('parameters_json must be an object')
            return ctx.query(sql,parameters,purpose)
        except Exception as e: return {'status':'error','code':'QUERY_REJECTED','retryable':False,'message':str(e).split('\n')[0][:200]}
    async def search_documents(query:str,effective_at:str|None=None,scope:str='all',top_k:int=4) -> dict:
        """Find applicable policy or runbook passages. effective_at is an ISO timestamp with timezone; defaults to the demo clock."""
        try: return await ctx.search(query,effective_at,scope,top_k)
        except Exception as e:
            logging.getLogger(__name__).warning('Retrieval failed (%s): %s',type(e).__name__,str(e)[:150])
            return {'status':'error','code':'RETRIEVAL_UNAVAILABLE','retryable':False,'message':'Retrieval failed; do not treat this as no matching documents.'}
    async def fetch_evidence(handle:str) -> dict:
        """Fetch full evidence already returned in this run by its handle."""
        return safe(ctx.fetch,handle)
    async def get_order_history(order_id:str) -> dict:
        """Get validated current order records and its chronological event evidence, including failed attempts and retries. Money is in paise."""
        return safe(ctx.order_history,order_id)
    return [get_catalog,query_business_data,search_documents,fetch_evidence,get_order_history]
