"""Deploy from authenticated Cloud Shell. No credentials serialized or printed."""
import argparse
import json
import os
from pathlib import Path
import agentplatform
from marketplace_google.agent import build_app
from backend_profiles import select_backend


def main():
    parser = argparse.ArgumentParser(description='Deploy or update the marketplace ADK lab.')
    parser.add_argument('--backend', choices=('local', 'cloud'),
                        help='Select a saved URL and secret reference together; update an existing runtime.')
    args = parser.parse_args()
    if args.backend:
        if not os.environ.get('GOOGLE_RUNTIME_RESOURCE'):
            parser.error('--backend requires GOOGLE_RUNTIME_RESOURCE to update the existing lab.')
        select_backend(args.backend, os.environ)
    project = os.environ['GOOGLE_CLOUD_PROJECT']
    location = os.environ['GOOGLE_CLOUD_LOCATION']
    client = agentplatform.Client(project=project, location=location)
    config = {
        'display_name': 'Marketplace Support ADK Lab',
        'description': 'Read-only remote MCP, native Sessions and Memory Bank',
        'staging_bucket': os.environ['GOOGLE_STAGING_BUCKET'],
        'requirements': Path('requirements.txt').read_text().splitlines(),
        'extra_packages': ['marketplace_google'],
        'python_version': '3.12',
        'min_instances': 0, 'max_instances': 1,
        'env_vars': {
            'GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY': 'true',
            'OTEL_SEMCONV_STABILITY_OPT_IN': 'gen_ai_latest_experimental',
            'OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT': 'EVENT_ONLY',
            'GOOGLE_GENAI_USE_ENTERPRISE': 'TRUE',
            'REMOTE_MCP_URL': os.environ['REMOTE_MCP_URL'],
            'BACKEND_PROFILE_CONFIG_VERSION': 'runtime-url-v1',
            'GOOGLE_MEMORY_ENABLED': os.environ.get('GOOGLE_MEMORY_ENABLED', 'true'),
            'REMOTE_MCP_API_KEY': {'secret': os.environ['GOOGLE_MCP_SECRET'],
                                   'version': os.environ.get('GOOGLE_MCP_SECRET_VERSION', '1')},
            'GOOGLE_AGENT_MODEL': os.environ.get('GOOGLE_AGENT_MODEL', 'gemini-3.5-flash'),
            'GOOGLE_MODEL_LOCATION': os.environ.get('GOOGLE_MODEL_LOCATION', 'us'),
        },
    }
    if os.environ.get('GOOGLE_RUNTIME_SERVICE_ACCOUNT'):
        config['service_account'] = os.environ['GOOGLE_RUNTIME_SERVICE_ACCOUNT']
    existing = os.environ.get('GOOGLE_RUNTIME_RESOURCE')
    if existing:
        # Keep the trace association identical to the deployed resource name.
        # Capture every lab invocation; production sampling is a separate choice.
        config['env_vars']['OTEL_RESOURCE_ATTRIBUTES'] = 'cloud.resource_id=//aiplatform.googleapis.com/' + existing
        config['env_vars']['OTEL_TRACES_SAMPLER'] = 'always_on'
        runtime = client.runtimes.update(name=existing, agent=build_app(), config=config)
    else:
        runtime = client.runtimes.create(agent=build_app(), config=config)
    result = {'resource_name': runtime.api_resource.name, 'project': project, 'location': location,
              'mcp_url': os.environ['REMOTE_MCP_URL'],
              'mcp_secret': os.environ['GOOGLE_MCP_SECRET'],
              'mcp_secret_version': os.environ.get('GOOGLE_MCP_SECRET_VERSION', '1')}
    if args.backend:
        result['backend'] = args.backend
    Path('deployment.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
