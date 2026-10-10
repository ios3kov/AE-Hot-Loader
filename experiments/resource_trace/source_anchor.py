"""Owned cross-process file-identity control. Does not launch/read Adobe code."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import uuid

ROOT = Path(__file__).resolve().parents[2]


def run(output, sanitizers=False):
    runner_before = Path(__file__).read_bytes()
    if type(sanitizers) is not bool:
        raise ValueError('invalid instrumentation choice')
    if platform.system() != 'Darwin' or platform.machine() != 'arm64':
        raise ValueError('source anchor control requires macOS arm64')
    output = Path(output).resolve()
    output.mkdir(mode=0o700, parents=True, exist_ok=False)
    source = Path(__file__).with_suffix('.cpp')
    before = source.read_bytes()
    binary = output / 'aehl-source-anchor'
    command = ['clang++', '-std=c++17', '-arch', 'arm64', '-Wall', '-Wextra', '-Werror',
               str(source), '-o', str(binary)]
    instrument = ['-fsanitize=address,undefined', '-fno-omit-frame-pointer'] if sanitizers else []
    command += instrument
    subprocess.run(command, check=True, timeout=60, capture_output=True)
    if source.read_bytes() != before:
        raise ValueError('source changed during build')
    payload = b'eMNA:AEHLR' + uuid.uuid4().hex[:12].encode() + b'\0'
    rows = []
    for mode, reason in [('none', 'NONE'), ('replace-fd', 'SOURCE_FILE_CHANGED'),
                         ('mutate-file', 'SOURCE_CONTENT_CHANGED')]:
        case = output / mode
        case.mkdir(mode=0o700)
        a, b = case / 'A.resource', case / 'B.resource'
        for path in (a, b):
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW, 0o600)
            with os.fdopen(fd, 'wb') as stream:
                stream.write(payload)
        child = subprocess.Popen([str(binary), str(a), str(b), mode], stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE)
        try:
            stdout, stderr = child.communicate(timeout=35)
        except subprocess.TimeoutExpired as error:
            # Do not implicitly kill even this owned fixture on an unexpected hang.
            (case / 'attention.json').write_text(json.dumps({'pid': child.pid, 'status': 'ATTENTION'}))
            raise ValueError('owned anchor retained; review attention receipt') from error
        (case / 'stdout.log').write_bytes(stdout)
        (case / 'stderr.log').write_bytes(stderr)
        if child.returncode != 0:
            raise ValueError(f'anchor {mode} failed: {stderr.decode(errors="replace")}')
        row = json.loads(stdout)
        if not (row['reason'] == reason and row['status'] == ('OWNED_SOURCE_OBSERVED' if mode == 'none' else 'REFUSED')
                and row['payload_reads'] == (1 if mode == 'none' else 0) and row['child_reaped'] is True
                and row['kernel_queries'] == 2 and row['AE_admission'] == 'BLOCKED'):
            raise ValueError('intended source control not observed')
        same = (row['initial_device'], row['initial_inode']) == (row['current_device'], row['current_inode'])
        if same != (mode != 'replace-fd'):
            raise ValueError('kernel file identity discriminator differs')
        rows.append({'mode': mode, 'result': row})
    ref_source = source.with_name('fsref_anchor.cpp')
    ref_before = ref_source.read_bytes()
    ref_binary = output / 'aehl-fsref-anchor'
    ref_command = ['clang++', '-std=c++17', '-arch', 'arm64', '-Wall', '-Wextra', '-Werror',
                   str(ref_source), '-framework', 'CoreFoundation', '-framework', 'CoreServices',
                   '-o', str(ref_binary)]
    ref_command += instrument
    subprocess.run(ref_command, check=True, timeout=60, capture_output=True)
    ref_child = subprocess.Popen([str(ref_binary), str(output/'none/A.resource'), str(output/'none/B.resource')],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        ref_out, ref_error = ref_child.communicate(timeout=10)
    except subprocess.TimeoutExpired as error:
        (output / 'fsref-attention.json').write_text(json.dumps({'pid': ref_child.pid, 'status': 'ATTENTION'}))
        raise ValueError('owned filesystem-reference control retained') from error
    (output / 'fsref-stdout.log').write_bytes(ref_out)
    (output / 'fsref-stderr.log').write_bytes(ref_error)
    if ref_child.returncode != 0:
        raise ValueError('filesystem-reference runtime failed: ' + ref_error.decode(errors='replace'))
    ref_result = json.loads(ref_out)
    if ref_result != {'status': 'OWNED_FSREF_OBSERVED', 'fsref_bytes': 80, 'fork_ref_bytes': 4,
                      'actual_count_bytes': 8, 'copied_ref_equal': True,
                      'same_bytes_file_twin_equal': False, 'AE_admission': 'BLOCKED'}:
        raise ValueError('intended filesystem-reference control not observed')
    if source.read_bytes() != before:
        raise ValueError('source changed during control')
    if ref_source.read_bytes() != ref_before:
        raise ValueError('filesystem-reference source changed during control')
    receipt = {'scope': 'OWNED_COOPERATIVE_CHILD_ONLY', 'source_sha256': hashlib.sha256(before).hexdigest(),
               'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'dirty': bool(subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT)),
               'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
               'payload_sha256': hashlib.sha256(payload).hexdigest(), 'command': command,
               'controls': rows, 'AE_run': 'NOT_RUN', 'Adobe_buffer_lifetime': 'UNKNOWN'}
    receipt['filesystem_ref'] = {'result': ref_result, 'command': ref_command,
                                'source_sha256': hashlib.sha256(ref_before).hexdigest(),
                                'binary_sha256': hashlib.sha256(ref_binary.read_bytes()).hexdigest()}
    if Path(__file__).read_bytes() != runner_before:
        raise ValueError('runner changed during control')
    receipt['runner_sha256'] = hashlib.sha256(runner_before).hexdigest()
    receipt['sanitizers'] = ['ASan', 'UBSan'] if sanitizers else []
    (output / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('output')
    parser.add_argument('--sanitizers', action='store_true')
    args = parser.parse_args()
    print(json.dumps(run(args.output, args.sanitizers), indent=2))
