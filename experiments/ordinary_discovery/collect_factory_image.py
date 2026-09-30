"""Offline AfterFXLib inspection. Never attach, launch AE, scan or call host code.

Python 3.9+, macOS developer tools. Output is private research evidence, not
an installable plug-in. Symbol selection is heuristic and explicitly bounded.
"""
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
MAIN_SHA256 = '464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6'
MAX_FUNCTIONS = 96
MAX_BYTES_PER_FUNCTION = 4096
MAX_TOOL_OUTPUT = 64 * 1024 * 1024
TEXT_SYMBOL = re.compile(r'([0-9a-fA-F]{16})\s+[tT]\s+(\S+)')
TEXT_SYMBOL_VERBOSE = re.compile(r'([0-9a-fA-F]{16})\s+\(__TEXT,__text\)\s+.*\s+(\S+)')
SCAFFOLD = re.compile(r'^__?Z(NK?(St|5boost|7dvacore)|TV|TI|TS)')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def choose_symbols(text):
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
    candidates = []
    for index, address in enumerate(addresses):
        names = by_address[address]
        relevant = [name for name in names if not SCAFFOLD.match(name) and
                    any(token in name for token in (
                        'Factory', 'MEE_', 'FLT_NotifyFilterLoadingDone',
                        'RecognizeFile', 'LoadPlugins', 'LoadAEPlugins'))]
        if not relevant:
            continue
        boundary = addresses[index + 1] if index + 1 < len(addresses) else None
        # A window is never promoted to a proven whole-function extent.
        end = min(boundary, address + MAX_BYTES_PER_FUNCTION) if boundary else address + MAX_BYTES_PER_FUNCTION
        candidates.append(dict(start=address, end=end, names=sorted(set(relevant)),
                               next_text_symbol=boundary,
                               window_capped=boundary is None or boundary > end,
                               priority=min(0 if 'MEE_' in n or 'FLT_NotifyFilterLoadingDone' in n else
                                            1 if any(t in n for t in ('Plugin', 'Filter', 'Recognize')) else 2
                                            for n in relevant)))
    candidates.sort(key=lambda item: (item['priority'], item['start']))
    return dict(matched_addresses=len(candidates), omitted_by_limit=max(0, len(candidates) - MAX_FUNCTIONS),
                functions=candidates[:MAX_FUNCTIONS], selection='heuristic-not-exhaustive')


def commands(image, selection):
    value = str(image)
    if not image.is_absolute() or any(c in value for c in ('"', '\\', '\n', '\r', '\x00')):
        raise ValueError('Unsafe image path')
    result = [
        'settings set target.load-cwd-lldbinit false',
        'settings set target.load-script-from-symbol-file false',
        'target create --no-dependents --arch arm64 "' + value + '"',
    ]
    for item in selection['functions']:
        start, end = item['start'], item['end']
        if type(start) is not int or type(end) is not int or not 0 < start < end <= start + MAX_BYTES_PER_FUNCTION:
            raise ValueError('Invalid address window')
        result.append('disassemble --start-address 0x%x --end-address 0x%x --force' % (start, end))
    return result + ['quit']


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


def main():
    if sys.platform != 'darwin':
        print('BLOCKED: run this offline collector on macOS.', file=sys.stderr)
        return 2
    folder = None
    try:
        app = APP.resolve(strict=True)
        image = (app / REL_IMAGE).resolve(strict=True)
        image.relative_to(app)
        if not image.is_file() or not 0 < image.stat().st_size <= 1024 ** 3:
            raise ValueError('Invalid AfterFXLib image')
        host = app / 'Contents/MacOS/After Effects'
        if digest(host) != MAIN_SHA256:
            raise ValueError('Main executable differs from the supplied baseline')
        before = digest(image)
        folder = Path(tempfile.mkdtemp(prefix='AEHL-AfterFXLib.', dir=Path.home() / 'Desktop'))
        os.chmod(folder, 0o700)
        record = dict(scope='offline-file-inspection-not-live-AE-proof',
                      collector_sha256=digest(Path(__file__).resolve()),
                      main_image_sha256=MAIN_SHA256, image_before_sha256=before,
                      image_baseline='first-observation-not-previously-pinned',
                      runtime_registration='NOT RUN', current_project='NOT OBSERVED')
        nm = run_tool(['/usr/bin/nm', '-arch', 'arm64', '-n', '-m', str(image)], folder, 'symbols.txt')
        run_tool(['/usr/bin/otool', '-arch', 'arm64', '-L', str(image)], folder, 'libraries.txt')
        run_tool(['/usr/bin/otool', '-arch', 'arm64', '-l', str(image)], folder, 'headers.txt')
        selection = choose_symbols(nm.decode('utf-8', errors='strict'))
        (folder / 'selection.json').write_text(json.dumps(selection, indent=2) + '\n')
        if selection['functions']:
            script = folder / 'inspect.lldb'
            script.write_text('\n'.join(commands(image, selection)) + '\n')
            output = run_tool(['/usr/bin/xcrun', 'lldb', '--no-lldbinit', '--batch',
                               '--source', str(script)], folder, 'disassembly.txt', timeout=90)
            stderr = (folder / 'disassembly.txt.stderr').read_bytes()
            if b'error:' in output.lower() or b'error:' in stderr.lower():
                raise ValueError('LLDB reported an inspection error')
        after = digest(image)
        if before != after or digest(host) != MAIN_SHA256:
            raise ValueError('An inspected image changed during collection')
        record.update(image_after_sha256=after, matched_addresses=selection['matched_addresses'],
                      omitted_by_limit=selection['omitted_by_limit'],
                      capture_status='PASS' if selection['functions'] else 'BLOCKED_NO_MATCHES',
                      coverage='bounded-symbol-windows-not-complete-functions-or-factory-proof')
        record['files_sha256'] = {p.name: digest(p) for p in sorted(folder.iterdir()) if p.is_file()}
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
            print('Частичные данные сохранены: ' + str(folder), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
