"""Update only the existing, manifest-identified Support Agent Basics deployment."""
import json
from pathlib import Path
from urllib.parse import urlsplit


def update_config(resource):
    if resource.display_name != 'Support Agent Basics':
        raise ValueError('Refusing to update a deployment other than Support Agent Basics')
    spec=resource.spec
    if spec.deployment_spec.secret_env:
        raise ValueError('Review this deployment configuration: unexpected secret bindings')
    bucket=urlsplit(spec.package_spec.pickle_object_gcs_uri).netloc
    if not bucket or not spec.service_account:
        raise ValueError('Existing staging bucket and runtime identity are required')
    return {
        'display_name':resource.display_name,
        'description':'Standalone fictional orders with explicit native preference saves',
        'staging_bucket':'gs://'+bucket,
        'service_account':spec.service_account,
        'requirements':Path(__file__).with_name('requirements.txt').read_text().splitlines(),
        'extra_packages':['support_agent_basics'],
        'python_version':spec.package_spec.python_version,
        'min_instances':spec.deployment_spec.min_instances,
        'max_instances':spec.deployment_spec.max_instances,
        'env_vars':{v.name:v.value for v in spec.deployment_spec.env},
    }


def main():
    import agentplatform
    from support_agent_basics.agent import build_app
    manifest=json.loads(Path(__file__).with_name('support-basics-deployment.json').read_text())
    name=manifest['resource_name']
    prefix=f"projects/{name.split('/')[1]}/locations/{manifest['location']}/reasoningEngines/"
    if not name.startswith(prefix) or manifest.get('display_name')!='Support Agent Basics':
        raise ValueError('A valid Basics deployment manifest is required')
    client=agentplatform.Client(project=manifest['project'],location=manifest['location'])
    old=client.runtimes.get(name=name)
    config=update_config(old.api_resource)
    if config['env_vars'].get('GOOGLE_MEMORY_ENABLED','true').lower()!='true':
        raise ValueError('Enable native memory intentionally before updating')
    result=client.runtimes.update(name=name,agent=build_app(),config=config)
    if result.api_resource.name!=name:
        raise RuntimeError('Unexpected resource returned by update')
    receipt={'resource_name':name,'display_name':result.api_resource.display_name,
             'feature':'explicit-native-preference-save','status':'deployment-update-completed',
             'live_memory_verification':'pending'}
    Path(__file__).with_name('support-basics-memory-update.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))


if __name__=='__main__':main()
