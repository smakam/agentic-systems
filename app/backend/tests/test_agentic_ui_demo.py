import asyncio
import json
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import AsyncMock

from marketplace.a2ui_demo import available_data, history_question
from marketplace.agentic_ui_demo import controlled_messages, compose, validate_html

SOURCE={'e1':{'status':'ok','rows':[{'order_id':'order-1','status':'dispatched'}]}}

def model_api(output):
    create=AsyncMock(return_value=SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=output))],
                      usage=SimpleNamespace(prompt_tokens=10,completion_tokens=20)))
    return SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))

class AgenticUIContract(TestCase):
    def test_controlled_selection_cannot_invent_data_or_choose_non_event_timeline(self):
        data=available_data('Order dispatched.',SOURCE)
        wire=controlled_messages('{"view":"summary","reference":"r0"}',data)
        self.assertEqual(wire[0]['version'],'1.0')
        self.assertEqual(wire[0]['createSurface']['dataModel'],data)
        nodes=wire[0]['createSurface']['components']
        self.assertEqual(next(n for n in nodes if n['id']=='selected')['record'],{'@path':'/records/r0'})
        for selection in [{'view':'summary','reference':'r999'},{'view':'timeline','reference':'d0'},
                          {'view':'answer','reference':'r0'},{'view':'unknown','reference':None},
                          {'view':'summary','reference':'r0','layout':'custom'}]:
            with self.subTest(selection=selection),self.assertRaises(ValueError):
                controlled_messages(json.dumps(selection),data)

    def test_three_modes_preserve_failure_fallback_and_usage(self):
        api=model_api('{"view":"summary","reference":"r0"}')
        result=asyncio.run(compose('Status?','Order dispatched.',SOURCE,api,'model',mode='controlled'))
        self.assertEqual(result['status'],'completed')
        self.assertEqual(result['input_tokens'],10)
        self.assertEqual(api.chat.completions.create.await_count,1)
        failed=asyncio.run(compose('Status?','Answer',SOURCE,model_api('invalid'),'model',mode='controlled'))
        self.assertEqual(failed['status'],'unavailable')
        code=asyncio.run(compose('Status?','Answer',SOURCE,model_api('<html><h1>Order</h1></html>'),'model',mode='open-ended'))
        self.assertEqual(code['status'],'completed')
        self.assertIn('a0',code['actions'])
        self.assertNotIn('messages',code)

    def test_history_action_resolves_saved_mode_and_remains_conversation_scoped(self):
        ui={'status':'completed','generation_mode':'open-ended','actions':available_data('Answer',SOURCE)['actions']}
        run=SimpleNamespace(status='completed',conversation_id='c1',metrics={'a2ui':{},'agentic_ui_variants':{'open-ended':ui}})
        self.assertIn('order-1',history_question(run,'c1','a0','open-ended'))
        with self.assertRaises(LookupError):history_question(run,'other','a0','open-ended')
        with self.assertRaises(ValueError):history_question(run,'c1','a7','open-ended')

    def test_open_ended_output_is_bounded_and_complete(self):
        self.assertEqual(validate_html('```html\n<html>ok</html>\n```'),'<html>ok</html>')
        for raw in ['<p>partial</p>','x'*100001]:
            with self.assertRaises(ValueError):validate_html(raw)
