"""Bounded debugger stop metadata; no frames, registers or target memory.

Classification describes why an observation is refused. It never authorizes a
resume, fixes a host fault, or identifies an ordinary effect's registration lane.
"""
from core import need

MAX_THREADS = 256


def capture(process, api):
    state, stop_id, total = int(process.GetState()), int(process.GetStopID()), process.GetNumThreads()
    # Oversized inventories keep a small diagnostic prefix, then refuse.
    count = min(total, 8) if total > MAX_THREADS else total
    threads = []
    for index in range(count):
        thread = process.GetThreadAtIndex(index)
        reason, size = int(thread.GetStopReason()), thread.GetStopReasonDataCount()
        breakpoint = reason == api.eStopReasonBreakpoint
        row = {'index': index, 'id': int(thread.GetThreadID()), 'reason': reason,
               'none': reason == api.eStopReasonNone, 'breakpoint': breakpoint,
               'reason_data_count': size}
        # Debugger IDs and an OS signal number only; no exception payload/frames.
        if breakpoint and size == 2:
            row['breakpoint_id'] = int(thread.GetStopReasonDataAtIndex(0))
            row['location_id'] = int(thread.GetStopReasonDataAtIndex(1))
        elif reason == api.eStopReasonSignal and size == 1:
            row['signal_number'] = int(thread.GetStopReasonDataAtIndex(0))
        threads.append(row)
    return {'state': state, 'stop_id': stop_id, 'total_threads': total,
            'threads': threads, 'state_after': int(process.GetState()),
            'stop_id_after': int(process.GetStopID())}


def stable(snapshot, stopped_state):
    need(snapshot['state'] == stopped_state and snapshot['state_after'] == stopped_state and
         snapshot['stop_id'] == snapshot['stop_id_after'], 'stop metadata changed while captured')
    need(0 < snapshot['total_threads'] <= MAX_THREADS and
         len(snapshot['threads']) == snapshot['total_threads'], 'stop thread inventory exceeds bound or incomplete')
    return [row for row in snapshot['threads'] if not row['none']]


def initial(snapshot, api, stop_signal):
    active = stable(snapshot, api.eStateStopped)
    need(len(active) == 1, 'initial stop is not isolated')
    row = active[0]
    need(row['reason'] == api.eStopReasonExec or
         (row['reason'] == api.eStopReasonSignal and row.get('signal_number') == stop_signal),
         'initial stop is not the expected launch stop')


def select(snapshot, stopped_state, owned_breakpoints, proven_thread=None):
    active = stable(snapshot, stopped_state)
    need(len(active) == 1 and active[0]['breakpoint'], 'not exactly one isolated breakpoint stop')
    row = active[0]
    need(row['reason_data_count'] == 2, 'breakpoint stop shape')
    need(row['breakpoint_id'] in owned_breakpoints and row['location_id'] > 0, 'unowned breakpoint stop')
    need(proven_thread is None or row['id'] == proven_thread, 'not the proven own main thread')
    return row['index'], owned_breakpoints[row['breakpoint_id']]
