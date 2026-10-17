"""Topic-based lab settings with compatibility for existing deployments."""
import os

_LEGACY = {
    'AGENT_LOOP_LAB': 'CH11_LOOP_LAB',
    'HOSTING_LAB': 'CH12_HOSTING_LAB',
    'HOSTED_AGENT_URL': 'CH12_AGENT_URL',
    'HOSTED_AGENT_API_KEY': 'CH12_AGENT_API_KEY',
    'HOSTED_AGENT_MODEL': 'CH12_MODEL',
}

def setting(name, default=''):
    # Presence takes precedence, including an explicitly empty new value.
    return os.environ.get(name, os.environ.get(_LEGACY.get(name, ''), default))
