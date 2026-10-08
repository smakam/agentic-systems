"""Use a separate disposable PostgreSQL container, never a marketplace database."""
import os
import asyncio
import unittest
from marketplace.cloud_registry import DurableInvestigations, DDL


class FakeContext:
    revision=1
    closed=0
    def __init__(self):
        self.snapshot={'revision':self.revision,'clock':'synthetic'}
        self.doc_hash='synthetic-policy'; self.evidence={}; self.calls=0
    def catalog(self):
        self.calls+=1
        result={'status':'ok','handle':'synthetic-evidence','call':self.calls}
        self.evidence[result['handle']]=result
        return result
    def fetch(self,handle):
        return self.evidence[handle]
    def close(self):
        type(self).closed+=1


@unittest.skipUnless(os.getenv('CLOUD_REGISTRY_TEST_DATABASE_URL'),'Requires disposable PostgreSQL')
class RegistryTests(unittest.IsolatedAsyncioTestCase):
    async def test_replica_restart_evidence_budget_drift_and_expiry(self):
        url=os.environ['CLOUD_REGISTRY_TEST_DATABASE_URL']
        # Refuse accidental execution against the application's named databases.
        self.assertTrue(url.endswith('/registry_test'))
        now=[100]
        first=DurableInvestigations(url,FakeContext,clock=lambda:now[0])
        with first.connection() as db:
            db.execute(DDL)
            db.execute('TRUNCATE public.mcp_investigations')
        FakeContext.revision=1
        started=first.begin(); key=started['investigation_id']
        evidence=await first.call(key,'get_catalog')
        first.close()
        second=DurableInvestigations(url,FakeContext,clock=lambda:now[0])
        self.assertEqual(await second.call(key,'fetch_evidence',handle=evidence['handle']),evidence)
        self.assertEqual((await second.call(key,'get_catalog'))['call'],2)
        with second.connection() as db:
            stored=db.execute('SELECT token_hash FROM public.mcp_investigations').fetchone()
            self.assertNotEqual(stored['token_hash'],key)
        FakeContext.revision=2
        self.assertEqual((await second.call(key,'get_catalog'))['code'],'REVISION_CHANGED')
        self.assertEqual((await second.call(key,'get_catalog'))['code'],'INVESTIGATION_UNAVAILABLE')
        renewed=second.begin()['investigation_id']
        now[0]+=181
        self.assertEqual((await first.call(renewed,'get_catalog'))['code'],'INVESTIGATION_UNAVAILABLE')
        self.assertEqual(second.begin()['status'],'ok')


    async def test_concurrent_calls_wait_without_blocking_awaited_tool(self):
        class SlowContext(FakeContext):
            async def search(self,*args):
                await asyncio.sleep(0.2)
                return self.catalog()
        registry=DurableInvestigations(os.environ['CLOUD_REGISTRY_TEST_DATABASE_URL'],SlowContext)
        with registry.connection() as db:
            db.execute(DDL)
            db.execute('TRUNCATE public.mcp_investigations')
            db.execute("ALTER ROLE postgres SET lock_timeout='2s'")
        key=registry.begin()['investigation_id']
        searching=asyncio.create_task(registry.call(key,'search_documents',query='synthetic'))
        await asyncio.sleep(0.05)
        catalog=asyncio.create_task(registry.call(key,'get_catalog'))
        results=await asyncio.wait_for(asyncio.gather(searching,catalog),timeout=3)
        self.assertEqual([r['call'] for r in results],[1,2])
        self.assertEqual((await registry.end(key))['status'],'ok')
