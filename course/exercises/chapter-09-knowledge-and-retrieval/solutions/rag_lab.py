"""Isolated Chapter 9 reference lab: real gateway embeddings and pgvector search.

Never connects to the marketplace or fixed evaluation databases. No lexical fallback.
"""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import re

import psycopg
from psycopg.rows import dict_row
from openai import AsyncOpenAI

ROOT = Path(__file__).resolve().parents[1]
DB_NAME = 'ch09_rag_lab'


def connect():
    url = os.environ['CH9_DATABASE_URL']
    if psycopg.conninfo.conninfo_to_dict(url).get('dbname') != DB_NAME:
        raise ValueError('CH9_DATABASE_URL must target ch09_rag_lab')
    return psycopg.connect(url, row_factory=dict_row)


def chunks(path, strategy):
    lines = path.read_text().splitlines()
    paragraphs = []
    start = 0
    for end in range(len(lines) + 1):
        if end < len(lines) and lines[end].strip():
            continue
        body = '\n'.join(lines[start:end]).strip()
        if body:
            paragraphs.append((start + 1, end, body))
        start = end + 1
    width = 1 if strategy == 'paragraph' else 2
    # Two consecutive paragraphs, stride one; source lines remain inspectable.
    return [(paragraphs[i][0], paragraphs[min(i + width - 1, len(paragraphs)-1)][1],
             '\n\n'.join(p[2] for p in paragraphs[i:i+width]))
            for i in range(len(paragraphs))]


async def ingest(db, api, corpus, filename, strategy, version):
    parts = chunks(ROOT / 'fixtures' / filename, strategy)
    response = await api.embeddings.create(model='embedding', input=[p[2] for p in parts])
    with db.transaction():
        db.execute('DELETE FROM lab_chunks WHERE corpus=%s', (corpus,))
        for i, (start, end, body) in enumerate(parts):
            db.execute('INSERT INTO lab_chunks VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s::vector)',
                       (corpus, f'{corpus}:{start}', version, filename, start, end, body,
                        hashlib.sha256(body.encode()).hexdigest(), str(response.data[i].embedding)))
    return len(parts)


async def retrieve(db, api, corpus, query, top_k):
    vector = (await api.embeddings.create(model='embedding', input=query)).data[0].embedding
    return db.execute('SELECT id,version,source,line_start,line_end,body, '
                      '1-(embedding <=> %s::vector) AS score FROM lab_chunks '
                      'WHERE corpus=%s ORDER BY embedding <=> %s::vector, id LIMIT %s',
                      (str(vector), corpus, str(vector), top_k)).fetchall()


async def answer(api, query, rows):
    response = await api.chat.completions.create(
        model='support-model', messages=[
            {'role': 'system', 'content': 'Use only supplied facts and policy passages. '
             'Cite passage IDs in square brackets. If evidence is incomplete, say so. '
             'Do not infer that eligibility means a payout was executed.'},
            {'role': 'user', 'content': query + '\nPassages:\n' + json.dumps(rows)}])
    return response.choices[0].message.content


async def run(args):
    api = AsyncOpenAI(base_url=os.environ['LITELLM_URL'], api_key=os.environ['LITELLM_API_KEY'],
                      max_retries=0, timeout=90)
    db = connect()
    try:
        db.execute('CREATE EXTENSION IF NOT EXISTS vector')
        db.execute('CREATE TABLE IF NOT EXISTS lab_chunks (corpus text, id text, version text, '
                   'source text, line_start integer, line_end integer, body text, content_hash text, '
                   'embedding vector(1536), PRIMARY KEY(corpus,id))')
        db.commit()
        q = ('Simulated fixed facts: payment captured, delivery 30 hours ago, no open return. '
             'Is the seller payout eligible? Give the waiting period and cite policy.')
        counts = {}
        counts['policy_v1'] = await ingest(db, api, 'policy', 'payout-v1.md', 'paragraph', 'v1')
        baseline = await retrieve(db, api, 'policy', q, 4)
        # A new source file is present, but the indexed corpus still holds v1.
        stale = await retrieve(db, api, 'policy', q, 4)
        assert baseline == stale, 'Indexed evidence unexpectedly changed before reindexing'
        counts['policy_v2'] = await ingest(db, api, 'policy', 'payout-v2.md', 'paragraph', 'v2')
        updated = await retrieve(db, api, 'policy', q, 4)
        assert all(r['version'] == 'v2' for r in updated)
        assert any('48 hours' in r['body'] for r in updated)
        result = {'embedding_alias': 'embedding', 'dimensions': 1536,
                  'policy': {'question': q, 'before': baseline, 'source_changed_not_reindexed': stale,
                             'after_reindex': updated}, 'chunking': []}
        if args.answers:
            for name, rows in [('before', baseline), ('after', updated)]:
                result['policy'][name + '_answer'] = await answer(api, q, rows)
        cq = ('Simulated fixed facts: payment captured, confirmed delivery 30 hours ago, '
              'no open return, Amber Review flag present. Is seller payout eligible? '
              'Explain the standard rule and the exception, with citations.')
        for strategy in ('paragraph', 'overlap'):
            counts[strategy] = await ingest(db, api, strategy, 'expanded-policy.md', strategy, 'lab-v1')
            for k in (1, 4):
                rows = await retrieve(db, api, strategy, cq, k)
                bodies = '\n'.join(r['body'] for r in rows)
                item = {'strategy': strategy, 'top_k': k, 'question': cq, 'passages': rows,
                        'has_standard_rule': bool(re.search(r'at least 24 elapsed', bodies)),
                        'has_exception': 'requires 72 elapsed' in bodies,
                        'retrieved_characters': sum(len(r['body']) for r in rows)}
                if args.answers:
                    item['answer'] = await answer(api, cq, rows)
                result['chunking'].append(item)
        result['chunk_counts'] = counts
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + '\n')
        print(json.dumps({'output': str(output), 'counts': counts,
                          'policy_index_refresh_verified': True,
                          'chunking': [{k: v for k, v in i.items() if k in (
                              'strategy', 'top_k', 'has_standard_rule', 'has_exception',
                              'retrieved_characters')} for i in result['chunking']]}))
    finally:
        db.close()
        await api.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--answers', action='store_true', help='Also make six model answer calls')
    parser.add_argument('--output', default='/tmp/ch9-results.json')
    asyncio.run(run(parser.parse_args()))
