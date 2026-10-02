"""Offline independent copied-byte verification; no host access or consent claims."""
import hashlib
import os
from pathlib import Path
import re
import stat

MAX_ADDRESS = (1 << 64) - 1
PAYLOAD_LIMIT = 65536
NAMES = ('claim.txt', 'call-started.txt', 'native.txt', 'result.txt')
SCOPE_KEYS = ('scope', 'layout', 'origin', 'run', 'source', 'build', 'binary',
              'pid', 'start_sec', 'start_usec', 'provider_sha', 'provider_uuid', 'root')


def need(condition, reason):
    if not condition:
        raise ValueError(reason)


def uint(value, limit=MAX_ADDRESS):
    need(isinstance(value, str) and len(value) <= 20 and
         re.fullmatch(r'0|[1-9][0-9]*', value) is not None, 'noncanonical unsigned number')
    number = int(value)
    need(number <= limit, 'unsigned number out of range')
    return number


def validate_scope(expected):
    need(isinstance(expected, dict) and set(expected) == set(SCOPE_KEYS) and
         all(isinstance(v, str) and len(v) <= 128 for v in expected.values()), 'expected scope shape')
    need(expected['scope'] == 'retained-identity' and expected['layout'] == 'mee-25.6-arm64-1',
         'unsupported scope/layout')
    for key, pattern in [('run', r'retained-identity-[0-9a-f]{32}'),
                         ('build', r'identity-[0-9a-f]{12}'), ('source', r'[0-9a-f]{40}'),
                         ('binary', r'[0-9a-f]{64}'), ('provider_sha', r'[0-9a-f]{64}'),
                         ('provider_uuid', r'[0-9a-f]{32}')]:
        need(re.fullmatch(pattern, expected[key]) is not None, 'invalid scope identity')
    root = uint(expected['root'])
    need(0 < uint(expected['pid'], 0x7fffffff) and uint(expected['start_sec']) > 0 and
         uint(expected['start_usec'], 999999) < 1000000 and
         root > 0 and root % 8 == 0 and root <= MAX_ADDRESS - 16, 'invalid process/root')
    need(expected['origin'] in ('owned-fixture', 'ae-diagnostic'), 'invalid origin')
    if expected['origin'] == 'ae-diagnostic':
        need(expected['provider_sha'] ==
             '18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344' and
             expected['provider_uuid'] == '74a30dbaa08b367bbd9915d6d77e9d52', 'provider pin mismatch')


def unwrap(raw, name):
    need(isinstance(raw, bytes) and len(raw) <= PAYLOAD_LIMIT + 128, 'journal envelope limit')
    prefix = b'AEHL-RESOURCE-JOURNAL-1\n' + name.encode('ascii') + b'\n'
    need(raw.startswith(prefix), 'journal envelope/name mismatch')
    rest = raw[len(prefix):]
    line_end = rest.find(b'\n')
    need(0 < line_end <= 6, 'journal envelope length')
    size = uint(rest[:line_end].decode('ascii'), PAYLOAD_LIMIT)
    start = line_end + 1
    need(rest[start + size:] == b'\nEND-AEHL-RECORD\n', 'journal payload/trailer mismatch')
    return rest[start:start + size]


def fields(payload):
    need(len(payload) <= PAYLOAD_LIMIT, 'journal payload limit')
    result, offset = [], 0
    while offset < len(payload):
        equal = payload.find(b'=', offset)
        colon = payload.find(b':', equal + 1)
        need(offset < equal <= offset + 32 and equal < colon <= equal + 7, 'field framing')
        key = payload[offset:equal].decode('ascii')
        need(re.fullmatch(r'[a-z_]+', key) is not None, 'field key')
        size = uint(payload[equal + 1:colon].decode('ascii'), PAYLOAD_LIMIT)
        end = colon + 1 + size
        need(end < len(payload) and payload[end:end + 1] == b'\n', 'field payload truncated')
        result.append((key, payload[colon + 1:end].decode('ascii')))
        need(len(result) <= 128, 'field count limit')
        offset = end + 1
    return result


def word(data, offset):
    need(0 <= offset <= len(data) - 8, 'word bounds')
    return int.from_bytes(data[offset:offset + 8], 'little')


def overlap(a, size, b, extent):
    return size > 0 and extent > 0 and a < b + extent and b < a + size


def verify_frames(body, root):
    keys = ('success', 'failure', 'read_calls', 'read_bytes', 'frame_count')
    need(tuple(k for k, _ in body[:5]) == keys, 'diagnostic scalar inventory')
    d = dict(body[:5])
    need(d['success'] == '1' and d['failure'] == '', 'capture did not succeed')
    calls, total, count = uint(d['read_calls'], 22), uint(d['read_bytes'], 6976), uint(d['frame_count'], 22)
    need(calls == count and len(body) == 5 + count * 4, 'frame count/inventory')
    frames, seen_mappings = [], {}
    for i in range(count):
        group = body[5 + i * 4:9 + i * 4]
        need(tuple(k for k, _ in group) == ('frame_address', 'frame_size', 'frame_hex', 'frame_mapping'),
             'frame field inventory/order')
        address, size = uint(group[0][1]), uint(group[1][1], 4096)
        encoded = group[2][1]
        need(address > 0 and size > 0 and address <= MAX_ADDRESS - size and
             len(encoded) == size * 2 and re.fullmatch(r'[0-9a-f]+', encoded) is not None, 'frame range/hex')
        parts = group[3][1].split(',')
        need(len(parts) == 8, 'mapping shape')
        mapping = tuple(uint(v) for v in parts)
        base, extent, _, obj, tag, depth, protection, maximum = mapping
        need(base > 0 and extent > 0 and base <= MAX_ADDRESS - extent and base <= address and
             address - base < extent and size <= extent - (address - base), 'mapping range')
        need(obj <= 0xffffffff and tag <= 0xffffffff and depth <= 16 and
             protection in (1, 3) and maximum <= 7 and protection & ~maximum == 0, 'mapping protection')
        need(address not in seen_mappings or seen_mappings[address] == mapping, 'mapping changed')
        seen_mappings[address] = mapping
        frames.append((address, bytes.fromhex(encoded)))
    need(sum(len(data) for _, data in frames) == total, 'byte budget mismatch')
    cursor = 0

    def take(address, size):
        nonlocal cursor
        need(cursor < len(frames) and frames[cursor][0] == address and
             len(frames[cursor][1]) == size, 'copy sequence/range mismatch')
        data = frames[cursor][1]
        cursor += 1
        return data

    def capture(expected=None):
        vector = take(root, 16)
        need(expected is None or vector == expected[0], 'vector copies differ')
        begin, end = word(vector, 0), word(vector, 8)
        need(begin % 8 == end % 8 == 0 and end >= begin and (end - begin) % 0xb0 == 0 and
             (end - begin) // 0xb0 <= 8 and ((begin == end == 0) or begin > 0), 'invalid vector')
        size = end - begin
        need(not overlap(root, 16, begin, size), 'record/root overlap')
        records = take(begin, size) if size else b''
        need(expected is None or records == expected[1], 'record copies differ')
        raw_names, copied_names, name_bytes = [], [], {}
        for index in range(size // 0xb0):
            record = records[index * 0xb0:(index + 1) * 0xb0]
            tag = record[0xa7]
            if tag < 128:
                need(tag <= 22 and record[0x90 + tag] == 0, 'inline name bounds/terminator')
                raw_names.append(record[0x90:0x90 + tag])
                continue
            address, length = word(record, 0x90), word(record, 0x98)
            need(length <= 255 and address > 0 and address <= MAX_ADDRESS - length - 1,
                 'external name bounds')
            extent = length + 1
            need(not overlap(address, extent, root, 16) and not overlap(address, extent, begin, size),
                 'name/state overlap')
            data = take(address, extent)
            need(data[-1] == 0, 'external name terminator')
            for offset, byte in enumerate(data):
                at = address + offset
                need(at not in name_bytes or name_bytes[at] == byte, 'overlapping names differ')
                name_bytes[at] = byte
            copied_names.append((index, address, data))
            raw_names.append(data[:-1])
        need(take(root, 16) == vector, 'root recheck differs')
        need(expected is None or copied_names == expected[2], 'name copies differ')
        return vector, records, copied_names, raw_names

    first = capture()
    capture(first)
    need(cursor == len(frames), 'extra/unconsumed frames')
    return {'record_count': len(first[3]), 'record_names_hex': [n.hex() for n in first[3]],
            'read_calls': calls, 'read_bytes': total}


def verify_records(records, expected):
    """Expected scope must come from a separate trusted candidate/run record."""
    validate_scope(expected)
    need(isinstance(records, dict) and set(records) == set(NAMES), 'journal inventory')
    payloads = {name: unwrap(records[name], name) for name in NAMES}
    prefix = [(key, expected[key]) for key in SCOPE_KEYS]
    parsed = {name: fields(data) for name, data in payloads.items()}
    need(parsed['claim.txt'] == parsed['call-started.txt'] == prefix, 'claim/marker binding')
    need(parsed['native.txt'][:len(prefix)] == prefix, 'native scope binding')
    need(parsed['result.txt'] == prefix + [('status', 'PASS'), ('claim', 'copied-byte-diagnostic-only')],
         'final result binding/status')
    summary = verify_frames(parsed['native.txt'][len(prefix):], uint(expected['root']))
    return {**summary, 'status': 'PASS', 'scope': 'journal-copied-byte-verification-only',
            'origin': expected['origin'], 'host_execution_verified': False,
            'journal_sha256': {name: hashlib.sha256(raw).hexdigest() for name, raw in records.items()}}


def _directory(path):
    path = Path(path)
    need(path.is_absolute() and '..' not in path.parts, 'noncanonical journal directory')
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    fd = os.open('/', flags)
    try:
        for component in path.parts[1:]:
            child = os.open(component, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        info = os.fstat(fd)
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
             stat.S_IMODE(info.st_mode) == 0o700, 'journal not private/owned')
        return fd
    except BaseException:
        os.close(fd)
        raise


def _identity(info):
    return (info.st_dev, info.st_ino, info.st_uid, info.st_mode, info.st_nlink,
            info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _names(fd):
    names = set()
    with os.scandir(fd) as entries:
        for entry in entries:
            names.add(entry.name)
            need(len(names) <= len(NAMES), 'journal inventory limit')
    return names


def verify_directory(path, expected):
    """Read only an existing private journal; never create/delete or query AE."""
    validate_scope(expected)
    fd = _directory(path)
    try:
        initial = os.fstat(fd)
        need(_names(fd) == set(NAMES), 'journal inventory')
        records, identities = {}, {}
        for name in NAMES:
            child = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=fd)
            try:
                info = os.fstat(child)
                need(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and info.st_nlink == 1 and
                     stat.S_IMODE(info.st_mode) == 0o600 and info.st_size <= PAYLOAD_LIMIT + 128,
                     'journal file ownership/type/mode/size')
                chunks, remaining = [], PAYLOAD_LIMIT + 129
                while remaining:
                    chunk = os.read(child, remaining)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    remaining -= len(chunk)
                raw = b''.join(chunks)
                need(len(raw) == info.st_size and _identity(info) == _identity(os.fstat(child)),
                     'journal file changed during read')
                records[name], identities[name] = raw, _identity(info)
            finally:
                os.close(child)
        result = verify_records(records, expected)
        need(_names(fd) == set(NAMES) and _identity(initial) == _identity(os.fstat(fd)),
             'journal directory changed')
        for name in NAMES:
            need(_identity(os.stat(name, dir_fd=fd, follow_symlinks=False)) == identities[name],
                 'journal entry replaced')
        fresh = _directory(path)
        try:
            need(_identity(os.fstat(fresh)) == _identity(initial), 'journal path replaced')
        finally:
            os.close(fresh)
        return result
    finally:
        os.close(fd)
