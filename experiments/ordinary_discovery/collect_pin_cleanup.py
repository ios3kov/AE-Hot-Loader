"""Collect exact PIN cleanup/sort file evidence. Never attach, launch or call AE."""
import argparse
import os
from pathlib import Path
import re
import sys
import tempfile
import zipfile
import subprocess

import collect_resource_search_abi as common

PIN = common.APP / 'Contents/Frameworks/PIN.dylib'
PIN_SHA256 = '63c1fc4869b0d440d98bb5b1ce7931f07f70f494685b32ea9afdafecd4e72210'
PIN_UUID = '11A71CEB-5A06-3FB7-92C7-0037233B101B'
WINDOWS = (('PIN-cleanup', 0x113c94, 0x113c98), ('PIN-sort', 0x113c98, 0x113d7c))
SYMBOLS = {
    0x113c94: '__ZL16PINp_CleanupFuncPvPFisPKcS_PhES_',
    0x113c98: '__ZL16PINp_SortModulesv',
    0x113d7c: '__ZN15PIN_GlobalState6CreateEP9U_Context',
}
require = common.require


def validate_symbols(text):
    definitions = []
    for line in text.splitlines():
        match = re.fullmatch(r'([0-9a-fA-F]+)\s+[tT]\s+(\S+)', line)
        if match:
            address = int(match[1], 16)
            if 0x113c94 <= address <= 0x113d7c:
                definitions.append((address, match[2]))
    require(definitions == list(SYMBOLS.items()), 'PIN exact symbol/window boundaries differ')
    return '\n'.join(line for line in text.splitlines() if
                     any(name in line for name in ('PINp_CleanupFunc', 'PINp_SortModules',
                                                   'PINp_G', 'PINp_ModCompareFunc', 'PIN_GlobalState'))) + '\n'


def validate_metadata(text):
    uuids = re.findall(r'^\s*uuid ([A-F0-9-]{36})\s*$', text, re.M)
    require(uuids == [PIN_UUID], 'PIN UUID differs or is ambiguous')
    segments = []
    for block in text.split('Load command ')[1:]:
        if re.search(r'^\s*segname __TEXT\s*$', block, re.M):
            values = []
            for key in ('vmaddr', 'vmsize', 'initprot', 'maxprot'):
                matches = re.findall(r'^\s*' + key + r' (0x[0-9a-fA-F]+)\s*$', block, re.M)
                require(len(matches) == 1, 'PIN text segment metadata incomplete')
                values.append(int(matches[0], 16))
            segments.append(values)
    require(segments == [[0, 0x224000, 5, 5]], 'PIN text segment identity/protection differs')
    require(all(0 <= start < end <= 0x224000 for _, start, end in WINDOWS), 'PIN window outside text')
    return {'uuid': PIN_UUID, 'text_vm': '0x0', 'text_size': '0x224000'}


def validate_window(text, label, start, end):
    count = common.validate_disassembly(text, start, end)
    rows = {}
    for address, op, operands in re.findall(
            r'^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:[ \t]+(\S+)[ \t]*([^\n]*)', text, re.M):
        rows[int(address, 16)] = (op, re.sub(r'\s+', '', operands.split(';')[0]))
    anchors = ({0x113c94: ('b', '0x113c98')} if label == 'PIN-cleanup' else {
        0x113ca8: ('adrp', 'x8,314'), 0x113cac: ('add', 'x8,x8,#0x1a8'),
        0x113cb0: ('ldp', 'x0,x1,[x8]'), 0x113cec: ('bl', '0x1171c0'),
        0x113cf0: ('mov', 'w19,#0x0'), 0x113d04: ('ret', ''),
        0x113d34: ('ret', ''), 0x113d64: ('ret', ''),
        0x113d74: ('bl', '0x1d2fe0'), 0x113d78: ('bl', '0x4f98'),
    })
    require((label, start, end) in WINDOWS, 'unknown PIN inspection window')
    require(all(rows.get(address) == expected for address, expected in anchors.items()),
            'PIN cleanup/sort structural anchors differ')
    return {'decoded_instructions': count, 'structural_anchors': len(anchors),
            'claim': 'file-only-structural-evidence-not-lifetime-or-runtime-certification'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    if sys.platform != 'darwin':
        parser.exit(2, 'BLOCKED: PIN file inspection requires macOS.\n')
    try:
        commit = common.source_identity()
        before = common.validate_input(PIN, PIN_SHA256)
        nm, errors = common.run_tool(['/usr/bin/nm', '-arch', 'arm64', '-n', str(PIN)])
        require(not errors.strip(), 'PIN symbol inspection diagnostics')
        symbols = validate_symbols(nm)
        metadata, errors = common.run_tool(['/usr/bin/otool', '-arch', 'arm64', '-l', str(PIN)])
        require(not errors.strip(), 'PIN metadata inspection diagnostics')
        identity = validate_metadata(metadata)
        parent = common.ROOT / 'build-ae-hot-loader'
        require(parent.is_dir() and not parent.is_symlink() and parent.stat().st_uid == os.getuid(),
                'owned evidence parent unavailable')
        folder = Path(tempfile.mkdtemp(prefix='pin-cleanup-', dir=parent))
        os.chmod(folder, 0o700)
        common.write_exclusive(folder / 'PIN-symbols.txt', symbols)
        common.write_exclusive(folder / 'PIN-load-commands.txt', metadata)
        windows = {}
        for label, start, end in WINDOWS:
            script = folder / (label + '-inspect.lldb')
            common.write_exclusive(script, common.lldb_script(PIN, start, end))
            output, errors = common.run_tool(['/usr/bin/xcrun', 'lldb', '--no-lldbinit', '--batch', '--source', str(script)])
            require(not errors.strip() and 'error:' not in output.lower() and 'fatal:' not in output.lower(),
                    'PIN bounded disassembly diagnostics')
            common.write_exclusive(folder / (label + '-disassembly.txt'), output)
            windows[label] = {'start': hex(start), 'end': hex(end), **validate_window(output, label, start, end)}
        require(common.validate_input(PIN, PIN_SHA256) == before, 'PIN file changed during collection')
        archive = common.package(folder, {'schema': 'AEHL-PIN-CLEANUP-FILE-1', 'source_commit': commit,
            'scope': 'offline-bounded-pin-cleanup-only', 'input': str(PIN), 'sha256': before,
            'file_identity': identity, 'windows': windows, 'live_ae_operation': 'NOT RUN',
            'plugin_scan': 'NOT RUN', 'runtime_pin_identity': 'NOT PROVEN', 'lifetime_quiescence': 'NOT PROVEN'})
        print('PASS: 58 decoded instructions, 11 structural anchors; file-only, Adobe calls=0')
        print('Report: ' + str(archive)); print('Report SHA-256: ' + common.sha256(archive))
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        parser.exit(2, 'BLOCKED: ' + str(error) + '\n')


if __name__ == '__main__':
    main()
