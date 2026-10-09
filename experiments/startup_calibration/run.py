"""One owned normal-startup/public-SDK apply/frame calibration. No private calls or late-add.

Execution is explicit. Refuses any existing AE/aerender, changed artifact, replay
or unsafe cleanup. Never stops another process or deletes a project/preferences.
"""
import argparse
import ctypes
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
HOST = Path('/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/MacOS/After Effects')
HOST_SHA = '464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6'
PLUGIN_ROOT = Path.home() / 'Library/Application Support/Adobe/Common/Plug-ins/7.0/MediaCore'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


common = load('startup_live_io', ROOT / 'experiments/ordinary_discovery/run_no_scan_directory_probe.py')
oracle = load('startup_live_oracle', Path(__file__).with_name('oracle.py'))
identity = load('startup_live_identity', Path(__file__).with_name('identity.py'))
png = load('startup_live_png', Path(__file__).with_name('png_frame.py'))


def need(value, reason):
    if not value:
        raise ValueError(reason)


def fields(data, schema):
    rows = data.decode('ascii').splitlines()
    need(rows and rows[0] == schema, 'wrong record schema')
    result = {}
    for row in rows[1:]:
        need('=' in row, 'malformed record'); key, value = row.split('=', 1)
        need(key and key not in result, 'duplicate record field'); result[key] = value
    return result


def write(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data); stream.flush(); os.fsync(stream.fileno())


def publish(control, data):
    common.private_directory(control)
    temporary = control / ('request-pending-' + uuid.uuid4().hex)
    write(temporary, data)
    library = ctypes.CDLL('/usr/lib/libSystem.B.dylib', use_errno=True)
    library.renamex_np.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
    library.renamex_np.restype = ctypes.c_int
    # Same reviewed RENAME_EXCL protocol, now with the calibration's leaf name.
    need(library.renamex_np(os.fsencode(temporary), os.fsencode(control / 'request'), 4) == 0,
         'exclusive publication failed; outcome unknown; do not retry')
    fd = os.open(control, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def processes():
    result = []
    for name in ('After Effects', 'aerender'):
        command = subprocess.run(['pgrep', '-x', name], capture_output=True, text=True, timeout=10)
        need(command.returncode in (0, 1) and not command.stderr, 'process inventory unavailable')
        result.extend(int(value) for value in command.stdout.split())
    return sorted(set(result))


def birth(identity):
    seconds, micros = identity['start'].split('.')
    return int(seconds) * 1_000_000 + int(micros)


def log_budget(live):
    need(sum(p.stat().st_size for p in (live / "host-stdout.log", live / "host-stderr.log") if p.exists()) <=
         8 * 1024 * 1024, "owned host log budget exceeded")


def cleanup_proof(raw, record, observed, age, raw_result):
    rows = raw.decode("ascii").splitlines()
    need(rows[:4] == ["AEHL-CAL-CLEANUP-1", "build=" + record["build_id"],
         "pid=" + str(observed["pid"]), "birth=" + str(birth(observed))], "cleanup proof differs")
    need(len(rows) == 6 and rows[4] == "AEHL-CAL-OWNED-1" and rows[5].isdigit() and
         0 <= age <= 2, "missing or stale owned-project proof")
    result = fields(raw_result, "AEHL-CAL-RESULT-2")
    need(result.get("build") == record["build_id"] and result.get("cleanup") == "PASS" and
         result.get("cleanup_safe") == "YES", "SDK resources not confirmed released")


def preserve_owned_host(child, control, record, observed):
    """A resource/project proof never authorizes SIGTERM as an application quit.

    Preserve the live process for manual close until a normal AE quit protocol
    has its own target evidence. This function sends no signal or Apple event.
    """
    if not child:
        return 'NOT RUN'
    if child.poll() is not None:
        return 'OWNED HOST EXITED: normal exit not certified'
    if observed and (control / 'cleanup-safe').exists():
        cleanup_proof(common.read(control / 'cleanup-safe', 1024), record, observed,
            time.time() - (control / 'cleanup-safe').stat().st_mtime,
            common.read(control / 'result', 4096))
        need(common.process_identity(child.pid) == observed and processes() == [child.pid],
             'cleanup process changed')
        return 'MANUAL CLOSE REQUIRED: owned-project proof PASS; no signal sent'
    return 'BLOCKED: no safe current owned-project proof; host preserved'


def ready_identity(raw, record, observed):
    ready = fields(raw, 'AEHL-CAL-READY-1')
    need(ready == {'build': record['build_id'], 'pid': str(observed['pid']), 'birth': str(birth(observed))},
         'ready identity differs from owned process/build')
    return ready


def request(record, observed, deadline, queue_mode=False, observation_mode=False):
    need(type(deadline) is int and deadline > 0, 'invalid deadline')
    need(not (queue_mode and observation_mode), 'request modes are mutually exclusive')
    need(not record.get('registration_route_discriminator', False) or observation_mode,
         'route discriminator permits read-only observation only')
    observer = record['bundles'][1]['binary_sha256']
    return ('AEHL-CAL-REQUEST-2 ' + record['token'] + ' ' + str(observed['pid']) + ' ' +
            str(birth(observed)) + ' ' + str(deadline) +
            (' OWNED-STARTUP-REGISTRY-OBSERVATION ' if observation_mode else
             ' OWNED-STARTUP-QUEUE-CONTROL ' if queue_mode else ' OWNED-STARTUP-APPLY-RENDER ') + observer + '\n').encode('ascii')


def verify_observation(record, raw_result, samples):
    result = fields(raw_result, 'AEHL-CAL-RESULT-2')
    need(result.get('build') == record['build_id'] and result.get('status') == 'LISTED_OBSERVED' and
         result.get('cleanup') == 'PASS' and result.get('cleanup_safe') == 'YES' and
         result.get('render') == result.get('apply') == 'NOT_RUN' and
         result.get('stage') == 'registry-observation', 'read-only observation incomplete')
    need(len(samples) == 3, 'three bounded samples required')
    selected = []
    resource_selected = []
    for index, raw in enumerate(samples):
        s = fields(raw, 'AEHL-CAL-NAMES-1')
        need(s.get('build') == record['build_id'] and s.get('sample') == str(index) and
             s.get('complete') == 'YES' and s.get('stage') == 'name-observation-complete' and
             s.get('exact') == '1', 'name sample incomplete or wrong identity')
        count, revision = int(s['count']), int(s['revision'])
        need(1 <= count <= 8192 and int(s['traversed']) == count and revision > 0 and
             1 <= int(s['own_observations']) <= 16, 'observation bounds differ')
        matches = []
        resources = []
        for own in range(int(s['own_observations'])):
            def decode(field):
                value = s[field]
                need(0 < len(value) <= 1024 and len(value) % 2 == 0 and
                     set(value) <= set('0123456789abcdef'), 'invalid bounded name encoding')
                text = bytes.fromhex(value).decode('utf-8', 'strict')
                need('\0' not in text, 'embedded name terminator')
                return text
            name, match = decode(f'own_{own}_name_hex'), decode(f'own_{own}_match_hex')
            if match == record['match_name']:
                need(name == record['config']['calibration_name'], 'own display name differs')
                matches.append(int(s[f'own_{own}_key']))
            if record.get('registration_route_discriminator', False) and match == record['resource_match_name']:
                need(name == record['config']['calibration_name'], 'resource display name differs')
                resources.append(int(s[f'own_{own}_key']))
        need(len(resources) <= 1 and all(0 < key < 2**31 for key in resources),
             'resource installed key invalid/duplicate')
        resource_selected.append(tuple(resources))
        need(len(matches) == 1 and matches[0] != 0, 'own installed key absent/duplicate')
        selected.append((matches[0], count, revision))
    need(len(set(selected)) == 1 and str(selected[0][0]) == result.get('key'), 'key/count/project changed')
    need(len(set(resource_selected)) == 1, 'resource key changed between samples')
    answer = {'installed_key': selected[0][0], 'count': selected[0][1], 'revision': selected[0][2],
              'scope': 'read-only normal-startup enumeration; internal record/owner/late-add NOT PROVED'}
    if record.get('registration_route_discriminator', False):
        resource = resource_selected[0]
        need(not resource or resource[0] != selected[0][0], 'distinct names share an installed key')
        answer.update(resource_key=resource[0] if resource else None,
                      route_observation='BOTH_NAMES_LISTED' if resource else 'METADATA_NAME_LISTED_RESOURCE_NAME_ABSENT')
    return answer


def native_complete(record, raw_result):
    result = fields(raw_result, 'AEHL-CAL-RESULT-2')
    need(result.get('build') == record['build_id'], 'native result build differs')
    need(result.get('status') == 'LISTED_APPLIED_FRAME_CAPTURED',
         'native refused or incomplete: status=' + result.get('status', 'UNKNOWN') +
         '; stage=' + result.get('stage', 'UNKNOWN') + '; no frame requested/accepted')
    return result


def verify_capture(record, raw_result, raw_metadata, pixels):
    result = native_complete(record, raw_result)
    need(result.get('build') == record['build_id'] and result.get('status') == 'LISTED_APPLIED_FRAME_CAPTURED' and
         result.get('cleanup') == 'PASS' and result.get('cleanup_safe') == 'YES' and
         int(result.get('key', '0')) != 0 and result.get('render') == 'CAPTURED_PIXEL_CHECK_PENDING',
         'native operation not confirmed complete')
    metadata = fields(raw_metadata, 'AEHL-CAL-FRAME-1')
    expected = {'build': record['build_id'], 'width': '64', 'height': '48', 'order': 'ARGB8',
                'stride': '256', 'world_type': '8', 'time': '1/24', 'working_space': 'NONE'}
    need(all(metadata.get(k) == v for k, v in expected.items()), 'frame provenance/shape differs')
    need(256 <= int(metadata['source_rowbytes']) <= 65536 and
         0 <= int(metadata['counter_before']) < int(metadata['counter_after']), 'no new marker render confirmed')
    comparison = oracle.compare(pixels, 64, 48, record['seed'], stride=256)
    need(comparison['pixel_status'] == 'PASS', 'frame differs from independent oracle')
    return {'installed_key': int(result['key']), 'metadata': metadata, 'pixels': comparison,
            'scope': 'verified transport/pixel assertions; real host provenance additionally requires owned launch/process/artifact checks'}


def queue_templates(queue):
    from urllib.parse import unquote_to_bytes
    def decode(value):
        need(len(value) <= 1152, 'template field too large')
        raw = unquote_to_bytes(value)
        text = raw.decode('utf-8', 'strict')
        # Reject malformed/noncanonical escapes; host emits encodeURIComponent.
        from urllib.parse import quote
        need(quote(text, safe="~!*'()-._") == value and 0 < len(text) <= 128, 'invalid template encoding')
        return text
    encoded = queue.get('templates', '')
    need(queue.get('inventory_complete') == 'YES' and len(encoded) <= 2600 and encoded.endswith(';'),
         'incomplete output template inventory')
    rows = encoded[:-1].split(';')
    need(1 <= len(rows) <= 64, 'invalid template count')
    inventory = []
    for row in rows:
        parts = row.split(':'); need(len(parts) == 3, 'invalid template record')
        inventory.append(tuple(decode(v) for v in parts))
    names = [v[0] for v in inventory]; need(len(set(names)) == len(names), 'duplicate template names')
    selected = decode(queue.get('selected_template', ''))
    eligible = [v for v in inventory if v[1] == 'PNG Sequence' and v[2] in ('RGB', 'RGB + Alpha')]
    need(eligible and eligible[0][0] == selected and eligible[0][2] == queue.get('channels'),
         'selected template differs from observed PNG format')
    return {'selected': selected, 'inventory': inventory}


def verify_queue(record, raw_result, raw_metadata, raw_queue, image):
    result = fields(raw_result, 'AEHL-CAL-RESULT-2')
    metadata = fields(raw_metadata, 'AEHL-CAL-QUEUE-FRAME-1')
    queue = fields(raw_queue, 'AEHL-CAL-QUEUE-1')
    need(result.get('build') == metadata.get('build') == record['build_id'] and
         result.get('status') == 'LISTED_APPLIED_QUEUE_EXPORTED' and
         result.get('render') == 'QUEUE_PIXEL_CHECK_PENDING' and
         result.get('cleanup') == 'PASS' and result.get('cleanup_safe') == 'YES', 'queue native operation incomplete')
    need(int(result.get('key', '0')) != 0 and result['key'] == metadata.get('key') and
         0 <= int(metadata['counter_before']) < int(metadata['counter_after']) and
         metadata.get('working_space') == 'NONE', 'queue marker provenance differs')
    need(queue.get('status') == 'DONE' and queue.get('format') == 'PNG Sequence' and
         queue.get('width') == '64' and queue.get('height') == '48' and
         queue.get('time') == queue.get('duration') == '1/24', 'queue export scope differs')
    need(queue.get('revision') == metadata.get('revision') and
         queue.get('revision', '').isdigit() and int(queue['revision']) > 0, 'queue project revision differs')
    templates = queue_templates(queue)
    pixels, decoded = png.decode(image)
    need(queue.get('channels') == ('RGB' if decoded['source_channels'] == 3 else 'RGB + Alpha'),
         'export channels differ from PNG bytes')
    comparison = oracle.compare(pixels, 64, 48, record['seed'], order='RGBA8')
    need(comparison['pixel_status'] == 'PASS', 'queue pixels differ from independent oracle')
    return {'installed_key': int(result['key']), 'metadata': metadata, 'queue': queue,
            'templates': templates, 'png': decoded, 'pixels': comparison, 'png_sha256': hashlib.sha256(image).hexdigest(),
            'scope': 'startup-only queue control; no async receipt or late-registration proof'}


def prepare(manifest, expected_hash):
    raw = common.read(manifest, 4 * 1024 * 1024)
    need(hashlib.sha256(raw).hexdigest() == expected_hash, 'manifest hash changed')
    record = json.loads(raw); base = manifest.parent
    need(record['schema'] == 'AEHL-STARTUP-CALIBRATION-1' and record['source']['clean'] is True and
         record['observer_host_binding'] == 'PROSPECTIVE_ONLY_NOT_AUTHORIZATION' and
         record['install'] == record['AE_load'] == record['AE_render'] == record['late_registration'] == 'NOT RUN',
         'wrong candidate scope')
    run = record['run_id']; need(len(run) == 32 and set(run) <= set('0123456789abcdef'), 'invalid run identity')
    need(len(record['token']) == 32 and set(record['token']) <= set('0123456789abcdef'), 'invalid activation token')
    need(record['build_id'] == record['source']['commit'] + ':' + run and
         record['match_name'] == identity.marker_match(run) and record['seed'] == int(run[:6], 16), 'candidate identity differs')
    route = record.get('registration_route_discriminator', False)
    need(type(route) is bool and record.get('resource_match_name', record['match_name']) ==
         identity.resource_match(run, route), 'resource route identity differs')
    need(not route or record.get('trace_identity') is False, 'route discriminator cannot mix debugger trace')
    if route:
        proof = record.get('resource_pipl_identity', {})
        need(proof.get('status') == 'PASS' and proof.get('match') == record['resource_match_name'] and
             isinstance(proof.get('pipl_sha256'), str) and len(proof['pipl_sha256']) == 64 and
             set(proof['pipl_sha256']) <= set('0123456789abcdef'), 'compiled resource identity missing')
    common.no_links(HOST); common.no_links(PLUGIN_ROOT)
    need(common.sha_trusted_binary(HOST) == HOST_SHA, 'AE binary changed')
    install = PLUGIN_ROOT / ('AEHLStartupCalibration-' + run[:12])
    observer = 'AEHLCalibration' + run[:12]; marker = 'AEHLMarker' + run[:12]
    need(len(record['bundles']) == 2 and [b['bundle'] for b in record['bundles']] ==
         [marker + '.plugin', observer + '.plugin'], 'unexpected bundle inventory')
    need(record['config']['calibration_executable'] == str(HOST) and
         record['config']['calibration_module'] == str(install / (observer + '.plugin') / 'Contents/MacOS' / observer) and
         record['config']['calibration_marker_module'] == str(install / (marker + '.plugin') / 'Contents/MacOS' / marker) and
         record['config']['calibration_marker_sha256'] == record['bundles'][0]['binary_sha256'] and
         record['config']['calibration_control'] == str(base / 'control'), 'prospective scope differs')
    common.private_directory(base); common.private_directory(base / 'control', empty=True)
    need(not install.exists() and not install.is_symlink() and not (base / 'live').exists(), 'replay or occupied destination')
    need(record['offline_tests']['exact_marker_pixel_oracle']['pixel_status'] == 'PASS' and
         record['offline_tests']['frame'].startswith('PASS:21 SDK async frame cases') and
         record['offline_tests']['backend'].startswith('PASS:13 SDK-backend cases') and
         record['offline_tests'].get('request', '').startswith('PASS:14 owned request refusals; 5 owned SDK-acquisition cases;') and
         record['offline_tests']['inert'].startswith('PASS: 3 inert cases'), 'mandatory offline checks missing')
    for item in record['bundles']:
        bundle = base / item['bundle']; need(common.bundle_hashes(bundle) == item['files'], 'candidate bundle changed')
        binary = bundle / 'Contents/MacOS' / bundle.stem
        need(common.sha(binary) == item['binary_sha256'], 'signed executable changed')
        subprocess.run(['codesign', '--verify', '--strict', str(bundle)], check=True, capture_output=True, timeout=30)
    # Current code must match the exact tested/build source; documentation-only follow-up is allowed.
    for name, digest in record['source']['tracked_sha256'].items():
        path = Path(name); need(not path.is_absolute() and '..' not in path.parts, 'invalid source path')
        if path.suffix != '.md':
            need(common.sha(ROOT / path) == digest, 'live controller/source differs from built source')
    return record, base, install


def run(manifest, digest, execute, queue_mode=False, observation_mode=False):
    need(execute, 'explicit owned-startup execution authority required')
    need(not (queue_mode and observation_mode), 'execution modes are mutually exclusive')
    need(platform.system() == 'Darwin' and platform.machine() == 'arm64', 'wrong execution platform')
    record, base, install = prepare(manifest, digest)
    need(not record.get('registration_route_discriminator', False) or observation_mode,
         'route discriminator permits read-only observation only')
    need(not processes(), 'AE/aerender already running; preserve user session')
    if queue_mode:
        (base / 'control' / 'queue-output').mkdir(mode=0o700)
    live = base / 'live'; live.mkdir(mode=0o700)
    before = {p.name: (p.lstat().st_ino, p.lstat().st_mtime_ns, p.lstat().st_mode) for p in PLUGIN_ROOT.iterdir()}
    report = {'schema': 'AEHL-STARTUP-LIVE-1', 'build_id': record['build_id'], 'source': record['source']['commit'],
              'scope': 'one owned startup/read-only registry provenance observation' if observation_mode else
                       'one owned startup/apply/script Render Queue control' if queue_mode else
                       'one owned normal startup/public-SDK apply/asynchronous frame', 'result': 'UNKNOWN',
              'installation': 'NOT RUN', 'launch': 'NOT RUN', 'publication': 'NOT SENT', 'cleanup': 'NOT RUN',
              'late_registration': 'NOT RUN', 'private_calls': 'NOT RUN', 'user_authority':
              'user authorized the fourteen-step conditional reader/publication packet' if observation_mode else
              'user authorized the ten-step separate control-render packet' if queue_mode else
              'user said делай after the proposed separate controlled AE startup/apply/frame run'}
    child = None; observed = None
    try:
        write(live / 'plugin-entry-baseline.json', json.dumps(before, sort_keys=True).encode())
        install.mkdir(mode=0o700)
        for item in record['bundles']:
            shutil.copytree(base / item['bundle'], install / item['bundle'], symlinks=True)
            need(common.bundle_hashes(install / item['bundle']) == item['files'], 'installed bytes differ')
            subprocess.run(['codesign', '--verify', '--strict', str(install / item['bundle'])],
                           check=True, capture_output=True, timeout=30)
        report['installation'] = 'PASS: exact two unique bundles, no replacement'
        write(live / 'attempt.json', json.dumps(report, indent=2).encode())
        need(not processes() and common.sha_trusted_binary(HOST) == HOST_SHA, 'host changed or a session opened before launch')
        env = {k: v for k, v in os.environ.items() if not k.startswith(('AEHL_', 'AE_HOT_LOADER_'))}
        env['AEHL_STARTUP_CALIBRATION_TOKEN'] = record['token']
        with (live / 'host-stdout.log').open('xb') as stdout, (live / 'host-stderr.log').open('xb') as stderr:
            os.chmod(stdout.name, 0o600); os.chmod(stderr.name, 0o600)
            child = subprocess.Popen([str(HOST)], cwd=live, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        report['launch'] = 'STARTED'; report['pid'] = child.pid
        stop = time.monotonic() + 180
        control = base / 'control'
        while not (control / 'ready').exists():
            need(child.poll() is None, 'owned host exited before ready')
            need(time.monotonic() < stop, 'startup timed out; preserve unknown host state')
            log_budget(live); time.sleep(0.2)
        observed = common.process_identity(child.pid)
        need(observed['executable'] == str(HOST) and processes() == [child.pid], 'owned host identity/exclusivity differs')
        ready_identity(common.read(control / 'ready', 512), record, observed)
        for item in record['bundles']:
            need(common.bundle_hashes(install / item['bundle']) == item['files'], 'loaded candidate files changed')
        report['owned_process'] = observed; report['launch'] = 'PASS: exact owned PID/birth/executable/ready'
        write(live / 'launch.json', json.dumps({'owned_process': observed, 'build_id': record['build_id']}, indent=2).encode())
        # Independent monotonic operation budget begins before publication and is never reset.
        stop = time.monotonic() + 120
        need(common.process_identity(child.pid) == observed and processes() == [child.pid], 'process changed before publication')
        report['publication'] = 'OUTCOME UNKNOWN'  # before entering atomic publication
        data = request(record, observed, int(time.time()) + 110, queue_mode, observation_mode)
        write(live / 'publication-intent.json', json.dumps({'build_id': record['build_id'],
              'request_sha256': hashlib.sha256(data).hexdigest(), 'outcome': 'UNKNOWN UNTIL JOURNAL'}, indent=2).encode())
        publish(control, data)
        report['publication'] = 'SENT ONCE'
        while not (control / 'result').exists():
            need(child.poll() is None, 'owned host exited during operation')
            need(time.monotonic() < stop, 'operation timed out; no retry or assumed rollback')
            log_budget(live); time.sleep(0.1)
        need(time.monotonic() < stop and common.process_identity(child.pid) == observed, 'late result or changed process')
        raw_result = common.read(control / 'result', 4096)
        report['native_result'] = fields(raw_result, 'AEHL-CAL-RESULT-2')
        if observation_mode:
            need(not any((control / leaf).exists() for leaf in ('begin', 'render-started', 'queue-output', 'frame.argb')),
                 'read-only request unexpectedly entered mutation/render')
            comparison = verify_observation(record, raw_result,
                [common.read(control / f'names-{i}', 8192) for i in range(3)])
        elif queue_mode:
            need(report['native_result'].get('status') == 'LISTED_APPLIED_QUEUE_EXPORTED',
                 'queue control refused/incomplete; no exported pixels accepted')
            output = control / 'queue-output'; common.private_directory(output)
            files = list(output.iterdir())
            need(len(files) == 1 and files[0].name.startswith('control') and files[0].suffix == '.png',
                 'expected exactly one owned PNG output')
            comparison = verify_queue(record, raw_result, common.read(control / 'queue-metadata', 4096),
                common.read(control / 'queue-result', 4096), common.read(files[0], png.MAX_FILE))
        else:
            native_complete(record, raw_result)  # refuse before opening nonexistent frame files
            comparison = verify_capture(record, raw_result,
                common.read(control / 'frame-metadata', 4096), common.read(control / 'frame.argb', 64 * 48 * 4))
        need(time.monotonic() < stop, 'verification exceeded original operation budget')
        report.update(comparison); report['result'] = 'PASS'
        report['host_provenance'] = 'OWNED AE READ-ONLY STARTUP' if observation_mode else \
            'OWNED AE STARTUP/APPLY/SCRIPT RENDER QUEUE' if queue_mode else 'OWNED AE SDK STARTUP/APPLY/ASYNC FRAME'
    except Exception as error:
        report['result'] = 'FAIL_OR_UNKNOWN'; report['reason'] = str(error)
    finally:
        # SIGTERM can enter AE crash handling; never use it as a normal quit.
        # A live owned host is preserved for manual closure, even with fresh proof.
        try:
            control = base / 'control'
            report['cleanup'] = preserve_owned_host(child, control, record, observed)
        except Exception as error:
            report['cleanup'] = 'BLOCKED_OR_UNKNOWN: ' + str(error)
        # An exit/proof failure must not skip independent installation checks.
        try:
            if not processes() and install.exists():
                need(set(p.name for p in install.iterdir()) == {b['bundle'] for b in record['bundles']}, 'installation scope changed')
                for item in record['bundles']:
                    need(common.bundle_hashes(install / item['bundle']) == item['files'], 'retirement bytes changed')
                shutil.move(str(install), str(live / 'retired-installation'))
                report['installation_retirement'] = 'OWNED UNIQUE DIRECTORY RETAINED OUTSIDE PLUGIN DISCOVERY'
            after = {p.name: (p.lstat().st_ino, p.lstat().st_mtime_ns, p.lstat().st_mode)
                     for p in PLUGIN_ROOT.iterdir() if p != install}
            need(after == before, 'original plugin entries changed; no further cleanup')
            report['other_plugin_entries'] = 'UNCHANGED'
        except Exception as error:
            report['installation_cleanup'] = 'BLOCKED_OR_UNKNOWN: ' + str(error)
        write(live / 'result.json', json.dumps(report, indent=2).encode())
    print(json.dumps({'result': report['result'], 'cleanup': report['cleanup'], 'report': str(live / 'result.json')}))
    # A frame PASS is separate from manual closure and its supplemental receipt.
    return 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, required=True); parser.add_argument('--sha256', required=True)
    parser.add_argument('--execute-owned-startup', action='store_true')
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--control-render-queue', action='store_true', help='separate one-frame PNG control; never invokes async receipt capture')
    mode.add_argument('--observe-registry', action='store_true', help='read-only startup enumeration/provider metadata; no Apply or render')
    args = parser.parse_args()
    return run(args.manifest.resolve(strict=True), args.sha256, args.execute_owned_startup,
               args.control_render_queue, args.observe_registry)


if __name__ == '__main__':
    raise SystemExit(main())
