#!/usr/bin/env python3
"""Collect bounded Stage C1 search, cleanup or lifecycle evidence from pinned files.

Offline/file-only: never launches or attaches to After Effects and never loads
Adobe code. Captures fixed arm64 disassembly windows plus selected symbols.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[2]
APP = Path("/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app")
PROFILE = ROOT / "experiments/ordinary_discovery/AE256ResourceProfile.hpp"
MAX_OUTPUT = 2 * 1024 * 1024
WINDOWS = {
    # SearchStatFunc + Egg_PlugSearch, and all of PLUG_Search through its
    # return/unwind paths. Ends are the next defined text symbols in these pins.
    "aelib": (0x638CC, 0x63A70),
    "PLUG": (0x8A6C, 0x9028),
}
REVIEWS = {
    "search-abi": tuple((name, name, *bounds) for name, bounds in WINDOWS.items()),
    "cleanup": (
        ("PLUG-install", "PLUG", 0x87E4, 0x8A6C),
        ("PLUG-cleanup", "PLUG", 0xEB20, 0xEC1C),
        ("FLT-birth", "FLT", 0xD7AC, 0xDAE0),
        ("MEE-setup", "MEE", 0x36C58, 0x36DA4),
        ("MEE-scan", "MEE", 0x36DA4, 0x376EC),
        ("MEE-callback", "MEE", 0x376EC, 0x37A00),
        ("MEE-finish", "MEE", 0x37EEC, 0x37F34),
        ("MEE-setdown", "MEE", 0x37F34, 0x38044),
    ),
    "lifecycle": (
        ("PLUG-prep", "PLUG", 0x7DE4, 0x807C),
        ("PLUG-unprep", "PLUG", 0x807C, 0x82B8),
        ("PLUG-unprep-internal", "PLUG", 0x7C74, 0x7D70),
        ("PLUG-state", "PLUG", 0xDFF0, 0xE028),
        ("PLUG-constructor", "PLUG", 0xC9B4, 0xCD74),
        ("MEE-callback", "MEE", 0x376EC, 0x37A00),
        ("MEE-setdown", "MEE", 0x37F34, 0x38044),
    ),
    "publication": (
        ("PLUG-file", "PLUG", 0xF6C0, 0xFA1C),
        ("PLUG-path", "PLUG", 0x6FA8, 0x7150),
        ("FLT-scan", "FLT", 0x8CF98, 0x8D250),
        ("FLT-setup-a", "FLT", 0x8D250, 0x8E250),
        ("FLT-setup-b", "FLT", 0x8E250, 0x8EF8C),
        ("FLT-add-a", "FLT", 0x8B2D4, 0x8C2D4),
        ("FLT-add-b", "FLT", 0x8C2D4, 0x8CC70),
        ("FLT-registry", "FLT", 0x5014, 0x53F0),
        ("FLT-postsetup", "FLT", 0x9284C, 0x92AB8),
        ("FLT-ready", "FLT", 0x146C8, 0x14838),
        ("FLT-lazy-globals", "FLT", 0x5E504, 0x5E764),
        ("FLT-register-lazy", "FLT", 0x99268, 0x993A4),
        ("FLT-if-missing", "FLT", 0x993A4, 0x997E4),
    ),
    "ownership": (
        ("MEE-setup", "MEE", 0x36C58, 0x36DA4),
        ("MEE-scan", "MEE", 0x36DA4, 0x376EC),
        ("MEE-callback", "MEE", 0x376EC, 0x37A00),
        ("MEE-finish", "MEE", 0x37EEC, 0x37F34),
        ("MEE-setdown", "MEE", 0x37F34, 0x38044),
    ),
}
DATA_WINDOWS = {"lifecycle": (("PLUG-vtable", "PLUG", 0x14920, 12),)}
INPUTS = {
    "aelib": (
        APP / "Contents/Frameworks/aelib.framework/Versions/A/aelib",
        "f6124504c8eea332ef257bf1111e6db656c2e07bb57a7b178ec775020ba5407f",
    ),
    "PLUG": (
        APP / "Contents/Frameworks/PLUG.dylib",
        "12f2493892c915dae2361beb2982d8e2c66022574f148cc0097df6966e941b22",
    ),
    "FLT": (
        APP / "Contents/Frameworks/FLT.dylib",
        "227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256",
    ),
    "MEE": (
        APP / "Contents/Frameworks/MEE.dylib",
        "18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344",
    ),
}
SYMBOL_WANTED = {
    "search-abi": re.compile(r"(PLUG_Search|Egg_PlugSearch|SearchStatFunc)"),
    "cleanup": re.compile(r"(PLUG_InstallScan|PLUGp_DoCleanups|FLT_Birth|"
                          r"SetupGeneralPluginScan|PluginScanFunc|PluginCleanupFunc|"
                          r"CleanupGeneralPluginScan|SetdownGeneralPlugins)"),
    "lifecycle": re.compile(r"(PLUG_PrepRoutine|PLUG_UnprepRoutine|PLUGp_UnprepRoutine|"
                            r"PLUG_RoutineDescPriv|PluginCleanupFunc|SetdownGeneralPlugins)"),
    "publication": re.compile(r"(PLUGp_ScanFile|PLUG_RegisterRoutine|FLT_PLUGScanFunc|"
                              r"FLTp_FiltSetup|FLTp_AddEffect|RegisterNewFilter|"
                              r"FiltPostSetup|ScReadyFilter|DoLazyGlobals|RegisterEffectIfMissing)"),
    "ownership": re.compile(r"(SetupGeneralPluginScan|PluginScanFunc|PluginCleanupFunc|"
                            r"CleanupGeneralPluginScan|SetdownGeneralPlugins|vectorI13GeneralPlugin)"),
}

# Addressed instruction checks corroborate the pinned file's ownership flow;
# they never certify actual record identity, lifetime or safe repeated invocation.
OWNERSHIP_ANCHORS = {
    "MEE-setup": {
        0x36c7c: ('adrp', 'x8,217'), 0x36c80: ('add', 'x8,x8,#0xd70'),
        0x36c84: ('ldp', 'x21,x22,[x8]'), 0x36c98: ('sub', 'x22,x22,#0xb0'),
        0x36ccc: ('ldaddal', 'w23,w8,[x8]'), 0x36ce4: ('blr', 'x8'),
        0x36cec: ('ldaddal', 'w23,w8,[x8]'), 0x36d04: ('blr', 'x8'),
        0x36d10: ('str', 'x21,[x8,#0xd78]'),
    },
    "MEE-scan": {
        0x37108: ('bl', '0x9ed98'), 0x371ec: ('adrp', 'x9,216'),
        0x371f0: ('add', 'x9,x9,#0xd78'), 0x371f4: ('ldp', 'x24,x9,[x9]'),
        0x37200: ('str', 'x8,[x24]'), 0x37208: ('str', 'x8,[x24,#0x8]'),
        0x37214: ('mov', 'w9,#0x1'), 0x37218: ('ldadd', 'w9,w8,[x8]'),
        0x3723c: ('add', 'x0,x24,#0x90'), 0x3726c: ('bl', '0x40614'),
        0x3730c: ('strb', 'w8,[x24,#0xa8]'), 0x37310: ('add', 'x0,x24,#0xb0'),
        0x37318: ('str', 'x0,[x27,#0xd78]'),
    },
    "MEE-callback": {
        0x37724: ('adrp', 'x8,216'), 0x37728: ('add', 'x8,x8,#0xd70'),
        0x3772c: ('ldp', 'x21,x24,[x8]'), 0x37768: ('add', 'x21,x21,#0xb0'),
        0x3779c: ('bl', '0x9e900'), 0x377a0: ('cbnz', 'w0,0x37768'),
        0x377a4: ('strb', 'w25,[x21,#0xa8]'), 0x377c0: ('mov', 'x22,x21'),
        0x377c4: ('movi.2d', 'v0,#0000000000000000'),
        0x377c8: ('str', 'q0,[x22,#0x10]!'), 0x377d0: ('stp', 'q0,q0,[x21,#0x20]'),
        0x377d4: ('stp', 'q0,q0,[x21,#0x40]'), 0x377d8: ('stp', 'q0,q0,[x21,#0x60]'),
        0x377dc: ('str', 'q0,[x21,#0x80]'), 0x377f0: ('mov', 'w0,#0x3'),
        0x377fc: ('mov', 'x4,x22'), 0x37800: ('blr', 'x8'),
    },
    "MEE-finish": {
        0x37ef8: ('adrp', 'x8,216'), 0x37efc: ('add', 'x8,x8,#0xd70'),
        0x37f00: ('ldp', 'x19,x20,[x8]'), 0x37f08: ('add', 'x19,x19,#0xb0'),
        0x37f14: ('ldr', 'x8,[x19,#0x80]'), 0x37f1c: ('ldr', 'x0,[x19,#0x10]'),
        0x37f20: ('blr', 'x8'),
    },
    "MEE-setdown": {
        0x37f50: ('ldr', 'x19,[x8,#0x360]'), 0x37f54: ('ldr', 'x20,[x8,#0x368]'),
        0x37f70: ('ldr', 'x8,[x19,#0x58]'), 0x37f7c: ('blr', 'x8'),
        0x37f80: ('ldrb', 'w8,[x19,#0xa8]'), 0x37f88: ('strb', 'wzr,[x19,#0xa8]'),
        0x37f90: ('bl', '0x9eb10'), 0x37f9c: ('add', 'x8,x8,#0xd70'),
        0x37fa0: ('ldp', 'x19,x21,[x8]'), 0x37fb4: ('sub', 'x21,x21,#0xb0'),
        0x37fe8: ('ldaddal', 'w22,w8,[x8]'), 0x38000: ('blr', 'x8'),
        0x38008: ('ldaddal', 'w22,w8,[x8]'), 0x38020: ('blr', 'x8'),
        0x3802c: ('str', 'x19,[x8,#0xd78]'),
    },
}


# File-only publication anchors. The "if missing" entry creates a MissingEffect
# placeholder; none of these checks certifies a usable native registration ABI.
PUBLICATION_ANCHORS = {
    'PLUG-file': {
        0xf750: ('blr', 'x8'),
        0xf770: ('tbnz', 'w26,#0x0,0xf93c'),
        0xf910: ('ldr', 'x2,[sp,#0x30]'),
        0xf91c: ('blr', 'x8'),
    },
    'PLUG-path': {
        0x7010: ('bl', '0xcd74'),
        0x7054: ('add', 'x20,x20,#0x488'),
        0x70b8: ('bl', '0x8560'),
    },
    'FLT-scan': {
        0x8cfb4: ('bl', '0x4208'),
        0x8cfc0: ('cmp', 'w8,#0xe99'),
        0x8cfd0: ('cmp', 'w8,#0xe99'),
        0x8cfe0: ('bl', '0xa5b68'),
        0x8d028: ('bl', '0xa5844'),
        0x8d05c: ('bl', '0xa5b08'),
        0x8d078: ('mov', 'x3,#0x0'),
        0x8d07c: ('mov', 'x4,#0x0'),
        0x8d080: ('mov', 'x5,#0x0'),
        0x8d084: ('bl', '0x8d250'),
    },
    'FLT-setup-a': {
        0x8d2cc: ('bl', '0x5cc60'),
        0x8d300: ('blr', 'x8'),
        0x8d304: ('mov', 'w8,#0x4b54'),
        0x8d308: ('movk', 'w8,#0x6546,lsl#16'),
        0x8d310: ('b.ne', '0x8ddec'),
        0x8df08: ('bl', '0x4a24'),
        0x8df2c: ('tbz', 'w24,#0x0,0x8dfa0'),
        0x8df30: ('cbz', 'x28,0x8eb4c'),
        0x8e05c: ('bl', '0x8b2d4'),
    },
    'FLT-setup-b': {
        0x8e288: ('bl', '0xa5b80'),
        0x8e388: ('bl', '0x5e26c'),
        0x8e3e4: ('bl', '0x9284c'),
        0x8e404: ('bl', '0x8b2d4'),
        0x8e4e0: ('bl', '0xa5b74'),
        0x8e610: ('bl', '0x5e26c'),
        0x8e66c: ('bl', '0x9284c'),
        0x8e68c: ('bl', '0x8b2d4'),
        0x8e70c: ('bl', '0x146c8'),
        0x8e73c: ('bl', '0x9a204'),
        0x8e74c: ('cbnz', 'w19,0x8ec5c'),
    },
    'FLT-add-a': {
        0x8b81c: ('bl', '0x6ea8'),
        0x8b820: ('cbz', 'w0,0x8b834'),
        0x8b82c: ('bl', '0x71a4'),
        0x8b850: ('bl', '0x4c4c'),
        0x8bd80: ('cbz', 'w21,0x8c200'),
        0x8bd8c: ('bl', '0x5014'),
        0x8c04c: ('bl', '0x5854'),
        0x8c06c: ('bl', '0x9a258'),
        0x8c0f4: ('bl', '0x9a258'),
    },
    'FLT-add-b': {
        0x8cc04: ('bl', '0xa5820'),
    },
    'FLT-registry': {
        0x5054: ('bl', '0xa6d44'),
        0x5058: ('ldp', 'x8,x9,[x20,#0x38]'),
        0x5068: ('str', 'x9,[x8]'),
        0x5080: ('ldadd', 'w10,w9,[x9]'),
        0x5094: ('bl', '0x1571c'),
        0x5098: ('str', 'x0,[x20,#0x38]'),
        0x50a8: ('blr', 'x8'),
        0x5254: ('bl', '0x15970'),
        0x52e4: ('b.eq', '0x5338'),
        0x5300: ('strh', 'w8,[x9,#0x218]'),
        0x530c: ('bl', '0x5480'),
        0x5350: ('stp', 'x9,x8,[x21,#0x38]'),
    },
    'FLT-postsetup': {
        0x9287c: ('blr', 'x8'),
        0x92880: ('tbz', 'w0,#0xa,0x928f0'),
        0x9288c: ('bl', '0x5d0dc'),
        0x9289c: ('blr', 'x8'),
    },
    'FLT-ready': {
        0x14704: ('bl', '0x983c8'),
        0x1475c: ('cbnz', 'w21,0x147e0'),
        0x147f8: ('bl', '0xa71dc'),
    },
    'FLT-lazy-globals': {
        0x5e518: ('bl', '0xa5b5c'),
        0x5e520: ('bl', '0xa60e4'),
        0x5e524: ('cbz', 'x0,0x5e538'),
        0x5e540: ('bl', '0x99fb4'),
    },
    'FLT-register-lazy': {
        0x992b8: ('bl', '0x993a4'),
        0x992c0: ('bl', '0x5e504'),
        0x9934c: ('bl', '0x5c34'),
        0x99354: ('bl', '0x5e504'),
    },
    'FLT-if-missing': {
        0x99544: ('bl', '0x4a24'),
        0x99564: ('tbnz', 'w21,#0x0,0x99748'),
        0x99574: ('bl', '0x5cc60'),
        0x99588: ('add', 'x0,x0,#0x6ba'),
        0x996cc: ('add', 'x1,x1,#0xb74'),
        0x996d0: ('bl', '0x5d0f8'),
        0x996dc: ('bl', '0x5dfd8'),
        0x996e8: ('bl', '0x5decc'),
        0x996f4: ('bl', '0x5014'),
    },
}


def verify_publication(text, label, start, end):
    require((label, 'PLUG' if label.startswith('PLUG-') else 'FLT', start, end)
            in REVIEWS['publication'], 'unreviewed publication window')
    count = validate_disassembly(text, start, end)
    rows = {}
    for address, op, operands in re.findall(
            r'^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:[ \t]+(\S+)[ \t]*([^\n]*)', text, re.M):
        rows[int(address, 16)] = (op, re.sub(r'\s+', '', operands.split(';')[0]))
    expected = PUBLICATION_ANCHORS[label]
    require(all(rows.get(address) == pair for address, pair in expected.items()),
            'publication structural anchors differ')
    return {'decoded_instructions': count, 'structural_anchors': len(expected),
            'claim': 'file-only-conditional-publication-not-safe-runtime-ABI'}


def verify_ownership(text, label, start, end):
    require((label, 'MEE', start, end) in REVIEWS['ownership'], 'unreviewed ownership window')
    count = validate_disassembly(text, start, end)
    rows = {}
    for address, op, operands in re.findall(
            r'^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:[ \t]+(\S+)[ \t]*([^\n]*)', text, re.M):
        rows[int(address, 16)] = (op, re.sub(r'\s+', '', operands.split(';')[0]))
    expected = OWNERSHIP_ANCHORS[label]
    require(all(rows.get(address) == pair for address, pair in expected.items()),
            'MEE ownership structural anchors differ')
    return {'decoded_instructions': count, 'structural_anchors': len(expected),
            'claim': 'file-only-ownership-flow-not-runtime-or-repeat-safety-proof'}


def review_windows(review):
    require(review in REVIEWS, "unknown review scope")
    windows = REVIEWS[review]
    require(len({label for label, *_ in windows}) == len(windows),
            "duplicate review window label")
    for label, name, start, end in windows:
        require(name in INPUTS and re.fullmatch(r"[A-Za-z0-9-]+", label),
                "invalid review window identity")
        lldb_script(INPUTS[name][0], start, end)
    return windows


def require(value, reason):
    if not value:
        raise ValueError(reason)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_identity():
    def git(*args):
        return subprocess.check_output(
            ["git", "-c", "core.fsmonitor=false", *args],
            cwd=ROOT, text=True, stderr=subprocess.STDOUT, timeout=15,
            env=dict(os.environ, GIT_OPTIONAL_LOCKS="0")).strip()
    commit = git("rev-parse", "HEAD")
    require(re.fullmatch(r"[0-9a-f]{40}", commit), "invalid Git source identity")
    require(git("status", "--porcelain=v1", "--untracked-files=all") == "",
            "source tree must be clean")
    return commit


def profile_agrees():
    text = PROFILE.read_text(encoding="utf-8")
    for name, (path, digest) in INPUTS.items():
        require(str(path) in text and digest in text,
                "collector pin differs from C1 profile: " + name)


def validate_input(path, expected):
    path = Path(path)
    require(path.is_absolute(), "input path must be absolute")
    resolved = path.resolve(strict=True)
    app = APP.resolve(strict=True)
    require(resolved == path and app in resolved.parents,
            "input path is outside reviewed app or uses a symlink")
    info = path.stat()
    require(info.st_uid in (0, os.getuid()) and info.st_nlink == 1 and
            0 < info.st_size <= 256 * 1024 * 1024,
            "input file identity is unsafe")
    actual = sha256(path)
    require(actual == expected, "input SHA-256 differs from reviewed profile")
    return actual


def lldb_target(path):
    value = str(path)
    require(not any(c in value for c in ('"', "\\", "\n", "\r", "\x00")),
            "unsafe input path")
    return [
        "settings set target.load-cwd-lldbinit false",
        "settings set target.load-script-from-symbol-file false",
        'target create --no-dependents --arch arm64 "' + value + '"',
    ]


def lldb_script(path, start, end):
    require(0 < start < end <= start + 4096 and start % 4 == 0 and end % 4 == 0,
            "invalid bounded disassembly window")
    return "\n".join(lldb_target(path) + [
        "disassemble --start-address 0x%x --end-address 0x%x" % (start, end), "quit", ""])


def lldb_data_script(path, start, count):
    require(0 < start and start % 8 == 0 and 1 <= count <= 32,
            "invalid bounded data window")
    return "\n".join(lldb_target(path) + [
        "memory read --format x --size 8 --count %d 0x%x" % (count, start), "quit", ""])


def validate_data(text, start, count):
    """Validate file-backed words only; never interpret them as runtime pointers."""
    words = []
    for address, values in re.findall(
            r"^0x([0-9a-fA-F]+):((?:\s+0x[0-9a-fA-F]{16})+)\s*$", text, re.M):
        for index, value in enumerate(values.split()):
            words.append((int(address, 16) + index * 8, int(value, 16)))
    require([address for address, _ in words] == list(range(start, start + count * 8, 8)),
            "data window is incomplete or outside reviewed bounds")
    return [value for _, value in words]


def run_tool(argv, *, input_text=None, timeout=45):
    result = subprocess.run(
        argv, input=input_text, text=True, stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
        env=dict(os.environ, LC_ALL="C"), check=False)
    require(result.returncode == 0, "offline inspection tool failed")
    require(len(result.stdout.encode()) <= MAX_OUTPUT and len(result.stderr.encode()) <= MAX_OUTPUT,
            "offline inspection output exceeded limit")
    return result.stdout, result.stderr


def select_symbols(text, review="search-abi"):
    selected = [line for line in text.splitlines() if SYMBOL_WANTED[review].search(line)]
    require(selected, "expected resource-search symbols were not found")
    return "\n".join(selected) + "\n"


def validate_disassembly(text, start, end):
    """Require one decoded arm64 instruction at every address in the window."""
    instructions = re.findall(r"^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:\s+(\S+)", text, re.M)
    addresses = [int(address, 16) for address, _ in instructions]
    require(addresses == list(range(start, end, 4)),
            "disassembly window is incomplete or outside reviewed bounds")
    require(all(op not in (".long", ".word", ".inst", "<unknown>")
                for _, op in instructions), "disassembly contains undecoded instructions")
    return len(instructions)


def verify_lldb_disassembly(text, diagnostics, start, end):
    """Reject tool errors, but not C++ exception names in decoded comments."""
    count = validate_disassembly(text, start, end)
    # Only verified addressed instruction lines may have their symbol comment
    # removed. Commands, other output and stderr retain the fail-closed check.
    transcript = re.sub(
        r'(^.*\[0x[0-9a-fA-F]+\]\s+<[^>]*>:[ \t]+[^;\n]*);[^\n]*',
        r'\1', text, flags=re.M)
    lowered = (transcript + diagnostics).lower()
    require('error:' not in lowered and 'fatal:' not in lowered,
            'lldb reported an inspection error')
    return count


def write_exclusive(path, data):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        raise


def package(folder, record):
    record_path = folder / "record.json"
    write_exclusive(record_path, json.dumps(record, indent=2, sort_keys=True) + "\n")
    files = [p for p in sorted(folder.iterdir()) if p.is_file()]
    hashes = {p.name: sha256(p) for p in files}
    manifest = folder / "SHA256.json"
    write_exclusive(manifest, json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    files.append(manifest)
    archive = folder.with_suffix(".zip")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as output:
        for path in files:
            output.write(path, path.name)
    os.chmod(archive, 0o600)
    with zipfile.ZipFile(archive) as check:
        require(check.testzip() is None, "collector ZIP integrity failed")
        require(set(check.namelist()) == {p.name for p in files},
                "collector ZIP inventory mismatch")
        archived = json.loads(check.read("SHA256.json"))
        require(archived == hashes, "collector ZIP hash manifest mismatch")
        for name, digest in hashes.items():
            require(hashlib.sha256(check.read(name)).hexdigest() == digest,
                    "collector ZIP payload hash mismatch")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", choices=tuple(REVIEWS), default="search-abi")
    parser.add_argument("--output-parent", type=Path,
                        default=ROOT / "build-ae-hot-loader")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.exit(2, "BLOCKED: Stage C1 resource collector requires macOS.\n")
    try:
        commit = source_identity()
        profile_agrees()
        windows = review_windows(args.review)
        names = tuple(dict.fromkeys(name for _, name, _, _ in windows))
        parent = args.output_parent.absolute()
        expected_parent = (ROOT / "build-ae-hot-loader").absolute()
        require(parent == expected_parent, "output parent must be the owned build directory")
        parent.mkdir(mode=0o700, exist_ok=True)
        require(not parent.is_symlink() and parent.is_dir() and parent.stat().st_uid == os.getuid(),
                "owned build directory is unsafe")
        parent = parent.resolve(strict=True)
        observed = {name: validate_input(*INPUTS[name]) for name in names}
        prefix = "resource-abi-" if args.review == "search-abi" else "resource-" + args.review + "-"
        folder = Path(tempfile.mkdtemp(prefix=prefix + uuid.uuid4().hex[:8] + "-",
                                       dir=parent))
        os.chmod(folder, 0o700)
        outputs = {}
        ownership = {}
        publication = {}
        for name in names:
            path, _ = INPUTS[name]
            nm, nm_err = run_tool(["/usr/bin/nm", "-arch", "arm64", "-n", "-m", str(path)])
            require(not nm_err.strip(), "nm produced unexpected diagnostics")
            symbols = select_symbols(nm, args.review)
            write_exclusive(folder / (name + "-symbols.txt"), symbols)
        for label, name, start, end in windows:
            path, _ = INPUTS[name]
            script = lldb_script(path, start, end)
            write_exclusive(folder / (label + "-inspect.lldb"), script)
            disassembly, diagnostics = run_tool(
                ["/usr/bin/xcrun", "lldb", "--no-lldbinit", "--batch",
                 "--source", str(folder / (label + "-inspect.lldb"))],
                timeout=60)
            instruction_count = verify_lldb_disassembly(disassembly, diagnostics, start, end)
            if args.review == 'publication':
                publication[label] = verify_publication(disassembly, label, start, end)
            if args.review == 'ownership':
                ownership[label] = verify_ownership(disassembly, label, start, end)
            write_exclusive(folder / (label + "-disassembly.txt"), disassembly)
            if diagnostics:
                write_exclusive(folder / (label + "-stderr.txt"), diagnostics)
            outputs[label] = {
                "path": str(path), "sha256_before": observed[name],
                "window_start": hex(start), "window_end": hex(end),
                "decoded_instructions": instruction_count,
            }
        data_outputs = {}
        for label, name, start, count in DATA_WINDOWS.get(args.review, ()):
            require(name in names, "data image not included in review identity")
            script = lldb_data_script(INPUTS[name][0], start, count)
            script_path = folder / (label + "-inspect.lldb")
            write_exclusive(script_path, script)
            output, diagnostics = run_tool(
                ["/usr/bin/xcrun", "lldb", "--no-lldbinit", "--batch", "--source", str(script_path)],
                timeout=60)
            require("error:" not in (output + diagnostics).lower() and
                    "fatal:" not in (output + diagnostics).lower(), "lldb reported a data inspection error")
            values = validate_data(output, start, count)
            write_exclusive(folder / (label + "-data.txt"), output)
            if diagnostics:
                write_exclusive(folder / (label + "-stderr.txt"), diagnostics)
            data_outputs[label] = {"image": name, "start": hex(start), "word_count": len(values),
                                   "interpretation": "file-backed serialized words, not runtime pointers"}
        if args.review == "lifecycle":
            fixups, diagnostics = run_tool(
                ["/usr/bin/xcrun", "dyld_info", "-arch", "arm64", "-fixup_chains", str(INPUTS["PLUG"][0])])
            require(not diagnostics.strip() and
                    re.search(r"pointer_format:\s+6 \(DYLD_CHAINED_PTR_64_OFFSET\)", fixups),
                    "reviewed PLUG fixup format was not confirmed")
            write_exclusive(folder / "PLUG-fixup-chains.txt", fixups)
        after = {name: validate_input(*INPUTS[name]) for name in names}
        require(observed == after, "input files changed during collection")
        record = {
            "schema": "AEHL-C1-RESOURCE-ABI-1",
            "scope": "offline-bounded-resource-" + args.review + "-only",
            "review": args.review,
            "source_commit": commit,
            "live_ae_operation": "NOT RUN",
            "plugin_scan": "NOT RUN",
            "inputs": outputs,
            "data_windows": data_outputs,
        }
        if args.review == 'publication':
            record['publication_evidence'] = publication
            record['missing_effect_route'] = 'placeholder-only-not-real-plugin-loading'
            record['native_registration_ABI'] = 'UNKNOWN'
            record['isolation_from_general_plugin_state'] = 'NOT PROVEN'
            record['registration_apply_render'] = 'NOT RUN'
        if args.review == 'ownership':
            record['ownership_evidence'] = ownership
            record['actual_record_identities'] = 'NOT OBSERVED'
            record['allocation_lifetime_quiescence'] = 'NOT PROVEN'
            record['safe_repeat_invocation'] = 'NOT PROVEN'
        archive = package(folder, record)
        print("PASS: bounded offline " + args.review + " evidence only; Adobe calls=0")
        print("Report: " + str(archive))
        print("Report SHA-256: " + sha256(archive))
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        parser.exit(2, "BLOCKED: " + str(error) + "\n")


if __name__ == "__main__":
    main()
