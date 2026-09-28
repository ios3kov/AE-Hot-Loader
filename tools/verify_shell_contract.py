#!/usr/bin/env python3
import pathlib
import re
import sys

if len(sys.argv) != 5:
    raise SystemExit(
        "usage: verify_shell_contract.py BUILD_RS LIB_RS SHELL_CPP RELOADER_CPP"
    )

build = pathlib.Path(sys.argv[1]).read_text()
lib = pathlib.Path(sys.argv[2]).read_text()
shell = pathlib.Path(sys.argv[3]).read_text()
reloader = pathlib.Path(sys.argv[4]).read_text()

def required(pattern: str, text: str, label: str) -> str:
    m = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if not m:
        raise SystemExit(f"missing {label}")
    return m.group(1)

# PiPL registration metadata must match the shell callback exactly.
name = required(r'Property::Name\("([^"]*)"\)', build, "PiPL name")
category = required(r'Property::Category\("([^"]*)"\)', build, "PiPL category")
match_name = required(
    r'Property::AE_Effect_Match_Name\("([^"]*)"\)', build, "PiPL match name"
)
support = required(
    r'Property::AE_Effect_Support_URL\("([^"]*)"\)', build, "PiPL support URL"
)
major = required(
    r'PF_PLUG_IN_VERSION:\s*u16\s*=\s*(\d+)', build, "PiPL API major"
)
minor = required(
    r'PF_PLUG_IN_SUBVERS:\s*u16\s*=\s*(\d+)', build, "PiPL API minor"
)

callback_start = shell.find("const A_Err result = in_callback(")
callback_end = shell.find(");", callback_start)
if callback_start < 0 or callback_end < 0:
    raise SystemExit("missing/unterminated shell registration callback")
callback = shell[callback_start:callback_end]
literals = re.findall(
    r'reinterpret_cast<const std::uint8_t\*>\("([^"]*)"\)',
    callback,
)
expected_literals = [name, match_name, category, "EffectMain", support]
if literals[:5] != expected_literals:
    raise SystemExit(
        "shell registration metadata drift:\n"
        f"  expected={expected_literals!r}\n"
        f"  actual={literals[:5]!r}"
    )

shell_major = required(r'kApiMajor\s*=\s*(\d+)', shell, "shell API major")
shell_minor = required(r'kApiMinor\s*=\s*(\d+)', shell, "shell API minor")
if (shell_major, shell_minor) != (major, minor):
    raise SystemExit(
        f"shell API version drift: PiPL={major}.{minor} shell={shell_major}.{shell_minor}"
    )

# Implementation-facing contract.
impl_protocol = required(
    r'HOT_RELOAD_IMPLEMENTATION_ABI:\s*u32\s*=\s*(\d+)',
    lib,
    "implementation protocol ABI",
)
impl_state = required(
    r'HOT_RELOAD_STATE_ABI:\s*u64\s*=\s*(\d+)',
    lib,
    "implementation state ABI",
)
impl_key = required(
    r'HOT_RELOAD_IMPLEMENTATION_KEY:\s*&str\s*=\s*"([^"]+)"',
    lib,
    "implementation key",
)

shell_protocol = required(
    r'kImplementationAbi\s*=\s*(\d+)', shell, "shell implementation ABI"
)
shell_state = required(
    r'kImplementationStateAbi\s*=\s*(\d+)', shell, "shell state ABI"
)
shell_key = required(
    r'kImplementationKey\s*=\s*"([^"]+)"', shell, "shell implementation key"
)

if (impl_protocol, impl_state, impl_key) != (
    shell_protocol,
    shell_state,
    shell_key,
):
    raise SystemExit(
        "implementation/shell contract drift:\n"
        f"  implementation={(impl_protocol, impl_state, impl_key)!r}\n"
        f"  shell={(shell_protocol, shell_state, shell_key)!r}"
    )

if impl_protocol != "2":
    raise SystemExit(
        f"expected implementation protocol ABI 2, got {impl_protocol}"
    )

# Shell discovery ABI must match the Agent before Agent calls the function.
shell_discovery = required(r'kShellAbi\s*=\s*(\d+)', shell, "shell discovery ABI")
agent_discovery = required(
    r'kShellAbi\s*=\s*(\d+)', reloader, "Agent shell discovery ABI"
)
if shell_discovery != agent_discovery:
    raise SystemExit(
        f"shell discovery ABI drift: shell={shell_discovery} Agent={agent_discovery}"
    )

for symbol in [
    "AEHotLoader_ImplementationRuntimeABI",
    "AEHotLoader_ImplementationABI",
    "AEHotLoader_ImplementationStateABI",
    "AEHotLoader_ImplementationKey",
    "AEHotLoader_ImplementationLabel",
    "AEHotLoader_SetGeneration",
]:
    if symbol not in lib:
        raise SystemExit(f"missing implementation export source: {symbol}")

for symbol in [
    "AEHotLoader_ShellReload",
    "AEHotLoader_ShellABI",
    "AEHotLoader_ShellKey",
]:
    if symbol not in shell:
        raise SystemExit(f"missing shell export source: {symbol}")

print(
    "shell contract: PASS "
    f"name={name!r} match={match_name!r} api={major}.{minor} "
    f"implABI={impl_protocol} stateABI={impl_state} key={impl_key!r} "
    f"shellABI={shell_discovery}"
)
