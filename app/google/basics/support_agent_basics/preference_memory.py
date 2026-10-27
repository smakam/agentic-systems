"""Explicit presentation-preference saves through the native ADK memory service."""
import os
import re

from google.adk.events import Event
from google.adk.tools import ToolContext
from google.genai import types


def _normalized(value):
    return ' '.join(value.casefold().split())


async def remember_preference(preference: str, tool_context: ToolContext) -> dict:
    """Request native memory generation for a presentation preference explicitly supplied now.

    Use only when the user starts the current message with 'Remember' or 'Please
    remember' (or 'Save ... to memory'). Copy their answer-format preference
    faithfully. Never use for order facts, inferred preferences or earlier turns.
    User, app and session scope come from ADK; there are no identity arguments.
    A successful call requests generation, not proof of stored or recalled memory.
    """
    if os.environ.get('GOOGLE_MEMORY_ENABLED', 'true').lower() != 'true':
        return {'status': 'disabled', 'generation_requested': False}
    if not isinstance(preference, str) or not 1 <= len(preference.strip()) <= 500:
        return {'status': 'invalid_preference', 'generation_requested': False}
    content = tool_context.user_content
    message = ' '.join(p.text for p in (content.parts if content else []) if p.text)
    directive = re.match(r'^\s*(?:please[,\s]+)?(?:remember\b|save\b.*\b(?:memory|preference)\b)', message, re.I)
    if not directive or _normalized(preference) not in _normalized(message):
        return {'status': 'explicit_request_required', 'generation_requested': False,
                'message': 'Ask the user to state the preference explicitly, starting with Remember.'}
    if not re.search(r'\b(format|answers?|responses?|tables?|paragraphs?|bullets?|columns?|concise|brief|detail(?:ed)?)\b', preference, re.I):
        return {'status': 'presentation_preference_required', 'generation_requested': False}
    # Send only the requested preference, not the entire order-investigation history.
    event = Event(author='user', content=types.Content(
        role='user', parts=[types.Part(text=preference.strip())]))
    try:
        await tool_context.add_events_to_memory(events=[event], custom_metadata={'wait_for_completion': False})
    except Exception:
        # Do not expose provider messages, credentials or uncertain success as a save.
        return {'status': 'generation_unconfirmed', 'generation_requested': False,
                'message': 'Memory generation could not be confirmed; do not claim it was saved.'}
    return {'status': 'generation_requested', 'generation_requested': True,
            'message': 'Generation requested for this user. Storage and fresh-session recall still need verification.'}
