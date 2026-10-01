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
}


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
            lowered = (disassembly + diagnostics).lower()
            require("error:" not in lowered and "fatal:" not in lowered,
                    "lldb reported an inspection error")
            instruction_count = validate_disassembly(disassembly, start, end)
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
        archive = package(folder, record)
        print("PASS: bounded offline " + args.review + " evidence only; Adobe calls=0")
        print("Report: " + str(archive))
        print("Report SHA-256: " + sha256(archive))
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        parser.exit(2, "BLOCKED: " + str(error) + "\n")


if __name__ == "__main__":
    main()
