#!/usr/bin/env python3
"""Generate Agent metadata from Git; never infer runtime identity from disk bytes."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args], check=True, capture_output=True,
        text=True, timeout=15,
    ).stdout.strip()


def make_identity(root: Path, env: dict[str, str]) -> dict:
    commit = git(root, "rev-parse", "HEAD")
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Expected a full Git commit")
    if env.get("GITHUB_SHA") and env["GITHUB_SHA"] != commit:
        raise ValueError("GITHUB_SHA differs from checked-out source")
    clean = not git(root, "status", "--porcelain", "--untracked-files=normal")
    if not clean and (env.get("CI") == "true" or env.get("AEHL_ALLOW_DIRTY") != "1"):
        raise ValueError("Commit source first; dirty experiments require AEHL_ALLOW_DIRTY=1 outside CI")
    build_id = env.get("PACKAGE_BUILD_ID", f"local-{commit[:12]}-{'clean' if clean else 'dirty'}")
    if not re.fullmatch(r"[A-Za-z0-9._-]{1,128}", build_id):
        raise ValueError("Invalid PACKAGE_BUILD_ID")
    target = env.get("TARGET", "")
    version = env.get("CARGO_PKG_VERSION", "")
    if target != "aarch64-apple-darwin" or not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?", version):
        raise ValueError("Expected version and aarch64-apple-darwin target")
    # The lock must belong to Git, not be an accidentally generated local file.
    git(root, "ls-files", "--error-unmatch", "agent/Cargo.lock", "core/Cargo.lock")
    lock = root / "agent/Cargo.lock"
    if lock.is_symlink():
        raise ValueError("Dependency lock must not be a symlink")
    return {
        "schema_version": 1,
        "component": "agent",
        "git_commit": commit,
        "build_id": build_id,
        "source_clean": clean,
        "target": target,
        "version": version,
        "loader_path_id": "ordinary-discovery-v1",
        "dependency_lock_sha256": hashlib.sha256(lock.read_bytes()).hexdigest(),
    }


def cargo_lines(root: Path, env: dict[str, str]) -> list[str]:
    record = make_identity(root, env)
    lines = ["cargo:rustc-env=AEHL_AGENT_IDENTITY=" + json.dumps(record, sort_keys=True, separators=(",", ":"))]
    for field in ("build_id", "git_commit", "target", "version"):
        lines.append(f"cargo:rustc-env=AEHL_AGENT_{field.upper()}={record[field]}")
    lines.append("cargo:rustc-env=AEHL_AGENT_SOURCE_CLEAN=" + str(record["source_clean"]).lower())
    # Track the commit as well as source, including detached HEAD and worktrees.
    paths = git(root, "ls-files", "-z").split("\0")
    for special in ("HEAD", "index", "packed-refs"):
        paths.append(git(root, "rev-parse", "--git-path", special))
    try:
        ref = git(root, "symbolic-ref", "-q", "HEAD")
    except subprocess.CalledProcessError:
        ref = ""  # Detached checkout: HEAD itself contains the commit.
    if ref:
        paths.append(git(root, "rev-parse", "--git-path", ref))
    for path in sorted(set(paths)):
        if not path:
            continue
        if any(char in path for char in "\r\n"):
            raise ValueError("Newlines in source paths are not supported")
        absolute = Path(path) if Path(path).is_absolute() else root / path
        lines.append("cargo:rerun-if-changed=" + str(absolute))
    for name in ("PACKAGE_BUILD_ID", "GITHUB_SHA", "CI", "AEHL_ALLOW_DIRTY"):
        lines.append("cargo:rerun-if-env-changed=" + name)
    return lines


def main() -> None:
    try:
        root = Path(__file__).resolve().parent.parent
        print("\n".join(cargo_lines(root, dict(os.environ))))
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        sys.exit(f"Agent build identity error: {exc}")


if __name__ == "__main__":
    main()
