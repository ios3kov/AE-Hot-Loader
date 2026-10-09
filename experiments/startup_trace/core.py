"""Pure register-event correlator; never launches, attaches, reads memory or calls AE.

Positive output is a bounded normal-startup identity observation, not a late-add,
transaction, complete lifetime or race-freedom result. All addresses are uint64
register values scoped to one PID/birth/thread and a verified image/site.
"""
import json

MAX_EVENTS = 256
MAX_STOPS = 256
MAX_BYTES = 1024 * 1024
ROLES = ('marker', 'convert', 'pipl', 'spec', 'writer', 'index', 'writer_return',
         'reader', 'match', 'lookup')
FIELDS = {
    'marker': ('stage', 'context', 'callback', 'status', 'main'),
    'convert': ('context',), 'pipl': ('pipl',),
    'spec': ('pipl', 'descriptor'), 'writer': ('descriptor', 'root'),
    'index': ('descriptor', 'index', 'root'), 'writer_return': ('root',),
    'reader': ('stage', 'key', 'function', 'status', 'main'),
    'match': ('key',), 'lookup': ('descriptor', 'owner', 'root', 'index'),
}


def need(value, reason):
    if not value:
        raise ValueError(reason)


class Trace:
    def __init__(self, pid, birth, callback, match_function):
        need(type(pid) is int and pid > 0 and type(birth) is int and birth > 0,
             'invalid process identity')
        self.pid, self.birth = pid, birth
        self.callback, self.match_function = callback, match_function
        self.phase = 'marker-start'
        self.thread = self.context = self.pipl = self.descriptor = self.root = None
        self.index = self.key = None
        self.events = []; self.stops = self.size = 0

    @property
    def enabled(self):
        return {
            'marker-start': {'marker'}, 'marker-end': {'marker'},
            'convert': {'convert'}, 'pipl': {'pipl'}, 'spec': {'spec'},
            'writer': {'writer'}, 'index': {'index'},
            'writer-return': {'writer_return'}, 'reader-start': {'reader'},
            'match': {'match'}, 'lookup': {'lookup'}, 'reader-end': {'reader'},
            'complete': set(),
        }[self.phase]

    def feed(self, event):
        need(set(event) == {'pid', 'birth', 'thread', 'role', 'values'}, 'wrong event fields')
        need(event['pid'] == self.pid and event['birth'] == self.birth, 'process identity changed')
        need(type(event['thread']) is int and event['thread'] > 0, 'invalid thread')
        role, v = event['role'], event['values']
        need(role in self.enabled, 'unexpected or replayed event')
        need(isinstance(v, dict) and set(v) == set(FIELDS[role]), 'wrong register fields')
        need(all(type(x) is int and 0 <= x < 2**64 for x in v.values()), 'invalid register value')
        self.stops += 1; need(self.stops <= MAX_STOPS, 'stop budget exhausted')
        if self.thread is not None:
            need(event['thread'] == self.thread, 'not the proven own main thread')
        # Other startup descriptors are ignored only by exact context/interface/
        # descriptor equality, never by time, index guesses or string dereference.
        if role == 'convert' and v['context'] != self.context: return False
        if role == 'spec' and v['pipl'] != self.pipl: return False
        if role == 'writer' and v['descriptor'] != self.descriptor: return False
        data = json.dumps(event, sort_keys=True, separators=(',', ':')).encode()
        need(len(self.events) < MAX_EVENTS and self.size + len(data) <= MAX_BYTES, 'event payload budget exhausted')
        if role == 'marker':
            stage = 1 if self.phase == 'marker-start' else 2
            need(v['stage'] == stage and v['main'] == 1 and v['context'] != 0 and
                 v['callback'] == self.callback and v['status'] == 0, 'marker identity/status differs')
            if stage == 1:
                self.thread, self.context = event['thread'], v['context']; self.phase = 'marker-end'
            else:
                need(v['context'] == self.context, 'marker context changed'); self.phase = 'convert'
        elif role == 'convert': self.phase = 'pipl'
        elif role == 'pipl':
            need(v['pipl'] != 0, 'null PiPL interface'); self.pipl = v['pipl']; self.phase = 'spec'
        elif role == 'spec':
            need(v['descriptor'] != 0, 'null FCSpec'); self.descriptor = v['descriptor']; self.phase = 'writer'
        elif role == 'writer':
            need(v['root'] != 0, 'null registry receiver'); self.root = v['root']; self.phase = 'index'
        elif role == 'index':
            need(v['descriptor'] == self.descriptor and v['root'] == self.root and
                 v['index'] < 8192, 'writer index/record differs')
            self.index = v['index']; self.phase = 'writer-return'
        elif role == 'writer_return':
            need(v['root'] == self.root, 'writer receiver changed'); self.phase = 'reader-start'
        elif role == 'reader':
            stage = 1 if self.phase == 'reader-start' else 2
            need(v['stage'] == stage and 0 < v['key'] < 2**31 and v['main'] == 1 and
                 v['function'] == self.match_function and v['status'] == 0, 'reader identity/status differs')
            if stage == 1:
                self.key = v['key']; self.phase = 'match'
            else:
                need(v['key'] == self.key, 'reader key changed'); self.phase = 'complete'
        elif role == 'match':
            need(v['key'] == self.key, 'acquired reader used a different key'); self.phase = 'lookup'
        elif role == 'lookup':
            need(v['descriptor'] == self.descriptor and v['root'] == self.root and
                 v['owner'] != 0 and v['index'] == self.index + 1, 'writer-reader correspondence differs')
            self.phase = 'reader-end'
        self.events.append(event); self.size += len(data)
        return True

    def result(self):
        return {'status': 'IDENTITY_OBSERVED' if self.phase == 'complete' else 'INCOMPLETE',
                'phase': self.phase, 'pid': self.pid, 'birth': self.birth,
                'descriptor': self.descriptor, 'root': self.root, 'key': self.key,
                'writer_index': self.index, 'accepted_events': len(self.events),
                'stops': self.stops, 'scope': 'normal startup register correspondence only',
                'late_add': 'NOT_RUN', 'complete_lifetime': 'UNKNOWN',
                'atomic_commit': 'UNKNOWN', 'render_readset': 'UNKNOWN'}
