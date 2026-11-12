"""Presentation contract tests: compilation, evidence grounding and fallback."""
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import AsyncMock

from a2ui.processor import A2uiGenerator, CatalogConfig
from a2ui.core.schema.v1_0.renderer_capabilities import A2uiRendererCapabilities
from marketplace.a2ui_demo import CATALOG_ID, available_data, catalog, compose, validate_messages

SOURCE = {'evidence-test': {'status': 'ok', 'purpose': 'Order status',
          'snapshot': {'revision': 7, 'clock': '2026-10-03T12:00:00Z'},
          'columns': ['order_id', 'status'], 'rows': [{'order_id': 'order-1', 'status': 'dispatched'}]}}
LAYOUT = '<a2ui>\nsummary = OrderSummary($/records/r0)\nanswer = Text($/answer)\nroot = Column([summary, answer])\n</a2ui>'


def compile_layout(raw, data):
    processor = A2uiGenerator(catalogs=[CatalogConfig(catalog=catalog())]).create_processor(
        A2uiRendererCapabilities.model_validate({'1.0': {'supportedCatalogIds': [CATALOG_ID]}}))
    return validate_messages(processor.parse_response(raw), data)


class PresentationContract(TestCase):
    def test_official_compiler_binds_server_data(self):
        data = available_data('Order is dispatched.', SOURCE)
        wire = compile_layout(LAYOUT, data)
        surface = wire[0]['createSurface']
        self.assertEqual(surface['dataModel'], data)
        self.assertEqual(surface['components'][0]['record'], {'@path': '/records/r0'})
        self.assertEqual(data['records']['r0']['fields'][1]['value'], 'dispatched')
        fixture = Path(__file__).parent / 'fixtures' / 'a2ui-answer.json'
        self.assertEqual(json.loads(fixture.read_text()), wire)

    def test_unknown_bindings_and_literal_facts_are_rejected(self):
        data = available_data('Order is dispatched.', SOURCE)
        for raw in [LAYOUT.replace('/records/r0', '/records/missing'),
                    LAYOUT.replace('Text($/answer)', 'Text("delivered")'),
                    LAYOUT.replace('OrderSummary($/records/r0)', 'OrderSummary($/answer)'),
                    LAYOUT.replace('OrderSummary($/records/r0)', 'EventTimeline($/datasets/d0)'),
                    LAYOUT.replace('root = Column', '$/answer = "Invented"\nroot = Column')]:
            with self.subTest(raw=raw), self.assertRaises(Exception):
                compile_layout(raw, data)

    def test_timeline_preserves_attempt_order_and_source_scope(self):
        source = {'evidence-events': {'status': 'ok', 'historical': True,
                  'rows': [{'revision': 1, 'kind': 'refund_failed', 'occurred_at': '2026-10-03'},
                           {'revision': 2, 'kind': 'refund_completed', 'occurred_at': '2026-10-03'}]}}
        data = available_data('One completed refund after a failed attempt.', source)
        raw = LAYOUT.replace('OrderSummary($/records/r0)', 'EventTimeline($/datasets/d0)')
        compile_layout(raw, data)
        dataset = data['datasets']['d0']
        self.assertTrue(dataset['timeline'])
        self.assertEqual([r[1] for r in dataset['rows']], ['refund_failed', 'refund_completed'])
        self.assertIn('Earlier question evidence', dataset['scope'])

    def test_bounded_records_explicitly_mark_partial_results(self):
        source = {'evidence-many': {'status': 'ok', 'rows': [{'number': n} for n in range(30)]}}
        data = available_data('30 records found.', source)
        self.assertEqual(len(data['datasets']['d0']['rows']), 12)
        self.assertIn('Partial', data['datasets']['d0']['notice'])
        self.assertEqual(len(data['records']), 12)

    def test_failed_and_empty_sources_are_not_presented_as_business_records(self):
        data = available_data('Could not retrieve records.', {'failure': {'status': 'error', 'rows': [{'status': 'delivered'}]}})
        self.assertEqual(data['records'], {})
        self.assertEqual(data['datasets'], {})

    def test_model_failure_and_invalid_ui_keep_text_fallback_and_usage(self):
        invalid = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content='Not a layout'))],
                                  usage=SimpleNamespace(prompt_tokens=42, completion_tokens=9))
        for result in [RuntimeError('unavailable'), invalid]:
            call = AsyncMock(side_effect=result) if isinstance(result, Exception) else AsyncMock(return_value=result)
            api = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=call)))
            ui = asyncio.run(compose('Status?', 'Order is dispatched.', SOURCE, api, 'test-model'))
            self.assertEqual(ui['status'], 'unavailable')
            self.assertEqual(ui['requests'], 1)
            self.assertNotIn('messages', ui)
            if result is invalid:
                self.assertEqual(ui['input_tokens'], 42)
                self.assertEqual(ui['output_tokens'], 9)

    def test_composition_uses_catalog_and_only_one_model_call(self):
        call = AsyncMock(return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=LAYOUT))],
                         usage=SimpleNamespace(prompt_tokens=100, completion_tokens=50)))
        api = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=call)))
        ui = asyncio.run(compose('Status?', 'Order is dispatched.', SOURCE, api, 'test-model'))
        self.assertEqual(ui['status'], 'completed')
        call.assert_awaited_once()
        request = call.call_args.kwargs
        self.assertNotIn('tools', request)
        self.assertIn('OrderSummary', request['messages'][0]['content'])
        self.assertEqual(ui['output_tokens'], 50)

    def test_only_known_read_action_can_be_composed(self):
        data = available_data('Order is dispatched.', SOURCE)
        raw = '<a2ui>\nlabel = Text($/actions/a0/label)\nbutton = Button(child=label, action=Event("show_order_history", {actionId: "a0"}))\nanswer = Text($/answer)\nroot = Column([button,answer])\n</a2ui>'
        wire = compile_layout(raw, data)
        self.assertEqual(wire[0]['createSurface']['dataModel']['actions']['a0']['order_id'], 'order-1')
        for bad in [raw.replace('show_order_history', 'refund'), raw.replace('"a0"', '"a7"')]:
            with self.assertRaises(ValueError):
                compile_layout(bad, data)

    def test_followup_uses_stored_order_and_rejects_foreign_or_unknown_actions(self):
        from marketplace.a2ui_demo import history_question
        ui = {'status': 'completed', 'messages': compile_layout(LAYOUT, available_data('Order is dispatched.', SOURCE))}
        run = SimpleNamespace(conversation_id='owned', status='completed', metrics={'a2ui': ui})
        self.assertEqual(history_question(run, 'owned', 'a0'), 'Show the recorded event history for order order-1.')
        with self.assertRaises(LookupError):
            history_question(run, 'other', 'a0')
        with self.assertRaises(ValueError):
            history_question(run, 'owned', 'a7')
        run.status = 'failed'
        with self.assertRaises(ValueError):
            history_question(run, 'owned', 'a0')
