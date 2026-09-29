"""Build isolated registration-only fixtures; does not install or contact AE."""
import hashlib
import argparse
import json
from pathlib import Path
import plistlib
import subprocess
import struct
import uuid


def run(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)


def pascal(value):
    data = value.encode("ascii")
    if len(data) > 255:
        raise ValueError("PiPL string too long")
    return bytes([len(data)]) + data


def pipl(name, match):
    properties = [
        ("kind", b"eFKT"), ("name", pascal(name)),
        ("catg", pascal("AE Hot Loader Diagnostic")),
        ("ma64", pascal("EffectMain")),
        ("ePVR", struct.pack(">HH", 2, 0)),
        ("eSVR", struct.pack(">HH", 13, 29)),
        ("eVER", struct.pack(">I", 0x8001)),
        ("eINF", b"\0\0"), ("eGLO", struct.pack(">I", 0)),
        ("eGL2", struct.pack(">I", 0)), ("eMNA", pascal(match)),
        ("aeFL", struct.pack(">I", 0)),
    ]
    data = struct.pack(">II", 0, len(properties))
    for key, value in properties:
        data += b"8BIM" + key.encode("ascii") + struct.pack(">II", 0, len(value))
        data += value + b"\0" * (-len(value) % 4)
    return data


def variants(kind):
    if kind == "dynamic":
        return [(0, "PiPL", "rsrc"), (1, "Dynamic", "rsrc")]
    if kind == "resource":
        return [(0, "Rsrc", "rsrc"), (0, "Flat", "flat")]
    raise ValueError("Unknown pair kind")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True,
                        help='Adobe After Effects SDK Examples directory')
    parser.add_argument('--pair-kind', choices=('dynamic', 'resource'), default='dynamic')
    args = parser.parse_args()
    headers = args.sdk.resolve() / 'Headers'
    if not (headers / 'AE_Effect.h').is_file():
        parser.error('--sdk must contain Headers/AE_Effect.h')
    root = Path(__file__).resolve().parents[2]
    source = Path(__file__).with_name("RegistrationPair.cpp")
    run_id = uuid.uuid4().hex[:12]
    output = root / "build-ae-hot-loader" / (args.pair_kind + "-pair-" + run_id if args.pair_kind == 'resource' else "registration-pair-" + run_id)
    output.mkdir(parents=True, exist_ok=False)
    record = {
        "run_id": run_id, "commit": run("git", "rev-parse", "HEAD").strip(),
        "source_state": run("git", "status", "--porcelain"),
        "compiler": run("clang++", "--version"),
        "sdk": run("xcrun", "--show-sdk-version").strip(),
        "ae_sdk_headers": str(headers),
        "ae_effect_header_sha256": hashlib.sha256((headers / 'AE_Effect.h').read_bytes()).hexdigest(),
        "scope": "registration only; do not apply or render", "probes": [],
        "pair_kind": args.pair_kind,
    }
    for dynamic, label, representation in variants(args.pair_kind):
        name = "AEHL " + label + " " + run_id
        match = "AEHL." + label + "." + run_id
        stem = "AEHLPair" + label + run_id
        bundle = output / (stem + ".plugin")
        contents = bundle / "Contents"
        (contents / "MacOS").mkdir(parents=True)
        (contents / "Resources").mkdir()
        (contents / "Info.plist").write_bytes(plistlib.dumps({
            "CFBundleExecutable": stem, "CFBundleName": name,
            "CFBundleIdentifier": "com.os3kov.AEHotLoader.Pair." + label + run_id,
            "CFBundlePackageType": "eFKT", "CFBundleSignature": "FXTC",
            "CFBundleVersion": "1", "CFBundleInfoDictionaryVersion": "6.0",
        }))
        resource = output / (stem + ".r")
        data = pipl(name, match)
        resource.write_text("data 'PiPL' (16000) {\n" + "\n".join(
            '$"' + data[i:i+32].hex() + '"' for i in range(0, len(data), 32)
        ) + "\n};\n")
        if representation == "rsrc":
            run("Rez", "-useDF", str(resource), "-o",
                str(contents / "Resources" / (stem + ".rsrc")))
        else:
            (contents / "Resources" / "16000.PiPL").write_bytes(data)
        binary = contents / "MacOS" / stem
        command = ["clang++", "-std=c++17", "-arch", "arm64", "-bundle",
                   '-I' + str(headers), '-I' + str(headers / 'SP'),
                   "-fvisibility=hidden", "-Wall", "-Wextra", "-Werror",
                   "-DDYNAMIC_REGISTRATION=" + str(dynamic),
                   '-DPROBE_NAME="' + name + '"', '-DPROBE_MATCH="' + match + '"',
                   str(source), "-o", str(binary)]
        run(*command)
        unsigned_hash = hashlib.sha256(binary.read_bytes()).hexdigest()
        run("codesign", "--force", "--sign", "-", str(bundle))
        run("codesign", "--verify", "--strict", str(bundle))
        exports = run("nm", "-arch", "arm64", "-gU", str(binary))
        assert "_EffectMain" in exports
        assert ("_PluginDataEntryFunction2" in exports) == bool(dynamic)
        record["probes"].append({"name": name, "match": match,
            "resource_representation": representation,
            "pipl_sha256": hashlib.sha256(data).hexdigest(),
            "unsigned_binary_sha256": unsigned_hash,
            "bundle": bundle.name, "command": command, "exports": exports,
            "files": {str(p.relative_to(bundle)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in sorted(bundle.rglob("*")) if p.is_file()}})
    (output / "manifest.json").write_text(json.dumps(record, indent=2) + "\n")
    print(output)


if __name__ == "__main__":
    main()
