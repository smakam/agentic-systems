"""Prepare optional gateway config without persisting credential values."""
from pathlib import Path

root=Path(__file__).resolve().parents[1]
env={}
for line in (root/'.env').read_text().splitlines():
 if '=' in line and not line.lstrip().startswith('#'):
  k,v=line.split('=',1);env[k.strip()]=v.strip().strip('"').strip("'")
if not env.get('LAKERA_API_KEY'):
 raise SystemExit('Add LAKERA_API_KEY to app/.env first. No config activated.')
fragment=(root/'infra/lakera-guardrail.fragment.yaml').read_text()
if env.get('LAKERA_PROJECT_ID'):
 fragment+='      project_id: os.environ/LAKERA_PROJECT_ID\n'
out=root/'infra/litellm.lakera.generated.yaml'
out.write_text((root/'infra/litellm.yaml').read_text()+'\n'+fragment)
print('Generated credential-free '+str(out))
