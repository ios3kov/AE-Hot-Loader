"""Resource-first correlation contract, restricted to an owned fixture.

No launch, debugger, process-memory access or Adobe calls. A completed fixture
chain does not admit AE: reviewed host sites, borrowed reads and transport proof
are still required. Refusal is terminal; caller-supplied addresses prove no lifetime.
"""
import hashlib
import json
import re

MAX_EVENTS = 32
MAX_BYTES = 16384
MAX_PAYLOAD = 128
ORIGINS = ('bundle-resource', 'legacy-resource', 'cache')
FIELDS = {
    'producer': ('call', 'origin', 'module_sha256', 'payload_hex'),
    'pipl': ('call', 'pipl', 'pipl_owner', 'source_storage', 'name'),
    'getter': ('call', 'pipl', 'source_storage', 'name'),
    'copy': ('call', 'pipl', 'descriptor', 'descriptor_owner', 'routine_owner',
             'source_storage', 'target_storage', 'name'),
    'writer': ('descriptor', 'descriptor_owner', 'routine_owner', 'root',
               'target_storage', 'name'),
    'index': ('descriptor', 'root', 'index'),
    'writer_return': ('root', 'status'),
    'reader_start': ('key', 'function'),
    'lookup': ('descriptor', 'descriptor_owner', 'routine_owner', 'root', 'index'),
    'reader_return': ('key', 'function', 'status', 'output_storage', 'name'),
}
ROLES = tuple(FIELDS)
TEXT_FIELDS = {'origin', 'module_sha256', 'payload_hex', 'name'}


def need(value, reason):
    if not value:
        raise ValueError(reason)


def uint(value, positive=False):
    return type(value) is int and (1 if positive else 0) <= value < 2**64


def digest(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None


class Trace:
    def __init__(self, profile):
        need(type(profile) is dict and set(profile) == {
            'schema', 'kind', 'run_id', 'pid', 'thread', 'origin',
            'module_sha256', 'payload_sha256', 'match_name'}, 'profile fields')
        need(profile['schema'] == 'AEHL-RESOURCE-FIXTURE-1' and
             profile['kind'] == 'owned-fixture', 'AE resource observation is not admitted')
        need(type(profile['run_id']) is str and
             re.fullmatch('[0-9a-f]{32}', profile['run_id']) is not None, 'run identity')
        need(uint(profile['pid'], True) and uint(profile['thread'], True), 'process/thread identity')
        need(type(profile['origin']) is str and profile['origin'] in ORIGINS, 'producer origin')
        need(digest(profile['module_sha256']) and digest(profile['payload_sha256']), 'source digest')
        need(type(profile['match_name']) is str and
             re.fullmatch('AEHLR[0-9a-f]{12}', profile['match_name']) is not None, 'own bounded match name')
        self.profile = dict(profile)
        self.position = self.size = 0
        self.events = []
        self.bound = {}
        self.refusal = None

    def feed(self, event):
        need(self.refusal is None, 'trace already refused')
        try:
            self._feed(event)
        except (ValueError, TypeError, KeyError) as exc:
            self.refusal = str(exc)
            raise ValueError(self.refusal) from exc

    def _feed(self, event):
        need(type(event) is dict and set(event) == {
            'run_id', 'pid', 'thread', 'sequence', 'role', 'values'}, 'event fields')
        need(self.position < len(ROLES) and len(self.events) < MAX_EVENTS, 'complete/replayed event or event budget')
        for field in ('run_id', 'pid', 'thread'):
            need(type(event[field]) is type(self.profile[field]) and
                 event[field] == self.profile[field], 'event identity differs: ' + field)
        need(type(event['sequence']) is int and event['sequence'] == self.position, 'event order/replay')
        role = event['role']
        need(type(role) is str and role == ROLES[self.position], 'event role/order')
        v = event['values']
        need(type(v) is dict and set(v) == set(FIELDS[role]), 'event value fields')
        for field, value in v.items():
            if field in TEXT_FIELDS:
                need(type(value) is str and len(value) <= MAX_PAYLOAD * 2, 'bounded text field')
            else:
                need(uint(value), 'unsigned integer field')
                if field not in ('status', 'index'):
                    need(value != 0, 'null identity field')
        raw = json.dumps(event, sort_keys=True, separators=(',', ':')).encode()
        need(self.size + len(raw) <= MAX_BYTES, 'payload budget')
        b = dict(self.bound)
        if role == 'producer':
            need(v['origin'] == self.profile['origin'] and
                 v['module_sha256'] == self.profile['module_sha256'], 'producer/module identity')
            need(re.fullmatch('(?:[0-9a-f]{2}){1,128}', v['payload_hex']) is not None, 'resource bytes encoding')
            payload = bytes.fromhex(v['payload_hex'])
            need(hashlib.sha256(payload).hexdigest() == self.profile['payload_sha256'], 'resource byte identity')
            # This is the fixture's explicit wire format, NOT an Adobe PiPL parser.
            need(payload == b'eMNA:' + self.profile['match_name'].encode('ascii') + b'\0', 'owned fixture payload')
            b['call'] = v['call']
        elif role == 'pipl':
            need(v['call'] == b['call'], 'producer call changed')
            b.update({k: v[k] for k in ('pipl', 'pipl_owner', 'source_storage')})
        elif role == 'getter':
            self._same(v, b, ('call', 'pipl', 'source_storage'))
        elif role == 'copy':
            self._same(v, b, ('call', 'pipl', 'source_storage'))
            need(v['source_storage'] != v['target_storage'], 'copy was replaced by source alias')
            b.update({k: v[k] for k in ('descriptor', 'descriptor_owner', 'routine_owner', 'target_storage')})
        elif role == 'writer':
            self._same(v, b, ('descriptor', 'descriptor_owner', 'routine_owner', 'target_storage'))
            b['root'] = v['root']
        elif role == 'index':
            self._same(v, b, ('descriptor', 'root'))
            need(v['index'] < 8192, 'fixture index bound')
            b['index'] = v['index']
        elif role == 'writer_return':
            self._same(v, b, ('root',))
            need(v['status'] == 0, 'writer failure; recovery UNKNOWN')
        elif role == 'reader_start':
            # Selected original-file index conversion, not a public SDK ABI.
            need(v['key'] == b['index'] + 703, 'selected index/key conversion')
            b.update({k: v[k] for k in ('key', 'function')})
        elif role == 'lookup':
            self._same(v, b, ('descriptor', 'descriptor_owner', 'routine_owner', 'root'))
            need(v['index'] == b['index'] + 1, 'reader index differs')
        elif role == 'reader_return':
            self._same(v, b, ('key', 'function'))
            need(v['status'] == 0, 'reader failure')
            need(v['output_storage'] not in (b['source_storage'], b['target_storage']), 'reader did not copy output')
        if 'name' in v:
            need(v['name'] == self.profile['match_name'], 'copied name identity differs')
        self.bound = b
        # Freeze accepted inputs: a caller cannot mutate the retained evidence.
        self.events.append(json.loads(raw))
        self.size += len(raw)
        self.position += 1

    @staticmethod
    def _same(values, bound, fields):
        need(all(values[field] == bound[field] for field in fields), 'object/owner continuity differs')

    def result(self):
        complete = self.position == len(ROLES) and self.refusal is None
        return {'kind': 'owned-fixture', 'status': 'REFUSED' if self.refusal else
                ('FIXTURE_CHAIN_OBSERVED' if complete else 'INCOMPLETE'),
                'phase': 'complete' if complete else (ROLES[self.position] if self.position < len(ROLES) else 'complete-refused'),
                'accepted_events': len(self.events), 'bytes': self.size, 'reason': self.refusal,
                'origin': self.profile['origin'],
                'current_resource_read': 'FIXTURE_ONLY' if complete and self.profile['origin'] != 'cache' else 'NOT_ESTABLISHED',
                'copied_name': 'FIXTURE_ONLY' if complete else 'UNKNOWN',
                'AE_observation': 'NOT_RUN', 'transport_admission': 'BLOCKED',
                'late_add': 'NOT_RUN', 'complete_lifetime': 'UNKNOWN',
                'atomic_commit': 'UNKNOWN', 'render_readset': 'UNKNOWN', 'failure_recovery': 'UNKNOWN'}
