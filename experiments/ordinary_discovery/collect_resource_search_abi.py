#!/usr/bin/env python3
"""Collect only the missing Stage C1 PLUG_Search ABI evidence from pinned files.

Offline/file-only: never launches or attaches to After Effects and never loads
Adobe code. Captures two bounded arm64 disassembly windows plus selected symbols.
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
    "aelib": (0x63914, 0x63A70),
    "PLUG": (0x8A6C, 0x8C20),
}
INPUTS = {
    "aelib": (
        APP / "Contents/Frameworks/aelib.framework/Versions/A/aelib",
        "f6124504c8eea332ef257bf1111e6db656c2e07bb57a7b178ec775020ba5407f",
    ),
    "PLUG": (
        APP / "Contents/Frameworks/PLUG.dylib",
        "12f2493892c915dae2361beb2982d8e2c66022574f148cc0097df6966e941b22",
    ),
}
SYMBOL_WANTED = re.compile(r"(PLUG_Search|Egg_PlugSearch|SearchStatFunc)")


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


def lldb_script(path, start, end):
    value = str(path)
    require(not any(c in value for c in ('"', "\\", "\n", "\r", "\x00")),
            "unsafe input path")
    require(0 < start < end <= start + 4096 and start % 4 == 0 and end % 4 == 0,
            "invalid bounded disassembly window")
    return "\n".join([
        "settings set target.load-cwd-lldbinit false",
        "settings set target.load-script-from-symbol-file false",
        'target create --no-dependents --arch arm64 "' + value + '"',
        "disassemble --start-address 0x%x --end-address 0x%x" % (start, end),
        "quit",
        "",
    ])


def run_tool(argv, *, input_text=None, timeout=45):
    result = subprocess.run(
        argv, input=input_text, text=True, stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
        env=dict(os.environ, LC_ALL="C"), check=False)
    require(result.returncode == 0, "offline inspection tool failed")
    require(len(result.stdout.encode()) <= MAX_OUTPUT and len(result.stderr.encode()) <= MAX_OUTPUT,
            "offline inspection output exceeded limit")
    return result.stdout, result.stderr


def select_symbols(text):
    selected = [line for line in text.splitlines() if SYMBOL_WANTED.search(line)]
    require(selected, "expected resource-search symbols were not found")
    return "\n".join(selected) + "\n"


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
    parser.add_argument("--output-parent", type=Path,
                        default=ROOT / "build-ae-hot-loader")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.exit(2, "BLOCKED: Stage C1 ABI collector requires macOS.\n")
    try:
        commit = source_identity()
        profile_agrees()
        parent = args.output_parent.absolute()
        expected_parent = (ROOT / "build-ae-hot-loader").absolute()
        require(parent == expected_parent, "output parent must be the owned build directory")
        parent.mkdir(mode=0o700, exist_ok=True)
        require(not parent.is_symlink() and parent.is_dir() and parent.stat().st_uid == os.getuid(),
                "owned build directory is unsafe")
        parent = parent.resolve(strict=True)
        observed = {name: validate_input(path, digest)
                    for name, (path, digest) in INPUTS.items()}
        folder = Path(tempfile.mkdtemp(prefix="resource-abi-" + uuid.uuid4().hex[:8] + "-",
                                       dir=parent))
        os.chmod(folder, 0o700)
        outputs = {}
        for name in ("aelib", "PLUG"):
            path, _ = INPUTS[name]
            nm, nm_err = run_tool(["/usr/bin/nm", "-arch", "arm64", "-n", "-m", str(path)])
            require(not nm_err.strip(), "nm produced unexpected diagnostics")
            symbols = select_symbols(nm)
            write_exclusive(folder / (name + "-symbols.txt"), symbols)
            start, end = WINDOWS[name]
            script = lldb_script(path, start, end)
            write_exclusive(folder / (name + "-inspect.lldb"), script)
            disassembly, diagnostics = run_tool(
                ["/usr/bin/xcrun", "lldb", "--no-lldbinit", "--batch",
                 "--source", str(folder / (name + "-inspect.lldb"))],
                timeout=60)
            lowered = (disassembly + diagnostics).lower()
            require("error:" not in lowered and "fatal:" not in lowered,
                    "lldb reported an inspection error")
            write_exclusive(folder / (name + "-disassembly.txt"), disassembly)
            if diagnostics:
                write_exclusive(folder / (name + "-stderr.txt"), diagnostics)
            outputs[name] = {
                "path": str(path), "sha256_before": observed[name],
                "window_start": hex(start), "window_end": hex(end),
            }
        after = {name: validate_input(path, digest)
                 for name, (path, digest) in INPUTS.items()}
        require(observed == after, "input files changed during collection")
        record = {
            "schema": "AEHL-C1-RESOURCE-ABI-1",
            "scope": "offline-bounded-resource-search-abi-only",
            "source_commit": commit,
            "live_ae_operation": "NOT RUN",
            "plugin_scan": "NOT RUN",
            "inputs": outputs,
        }
        archive = package(folder, record)
        print("PASS: bounded offline ABI evidence only; Adobe calls=0")
        print("Report: " + str(archive))
        print("Report SHA-256: " + sha256(archive))
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        parser.exit(2, "BLOCKED: " + str(error) + "\n")


if __name__ == "__main__":
    main()
