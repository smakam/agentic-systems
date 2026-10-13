"""Bind a gateway identity to one authenticated request, never process-wide."""
from contextlib import contextmanager
from contextvars import ContextVar
import os

_selected_key = ContextVar("marketplace_gateway_key", default=None)

def current_key():
    return _selected_key.get() or os.getenv("LITELLM_API_KEY")

@contextmanager
def for_key(key):
    token = _selected_key.set(key)
    try:
        yield
    finally:
        _selected_key.reset(token)

@contextmanager
def for_role(role):
    # Existing deployments without an Operator key retain their configured route.
    # Startup provisions distinct keys for the local Chapter Six course stack.
    key = os.getenv("OPERATOR_GATEWAY_KEY") if role == "operator" else None
    token = _selected_key.set(key or os.getenv("LITELLM_API_KEY"))
    try:
        yield
    finally:
        _selected_key.reset(token)
