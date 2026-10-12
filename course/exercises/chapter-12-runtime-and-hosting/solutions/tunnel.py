"""Start/stop only the Chapter 12 middleware tunnel; keep other tunnels intact."""
import argparse,os,re,signal,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];APP=ROOT/'app'
def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['start','stop']);a=p.parse_args()
    pidfile=APP/'.ch12-tunnel.pid';log=APP/'.ch12-tunnel.log'
    if a.action=='stop':
        if pidfile.exists():
            pid=int(pidfile.read_text())
            command=subprocess.run(['ps','-p',str(pid),'-o','command='],capture_output=True,text=True).stdout
            if 'cloudflared' in command and '58013' in command:os.kill(pid,signal.SIGTERM)
            elif command.strip():raise SystemExit('PID was reused; refusing to stop unrelated process.')
            pidfile.unlink()
        print('Chapter 12 tunnel stopped.');return
    if pidfile.exists():raise SystemExit('Existing Chapter 12 PID file preserved; stop the tunnel before restarting.')
    binary=APP/'.remote-mcp/cloudflared'
    if not binary.exists():raise SystemExit('Install cloudflared or complete the existing remote-MCP tunnel setup first.')
    with log.open('w') as output:
        proc=subprocess.Popen([str(binary),'tunnel','--no-autoupdate','--url','http://localhost:58013'],stdout=output,stderr=output,start_new_session=True)
    pidfile.write_text(str(proc.pid))
    for _ in range(60):
        found=re.search(r'https://[a-z0-9-]+\.trycloudflare\.com',log.read_text())
        if found:print(found.group()+'/mcp');return
        if proc.poll() is not None:raise SystemExit('Tunnel exited; inspect app/.ch12-tunnel.log.')
        time.sleep(.5)
    raise SystemExit('No tunnel URL yet; inspect the log. A running PID is recorded for cleanup.')
if __name__=='__main__':main()
