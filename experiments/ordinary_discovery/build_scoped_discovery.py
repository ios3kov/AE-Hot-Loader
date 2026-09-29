"""Build an inert, research-only scoped AEGP; never install, launch or contact AE."""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import plistlib
import re
import subprocess
import uuid

from verify_scoped_fixture import verify


def run(*command):
    return subprocess.check_output(command, text=True, stderr=subprocess.STDOUT, timeout=120)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cpp(value):
    # JSON's escapes are also valid for these generated C++ strings.
    return json.dumps(value, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--fixture', type=Path, required=True)
    parser.add_argument('--fixture-sha256', required=True,
                        help='expected SHA-256 from the approved fixture record')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    owned = repo / 'build-ae-hot-loader'
    fixture_path = args.fixture.absolute()
    if sha(fixture_path) != args.fixture_sha256:
        parser.error('fixture manifest SHA-256 does not match the selected evidence')
    fixture = verify(fixture_path, owned)
    if not re.fullmatch(r'AEHL\.Embedded\.[0-9a-f]{12}', fixture['match']):
        parser.error('expected the single embedded fixture identity')
    manifest = json.loads(fixture_path.read_text())
    probe = manifest['probes'][0]
    source_state = run('git', '-C', str(repo), 'status', '--porcelain')
    if source_state:
        parser.error('clean source tree required for identified research build')
    sdk = args.sdk.resolve()
    for name in ('Headers/AE_GeneralPlug.h', 'Resources/AE_General.r'):
        if not (sdk / name).is_file():
            parser.error('SDK missing ' + name)
    build_id = 'scoped-' + uuid.uuid4().hex[:12]
    output = owned / build_id
    output.mkdir(mode=0o700)
    evidence = output / 'evidence'
    evidence.mkdir(mode=0o700)
    # This deliberately does not point to /Applications or the running AE.
    # A future supervisor must establish real host isolation at this location.
    host = output / 'host/Adobe After Effects 2025.app/Contents/MacOS/After Effects'
    commit = run('git', '-C', str(repo), 'rev-parse', 'HEAD').strip()
    identity = {'build_id': build_id, 'source_commit': commit, 'source_clean': True,
                'target': 'aarch64-apple-darwin', 'kind': 'research-only-scoped-aegp',
                'fixture_build_id': fixture['build_id'],
                'fixture_manifest_sha256': fixture['manifest_sha256']}
    token = uuid.uuid4().hex
    fields = [build_id, commit, token, str(host), fixture['scan_root'],
              Path(probe['bundle']).name, str(evidence), fixture['match']]
    file_map = ',\n'.join('{' + cpp(name) + ', ' + cpp(digest) + '}'
                         for name, digest in sorted(fixture['files'].items()))
    config = output / 'ScopedDiscoveryConfig.hpp'
    config.write_text('#pragma once\nstatic const scoped::Config research_config {\n' +
                      ',\n'.join(cpp(value) for value in fields) + ',\n{' + file_map + '}};\n' +
                      'static constexpr const char* research_identity = ' +
                      cpp(json.dumps(identity, sort_keys=True)) + ';\n')
    native = repo / 'agent/native/InternalLoader.cpp'
    loader = native.read_text()
    redirects = {
        '/tmp/ae-hot-loader-agent.log': str(evidence / 'native-loader.log'),
        '/tmp/ae-hot-loader-diagnostic-report.log': str(evidence / 'native-diagnostic.log'),
    }
    for old, new in redirects.items():
        if loader.count(cpp(old)) != 1:
            raise ValueError('unexpected native logger source; review required')
        loader = loader.replace(cpp(old), cpp(new))
    native_copy = output / 'InternalLoaderResearch.cpp'
    native_copy.write_text(loader)
    stem = 'AEHLScopedResearch' + build_id.removeprefix('scoped-')
    bundle = output / (stem + '.plugin')
    contents = bundle / 'Contents'
    (contents / 'MacOS').mkdir(parents=True)
    (contents / 'Resources').mkdir()
    (contents / 'Info.plist').write_bytes(plistlib.dumps({
        'CFBundleExecutable': stem, 'CFBundleName': stem,
        'CFBundleIdentifier': 'com.os3kov.AEHotLoader.ScopedResearch.' + build_id,
        'CFBundlePackageType': 'AEgx', 'CFBundleSignature': 'FXTC',
        'CFBundleVersion': '1', 'LSRequiresCarbon': True,
    }))
    resource = output / 'ScopedDiscovery.r'
    resource.write_text('#include "AE_General.r"\nresource \'PiPL\' (16000) {{\n'
                        'Kind { AEGP }, Name { "' + stem + '" },\n'
                        'Category { "General Plugin" }, CodeMacARM64 { "EntryPointFunc" }\n}};\n')
    run('Rez', '-useDF', '-i', str(sdk / 'Resources'), str(resource), '-o',
        str(contents / 'Resources' / (stem + '.rsrc')))
    binary = contents / 'MacOS' / stem
    common = ['clang++', '-std=c++17', '-arch', 'arm64', '-Wall', '-Wextra', '-Werror']
    command = common + ['-bundle', '-fvisibility=hidden', '-I' + str(output),
                       '-Wl,-exported_symbol,_EntryPointFunc,-exported_symbol,_AEHL_ScopedBuildIdentity',
                       '-I' + str(sdk / 'Headers'), '-I' + str(sdk / 'Headers/SP'),
                       str(Path(__file__).with_name('ScopedDiscovery.cpp')),
                       str(native_copy), '-framework', 'CoreFoundation', '-o', str(binary)]
    run(*command)
    run('codesign', '--force', '--sign', '-', str(bundle))
    run('codesign', '--verify', '--strict', str(bundle))
    exports = run('nm', '-arch', 'arm64', '-gU', str(binary))
    if {line.split()[-1] for line in exports.splitlines()} != {
            '_AEHL_ScopedBuildIdentity', '_EntryPointFunc'}:
        raise ValueError('unexpected exported entrypoints')
    library = ctypes.CDLL(str(binary))
    getter = library.AEHL_ScopedBuildIdentity
    getter.restype = ctypes.c_char_p
    if json.loads(getter().decode()) != identity:
        raise ValueError('runtime metadata mismatch')
    # A null suite pointer must remain inert even if this library is loaded by
    # a standalone diagnostic process; never invoke a real AE entry point here.
    entry = library.EntryPointFunc
    entry.argtypes = [ctypes.c_void_p, ctypes.c_int32, ctypes.c_int32,
                     ctypes.c_int32, ctypes.c_void_p]
    entry.restype = ctypes.c_int32
    if entry(None, 0, 0, 0, None) != 0 or list(evidence.iterdir()):
        raise ValueError('inactive entrypoint produced side effects')
    test = output / 'scoped-guard-tests'
    run(*(common + [str(repo / 'tests/scoped_discovery_gate.cpp'), '-o', str(test)]))
    test_result = run(str(test))
    record = {**identity, 'source_state': source_state, 'compiler': run('clang++', '--version'),
              'sdk': run('xcrun', '--show-sdk-version').strip(), 'command': command,
              'sdk_general_header_sha256': sha(sdk / 'Headers/AE_GeneralPlug.h'),
              'native_source_sha256': sha(native), 'generated_native_sha256': sha(native_copy),
              'native_changes': 'only the two log destinations redirected to owned evidence',
              'config_sha256': sha(config), 'exports': exports,
              'host_executable': str(host), 'scan_root': fixture['scan_root'],
              'evidence': str(evidence), 'activation_env': {'AEHL_SCOPED_GATE_TOKEN': token},
              'checks': {'build_sign_exports': 'PASS', 'identity_getter': 'PASS',
                         'inert_null_entrypoint': 'PASS', 'native_guard_tests': 'PASS',
                         'live_ae': 'NOT RUN'}, 'native_guard_output': test_result,
              'native_guard_binary_sha256': sha(test),
              'files': {str(p.relative_to(bundle)): sha(p) for p in sorted(bundle.rglob('*'))
                        if p.is_file()}}
    (output / 'manifest.json').write_text(json.dumps(record, indent=2) + '\n')
    print(output)
    print(test_result.strip())


if __name__ == '__main__':
    main()
