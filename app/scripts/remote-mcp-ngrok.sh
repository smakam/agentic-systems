#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
state=.remote-mcp
compose=(docker compose -f compose.yaml -f compose.remote-mcp.yaml -f compose.ngrok.yaml)
case "${1:-status}" in
 start)
  [[ -x "$state/ngrok" && -f "$state/ngrok.yml" && -f "$state/ngrok-domain.txt" ]] || { echo 'Configure ngrok credentials and assigned domain first.' >&2; exit 2; }
  "$state/ngrok" config check --config "$state/ngrok.yml"
  runtime="$HOME/Library/Application Support/marketplace-mcp"
  mkdir -p "$runtime"
  chmod 700 "$runtime"
  cp "$state/ngrok" "$runtime/ngrok"
  cp "$state/ngrok.yml" "$runtime/ngrok.yml"
  chmod 700 "$runtime/ngrok"
  chmod 600 "$runtime/ngrok.yml"
  python3 - <<'CONFIG'
from pathlib import Path
import re
host=Path('.remote-mcp/ngrok-domain.txt').read_text().strip()
if not re.fullmatch(r'[a-z0-9-]+\.ngrok-free\.(dev|app)',host):raise SystemExit('Expected account-assigned ngrok dev domain')
p=Path('.remote-mcp.env')
if not p.exists():raise SystemExit('Existing MCP key file required; use the lab setup first')
s=p.read_text();s=re.sub(r'^REMOTE_MCP_ALLOWED_HOSTS=.*$',f'REMOTE_MCP_ALLOWED_HOSTS={host}',s,flags=re.M)
p.write_text(s);p.chmod(0o600)
Path('.remote-mcp/endpoint.txt').write_text('https://'+host+'/mcp\n')
CONFIG
  "${compose[@]}" up -d postgres gateway remote-mcp
  service="gui/$(id -u)/tech.marketplace-lab.ngrok"
  plist="$HOME/Library/LaunchAgents/tech.marketplace-lab.ngrok.plist"
  [[ -f "$plist" ]] || { echo 'Install the ngrok login service first.' >&2; exit 2; }
  launchctl enable "$service"
  if launchctl print "$service" >/dev/null 2>&1; then
   launchctl kickstart "$service"
  else
   launchctl bootstrap "gui/$(id -u)" "$plist"
  fi
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
  service="gui/$(id -u)/tech.marketplace-lab.ngrok"
  launchctl disable "$service"
  launchctl bootout "$service" 2>/dev/null || true
  "${compose[@]}" stop remote-mcp
  ;;
 status)
  "${compose[@]}" ps remote-mcp
  [[ ! -f "$state/endpoint.txt" ]] || cat "$state/endpoint.txt"
  launchctl print "gui/$(id -u)/tech.marketplace-lab.ngrok" 2>/dev/null | grep -E 'state =|pid =|last exit code =' || true
  ;;
 *) echo 'Usage: scripts/remote-mcp-ngrok.sh start|stop|status' >&2; exit 2;;
esac
