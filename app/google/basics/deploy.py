"""Create a NEW Support Agent Basics runtime; never update the existing lab."""
import json
import os
from pathlib import Path
from support_agent_basics.tools import load_fixture

MANIFEST = Path(__file__).with_name('support-basics-deployment.json')

def deployment_config():
    return {
        'display_name':'Support Agent Basics',
        'description':'Standalone fictional-order native tools, Sessions and Memory Bank',
        'staging_bucket':os.environ['GOOGLE_STAGING_BUCKET'],
        'requirements':Path(__file__).with_name('requirements.txt').read_text().splitlines(),
        'extra_packages':['support_agent_basics'], 'python_version':'3.12',
        'min_instances':0,'max_instances':1,
        'service_account':os.environ['GOOGLE_RUNTIME_SERVICE_ACCOUNT'],
        'env_vars':{
            'GOOGLE_CLOUD_AGENT_ENGINE_ENABLE_TELEMETRY':'true',
            'OTEL_SEMCONV_STABILITY_OPT_IN':'gen_ai_latest_experimental',
            'OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT':'EVENT_ONLY',
            'OTEL_TRACES_SAMPLER':'always_on',
            'GOOGLE_GENAI_USE_ENTERPRISE':'TRUE',
            'GOOGLE_MEMORY_ENABLED':os.environ.get('GOOGLE_MEMORY_ENABLED','true'),
            'GOOGLE_AGENT_MODEL':os.environ.get('GOOGLE_AGENT_MODEL','gemini-3.5-flash'),
            'GOOGLE_MODEL_LOCATION':os.environ.get('GOOGLE_MODEL_LOCATION','us'),
        },
    }

def main():
    if MANIFEST.exists():
        raise SystemExit('A Basics deployment manifest already exists; inspect it before creating another runtime.')
    # Intentionally ignores GOOGLE_RUNTIME_RESOURCE belonging to the existing lab.
    # There is no update/delete operation in this script.
    load_fixture()
    import agentplatform
    from support_agent_basics.agent import build_app
    project=os.environ['GOOGLE_CLOUD_PROJECT'];location=os.environ.get('GOOGLE_CLOUD_LOCATION','us-central1')
    config=deployment_config()
    client=agentplatform.Client(project=project,location=location)
    runtime=client.runtimes.create(agent=build_app(),config=config)
    manifest={'resource_name':runtime.api_resource.name,'project':project,'location':location,
              'display_name':'Support Agent Basics','app_name':'support_agent_basics',
              'dataset_id':load_fixture()['dataset_id'],'memory_enabled':config['env_vars']['GOOGLE_MEMORY_ENABLED']=='true'}
    MANIFEST.write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps(manifest,indent=2))

if __name__=='__main__':main()
