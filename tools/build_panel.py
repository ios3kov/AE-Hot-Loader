#!/usr/bin/env python3
"""Stamp the ScriptUI panel with the same clean source/Build ID as its Agent."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import subprocess
import tomllib

from agent_build_identity import make_identity

MARKER = 'var PANEL_IDENTITY = null; // @AEHL_PANEL_IDENTITY@'


def render(source: str, agent: dict) -> str:
    """Only insert validated literals; no runtime manifest evaluation or global override."""
    if source.count(MARKER) != 1:
        raise ValueError("Expected exactly one unstamped panel marker")
    if agent.get("component") != "agent" or agent.get("source_clean") is not True:
        raise ValueError("Panel packaging requires a clean Agent identity")
    for field, pattern in (
        ("git_commit", r"[0-9a-f]{40}"), ("build_id", r"[A-Za-z0-9._-]{1,128}"),
        ("version", r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?"),
    ):
        if not isinstance(agent.get(field), str) or not re.fullmatch(pattern, agent[field]):
            raise ValueError(f"Invalid panel identity field: {field}")
    if agent.get("target") != "aarch64-apple-darwin":
        raise ValueError("Unsupported panel package target")
    record = {key: agent[key] for key in ("git_commit", "build_id", "source_clean", "target", "version")}
    record.update(schema_version=1, component="panel")
    return source.replace(MARKER, "var PANEL_IDENTITY = " + json.dumps(record, sort_keys=True, separators=(",", ":")) + ";")


def build(root: Path, destination: Path, environment: dict[str, str]) -> None:
    version = tomllib.loads((root / "agent/Cargo.toml").read_text(encoding="utf-8"))["package"]["version"]
    env = {**environment, "TARGET": "aarch64-apple-darwin", "CARGO_PKG_VERSION": version}
    identity = make_identity(root, env)
    source = (root / "ui/AE Hot Loader.jsx").read_text(encoding="utf-8")
    result = render(source, identity)
    # Exclusive creation also rejects a pre-existing symlink or source path.
    with destination.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(result)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    try:
        build(Path(__file__).resolve().parent.parent, args.output, dict(os.environ))
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        parser.exit(1, f"Panel package identity failed: {exc}\n")
    print("Panel generated from clean source with package Build ID")


if __name__ == "__main__":
    main()
