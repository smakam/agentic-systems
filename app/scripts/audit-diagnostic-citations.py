"""Offline strict audit of diagnostic responses; does not repair any output."""
import argparse,json,re
from pathlib import Path

def audit(path):
    data=json.loads(path.read_text());rows=[]
    for case in data['results']:
        prior=set()
        for index,turn in enumerate(case['turns'],1):
            answer=turn['run']['answer'];current=set(turn['run']['evidence']);allowed=current|prior
            # Broad extraction catches missing evidence- prefixes, spaces and chunk/query IDs.
            tokens=re.findall(r'\[[Ee][Vv][Ii][Dd][Ee][Nn][Cc][Ee][^\]\n]*(?:\]|$)',answer)
            citations=[]
            for token in tokens:
                exact=re.fullmatch(r'\[evidence:(evidence-[A-Za-z0-9_-]+)\]',token)
                handle=exact.group(1) if exact else None
                citations.append({'text':token,'exact_format':bool(exact),'handle_exists':bool(handle and handle in allowed),'source':'current' if handle in current else 'prior' if handle in prior else None})
            # Bare returned handles or raw hashes are flagged for manual inspection.
            outside=answer
            for token in tokens:outside=outside.replace(token,'')
            bare=re.findall(r'\bevidence-[A-Za-z0-9_-]+\b|\b[a-f0-9]{64}\b',outside)
            rows.append({'case':case['case']['id'],'model':case['model'],'turn':index,'question':turn['question'],'status':turn['run']['status'],'citations':citations,'bare_reference_candidates':bare,'citation_count':len(citations),'invalid_count':sum(not(c['exact_format'] and c['handle_exists']) for c in citations),'emitted_citations_valid':bool(citations) and all(c['exact_format'] and c['handle_exists'] for c in citations) and not bare,'no_citations':not citations,'note':'No citations is not automatically a pass: clarification may not need them; factual answers require manual coverage review.'})
            prior.update(current)
    return {'scope':'Exact citation syntax and reference existence, not claim entailment; prior-session references counted separately. Raw model text unchanged.','rows':rows}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('results');args=parser.parse_args();p=Path(args.results)
    result=audit(p);p.with_name('citation-audit.json').write_text(json.dumps(result,indent=2)+'\n')
    for r in result['rows']:print(r['case'],r['model'],r['turn'],'citations',r['citation_count'],'invalid',r['invalid_count'],'bare',len(r['bare_reference_candidates']))
