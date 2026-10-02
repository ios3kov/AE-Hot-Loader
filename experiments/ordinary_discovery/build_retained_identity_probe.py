"""Build/sign/hash one inert diagnostic AEGP; never installs, launches or contacts AE."""
import argparse
import ctypes
import json
import os
from pathlib import Path
import plistlib
import uuid

from build_no_scan_directory_probe import run, sha, cpp, canonical_existing, EXPECTED_HOST
from collect_resource_search_abi import INPUTS, profile_agrees, validate_input
from collect_resource_roots import REQUESTS
from mach_o_root_metadata import parse_roots
from run_no_scan_directory_probe import read_trusted_binary

UUIDS = {'MEE': '74a30dbaa08b367bbd9915d6d77e9d52'}
HOST_SHA256 = '464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6'


def reviewed_roots():
    profile_agrees()
    result = {}
    for key in ('MEE',):
        path, digest = INPUTS[key]
        validate_input(path, digest)
        metadata = parse_roots(read_trusted_binary(path), REQUESTS[key])
        if metadata['uuid'] != UUIDS[key]:
            raise ValueError('root UUID differs from static review')
        validate_input(path, digest)
        result[key] = {'path': str(path), 'sha256': digest, 'uuid': UUIDS[key],
                       'root_vm': 0x10fd70,
                       'root_size': 16, 'base_vm': int(metadata['image_base_vm'], 16)}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--authorized-host', type=Path, help='reviewed prospective scope only; no live approval')
    parser.add_argument('--authorized-plugin-root', type=Path, help='prospective install root; no copy performed')
    args = parser.parse_args()
    if bool(args.authorized_host) != bool(args.authorized_plugin_root):
        parser.error('host and plugin root must be supplied together')
    repo = Path(__file__).resolve().parents[2]
    if run('git', '-C', str(repo), 'status', '--porcelain'):
        parser.error('exact clean source required')
    commit = run('git', '-C', str(repo), 'rev-parse', 'HEAD').strip()
    sdk = args.sdk.resolve()
    for name in ('Headers/AE_GeneralPlug.h', 'Resources/AE_General.r'):
        if not (sdk / name).is_file():
            parser.error('SDK missing ' + name)
    if sha(sdk / 'Headers/AE_GeneralPlug.h') != '30d12ec3eb5af1a902c7414053b1be1da0204b226e0b1cdc71272be1e137000c':
        parser.error('SDK header differs from reviewed 25.6 contract')
    sdk_inputs = {str(p.relative_to(sdk)): sha(p) for folder in ('Headers', 'Resources')
                  for p in sorted((sdk / folder).rglob('*')) if p.is_file()}
    providers = reviewed_roots()
    build_id = 'identity-' + uuid.uuid4().hex[:12]
    run_id = 'retained-identity-' + uuid.uuid4().hex
    output = repo / 'build-ae-hot-loader' / build_id
    output.mkdir(parents=True, mode=0o700)
    control, journal = output / 'control', output / 'journal'
    control.mkdir(mode=0o700); journal.mkdir(mode=0o700)
    stem = 'AEHLRetained' + build_id[9:]
    candidate = output / (stem + '.plugin')
    if args.authorized_host:
        host = canonical_existing(args.authorized_host, 'host')
        root = canonical_existing(args.authorized_plugin_root, 'plugin root')
        if host != EXPECTED_HOST or not host.is_file() or not root.is_dir():
            parser.error('scope must use reviewed AE 25.6 host and existing root')
        installed = root / candidate.name
        if installed.exists():
            parser.error('prospective destination exists')
        mode = 'authorized-user-host'
    else:
        host = output / 'host/Adobe After Effects 2025.app/Contents/MacOS/After Effects'
        installed = output / 'host-plugins' / candidate.name
        mode = 'owned-isolated-host-not-created'
    module = installed / 'Contents/MacOS' / stem
    identity = {'build_id': build_id, 'source_commit': commit, 'source_clean': True,
                'target': 'aarch64-apple-darwin', 'kind': 'research-only-retained-identity-aegp', 'run_id': run_id}
    token = uuid.uuid4().hex
    values = [run_id, commit, build_id, host, module, journal, control, token]
    config = output / 'RetainedIdentityConfig.hpp'
    config.write_text('#pragma once\nstatic const retained_probe::Config research_config {\n    ' +
        ', '.join(cpp(v) for v in values) + '\n};\n' +
        'static constexpr const char* research_identity = ' + cpp(json.dumps(identity, sort_keys=True)) + ';\n')
    os.chmod(config, 0o600)
    contents = candidate / 'Contents'
    (contents / 'MacOS').mkdir(parents=True); (contents / 'Resources').mkdir()
    (contents / 'Info.plist').write_bytes(plistlib.dumps({
        'CFBundleExecutable': stem, 'CFBundleName': stem,
        'CFBundleIdentifier': 'com.os3kov.AEHotLoader.Retained.' + build_id,
        'CFBundlePackageType': 'AEgx', 'CFBundleSignature': 'FXTC', 'CFBundleVersion': '1', 'LSRequiresCarbon': True}))
    resource = output / 'RetainedIdentityProbe.r'
    resource.write_text('#include "AE_General.r"\nresource \'PiPL\' (16000) {{\n'
                        'Kind { AEGP }, Name { "' + stem + '" }, Category { "General Plugin" },\n'
                        'CodeMacARM64 { "EntryPointFunc" }\n}};\n')
    run('Rez', '-useDF', '-i', str(sdk / 'Resources'), str(resource), '-o', str(contents / 'Resources' / (stem + '.rsrc')))
    common = ['clang++', '-std=c++17', '-arch', 'arm64', '-Wall', '-Wextra', '-Wpedantic', '-Werror']
    binary = contents / 'MacOS' / stem
    command = common + ['-bundle', '-fvisibility=hidden', '-I' + str(output),
        '-I' + str(sdk / 'Headers'), '-I' + str(sdk / 'Headers/SP'),
        '-Wl,-exported_symbol,_EntryPointFunc,-exported_symbol,_AEHL_RetainedBuildIdentity',
        str(Path(__file__).with_name('RetainedIdentityProbe.cpp')), '-o', str(binary)]
    run(*command); run('codesign', '--force', '--sign', '-', str(candidate)); run('codesign', '--verify', '--strict', str(candidate))
    exports = run('nm', '-arch', 'arm64', '-gU', str(binary))
    if {line.split()[-1] for line in exports.splitlines()} != {'_EntryPointFunc', '_AEHL_RetainedBuildIdentity'}:
        raise ValueError('unexpected exported entrypoint')
    library = ctypes.CDLL(str(binary)); getter = library.AEHL_RetainedBuildIdentity; getter.restype = ctypes.c_char_p
    if json.loads(getter().decode()) != identity:
        raise ValueError('runtime identity mismatch')
    inert = output / 'observer-inert-tests'
    run(*(common + ['-I' + str(sdk / 'Headers'), '-I' + str(sdk / 'Headers/SP'),
        str(repo / 'tests/retained_identity_inert.cpp'), '-o', str(inert)]))
    inert_result = run(str(inert), str(binary), token, sha(binary))
    if any(control.iterdir()) or any(journal.iterdir()):
        raise ValueError('inert entry produced evidence side effects')
    if any(sha(sdk / name) != digest for name, digest in sdk_inputs.items()):
        raise ValueError('SDK changed during build')
    if reviewed_roots() != providers:
        raise ValueError('provider files changed during build')
    if run('git', '-C', str(repo), 'status', '--porcelain') or run('git', '-C', str(repo), 'rev-parse', 'HEAD').strip() != commit:
        raise ValueError('source changed during build')
    record = {**identity, 'compiler': run('clang++', '--version'), 'sdk': run('xcrun', '--show-sdk-version').strip(),
        'sdk_input_sha256': sdk_inputs, 'sdk_general_header_sha256': sha(sdk / 'Headers/AE_GeneralPlug.h'), 'command': command,
        'host_executable': str(host), 'host_sha256': HOST_SHA256, 'host_mode': mode,
        'module_path': str(module), 'authorized_bundle': str(installed) if args.authorized_host else None,
        'candidate_bundle': str(candidate), 'control_directory': str(control), 'journal_directory': str(journal),
        'native_timeout_ms': 15000, 'activation_env': {'AEHL_RETAINED_IDENTITY_TOKEN': token}, 'provider_profile': providers,
        'checks': {'build_sign_exports': 'PASS', 'identity_getter': 'PASS', 'inert_entrypoint': 'PASS', 'live_ae': 'NOT RUN'},
        'inert_entrypoint_output': inert_result, 'external_supervisor': 'NOT CONNECTED', 'installation_performed': False, 'ae_launch_performed': False,
        'files': {str(p.relative_to(candidate)): sha(p) for p in sorted(candidate.rglob('*')) if p.is_file()}}
    manifest = output / 'manifest.json'; manifest.write_text(json.dumps(record, indent=2, sort_keys=True) + '\n'); os.chmod(manifest, 0o600)
    print(output); print('manifest_sha256=' + sha(manifest)); print(inert_result.strip())


if __name__ == '__main__':
    main()
