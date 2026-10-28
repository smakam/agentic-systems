"""Load optional cloud guardrails only when their dependencies are configured."""
import copy
import os
from pathlib import Path


def configured_guardrails(config, environment):
    result = copy.deepcopy(config)
    analyzer = bool(environment.get('PRESIDIO_ANALYZER_API_BASE'))
    anonymizer = bool(environment.get('PRESIDIO_ANONYMIZER_API_BASE'))
    if analyzer != anonymizer:
        raise ValueError('Configure both Presidio sidecar endpoints together.')
    lakera = environment.get('LAKERA_API_KEY', '') not in ('', 'not-configured')
    kept = []
    for guardrail in result.get('guardrails', []):
        params = guardrail.get('litellm_params', {})
        kind = params.get('guardrail')
        unavailable = (kind == 'presidio' and not analyzer) or (kind == 'lakera_v2' and not lakera)
        if unavailable:
            # A future mandatory control must fail closed, never be silently removed.
            if params.get('default_on', False):
                raise ValueError('A mandatory guardrail has an unconfigured dependency.')
            continue
        kept.append(guardrail)
    result['guardrails'] = kept
    return result


def main():
    import yaml  # Provided by the pinned LiteLLM image.
    config = yaml.safe_load(Path('/app/config.yaml').read_text())
    selected = configured_guardrails(config, os.environ)
    target = Path('/tmp/marketplace-gateway.yaml')
    target.write_text(yaml.safe_dump(selected, sort_keys=False))
    target.chmod(0o600)
    print('Cloud gateway configuration ready; unconfigured opt-in external hooks omitted.', flush=True)
    os.execvp('litellm', ['litellm', '--config', str(target), '--port', os.environ.get('PORT', '8080')])


if __name__ == '__main__':
    main()
