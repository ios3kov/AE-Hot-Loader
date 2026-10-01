"""Read-only check of a single embedded-resource fixture's owned scan root."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(manifest_path, owned_base):
    manifest_path = manifest_path.absolute()
    owned_base = owned_base.absolute()
    if (owned_base.is_symlink() or not owned_base.is_dir() or
            manifest_path.parent.parent != owned_base or
            manifest_path.parent.is_symlink()):
        raise ValueError("fixture is not a direct, non-symlink child of the owned base")
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("manifest must be a regular file")
    manifest_stat = manifest_path.stat()
    if manifest_stat.st_uid != os.getuid() or manifest_stat.st_nlink != 1 or \
            (manifest_stat.st_mode & 0o777) != 0o600:
        raise ValueError("manifest must be owned/private")
    fixture_stat = manifest_path.parent.stat()
    if fixture_stat.st_uid != os.getuid() or (fixture_stat.st_mode & 0o777) != 0o700:
        raise ValueError("fixture directory must be owned/private")
    record = json.loads(manifest_path.read_text())
    if (record.get("pair_kind") != "embedded" or record.get("scan_root") != "scan-root" or
            record.get("fixture_scope") != "single-owned-embedded-root"):
        raise ValueError("not a single embedded fixture manifest")
    if not re.fullmatch(r"[0-9a-f]{12}", str(record.get("run_id", ""))):
        raise ValueError("invalid fresh fixture run id")
    if not re.fullmatch(r"[0-9a-f]{40}", str(record.get("commit", ""))):
        raise ValueError("invalid fixture source commit")
    if record.get("source_state"):
        raise ValueError("fixture was built from a dirty source tree")
    probes = record.get("probes")
    if not isinstance(probes, list) or len(probes) != 1:
        raise ValueError("expected exactly one fixture")
    probe = probes[0]
    if probe.get("resource_representation") != "rsrc":
        raise ValueError("fixture is not an embedded resource")
    root = manifest_path.parent / "scan-root"
    if root.is_symlink() or not root.is_dir():
        raise ValueError("scan root is missing or is a symlink")
    root_stat = root.stat()
    if root_stat.st_uid != os.getuid() or (root_stat.st_mode & 0o777) != 0o700:
        raise ValueError("scan root must be owned/private")
    bundle_name = probe.get("bundle")
    if not isinstance(bundle_name, str) or bundle_name != "scan-root/" + Path(bundle_name).name or not bundle_name.endswith(".plugin"):
        raise ValueError("bundle path escapes the scan root")
    bundle = manifest_path.parent / bundle_name
    if bundle.is_symlink() or not bundle.is_dir():
        raise ValueError("bundle is missing or is a symlink")
    if set(root.iterdir()) != {bundle}:
        raise ValueError("scan root contains extra entries")
    actual = {}
    for path in bundle.rglob("*"):
        if path.is_symlink():
            raise ValueError("symlink in fixture")
        if path.is_file():
            actual[str(path.relative_to(bundle))] = sha256(path)
        elif not path.is_dir():
            raise ValueError("non-regular fixture entry")
    match = probe.get("match")
    if (not isinstance(match, str) or
            not re.fullmatch(r"AEHL\.Embedded\.[0-9a-f]{12}", match) or
            match == "AEHL.Embedded.88019a1a01a7"):
        raise ValueError("fixture identity is not fresh embedded identity")
    expected = probe.get("files")
    if not isinstance(expected, dict) or actual != expected:
        raise ValueError("fixture file inventory or SHA-256 mismatch")
    resources = [name for name in actual if name.endswith(".rsrc")]
    if len(resources) != 1 or any(name.endswith(".PiPL") for name in actual):
        raise ValueError("expected one embedded .rsrc and no flat .PiPL")
    return {"status": "PASS", "build_id": record["run_id"],
            "source_commit": record["commit"], "match": probe["match"],
            "scan_root": str(root), "manifest_sha256": sha256(manifest_path),
            "files": actual}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--owned-base", type=Path, default=Path(__file__).resolve().parents[2] / "build-ae-hot-loader")
    args = parser.parse_args()
    try:
        result = verify(args.manifest, args.owned_base)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.exit(1, "FAIL: " + str(error) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
