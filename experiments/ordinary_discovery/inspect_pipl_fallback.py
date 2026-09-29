"""Offline inspection only: no process attach, launch, expression or host calls.

Full disassembly stays in ignored local evidence, not in redistributed source.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import uuid

FUNCTIONS = (
    'ML::GetPFPluginData(ML::PluginImpl&, PF_PluginData&)',
    'ML::PluginImpl::GetPiPLs()',
    'ML::AEPlugin::LoadPiPLs()',
    'ML::PluginImpl::LoadPiPLs()',
    'ML::PluginImpl::InternalLoadPiPLs(std::__1::shared_ptr<ASL::Module>)',
    'ML::PiPL::LoadFromResource(std::__1::shared_ptr<ASL::Module> const&)',
    'ML::PiPL::LoadFromResource(std::__1::shared_ptr<ASL::Module>, short)',
)
ASL_FUNCTIONS = (
    'ASL::Module::LoadResource(short, std::__1::basic_string<unsigned short, std::__1::char_traits<unsigned short>, dvacore::allocator::STLAllocator<unsigned short>> const&, int&) const',
    'ASL::Module::LoadResource(unsigned short const*, unsigned short const*, int&) const',
    'ASL::Module::FindLocalizedResource(unsigned short const*, unsigned short const*, int&) const',
    'ASL::Module::FindNonLocalizedResource(unsigned short const*, unsigned short const*, int&) const',
)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--output-parent', type=Path, required=True)
    parser.add_argument('--profile', choices=('pipl', 'asl'), default='pipl')
    args = parser.parse_args()
    image = args.image.resolve(strict=True)
    if not image.is_file() or any(c in str(image) for c in '\"\n\r'):
        parser.error('Require a regular image path without quotes or line breaks')
    repo = Path(__file__).resolve().parents[2]
    sha = hashlib.sha256(image.read_bytes()).hexdigest()
    run = 'pipl-static-' + uuid.uuid4().hex
    folder = args.output_parent.resolve(strict=True) / run
    folder.mkdir(mode=0o700)
    commands = ['target create "' + str(image) + '"']
    commands += ['disassemble -n "' + name + '"' for name in (ASL_FUNCTIONS if args.profile == 'asl' else FUNCTIONS)]
    commands += ['quit']
    argv = ['xcrun', 'lldb', '-b', '--no-lldbinit']
    for command in commands:
        argv += ['-o', command]
    result = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    with (folder / 'disassembly.txt').open('x') as f:
        f.write(result.stdout + result.stderr)
    record = dict(run_id=run, scope='offline-only-not-runtime-proof',
                  image=str(image), image_sha256=sha, command=argv,
                  source_commit=subprocess.check_output(['git','rev-parse','HEAD'], cwd=repo, text=True).strip(),
                  source_state=subprocess.check_output(['git','status','--porcelain'], cwd=repo, text=True),
                  status='PASS' if result.returncode == 0 and hashlib.sha256(image.read_bytes()).hexdigest() == sha else 'FAIL',
                  returncode=result.returncode,
                  output_sha256=hashlib.sha256((folder/'disassembly.txt').read_bytes()).hexdigest())
    with (folder / 'record.json').open('x') as f:
        json.dump(record, f, indent=2)
    print(record['status'], folder)
    if record['status'] != 'PASS':
        raise SystemExit(1)

if __name__ == '__main__':
    main()
