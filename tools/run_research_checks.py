#!/usr/bin/env python3
"""One offline research run, one private ZIP. Never a live-AE/release gate.

Runs fixed, existing repository checks in order. No installation, dependency
installation, Adobe library loading, AE attachment, scripting or scan is added.
Only child test process groups created here may be stopped on timeout.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import selectors
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time
import unittest
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[1]
MAX_LOG = 8 * 1024 * 1024


class Blocked(RuntimeError):
    pass


def write_json(path, value):
    with path.open('x', encoding='utf-8') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True)
        stream.write('\n')
    path.chmod(0o600)


def source_identity(root, expected=None):
    """Pin actual tracked bytes as well as Git; do not clean, stash or checkout."""
    def git(*args):
        result = subprocess.run(['git', '-c', 'core.fsmonitor=false', *args], cwd=root,
                                stdin=subprocess.DEVNULL, capture_output=True, timeout=15,
                                env=dict(os.environ, GIT_OPTIONAL_LOCKS='0'), check=False)
        if result.returncode:
            raise Blocked('Git source identity unavailable')
        return result.stdout
    if Path(os.fsdecode(git('rev-parse', '--show-toplevel')).strip()).resolve() != root:
        raise Blocked('Run from the repository root, not an unrelated parent checkout')
    commit = git('rev-parse', 'HEAD').decode().strip()
    if not re.fullmatch(r'[0-9a-f]{40}', commit) or (expected and commit != expected):
        raise Blocked('Source commit differs from the expected commit')
    if git('status', '--porcelain=v1', '--untracked-files=all'):
        raise Blocked('Source must be clean; no files were removed or reset')
    entries = git('ls-tree', '-r', '-z', '--full-tree', 'HEAD').split(b'\0')
    hashes = {}
    for entry in filter(None, entries):
        metadata, raw = entry.split(b'\t', 1)
        mode, kind, object_id = metadata.split()
        if kind != b'blob' or mode not in (b'100644', b'100755'):
            raise Blocked('Unsupported tracked source kind')
        relative = Path(os.fsdecode(raw))
        path = root / relative
        if relative.is_absolute() or '..' in relative.parts or path.is_symlink():
            raise Blocked('Unsupported tracked path')
        if not stat.S_ISREG(path.stat().st_mode):
            raise Blocked('Tracked source is not a regular file')
        data = path.read_bytes()
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if blob != object_id.decode():
            raise Blocked('Tracked bytes differ from HEAD, including hidden index changes')
        hashes[relative.as_posix()] = hashlib.sha256(data).hexdigest()
    if not hashes:
        raise Blocked('Empty source inventory')
    payload = json.dumps(hashes, sort_keys=True, separators=(',', ':')).encode()
    return {'commit': commit, 'tracked_sha256': hashes,
            'inventory_sha256': hashlib.sha256(payload).hexdigest(), 'clean': True}


def run_command(argv, root, log, timeout=120, limit=MAX_LOG):
    """Bound time/output; terminate only this newly created test process group."""
    started = time.monotonic()
    result = {'status': 'FAIL', 'returncode': None, 'log': 'logs/' + log.name}
    proc = None
    try:
        with log.open('xb') as output, selectors.DefaultSelector() as selector:
            proc = subprocess.Popen(argv, cwd=root, stdin=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                    start_new_session=True,
                                    env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1',
                                             PYTHONUNBUFFERED='1', LC_ALL='C'))
            selector.register(proc.stdout, selectors.EVENT_READ)
            size = 0
            while selector.get_map():
                remaining = timeout - (time.monotonic() - started)
                if remaining <= 0:
                    raise TimeoutError('Test time limit exceeded')
                for key, _ in selector.select(min(remaining, 0.1)):
                    data = os.read(key.fd, 65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    output.write(data[:max(0, limit - size)])
                    size += len(data)
                    if size > limit:
                        raise RuntimeError('Test output limit exceeded; log truncated')
            code = proc.wait(timeout=max(0.01, timeout - (time.monotonic() - started)))
            result.update(returncode=code, status='PASS' if code == 0 else 'FAIL')
    except FileNotFoundError:
        result.update(status='BLOCKED', reason='Required local tool not found')
    except (TimeoutError, subprocess.TimeoutExpired):
        result['reason'] = 'Test time limit exceeded; no retry'
    except KeyboardInterrupt:
        result['reason'] = 'Interrupted; no retry'
    except (OSError, RuntimeError):
        result['reason'] = 'Test process or bounded log failed; partial evidence retained'
    finally:
        if proc is not None:
            try:
                if result['status'] != 'PASS' or proc.poll() is None:
                    # The group may outlive its direct child while holding our pipe.
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    except PermissionError:
                        # macOS can deny signalling after the direct child exits.
                        # Keep the existing FAIL; never ignore denial for a live child.
                        if proc.poll() is None:
                            raise
                    proc.wait(timeout=5)
            finally:
                if proc.stdout is not None:
                    proc.stdout.close()
        result['seconds'] = round(time.monotonic() - started, 3)
    return result


def python_worker(root, destination):
    """Machine-readable counts; a nested native suite remains ONE Python test."""
    suite = unittest.TestLoader().discover(str(root / 'tests'), pattern='test_*.py')
    result = unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
    good = result.wasSuccessful() and result.testsRun > 0 and not result.expectedFailures
    write_json(destination, {'status': 'PASS' if good else 'FAIL',
                             'tests_run': result.testsRun,
                             'failures': len(result.failures), 'errors': len(result.errors),
                             'skipped': [{'test': case.id(), 'reason': why} for case, why in result.skipped],
                             'expected_failures': len(result.expectedFailures),
                             'unexpected_successes': len(result.unexpectedSuccesses),
                             'nested_native_cases_not_added_to_python_count': True})
    return 0 if good else 1


def stages(root, work, system):
    python = sys.executable
    plan = [
        ('node-version', ['node', '--version']),
        ('compiler-version', ['clang++', '--version']),
        ('shell-metadata', [python, 'tools/verify_shell_metadata.py', 'core/build.rs', 'wrapper/AEHotLoader.cpp']),
        ('shell-contract', [python, 'tools/verify_shell_contract.py', 'core/build.rs', 'core/src/lib.rs',
                            'wrapper/AEHotLoader.cpp', 'agent/native/ShellReloader.cpp']),
        ('python', [python, str(root / 'tools/run_research_checks.py'), '--python-worker', str(work / 'python.json')]),
        ('node-panel', ['node', '--test', 'tests/panel.test.cjs']),
        ('node-snapshot', ['node', '--test', 'tests/scoped-snapshot.test.cjs']),
    ]
    if system == 'darwin':
        for index, source in enumerate(('wrapper/AEHotLoader.cpp', 'agent/native/ShellReloader.cpp',
                                        'agent/native/InternalLoader.cpp')):
            plan.append(('native-syntax-' + str(index + 1), ['/usr/bin/xcrun', 'clang++', '-std=c++17',
                         '-arch', 'arm64', '-Wall', '-Wextra', '-Wpedantic', '-Werror', '-fsyntax-only', source]))
        scripts = sorted(root.glob('*.command')) + sorted((root / 'experiments/host_preflight').glob('*.command'))
        for index, script in enumerate(scripts):
            plan.append(('script-syntax-' + str(index + 1), ['/bin/zsh', '-n', str(script)]))
        binary = work / 'scoped-guards'
        plan += [('scoped-guard-build', ['/usr/bin/xcrun', 'clang++', '-std=c++17', '-arch', 'arm64',
                                       '-Wall', '-Wextra', '-Werror', 'tests/scoped_discovery_gate.cpp', '-o', str(binary)]),
                 ('scoped-guard-run', [str(binary)])]
    return plan


def package_report(folder, record):
    """Package logs/summary only, never test binaries or original Adobe inputs."""
    write_json(folder / 'report.json', record)
    text = ('AE HOT LOADER: OFFLINE RESEARCH CHECKS\n'
            'Offline result: ' + record['offline_status'] + '\n'
            'Full pipeline: BLOCKED (no-scan AEGP/live host gate not executed)\n'
            'No AE operation was requested by this runner.\n'
            'Product build/sign/package: NOT RUN by this runner; separate macOS CI.\n'
            'Historical results are not rerun or relabelled by this report.\n\n')
    if record.get('reason'):
        text += 'Reason: ' + record['reason'] + '\n'
    text += ''.join(step['name'] + ': ' + step['status'] + '\n' for step in record['steps'])
    (folder / 'SUMMARY.txt').write_text(text, encoding='utf-8')
    files = [folder / 'report.json', folder / 'SUMMARY.txt', *sorted((folder / 'logs').glob('*'))]
    manifest = {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    write_json(folder / 'manifest.json', manifest)
    archive = folder.with_suffix('.zip')
    with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as output:
        for path in [*files, folder / 'manifest.json']:
            path.chmod(0o600)
            output.write(path, path.relative_to(folder).as_posix())
    archive.chmod(0o600)
    with zipfile.ZipFile(archive) as check:
        if check.testzip() or set(check.namelist()) != set(manifest) | {'manifest.json'}:
            raise RuntimeError('Report archive integrity check failed')
        if any(hashlib.sha256(check.read(name)).hexdigest() != value for name, value in manifest.items()):
            raise RuntimeError('Report archive hash check failed')
    return archive


def run(root, parent, expected=None):
    root, parent = root.resolve(strict=True), parent.resolve(strict=True)
    if not parent.is_dir():
        raise Blocked('Output parent must already exist')
    if parent == root or root in parent.parents:
        raise Blocked('Output must be outside the source checkout')
    folder = Path(tempfile.mkdtemp(prefix='AEHL-checks-', dir=parent))
    (folder / 'logs').mkdir(mode=0o700)
    (folder / 'work').mkdir(mode=0o700)
    record = {'schema': 'AEHL-OFFLINE-RUN-1', 'run_id': uuid.uuid4().hex,
              'scope': 'offline-research-checks-only', 'offline_status': 'BLOCKED',
              'full_pipeline_status': 'BLOCKED', 'live_ae_operations_requested': False,
              'product_package_status': 'NOT RUN', 'macos_native_status': 'NOT RUN',
              'platform': platform.platform(),
              'python_version': platform.python_version(), 'steps': [],
              'unavailable_gates': ['no-scan AEGP SDK build/live host gate', 'fresh AE baseline',
                                    'late registration', 'apply/render', 'repeat/lifecycle',
                                    'release acceptance']}
    plan = []
    try:
        if os.name != 'posix' or sys.platform not in ('linux', 'darwin'):
            raise Blocked('This offline runner supports Linux and macOS only')
        if sys.platform == 'darwin' and platform.machine() != 'arm64':
            raise Blocked('The macOS native checks require arm64')
        identity = source_identity(root, expected)
        record['source'] = identity
        for tool in ('node', 'clang', 'clang++'):
            if not shutil.which(tool):
                raise Blocked('Required tool unavailable: ' + tool)
        plan = stages(root, folder / 'work', sys.platform)
        record['steps'] = [{'name': name, 'status': 'NOT RUN'} for name, _ in plan]
        for index, (name, command) in enumerate(plan):
            if source_identity(root, expected) != identity:
                raise Blocked('Source changed; remaining stages stopped')
            print('CHECK ' + name, flush=True)
            result = run_command(command, root, folder / 'logs' / (name + '.log'))
            record['steps'][index].update(result)
            if name == 'python' and result['status'] == 'PASS':
                try:
                    counts = json.loads((folder / 'work/python.json').read_text())
                    if (counts['status'] != 'PASS' or type(counts['tests_run']) is not int or
                            counts['tests_run'] < 1 or not isinstance(counts['skipped'], list)):
                        raise ValueError('Invalid worker result')
                    record['python_tests'] = counts
                except (OSError, ValueError, TypeError, KeyError):
                    record['steps'][index].update(status='FAIL', reason='Python evidence missing/invalid')
                    raise RuntimeError('Python worker evidence invalid')
                # No platform-specific tests may silently skip on the target Mac.
                if sys.platform == 'darwin' and counts['skipped']:
                    record['steps'][index].update(status='FAIL', reason='Unexpected macOS skips')
            if record['steps'][index]['status'] != 'PASS':
                record['offline_status'] = record['steps'][index]['status']
                break
        else:
            record['offline_status'] = 'PASS'
            if sys.platform == 'darwin':
                record['macos_native_status'] = 'PASS'
        if source_identity(root, expected) != identity:
            raise Blocked('Source changed; results cannot identify one candidate')
        record['source_unchanged_after'] = True
    except Blocked as error:
        record.update(offline_status='BLOCKED', reason=str(error))
    except KeyboardInterrupt:
        record.update(offline_status='FAIL', reason='Interrupted; no retry')
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError, KeyError):
        record.update(offline_status='FAIL', reason='Runner/evidence failure; remaining stages stopped')
    archive = package_report(folder, record)
    print(record['offline_status'] + ': offline only. Full AE pipeline: BLOCKED.\nReport: ' + str(archive))
    return (0 if record['offline_status'] == 'PASS' else 2), archive


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-parent', type=Path, default=Path(tempfile.gettempdir()))
    parser.add_argument('--expected-commit')
    parser.add_argument('--python-worker', type=Path, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.python_worker:
        return python_worker(ROOT, args.python_worker)
    if args.expected_commit and not re.fullmatch(r'[0-9a-f]{40}', args.expected_commit):
        parser.error('--expected-commit requires a full lowercase Git SHA')
    try:
        return run(ROOT, args.output_parent, args.expected_commit)[0]
    except (Blocked, OSError, RuntimeError, zipfile.BadZipFile):
        print('BLOCKED: report could not be finalized; no complete ZIP is claimed.', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
