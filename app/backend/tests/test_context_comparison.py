import asyncio,unittest
from unittest.mock import Mock
from marketplace.tools import ReadContext
class ContextComparisonTests(unittest.TestCase):
 def context(self,catalog=False,documents=False):
  c=ReadContext.__new__(ReadContext);c.suppress_catalog=catalog;c.suppress_documents=documents;c.conn=Mock();c.snapshot={'revision':1,'clock':'2026-09-27T12:00:00+00:00'};c.doc_hash='fixture';c.calls=0;c.evidence={};return c
 def test_catalog_succeeds_empty_and_fetch_cannot_restore_it(self):
  c=self.context(catalog=True);r=c.catalog();self.assertEqual(r['status'],'ok');self.assertIsNone(r['catalog']);self.assertEqual(c.fetch(r['handle']),r);c.conn.execute.assert_not_called()
 def test_retrieval_succeeds_empty_without_query_or_fallback(self):
  c=self.context(documents=True);r=asyncio.run(c.search('payout policy'));self.assertEqual(r['status'],'ok');self.assertEqual(r['chunks'],[]);self.assertEqual(c.fetch(r['handle'])['chunks'],[]);c.conn.execute.assert_not_called()
 def test_request_flags_are_independent(self):
  a=self.context(catalog=True);b=self.context(documents=True);self.assertFalse(a.suppress_documents);self.assertFalse(b.suppress_catalog);a.catalog();asyncio.run(b.search('payout'));self.assertTrue(all(x['type']=='catalog' for x in a.evidence.values()));self.assertTrue(all(x['type']=='documents' for x in b.evidence.values()))
if __name__=='__main__':unittest.main()
