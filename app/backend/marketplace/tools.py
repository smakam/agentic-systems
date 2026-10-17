"""Bounded, snapshot-consistent read tools. No business credentials reach SQL."""
import hashlib, json, os, time, uuid, re
from datetime import datetime
import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb
import sqlglot
from sqlglot import exp
from openai import AsyncOpenAI, DefaultAsyncHttpxClient
from .seed import DATA

TABLES={'sellers','products','listings','orders','order_items','payments','shipments','allocations','payouts','returns','refunds','events','tickets','incidents','customers','freshness','seller_balances'}
FUNCTIONS={'SUM','COUNT','AVG','MIN','MAX','COALESCE','ROUND','ABS','LOWER','UPPER','LENGTH','NULLIF','CAST','EXTRACT','DATE_TRUNC','AND','OR','JSON_EXTRACT_SCALAR'}

def validate_sql(sql):
    if len(sql)>8000: raise ValueError('Query is too long')
    statements=sqlglot.parse(sql,read='postgres')
    if len(statements)!=1 or not isinstance(statements[0],(exp.Select,exp.Union)): raise ValueError('One read-only SELECT is required')
    tree=statements[0]
    for node in tree.walk():
        if isinstance(node,(exp.Insert,exp.Update,exp.Delete,exp.Create,exp.Drop,exp.Command,exp.Into,exp.Lock,exp.Star)):
            # Stars are acceptable in projection or COUNT; never a write.
            if isinstance(node,exp.Star): continue
            raise ValueError('Unsupported SQL operation')
        if isinstance(node,exp.Func):
            name=node.name.upper() if isinstance(node,exp.Anonymous) else node.sql_name()
            if name not in FUNCTIONS: raise ValueError(f'Function {name} is not allowed')
    ctes={x.alias_or_name for x in tree.find_all(exp.CTE)}
    for table in tree.find_all(exp.Table):
        if table.catalog or (table.db and table.db!='analytics'): raise ValueError('Only the analytics schema is allowed')
        if table.name not in TABLES and table.name not in ctes: raise ValueError(f'Table {table.name} is not available')
        if table.name in TABLES: table.set('db',exp.to_identifier('analytics'))
    if any(isinstance(x,exp.Join) and x.args.get('kind')=='CROSS' for x in tree.walk()): raise ValueError('Cross joins are not allowed')
    return tree.sql(dialect='postgres')

def client(*, judge=False):
    from .gateway_identity import current_key
    key=os.getenv("JUDGE_GATEWAY_KEY") if judge else current_key()
    if not key: raise RuntimeError("Gateway virtual key missing; run scripts/start.sh")
    from .gateway_cost import record_gateway_cost
    from .routing_demo import record_routing_call
    from .response_cache_demo import record as record_response_cache
    http_options={'event_hooks': {'response': [record_gateway_cost, record_routing_call, record_response_cache]}}
    options={}
    audience=os.getenv('GATEWAY_IAM_AUDIENCE')
    # Scale-to-zero gateways need time for container and dependency startup.
    timeout=float(os.getenv('GATEWAY_REQUEST_TIMEOUT_SECONDS', '120' if audience else '40'))
    if audience:
        from .cloud_auth import CloudRunAuth
        http_options['auth']=CloudRunAuth(audience)
    options['http_client']=DefaultAsyncHttpxClient(timeout=timeout,**http_options)
    return AsyncOpenAI(base_url=os.getenv('LITELLM_URL','http://localhost:4000/v1'),api_key=key,max_retries=0,timeout=timeout,**options)

class ReadContext:
    def __init__(self, *, suppress_catalog=False, suppress_documents=False):
        self.suppress_catalog = suppress_catalog
        self.suppress_documents = suppress_documents
        self.conn=psycopg.connect(os.getenv('READ_DATABASE_URL','postgresql://agent_reader:reader-local@localhost:55432/market'),row_factory=dict_row)
        self.conn.execute('BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY')
        self.snapshot=self.conn.execute('SELECT * FROM analytics.freshness').fetchone()
        self.evidence={}; self.calls=0
        self.ontology=json.loads((DATA/'ontology.json').read_text())
        self.doc_hash=hashlib.sha256(json.dumps(self.conn.execute('SELECT id,content_hash FROM public.document_chunks ORDER BY id').fetchall(),default=str).encode()).hexdigest()[:16]
    def close(self): self.conn.close()
    def save(self,payload):
        self.calls+=1
        if self.calls>24: raise ValueError('Tool call budget exhausted')
        handle='evidence-'+uuid.uuid4().hex[:12]
        envelope={'contract_version':'1.0','status':'ok' if payload.get('rows',payload.get('chunks',[1])) else 'empty','handle':handle,'snapshot':self.snapshot,'document_revision':self.doc_hash,'attempt':1,**payload}
        # Normalize timestamps before storage and prevent oversized tool responses.
        envelope=json.loads(json.dumps(envelope,default=str))
        if len(json.dumps(envelope))>60000: raise ValueError('Response exceeds evidence size limit; narrow the query')
        self.evidence[handle]=envelope
        return envelope
    def query(self,sql,params=None,purpose=""):
        normalized=validate_sql(sql)
        started=time.monotonic()
        # SAVEPOINT lets a syntax/timeout error be repaired without losing the snapshot.
        self.conn.execute('SAVEPOINT tool_query')
        try:
            # psycopg interprets percent signs only when a parameter mapping is supplied.
            # Preserve named bindings while escaping SQL literals/operators for that mode.
            execution_sql=re.sub(r'%(?!\([^)]+\)[sbt])','%%',normalized) if params else normalized
            cursor=self.conn.execute(f'SELECT * FROM ({execution_sql}) AS bounded_result LIMIT 101',params or None)
            rows=cursor.fetchall()
            self.conn.execute('RELEASE SAVEPOINT tool_query')
        except Exception:
            self.conn.execute('ROLLBACK TO SAVEPOINT tool_query'); self.conn.execute('RELEASE SAVEPOINT tool_query'); raise
        return self.save({'type':'query','purpose':purpose,'sql':normalized,'params':params or {},'rows':rows[:100],'columns':[x.name for x in cursor.description],'truncated':len(rows)>100,'row_count':min(len(rows),100),'elapsed_ms':round((time.monotonic()-started)*1000),'query_hash':hashlib.sha256(normalized.encode()).hexdigest()})
    def order_history(self,order_id):
        current=self.query('''SELECT i.order_id,i.id AS item_id,i.quantity,
          r.id AS return_id,r.status AS return_status,r.quantity AS return_quantity,
          f.id AS refund_id,f.status AS refund_status,f.amount AS refund_amount_paise,
          a.gross AS gross_paise,a.refunded AS refunded_paise,a.fee AS fee_paise,
          p.id AS payout_id,p.status AS payout_status,p.amount AS payout_amount_paise
          FROM analytics.order_items i
          LEFT JOIN analytics.returns r ON r.item_id=i.id
          LEFT JOIN analytics.refunds f ON f.return_id=r.id
          LEFT JOIN analytics.allocations a ON a.item_id=i.id
          LEFT JOIN analytics.payouts p ON p.allocation_id=a.id
          WHERE i.order_id=%(order_id)s ORDER BY i.id,r.id''',
          {'order_id':order_id},'Current order, return, refund and payout records; allocation amounts repeat across multiple returns')
        events=self.query('''WITH items AS (
          SELECT id FROM analytics.order_items WHERE order_id=%(order_id)s
        ), return_ids AS (
          SELECT id FROM analytics.returns WHERE item_id IN (SELECT id FROM items)
        ), allocation_ids AS (
          SELECT id FROM analytics.allocations WHERE item_id IN (SELECT id FROM items)
        ), related AS (
          SELECT id FROM analytics.orders WHERE id=%(order_id)s
          UNION SELECT id FROM items UNION SELECT id FROM return_ids
          UNION SELECT id FROM allocation_ids
          UNION SELECT id FROM analytics.refunds WHERE return_id IN (SELECT id FROM return_ids)
          UNION SELECT id FROM analytics.payouts WHERE allocation_id IN (SELECT id FROM allocation_ids)
          UNION SELECT id FROM analytics.shipments WHERE item_id IN (SELECT id FROM items)
          UNION SELECT id FROM analytics.payments WHERE order_id=%(order_id)s
        ) SELECT e.revision,e.kind,e.entity_id,e.details,e.occurred_at,e.recorded_at
          FROM analytics.events e
          WHERE e.entity_id IN (SELECT id FROM related) OR e.details->>'id' IN (SELECT id FROM related)
          ORDER BY e.revision,e.recorded_at,e.id''',
          {'order_id':order_id},'Recorded order event timeline, including failed and successful attempts')
        return {'current_records':current,'event_timeline':events}
    def catalog(self):
        if self.suppress_catalog:
            return self.save({"type":"catalog","status":"ok","catalog":None,"method":"context_suppressed"})
        from .catalog import build_catalog
        catalog = build_catalog(self.conn, self.ontology)
        payload = {'type': 'catalog', 'catalog': catalog}
        if catalog['validation']['status'] == 'error':
            payload.update(status='error', code='CATALOG_DRIFT', message='Catalog and database differ; do not construct SQL until definitions are repaired.')
        return self.save(payload)
    async def search(self,query,effective_at=None,scope='all',top_k=4):
        if self.suppress_documents:
            return self.save({'type':'documents','status':'ok','chunks':[],'method':'context_suppressed'})
        if not 1<=top_k<=8: raise ValueError('top_k must be 1–8')
        when=datetime.fromisoformat(effective_at) if effective_at else self.snapshot['clock']
        if when.tzinfo is None: raise ValueError('Use a date-time with timezone')
        rows=self.conn.execute('SELECT id,title,version,scope,source,line_start,line_end,body,embedding::text AS embedding FROM public.document_chunks WHERE effective_from<=%s AND (effective_to IS NULL OR effective_to>%s) AND (scope=\'all\' OR scope=%s)',(when,when,scope)).fetchall()
        if not rows: return self.save({'type':'documents','chunks':[],'method':'no_applicable_documents'})
        if all(r['embedding'] is not None for r in rows):
            api=client()
            try: vector=(await api.embeddings.create(model='embedding',input=query)).data[0].embedding
            finally: await api.close()
            # Exact cosine comparison lives in pgvector, scoped to the frozen corpus.
            ranked=self.conn.execute('SELECT id,title,version,scope,source,line_start,line_end,body,1-(embedding OPERATOR(public.<=>) %s::public.vector) AS score FROM public.document_chunks WHERE effective_from<=%s AND (effective_to IS NULL OR effective_to>%s) AND (scope=\'all\' OR scope=%s) ORDER BY embedding OPERATOR(public.<=>) %s::public.vector LIMIT %s',(str(vector),when,when,scope,str(vector),top_k)).fetchall()
            method='pgvector_cosine'
        else:
            # Explicit degraded mode permits no-key development, never disguised as vectors.
            words=set(query.lower().split())
            for r in rows:
                r.pop('embedding'); r['score']=len(words & set((r['title']+' '+r['body']).lower().split()))
            ranked=sorted((r for r in rows if r['score']>0),key=lambda x:x['score'],reverse=True)[:top_k]
            method='lexical_fallback_unindexed'
        return self.save({'type':'documents','chunks':ranked,'method':method,'effective_at':when,'warning':'Scores rank candidates; they are not confidence or proof.'})
    def fetch(self,handle):
        if handle not in self.evidence: raise ValueError('Evidence handle is not part of this run')
        return self.evidence[handle]
