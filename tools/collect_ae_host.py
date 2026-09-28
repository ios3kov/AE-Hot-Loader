#!/usr/bin/env python3
"""Read-only AE host preflight; never reload plug-ins, render or install anything.

Run on the Mac with AE already open. Output stays local. The only host-side
writes are unique report files and one get_build_identity bridge request.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
import uuid

EXPECTED = {
    "agent_build_id": "native-36483421984-1",
    "agent_git_commit": "04fea7060c7ef7ebc4a315b5c39364850287e294",
    "agent_source_clean": "true", "agent_target": "aarch64-apple-darwin",
    "agent_version": "0.1.0",
}
RSMB = ("Smart Motion Blur 3.x", "RS Motion Blur Pro A 3.x", "RS Motion Blur Pro Vectors 3.x")
MAX_REPLY = 16384
SNAPSHOT = r'''(function () {
    var cfg = __CONFIG__;
    function quote(s) {
        return '"' + String(s).replace(/[\\"\u0000-\u001f\u2028\u2029]/g, function (c) {
            return "\\u" + ("0000" + c.charCodeAt(0).toString(16)).slice(-4);
        }) + '"';
    }
    function stringify(v) {
        if (v === null) return "null";
        if (typeof v === "string") return quote(v);
        if (typeof v === "boolean" || typeof v === "number") return String(v);
        var a = [], k, i;
        if (v instanceof Array) {
            for (i = 0; i < v.length; i++) a.push(stringify(v[i]));
            return "[" + a.join(",") + "]";
        }
        for (k in v) if (v.hasOwnProperty(k)) a.push(quote(k) + ":" + stringify(v[k]));
        return "{" + a.join(",") + "}";
    }
    var data = {schema_version: 1, run_id: cfg.run_id, phase: cfg.phase,
                captured_at_ms: (new Date()).getTime(), status: "BLOCKED"};
    var project = app.project;
    try {
        if (data.captured_at_ms > cfg.deadline_ms) throw Error("Expired probe; no host reads performed");
        data.host_version = String(app.version);
        data.host_build = String(app.buildNumber);
        if (!project) throw Error("No project object; project was not created");
        // Never record project names, paths, layer content or preferences.
        data.project = {items: project.numItems, revision: project.revision,
                        saved: project.file !== null, dirty: typeof project.dirty === "boolean" ? project.dirty : null,
                        queued: project.renderQueue.numItems,
                        rendering: project.renderQueue.rendering};
        var list = app.effects, names = [], seen = {}, n, i;
        if (!list || typeof list.length !== "number") throw Error("Effect registry unavailable");
        for (i = 0; i < list.length; i++) {
            n = list[i].matchName;
            if (typeof n !== "string" || !n || seen["$" + n]) throw Error("Invalid or duplicate effect identity");
            seen["$" + n] = true;
            names.push(n);
        }
        // Keep the complete registry private; report only the relevant effects and count.
        data.effect_count = names.length;
        data.rsmb = [];
        for (i = 0; i < cfg.rsmb.length; i++)
            data.rsmb.push({match_name: cfg.rsmb[i], present: seen["$" + cfg.rsmb[i]] === true});
        data.status = "PASS";
    } catch (e) { data.reason = String(e).slice(0, 400); }
    var output = new File(cfg.output);
    if (output.exists) throw Error("Refusing to overwrite probe result");
    output.encoding = "UTF-8";
    output.lineFeed = "Unix";
    if (!output.open("w")) throw Error("Probe cannot write its result; scripting file access may be disabled");
    var wrote = false, closed = false;
    try { wrote = output.write(stringify(data) + "\n"); } finally { closed = output.close(); }
    if (!wrote || !closed) throw Error("Incomplete probe result");
})();
'''


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


def parse_reply(raw: bytes) -> dict[str, str]:
    text = raw.decode("utf-8-sig")
    if not raw or len(raw) > MAX_REPLY or not text.endswith("\n") or "\0" in text:
        raise Blocked("Incomplete or oversized Agent reply")
    result = {}
    for line in text.splitlines():
        if not line:
            continue
        key, separator, value = line.partition("=")
        if not separator or not re.fullmatch(r"[a-z_]+", key) or key in result:
            raise Blocked("Malformed or duplicate Agent reply field")
        result[key] = value
    if result.get("version") != "1" or result.get("status") not in ("success", "error", "noop"):
        raise Blocked("Unsupported Agent reply")
    return result


def agent_query(bridge: Path, run_id: str, timeout: float = 10) -> dict[str, str]:
    if not re.fullmatch(r"aehl-preflight-[0-9a-f]{32}", run_id):
        raise Blocked("Invalid diagnostic Run ID")
    no_symlinks(bridge)
    if not bridge.is_dir():
        raise Blocked("Agent bridge directory is absent; nothing was installed")
    request, response = bridge / "request.txt", bridge / "response.txt"
    if request.exists() or response.exists() or request.is_symlink() or response.is_symlink():
        raise Blocked("Existing bridge request/response preserved; query not sent")
    temp = bridge / ("probe-" + run_id + ".tmp")
    body = ("version=1\ncommand=get_build_identity\nrequest_id=" + run_id +
            "\ntimestamp=" + str(int(time.time() * 1000)) + "\n").encode("ascii")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(body)
            stream.flush()
            os.fsync(stream.fileno())
        # Atomic no-replace publication. A concurrent request wins, never overwritten.
        os.link(temp, request)
    finally:
        temp.unlink()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            info = response.lstat()
            reply = parse_reply(read_regular(response))
            if reply.get("request_id") == run_id:
                # Consume only our response, never a stale/foreign response.
                current = response.lstat()
                if (current.st_dev, current.st_ino, current.st_mtime_ns, current.st_size) != (
                        info.st_dev, info.st_ino, info.st_mtime_ns, info.st_size):
                    raise Blocked("Agent response changed during read; preserved")
                response.unlink()
                return reply
        except FileNotFoundError:
            pass
        time.sleep(0.1)
    # The Agent may still process the request. Never cancel/delete it on timeout.
    raise Blocked("Agent query timed out; pending state preserved, no plug-in scan requested")


def find_host(ps_output: str) -> tuple[int, Path]:
    hosts = []
    for line in ps_output.splitlines():
        m = re.fullmatch(r"\s*(\d+)\s+(.+)", line)
        if m and ".app/Contents/MacOS/" in m[2] and Path(m[2]).name == "After Effects":
            hosts.append((int(m[1]), Path(m[2].split(".app/Contents/MacOS/", 1)[0] + ".app")))
    if len(hosts) != 1:
        raise Blocked("Exactly one running After Effects is required; no app was started or stopped")
    return hosts[0]


def process_list() -> str:
    return subprocess.run(["/bin/ps", "-axo", "pid=,comm="], check=True,
                          capture_output=True, text=True, timeout=5).stdout


def process_start(pid: int) -> str:
    result = subprocess.run(["/bin/ps", "-p", str(pid), "-o", "lstart="],
                            check=True, capture_output=True, text=True, timeout=5).stdout.strip()
    if not result:
        raise Blocked("AE process no longer exists")
    return result


def applescript(app: Path) -> str:
    text = str(app)
    if any(ord(c) < 32 for c in text):
        raise Blocked("Invalid application path")
    quoted = '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return ("on run argv\nif application " + quoted + ' is not running then error "AE is not running"\n'
            "with timeout of 20 seconds\ntell application " + quoted +
            "\nDoScriptFile (POSIX file (item 1 of argv))\nend tell\nend timeout\nend run")


def snapshot(app: Path, folder: Path, run_id: str, phase: str) -> dict:
    result = folder / (phase + ".json")
    config = {"run_id": run_id, "phase": phase, "output": str(result), "rsmb": RSMB,
              "deadline_ms": int(time.time() * 1000) + 25000}
    source = SNAPSHOT.replace("__CONFIG__", json.dumps(config, ensure_ascii=True))
    script = folder / (phase + ".jsx")
    with script.open("x", encoding="utf-8") as stream:
        stream.write(source)
    subprocess.run(["/usr/bin/osascript", "-e", applescript(app), str(script)],
                   check=True, capture_output=True, text=True, timeout=25)
    raw = read_regular(result)
    data = json.loads(raw.decode("utf-8-sig"))
    if (data.get("schema_version") != 1 or data.get("run_id") != run_id
            or data.get("phase") != phase or data.get("status") != "PASS"
            or type(data.get("captured_at_ms")) not in (int, float)
            or data["captured_at_ms"] > config["deadline_ms"]
            or data["captured_at_ms"] < config["deadline_ms"] - 25000):
        raise Blocked("Snapshot failed or belongs to a different/expired run")
    return data


def identity_check(reply: dict[str, str]) -> dict:
    mismatches = [key for key, value in EXPECTED.items() if reply.get(key) != value]
    return {"status": "PASS" if reply.get("status") == "success" and not mismatches else "FAIL",
            "expected": EXPECTED, "observed": {key: reply.get(key) for key in EXPECTED},
            "mismatched_fields": mismatches, "scope": "resident Agent bridge identity, not ScriptUI or render"}


def collect(folder: Path, run_id: str) -> dict:
    report = {"schema_version": 1, "run_id": run_id, "collection_status": "BLOCKED",
              "scope": "existing-process-read-only-preflight",
              "collector_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "checks": {stage: {"status": "NOT RUN"} for stage in
                         ("agent_identity", "registry", "project_unchanged", "cold_start",
                          "panel_roundtrip", "apply", "render", "late_registration")},
              "limitations": ["No installation, restart, plug-in reload, application or render is performed.",
                              "A matching Build ID is not proof of full runtime correctness.",
                              "Use an idle host; simultaneous bridge clients are not supported."]}
    if sys.platform != "darwin":
        report["reason"] = "Live preflight requires the Mac running After Effects"
        return report
    try:
        pid, app = find_host(process_list())
        start = process_start(pid)
        report["host_pid"] = pid
        report["host_start"] = start
        before = snapshot(app, folder, run_id, "before")
        report["before"] = before
        if not re.fullmatch(r"25\.6(?:\.0)?(?:x\d+)?", before["host_version"]):
            raise Blocked("Host version is outside the AE 25.6 research target")
        if before["project"]["rendering"]:
            raise Blocked("AE is rendering; diagnostic bridge request not sent")
        if find_host(process_list()) != (pid, app) or process_start(pid) != start:
            raise Blocked("AE process changed before Agent query")
        try:
            reply = agent_query(Path.home() / "Library/Application Support/AE Hot Loader/bridge", run_id)
            report["checks"]["agent_identity"] = identity_check(reply)
        except (OSError, ValueError, Blocked) as exc:
            report["checks"]["agent_identity"] = {"status": "BLOCKED", "reason": str(exc)[:400]}
        after = snapshot(app, folder, run_id, "after")
        report["after"] = after
        if find_host(process_list()) != (pid, app) or process_start(pid) != start:
            raise Blocked("AE process changed; observations do not form a single-host test")
        report["checks"]["registry"] = {"status": "PASS" if all(x["present"] for x in after["rsmb"]) else "FAIL",
                                          "scope": "presence of the three exact RSMB match names only"}
        unchanged = before["project"] == after["project"]
        report["checks"]["project_unchanged"] = {
            "status": "PASS" if unchanged else "FAIL",
            "scope": "item count, revision, saved/dirty flags and render queue; not full project integrity"}
        report["collection_status"] = "COMPLETE"
    except (OSError, ValueError, KeyError, Blocked, subprocess.SubprocessError) as exc:
        # Do not copy osascript stderr/project data into a shareable report.
        report["reason"] = (type(exc).__name__ + ": " + str(exc).replace(str(Path.home()), "~"))[:600]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-parent", type=Path, default=Path.home() / "Downloads")
    args = parser.parse_args()
    args.output_parent = args.output_parent.absolute()
    no_symlinks(args.output_parent)
    if not args.output_parent.is_dir():
        parser.error("Output parent must already be a real directory")
    run_id = "aehl-preflight-" + uuid.uuid4().hex
    folder = args.output_parent / run_id
    folder.mkdir(mode=0o700)
    report = collect(folder, run_id)
    with (folder / "report.json").open("x", encoding="utf-8") as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
    print("Report: " + str(folder / "report.json"))
    print("Collection: " + report["collection_status"] + "; apply/render/cold-start: NOT RUN")
    return 0 if report["collection_status"] == "COMPLETE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
