#!/usr/bin/env python3
"""Record and verify signed package bytes; no claim about AE runtime behavior."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re

NAME = "artifact-manifest.json"


def payload(root: Path) -> dict[str, str]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("Package root must be a real directory")
    files = {}
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise ValueError("Symlinks are not accepted in this package")
        if path.is_file() and path.relative_to(root).as_posix() != NAME:
            files[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif not path.is_file() and not path.is_dir():
            raise ValueError("Unsupported package entry")
    if not files:
        raise ValueError("Package is empty")
    return files


def create(root: Path, commit: str, build_id: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("A full Git commit SHA is required")
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", build_id):
        raise ValueError("Invalid build ID")
    record = {
        "schema_version": 1,
        "git_commit": commit,
        "build_id": build_id,
        "scope": "internal-build-not-release-approved",
        "runtime_identity_verified": False,
        "files": payload(root),
    }
    # Never overwrite a manifest from another build, or include its own hash.
    with (root / NAME).open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    return record


def verify(root: Path, expected_commit: str, expected_build_id: str) -> dict:
    actual = payload(root)  # Reject symlinks before opening the manifest.
    record = json.loads((root / NAME).read_text(encoding="utf-8"))
    if not isinstance(record, dict) or set(record) != {
        "schema_version", "git_commit", "build_id", "scope", "runtime_identity_verified", "files"
    }:
        raise ValueError("Unexpected manifest schema")
    if (type(record["schema_version"]) is not int or record["schema_version"] != 1
            or record["git_commit"] != expected_commit
            or record["build_id"] != expected_build_id
            or record["runtime_identity_verified"] is not False
            or record["scope"] != "internal-build-not-release-approved"):
        raise ValueError("Manifest identity or scope mismatch")
    # Compare complete relative-path maps; never open paths supplied by a manifest.
    if record["files"] != actual:
        raise ValueError("Package bytes or file inventory changed")
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("create", "verify"))
    parser.add_argument("root", type=Path)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--build-id", required=True)
    args = parser.parse_args()
    try:
        action = create if args.mode == "create" else verify
        record = action(args.root, args.commit, args.build_id)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"manifest error: {exc}\n")
    print(f"{args.mode}: {len(record['files'])} payload files; {record['build_id']}")


if __name__ == "__main__":
    main()
