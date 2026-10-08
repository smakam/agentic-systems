#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
state=.remote-mcp
mkdir -p "$state"
compose=(docker compose -f compose.yaml -f compose.remote-mcp.yaml)
case "${1:-status}" in
 start)
  python3 - <<'PY'
from pathlib import Path
import secrets
p=Path('.remote-mcp.env')
if not p.exists():
 p.write_text('REMOTE_MCP_API_KEY='+secrets.token_urlsafe(48)+'\nREMOTE_MCP_ALLOWED_HOSTS=\n')
p.chmod(0o600)
PY
  if [[ ! -x "$state/cloudflared" ]]; then
   python3 - <<'PY'
import urllib.request,json,hashlib,tarfile,platform
from pathlib import Path
if platform.system()!='Darwin': raise SystemExit('This lab launcher supports macOS. Install cloudflared from the official vendor for other hosts.')
arch='arm64' if platform.machine()=='arm64' else 'amd64'
r=json.load(urllib.request.urlopen('https://api.github.com/repos/cloudflare/cloudflared/releases/latest'))
a=next(x for x in r['assets'] if x['name']==f'cloudflared-darwin-{arch}.tgz')
b=urllib.request.urlopen(a['browser_download_url']).read();digest=hashlib.sha256(b).hexdigest()
if a.get('digest'): assert a['digest']=='sha256:'+digest,'Checksum mismatch'
else: assert digest in r['body'],'Checksum absent or mismatched'
p=Path('.remote-mcp/cloudflared.tgz');p.write_bytes(b)
with tarfile.open(p) as t:t.extractall('.remote-mcp',filter='data')
Path('.remote-mcp/cloudflared').chmod(0o700)
print('Verified Cloudflare release',r['tag_name'])
PY
  fi
  "${compose[@]}" up -d --no-deps remote-mcp
  if [[ ! -f "$state/tunnel.pid" ]] || ! kill -0 "$(cat "$state/tunnel.pid")" 2>/dev/null; then
   nohup "$state/cloudflared" tunnel --url http://127.0.0.1:58001 --no-autoupdate --protocol http2 > "$state/tunnel.log" 2>&1 < /dev/null &
   echo "$!" > "$state/tunnel.pid"
  fi
  python3 - <<'PY'
from pathlib import Path
import re,time
p=Path('.remote-mcp/tunnel.log')
for _ in range(45):
 s=p.read_text() if p.exists() else ''
 matches=re.findall(r'https://[a-z0-9-]+\.trycloudflare\.com',s)
 if matches: break
 time.sleep(1)
else: raise SystemExit('Tunnel URL unavailable; inspect .remote-mcp/tunnel.log')
url=matches[-1];host=url.split('//')[1]
e=Path('.remote-mcp.env');s=e.read_text();s=re.sub(r'^REMOTE_MCP_ALLOWED_HOSTS=.*$',f'REMOTE_MCP_ALLOWED_HOSTS={host}',s,flags=re.M);e.write_text(s);e.chmod(0o600)
Path('.remote-mcp/endpoint.txt').write_text(url+'/mcp\n')
print('Allocated MCP endpoint (awaiting readiness):',url+'/mcp')
PY
  "${compose[@]}" up -d --no-deps remote-mcp
  python3 - <<'READY'
from pathlib import Path
import json,time,urllib.request,urllib.error
url=Path('.remote-mcp/endpoint.txt').read_text().strip()
settings=dict(line.split('=',1) for line in Path('.remote-mcp.env').read_text().splitlines() if '=' in line)
headers={'x-api-key':settings['REMOTE_MCP_API_KEY'],'Content-Type':'application/json','Accept':'application/json, text/event-stream'}
payload=json.dumps({'jsonrpc':'2.0','id':1,'method':'initialize','params':{'protocolVersion':'2025-03-26','capabilities':{},'clientInfo':{'name':'readiness','version':'1'}}}).encode()
deadline=time.monotonic()+120
last='not checked'
while time.monotonic()<deadline:
 try:
  with urllib.request.urlopen(urllib.request.Request(url,data=payload,headers=headers),timeout=5) as response:
   data=json.load(response)
   if 'result' in data and 'serverInfo' in data['result']:
    print('MCP ready: authenticated public initialization succeeded:',url)
    break
   last='unexpected initialization response'
 except urllib.error.HTTPError as exc: last='HTTP '+str(exc.code)
 except (OSError,ValueError) as exc: last=type(exc).__name__
 time.sleep(2)
else: raise SystemExit('MCP endpoint is not ready ('+last+'); inspect .remote-mcp/tunnel.log. Do not update Studio yet.')
READY
  ;;
 stop)
  if [[ -f "$state/tunnel.pid" ]]; then kill "$(cat "$state/tunnel.pid")" 2>/dev/null || true; rm "$state/tunnel.pid"; fi
  "${compose[@]}" stop remote-mcp
  ;;
 status)
  "${compose[@]}" ps remote-mcp
  [[ ! -f "$state/endpoint.txt" ]] || cat "$state/endpoint.txt"
  ;;
 *) echo 'Usage: scripts/remote-mcp.sh start|stop|status' >&2; exit 2;;
esac
