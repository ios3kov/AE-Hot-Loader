"""Explicit owned LLDB fixture runner. No Adobe target or automatic kill."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import platform
import shlex
import subprocess
import sys
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from experiments.resource_trace.core import need
from experiments.resource_trace.transport_profile import hashes, clean_source, read_profile
from experiments.startup_trace.image import Image
from experiments.startup_trace.lldb_collector import write_once


def build(origin='bundle-resource', fault='none', bad_extent=False):
    need(platform.system() == 'Darwin' and platform.machine() == 'arm64', 'owned debugger fixture needs macOS arm64')
    need(origin in ('bundle-resource', 'legacy-resource', 'cache') and
         fault in ('none', 'alias', 'writer-failure', 'wrong-owner', 'read-name', 'cross-reader', 'aba') and
         type(bad_extent) is bool, 'fixture variant')
    source = clean_source(); before = hashes(); run = uuid.uuid4().hex
    directory = ROOT/'build-ae-hot-loader'/('resource-debug-' + run)
    directory.mkdir(mode=0o700)
    binary = directory/'aehl-resource-transport'
    command = ['clang++', '-std=c++17', '-arch', 'arm64', '-O0', '-Wall', '-Wextra', '-Werror',
               '-DAEHL_RESOURCE_DEBUGGER', *(['-DAEHL_RESOURCE_BAD_EXTENT'] if bad_extent else []),
               str(Path(__file__).with_name('fixture.cpp')), '-o', str(binary)]
    subprocess.run(command, check=True, timeout=60)
    need(before == hashes() and source == clean_source(), 'source changed during build')
    image = Image(binary); name = 'AEHLR' + run[:12]
    resource = directory/'input.resource'; payload = b'eMNA:' + name.encode() + b'\0'
    with resource.open('xb') as out: out.write(payload)
    resource.chmod(0o600)
    record = {'schema': 1, 'kind': 'owned-resource-transport', 'source_commit': source,
              'sources': before, 'image': {'path': str(binary), 'sha256': image.sha256, 'uuid': image.uuid},
              'site': {'offset': image.symbol('_resource_probe_site'), 'word': '1f2003d5'},
              'run_id': run, 'match_name': name, 'resource': str(resource),
              'payload_sha256': hashlib.sha256(payload).hexdigest(), 'origin': origin, 'fault': fault}
    profile = directory/'profile.json'; write_once(profile, record)
    write_once(directory/'build.json', {'source_commit': source, 'sources': before, 'command': command,
                                      'binary_sha256': image.sha256, 'bad_extent': bad_extent})
    digest = hashlib.sha256(profile.read_bytes()).hexdigest(); read_profile(profile, digest)
    return profile, digest


def drive(profile, digest):
    record = read_profile(profile, digest)
    output = Path(profile).parent/'capture'; output.mkdir(mode=0o700)
    console = output.with_name('debugger.log')
    fd = os.open(console, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as log:
        child = subprocess.Popen(['lldb', '--no-lldbinit'], stdin=subprocess.PIPE, stdout=log, stderr=log,
                                 env={k: v for k, v in os.environ.items() if not k.startswith('AEHL_')})
        commands = ['command script import ' + shlex.quote(str(Path(__file__).with_name('transport.py'))),
                    'aehl-resource-fixture ' + ' '.join(shlex.quote(str(x)) for x in (profile, digest, output))]
        child.stdin.write(('\n'.join(commands) + '\n').encode()); child.stdin.flush()
        started = time.monotonic(); attention = False
        while not (output/'result.json').exists():
            if console.stat().st_size > 1048576 and not (output/'cancel').exists():
                write_once(output/'cancel', {'reason': 'debugger console byte budget'})
            code = child.poll()
            if code is not None:
                failure = {'status': 'DEBUGGER_EXITED_WITHOUT_RESULT', 'cleanup_safe': False,
                           'debugger_exit_code': code, 'detach': 'UNKNOWN', 'source_commit': record['source_commit']}
                write_once(output/'launcher-failure.json', failure); child.stdin.close(); return failure
            if time.monotonic() - started > 90 and not attention:
                write_once(output/'attention.json', {'debugger_pid': child.pid, 'status': 'MANUAL_ATTENTION',
                                                    'reason': 'No final collector receipt; process and debugger retained'})
                print('MANUAL_ATTENTION: debugger retained', flush=True); attention = True
            time.sleep(0.2)
        result = json.loads((output/'result.json').read_text())
        if result.get('cleanup_safe') is not True:
            print('MANUAL_ATTENTION: detach not proven; debugger retained', flush=True)
            while child.poll() is None: time.sleep(1)
            raise ValueError('manual debugger attention; no cleanup certification')
        child.stdin.write(b'quit\n'); child.stdin.flush()
        while child.poll() is None: time.sleep(0.2)
        child.stdin.close()
    # Independent PID existence check after detach; no action against that PID.
    owned = result.get('owned_process')
    if owned:
        deadline = time.monotonic() + 10
        while True:
            # Signal zero queries existence; it does not deliver a signal or quit.
            # A reused PID conservatively blocks absence rather than being touched.
            try: os.kill(owned['pid'], 0)
            except ProcessLookupError: break
            except PermissionError: raise ValueError('process absence query unavailable')
            need(time.monotonic() < deadline, 'owned fixture remains; preserve it')
            time.sleep(0.1)
        result['process_absence'] = 'PASS'
    result['debugger_exit_code'] = child.returncode
    read_profile(profile, digest)
    write_once(output/'supervisor.json', result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--origin', choices=('bundle-resource', 'legacy-resource', 'cache'), default='bundle-resource')
    parser.add_argument('--fault', choices=('none', 'alias', 'writer-failure', 'wrong-owner', 'read-name', 'cross-reader', 'aba'), default='none')
    parser.add_argument('--bad-extent', action='store_true')
    args = parser.parse_args(); profile, digest = build(args.origin, args.fault, args.bad_extent)
    print(json.dumps({'profile': str(profile), 'sha256': digest}), flush=True)
    result = drive(profile, digest)
    print(json.dumps({k: result.get(k) for k in ('status', 'cleanup_safe', 'process_absence', 'reason')}), flush=True)
    need(result.get('cleanup_safe') is True and result.get('process_absence') == 'PASS' and
         result.get('debugger_exit_code') == 0, 'fixture lifecycle not verified')
    expected = 'REFUSED_OR_INCOMPLETE' if args.fault != 'none' or args.bad_extent else 'OWNED_RESOURCE_TRANSPORT_OBSERVED'
    need(result['status'] == expected, 'control outcome differs')
