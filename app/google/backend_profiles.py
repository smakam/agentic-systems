"""Select a URL and Secret Manager reference together; never store key values."""
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


def select_backend(name, environ, path=None):
    path = path or Path(__file__).with_name('backend_profiles.json')
    profile = json.loads(Path(path).read_text())[name]
    url, secret, version = (profile[field] for field in ('url', 'secret', 'version'))
    parsed = urlsplit(url)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError('Backend profile requires an HTTPS URL without credentials.')
    if not isinstance(secret, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', secret) or not str(version).isdigit():
        raise ValueError('Backend profile requires a Secret Manager reference and numeric version.')
    # Validate the complete pair before replacing any current configuration.
    environ.update(REMOTE_MCP_URL=url, GOOGLE_MCP_SECRET=secret,
                   GOOGLE_MCP_SECRET_VERSION=str(version))
    return profile
