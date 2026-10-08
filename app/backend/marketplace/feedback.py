"""PostgreSQL is authoritative; trace score export is best effort."""
import hashlib
import logging
import os


def export_rating(run, rating, user_id):
    trace_id=(run.metrics or {}).get('trace_id')
    if not trace_id or not os.getenv('LANGFUSE_PUBLIC_KEY') or not os.getenv('LANGFUSE_SECRET_KEY'):
        return
    try:
        from langfuse import Langfuse
        client=Langfuse()
        client.create_score(
            score_id=hashlib.sha256(('answer-feedback:'+run.id).encode()).hexdigest(),
            trace_id=trace_id, name='user_feedback', value=1 if rating=='up' else 0,
            data_type='BOOLEAN', comment='User thumbs-up/down; satisfaction signal, not a correctness grade.',
            metadata={'run_id':run.id,'user_id':user_id},
        )
        client.flush()
    except Exception:
        logging.getLogger(__name__).warning('Answer feedback saved locally; trace score export failed')
