"""Supervise ONE diagnostic capture. Never installs/launches/stops AE or calls registration."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
import zipfile

import run_no_scan_directory_probe as common
from build_cleanup_observation_probe import UUIDS, HOST_SHA256
from collect_resource_search_abi import INPUTS
from collect_resource_roots import REQUESTS
from mach_o_root_metadata import parse_roots

require = common.require
NATIVE_NAMES = common.NATIVE_NAMES
MAX_ADDRESS = (1 << 64) - 1


def profile():
    return {key: {'path': str(INPUTS[key][0]), 'sha256': INPUTS[key][1], 'uuid': UUIDS[key],
                  'root_vm': 0x18490 if key == 'PLUG' else 0x10fd70, 'root_size': 8 if key == 'PLUG' else 16}
            for key in ('PLUG', 'MEE')}


def verify_providers(record):
    require(record['provider_profile'] == profile(), 'diagnostic profile differs from reviewed constants')
    hashes = {}
    for key, expected in profile().items():
        raw = common.read_trusted_binary(expected['path'])
        digest = hashlib.sha256(raw).hexdigest()
        require(digest == expected['sha256'], 'diagnostic provider file changed')
        metadata = parse_roots(raw, REQUESTS[key])
        require(metadata['uuid'] == expected['uuid'], 'diagnostic provider UUID changed')
        hashes[expected['path']] = digest
    require(record['host_sha256'] == HOST_SHA256 and
            common.sha_trusted_binary(record['host_executable']) == HOST_SHA256, 'host file changed')
    return hashes


def expected_request(record, observed):
    token = record['activation_env']['AEHL_CLEANUP_OBSERVER_TOKEN']
    return ('version=1\nkind=cleanup-observer\nbuild_id=' + record['build_id'] +
            '\nrun_id=' + record['run_id'] + '\npid=' + str(observed['pid']) +
            '\nstart=' + observed['start'] + '\ntoken=' + token +
            '\nread_only=authorized\ncontract=reviewed\n').encode()


def prepare(manifest, expected_hash, pid, authorized_host, authorized_bundle,
            identity_fn=common.process_identity, provider_verifier=verify_providers,
            signature_fn=lambda bundle: subprocess.run(['codesign', '--verify', '--strict', str(bundle)],
                check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)):
    require(pid > 0 and authorized_host is not None and authorized_bundle is not None, 'exact host/bundle/PID required')
    manifest = Path(manifest).absolute(); raw = common.read(manifest, 4 * 1024 * 1024)
    require(hashlib.sha256(raw).hexdigest() == expected_hash, 'manifest hash mismatch')
    r = json.loads(raw)
    require(r['target'] == 'aarch64-apple-darwin' and len(r['source_commit']) == 40 and
            set(r['source_commit']) <= set('0123456789abcdef') and
            r['run_id'].startswith('cleanup-observer-') and len(r['run_id']) == 49 and
            set(r['run_id'][17:]) <= set('0123456789abcdef') and
            r['build_id'].startswith('observe-') and len(r['build_id']) == 20 and
            set(r['build_id'][8:]) <= set('0123456789abcdef') and
            r['kind'] == 'research-only-cleanup-observer-aegp' and r['source_clean'] is True and
            r['host_mode'] == 'authorized-user-host' and r['installation_performed'] is False and
            r['ae_launch_performed'] is False and r['native_timeout_ms'] == 15000 and
            r['checks'] == {'build_sign_exports': 'PASS', 'identity_getter': 'PASS', 'inert_entrypoint': 'PASS', 'live_ae': 'NOT RUN'},
            'wrong diagnostic artifact')
    require(r['host_executable'] == str(authorized_host) and r['authorized_bundle'] == str(authorized_bundle), 'scope mismatch')
    common.no_links(authorized_host); common.no_links(authorized_bundle)
    require(common.bundle_hashes(authorized_bundle) == r['files'], 'installed bundle differs from candidate')
    require(Path(r['module_path']).parent.parent.parent == Path(authorized_bundle) and
            Path(r['module_path']).is_file(), 'module path outside authorized bundle')
    signature_fn(authorized_bundle)
    control, journal = Path(r['control_directory']), Path(r['journal_directory'])
    require(control == manifest.parent / 'control' and journal == manifest.parent / 'journal', 'evidence outside build')
    common.private_directory(control); common.private_directory(journal, empty=True)
    require({p.name for p in control.iterdir()} == {'ready.txt'}, 'diagnostic control already consumed')
    observed = identity_fn(pid); require(observed['executable'] == r['host_executable'], 'wrong host PID')
    _, start = common.identity_from_ready(r, common.read(control / 'ready.txt', 16384), pid)
    require(start == observed['start'], 'loaded/supervisor process-start mismatch'); r['loaded_process_start'] = start
    providers = provider_verifier(r)
    require(identity_fn(pid) == observed, 'host changed during preparation')
    return r, control, journal, observed, expected_request(r, observed), providers


def uint(value, limit=MAX_ADDRESS):
    require(isinstance(value, str) and value.isascii() and value.isdigit() and
            value == str(int(value)) and int(value) <= limit, 'invalid unsigned diagnostic number')
    return int(value)


def single(fields, key):
    require(len(fields.get(key, [])) == 1, 'missing/duplicate diagnostic field: ' + key)
    return fields[key][0]


def word(data, at, size=8):
    require(at + size <= len(data), 'truncated diagnostic word')
    return int.from_bytes(data[at:at + size], 'little')


def mapping_records(fields, prefix, count):
    addresses, sizes, mappings = [fields.get(prefix + key, []) for key in ('address', 'size', 'mapping')]
    require(len(addresses) == len(sizes) == len(mappings) == count, 'mapping record count mismatch')
    result = []
    for a, s, text in zip(addresses, sizes, mappings):
        address, size = uint(a), uint(s)
        parts = text.split(','); require(len(parts) == 8, 'mapping provenance shape')
        base, extent, offset, obj, tag, depth, prot, maximum = [uint(p) for p in parts]
        require(address > 0 and size > 0 and address <= MAX_ADDRESS - size and base > 0 and extent > 0 and
                base <= MAX_ADDRESS - extent and base <= address and address - base < extent and
                size <= extent - (address - base), 'mapping containment mismatch')
        require(obj <= 0xffffffff and tag <= 0xffffffff and depth <= 16 and prot in (1, 3) and
                maximum <= 7 and prot & ~maximum == 0, 'mapping protection/depth mismatch')
        result.append((address, size))
    return result


def verify_diagnostic(fields, root_addresses):
    scalar = {'scope', 'success', 'failure', 'read_calls', 'read_bytes', 'global_address', 'global_hex',
              'general_plugin_records', 'callback_count', 'frame_count', 'read_count', 'containment_count'}
    repeated = {'callback_target', 'callback_context', 'frame_address', 'frame_hex',
                'read_address', 'read_size', 'read_mapping', 'containment_address', 'containment_size', 'containment_mapping'}
    require(set(fields) <= scalar | repeated and scalar <= set(fields), 'unexpected diagnostic authority/field')
    require(single(fields, 'scope') == 'cleanup-observer' and single(fields, 'success') == '1' and
            single(fields, 'failure') == '', 'diagnostic capture failed')
    calls, size = uint(single(fields, 'read_calls'), 24), uint(single(fields, 'read_bytes'), 16384)
    callbacks = uint(single(fields, 'callback_count'), 256)
    count = uint(single(fields, 'frame_count'), 6)
    require(count == (6 if callbacks else 5), 'diagnostic frame count')
    addresses, encoded = fields.get('frame_address', []), fields.get('frame_hex', [])
    require(len(addresses) == len(encoded) == count, 'diagnostic frame inventory')
    frames = []
    for address, text in zip(addresses, encoded):
        require(len(text) <= 8192 and len(text) % 2 == 0 and set(text) <= set('0123456789abcdef'), 'invalid frame bytes')
        frames.append((uint(address), bytes.fromhex(text)))
    sizes = [8, 24, 8, 72] + ([callbacks * 16] if callbacks else []) + [16]
    require([len(b) for _, b in frames] == sizes and all(a > 0 and a % 8 == 0 for a, _ in frames), 'diagnostic frame range')
    global_address = uint(single(fields, 'global_address'))
    global_hex = single(fields, 'global_hex')
    require(global_address == root_addresses['PLUG'] and len(global_hex) == 16 and
            set(global_hex) <= set('0123456789abcdef') and word(bytes.fromhex(global_hex), 0) == frames[0][0], 'global/handle mismatch')
    require(word(frames[0][1], 0) == frames[1][0] and word(frames[1][1], 16) == frames[2][0] and
            word(frames[2][1], 0) == frames[3][0], 'diagnostic pointer chain')
    header = frames[3][1]
    require(word(header, 0, 4) == 0x00d00bee and word(header, 16, 4) == callbacks and word(header, 24, 4) == 16, 'diagnostic LIST header')
    targets, contexts = fields.get('callback_target', []), fields.get('callback_context', [])
    require(len(targets) == len(contexts) == callbacks, 'callback inventory')
    if callbacks:
        require(frames[4][0] == frames[3][0] + 72, 'payload address')
        for i, (target, context) in enumerate(zip(targets, contexts)):
            t, c = uint(target), uint(context)
            require(t > 0 and t % 4 == 0 and word(frames[4][1], i * 16) == t and
                    word(frames[4][1], i * 16 + 8) == c, 'ordered callback bytes mismatch')
    require(frames[-1][0] == root_addresses['MEE'], 'MEE root mismatch')
    begin, end = word(frames[-1][1], 0), word(frames[-1][1], 8)
    records = uint(single(fields, 'general_plugin_records'), 8192)
    require(begin % 8 == 0 and end % 8 == 0 and end >= begin and (end - begin) % 0xb0 == 0 and
            (end - begin) // 0xb0 == records and ((begin == end == 0) or begin != 0), 'retained vector mismatch')
    read_count = uint(single(fields, 'read_count'), 24)
    require(read_count == calls == (20 if callbacks else 17), 'read count/budget mismatch')
    reads = mapping_records(fields, 'read_', read_count)
    expected = [(global_address, 8)] + [(a, len(b)) for a, b in frames] * 3 + [(global_address, 8)]
    require(reads == expected and sum(s for _, s in reads) == size and all(s <= 4096 for _, s in reads), 'read sequence/byte budget mismatch')
    containment = uint(single(fields, 'containment_count'), 1)
    ranges = mapping_records(fields, 'containment_', containment)
    require(ranges == ([(begin, max(1, end - begin))] if begin else []), 'record containment mismatch')
    return {'callback_count': callbacks, 'general_plugin_records': records, 'read_calls': calls, 'read_bytes': size,
            'claim': 'diagnostic-only-not-complete-or-registration-eligibility'}


def verify_native_pass(record, journal, observed):
    require({p.name for p in journal.iterdir()} == NATIVE_NAMES, 'diagnostic journal incomplete/unexpected')
    before, after = [common.unwrap_journal(journal / (name + '.txt')) for name in ('before', 'after')]
    o, added = common.compatible_observations(before, after)
    claim_payload = common.unwrap_journal(journal / 'claim.txt'); require(claim_payload.endswith(before), 'claim/baseline mismatch')
    plan = claim_payload[:-len(before)]; expected_plan = {
        'scope': 'cleanup-observer', 'run': record['run_id'], 'source': record['source_commit'], 'build': record['build_id'],
        'executable': record['host_executable'], 'module': record['module_path'], 'journal': record['journal_directory'], 'timeout_ms': '15000'}
    require(common.field_map(plan) == {k: [v] for k, v in expected_plan.items()}, 'claim scope mismatch')
    require(set(o) == {'pid', 'start', 'executable', 'module', 'version', 'arch', 'build', 'main_thread',
        'unsaved', 'dirty', 'rendering', 'items', 'queued', 'revision', 'registry_count', 'effect',
        'image_count', 'image_path', 'image_header', 'image_slide'}, 'unexpected baseline fields')
    expected = {'pid': str(observed['pid']), 'start': observed['start'], 'executable': record['host_executable'],
        'module': record['module_path'], 'version': '25.6x101', 'arch': 'arm64', 'build': '101',
        'main_thread': '1', 'unsaved': '1', 'dirty': '0', 'rendering': '0', 'items': '0', 'queued': '0'}
    require(all(o.get(k) == [v] for k, v in expected.items()) and record['loaded_process_start'] == observed['start'], 'host baseline mismatch')
    uint(single(o, 'revision')); require(uint(single(o, 'revision')) > 0, 'zero revision')
    effects = o.get('effect', []); require(0 < len(effects) <= 20000 and len(effects) == len(set(effects)) and
        o.get('registry_count') == [str(len(effects))], 'registry inventory mismatch')
    images = common.observation_images(o); require(len(images) <= 8192 and all(uint(h) > 0 for _, h, _ in images), 'image range')
    require(record['module_path'] in [p for p, _, _ in images], 'helper absent from image list')
    roots = {}
    for key, pin in profile().items():
        matches = [uint(h) for p, h, _ in images if p == pin['path']]
        require(len(matches) == 1 and matches[0] > 0 and matches[0] <= MAX_ADDRESS - pin['root_vm'], 'provider runtime identity absent/ambiguous')
        roots[key] = matches[0] + pin['root_vm']
    require(common.unwrap_journal(journal / 'call-started.txt') == plan + before, 'read marker/baseline mismatch')
    native = verify_diagnostic(common.field_map(common.unwrap_journal(journal / 'native.txt')), roots)
    expected_result = {'scope': 'cleanup-observer', 'status': 'PASS', 'stage': 'complete', 'reason': 'matching-diagnostic-only',
                       'claimed': '1', 'read_started': '1', 'diagnostic_saved': '1', 'postflight_saved': '1'}
    require(common.field_map(common.unwrap_journal(journal / 'result.txt')) == {k: [v] for k, v in expected_result.items()}, 'diagnostic final result mismatch')
    return {**native, 'registry_count': len(effects), 'lazy_system_images': [p for p, _, _ in added],
            'before_sha256': hashlib.sha256(before).hexdigest(), 'after_sha256': hashlib.sha256(after).hexdigest()}


def supervise(record, control, journal, observed, request, providers, timeout,
              identity_fn=common.process_identity, provider_verifier=verify_providers,
              publish_fn=common.publish, clock=time.monotonic, sleep=time.sleep, report_path=None):
    require(20 <= timeout <= 60, 'invalid supervisor timeout')
    common.private_directory(control); common.private_directory(journal, empty=True)
    started = datetime.now(timezone.utc).isoformat(); deadline = clock() + timeout
    common.write_json_exclusive(control / 'supervisor-claim.json', {'host': observed, 'run_id': record['run_id'],
        'build_id': record['build_id'], 'started_utc': started, 'read_only_authorized': True})
    status, reason, published, native = 'FAIL', 'not published', False, None
    try:
        require(identity_fn(observed['pid']) == observed, 'host changed before request')
        require(provider_verifier(record) == providers, 'provider changed before request')
        require(clock() < deadline, 'timeout before publication; attempt consumed; no retry')
        publish_fn(control, request); published = True
        while clock() < deadline:
            require(identity_fn(observed['pid']) == observed, 'host exited/changed')
            if (control / 'adapter-stopped.txt').exists(): raise ValueError('diagnostic adapter stopped; no retry')
            if (journal / 'result.txt').exists():
                native = verify_native_pass(record, journal, observed)
                require(identity_fn(observed['pid']) == observed and provider_verifier(record) == providers, 'identity changed after capture')
                require(common.bundle_hashes(record['authorized_bundle']) == record['files'], 'installed helper changed')
                require(clock() < deadline, 'timeout during verification; native state preserved; no retry')
                status, reason = 'PASS', 'matching diagnostic only; registration/complete cleanup NOT PROVEN'; break
            sleep(0.2)
        else: reason = 'timeout; native state preserved; no retry'
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, json.JSONDecodeError) as e: reason = str(e)
    result = {'status': status, 'reason': reason, 'host': observed, 'run_id': record['run_id'], 'build_id': record['build_id'],
        'source_commit': record['source_commit'], 'native': native, 'provider_hashes': providers,
        'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(), 'request_published': published,
        'timeout_seconds': timeout, 'process_stopped': False, 'plugin_scan_requested': False, 'private_adobe_call_requested': False,
        'installation_performed': False, 'ae_launch_performed': False}
    common.write_json_exclusive(control / 'supervisor.json', result)
    archive = common.package_report(record, control, journal, report_path or control.parent / ('AEHL-Cleanup-' + record['build_id'] + '.zip'))
    return result, archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path); parser.add_argument('--sha256', required=True)
    parser.add_argument('--pid', type=int, required=True); parser.add_argument('--authorized-host', type=Path, required=True)
    parser.add_argument('--authorized-bundle', type=Path, required=True)
    parser.add_argument('--timeout', type=int, default=45, choices=range(20, 61), metavar='20..60')
    parser.add_argument('--authorize-read-only', action='store_true'); parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    try:
        prepared = prepare(args.manifest, args.sha256, args.pid, args.authorized_host, args.authorized_bundle)
        if not args.execute: print('PASS: preparation only; no request published'); return
        require(args.authorize_read_only, 'fresh read-only scope required')
        result, archive = supervise(*prepared, args.timeout)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, json.JSONDecodeError) as e: parser.exit(2, 'BLOCKED: ' + str(e) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True)); print('Report: ' + str(archive)); print('Report SHA-256: ' + common.sha(archive))
    raise SystemExit(0 if result['status'] == 'PASS' else 1)


if __name__ == '__main__':
    main()
