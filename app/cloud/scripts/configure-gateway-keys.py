"""Provision scoped cloud gateway keys without printing credentials."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    parser.add_argument('--gateway', required=True)
    args = parser.parse_args()
    if not args.gateway.startswith('https://marketplace-gateway-') or not args.gateway.endswith('.run.app'):
        raise SystemExit('Expected the deployed marketplace gateway HTTPS URL.')
    spec = importlib.util.spec_from_file_location('credentials', Path(__file__).with_name('configure-cloud.py'))
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    google = config.Google(args.project)
    identity = subprocess.check_output(['gcloud', 'auth', 'print-identity-token'], text=True).strip()
    master = google.secret('gateway-master-key')
    if not master:
        raise SystemExit('Gateway master credential is missing.')

    def call(path, method='GET', body=None):
        request = Request(args.gateway + path, method=method,
                          data=json.dumps(body).encode() if body is not None else None,
                          headers={'Authorization': 'Bearer ' + master,
                                   'X-Serverless-Authorization': 'Bearer ' + identity,
                                   'Content-Type': 'application/json'})
        try:
            with urlopen(request, timeout=180) as response:
                return json.load(response)
        except HTTPError as error:
            code = error.code
            error.close()
            raise RuntimeError(f'Gateway returned HTTP {code}; inspect service status.') from None

    call('/health/liveliness')
    for secret, alias, models in [('web-support-key', 'marketplace-cloud-support', ['support-model', 'embedding']),
                                  ('mcp-embedding-key', 'marketplace-cloud-embedding', ['embedding'])]:
        key = google.secret(secret)
        if key:
            info = call('/key/info?' + urlencode({'key': key}))['info']
            if set(info.get('models', [])) != set(models):
                raise RuntimeError('Existing virtual key scope differs; review before changing access.')
        else:
            key = call('/key/generate', 'POST', {'key_alias': alias, 'models': models,
                                               'metadata': {'purpose': alias, 'project': args.project}})['key']
            google.store(secret, key)
        print(f'{alias}: ready; credential withheld', flush=True)


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError) as error:
        message = str(error) if isinstance(error, RuntimeError) else 'Connection or response failure; inspect service status.'
        raise SystemExit(message) from None
