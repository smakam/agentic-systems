"""Small live transport comparison; requires isolated market_test, never resets data."""
import asyncio, json, os, time, uuid
from pathlib import Path
assert os.environ['DATABASE_URL'].endswith('/market_test')
from marketplace.agent import answer
from marketplace.db import Session, Conversation

async def main():
    results=[]
    questions=['What products and quantities are in order-1, and who sells them?',
               'What is the total quantity in that order?',
               'What is the current return window according to policy?',
               'Explain the payout history and eligibility for order-1.']
    for transport in ('direct','mcp'):
        cid='mcp-smoke-'+uuid.uuid4().hex[:12]
        with Session.begin() as db:
            db.add(Conversation(id=cid,owner_id='support',title='MCP transport check',items=[]))
        for question in questions:
            start=time.monotonic()
            result=await answer(cid,question,evaluation_config={'tool_transport':transport,'alias':'support-model','model':os.getenv('OPENAI_MODEL'),'budget':.05})
            result.update(question=question,transport=transport,wall_seconds=round(time.monotonic()-start,2))
            results.append(result)
            Path('/results/comparison.json').write_text(json.dumps(results,indent=2,default=str))
            print(transport, result['status'],question,flush=True)
    assert all(r['status']=='completed' for r in results)
asyncio.run(main())
