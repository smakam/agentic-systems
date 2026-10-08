"""Package only baseline learner source; never copy local credentials or state."""
import hashlib, json, tarfile, argparse
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('output',type=Path); a=p.parse_args()
root=Path(__file__).resolve().parents[3]
app=root/'app'
roots=['backend','frontend','infra','data','scripts','eval']
files=[app/'compose.yaml',app/'compose.memory.yaml',app/'.env.example',app/'LOCAL-SETUP.md']
excluded={'.git','.env','.venv','node_modules','dist','__pycache__','.pytest_cache','.google-auth','.backend-switch','.remote-mcp'}
for name in roots:
    files.extend(x for x in (app/name).rglob('*') if x.is_file() and not any(part in excluded for part in x.relative_to(app).parts) and not x.name.endswith(('.pyc','.log')) and x.name!='litellm.lakera.generated.yaml')
# No cloud scripts, results, ignored access notes or service credentials are included.
with tarfile.open(a.output,'w:gz') as t:
    for x in sorted(set(files)):
        if x.is_symlink(): raise RuntimeError('Refusing symlink '+str(x))
        t.add(x,arcname=str(x.relative_to(root)))
receipt={'source':'unpublished sanitized working-tree archive; not GitHub clone validation','files':len(set(files)),'sha256':hashlib.sha256(a.output.read_bytes()).hexdigest()}
a.output.with_suffix('.receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
