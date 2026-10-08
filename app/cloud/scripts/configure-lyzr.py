#!/usr/bin/env python3
"""Private Lyzr inference-key entry after Terraform provisions the secret."""
import argparse
import getpass
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project', required=True)
    args = parser.parse_args()
    print(f'Lyzr inference credential destination: {args.project}/marketplace-web-lyzr-api-key')
    print('Use the Lyzr inference API key, not the marketplace MCP API key.')
    if input('Type the project ID to confirm: ').strip() != args.project:
        raise SystemExit('Project confirmation did not match; nothing changed.')
    value = getpass.getpass('Lyzr inference API key (hidden): ').strip()
    if not value:
        raise SystemExit('Empty key; nothing changed.')
    result = subprocess.run([
        'gcloud', 'secrets', 'versions', 'add', 'marketplace-web-lyzr-api-key',
        '--project', args.project, '--data-file=-', '--quiet'],
        input=value, text=True, capture_output=True)
    del value
    if result.returncode:
        raise SystemExit('Secret write failed; inspect project/secret access and retry. Secret values were not logged.')
    print('Lyzr inference secret configured. The runtime still needs deployment and validation.')


if __name__ == '__main__':
    main()
