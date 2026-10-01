"""Supervise one no-scan directory probe. Never installs, launches, restarts or stops AE."""
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
import zipfile

MAGIC = b'AEHL-RESOURCE-JOURNAL-1\n'
NATIVE_NAMES = {'claim.txt', 'before.txt', 'call-started.txt', 'after.txt', 'result.txt'}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def no_links(path):
    path = Path(path).absolute()
    for item in (path, *path.parents):
        require(not item.is_symlink(), 'symlink path rejected')


def read(path, limit=24 * 1024 * 1024):
    path = Path(path)
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


def sha(path):
    return hashlib.sha256(read(path, 256 * 1024 * 1024)).hexdigest()


def private_directory(path, empty=False):
    path = Path(path)
    no_links(path)
    info = path.stat()
    require(stat.S_ISDIR(info.st_mode) and info.st_uid == os.getuid() and
            stat.S_IMODE(info.st_mode) == 0o700, 'directory is not private/owned')
    if empty:
        require(not any(path.iterdir()), 'directory must be empty')
    return (info.st_dev, info.st_ino, info.st_uid, info.st_mode)


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


def bundle_hashes(bundle):
    bundle = Path(bundle)
    no_links(bundle)
    result = {}
    for path in sorted(bundle.rglob('*')):
        no_links(path)
        if path.is_dir():
            continue
        require(path.is_file(), 'unsupported installed bundle entry')
        result[str(path.relative_to(bundle))] = sha(path)
    return result


def verify_providers(record):
    profile = record['provider_profile']
    root = Path(profile['frameworks'])
    expected = {
        root / 'FILE.dylib': profile['FILE_sha256'],
        root / 'U.dylib': profile['U_sha256'],
        root / 'dvacore.framework/Versions/A/dvacore': profile['dvacore_sha256'],
    }
    for path, digest in expected.items():
        require(sha(path) == digest, 'provider bytes differ from reviewed profile')
    return {str(path): digest for path, digest in expected.items()}


def identity_from_ready(record, ready, pid):
    lines = ready.decode('utf-8').splitlines()
    require(len(lines) == 3 and lines[1] == 'pid=' + str(pid) and lines[2].startswith('image='),
            'ready record PID/format mismatch')
    identity = json.loads(lines[0])
    expected = {k: record[k] for k in (
        'build_id', 'source_commit', 'source_clean', 'target', 'kind', 'run_id')}
    require(identity == expected, 'loaded no-scan identity mismatch')
    require(lines[2][6:] == record['module_path'], 'loaded module path mismatch')
    return identity


def expected_request(record, pid):
    token = record['activation_env']['AEHL_NOSCAN_GATE_TOKEN']
    return ('version=1\nkind=no-scan-directory\nbuild_id=' + record['build_id'] +
            '\nrun_id=' + record['run_id'] + '\npid=' + str(pid) + '\ntoken=' + token +
            '\nprivate_file_call=authorized\nprovider_retention=authorized\ncontract=reviewed\n').encode()


def prepare(manifest_path, expected_hash, pid, identity_fn=process_identity,
            authorized_host=None, authorized_bundle=None, provider_verifier=verify_providers):
    require(pid > 0, 'invalid PID')
    manifest_path = Path(manifest_path).absolute()
    raw = read(manifest_path, 4 * 1024 * 1024)
    require(hashlib.sha256(raw).hexdigest() == expected_hash, 'manifest hash mismatch')
    record = json.loads(raw)
    require(record['source_clean'] is True and
            record['kind'] == 'research-only-no-scan-directory-aegp' and
            record['installation_performed'] is False and record['ae_launch_performed'] is False,
            'wrong research artifact')
    base = manifest_path.parent
    control = Path(record['control_directory']); journal = Path(record['journal_directory'])
    probe = Path(record['probe_directory'])
    require(control.parent == base and journal.parent == base and probe.parent == base,
            'probe directories outside build')
    private_directory(control); private_directory(journal, empty=True); private_directory(probe, empty=True)
    try:
        str(probe).encode('ascii')
    except UnicodeEncodeError as error:
        raise ValueError('probe directory is not ASCII') from error
    require(record['host_mode'] == 'authorized-user-host', 'live probe requires authorized-user-host build')
    require(authorized_host is not None and authorized_bundle is not None,
            'explicit authorized host and bundle required')
    require(str(authorized_host) == record['host_executable'] and
            str(authorized_bundle) == record['authorized_bundle'], 'authorized paths differ from manifest')
    host = Path(record['host_executable']); bundle = Path(record['authorized_bundle'])
    no_links(host); no_links(bundle)
    require(host.is_file() and bundle.is_dir(), 'authorized host/module is not installed as expected')
    require(bundle_hashes(bundle) == record['files'], 'installed no-scan bundle bytes differ from candidate')
    observed = identity_fn(pid)
    require(observed['executable'] == str(host), 'PID is not the pinned After Effects host')
    ready = read(control / 'ready.txt', 16384)
    identity_from_ready(record, ready, pid)
    require(Path(record['module_path']).is_file(), 'loaded module path is absent')
    providers = provider_verifier(record)
    allowed = {'ready.txt'}
    require({p.name for p in control.iterdir()} == allowed, 'control directory was already used')
    require(identity_fn(pid) == observed, 'host changed during preparation')
    return record, control, journal, probe, observed, expected_request(record, pid), providers


def publish(control, request):
    temporary = control / ('request-' + uuid.uuid4().hex + '.tmp')
    fd = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(request); stream.flush(); os.fsync(stream.fileno())
        library = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
        library.renamex_np.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        library.renamex_np.restype = ctypes.c_int
        if library.renamex_np(os.fsencode(temporary), os.fsencode(control / 'request.txt'), 4):
            raise OSError(ctypes.get_errno(), 'exclusive request publication failed')
    finally:
        temporary.unlink(missing_ok=True)


def unwrap_journal(path):
    data = read(path)
    require(data.startswith(MAGIC), 'wrong journal magic')
    rest = data[len(MAGIC):]
    name_end = rest.find(b'\n'); require(name_end > 0, 'malformed journal name')
    name = rest[:name_end].decode('ascii')
    size_end = rest.find(b'\n', name_end + 1); require(size_end > name_end, 'malformed journal size')
    size = int(rest[name_end + 1:size_end])
    payload_start = size_end + 1; payload_end = payload_start + size
    require(payload_end <= len(rest), 'truncated journal payload')
    payload = rest[payload_start:payload_end]
    require(rest[payload_end:] == b'\nEND-AEHL-RECORD\n', 'malformed journal trailer')
    require(name == Path(path).name, 'journal filename mismatch')
    return payload


def parse_fields(payload):
    fields = []
    pos = 0
    while pos < len(payload):
        eq = payload.find(b'=', pos); require(eq > pos, 'malformed journal field')
        colon = payload.find(b':', eq + 1); require(colon > eq, 'malformed journal field length')
        length = int(payload[eq + 1:colon]); start = colon + 1; end = start + length
        require(end < len(payload) and payload[end:end + 1] == b'\n', 'truncated journal field')
        fields.append((payload[pos:eq].decode('ascii'), payload[start:end].decode('utf-8')))
        pos = end + 1
    return fields


def field_map(payload):
    result = {}
    for key, value in parse_fields(payload):
        result.setdefault(key, []).append(value)
    return result


def verify_native_pass(record, journal, observed=None):
    require({p.name for p in journal.iterdir()} == NATIVE_NAMES, 'native journal is incomplete/unexpected')
    before = unwrap_journal(journal / 'before.txt')
    after = unwrap_journal(journal / 'after.txt')
    require(before == after, 'native pre/post observation differs')
    observation = field_map(before)
    claim_payload = unwrap_journal(journal / 'claim.txt')
    require(claim_payload.endswith(before), 'native claim is not bound to exact baseline')
    plan_payload = claim_payload[:-len(before)]
    claim = field_map(plan_payload)
    result = field_map(unwrap_journal(journal / 'result.txt'))
    require(claim.get('scope') == ['no-scan-directory'] and claim.get('run') == [record['run_id']] and
            claim.get('source') == [record['source_commit']] and claim.get('build') == [record['build_id']] and
            claim.get('executable') == [record['host_executable']] and claim.get('module') == [record['module_path']] and
            claim.get('directory') == [record['probe_directory']] and claim.get('timeout_ms') == ['15000'],
            'native claim scope mismatch')
    expected = {
        'executable': record['host_executable'], 'module': record['module_path'],
        'version': '25.6x101', 'arch': 'arm64', 'build': '101',
        'main_thread': '1', 'unsaved': '1', 'dirty': '0', 'rendering': '0',
        'items': '0', 'queued': '0',
    }
    for key, value in expected.items():
        require(observation.get(key) == [value], 'native baseline field mismatch: ' + key)
    require(len(observation.get('pid', [])) == 1 and observation['pid'][0].isdigit() and
            int(observation['pid'][0]) > 0, 'invalid native PID evidence')
    if observed is not None:
        require(int(observation['pid'][0]) == observed['pid'], 'native/supervisor PID mismatch')
    require(len(observation.get('start', [])) == 1 and observation['start'][0],
            'missing native process-start evidence')
    require(len(observation.get('revision', [])) == 1 and observation['revision'][0].isdigit() and
            int(observation['revision'][0]) > 0, 'invalid project revision evidence')
    effects = observation.get('effect', [])
    images = observation.get('image_path', [])
    require(observation.get('registry_count') == [str(len(effects))] and len(effects) > 0 and
            len(effects) == len(set(effects)), 'invalid registry evidence')
    require(observation.get('image_count') == [str(len(images))] and len(images) > 0 and
            len(images) == len(observation.get('image_header', [])) == len(observation.get('image_slide', [])) and
            record['module_path'] in images, 'invalid image evidence')
    require(result.get('scope') == ['no-scan-directory'] and result.get('status') == ['PASS'] and
            result.get('stage') == ['complete'] and result.get('reason') == ['directory-roundtrip-release-only'] and
            result.get('claimed') == ['1'] and result.get('call_started') == ['1'] and
            result.get('postflight_observed') == ['1'] and result.get('cleanup_ok') == ['1'],
            'native no-scan gate did not pass exactly')
    call_started = unwrap_journal(journal / 'call-started.txt')
    require(call_started == plan_payload + before, 'call marker is not bound to exact plan/baseline')
    return {'journal_files': sorted(NATIVE_NAMES),
            'before_after_sha256': hashlib.sha256(before).hexdigest(),
            'registry_count': len(effects), 'image_count': len(images),
            'project_revision': int(observation['revision'][0])}


def write_json_exclusive(path, value):
    with Path(path).open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True); stream.write('\n')
        stream.flush(); os.fsync(stream.fileno())
    os.chmod(path, 0o600)


def package_report(record, control, journal, destination):
    destination = Path(destination)
    report_files = []
    sanitized = {k: v for k, v in record.items() if k not in ('activation_env', 'command')}
    sanitized_path = control / 'report-artifact.json'
    write_json_exclusive(sanitized_path, sanitized)
    for path in [control / 'ready.txt', control / 'supervisor-claim.json', control / 'supervisor.json',
                 sanitized_path, *sorted(journal.iterdir())]:
        if path.exists() and path.is_file(): report_files.append(path)
    hashes = {p.name if p.parent == control else 'journal/' + p.name:
              hashlib.sha256(read(p)).hexdigest() for p in report_files}
    manifest_path = control / 'report-hashes.json'; write_json_exclusive(manifest_path, hashes)
    report_files.append(manifest_path)
    with zipfile.ZipFile(destination, 'x', zipfile.ZIP_DEFLATED) as output:
        for path in report_files:
            arc = path.name if path.parent == control else 'journal/' + path.name
            output.write(path, arc)
    os.chmod(destination, 0o600)
    with zipfile.ZipFile(destination) as check:
        require(check.testzip() is None, 'report ZIP integrity failed')
    return destination


def supervise(record, control, journal, probe, observed, request, providers, timeout,
              identity_fn=process_identity, provider_verifier=verify_providers,
              publish_fn=publish, clock=time.monotonic, sleep=time.sleep, report_path=None):
    started = datetime.now(timezone.utc).isoformat()
    deadline = clock() + timeout
    status, reason, published = 'FAIL', 'request not published', False
    claim = {'host': observed, 'started_utc': started, 'build_id': record['build_id'],
             'run_id': record['run_id'], 'private_file_call_authorized': True,
             'provider_reference_retention_authorized': True}
    write_json_exclusive(control / 'supervisor-claim.json', claim)
    native = None
    try:
        require(identity_fn(observed['pid']) == observed, 'host changed before publication')
        require(provider_verifier(record) == providers, 'provider bytes changed before publication')
        private_directory(probe, empty=True)
        publish_fn(control, request); published = True
        while clock() < deadline:
            require(identity_fn(observed['pid']) == observed, 'host exited or changed')
            if (control / 'adapter-stopped.txt').exists():
                raise ValueError('research adapter stopped; no retry')
            if (journal / 'result.txt').exists():
                native = verify_native_pass(record, journal, observed)
                require(identity_fn(observed['pid']) == observed, 'host changed after native result')
                require(provider_verifier(record) == providers, 'provider bytes changed after native result')
                require(bundle_hashes(Path(record['authorized_bundle'])) == record['files'],
                        'installed no-scan bundle changed during run')
                private_directory(probe, empty=True)
                status, reason = 'PASS', 'exact no-scan directory lifecycle; same host/providers/bundle'
                break
            sleep(0.2)
        else:
            reason = 'timeout; request/native state preserved; no retry'
    except (OSError, ValueError, subprocess.SubprocessError, json.JSONDecodeError, zipfile.BadZipFile) as error:
        reason = str(error)
    result = {'status': status, 'reason': reason, 'build_id': record['build_id'],
              'run_id': record['run_id'], 'source_commit': record['source_commit'],
              'host': observed, 'provider_hashes': providers, 'native': native,
              'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
              'timeout_seconds': timeout, 'request_published': published,
              'process_stopped': False, 'plugin_scan_requested': False,
              'installation_performed': False, 'ae_launch_performed': False}
    write_json_exclusive(control / 'supervisor.json', result)
    if report_path is None:
        report_path = Path(record['control_directory']).parent / ('AEHL-NoScan-' + record['build_id'] + '.zip')
    archive = package_report(record, control, journal, report_path)
    return result, archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--timeout', type=int, default=45, choices=range(1, 61), metavar='1..60')
    parser.add_argument('--authorized-host', type=Path)
    parser.add_argument('--authorized-bundle', type=Path)
    parser.add_argument('--authorize-private-file-call', action='store_true')
    parser.add_argument('--authorize-provider-retention', action='store_true')
    parser.add_argument('--execute', action='store_true', help='publish exactly one request after all checks')
    args = parser.parse_args()
    try:
        prepared = prepare(args.manifest, args.sha256, args.pid,
                           authorized_host=args.authorized_host,
                           authorized_bundle=args.authorized_bundle)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        parser.exit(2, 'BLOCKED: ' + str(error) + '\n')
    if not args.execute:
        print('PASS: preparation checks only; no request published, no AE action performed')
        return
    if not (args.authorize_private_file_call and args.authorize_provider_retention):
        parser.exit(2, 'BLOCKED: both fresh live-call authorization flags are required\n')
    result, archive = supervise(*prepared, args.timeout)
    print(json.dumps(result, indent=2, sort_keys=True))
    print('Report: ' + str(archive))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
