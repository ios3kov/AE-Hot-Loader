#!/usr/bin/env python3
"""Inspect existing AE bridge files without contacting After Effects.

Only a new private report directory is created. No commands are sent and no
bridge files are changed, consumed or deleted. Stored replies are not proof
of the resident Agent identity. Run on the Mac where the files reside.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import uuid

EXPECTED = {
    "agent_build_id": "native-36483421984-1",
    "agent_git_commit": "04fea7060c7ef7ebc4a315b5c39364850287e294",
    "agent_source_clean": "true", "agent_target": "aarch64-apple-darwin",
    "agent_version": "0.1.0",
}
MAX_REPLY = 16384


class Blocked(RuntimeError):
    """A missing prerequisite, not a successful AE test."""


def read_regular(path: Path, limit: int = MAX_REPLY) -> bytes:
    """Bounded read without following a final symlink or opening a pipe/device."""
    fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_size > limit:
            raise Blocked("Unexpected file type, owner or size")
        data = os.read(fd, limit + 1)
        if len(data) > limit:
            raise Blocked("Response exceeds size limit")
        return data
    finally:
        os.close(fd)


def no_symlinks(path: Path) -> None:
    for part in (path, *path.parents):
        if part.is_symlink():
            raise Blocked("Symlinked diagnostic paths are not supported")


def inspect_bridge_file(path: Path) -> dict:
    """Summarize one existing record without consuming it or disclosing messages."""
    record = {"present": None, "status": "BLOCKED"}
    try:
        no_symlinks(path.parent)
        try:
            before = path.lstat()
        except FileNotFoundError:
            return {"present": False, "status": "NOT RUN"}
        record["present"] = True
        if not stat.S_ISREG(before.st_mode) or before.st_uid != os.getuid():
            raise Blocked("Unexpected bridge file type or owner")
        raw = read_regular(path)
        after = path.lstat()
        # A successful read never establishes that a queued request is idle/stale.
        fields = ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns", "st_mode", "st_uid")
        if any(getattr(before, key) != getattr(after, key) for key in fields):
            raise Blocked("Bridge file changed during inspection")
        text = raw.decode("utf-8-sig")
        if not text or not text.endswith("\n") or "\0" in text:
            raise Blocked("Incomplete bridge record")
        values = {}
        for line in text.splitlines():
            if not line:
                continue
            key, separator, value = line.partition("=")
            if not separator or not re.fullmatch(r"[a-z_]{1,64}", key) or key in values:
                raise Blocked("Malformed or duplicate bridge field")
            if any(ord(char) < 32 for char in value):
                raise Blocked("Control characters in bridge record")
            values[key] = value
        request_id = values.get("request_id", "")
        if values.get("version") != "1" or not 1 <= len(request_id.encode("utf-8")) <= 128:
            raise Blocked("Unsupported or incomplete bridge record")
        summary = {"version": "1", "request_id_sha256": hashlib.sha256(request_id.encode("utf-8")).hexdigest()}
        if path.name == "request.txt":
            command = values.get("command")
            summary["command"] = command if command in ("get_build_identity", "reload_plugins") else "unrecognized"
        else:
            status = values.get("status")
            summary["status"] = status if status in ("success", "error", "noop") else "unrecognized"
            patterns = {
                "agent_build_id": r"[A-Za-z0-9][A-Za-z0-9._-]{0,95}",
                "agent_git_commit": r"[0-9a-f]{40}",
                "agent_source_clean": r"true|false",
                "agent_target": r"[A-Za-z0-9_-]{1,80}",
                "agent_version": r"[0-9]+\.[0-9]+\.[0-9]+(?:[-+][A-Za-z0-9.-]+)?",
            }
            identity = {key: value for key, value in values.items()
                        if key in patterns and len(value) <= 96 and re.fullmatch(patterns[key], value)}
            summary["stored_agent_identity"] = identity
            summary["identity_fields_invalid"] = [key for key in patterns if key in values and key not in identity]
            summary["matches_reference_record"] = all(identity.get(key) == value for key, value in EXPECTED.items())
            summary["identity_scope"] = "stored response only; may be stale; NOT resident verification"
        record.update(status="PASS", bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                      modified_at_ns=before.st_mtime_ns, record=summary)
    except Blocked as exc:
        record["reason"] = str(exc)
    except (OSError, UnicodeError):
        # Never echo file content or filesystem paths in a shareable report.
        record["reason"] = "Bridge file could not be read safely"
    return record


def inspect_bridge(bridge: Path, run_id: str) -> dict:
    """Passive filesystem inspection: no AE calls, request publication or cleanup."""
    report = {
        "schema_version": 1, "run_id": run_id,
        "scope": "passive-bridge-files-only", "collection_status": "BLOCKED",
        "collector_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "expected_reference": EXPECTED,
        "live_agent_identity": {"status": "NOT RUN", "reason": "Existing files cannot establish the resident Agent"},
        "request_execution_state": "UNKNOWN",
        "limitations": ["No commands sent, no AE access, no bridge files changed or removed.",
                        "File presence, matching IDs and age do not prove completion or safe deletion.",
                        "Snapshots of the two files are not atomic; simultaneous clients remain unsupported.",
                        "Messages, raw request IDs, unknown fields and filesystem paths are omitted."],
    }
    try:
        no_symlinks(bridge)
        if not bridge.is_dir():
            raise Blocked("Bridge directory is absent; nothing was created there")
        report["files"] = {name: inspect_bridge_file(bridge / name) for name in ("request.txt", "response.txt")}
        files = report["files"]
        if any(item["status"] == "BLOCKED" for item in files.values()):
            report["disposition"] = "INSPECTION_BLOCKED"
            return report
        present = [name for name, item in files.items() if item["present"]]
        report["disposition"] = {(): "EMPTY_AT_SNAPSHOT", ("request.txt",): "REQUEST_PRESENT",
                                 ("response.txt",): "RESPONSE_PRESENT",
                                 ("request.txt", "response.txt"): "REQUEST_AND_RESPONSE_PRESENT"}[tuple(present)]
        if len(present) == 2:
            report["stored_request_ids_match"] = (files["request.txt"]["record"]["request_id_sha256"] ==
                                                   files["response.txt"]["record"]["request_id_sha256"])
        report["collection_status"] = "COMPLETE"
    except Blocked as exc:
        report["reason"] = str(exc)
    except OSError:
        report["reason"] = "Bridge directory could not be inspected safely"
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-parent", type=Path, default=Path.home() / "Downloads")
    args = parser.parse_args()
    args.output_parent = args.output_parent.absolute()
    try:
        no_symlinks(args.output_parent)
        if not args.output_parent.is_dir():
            parser.error("Output parent must already be a real directory")
        run_id = "aehl-bridge-" + uuid.uuid4().hex
        folder = args.output_parent / run_id
        folder.mkdir(mode=0o700)
        report = inspect_bridge(Path.home() / "Library/Application Support/AE Hot Loader/bridge", run_id)
        fd = os.open(folder / "report.json", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
            stream.write("\n")
    except (Blocked, OSError):
        parser.error("Cannot safely create the local diagnostic report")
    print("Report: " + str(folder / "report.json"))
    print("Collection: " + report["collection_status"] + "; resident identity: NOT RUN; no commands sent")
    return 0 if report["collection_status"] == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
