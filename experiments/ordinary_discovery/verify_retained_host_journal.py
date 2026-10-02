"""Independent offline host/copy evidence checks, never live attestation/authority."""
import hashlib
import os
import re
import time

import verify_retained_identity_journal as copied

need, uint = copied.need, copied.uint
NAMES = ('claim.txt', 'call-started.txt', 'native.txt', 'after.txt', 'result.txt')
PAYLOAD_LIMIT = 4 * 1024 * 1024
OBSERVATION_LIMIT = 2 * 1024 * 1024
PLAN_KEYS = copied.SCOPE_KEYS + ('protocol', 'executable_hex', 'module_hex', 'journal_hex', 'timeout_ms')
HOST_KEYS = ('observed_pid', 'observed_start', 'observed_executable_hex', 'observed_module_hex',
             'version', 'arch', 'build_number', 'main_thread', 'unsaved', 'dirty', 'rendering',
             'items', 'queued', 'revision')


def raw_hex(text, limit):
    need(isinstance(text, str) and len(text) <= limit * 2 and len(text) % 2 == 0 and
         re.fullmatch(r'[0-9a-f]*', text) is not None, 'noncanonical/bounded hex')
    return bytes.fromhex(text)


def canonical(path):
    return (2 <= len(path) <= 4096 and path.startswith(b'/') and not path.endswith(b'/') and
            all(part not in (b'', b'.', b'..') for part in path.split(b'/')[1:]) and
            all(c >= 32 and c != 127 for c in path))


def validate_plan(expected):
    need(type(expected) is dict and len(expected) == len(PLAN_KEYS) and set(expected) == set(PLAN_KEYS) and
         all(isinstance(v, str) for v in expected.values()), 'expected host plan inventory/type')
    copied.validate_scope({k: expected[k] for k in copied.SCOPE_KEYS})
    need(expected['protocol'] == 'retained-host-1' and expected['timeout_ms'] == '15000',
         'host protocol/deadline mismatch')
    for key in ('executable_hex', 'module_hex', 'journal_hex'):
        need(canonical(raw_hex(expected[key], 4096)), 'noncanonical expected path')


class Budget:
    """Start comes from the supervisor BEFORE request publication, not a journal."""
    def __init__(self, started_ns, now_ns):
        need(type(started_ns) is int and 0 <= started_ns <= copied.MAX_ADDRESS - 15000000000 and
             callable(now_ns), 'invalid independent verification clock')
        self.previous, self.deadline, self.now = started_ns, started_ns + 15000000000, now_ns

    def tick(self):
        now = self.now()
        need(type(now) is int and self.previous <= now < self.deadline, 'verification deadline/clock')
        self.previous = now


def unwrap(raw, name):
    need(isinstance(raw, bytes) and len(raw) <= PAYLOAD_LIMIT + 128, 'host envelope limit')
    prefix = b'AEHL-RESOURCE-JOURNAL-1\n' + name.encode() + b'\n'
    need(raw.startswith(prefix), 'host envelope name/version')
    rest = raw[len(prefix):]
    end = rest.find(b'\n')
    need(0 < end <= 8, 'host envelope length')
    size = uint(rest[:end].decode('ascii'), PAYLOAD_LIMIT)
    need(rest[end + 1 + size:] == b'\nEND-AEHL-RECORD\n', 'host payload/trailer mismatch')
    return rest[end + 1:end + 1 + size]


def fields(payload, limit=PAYLOAD_LIMIT, count_limit=64):
    need(isinstance(payload, bytes) and len(payload) <= limit, 'host field payload limit')
    out, offset = [], 0
    while offset < len(payload):
        equal = payload.find(b'=', offset)
        colon = payload.find(b':', equal + 1)
        need(offset < equal <= offset + 32 and equal < colon <= equal + 9, 'host field framing')
        key = payload[offset:equal].decode('ascii')
        need(re.fullmatch(r'[a-z_]+', key) is not None, 'host field key')
        size = uint(payload[equal + 1:colon].decode('ascii'), limit)
        end = colon + 1 + size
        need(end < len(payload) and payload[end:end + 1] == b'\n', 'host field truncated')
        out.append((key, payload[colon + 1:end].decode('ascii')))
        need(len(out) <= count_limit, 'host field count')
        offset = end + 1
    return out


def observation(text, expected):
    data = fields(raw_hex(text, OBSERVATION_LIMIT), OBSERVATION_LIMIT, 50000)
    prefix = [(k, expected[k]) for k in copied.SCOPE_KEYS]
    need(data[:len(prefix)] == prefix, 'measured process/provider/root binding')
    body = data[len(prefix):]
    need(tuple(k for k, _ in body[:len(HOST_KEYS)]) == HOST_KEYS, 'host scalar inventory')
    h = dict(body[:len(HOST_KEYS)])
    exact = {'observed_pid': expected['pid'],
             'observed_start': expected['start_sec'] + '.' + expected['start_usec'],
             'observed_executable_hex': expected['executable_hex'],
             'observed_module_hex': expected['module_hex'],
             'version': '25.6x101', 'arch': 'arm64', 'build_number': '101',
             'main_thread': '1', 'unsaved': '1', 'dirty': '0', 'rendering': '0',
             'items': '0', 'queued': '0'}
    need(all(h[k] == v for k, v in exact.items()) and uint(h['revision']) > 0,
         'unsafe or mismatched host/project')
    cursor = len(HOST_KEYS)
    need(len(body) > cursor and body[cursor][0] == 'registry_count', 'registry inventory')
    count = uint(body[cursor][1], 20000)
    need(count > 0, 'empty registry')
    cursor += 1
    effects = body[cursor:cursor + count]
    need(len(effects) == count and all(k == 'effect_hex' for k, _ in effects), 'effect field inventory')
    registry = [raw_hex(v, 1024) for _, v in effects]
    need(all(v and all(c >= 32 and c != 127 for c in v) for v in registry) and
         len(set(registry)) == count, 'invalid/ambiguous effect identity')
    cursor += count
    need(len(body) > cursor and body[cursor][0] == 'image_count', 'image count inventory')
    count = uint(body[cursor][1], 8192)
    cursor += 1
    need(count > 0 and len(body) == cursor + 3 * count, 'image field inventory')
    images = []
    for i in range(count):
        group = body[cursor + 3 * i:cursor + 3 * i + 3]
        need(tuple(k for k, _ in group) == ('image_path_hex', 'image_header', 'image_slide'), 'image shape')
        path = raw_hex(group[0][1], 4096)
        header = uint(group[1][1])
        slide = group[2][1]
        need(isinstance(slide, str) and len(slide) <= 20 and
             re.fullmatch(r'0|-?[1-9][0-9]*', slide) is not None, 'noncanonical image slide')
        slide = int(slide)
        need(canonical(path) and header > 0 and -(1 << 63) <= slide < (1 << 63), 'image bounds/path')
        images.append((path, header, slide))
    need(len(set(images)) == count, 'ambiguous image inventory')
    return {'revision': uint(h['revision']), 'registry': frozenset(registry), 'images': frozenset(images)}


def same_host(before, after):
    need(before['revision'] == after['revision'] and before['registry'] == after['registry'],
         'project/registry changed')
    need(before['images'] <= after['images'] and
         all(path.startswith(b'/System/Library/') for path, _, _ in after['images'] - before['images']),
         'resident images changed')


def _verify(records, expected, budget):
    budget.tick()
    need(type(records) is dict and len(records) == len(NAMES) and set(records) == set(NAMES), 'host journal inventory')
    prefix = [(k, expected[k]) for k in PLAN_KEYS]
    observations = []
    for name, key in [('claim.txt', 'before_hex'), ('call-started.txt', 'immediate_hex'), ('after.txt', 'after_hex')]:
        data = fields(unwrap(records[name], name))
        need(len(data) == len(prefix) + 1 and data[:len(prefix)] == prefix and data[-1][0] == key,
             'host plan/observation binding')
        observations.append(observation(data[-1][1], expected))
    same_host(observations[0], observations[1])
    same_host(observations[0], observations[2])
    # Reuse the already independent reconstruction of BOTH native copy sequences.
    native = copied.fields(copied.unwrap(records['native.txt'], 'native.txt'))
    scope = [(k, expected[k]) for k in copied.SCOPE_KEYS]
    need(native[:len(scope)] == scope, 'native transaction scope binding')
    diagnostic = copied.verify_frames(native[len(scope):], uint(expected['root']))
    tail = [('status', 'PASS'), ('stage', 'complete'), ('reason', 'guarded-copied-byte-diagnostic-only'),
            ('evidence_failure', '')] + [(k, '1') for k in
            ('consumed', 'claim_attempted', 'claimed', 'marker_attempted', 'read_started',
             'diagnostic_saved', 'postflight_attempted', 'postflight_saved')] + [
            ('host_execution_verified', '0'), ('claim', 'provisional-guarded-diagnostic-only')]
    need(fields(unwrap(records['result.txt'], 'result.txt')) == prefix + tail,
         'incomplete/unverified producer result')
    out = {**diagnostic, 'status': 'PASS', 'scope': 'guarded-transaction-evidence-only',
           'origin': expected['origin'], 'host_execution_verified': False,
           'registry_count': len(observations[0]['registry']),
           'resident_image_count': len(observations[0]['images']),
           'journal_sha256': {n: hashlib.sha256(raw).hexdigest() for n, raw in records.items()}}
    budget.tick()
    return out


def verify_records(records, expected, *, started_ns, now_ns=time.monotonic_ns):
    validate_plan(expected)
    plan = expected.copy()  # Freeze before any supplied clock/boundary callback.
    return _verify(records, plan, Budget(started_ns, now_ns))


def verify_directory(path, expected, *, started_ns, now_ns=time.monotonic_ns):
    validate_plan(expected)  # Bad policy never accesses evidence files.
    plan = expected.copy()
    need(os.fsencode(path) == raw_hex(plan['journal_hex'], 4096), 'journal path outside expected plan')
    budget = Budget(started_ns, now_ns)
    budget.tick()
    # Native has a tighter inner 64 KiB limit; shared reader bounds every outer file.
    out = copied._verify_directory(path, plan, NAMES, PAYLOAD_LIMIT,
                                   lambda records, plan: _verify(records, plan, budget))
    budget.tick()  # Includes final filesystem identity checks, not only parsing.
    return out
