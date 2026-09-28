#!/usr/bin/env python3
"""Exercise an isolated Agent dylib's metadata exports; never invoke its AE entrypoint."""
from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import sys


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def getter(library, name: str):
    function = getattr(library, name)
    function.argtypes = [ctypes.c_void_p, ctypes.c_size_t]
    function.restype = ctypes.c_int
    return function


def exercise(function) -> bytes:
    require(function(None, 4096) == -1, "NULL output not rejected")
    sentinel = ctypes.create_string_buffer(b"XXX", 4)
    require(function(sentinel, 0) == -1 and sentinel.raw == b"XXX\0", "zero-capacity buffer modified")
    require(function(sentinel, 1) == -2 and sentinel.raw == b"\0XX\0", "short-buffer contract violated")
    output = ctypes.create_string_buffer(4096)
    require(function(output, len(output)) == 0, "metadata/path getter failed")
    result = output.value
    require(bool(result) and len(result) < len(output) - 1, "empty or unterminated result")
    exact = ctypes.create_string_buffer(len(result))
    require(function(exact, len(exact)) == -2 and exact[0] == b"\0", "truncated result accepted")
    full = ctypes.create_string_buffer(len(result) + 1)
    for _ in range(3):
        require(function(full, len(full)) == 0 and full.value == result, "result changed across calls")
    return result


def verify(binary: Path, commit: str, build_id: str, lock: Path) -> dict:
    binary = binary.resolve(strict=True)
    digest = hashlib.sha256(binary.read_bytes()).hexdigest()
    library = ctypes.CDLL(str(binary))
    record = json.loads(exercise(getter(library, "AEHotLoader_AgentBuildIdentity")))
    expected = {
        "schema_version": 1, "component": "agent", "git_commit": commit,
        "build_id": build_id, "source_clean": True,
        "target": "aarch64-apple-darwin", "version": "0.1.0",
        "loader_path_id": "ordinary-discovery-v1",
        "dependency_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
    }
    require(record == expected, "loaded metadata differs from expected clean source")
    image_path = exercise(getter(library, "AEHotLoader_AgentImagePath")).decode("utf-8")
    require(Path(image_path).resolve(strict=True) == binary, "getter belongs to another loaded image")
    require(hashlib.sha256(binary.read_bytes()).hexdigest() == digest, "binary changed during check")
    return {
        "status": "PASS", "scope": "standalone-macOS-dylib-not-AE",
        "identity": record, "binary_sha256": digest, "loaded_image_path": image_path,
        "getters": 2, "calls_per_getter": 8,
        "host_entrypoint_called": False, "live_ae_status": "NOT RUN",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("binary", type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--build-id", required=True)
    parser.add_argument("--lock", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.exit(1, "This standalone native test requires macOS\n")
    try:
        record = verify(args.binary, args.commit, args.build_id, args.lock)
        with args.output.open("x", encoding="utf-8") as stream:
            json.dump(record, stream, sort_keys=True, indent=2)
            stream.write("\n")
    except (OSError, ValueError, AttributeError) as exc:
        parser.exit(1, f"Agent identity check failed: {exc}\n")
    print("PASS: both loaded Agent identity getters; no AE entrypoint called")


if __name__ == "__main__":
    main()
