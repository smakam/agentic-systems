"""Small teaching loop: no Agents SDK runner; adapters own network connections."""
import copy
import json

async def run_loop(model, execute, tools, question, *, instructions, max_turns=8):
    if max_turns < 1:
        raise ValueError('max_turns must be positive')
    allowed = {t['function']['name'] for t in tools}
    messages = [{'role': 'system', 'content': instructions}, {'role': 'user', 'content': question}]
    events = []
    for turn in range(1, max_turns + 1):
        response = await model(copy.deepcopy(messages), tools)
        calls = response.get('tool_calls') or []
        # A text response with outstanding tool calls is not a final answer.
        events.append({'kind': 'model', 'turn': turn, 'response': response})
        messages.append({'role': 'assistant', 'content': response.get('content'), **({'tool_calls': calls} if calls else {})})
        if not calls:
            answer = response.get('content')
            return {'status': 'completed' if answer else 'incomplete', 'answer': answer,
                    'turns': turn, 'messages': messages, 'events': events}
        for call in calls:
            name = call['function']['name']
            try:
                args = json.loads(call['function']['arguments'])
                if name not in allowed or not isinstance(args, dict):
                    raise ValueError('Tool is not allowed or arguments are not an object')
                result = await execute(name, args)
            except (ValueError, TypeError):
                result = {'status': 'error', 'code': 'INVALID_TOOL_REQUEST',
                          'message': 'Use an allowed tool with valid JSON object arguments. This is not an empty result.'}
            # Operational adapter failures should stop, not be disguised as model errors.
            messages.append({'role': 'tool', 'tool_call_id': call['id'],
                             'content': json.dumps(result, default=str)})
            events.append({'kind': 'tool', 'turn': turn, 'name': name, 'arguments': call['function']['arguments'], 'result': result})
    return {'status': 'turn_limit', 'answer': 'Investigation incomplete: model-turn limit reached.',
            'turns': max_turns, 'messages': messages, 'events': events}
