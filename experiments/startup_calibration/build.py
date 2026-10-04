"""Build and test two isolated calibration bundles offline. Never installs or runs AE.

Requires a clean research checkout and the selected SDK. Artifacts are diagnostic
preparation, not an installable hot-loader release or host acceptance evidence.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import plistlib
import subprocess
import tempfile
import uuid

ROOT = Path(__file__).resolve().parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checks = load("calibration_source_checks", ROOT / "tools/run_research_checks.py")
pipl = load("calibration_pipl", ROOT / "experiments/ordinary_discovery/build_registration_pair.py")


def run(*command):
    # Existing owned-child runner enforces deadline, output bound and process-group cleanup.
    with tempfile.TemporaryDirectory(prefix="aehl-calibration-command-") as directory:
        log = Path(directory) / "command.log"
        result = checks.run_command(list(command), ROOT, log, timeout=120)
        data = log.read_bytes()
        if result["status"] != "PASS":
            raise subprocess.CalledProcessError(result.get("exit_code") or 1, command, output=data)
        return data.decode("utf-8", errors="strict")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sdk_files(root):
    paths = sorted(p for parent in ("Headers", "Resources") for p in (root / parent).rglob("*") if p.is_file())
    if any(p.is_symlink() for p in paths):
        raise ValueError("SDK contains symlinks")
    return {p.relative_to(root).as_posix(): sha(p) for p in paths}


def cpp(value):
    # JSON string literal is a C++ literal here; never used as shell escaping.
    return json.dumps(value, ensure_ascii=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sdk", type=Path, required=True, help="SDK 25.6_61 Examples directory")
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--prospective-host", type=Path, help="future authorized host executable; this argument performs no host operation")
    parser.add_argument("--prospective-module", type=Path, help="future exact observer executable location; no installation")
    args = parser.parse_args()
    if bool(args.prospective_host) != bool(args.prospective_module):
        parser.error("prospective host and observer location must be supplied together")
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        parser.error("offline native artifact builder requires macOS arm64")
    source = checks.source_identity(ROOT, args.expected_commit)
    sdk = args.sdk.resolve(strict=True); headers = sdk / "Headers"
    pins = sdk_files(sdk)
    if pins.get("Headers/AE_GeneralPlug.h") != "30d12ec3eb5af1a902c7414053b1be1da0204b226e0b1cdc71272be1e137000c" or \
       pins.get("Headers/AE_Effect.h") != "5432df9bb447cefce2f96c1477d6beccd4686b7236d460c803beab76dae1d537":
        parser.error("selected SDK header identity does not match")
    run_id = uuid.uuid4().hex
    output = ROOT / "build-ae-hot-loader" / ("startup-calibration-" + run_id)
    output.mkdir(parents=True, exist_ok=False, mode=0o700); output.chmod(0o700)
    control = output / "control"; control.mkdir(mode=0o700); control.chmod(0o700)
    marker = "AEHLMarker" + run_id[:12]; observer = "AEHLCalibration" + run_id[:12]
    match = "AEHL.Marker." + run_id
    build = source["commit"] + ":" + run_id
    token = uuid.uuid4().hex
    seed = int(run_id[:6], 16)
    bundles = []
    observer_module = output / (observer + ".plugin") / "Contents/MacOS" / observer
    config = {"calibration_build": build, "calibration_token": token,
              "calibration_executable": str(output / "unconfigured-owned-host"),
              "calibration_module": str(observer_module), "calibration_control": str(control),
              "calibration_match": match, "calibration_fixture": "AEHL Calibration " + run_id[:12]}
    if args.prospective_host:
        if not args.prospective_host.is_absolute() or not args.prospective_module.is_absolute():
            parser.error("prospective paths must be absolute")
        config["calibration_executable"] = str(args.prospective_host.resolve(strict=True))
        config["calibration_module"] = str(args.prospective_module.resolve())
    (output / "CalibrationConfig.hpp").write_text("#pragma once\n" + "".join(
        "static constexpr const char* " + key + " = " + cpp(value) + ";\n" for key, value in config.items()) +
        "static constexpr unsigned calibration_seed = " + str(seed) + "u;\n")
    (output / "CalibrationConfig.hpp").chmod(0o600)
    common = ["clang++", "-std=c++17", "-arch", "arm64", "-mmacosx-version-min=12.0", "-Wall", "-Wextra", "-Werror",
              "-I" + str(headers), "-I" + str(headers / "SP"), "-I" + str(output)]
    for stem, source_name, exports in [
        (marker, "MarkerEffect.cpp", ["_EffectMain", "_AEHL_MarkerBuildIdentity"]),
        (observer, "CalibrationObserver.cpp", ["_EntryPointFunc", "_AEHL_CalibrationBuildIdentity"])]:
        bundle = output / (stem + ".plugin"); contents = bundle / "Contents"
        (contents / "MacOS").mkdir(parents=True); (contents / "Resources").mkdir()
        (contents / "Info.plist").write_bytes(plistlib.dumps({
            "CFBundleExecutable": stem, "CFBundleName": stem, "CFBundleIdentifier": "com.os3kov.AEHotLoader.Calibration." + stem,
            "CFBundlePackageType": "eFKT" if stem == marker else "AEgx", "CFBundleSignature": "FXTC",
            "CFBundleVersion": "1", "LSRequiresCarbon": True}))
        resource = output / (stem + ".r")
        if stem == marker:
            data = pipl.pipl("AEHL Marker " + run_id[:12], match)
            resource.write_text("data 'PiPL' (16000) {\n" + "\n".join(
                '$"' + data[i:i+32].hex() + '"' for i in range(0, len(data), 32)) + "\n};\n")
        else:
            resource.write_text('#include "AE_General.r"\nresource \'PiPL\' (16000) {{\n'
                'Kind { AEGP }, Name { "' + stem + '" }, Category { "General Plugin" },\n'
                'CodeMacARM64 { "EntryPointFunc" }\n}};\n')
        run("Rez", "-useDF", "-i", str(sdk / "Resources"), str(resource), "-o", str(contents / "Resources" / (stem + ".rsrc")))
        binary = contents / "MacOS" / stem
        command = common + ["-bundle", "-fvisibility=hidden", "-Wl," + ",".join("-exported_symbol," + name for name in exports),
                  "-DAEHL_BUILD_ID=" + cpp(build), "-DAEHL_MARKER_SEED=" + str(seed) + "u",
                  str(Path(__file__).with_name(source_name)), "-o", str(binary)]
        compile_log = run(*command)
        run("codesign", "--force", "--sign", "-", str(bundle)); run("codesign", "--verify", "--strict", str(bundle))
        actual_exports = run("nm", "-arch", "arm64", "-gU", str(binary))
        if {line.split()[-1] for line in actual_exports.splitlines()} != set(exports):
            raise RuntimeError("unexpected exported ABI")
        bundles.append({"bundle": bundle.relative_to(output).as_posix(), "binary_sha256": sha(binary),
                        "build_id": build, "command": command, "compile_log": compile_log,
                        "exports": actual_exports, "dependencies": run("otool", "-L", str(binary)),
                        "load_commands": run("otool", "-l", str(binary)),
                        "files": {p.relative_to(bundle).as_posix(): sha(p) for p in sorted(bundle.rglob("*")) if p.is_file()}})
    results = {}
    tests = [("adapter", ROOT / "tests/startup_marker_adapter.cpp"), ("inert", ROOT / "tests/startup_calibration_inert.cpp")]
    for label, test in tests:
        binary = output / (label + "-test")
        command = common + ["-fsanitize=address,undefined", "-fno-omit-frame-pointer", str(test)]
        if label == "adapter":
            command += [str(Path(__file__).with_name("MarkerEffect.cpp"))]
        run(*(command + ["-o", str(binary)]))
        marker_binary = output / (marker + ".plugin") / "Contents/MacOS" / marker
        results[label] = run(str(binary), *([str(observer_module), token] if label == "inert" else [str(marker_binary), build]))
        if label == "adapter":
            frame = bytes.fromhex(results[label].split("FRAME_ARGB8_HEX=", 1)[1].splitlines()[0])
            oracle = load("calibration_artifact_oracle", Path(__file__).with_name("oracle.py"))
            results["exact_marker_pixel_oracle"] = oracle.compare(frame, 5, 3, seed, stride=32)
            if results["exact_marker_pixel_oracle"]["pixel_status"] != "PASS":
                raise RuntimeError("signed marker output does not match independent oracle")
    if list(control.iterdir()):
        raise RuntimeError("inert test unexpectedly touched control journal")
    if checks.source_identity(ROOT, args.expected_commit) != source or sdk_files(sdk) != pins:
        raise RuntimeError("source/SDK changed during build")
    record = {"schema": "AEHL-STARTUP-CALIBRATION-1", "source": source, "build_id": build,
              "sdk_files": pins, "compiler": run("clang++", "--version"), "system_sdk": run("xcrun", "--show-sdk-version"),
              "run_id": run_id, "match_name": match, "seed": seed, "token": token, "config": config,
              "bundles": bundles, "offline_tests": results,
              "observer_host_binding": "PROSPECTIVE_ONLY_NOT_AUTHORIZATION" if args.prospective_host else "UNCONFIGURED_INERT",
              "install": "NOT RUN", "AE_load": "NOT RUN", "AE_render": "NOT RUN", "late_registration": "NOT RUN",
              "scope": "offline diagnostic preparation; not a release or live approval"}
    manifest = output / "manifest.json"; manifest.write_text(json.dumps(record, indent=2) + "\n"); manifest.chmod(0o600)
    print(output)
    print("manifest_sha256=" + sha(manifest))


if __name__ == "__main__":
    main()
