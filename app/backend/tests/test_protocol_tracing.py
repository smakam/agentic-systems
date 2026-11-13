from contextlib import contextmanager
from types import SimpleNamespace
import pytest
from marketplace import protocol_tracing as tracing

def test_protocol_context_is_validated_and_propagates(monkeypatch):
    trace='1'*32; parent='2'*16
    monkeypatch.setattr(tracing,'_client',lambda:SimpleNamespace(
        get_current_trace_id=lambda:trace,get_current_observation_id=lambda:parent))
    headers=tracing.outgoing_headers()
    assert tracing.incoming_trace(headers['traceparent'])=={'trace_id':trace,'parent_span_id':parent}
    for value in ('invalid','00-'+'0'*32+'-'+parent+'-01','00-'+trace+'-'+'0'*16+'-01'):
        assert tracing.incoming_trace(value) is None

def test_protocol_failure_marks_span_without_recording_exception_secrets(monkeypatch,caplog):
    events=[]
    @contextmanager
    def start(**kwargs):
        events.append(kwargs)
        yield SimpleNamespace(update=lambda **value:events.append(value))
    monkeypatch.setattr(tracing,'_client',lambda:SimpleNamespace(start_as_current_observation=start))
    with pytest.raises(RuntimeError):
        with tracing.protocol_span('A2A delivery outbound',{'operation':'SendMessage'}):
            raise RuntimeError('private-credential-must-not-export')
    assert events[-1]['level']=='ERROR'
    assert 'private-credential' not in str(events)+caplog.text

def test_protocol_tracing_is_optional(monkeypatch):
    monkeypatch.setattr(tracing,'_client',lambda:None)
    assert tracing.outgoing_headers()=={}
    with tracing.protocol_span('Standard API request',{}) as span:assert span is None
