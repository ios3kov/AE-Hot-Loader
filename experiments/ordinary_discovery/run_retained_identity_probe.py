"""One read-only name request and independent evidence checks; never installs/launches/stops AE."""
import argparse
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import zipfile
import run_no_scan_directory_probe as common
import verify_retained_host_journal as host
import verify_retained_identity_journal as copied
from build_retained_identity_probe import UUIDS, HOST_SHA256
from collect_resource_search_abi import INPUTS
from collect_resource_roots import REQUESTS
from mach_o_root_metadata import parse_roots
require = common.require


def profile():
    return {'MEE': {'path': str(INPUTS['MEE'][0]), 'sha256': INPUTS['MEE'][1],
        'uuid': UUIDS['MEE'], 'root_vm': 0x10fd70, 'root_size': 16, 'base_vm': 0}}


def verify_providers(record):
    require(record['provider_profile'] == profile(), 'fixed MEE profile mismatch')
    pin = profile()['MEE']; raw = common.read_trusted_binary(pin['path'])
    require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'MEE file changed')
    metadata = parse_roots(raw, REQUESTS['MEE'])
    require(metadata['uuid'] == pin['uuid'] and int(metadata['image_base_vm'], 16) == pin['base_vm'],
            'MEE UUID/base changed')
    require(record['host_sha256'] == HOST_SHA256 and
            common.sha_trusted_binary(record['host_executable']) == HOST_SHA256, 'host file changed')
    return {pin['path']: pin['sha256']}


def expected_request(record, observed):
    token = record['activation_env']['AEHL_RETAINED_IDENTITY_TOKEN']
    require(re.fullmatch('[0-9a-f]{32}', token) is not None, 'invalid activation identity')
    return ('version=1\nkind=retained-identity\nbuild_id=' + record['build_id'] +
        '\nrun_id=' + record['run_id'] + '\nsource=' + record['source_commit'] +
        '\npid=' + str(observed['pid']) + '\nstart=' + observed['start'] + '\ntoken=' + token +
        '\nbinary_sha256=' + record['binary_sha256'] +
        '\nread_only=authorized\ncontract=reviewed\n').encode()


def prepare(manifest, expected_hash, pid, authorized_host, authorized_bundle,
            identity_fn=common.process_identity, provider_verifier=verify_providers,
            signature_fn=lambda bundle: subprocess.run(['codesign', '--verify', '--strict', str(bundle)],
                check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30)):
    require(type(pid) is int and pid > 0 and authorized_host is not None and authorized_bundle is not None, 'exact host/bundle/PID required')
    manifest = Path(manifest).absolute(); raw = common.read(manifest, 4 * 1024 * 1024)
    require(hashlib.sha256(raw).hexdigest() == expected_hash, 'manifest hash mismatch')
    r = json.loads(raw)
    require(r['target'] == 'aarch64-apple-darwin' and len(r['source_commit']) == 40 and
            set(r['source_commit']) <= set('0123456789abcdef') and
            r['run_id'].startswith('retained-identity-') and len(r['run_id']) == 50 and
            set(r['run_id'][18:]) <= set('0123456789abcdef') and
            r['build_id'].startswith('identity-') and len(r['build_id']) == 21 and
            set(r['build_id'][9:]) <= set('0123456789abcdef') and
            r['kind'] == 'research-only-retained-identity-aegp' and r['source_clean'] is True and
            r['host_mode'] == 'authorized-user-host' and r['installation_performed'] is False and
            r['ae_launch_performed'] is False and r['native_timeout_ms'] == 15000 and r['external_supervisor'] == 'AVAILABLE-NOT-RUN' and
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
    r['binary_sha256'] = r['files'][str(Path(r['module_path']).relative_to(authorized_bundle))]
    require(len(r['binary_sha256']) == 64, 'missing final binary hash')
    providers = provider_verifier(r)
    require(identity_fn(pid) == observed, 'host changed during preparation')
    return r, control, journal, observed, expected_request(r, observed), providers


def policy(record, observed):
    parts = observed['start'].split('.')
    require(len(parts) == 2, 'process start format')
    sec, usec = [host.uint(p) for p in parts]
    require(sec > 0 and usec < 1000000 and type(observed['pid']) is int, 'process start/PID bounds')
    pin = profile()['MEE']
    values = ('retained-identity', 'mee-25.6-arm64-1', 'ae-diagnostic',
        record['run_id'], record['source_commit'], record['build_id'], record['binary_sha256'],
        str(observed['pid']), str(sec), str(usec), pin['sha256'], pin['uuid'], '8')
    p = {**dict(zip(copied.SCOPE_KEYS, values)), 'protocol': 'retained-host-1',
        'executable_hex': os.fsencode(record['host_executable']).hex(),
        'module_hex': os.fsencode(record['module_path']).hex(),
        'journal_hex': os.fsencode(record['journal_directory']).hex(), 'timeout_ms': '15000'}
    host.validate_plan(p); return p


def derived_policy(records, base):
    # The claimed root is used only to parse bounded inventory, never as our expected address.
    claim = host.fields(host.unwrap(records['claim.txt'], 'claim.txt'))
    require(len(claim) == len(host.PLAN_KEYS) + 1 and
            tuple(k for k, _ in claim[:-1]) == host.PLAN_KEYS and claim[-1][0] == 'before_hex',
            'claim plan inventory')
    claimed = dict(claim[:-1]); host.validate_plan(claimed)
    require(all(claimed[k] == base[k] for k in host.PLAN_KEYS if k != 'root'), 'untrusted claim scope changed')
    observed = host.observation(claim[-1][1], claimed)
    pin = profile()['MEE']; images = observed['images']
    mee = [(h, s) for p, h, s in images if p == os.fsencode(pin['path'])]
    helper = [(h, s) for p, h, s in images if p == bytes.fromhex(base['module_hex'])]
    require(len(mee) == len(helper) == 1, 'MEE/helper image absent or ambiguous')
    header, slide = mee[0]
    require(pin['base_vm'] + slide == header and pin['root_vm'] >= pin['base_vm'] and
            header <= copied.MAX_ADDRESS - (pin['root_vm'] - pin['base_vm']), 'MEE slide/root overflow')
    p = base.copy(); p['root'] = str(header + pin['root_vm'] - pin['base_vm'])
    host.validate_plan(p); return p


def verify_native_pass(record, journal, observed, *, started_ns, now_ns=time.monotonic_ns):
    base = policy(record, observed)
    require(os.fsencode(journal).hex() == base['journal_hex'], 'unexpected evidence directory')
    budget = host.Budget(started_ns, now_ns); budget.tick()
    def verify(records, frozen):
        budget.tick(); expected = derived_policy(records, frozen)
        return host.verify_records(records, expected, started_ns=started_ns, now_ns=now_ns)
    # One bounded no-follow read, identity rechecked AFTER verification. No double-read root race.
    result = copied._verify_directory(journal, base, host.NAMES, host.PAYLOAD_LIMIT, verify)
    budget.tick(); return result


def write_json(path, value):
    raw = (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(raw); stream.flush(); os.fsync(stream.fileno())
    directory = os.open(Path(path).parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try: os.fsync(directory)
    finally: os.close(directory)


def package_report(record, control, journal):
    sanitized = {k: v for k, v in record.items() if k not in ('activation_env', 'command')}
    write_json(control / 'report-artifact.json', sanitized)
    files = {}
    for path in [control / n for n in ('ready.txt', 'adapter-stopped.txt', 'supervisor-claim.json',
                                      'supervisor.json', 'report-artifact.json')] + [journal / n for n in host.NAMES]:
        if path.exists():
            name = path.name if path.parent == control else 'journal/' + path.name
            files[name] = common.read(path, host.PAYLOAD_LIMIT + 128)
    token = record['activation_env']['AEHL_RETAINED_IDENTITY_TOKEN'].encode()
    require(all(token not in raw for raw in files.values()), 'activation token in report')
    hashes = {n: hashlib.sha256(b).hexdigest() for n, b in files.items()}
    files['report-hashes.json'] = (json.dumps(hashes, sort_keys=True) + '\n').encode()
    destination = control.parent / ('AEHL-Retained-' + record['build_id'] + '.zip')
    # Private/exclusive archive from the already bounded bytes, never reopen evidence for packaging.
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as z:
            for name, raw in files.items(): z.writestr(name, raw)
        stream.flush(); os.fsync(stream.fileno())
    with zipfile.ZipFile(destination) as z:
        require(z.testzip() is None and set(z.namelist()) == set(files), 'report ZIP inventory/CRC')
        require(all(hashlib.sha256(z.read(n)).hexdigest() == h for n, h in hashes.items()), 'report ZIP hashes')
    return destination


def supervise(record, control, journal, observed, request, providers, *, authorized=False,
              identity_fn=common.process_identity, provider_verifier=verify_providers,
              bundle_fn=common.bundle_hashes, publish_fn=common.publish,
              clock_ns=time.monotonic_ns, sleep=time.sleep):
    require(authorized is True, 'fresh exact read-only execution authority required')
    r, observed, providers = deepcopy(record), deepcopy(observed), deepcopy(providers)
    request = bytes(request)
    require(request == expected_request(r, observed), 'request retargeted after preparation')
    base = policy(r, observed); host.validate_plan(base)
    require(str(control) == r['control_directory'] and str(journal) == r['journal_directory'],
            'control/journal path retargeted')
    common.private_directory(control); common.private_directory(journal, empty=True)
    require({p.name for p in control.iterdir()} == {'ready.txt'}, 'attempt already consumed')
    started_ns = clock_ns(); budget = host.Budget(started_ns, clock_ns)
    started = datetime.now(timezone.utc).isoformat()
    write_json(control / 'supervisor-claim.json', {'host': observed, 'source_commit': r['source_commit'],
        'run_id': r['run_id'], 'build_id': r['build_id'], 'started_ns': started_ns,
        'started_utc': started, 'read_only_authorized': True})
    status, reason, attempted, published, native = 'FAIL', 'not published', False, False, None
    try:
        budget.tick()
        require(identity_fn(observed['pid']) == observed, 'host changed before publication')
        _, ready_start = common.identity_from_ready(r, common.read(control / 'ready.txt', 16384), observed['pid'])
        require(ready_start == observed['start'], 'ready process start changed')
        require(provider_verifier(r) == providers and bundle_fn(r['authorized_bundle']) == r['files'],
                'provider/helper changed before publication')
        budget.tick(); attempted = True; publish_fn(control, request); published = True; budget.tick()
        while True:
            budget.tick(); require(identity_fn(observed['pid']) == observed, 'host exited/changed')
            if (control / 'adapter-stopped.txt').exists(): raise ValueError('native adapter stopped; no retry')
            if (journal / 'result.txt').exists():
                native = verify_native_pass(r, journal, observed, started_ns=started_ns, now_ns=clock_ns)
                require(identity_fn(observed['pid']) == observed and provider_verifier(r) == providers and
                        bundle_fn(r['authorized_bundle']) == r['files'], 'identity changed after verification')
                budget.tick(); status, reason = 'PASS', 'guarded retained-name diagnostic only'; break
            sleep(0.1)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, json.JSONDecodeError) as e:
        reason = str(e)
    result = {'status': status, 'reason': reason, 'source_commit': r['source_commit'], 'build_id': r['build_id'],
        'run_id': r['run_id'], 'host': observed, 'native': native, 'provider_hashes': providers,
        'started_ns': started_ns, 'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
        'request_attempted': attempted, 'request_published': published, 'publication_unknown': attempted and not published,
        'timeout_ms': 15000, 'diagnostic_verified_within_budget': status == 'PASS',
        'evidence_packaging_outside_operation_budget': True, 'host_execution_verified': False, 'process_stopped': False,
        'installation_performed': False, 'ae_launch_performed': False, 'private_adobe_call_requested': False}
    write_json(control / 'supervisor.json', result)
    return result, package_report(r, control, journal)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest', type=Path); parser.add_argument('--sha256', required=True)
    parser.add_argument('--pid', type=int, required=True); parser.add_argument('--authorized-host', type=Path, required=True)
    parser.add_argument('--authorized-bundle', type=Path, required=True)
    parser.add_argument('--authorize-read-only', action='store_true'); parser.add_argument('--execute', action='store_true')
    args = parser.parse_args()
    try:
        require(not args.execute or args.authorize_read_only, 'fresh exact read-only authority required')
        prepared = prepare(args.manifest, args.sha256, args.pid, args.authorized_host, args.authorized_bundle)
        if not args.execute: print('PASS: preparation only; no request published'); return
        result, archive = supervise(*prepared, authorized=True)
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, json.JSONDecodeError) as e:
        parser.exit(2, 'BLOCKED: ' + str(e) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True)); print('Report: ' + str(archive))
    print('Report SHA-256: ' + common.sha(archive)); raise SystemExit(0 if result['status'] == 'PASS' else 1)

if __name__ == '__main__': main()
