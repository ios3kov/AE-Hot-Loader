"""Correlate one AE minidump with one owned late-scan run, read-only."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess
import uuid


CHAIN = (
    ("pipl_url_read", "ML::PiPL::LoadFromResource", "__CFURL const*"),
    ("internal_pipl_read", "ML::PluginImpl::InternalLoadPiPLs", ""),
    ("pipl_fallback", "ML::PluginImpl::LoadPiPLs", ""),
    ("pipl_dispatch", "ML::PluginImpl::GetPiPLs", ""),
    ("host_load", "ML::LoadPlugins", ""),
    ("agent_load", "AEHotLoaderAgent", "LoadPluginFolder"),
)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dump", type=Path, required=True)
    parser.add_argument("--run-folder", type=Path, required=True)
    parser.add_argument("--output-parent", type=Path, required=True)
    parser.add_argument("--fixture-marker", required=True)
    args = parser.parse_args()
    repo = Path(__file__).resolve().parents[2]
    dump = args.dump.resolve(strict=True)
    run_folder = args.run_folder.resolve(strict=True)
    owned = (repo / "build-ae-hot-loader").resolve()
    if not run_folder.is_relative_to(owned):
        parser.error("run folder must belong to build-ae-hot-loader")
    if not dump.is_file() or dump.suffix != ".dmp":
        parser.error("dump must be an existing .dmp file")
    if not re.fullmatch(r"AEHLPair[A-Za-z0-9]{1,80}", args.fixture_marker):
        parser.error("fixture marker must be a bounded owned fixture name")
    baseline_path = run_folder / "absent-baseline.json"
    result_path = run_folder / "result.json"
    baseline = json.loads(baseline_path.read_text())
    result = json.loads(result_path.read_text())
    expected_pid = baseline["host_pid"]
    if not isinstance(expected_pid, int) or expected_pid <= 0:
        parser.error("baseline lacks a valid host PID")
    with dump.open("rb") as stream:
        header = stream.read(32)
    if len(header) != 32 or header[:4] != b"MDMP":
        parser.error("not a minidump header")
    dump_epoch = struct.unpack_from("<I", header, 20)[0]
    command = ["xcrun", "lldb", "-b", "--no-lldbinit", "-c", str(dump),
               "-o", "process status", "-o", "thread backtrace -c 25",
               "-o", "quit"]
    completed = subprocess.run(command, capture_output=True, text=True,
                               timeout=60)
    output = completed.stdout + completed.stderr
    pid_match = re.search(r"\bProcess (\d+) stopped\b", output)
    observed_pid = int(pid_match.group(1)) if pid_match else None
    has_fault = "stop reason = EXC_BAD_ACCESS" in output
    frames = {}
    for label, first, second in CHAIN:
        frames[label] = any(first in line and second in line
                            for line in output.splitlines()
                            if "frame #" in line)
    dump_bytes = dump.read_bytes()
    marker_present = args.fixture_marker.encode("ascii") in dump_bytes
    baseline_epoch = baseline_path.stat().st_mtime
    result_epoch = result_path.stat().st_mtime
    time_correlated = baseline_epoch - 2 <= dump_epoch <= result_epoch + 2
    pass_link = (completed.returncode == 0 and observed_pid == expected_pid
                 and has_fault and time_correlated and all(frames.values()))
    record = {
        "analysis_run_id": "crash-link-" + uuid.uuid4().hex,
        "collector_source_commit": subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip(),
        "collector_source_state": subprocess.check_output(
            ["git", "-C", str(repo), "status", "--porcelain"], text=True),
        "original_run_id": run_folder.name,
        "original_source_commit": result["source"],
        "original_build_id": result["build_id"],
        "original_gate_status": result["status"],
        "baseline_sha256": sha256(baseline_path),
        "result_sha256": sha256(result_path),
        "dump_sha256": hashlib.sha256(dump_bytes).hexdigest(),
        "dump_utc": datetime.fromtimestamp(dump_epoch, timezone.utc).isoformat(),
        "expected_pid": expected_pid,
        "observed_pid": observed_pid,
        "time_correlated": time_correlated,
        "fault_observed": has_fault,
        "stack_chain": frames,
        "fixture_name_present_in_dump": marker_present,
        "fixture_name_is_faulting_url": "BLOCKED",
        "specific_root_cause": "BLOCKED",
        "lldb_exit_code": completed.returncode,
        "crash_correlation": "PASS" if pass_link else "FAIL",
        "scope": "PID/time/stack correlation only; no plugin attribution from a string",
    }
    output_parent = args.output_parent.resolve(strict=True)
    if not output_parent.is_relative_to(owned):
        parser.error("output must stay under build-ae-hot-loader")
    output_folder = output_parent / record["analysis_run_id"]
    output_folder.mkdir(mode=0o700)
    (output_folder / "record.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))
    return 0 if pass_link else 1


if __name__ == "__main__":
    raise SystemExit(main())
