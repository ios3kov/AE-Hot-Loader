"""Build/run header-only public-API control; never launch AE or load plugins."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import uuid


def run(argv):
    return subprocess.check_output(argv, text=True, stderr=subprocess.STDOUT, timeout=30)


def hashes(folder):
    return {str(p.relative_to(folder)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(folder.rglob('*')) if p.is_file()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    bundle = args.bundle.resolve(strict=True)
    owned = (root / 'build-ae-hot-loader').resolve()
    if not bundle.is_relative_to(owned) or bundle.suffix != '.plugin':
        parser.error('require an existing owned build-ae-hot-loader fixture')
    if any(p.is_symlink() for p in bundle.rglob('*')):
        parser.error('fixture must not contain symlinks')
    before = hashes(bundle)
    run_id = 'endian-control-' + uuid.uuid4().hex
    output = owned / 'evidence' / run_id
    output.mkdir(mode=0o700)
    source = Path(__file__).with_name('resource_endian_control.cpp')
    binary = output / 'probe'
    record = {'run_id': run_id, 'build_id': run_id,
              'commit': run(['git', '-C', str(root), 'rev-parse', 'HEAD']).strip(),
              'source_state': run(['git', '-C', str(root), 'status', '--porcelain']),
              'scope': 'public API header-only, not AE runtime or full PiPL parser',
              'input_files': before, 'compiler': run(['clang++', '--version']),
              'sdk': run(['xcrun', '--show-sdk-version']).strip()}
    command = ['clang++', '-std=c++17', '-arch', 'arm64', '-Wall', '-Wextra',
               '-Werror', '-Wno-deprecated-declarations', str(source),
               '-framework', 'Carbon', '-framework', 'CoreFoundation',
               '-o', str(binary)]
    record['build_command'] = command
    run(command)
    record['binary_sha256'] = hashlib.sha256(binary.read_bytes()).hexdigest()
    record['results'] = {}
    for mode in ('baseline', 'callback', 'baseline'):
        key = mode if mode not in record['results'] else 'baseline_after'
        record['results'][key] = json.loads(run([str(binary), str(bundle), mode]))
    record['input_unchanged'] = before == hashes(bundle)
    record['status'] = 'PASS' if record['input_unchanged'] and all(
        r['status'] == 'PASS' for r in record['results'].values()) else 'FAIL'
    (output / 'record.json').write_text(json.dumps(record, indent=2) + '\n')
    print(json.dumps(record, indent=2))
    print(output)
    return 0 if record['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
