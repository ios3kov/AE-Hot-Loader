"""Build one inert no-scan AEGP candidate. Never installs, launches or contacts AE."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import plistlib
import subprocess
import uuid

EXPECTED_HOST = Path('/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/MacOS/After Effects')


def run(*command):
    return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT, timeout=120)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cpp(value):
    return json.dumps(str(value), ensure_ascii=True)


def canonical_existing(path, kind):
    if not path.is_absolute() or path.resolve() != path or not path.exists():
        raise ValueError(kind + ' must be an existing absolute canonical path')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--authorized-host', type=Path,
                        help='explicitly authorized AE executable; does not grant live-call approval')
    parser.add_argument('--authorized-plugin-root', type=Path,
                        help='expected install root; this builder does not copy into it')
    args = parser.parse_args()
    if bool(args.authorized_host) != bool(args.authorized_plugin_root):
        parser.error('authorized host and plugin root must be supplied together')
    repo = Path(__file__).resolve().parents[2]
    if run('git', '-C', str(repo), 'status', '--porcelain'):
        parser.error('clean source tree required for identified research build')
    commit = run('git', '-C', str(repo), 'rev-parse', 'HEAD').strip()
    sdk = args.sdk.resolve()
    for name in ('Headers/AE_GeneralPlug.h', 'Resources/AE_General.r'):
        if not (sdk / name).is_file():
            parser.error('SDK missing ' + name)
    build_id = 'noscan-' + uuid.uuid4().hex[:12]
    run_id = 'directory-probe-' + uuid.uuid4().hex
    output = repo / 'build-ae-hot-loader' / build_id
    output.mkdir(mode=0o700)
    control = output / 'control'; journal = output / 'journal'; probe = output / 'probe-directory'
    for path in (control, journal, probe): path.mkdir(mode=0o700)
    stem = 'AEHLNoScan' + build_id.removeprefix('noscan-')
    candidate = output / (stem + '.plugin')
    if args.authorized_host:
        host = canonical_existing(args.authorized_host, 'authorized host')
        plugin_root = canonical_existing(args.authorized_plugin_root, 'authorized plugin root')
        if not host.is_file() or not plugin_root.is_dir():
            parser.error('invalid authorized host or plugin root')
        if host != EXPECTED_HOST:
            parser.error('authorized host must match the reviewed AE 25.6 location')
        installed_bundle = plugin_root / candidate.name
        if installed_bundle.exists():
            parser.error('installation destination already exists; builder will not overwrite it')
        expected_module = installed_bundle / 'Contents/MacOS' / stem
        host_mode = 'authorized-user-host'
    else:
        host = output / 'host/Adobe After Effects 2025.app/Contents/MacOS/After Effects'
        installed_bundle = output / 'host-plugins' / candidate.name
        expected_module = installed_bundle / 'Contents/MacOS' / stem
        host_mode = 'owned-isolated-host-not-created'
    for value, label in ((probe, 'probe directory'), (control, 'control directory'),
                         (journal, 'journal directory')):
        try: str(value).encode('ascii')
        except UnicodeEncodeError: parser.error(label + ' must be ASCII for this reviewed contract')
    token = uuid.uuid4().hex
    plan = [run_id, commit, build_id, str(host), str(expected_module), str(probe), 15000]
    config = output / 'NoScanDirectoryConfig.hpp'
    config.write_text(
        '#pragma once\nstatic const no_scan_directory::Config research_config {\n    {' +
        ', '.join(cpp(v) if not isinstance(v, int) else str(v) for v in plan) + '},\n    ' +
        ', '.join(cpp(v) for v in (token, control, journal)) + '\n};\n' +
        'static constexpr const char* research_identity = ' + cpp(json.dumps({
            'build_id': build_id, 'source_commit': commit, 'source_clean': True,
            'target': 'aarch64-apple-darwin', 'kind': 'research-only-no-scan-directory-aegp',
            'run_id': run_id,
        }, sort_keys=True)) + ';\n', encoding='utf-8')
    contents = candidate / 'Contents'
    (contents / 'MacOS').mkdir(parents=True)
    (contents / 'Resources').mkdir()
    (contents / 'Info.plist').write_bytes(plistlib.dumps({
        'CFBundleExecutable': stem, 'CFBundleName': stem,
        'CFBundleIdentifier': 'com.os3kov.AEHotLoader.NoScan.' + build_id,
        'CFBundlePackageType': 'AEgx', 'CFBundleSignature': 'FXTC',
        'CFBundleVersion': '1', 'LSRequiresCarbon': True,
    }))
    resource = output / 'NoScanDirectoryProbe.r'
    resource.write_text('#include "AE_General.r"\nresource \'PiPL\' (16000) {{\n'
                        'Kind { AEGP }, Name { "' + stem + '" },\n'
                        'Category { "General Plugin" }, CodeMacARM64 { "EntryPointFunc" }\n}};\n')
    run('Rez', '-useDF', '-i', str(sdk / 'Resources'), str(resource), '-o',
        str(contents / 'Resources' / (stem + '.rsrc')))
    binary = contents / 'MacOS' / stem
    common = ['clang++', '-std=c++17', '-arch', 'arm64', '-Wall', '-Wextra', '-Wpedantic', '-Werror']
    command = common + ['-bundle', '-fvisibility=hidden', '-I' + str(output),
        '-Wl,-exported_symbol,_EntryPointFunc,-exported_symbol,_AEHL_NoScanBuildIdentity',
        '-I' + str(sdk / 'Headers'), '-I' + str(sdk / 'Headers/SP'),
        str(Path(__file__).with_name('NoScanDirectoryProbe.cpp')),
        str(Path(__file__).with_name('HostIndirectResult_arm64.S')),
        '-framework', 'CoreFoundation', '-o', str(binary)]
    run(*command)
    run('codesign', '--force', '--sign', '-', str(candidate))
    run('codesign', '--verify', '--strict', str(candidate))
    exports = run('nm', '-arch', 'arm64', '-gU', str(binary))
    if {line.split()[-1] for line in exports.splitlines()} != {
            '_AEHL_NoScanBuildIdentity', '_EntryPointFunc'}:
        raise ValueError('unexpected exported entrypoints')
    library = ctypes.CDLL(str(binary))
    getter = library.AEHL_NoScanBuildIdentity; getter.restype = ctypes.c_char_p
    identity = json.loads(getter().decode())
    if identity != {'build_id': build_id, 'source_commit': commit, 'source_clean': True,
                    'target': 'aarch64-apple-darwin', 'kind': 'research-only-no-scan-directory-aegp',
                    'run_id': run_id}:
        raise ValueError('runtime metadata mismatch')
    inert = output / 'no-scan-inert-tests'
    run(*(common + ['-I' + str(sdk / 'Headers'), '-I' + str(sdk / 'Headers/SP'),
                   str(repo / 'tests/no_scan_directory_inert.cpp'), '-o', str(inert)]))
    inert_result = run(str(inert), str(binary), token)
    if any(control.iterdir()) or any(journal.iterdir()) or any(probe.iterdir()):
        raise ValueError('inert entrypoint produced filesystem side effects')
    record = {
        **identity, 'source_state': '', 'compiler': run('clang++', '--version'),
        'sdk': run('xcrun', '--show-sdk-version').strip(), 'command': command,
        'sdk_general_header_sha256': sha(sdk / 'Headers/AE_GeneralPlug.h'),
        'host_executable': str(host), 'module_path': str(expected_module),
        'host_mode': host_mode, 'authorized_bundle': str(installed_bundle) if args.authorized_host else None,
        'candidate_bundle': str(candidate), 'probe_directory': str(probe),
        'control_directory': str(control), 'journal_directory': str(journal),
        'activation_env': {'AEHL_NOSCAN_GATE_TOKEN': token},
        'provider_profile': {
            'frameworks': '/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app/Contents/Frameworks',
            'FILE_sha256': 'df0db4a31955f1890b9bd6b1bff0f28c753824f63e4736721172e8697326f864',
            'U_sha256': 'aecabb33c5ac5948ad742848c46588398bc690411b70aae7ca3f08a919362daa',
            'dvacore_sha256': 'cb6faaf5b745903b80b44105b658ab68186d5065ae47c8a57c9b23e26aa8ecb0',
        },
        'checks': {'build_sign_exports': 'PASS', 'identity_getter': 'PASS',
                   'inert_entrypoint': 'PASS', 'live_ae': 'NOT RUN',
                   'private_file_call': 'NOT RUN', 'provider_retention': 'NOT RUN'},
        'inert_entrypoint_output': inert_result,
        'files': {str(p.relative_to(candidate)): sha(p) for p in sorted(candidate.rglob('*')) if p.is_file()},
        'installation_performed': False, 'ae_launch_performed': False,
    }
    manifest = output / 'manifest.json'
    manifest.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n')
    os.chmod(manifest, 0o600)
    print(output)
    print('manifest_sha256=' + sha(manifest))
    print(inert_result.strip())


if __name__ == '__main__':
    main()
