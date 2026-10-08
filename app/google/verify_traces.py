"""Read Cloud Trace and correlate the hosted memory suite's session IDs.

Use Cloud Shell credentials; this only reads telemetry and writes local results.
Run after verify_memory.py, allowing trace ingestion time before checking.
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import google.auth
from google.auth.transport.requests import AuthorizedSession


def main():
    settings = json.loads(Path('deployment.json').read_text())
    cases = json.loads(Path('memory-verification-results.json').read_text())
    credentials, _ = google.auth.default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
    transport = AuthorizedSession(credentials)
    now = datetime.now(timezone.utc)
    params = dict(startTime=(now-timedelta(hours=1)).isoformat(), endTime=now.isoformat(), view='COMPLETE', pageSize=100, orderBy='start desc')
    traces = []
    for _ in range(30):
        response = transport.get(f"https://cloudtrace.googleapis.com/v1/projects/{settings['project']}/traces", params=params, timeout=60)
        response.raise_for_status()
        data = response.json()
        traces.extend(data.get('traces', []))
        if not data.get('nextPageToken'):
            break
        params['pageToken'] = data['nextPageToken']
    else:
        raise RuntimeError('More trace pages remain; this is not a complete read')
    Path('trace-verification-results.json').write_text(json.dumps(traces, indent=2))
    missing = []
    for case in cases:
        matches = [t for t in traces if any(s.get('labels', {}).get('gen_ai.conversation.id') == case['session'] for s in t.get('spans', []))]
        print(json.dumps(dict(label=case['label'], session=case['session'], trace_ids=[t['traceId'] for t in matches], span_names=sorted({s['name'] for t in matches for s in t['spans']}))))
        if not matches:
            missing.append(case['label'])
    if missing:
        raise RuntimeError(f'Trace correlation is not verified for {missing}; check ingestion before retrying')
    print('All test sessions have correlated Cloud Trace spans. Inspect native UI separately.')


if __name__ == '__main__':
    main()
