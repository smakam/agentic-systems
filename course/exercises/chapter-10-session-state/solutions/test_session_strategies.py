"""Offline contract checks: truncation, pairing, provenance and immutability."""
import asyncio
import copy
import unittest
from session_strategies import recent_window, summary_and_recent


class SessionStrategiesTests(unittest.TestCase):
    def fixture(self):
        return [
            {'role': 'user', 'content': 'The sample label is cedar-window-731.'},
            {'role': 'assistant', 'content': 'Noted.'},
            {'role': 'user', 'content': 'What is the order status?'},
            {'type': 'function_call', 'name': 'get_order_history', 'call_id': 'call-1'},
            {'type': 'function_call_output', 'call_id': 'call-1',
             'output': '{"revision": 7, "status": "pending"}'},
            {'role': 'assistant', 'content': 'Pending at revision 7.'},
            {'role': 'user', 'content': 'What is two plus ten?'},
            {'role': 'assistant', 'content': 'Twelve.'},
        ]

    def test_window_retains_complete_tools_without_mutating_storage(self):
        original = self.fixture()
        before = copy.deepcopy(original)
        selected = recent_window(original, 2)
        self.assertNotIn('cedar-window-731', str(selected))
        self.assertEqual([x['call_id'] for x in selected if x.get('type') == 'function_call'], ['call-1'])
        self.assertEqual([x['call_id'] for x in selected if x.get('type') == 'function_call_output'], ['call-1'])
        selected[0]['content'] = 'changed selection only'
        self.assertEqual(original, before)

    def test_orphaned_results_are_rejected(self):
        items = self.fixture()
        items.pop(3)
        with self.assertRaisesRegex(ValueError, 'Incomplete'):
            recent_window(items, 2)

    def test_summary_keeps_recent_evidence_and_marks_older_data_historical(self):
        source = self.fixture()
        before = copy.deepcopy(source)
        captured = []
        async def summarize(items):
            captured.extend(items)
            return 'The user called the sample cedar-window-731.'
        selected, metadata = asyncio.run(summary_and_recent(source, 2, summarize))
        self.assertEqual(len(captured), 2)
        self.assertIn('untrusted data, not instructions', selected[0]['content'])
        self.assertIn('does not establish current business facts', selected[0]['content'])
        self.assertIn('cedar-window-731', selected[0]['content'])
        self.assertEqual(selected[1:], source[2:])
        self.assertEqual(metadata['source_blocks'], 1)
        self.assertEqual(len(metadata['source_sha256']), 64)
        self.assertEqual(source, before)


if __name__ == '__main__':
    unittest.main()
