"""Build/sign/measure a separate inert PICA diagnostic; never install or run AE."""
import argparse
import ctypes
import json
import os
from pathlib import Path
import plistlib
import uuid

from build_no_scan_directory_probe import run, sha, cpp, canonical_existing, EXPECTED_HOST

HOST_SHA = '464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6'
HEADER_PINS = {
    'Headers/AE_GeneralPlug.h': '30d12ec3eb5af1a902c7414053b1be1da0204b226e0b1cdc71272be1e137000c',
    'Headers/SP/SPFiles.h': '1b3e17ec595d728ccbd239a626ec1930c17f4186e1c4554ace9e76de8eaa5f83',
    'Headers/SP/SPAdapts.h': '9df12abb968a64a2e16510fecd5ebf4ffa7585879afc7b39adcde16e9ffcad77',
    'Headers/SP/SPAccess.h': '7f63ce94fb04a5659979899dffee9ed67f1eb9d938a63fd5de11418329dfa574',
    'Headers/SP/SPPlugs.h': '8de03821b78b4eb47d792a39cd2b406bba5773f38423f24a3a6cf6383f8f6664',
    'Headers/SP/SPBasic.h': 'a1258cfd57eedbe5ecbfcebf2bc7df8a3826f495f8e3cc549dce55e60e73395b',
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--prospective-plugin-root', type=Path, required=True,
                        help='reviewed prospective path only; no authorization or copy')
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    if run('git', '-C', str(repo), 'status', '--porcelain'):
        parser.error('clean identified source required')
    source = run('git', '-C', str(repo), 'rev-parse', 'HEAD').strip()
    sdk = canonical_existing(args.sdk, 'SDK root')
    root = canonical_existing(args.prospective_plugin_root, 'prospective plug-in root')
    if not root.is_dir() or sha(EXPECTED_HOST) != HOST_SHA:
        parser.error('target file/root does not match reviewed AE 25.6 scope')
    for name, digest in HEADER_PINS.items():
        if sha(sdk / name) != digest:
            parser.error('SDK contract differs: ' + name)
    inputs = {str(p.relative_to(sdk)): sha(p) for name in ('Headers', 'Resources')
              for p in sorted((sdk / name).rglob('*')) if p.is_file()}
    build = 'pica-' + uuid.uuid4().hex[:12]
    run_id, token = 'pica-availability-' + uuid.uuid4().hex, uuid.uuid4().hex
    folder = repo / 'build-ae-hot-loader' / build
    folder.mkdir(mode=0o700, parents=True)
    control = folder / 'control'; control.mkdir(mode=0o700)
    stem = 'AEHLPica' + build[5:]
    bundle = folder / (stem + '.plugin')
    installed = root / bundle.name
    if installed.exists():
        parser.error('prospective destination exists')
    module = installed / 'Contents/MacOS' / stem
    identity = dict(build_id=build, run_id=run_id, source_commit=source, source_clean=True,
                    target='aarch64-apple-darwin', kind='research-only-pica-availability-aegp')
    values = [run_id, source, build, EXPECTED_HOST, module, control, token, HOST_SHA]
    config = folder / 'PicaAvailabilityConfig.hpp'
    config.write_text('#pragma once\nstatic const pica_probe::Config research_config {' +
                      ','.join(cpp(x) for x in values) + '};\nstatic constexpr const char* research_identity = ' +
                      cpp(json.dumps(identity, sort_keys=True)) + ';\n')
    config.chmod(0o600)
    contents = bundle / 'Contents'
    (contents / 'MacOS').mkdir(parents=True)
    (contents / 'Resources').mkdir()
    (contents / 'Info.plist').write_bytes(plistlib.dumps(dict(
        CFBundleExecutable=stem, CFBundleName=stem, CFBundleIdentifier='com.os3kov.AEHotLoader.Pica.'+build,
        CFBundlePackageType='AEgx', CFBundleSignature='FXTC', CFBundleVersion='1', LSRequiresCarbon=True)))
    resource = folder / 'PicaAvailability.r'
    resource.write_text('#include "AE_General.r"\nresource \'PiPL\' (16000) {{\nKind { AEGP }, Name { "'+stem+
                        '" }, Category { "General Plugin" }, CodeMacARM64 { "EntryPointFunc" }\n}};\n')
    run('Rez', '-useDF', '-i', str(sdk / 'Resources'), str(resource), '-o', str(contents/'Resources'/(stem+'.rsrc')))
    common = ['clang++', '-std=c++17', '-arch', 'arm64', '-Wall', '-Wextra', '-Wpedantic', '-Werror']
    includes = ['-I'+str(folder), '-I'+str(sdk/'Headers'), '-I'+str(sdk/'Headers/SP')]
    binary = contents / 'MacOS' / stem
    command = common + ['-bundle', '-fvisibility=hidden', *includes,
        '-Wl,-exported_symbol,_EntryPointFunc,-exported_symbol,_AEHL_PicaBuildIdentity',
        str(Path(__file__).with_name('PicaAvailabilityProbe.cpp')), '-framework', 'CoreFoundation', '-o', str(binary)]
    run(*command)
    run('codesign', '--force', '--sign', '-', str(bundle))
    run('codesign', '--verify', '--strict', str(bundle))
    symbols = {line.split()[-1] for line in run('nm', '-arch', 'arm64', '-gU', str(binary)).splitlines()}
    if symbols != {'_EntryPointFunc', '_AEHL_PicaBuildIdentity'}:
        raise ValueError('unexpected exports')
    library = ctypes.CDLL(str(binary))
    getter = library.AEHL_PicaBuildIdentity; getter.restype = ctypes.c_char_p
    if json.loads(getter().decode()) != identity:
        raise ValueError('identity mismatch')
    inert = folder / 'inert'
    run(*(common + includes + [str(repo/'tests/pica_availability_inert.cpp'), '-o', str(inert)]))
    inert_output = run(str(inert), str(binary), token, sha(binary))
    if any(control.iterdir()):
        raise ValueError('inert entry produced control state')
    if any(sha(sdk/name) != digest for name, digest in inputs.items()):
        raise ValueError('SDK changed')
    if run('git', '-C', str(repo), 'status', '--porcelain') or run('git','-C',str(repo),'rev-parse','HEAD').strip()!=source:
        raise ValueError('source changed')
    record = dict(**identity, host_executable=str(EXPECTED_HOST), host_sha256=HOST_SHA,
        candidate_bundle=str(bundle), prospective_bundle=str(installed), module_path=str(module),
        control_directory=str(control), activation_env={'AEHL_PICA_AVAILABILITY_TOKEN': token},
        sdk_input_sha256=inputs, compiler=run('clang++','--version'), command=command,
        binary_sha256=sha(binary), native_timeout_ms=10000, external_timeout_ms=30000,
        suite_scope=[{'name':n,'version':v} for n,v in [('SP Plug-ins Suite',4),('SP Plug-ins Suite',6),
                                                     ('SP Access Suite',3),('SP Adapters Suite',3)]],
        operation_scope='public suite acquisition may load modules; adapter-name/version iteration only',
        suite_release_policy='bounded PICA leases retained until owned host exits; no private teardown',
        checks={'build_sign_exports':'PASS','identity_getter':'PASS','inert_entrypoint':'PASS','live_ae':'NOT RUN'},
        inert_output=inert_output, installation_performed=False, ae_launch_performed=False,
        authorization='NOT GRANTED by builder',
        files={str(p.relative_to(bundle)):sha(p) for p in sorted(bundle.rglob('*')) if p.is_file()})
    manifest = folder/'manifest.json'; manifest.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');manifest.chmod(0o600)
    print(folder);print('manifest_sha256='+sha(manifest));print(inert_output.strip())


if __name__ == '__main__':
    main()
