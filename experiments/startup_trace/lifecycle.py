"""Process-event identity and durable launcher refusal; no target operations."""
from core import need


def same_stop(process, stop_id, api):
    need(process.GetState() == api.eStateStopped and process.GetStopID() == stop_id,
         'process left the admitted stop')


def stopped_event(event, process, api):
    """Consume a dedicated listener event before inspecting any stopped thread.

    Loader notifications that LLDB already restarted are not user stops. This
    function never continues a target and never obtains a frame or register.
    """
    if not api.SBProcess.EventIsProcessEvent(event):
        return False
    owner = api.SBProcess.GetProcessFromEvent(event)
    need(owner.IsValid() and owner.GetUniqueID() == process.GetUniqueID() and
         owner.GetProcessID() == process.GetProcessID(), 'event process identity changed')
    if not event.GetType() & api.SBProcess.eBroadcastBitStateChanged:
        return False
    state = api.SBProcess.GetStateFromEvent(event)
    if state != api.eStateStopped or api.SBProcess.GetRestartedFromEvent(event):
        return False
    need(process.GetState() == api.eStateStopped, 'stop event no longer describes a stopped process')
    return True


def debugger_exit(record, returncode, request_intent):
    need(type(returncode) is int, 'debugger exit code unavailable')
    return {'status': 'DEBUGGER_EXITED_WITHOUT_RESULT', 'cleanup_safe': False,
            'kind': record['kind'], 'source_commit': record['source_commit'],
            'collector_sha256': record['collector_sha256'],
            'debugger_exit_code': returncode, 'detach': 'UNKNOWN',
            'publication': 'UNKNOWN' if request_intent else 'NOT_SENT',
            'reason': 'debugger exited before final collector journal; no retry or target action',
            'scope': 'launcher observation only; host state and exit cause UNKNOWN'}
