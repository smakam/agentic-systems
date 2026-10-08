"""Explicitly reset only this application's interactive demo records."""
import argparse
from sqlalchemy import text
from .db import engine,Base,Session
from .seed import seed

def reset(confirm=False):
    if not confirm: raise ValueError('Pass --confirm-demo-reset to erase demo state and conversations')
    with engine.begin() as db:
        # Exclusive lock serializes with commands. Caller stops backend first.
        db.execute(text('LOCK TABLE state IN ACCESS EXCLUSIVE MODE'))
        tables=','.join('public.'+x.name for x in reversed(Base.metadata.sorted_tables))
        db.execute(text(f'TRUNCATE {tables} CASCADE'))
    with Session.begin() as db: seed(db)
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--confirm-demo-reset',action='store_true');args=parser.parse_args();reset(args.confirm_demo_reset)
