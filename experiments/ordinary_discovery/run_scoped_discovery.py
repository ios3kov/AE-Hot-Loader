"""Supervise one owned scoped AEGP request. Does not install, launch or stop AE."""
import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import time
import uuid


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def no_links(path):
    path = path.absolute()
    for item in (path, *path.parents):
        require(not item.is_symlink(), 'symlink path rejected')


def read(path, limit=1024 * 1024):
    no_links(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        info = os.fstat(fd)
        require(stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid() and
                info.st_nlink == 1 and 0 <= info.st_size <= limit, 'invalid evidence file')
        with os.fdopen(fd, 'rb', closefd=False) as stream:
            data = stream.read(limit + 1)
        require(len(data) == info.st_size, 'file changed during read')
        return data
    finally:
        os.close(fd)


def process_identity(pid):
    library = ctypes.CDLL('/usr/lib/libproc.dylib')
    library.proc_pidpath.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_uint32]
    library.proc_pidpath.restype = ctypes.c_int
    buffer = ctypes.create_string_buffer(4096)
    require(library.proc_pidpath(pid, buffer, len(buffer)) > 0, 'test host is absent')
    start = subprocess.check_output(['ps', '-p', str(pid), '-o', 'lstart='],
                                    text=True, timeout=5).strip()
    require(bool(start), 'test host start time unavailable')
    return {'pid': pid, 'executable': str(Path(os.fsdecode(buffer.value)).resolve()), 'start': start}


def prepare(manifest_path, expected_hash, pid, identity_fn=process_identity):
    require(pid > 0, 'invalid PID')
    raw = read(manifest_path)
    require(hashlib.sha256(raw).hexdigest() == expected_hash, 'manifest hash mismatch')
    record = json.loads(raw)
    base = manifest_path.absolute().parent
    no_links(base)
    require(record['source_clean'] is True and record['kind'] == 'research-only-scoped-aegp',
            'wrong research artifact')
    evidence = Path(record['evidence'])
    require(evidence == base / 'evidence', 'evidence path outside this build')
    no_links(evidence)
    info = evidence.stat()
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
            stat.S_IMODE(info.st_mode) == 0o700, 'evidence directory is not private/owned')
    host = Path(record['host_executable'])
    require(host.is_relative_to(base / 'host'), 'host executable outside owned host directory')
    no_links(host)
    observed = identity_fn(pid)
    require(observed['executable'] == str(host), 'PID is not the pinned test host')
    ready = read(evidence / 'ready.txt', 16384).decode('utf-8').splitlines()
    require(len(ready) == 3 and ready[1] == 'pid=' + str(pid) and ready[2].startswith('image='),
            'ready record PID/format mismatch')
    identity = json.loads(ready[0])
    require(identity == {k: record[k] for k in (
        'build_id', 'source_commit', 'source_clean', 'target', 'kind',
        'fixture_build_id', 'fixture_manifest_sha256')}, 'loaded research identity mismatch')
    image = Path(ready[2][6:])
    require(image == image.resolve() and image.is_relative_to(base / 'host') and image.parent.name == 'MacOS' and
            image.parent.parent.name == 'Contents', 'research image outside owned host')
    bundle = image.parent.parent.parent
    no_links(bundle)
    actual = {}
    for path in bundle.rglob('*'):
        no_links(path)
        if not path.is_dir():
            actual[str(path.relative_to(bundle))] = hashlib.sha256(read(path, 16 * 1024 * 1024)).hexdigest()
    require(actual == record['files'], 'loaded research bundle file/hash mismatch')
    for name in ('request.txt', 'claim.txt', 'claim.txt.writing', 'result.txt',
                 'adapter-stopped.txt', 'supervisor-claim.json', 'supervisor.json'):
        require(not os.path.lexists(evidence / name), 'experiment has already been used')
    token = record['activation_env']['AEHL_SCOPED_GATE_TOKEN']
    request = ('version=1\nbuild_id=' + record['build_id'] + '\npid=' + str(pid) +
               '\ntoken=' + token + '\n').encode()
    require(identity_fn(pid) == observed, 'test host changed during preparation')
    return record, evidence, observed, request


def publish(evidence, request):
    temporary = evidence / ('request-' + uuid.uuid4().hex + '.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(request)
            stream.flush()
            os.fsync(stream.fileno())
        # macOS exclusive rename keeps link count one throughout publication.
        # A link/unlink pair could race the native no-hard-links check.
        library = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
        library.renamex_np.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        library.renamex_np.restype = ctypes.c_int
        if library.renamex_np(os.fsencode(temporary), os.fsencode(evidence / 'request.txt'), 4):
            raise OSError(ctypes.get_errno(), 'exclusive request publication failed')
    finally:
        temporary.unlink(missing_ok=True)


def registry(text):
    lines = text.decode('utf-8').splitlines()
    require(len(lines) >= 3 and lines[0] == 'AEHL-SNAPSHOT-1' and lines[1].isdigit() and
            all(lines[2:]), 'invalid host snapshot')
    return lines[1], sorted(lines[2:])


def verify_result(record, evidence, pid, request):
    expected = ('status=PASS\nscope=registration-only\nbuild_id=' + record['build_id'] +
                '\nsource=' + record['source_commit'] + '\npid=' + str(pid) + '\n').encode()
    require(read(evidence / 'result.txt') == expected, 'native gate did not pass')
    require(read(evidence / 'claim.txt') == request, 'claim does not match request')
    require(read(evidence / 'call-started.txt') ==
            ('root=' + record['scan_root'] + '\npid=' + str(pid) + '\n').encode(),
            'native call identity mismatch')
    require(int(read(evidence / 'loader-result.txt')) >= 0, 'native loader error')
    before, after = registry(read(evidence / 'before.txt')), registry(read(evidence / 'after.txt'))
    require(record['match'] not in before[1] and before[0] == after[0] and
            sorted(before[1] + [record['match']]) == after[1], 'registry/project gate failed')


def supervise(record, evidence, observed, request, timeout,
              identity_fn=process_identity, clock=time.monotonic, sleep=time.sleep):
    started = datetime.now(timezone.utc).isoformat()
    deadline = clock() + timeout
    published = False
    status, reason = 'FAIL', 'request not published'
    # One external supervisor per build, including concurrent invocations.
    with (evidence / 'supervisor-claim.json').open('x') as stream:
        json.dump({'host': observed, 'started_utc': started}, stream)
        stream.flush()
        os.fsync(stream.fileno())
    try:
        require(identity_fn(observed['pid']) == observed, 'host changed before publication')
        publish(evidence, request)
        published = True
        while clock() < deadline:
            require(identity_fn(observed['pid']) == observed, 'host exited or changed')
            require(not os.path.lexists(evidence / 'adapter-stopped.txt'), 'research adapter stopped')
            if os.path.lexists(evidence / 'result.txt'):
                verify_result(record, evidence, observed['pid'], request)
                require(identity_fn(observed['pid']) == observed, 'host changed after result')
                status, reason = 'PASS', 'exact registration-only result and same host'
                break
            sleep(0.2)
        else:
            reason = 'timeout; pending request and native state preserved; no retry'
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        reason = str(error)
    result = {'status': status, 'reason': reason, 'build_id': record['build_id'],
              'source_commit': record['source_commit'], 'host': observed,
              'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'timeout_seconds': timeout, 'request_published': published, 'process_stopped': False}
    with (evidence / 'supervisor.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--pid', required=True, type=int)
    parser.add_argument('--timeout', type=int, default=45, choices=range(1, 61), metavar='1..60')
    parser.add_argument('--execute', action='store_true', help='publish the one-shot request after checks')
    args = parser.parse_args()
    try:
        record, evidence, observed, request = prepare(args.manifest, args.sha256, args.pid)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        parser.exit(2, 'BLOCKED: ' + str(error) + '\n')
    if not args.execute:
        print('PASS: preparation checks only; no request published')
        return
    result = supervise(record, evidence, observed, request, args.timeout)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
