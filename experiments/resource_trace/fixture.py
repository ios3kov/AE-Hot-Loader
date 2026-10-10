"""Build/run only our self-terminating resource-chain fixture; never AE/LLDB."""
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

from experiments.resource_trace.core import ORIGINS, Trace, need

ROOT = Path(__file__).resolve().parents[2]
_built = {}


def source_hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in (Path(__file__), Path(__file__).with_name('core.py'), Path(__file__).with_name('fixture.cpp'))}


def build(directory):
    directory = Path(directory)
    need(directory.is_absolute() and directory.is_dir() and
         not any(p.is_symlink() for p in (directory, *directory.parents)), 'owned fixture directory')
    target = directory / 'aehl-resource-fixture'
    need(not target.exists(), 'fixture binary already exists')
    sources = source_hashes()
    subprocess.run(['clang++', '-std=c++17', '-O0', '-Wall', '-Wextra', '-Werror',
                    str(Path(__file__).with_name('fixture.cpp')), '-o', str(target)], check=True, timeout=60)
    need(source_hashes() == sources, 'fixture sources changed during build')
    _built[str(target)] = {'binary': hashlib.sha256(target.read_bytes()).hexdigest(), 'sources': sources}
    return target


def run(target, directory, origin='bundle-resource', fault='none'):
    target, directory = Path(target), Path(directory)
    need(target.name == 'aehl-resource-fixture' and target.parent == directory and
         target.is_file() and not any(p.is_symlink() for p in (target, *target.parents)), 'fixture executable identity')
    need(str(target) in _built and
         hashlib.sha256(target.read_bytes()).hexdigest() == _built[str(target)]['binary'] and
         source_hashes() == _built[str(target)]['sources'], 'fixture was not built here or has changed')
    need(origin in ORIGINS and fault in ('none', 'alias', 'writer-failure', 'wrong-owner', 'read-name'), 'fixture variant')
    run_id = uuid.uuid4().hex
    name = 'AEHLR' + run_id[:12]
    payload = b'eMNA:' + name.encode('ascii') + b'\0'
    resource = directory / (run_id + '.resource')
    with resource.open('xb') as output:
        output.write(payload)
    resource.chmod(0o600)
    sources = source_hashes()
    module_sha = hashlib.sha256(target.read_bytes()).hexdigest()
    process = subprocess.Popen([str(target), str(resource), run_id, module_sha, origin, fault],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        output, errors = process.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        # Retain PID and executable rather than silently killing an uncertain process.
        pending = {'status': 'MANUAL_ATTENTION', 'pid': process.pid, 'executable': str(target), 'run_id': run_id}
        (directory / (run_id + '-pending.json')).write_text(json.dumps(pending, indent=2) + '\n')
        raise
    need(process.returncode == 0 and not errors, 'fixture did not exit cleanly')
    need(len(output) <= 16384 and len(output.splitlines()) == 10, 'fixture output bounds')
    need(hashlib.sha256(target.read_bytes()).hexdigest() == module_sha and source_hashes() == sources and
         resource.read_bytes() == payload, 'fixture inputs changed')
    profile = {'schema': 'AEHL-RESOURCE-FIXTURE-1', 'kind': 'owned-fixture',
               'run_id': run_id, 'pid': process.pid, 'thread': 1, 'origin': origin,
               'module_sha256': module_sha, 'payload_sha256': hashlib.sha256(payload).hexdigest(), 'match_name': name}
    trace = Trace(profile)
    rows = [json.loads(line) for line in output.splitlines()]
    for row in rows:
        try:
            trace.feed(row)
        except ValueError:
            break
    receipt = {'profile': profile, 'source_sha256': sources, 'binary_sha256': module_sha,
               'exit_code': process.returncode, 'process_exited': True, 'debugger': 'NOT_RUN',
               'fault': fault, 'events': rows, 'result': trace.result()}
    path = directory / (run_id + '-result.json')
    with path.open('x') as report:
        json.dump(receipt, report, indent=2); report.write('\n')
    path.chmod(0o600)
    return receipt


if __name__ == '__main__':
    directory = ROOT / 'build-ae-hot-loader' / ('resource-fixture-' + uuid.uuid4().hex)
    directory.mkdir(mode=0o700)
    target = build(directory)
    receipts = [run(target, directory, origin) for origin in ORIGINS]
    receipts += [run(target, directory, fault=fault) for fault in ('alias', 'writer-failure', 'wrong-owner', 'read-name')]
    need(all(r['result']['status'] == 'FIXTURE_CHAIN_OBSERVED' for r in receipts[:3]) and
         all(r['result']['status'] == 'REFUSED' for r in receipts[3:]), 'fixture control expectation failed')
    summary = {'status': 'PASS', 'source_sha256': source_hashes(), 'binary_sha256': receipts[0]['binary_sha256'],
               'controls': [{'origin': r['profile']['origin'], 'fault': r['fault'], 'result': r['result']['status'],
                             'pid': r['profile']['pid'], 'process_exited': r['process_exited']} for r in receipts],
               'scope': 'Owned native model only; no Adobe PiPL parser, debugger, process memory or host operation',
               'AE_transport_admission': 'BLOCKED', 'late_add': 'NOT_RUN'}
    (directory / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (directory / 'summary.json').chmod(0o600)
    print(json.dumps({'status': 'PASS', 'summary': str(directory / 'summary.json')}))
