"""Allowlist deployable source; never archive .env, state, results or credentials."""
import argparse
from pathlib import Path
import tarfile


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    app=Path(__file__).resolve().parents[2]
    files=[app/'.dockerignore',app/'backend/requirements.txt',app/'frontend/package.json',app/'frontend/package-lock.json',app/'frontend/index.html',app/'frontend/vite.config.js']
    for folder,pattern in [('backend/marketplace','*.py'),('frontend/src','*'),('data','*'),('cloud','Dockerfile.*'),('cloud/scripts','*.py')]:
        files.extend(p for p in (app/folder).rglob(pattern) if p.is_file() and '__pycache__' not in p.parts)
    for name in ['litellm.yaml','gateway_audit.py','lakera-guardrail.fragment.yaml']:
        path=app/'infra'/name
        if path.exists(): files.append(path)
    with tarfile.open(args.output,'w:gz') as archive:
        for path in sorted(set(files)):
            archive.add(path,arcname=str(path.relative_to(app)),recursive=False)
    print(f'Packaged {len(set(files))} source files; secrets/state/results excluded.')


if __name__=='__main__': main()
