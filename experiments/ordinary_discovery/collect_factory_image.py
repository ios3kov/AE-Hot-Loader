"""Offline inspection of allowlisted AE libraries. Never attach, launch AE, scan or call host code.

Python 3.9+, macOS developer tools. Output is private research evidence, not
an installable plug-in. Symbol selection is heuristic and explicitly bounded.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys
import tempfile
import zipfile

APP = Path('/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app')
REL_IMAGE = 'Contents/Frameworks/AfterFXLib.framework/Versions/A/AfterFXLib'
IMAGE_PATHS = {'AfterFXLib': REL_IMAGE, 'MEE': 'Contents/Frameworks/MEE.dylib',
               'FLT': 'Contents/Frameworks/FLT.dylib'}
MAIN_SHA256 = '464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6'
MAX_FUNCTIONS = 96
MAX_BYTES_PER_FUNCTION = 4096
MAX_FACTORY_BYTES = 8192
MAX_TOOL_OUTPUT = 64 * 1024 * 1024
TEXT_SYMBOL = re.compile(r'([0-9a-fA-F]{16})\s+[tT]\s+(\S+)')
TEXT_SYMBOL_VERBOSE = re.compile(r'([0-9a-fA-F]{16})\s+\(__TEXT,__text\)\s+.*\s+(\S+)')
SCAFFOLD = re.compile(r'^__?Z(NK?(St|5boost|7dvacore)|TV|TI|TS)')
MEE_IMAGE_SHA256 = '18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344'
REGISTRATION_ANCHORS = ('MEE_RegisterVideoFilterFactory', 'MEE_GetVideoFilterModules',
                        'MEE_SetAELibPluginSetter', 'MEE_GetAELibPluginSetter',
                        'FLT_NotifyFilterLoadingDone')
FACTORY_FOCUS = ('AELibraryVideoFilterFactory', 'AELibraryVideoFilterModule',
                 *REGISTRATION_ANCHORS)
# Diagnostic lines are distinct from strings/symbol names in instruction output.
ANSI_STYLE = re.compile(r'\x1b\[[0-9;]*m')
LLDB_ERROR = re.compile(r'^\s*(?:\(lldb\)\s*)?(?:fatal\s+)?error:', re.I | re.M)
DISASSEMBLE_ECHO = re.compile(
    r'^\(lldb\) disassemble --start-address (0x[0-9a-f]+) --end-address (0x[0-9a-f]+)$')
INSTRUCTION = re.compile(r'^.+?\[(0x[0-9a-fA-F]+)\]\s+<\+[0-9]+>:\s+\S')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def choose_symbols(text, factory_only=False):
    by_address = {}
    for line in text.splitlines():
        match = TEXT_SYMBOL.fullmatch(line.strip()) or TEXT_SYMBOL_VERBOSE.fullmatch(line.strip())
        if match:
            address = int(match[1], 16)
            if address > 0 and address % 4 == 0:
                by_address.setdefault(address, []).append(match[2])
    if not by_address:
        raise ValueError('No arm64 text-symbol records')
    addresses = sorted(by_address)
    window_limit = MAX_FACTORY_BYTES if factory_only else MAX_BYTES_PER_FUNCTION
    candidates = []
    for index, address in enumerate(addresses):
        names = by_address[address]
        relevant = [name for name in names if not SCAFFOLD.match(name) and
                    any(token in name for token in (
                        'Factory', 'AELibraryVideoFilter', 'MEE_', 'FLT_NotifyFilterLoadingDone',
                        'RecognizeFile', 'LoadPlugins', 'LoadAEPlugins'))]
        if factory_only:
            relevant = [name for name in relevant if any(t in name for t in FACTORY_FOCUS)]
        if not relevant:
            continue
        boundary = addresses[index + 1] if index + 1 < len(addresses) else None
        # A window is never promoted to a proven whole-function extent.
        end = min(boundary, address + window_limit) if boundary else address + window_limit
        candidates.append(dict(start=address, end=end, names=sorted(set(relevant)),
                               next_text_symbol=boundary,
                               window_capped=boundary is None or boundary > end,
                               priority=min(0 if any(t in n for t in REGISTRATION_ANCHORS) else
                                            1 if 'Factory' in n and any(t in n for t in ('Plugin', 'Filter')) else
                                            2 if any(t in n for t in ('Plugin', 'Filter', 'Recognize')) else 3
                                            for n in relevant)))
    candidates.sort(key=lambda item: (item['priority'], item['start']))
    return dict(matched_addresses=len(candidates), omitted_by_limit=max(0, len(candidates) - MAX_FUNCTIONS),
                functions=candidates[:MAX_FUNCTIONS],
                selection='mee-factory-only' if factory_only else 'heuristic-not-exhaustive')


def commands(image, selection):
    value = str(image)
    if not image.is_absolute() or any(c in value for c in ('"', '\\', '\n', '\r', '\x00')):
        raise ValueError('Unsafe image path')
    result = [
        'settings set target.load-cwd-lldbinit false',
        'settings set target.load-script-from-symbol-file false',
        'target create --no-dependents --arch arm64 "' + value + '"',
    ]
    window_limit = MAX_FACTORY_BYTES if selection.get('selection') == 'mee-factory-only' else MAX_BYTES_PER_FUNCTION
    for item in selection['functions']:
        start, end = item['start'], item['end']
        if type(start) is not int or type(end) is not int or not 0 < start < end <= start + window_limit or start % 4 or end % 4:
            raise ValueError('Invalid address window')
        # LLDB's explicit end-address option group does not accept --force.
        result.append('disassemble --start-address 0x%x --end-address 0x%x' % (start, end))
    return result + ['quit']


def validate_disassembly(output, stderr, selection):
    """Require a complete bounded arm64 transcript, not merely exit status zero.

    Called only after run_tool verified process success. The separate offline
    transcript check can also inspect retained output without rerunning LLDB;
    it cannot establish prior process exit status or image stability.
    """
    if len(output) > MAX_TOOL_OUTPUT or len(stderr) > MAX_TOOL_OUTPUT:
        raise ValueError('Oversized LLDB output')
    text = ANSI_STYLE.sub('', output.decode('utf-8', errors='strict'))
    errors = ANSI_STYLE.sub('', stderr.decode('utf-8', errors='strict'))
    if LLDB_ERROR.search(text) or LLDB_ERROR.search(errors):
        raise ValueError('LLDB reported a diagnostic error')
    functions = selection['functions']
    if not functions or len(functions) > MAX_FUNCTIONS:
        raise ValueError('Invalid disassembly selection')
    # Reuse numeric validation without incorporating untrusted symbol names.
    commands(Path('/offline/validation-image'), selection)
    expected = [(f['start'], f['end']) for f in functions]
    if len(expected) != len(set(expected)):
        raise ValueError('Duplicate disassembly window')
    observed, addresses = [], []
    current = None
    finished = False
    for line in text.splitlines():
        echo = DISASSEMBLE_ECHO.fullmatch(line)
        if echo:
            if finished:
                raise ValueError('Disassembly after quit')
            current = (int(echo[1], 16), int(echo[2], 16))
            observed.append(current)
            addresses.append([])
        elif line.startswith('(lldb) disassemble'):
            raise ValueError('Unexpected disassembly command')
        elif line == '(lldb) quit':
            if finished:
                raise ValueError('Repeated quit')
            finished = True
            current = None
        else:
            instruction = INSTRUCTION.match(line)
            if instruction:
                if current is None:
                    raise ValueError('Instruction outside a requested window')
                addresses[-1].append(int(instruction[1], 16))
    if not finished or observed != expected:
        raise ValueError('Incomplete or unexpected LLDB transcript')
    for (start, end), actual in zip(expected, addresses):
        if actual != list(range(start, end, 4)):
            raise ValueError('Missing or out-of-range arm64 instructions')
    return dict(status='PASS', windows=len(expected),
                instruction_count=sum(map(len, addresses)),
                scope='transcript-only-not-runtime-proof')


def output_limit():
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_TOOL_OUTPUT, MAX_TOOL_OUTPUT))


def run_tool(argv, folder, name, timeout=60):
    # Limits affect only the inspection subprocess, never the running AE.
    with (folder / name).open('xb') as out, (folder / (name + '.stderr')).open('xb') as err:
        result = subprocess.run(argv, stdin=subprocess.DEVNULL, stdout=out, stderr=err,
                                cwd=folder, timeout=timeout, preexec_fn=output_limit)
    if result.returncode != 0:
        raise ValueError('Inspection tool failed: ' + name)
    return (folder / name).read_bytes()


def main(module='AfterFXLib', factory_only=False):
    if sys.platform != 'darwin':
        print('BLOCKED: run this offline collector on macOS.', file=sys.stderr)
        return 2
    folder = None
    record = None
    try:
        if module not in IMAGE_PATHS or (factory_only and module != 'MEE'):
            raise ValueError('Unknown module or unsupported factory-only combination')
        app = APP.resolve(strict=True)
        image = (app / IMAGE_PATHS[module]).resolve(strict=True)
        image.relative_to(app)
        if not image.is_file() or not 0 < image.stat().st_size <= 1024 ** 3:
            raise ValueError('Invalid inspection image')
        host = app / 'Contents/MacOS/After Effects'
        if digest(host) != MAIN_SHA256:
            raise ValueError('Main executable differs from the supplied baseline')
        before = digest(image)
        if factory_only and before != MEE_IMAGE_SHA256:
            raise ValueError('MEE image differs from the supplied baseline')
        folder = Path(tempfile.mkdtemp(prefix='AEHL-' + module + '.', dir=Path.home() / 'Desktop'))
        os.chmod(folder, 0o700)
        record = dict(scope='offline-file-inspection-not-live-AE-proof',
                      module=module, capture_status='NOT RUN',
                      collector_sha256=digest(Path(__file__).resolve()),
                      main_image_sha256=MAIN_SHA256, image_before_sha256=before,
                      image_baseline='pinned-to-supplied-MEE-record' if factory_only else 'first-observation-not-previously-pinned',
                      factory_only=factory_only,
                      runtime_registration='NOT RUN', current_project='NOT OBSERVED')
        # Save identity before the first tool, including on partial failure.
        (folder / 'record.json').write_text(json.dumps(record, indent=2) + '\n')
        nm = run_tool(['/usr/bin/nm', '-arch', 'arm64', '-n', '-m', str(image)], folder, 'symbols.txt')
        run_tool(['/usr/bin/otool', '-arch', 'arm64', '-L', str(image)], folder, 'libraries.txt')
        run_tool(['/usr/bin/otool', '-arch', 'arm64', '-l', str(image)], folder, 'headers.txt')
        selection = choose_symbols(nm.decode('utf-8', errors='strict'), factory_only=factory_only)
        (folder / 'selection.json').write_text(json.dumps(selection, indent=2) + '\n')
        if selection['functions']:
            run_tool(['/usr/bin/xcrun', 'lldb', '--version'], folder, 'lldb-version.txt')
            script = folder / 'inspect.lldb'
            script.write_text('\n'.join(commands(image, selection)) + '\n')
            output = run_tool(['/usr/bin/xcrun', 'lldb', '--no-lldbinit', '--batch',
                               '--source', str(script)], folder, 'disassembly.txt', timeout=90)
            stderr = (folder / 'disassembly.txt.stderr').read_bytes()
            record['disassembly_validation'] = validate_disassembly(output, stderr, selection)
        after = digest(image)
        if before != after or digest(host) != MAIN_SHA256:
            raise ValueError('An inspected image changed during collection')
        record.update(image_after_sha256=after, matched_addresses=selection['matched_addresses'],
                      omitted_by_limit=selection['omitted_by_limit'],
                      capture_status='PASS' if selection['functions'] else 'BLOCKED_NO_MATCHES',
                      coverage='bounded-symbol-windows-not-complete-functions-or-factory-proof')
        record['files_sha256'] = {p.name: digest(p) for p in sorted(folder.iterdir()) if p.is_file() and p.name != 'record.json'}
        (folder / 'record.json').write_text(json.dumps(record, indent=2) + '\n')
        archive = folder.with_name(folder.name + '.zip')
        with zipfile.ZipFile(archive, 'x', zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(folder.iterdir()):
                bundle.write(path, arcname=path.name)
        os.chmod(archive, 0o600)
        print('Пришлите: ' + str(archive))
        return 0 if selection['functions'] else 2
    except (OSError, ValueError, UnicodeError, subprocess.TimeoutExpired) as exc:
        print('BLOCKED: ' + str(exc), file=sys.stderr)
        if folder:
            if record is not None:
                record.update(capture_status='FAIL', error_type=type(exc).__name__,
                              failure=str(exc), image_after_sha256=None,
                              image_stability='NOT VERIFIED after failure')
                try:
                    record['files_sha256'] = {p.name: digest(p) for p in sorted(folder.iterdir())
                                               if p.is_file() and p.name != 'record.json'}
                    (folder / 'record.json').write_text(json.dumps(record, indent=2) + '\n')
                except OSError:
                    pass  # Preserve all earlier outputs even if the disk is unavailable.
            print('Частичные данные сохранены: ' + str(folder), file=sys.stderr)
        return 2


def entry(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--module', choices=tuple(IMAGE_PATHS), action='append',
                        help='Read only this library; repeat to inspect MEE and FLT.')
    parser.add_argument('--factory-only', action='store_true',
                        help='MEE only: inspect the identified factory/module and registration anchors.')
    args = parser.parse_args(argv)
    modules = args.module or ['AfterFXLib']
    if len(set(modules)) != len(modules):
        parser.error('Do not repeat a module')
    if args.factory_only and modules != ['MEE']:
        parser.error('--factory-only requires exactly --module MEE')
    for module in modules:
        status = main(module, factory_only=True) if args.factory_only else main(module)
        if status:
            return status
    return 0


if __name__ == '__main__':
    raise SystemExit(entry())
