"""Resume only a credit-interrupted question; preserve every paid/completed attempt."""
from pathlib import Path
import hashlib,json
script=Path('/scripts/routing-granularity.py');source=script.read_text()
old="""   if existing:
    assert existing['status']=='complete','Interrupted scenario: preserve it and use a new run rather than overwrite';continue
"""
new="""   if existing and existing['status']=='complete':continue
   resume=bool(existing)
   if resume:
    assert existing['key']=='S2-conversation', 'Resume reviewed only for the saved credit interruption'
    assert len(existing['turns'])==2 and existing['turns'][-1]['run']['status']=='failed'
    assert existing['turns'][-1]['run']['metrics']['error_type']=='RateLimitError'
    existing.setdefault('interrupted_attempts',[]).append(existing['turns'].pop())
    saved_items=json.loads((OUT/'interrupted-session.json').read_text())
    assert len(saved_items)==3 and saved_items[-1]['role']=='user'
    saved_items=saved_items[:-1]  # SDK persisted the failed user ask; retry must add it only once.
    state.setdefault('resumptions',[]).append({'reason':'OpenAI credits replenished; retry failed question only','resume_script_sha256':RESUME_HASH,'kept_completed_turns':len(existing['turns']),'failed_attempt_retained':True})
    save()
"""
assert old in source;source=source.replace(old,new)
source=source.replace("with Session.begin() as db:db.add(Conversation(id=cid,owner_id='support',title=key,items=[]))", "with Session.begin() as db:db.add(Conversation(id=cid,owner_id='support',title=key,items=saved_items if resume else []))")
old="""   record={'key':key,'session':s['id'],'policy':policy,'conversation_id':cid,'turns':[],'status':'running'};state['results'].append(record);save();pinned=None"""
new="""   record=existing if resume else {'key':key,'session':s['id'],'policy':policy,'conversation_id':cid,'turns':[],'status':'running'}
   if not resume:state['results'].append(record)
   save();pinned=record['turns'][0]['decision'] if resume else None"""
assert old in source;source=source.replace(old,new)
source=source.replace("mutate(f,turn);validate(s['id'],idx);before=fingerprint();q=turn['question']", "mutate(f,turn);validate(s['id'],idx)\n    if resume and idx<len(record['turns']):continue\n    before=fingerprint();q=turn['question']")
# The original source hash remains its honest value; the explicit resume patch hash is recorded separately.
exec(compile(source,str(script),'exec'),{'__name__':'__main__','__file__':str(script),'RESUME_HASH':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
