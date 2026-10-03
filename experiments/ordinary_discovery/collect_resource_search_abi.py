#!/usr/bin/env python3
"""Collect bounded Stage C1 search, ownership and effect evidence from pinned files.

Offline/file-only: never launches or attaches to After Effects and never loads
Adobe code. Captures fixed arm64 disassembly windows plus selected symbols.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid
import zipfile

ROOT = Path(__file__).resolve().parents[2]
APP = Path("/Applications/Adobe After Effects 2025/Adobe After Effects 2025.app")
PROFILE = ROOT / "experiments/ordinary_discovery/AE256ResourceProfile.hpp"
FILE_ONLY_PROFILE = ROOT / "experiments/ordinary_discovery/AE256ProviderFactoryFiles.json"
MAX_OUTPUT = 2 * 1024 * 1024
WINDOWS = {
    # SearchStatFunc + Egg_PlugSearch, and all of PLUG_Search through its
    # return/unwind paths. Ends are the next defined text symbols in these pins.
    "aelib": (0x638CC, 0x63A70),
    "PLUG": (0x8A6C, 0x9028),
}
REVIEWS = {
    "search-abi": tuple((name, name, *bounds) for name, bounds in WINDOWS.items()),
    "cleanup": (
        ("PLUG-install", "PLUG", 0x87E4, 0x8A6C),
        ("PLUG-cleanup", "PLUG", 0xEB20, 0xEC1C),
        ("FLT-birth", "FLT", 0xD7AC, 0xDAE0),
        ("MEE-setup", "MEE", 0x36C58, 0x36DA4),
        ("MEE-scan", "MEE", 0x36DA4, 0x376EC),
        ("MEE-callback", "MEE", 0x376EC, 0x37A00),
        ("MEE-finish", "MEE", 0x37EEC, 0x37F34),
        ("MEE-setdown", "MEE", 0x37F34, 0x38044),
    ),
    "lifecycle": (
        ("PLUG-prep", "PLUG", 0x7DE4, 0x807C),
        ("PLUG-unprep", "PLUG", 0x807C, 0x82B8),
        ("PLUG-unprep-internal", "PLUG", 0x7C74, 0x7D70),
        ("PLUG-state", "PLUG", 0xDFF0, 0xE028),
        ("PLUG-constructor", "PLUG", 0xC9B4, 0xCD74),
        ("MEE-callback", "MEE", 0x376EC, 0x37A00),
        ("MEE-setdown", "MEE", 0x37F34, 0x38044),
    ),
    "publication": (
        ("PLUG-file", "PLUG", 0xF6C0, 0xFA1C),
        ("PLUG-path", "PLUG", 0x6FA8, 0x7150),
        ("FLT-scan", "FLT", 0x8CF98, 0x8D250),
        ("FLT-setup-a", "FLT", 0x8D250, 0x8E250),
        ("FLT-setup-b", "FLT", 0x8E250, 0x8EF8C),
        ("FLT-add-a", "FLT", 0x8B2D4, 0x8C2D4),
        ("FLT-add-b", "FLT", 0x8C2D4, 0x8CC70),
        ("FLT-registry", "FLT", 0x5014, 0x53F0),
        ("FLT-postsetup", "FLT", 0x9284C, 0x92AB8),
        ("FLT-ready", "FLT", 0x146C8, 0x14838),
        ("FLT-lazy-globals", "FLT", 0x5E504, 0x5E764),
        ("FLT-register-lazy", "FLT", 0x99268, 0x993A4),
        ("FLT-if-missing", "FLT", 0x993A4, 0x997E4),
    ),
    "effect-readiness": (
        ("FLT-ready-body", "FLT", 0x5CEA8, 0x5D0DC),
        ("FLT-lazy-setup", "FLT", 0x5D328, 0x5D644),
        ("FLT-unready", "FLT", 0x5D104, 0x5D328),
        ("FLT-setdown", "FLT", 0x5D644, 0x5D7DC),
        ("FLT-global-dispatch", "FLT", 0x906C4, 0x90B7C),
        ("FLT-std-params", "FLT", 0x539EC, 0x53A24),
        ("PLUG-path-ctor", "PLUG", 0xC9B4, 0xCC9C),
        ("PLUG-classref", "PLUG", 0xCC9C, 0xCD74),
        ("PLUG-path-thunk", "PLUG", 0xCD74, 0xCD78),
    ),
    "effect-dispatch": (
        ("FLT-params-setup", "FLT", 0x535AC, 0x539EC),
        ("FLT-dispatch", "FLT", 0x98494, 0x98C80),
        ("FLT-host-dispatch", "FLT", 0x38D60, 0x394A4),
        ("FLT-dispatch-ctor", "FLT", 0x3ACA4, 0x3ADFC),
        ("FLT-dispatch-optional", "FLT", 0x3B080, 0x3B268),
        ("FLT-dispatch-hardware", "FLT", 0x3B268, 0x3B2A8),
        ("FLT-dispatch-machine", "FLT", 0x3B2A8, 0x3B804),
        ("FLT-dispatch-crash", "FLT", 0x3B804, 0x3BA04),
    ),
    "provider-factory": (
        ("PS-ctor", "PluginSupport", 0x4ba6c, 0x4bb34),
        ("PS-dtor", "PluginSupport", 0x4bbd0, 0x4bd14),
        ("PS-init", "PluginSupport", 0x4becc, 0x4c440),
        ("PS-load", "PluginSupport", 0x4c440, 0x4c55c),
        ("PS-free", "PluginSupport", 0x4c55c, 0x4c560),
        ("PS-entry", "PluginSupport", 0x4c568, 0x4c71c),
        ("PS-module", "PluginSupport", 0x4d368, 0x4d394),
        ("TDB-factory", "TDB", 0x599c, 0x59a8),
        ("TDB-get-instance", "TDB", 0x1f014, 0x1f15c),
        ("TDB-register", "TDB", 0x1f15c, 0x1f400),
        ("TDB-unregister-name", "TDB", 0x1f804, 0x1f8c8),
        ("TDB-unregister-factory", "TDB", 0x1fbe4, 0x1fe1c),
        ("TDB-unregister-recursive", "TDB", 0x1fe1c, 0x200f4),
        ("TDB-get-stream", "TDB", 0x20128, 0x20230),
    ),
    "entry-lifetime": (
        ("ASL-load", "ASLFoundation", 0x23b18, 0x23e4c),
        ("ASL-create", "ASLFoundation", 0x241d0, 0x24310),
        ("ASL-ctor", "ASLFoundation", 0x24344, 0x243ac),
        ("ASL-ctor-base", "ASLFoundation", 0x243ac, 0x24404),
        ("ASL-dtor", "ASLFoundation", 0x24404, 0x24450),
        ("ASL-dtor-complete", "ASLFoundation", 0x24450, 0x2449c),
        ("ASL-delete", "ASLFoundation", 0x2449c, 0x244e8),
        ("ASL-proc", "ASLFoundation", 0x24594, 0x24aa4),
        ("ASL-unload-flag", "ASLFoundation", 0x24b3c, 0x24b44),
        ("ASL-last-owner", "ASLFoundation", 0x27ca8, 0x27cc0),
        ("FLT-ctor", "FLT", 0x5cae4, 0x5cbec),
        ("FLT-desc-release", "FLT", 0x5cbec, 0x5cc60),
        ("FLT-ctor-thunk", "FLT", 0x5cc60, 0x5cc64),
        ("FLT-dtor", "FLT", 0x5cc64, 0x5cd3c),
        ("FLT-get-desc", "FLT", 0x5d0dc, 0x5d0f8),
        ("FLT-set-proc", "FLT", 0x5d0f8, 0x5d104),
        ("FLT-set-desc", "FLT", 0x5e26c, 0x5e2f0),
        ("FLT-get-proc", "FLT", 0x5e2f0, 0x5e2fc),
        ("PLUG-load-platform", "PLUG", 0x1087c, 0x10b98),
        ("PLUG-entry", "PLUG", 0x10b98, 0x10dac),
        ("PLUG-unload-platform", "PLUG", 0x10dac, 0x10e6c),
        ("PLUG-unload-plugin", "PLUG", 0x87a0, 0x87a4),
        ("PLUG-desc-dtor", "PLUG", 0xe720, 0xe7f0),
    ),
    "ownership": (
        ("MEE-setup", "MEE", 0x36C58, 0x36DA4),
        ("MEE-scan", "MEE", 0x36DA4, 0x376EC),
        ("MEE-callback", "MEE", 0x376EC, 0x37A00),
        ("MEE-finish", "MEE", 0x37EEC, 0x37F34),
        ("MEE-setdown", "MEE", 0x37F34, 0x38044),
    ),
}
DATA_WINDOWS = {
    "lifecycle": (("PLUG-vtable", "PLUG", 0x14920, 12),),
    "entry-lifetime": (
        ("FLT-vtable", "FLT", 0xd5c70, 14),
        ("ASL-module-vtable", "ASLFoundation", 0x31670, 11),
        ("ASL-owner-vtable", "ASLFoundation", 0x317f8, 7),
    ),
}
# File-relative targets after decoding DYLD_CHAINED_PTR_64_OFFSET rebases.
# Word zero is offset-to-top, not a fixup. These are never live addresses.
ENTRY_TABLE_TARGETS = {
    "FLT-vtable": (0, 0xd60d8, 0x5cd3c, 0x5cd40, 0x5e2f0, 0x5e1c8,
                   0x5e0c8, 0x5e0f4, 0x5e0fc, 0x5d7e4, 0x5dec4, 0x5e120,
                   0x5e12c, 0x5e2fc),
    "ASL-module-vtable": (0, 0x316c8, 0x24450, 0x2449c, 0x28718,
                          0x28ce8, 0x24b44, 0x24f40, 0x24fa8, 0x25220, 0x24f00),
    "ASL-owner-vtable": (0, 0x31830, 0x27c90, 0x27c94, 0x27ca8, 0x27cc0, 0x27d3c),
}
INPUTS = {
    "aelib": (
        APP / "Contents/Frameworks/aelib.framework/Versions/A/aelib",
        "f6124504c8eea332ef257bf1111e6db656c2e07bb57a7b178ec775020ba5407f",
    ),
    "PLUG": (
        APP / "Contents/Frameworks/PLUG.dylib",
        "12f2493892c915dae2361beb2982d8e2c66022574f148cc0097df6966e941b22",
    ),
    "FLT": (
        APP / "Contents/Frameworks/FLT.dylib",
        "227f0688d4272b1c0be2b2066d53b702e2363fca6002f873ea0acdc6a4d01256",
    ),
    "MEE": (
        APP / "Contents/Frameworks/MEE.dylib",
        "18579ae84d541df7d08eda4507a5d3ceed78f2c4385f07c8a222f02255ec7344",
    ),
    "PluginSupport": (
        APP / "Contents/Frameworks/PluginSupport.framework/Versions/A/PluginSupport",
        "4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832",
    ),
}
# Additional pins are offline collector inputs, not a native/live profile extension.
FILE_ONLY_INPUTS = {
    "TDB": (APP / "Contents/Frameworks/TDB.dylib",
            "c40f65989078368f63302050edc42315873dbbd71949324ddc79f01753f2d7d5"),
    "ASLFoundation": (
        APP / "Contents/Frameworks/ASLFoundation.framework/Versions/A/ASLFoundation",
        "f1c3c7256f8a986f39519387511436577a3d65fb9d04a672bbb115c1871a3fe7"),
}
INPUTS.update(FILE_ONLY_INPUTS)
SYMBOL_WANTED = {
    "search-abi": re.compile(r"(PLUG_Search|Egg_PlugSearch|SearchStatFunc)"),
    "cleanup": re.compile(r"(PLUG_InstallScan|PLUGp_DoCleanups|FLT_Birth|"
                          r"SetupGeneralPluginScan|PluginScanFunc|PluginCleanupFunc|"
                          r"CleanupGeneralPluginScan|SetdownGeneralPlugins)"),
    "lifecycle": re.compile(r"(PLUG_PrepRoutine|PLUG_UnprepRoutine|PLUGp_UnprepRoutine|"
                            r"PLUG_RoutineDescPriv|PluginCleanupFunc|SetdownGeneralPlugins)"),
    "publication": re.compile(r"(PLUGp_ScanFile|PLUG_RegisterRoutine|FLT_PLUGScanFunc|"
                              r"FLTp_FiltSetup|FLTp_AddEffect|RegisterNewFilter|"
                              r"FiltPostSetup|ScReadyFilter|DoLazyGlobals|RegisterEffectIfMissing)"),
    "effect-readiness": re.compile(r"(ReadyFilter|UnreadyFilter|DoLazyGlobalSetup|"
                                   r"DoGlobalSetdown|FLTp_DoGlobal|FLTp_GetStdParams|"
                                   r"PLUG_RoutineDescPriv|CreateClassRef)"),
    "effect-dispatch": re.compile(r"(DispatchFilter|FLTp_DoParamsSetup|"
                                  r"U_GenericPluginDispatch|GetCanonicalEffect)"),
    "provider-factory": re.compile(r"(PluginImpl|Get_AE_StreamFactory|"
                                   r"StreamFactory.*(Canonical|UnregisterFactoryFunc))"),
    "entry-lifetime": re.compile(r"(Module.*(Load|Create|ProcAddress|UnloadOnDestroy|[CD][012])|"
                                 r"shared_ptr_pointerIPN3ASL6Module|"
                                 r"FLT_FCSpec.*(RoutineDescH|EffectProc|[CD][012])|"
                                 r"PLUGp_(Load|Unload)PlatRoutine|"
                                 r"PLUG_RoutineDescPriv.*(GetEntryPoint|UnloadPlugin|D2)|"
                                 r"ZTV.*(ASL6Module|FLT_FCSpec))"),
    "ownership": re.compile(r"(SetupGeneralPluginScan|PluginScanFunc|PluginCleanupFunc|"
                            r"CleanupGeneralPluginScan|SetdownGeneralPlugins|vectorI13GeneralPlugin)"),
}

# Addressed instruction checks corroborate the pinned file's ownership flow;
# they never certify actual record identity, lifetime or safe repeated invocation.
OWNERSHIP_ANCHORS = {
    "MEE-setup": {
        0x36c7c: ('adrp', 'x8,217'), 0x36c80: ('add', 'x8,x8,#0xd70'),
        0x36c84: ('ldp', 'x21,x22,[x8]'), 0x36c98: ('sub', 'x22,x22,#0xb0'),
        0x36ccc: ('ldaddal', 'w23,w8,[x8]'), 0x36ce4: ('blr', 'x8'),
        0x36cec: ('ldaddal', 'w23,w8,[x8]'), 0x36d04: ('blr', 'x8'),
        0x36d10: ('str', 'x21,[x8,#0xd78]'),
    },
    "MEE-scan": {
        0x37108: ('bl', '0x9ed98'), 0x371ec: ('adrp', 'x9,216'),
        0x371f0: ('add', 'x9,x9,#0xd78'), 0x371f4: ('ldp', 'x24,x9,[x9]'),
        0x37200: ('str', 'x8,[x24]'), 0x37208: ('str', 'x8,[x24,#0x8]'),
        0x37214: ('mov', 'w9,#0x1'), 0x37218: ('ldadd', 'w9,w8,[x8]'),
        0x3723c: ('add', 'x0,x24,#0x90'), 0x3726c: ('bl', '0x40614'),
        0x3730c: ('strb', 'w8,[x24,#0xa8]'), 0x37310: ('add', 'x0,x24,#0xb0'),
        0x37318: ('str', 'x0,[x27,#0xd78]'),
    },
    "MEE-callback": {
        0x37724: ('adrp', 'x8,216'), 0x37728: ('add', 'x8,x8,#0xd70'),
        0x3772c: ('ldp', 'x21,x24,[x8]'), 0x37768: ('add', 'x21,x21,#0xb0'),
        0x3779c: ('bl', '0x9e900'), 0x377a0: ('cbnz', 'w0,0x37768'),
        0x377a4: ('strb', 'w25,[x21,#0xa8]'), 0x377c0: ('mov', 'x22,x21'),
        0x377c4: ('movi.2d', 'v0,#0000000000000000'),
        0x377c8: ('str', 'q0,[x22,#0x10]!'), 0x377d0: ('stp', 'q0,q0,[x21,#0x20]'),
        0x377d4: ('stp', 'q0,q0,[x21,#0x40]'), 0x377d8: ('stp', 'q0,q0,[x21,#0x60]'),
        0x377dc: ('str', 'q0,[x21,#0x80]'), 0x377f0: ('mov', 'w0,#0x3'),
        0x377fc: ('mov', 'x4,x22'), 0x37800: ('blr', 'x8'),
    },
    "MEE-finish": {
        0x37ef8: ('adrp', 'x8,216'), 0x37efc: ('add', 'x8,x8,#0xd70'),
        0x37f00: ('ldp', 'x19,x20,[x8]'), 0x37f08: ('add', 'x19,x19,#0xb0'),
        0x37f14: ('ldr', 'x8,[x19,#0x80]'), 0x37f1c: ('ldr', 'x0,[x19,#0x10]'),
        0x37f20: ('blr', 'x8'),
    },
    "MEE-setdown": {
        0x37f50: ('ldr', 'x19,[x8,#0x360]'), 0x37f54: ('ldr', 'x20,[x8,#0x368]'),
        0x37f70: ('ldr', 'x8,[x19,#0x58]'), 0x37f7c: ('blr', 'x8'),
        0x37f80: ('ldrb', 'w8,[x19,#0xa8]'), 0x37f88: ('strb', 'wzr,[x19,#0xa8]'),
        0x37f90: ('bl', '0x9eb10'), 0x37f9c: ('add', 'x8,x8,#0xd70'),
        0x37fa0: ('ldp', 'x19,x21,[x8]'), 0x37fb4: ('sub', 'x21,x21,#0xb0'),
        0x37fe8: ('ldaddal', 'w22,w8,[x8]'), 0x38000: ('blr', 'x8'),
        0x38008: ('ldaddal', 'w22,w8,[x8]'), 0x38020: ('blr', 'x8'),
        0x3802c: ('str', 'x19,[x8,#0xd78]'),
    },
}


# File-only publication anchors. The "if missing" entry creates a MissingEffect
# placeholder; none of these checks certifies a usable native registration ABI.
PUBLICATION_ANCHORS = {
    'PLUG-file': {
        0xf750: ('blr', 'x8'),
        0xf770: ('tbnz', 'w26,#0x0,0xf93c'),
        0xf910: ('ldr', 'x2,[sp,#0x30]'),
        0xf91c: ('blr', 'x8'),
    },
    'PLUG-path': {
        0x7010: ('bl', '0xcd74'),
        0x7054: ('add', 'x20,x20,#0x488'),
        0x70b8: ('bl', '0x8560'),
    },
    'FLT-scan': {
        0x8cfb4: ('bl', '0x4208'),
        0x8cfc0: ('cmp', 'w8,#0xe99'),
        0x8cfd0: ('cmp', 'w8,#0xe99'),
        0x8cfe0: ('bl', '0xa5b68'),
        0x8d028: ('bl', '0xa5844'),
        0x8d05c: ('bl', '0xa5b08'),
        0x8d078: ('mov', 'x3,#0x0'),
        0x8d07c: ('mov', 'x4,#0x0'),
        0x8d080: ('mov', 'x5,#0x0'),
        0x8d084: ('bl', '0x8d250'),
    },
    'FLT-setup-a': {
        0x8d2cc: ('bl', '0x5cc60'),
        0x8d300: ('blr', 'x8'),
        0x8d304: ('mov', 'w8,#0x4b54'),
        0x8d308: ('movk', 'w8,#0x6546,lsl#16'),
        0x8d310: ('b.ne', '0x8ddec'),
        0x8df08: ('bl', '0x4a24'),
        0x8df2c: ('tbz', 'w24,#0x0,0x8dfa0'),
        0x8df30: ('cbz', 'x28,0x8eb4c'),
        0x8e05c: ('bl', '0x8b2d4'),
    },
    'FLT-setup-b': {
        0x8e288: ('bl', '0xa5b80'),
        0x8e388: ('bl', '0x5e26c'),
        0x8e3e4: ('bl', '0x9284c'),
        0x8e404: ('bl', '0x8b2d4'),
        0x8e4e0: ('bl', '0xa5b74'),
        0x8e610: ('bl', '0x5e26c'),
        0x8e66c: ('bl', '0x9284c'),
        0x8e68c: ('bl', '0x8b2d4'),
        0x8e70c: ('bl', '0x146c8'),
        0x8e73c: ('bl', '0x9a204'),
        0x8e74c: ('cbnz', 'w19,0x8ec5c'),
    },
    'FLT-add-a': {
        0x8b81c: ('bl', '0x6ea8'),
        0x8b820: ('cbz', 'w0,0x8b834'),
        0x8b82c: ('bl', '0x71a4'),
        0x8b850: ('bl', '0x4c4c'),
        0x8bd80: ('cbz', 'w21,0x8c200'),
        0x8bd8c: ('bl', '0x5014'),
        0x8c04c: ('bl', '0x5854'),
        0x8c06c: ('bl', '0x9a258'),
        0x8c0f4: ('bl', '0x9a258'),
    },
    'FLT-add-b': {
        0x8cc04: ('bl', '0xa5820'),
    },
    'FLT-registry': {
        0x5054: ('bl', '0xa6d44'),
        0x5058: ('ldp', 'x8,x9,[x20,#0x38]'),
        0x5068: ('str', 'x9,[x8]'),
        0x5080: ('ldadd', 'w10,w9,[x9]'),
        0x5094: ('bl', '0x1571c'),
        0x5098: ('str', 'x0,[x20,#0x38]'),
        0x50a8: ('blr', 'x8'),
        0x5254: ('bl', '0x15970'),
        0x52e4: ('b.eq', '0x5338'),
        0x5300: ('strh', 'w8,[x9,#0x218]'),
        0x530c: ('bl', '0x5480'),
        0x5350: ('stp', 'x9,x8,[x21,#0x38]'),
    },
    'FLT-postsetup': {
        0x9287c: ('blr', 'x8'),
        0x92880: ('tbz', 'w0,#0xa,0x928f0'),
        0x9288c: ('bl', '0x5d0dc'),
        0x9289c: ('blr', 'x8'),
    },
    'FLT-ready': {
        0x14704: ('bl', '0x983c8'),
        0x1475c: ('cbnz', 'w21,0x147e0'),
        0x147f8: ('bl', '0xa71dc'),
    },
    'FLT-lazy-globals': {
        0x5e518: ('bl', '0xa5b5c'),
        0x5e520: ('bl', '0xa60e4'),
        0x5e524: ('cbz', 'x0,0x5e538'),
        0x5e540: ('bl', '0x99fb4'),
    },
    'FLT-register-lazy': {
        0x992b8: ('bl', '0x993a4'),
        0x992c0: ('bl', '0x5e504'),
        0x9934c: ('bl', '0x5c34'),
        0x99354: ('bl', '0x5e504'),
    },
    'FLT-if-missing': {
        0x99544: ('bl', '0x4a24'),
        0x99564: ('tbnz', 'w21,#0x0,0x99748'),
        0x99574: ('bl', '0x5cc60'),
        0x99588: ('add', 'x0,x0,#0x6ba'),
        0x996cc: ('add', 'x1,x1,#0xb74'),
        0x996d0: ('bl', '0x5d0f8'),
        0x996dc: ('bl', '0x5dfd8'),
        0x996e8: ('bl', '0x5decc'),
        0x996f4: ('bl', '0x5014'),
    },
}


# Preparation/global setup are stateful and can fail after mutation. These
# addressed file checks deliberately make no runtime receiver/rollback claim.
READINESS_ANCHORS = {
    'FLT-ready-body': {
        0x5cec0: ('add', 'x20,x0,#0x170'),
        0x5cee0: ('bl', '0xa6d44'),
        0x5cee8: ('ldaddal', 'w21,w8,[x8]'),
        0x5ceec: ('cbz', 'w8,0x5cf1c'),
        0x5cf1c: ('ldp', 'x21,x20,[x19,#0xc0]'),
        0x5cf74: ('cbz', 'x21,0x5cef0'),
        0x5cfa0: ('bl', '0xa59dc'),
        0x5cff8: ('cbz', 'w20,0x5d020'),
        0x5d008: ('swpalh', 'w9,w8,[x8]'),
        0x5d014: ('ldaddal', 'w9,w8,[x8]'),
        0x5d018: ('mov', 'w20,#0x1902'),
        0x5d034: ('ldr', 'x8,[x8,#0x8]'),
        0x5d03c: ('swpal', 'x8,x8,[x10]'),
        0x5d090: ('swpal', 'x8,x8,[x9]'),
        0x5d0bc: ('bl', '0xa5820'),
    },
    'FLT-lazy-setup': {
        0x5d374: ('bl', '0xa6d44'),
        0x5d380: ('strb', 'w8,[x20]'),
        0x5d38c: ('tbnz', 'w8,#0x1,0x5d490'),
        0x5d474: ('mov', 'w1,#0x1'),
        0x5d47c: ('bl', '0x906c4'),
        0x5d48c: ('cbnz', 'w22,0x5d4a4'),
        0x5d498: ('bl', '0x539ec'),
        0x5d4b0: ('swpalh', 'w9,w8,[x8]'),
        0x5d4bc: ('strb', 'wzr,[x20]'),
        0x5d4c8: ('strb', 'w9,[x19]'),
        0x5d4cc: ('tbz', 'w8,#0x0,0x5d530'),
        0x5d548: ('bl', '0xa71dc'),
        0x5d5f0: ('bl', '0x498c'),
        0x5d61c: ('bl', '0xa5c7c'),
        0x5d63c: ('bl', '0xa5820'),
    },
    'FLT-unready': {
        0x5d13c: ('bl', '0xa6d44'),
        0x5d148: ('ldaddal', 'w9,w8,[x8]'),
        0x5d150: ('b.ne', '0x5d234'),
        0x5d1d8: ('bl', '0xa5acc'),
        0x5d2a8: ('swpal', 'xzr,x8,[x8]'),
        0x5d2ac: ('cbz', 'w20,0x5d2bc'),
        0x5d2b8: ('ldaddal', 'w9,w8,[x8]'),
        0x5d308: ('bl', '0xa5820'),
    },
    'FLT-setdown': {
        0x5d664: ('tbnz', 'w8,#0x1,0x5d684'),
        0x5d6a4: ('bl', '0x983c8'),
        0x5d6fc: ('cbnz', 'w20,0x5d66c'),
        0x5d704: ('mov', 'w1,#0x3'),
        0x5d70c: ('bl', '0x906c4'),
        0x5d730: ('bl', '0x983d0'),
        0x5d790: ('csel', 'w20,w20,w19,eq'),
    },
    'FLT-global-dispatch': {
        0x90768: ('bl', '0x7e014'),
        0x907e0: ('mov', 'x4,x22'),
        0x907e8: ('bl', '0x98494'),
        0x907f0: ('cbnz', 'w0,0x90b3c'),
        0x907f8: ('b.eq', '0x90b30'),
        0x90814: ('stp', 'w1,w8,[x21]'),
        0x90820: ('bl', '0x5ce90'),
        0x90854: ('bl', '0x8cc70'),
        0x908dc: ('orr', 'w1,w0,#0x2'),
        0x908e4: ('bl', '0x5ce9c'),
        0x90b38: ('bl', '0x5e1bc'),
    },
    'FLT-std-params': {
        0x539fc: ('bl', '0x546bc'),
        0x53a00: ('cbz', 'x0,0x53a14'),
        0x53a20: ('b', '0x535ac'),
    },
    'PLUG-path-ctor': {
        0xca18: ('str', 'x8,[x19]'),
        0xca2c: ('str', 'x8,[x20,#0x30]!'),
        0xca50: ('ldadd', 'x11,x10,[x10]'),
        0xca58: ('stp', 'x8,x9,[x19,#0x38]'),
        0xcab4: ('cbz', 'x8,0xcbd8'),
        0xcac0: ('bl', '0xcc9c'),
        0xcaec: ('blr', 'x8'),
        0xcb04: ('str', 'q0,[x19,#0x50]'),
        0xcb08: ('str', 'x0,[x19,#0x48]'),
        0xcbb0: ('bl', '0x11260'),
        0xcbd4: ('bl', '0x1111c'),
        0xcc00: ('blr', 'x8'),
        0xcc08: ('strb', 'w8,[x19,#0x60]'),
        0xcc98: ('bl', '0x110a4'),
    },
    'PLUG-classref': {
        0xccac: ('mov', 'x19,x8'),
        0xccb8: ('bl', '0xe040'),
        0xccd0: ('bl', '0x112cc'),
        0xccf4: ('stp', 'xzr,xzr,[sp,#0x8]'),
        0xccf8: ('stp', 'x8,x9,[x19,#0x8]'),
    },
    'PLUG-path-thunk': {0xcd74: ('b', '0xc9b4')},
}


# These checks include the actual indirect procedure instructions and the
# earlier canonical publication, without certifying their runtime recipients.
DISPATCH_ANCHORS = {
    'FLT-params-setup': {
        0x535d8: ('bl', '0xa5b5c'),
        0x53650: ('bl', '0x7e014'),
        0x536b0: ('bl', '0x5ce2c'),
        0x536b4: ('tbz', 'w0,#0x0,0x536dc'),
        0x536d4: ('bl', '0x34744'),
        0x536f8: ('bl', '0x5b95c'),
        0x53758: ('bl', '0xa60f0'),
        0x53854: ('cbz', 'x0,0x538c4'),
        0x53890: ('mov', 'w4,#0x4'),
        0x53898: ('bl', '0x98494'),
        0x538a0: ('cbnz', 'w0,0x53928'),
        0x538b0: ('b.ne', '0x538cc'),
        0x538b8: ('bl', '0x97d1c'),
        0x538c4: ('mov', 'w21,#0x4'),
        0x53924: ('mov', 'w21,#0x3'),
        0x53930: ('bl', '0xa573c'),
        0x539b8: ('bl', '0xa5c7c'),
        0x539e8: ('bl', '0xa5820'),
    },
    'FLT-dispatch': {
        0x984ec: ('b.hi', '0x98a50'),
        0x98518: ('bl', '0xa5b38'),
        0x98558: ('bl', '0x5e1d4'),
        0x985b0: ('bl', '0x580a8'),
        0x98618: ('csel', 'x1,xzr,x8,eq'),
        0x98624: ('csel', 'x2,xzr,x8,eq'),
        0x98630: ('mov', 'x3,x19'),
        0x98640: ('bl', '0x38d60'),
        0x98658: ('blr', 'x8'),
        0x9869c: ('blr', 'x8'),
        0x98c50: ('bl', '0xa5c7c'),
        0x98c60: ('bl', '0xa5820'),
    },
    'FLT-host-dispatch': {
        0x38db8: ('str', 'x8,[x5,#0x28]'),
        0x38dc0: ('str', 'x27,[x5,#0x38]'),
        0x38dd0: ('ldr', 'x8,[x8,#0x10]'),
        0x38dd4: ('blr', 'x8'),
        0x38ddc: ('str', 'x0,[sp,#0x50]'),
        0x38e50: ('bl', '0x3aca4'),
        0x38e9c: ('bl', '0xa71e8'),
        0x38eb0: ('bl', '0x35a78'),
        0x38f20: ('mov', 'w1,#0x0'),
        0x38f24: ('bl', '0x3b080'),
        0x38f6c: ('bl', '0x35fa4'),
        0x38f78: ('bl', '0x35c40'),
        0x38fb0: ('cbz', 'x8,0x39154'),
        0x393ac: ('bl', '0x394a4'),
        0x39440: ('bl', '0xa5c7c'),
    },
    'FLT-dispatch-ctor': {
        0x3accc: ('ldp', 'q0,q1,[x1]'),
        0x3acd0: ('ldr', 'q2,[x1,#0x20]'),
        0x3acd8: ('str', 'x8,[x0,#0x30]'),
        0x3acdc: ('stp', 'q1,q2,[x0,#0x10]'),
        0x3ace0: ('str', 'q0,[x0]'),
        0x3ad44: ('str', 'w23,[x20,#0x68]'),
    },
    'FLT-dispatch-optional': {
        0x3b0d4: ('bl', '0xa6408'),
        0x3b0dc: ('str', 'q0,[x19,#0x70]'),
        0x3b0e0: ('cbz', 'w27,0x3b110'),
        0x3b108: ('bl', '0x3b2a8'),
        0x3b134: ('bl', '0x3b804'),
        0x3b1c8: ('mov', 'w20,#0xe'),
        0x3b1d0: ('bl', '0xa6414'),
        0x3b218: ('bl', '0xa6414'),
    },
    'FLT-dispatch-hardware': {
        0x3b280: ('bl', '0xa5a54'),
        0x3b284: ('ldr', 'x1,[x19,#0x70]'),
        0x3b288: ('cbz', 'x1,0x3b29c'),
        0x3b298: ('br', 'x1'),
    },
    'FLT-dispatch-machine': {
        0x3b510: ('bl', '0xa72d8'),
        0x3b518: ('cbnz', 'w0,0x3b5c4'),
        0x3b51c: ('ldr', 'x8,[x21]'),
        0x3b520: ('ldr', 'w0,[x21,#0x8]'),
        0x3b524: ('ldp', 'x1,x2,[x21,#0x10]'),
        0x3b528: ('ldp', 'x3,x4,[x21,#0x20]'),
        0x3b52c: ('ldr', 'x5,[x21,#0x30]'),
        0x3b530: ('blr', 'x8'),
        0x3b548: ('bl', '0xa67f8'),
        0x3b708: ('cbnz', 'w0,0x3b764'),
        0x3b754: ('mov', 'w19,#0xe'),
        0x3b794: ('bl', '0xa6810'),
        0x3b800: ('bl', '0xa5820'),
    },
    'FLT-dispatch-crash': {
        0x3b89c: ('bl', '0xa6690'),
        0x3b8cc: ('ldr', 'x8,[x19]'),
        0x3b8d0: ('ldr', 'w0,[x19,#0x8]'),
        0x3b8d4: ('ldp', 'x1,x2,[x19,#0x10]'),
        0x3b8d8: ('ldp', 'x3,x4,[x19,#0x20]'),
        0x3b8dc: ('ldr', 'x5,[x19,#0x30]'),
        0x3b8e0: ('blr', 'x8'),
        0x3b8e8: ('bl', '0xa6684'),
        0x3b99c: ('bl', '0xa6684'),
        0x3b9e8: ('bl', '0xa5820'),
    },
}


# Static provider references/maps/cleanup only; no runtime recipient certification.
RETENTION_ANCHORS = {
    'PS-ctor': {
        0x4baa4: ('str', 'x8,[x0]'),
        0x4baf0: ('bl', '0x8ca54'),
        0x4bb1c: ('stp', 'xzr,xzr,[x19,#0x128]'),
        0x4bb20: ('strb', 'wzr,[x19,#0x138]'),
    },
    'PS-dtor': {
        0x4bc04: ('ldr', 'x20,[x0,#0x130]'),
        0x4bc14: ('ldaddal', 'x9,x8,[x8]'),
        0x4bc44: ('blr', 'x8'),
        0x4bc4c: ('bl', '0x8d300'),
        0x4bc58: ('ldr', 'x20,[x19,#0x100]'),
        0x4bc68: ('ldaddal', 'x9,x8,[x8]'),
        0x4bce8: ('blr', 'x8'),
        0x4bcf0: ('bl', '0x8d300'),
        0x4bc74: ('str', 'xzr,[x19,#0xe8]'),
        0x4bc90: ('blr', 'x8'),
        0x4bcc8: ('bl', '0x8ca60'),
    },
    'PS-init': {
        0x4bef0: ('cbnz', 'x0,0x4bfd8'),
        0x4bfe4: ('ldr', 'x8,[x8,#0x30]'),
        0x4bfe8: ('blr', 'x8'),
        0x4bff4: ('bl', '0x8d1e0'),
        0x4c03c: ('str', 'w0,[x19,#0xe0]'),
        0x4c05c: ('str', 'w0,[x19,#0xe4]'),
        0x4c07c: ('add', 'x21,x19,#0xe8'),
        0x4c0a4: ('blr', 'x8'),
        0x4c0cc: ('str', 'x22,[x21]'),
        0x4c110: ('blr', 'x8'),
        0x4c138: ('blr', 'x8'),
        0x4c13c: ('str', 'w0,[x19,#0x120]'),
        0x4c274: ('bl', '0x8c97c'),
        0x4c2e8: ('bl', '0x8c928'),
        0x4c2ec: ('brk', '#0x1'),
        0x4c43c: ('bl', '0x8c334'),
    },
    'PS-load': {
        0x4c460: ('mov', 'x20,x8'),
        0x4c464: ('add', 'x19,x0,#0x8'),
        0x4c488: ('bl', '0x8ceb0'),
        0x4c48c: ('ldrb', 'w8,[x21,#0x138]'),
        0x4c49c: ('bl', '0x8c628'),
        0x4c4a0: ('ldr', 'x8,[x21,#0x128]'),
        0x4c4ac: ('stp', 'x8,x9,[x20]'),
        0x4c4c4: ('bl', '0x8c61c'),
        0x4c4c8: ('tbnz', 'w0,#0x1f,0x4c4ec'),
        0x4c4d4: ('stp', 'x8,x9,[x20]'),
        0x4c4e4: ('ldadd', 'x9,x8,[x8]'),
        0x4c4f0: ('str', 'w0,[x22]'),
        0x4c4f4: ('stp', 'xzr,xzr,[x20]'),
        0x4c4fc: ('bl', '0x8cebc'),
        0x4c528: ('bl', '0x8c334'),
        0x4c558: ('bl', '0x8c334'),
    },
    'PS-free': {
        0x4c55c: ('ret', ''),
    },
    'PS-entry': {
        0x4c58c: ('ldr', 'x9,[x8,#0x20]'),
        0x4c598: ('blr', 'x9'),
        0x4c59c: ('ldr', 'x21,[sp,#0x28]'),
        0x4c5ac: ('ldaddal', 'x9,x8,[x8]'),
        0x4c5b4: ('ldr', 'x21,[x20,#0x128]'),
        0x4c5b8: ('cbz', 'x21,0x4c6cc'),
        0x4c5c0: ('cbz', 'w8,0x4c6a0'),
        0x4c5d4: ('cmp', 'x23,#0x90'),
        0x4c5d8: ('b.eq', '0x4c674'),
        0x4c648: ('ldr', 'x21,[x24,#0x148]'),
        0x4c690: ('bl', '0x8d300'),
        0x4c6a8: ('bl', '0x8ca18'),
        0x4c6b4: ('bl', '0x8ce2c'),
        0x4c6cc: ('mov', 'x0,x21'),
        0x4c718: ('bl', '0x8c334'),
    },
    'PS-module': {
        0x4d368: ('ldr', 'x10,[x0,#0x128]'),
        0x4d374: ('stp', 'x10,x9,[x8]'),
        0x4d384: ('ldadd', 'x9,x8,[x8]'),
        0x4d38c: ('stp', 'xzr,xzr,[x8]'),
    },
    'TDB-factory': {
        0x599c: ('adrp', 'x8,95'),
        0x59a0: ('ldr', 'x0,[x8,#0xd40]'),
        0x59a4: ('ret', ''),
    },
    'TDB-get-instance': {
        0x1f054: ('bl', '0x50974'),
        0x1f05c: ('ldr', 'x23,[x21,#0x40]!'),
        0x1f0a0: ('tbz', 'w0,#0x0,0x1f0d4'),
        0x1f0a4: ('mov', 'x19,#0x0'),
        0x1f0b4: ('bl', '0x50980'),
        0x1f0d4: ('add', 'x0,x20,#0x50'),
        0x1f0f0: ('bl', '0x21f8c'),
        0x1f0f4: ('ldr', 'x19,[x0,#0x30]'),
        0x1f158: ('bl', '0x50404'),
    },
    'TDB-register': {
        0x1f1ac: ('bl', '0x50974'),
        0x1f1b4: ('bl', '0x302c8'),
        0x1f1c8: ('ldr', 'x23,[x21,#0x40]!'),
        0x1f20c: ('tbz', 'w0,#0x0,0x1f30c'),
        0x1f214: ('mov', 'w1,#0x1'),
        0x1f218: ('bl', '0x2f370'),
        0x1f220: ('ldr', 'x8,[x8,#0x158]'),
        0x1f228: ('blr', 'x8'),
        0x1f238: ('str', 'x19,[sp,#0x38]'),
        0x1f23c: ('add', 'x0,x20,#0x50'),
        0x1f248: ('bl', '0x21e68'),
        0x1f25c: ('bl', '0x50cb0'),
        0x1f27c: ('stp', 'xzr,x20,[x0,#0x10]'),
        0x1f294: ('bl', '0x21d04'),
        0x1f2d4: ('bl', '0x50980'),
        0x1f31c: ('blr', 'x8'),
        0x1f320: ('add', 'x0,x20,#0x50'),
        0x1f340: ('bl', '0x21f8c'),
        0x1f344: ('ldr', 'x19,[x0,#0x30]'),
        0x1f3e0: ('blr', 'x8'),
        0x1f3fc: ('bl', '0x50404'),
    },
    'TDB-unregister-name': {
        0x1f824: ('bl', '0x20128'),
        0x1f828: ('cbz', 'x0,0x1f884'),
        0x1f830: ('ldr', 'x8,[x8,#0x98]'),
        0x1f834: ('blr', 'x8'),
        0x1f848: ('bl', '0x1fe1c'),
        0x1f86c: ('bl', '0x50974'),
        0x1f870: ('add', 'x0,x20,#0x8'),
        0x1f878: ('bl', '0x228e4'),
        0x1f880: ('bl', '0x50980'),
        0x1f8c0: ('bl', '0x50404'),
    },
    'TDB-unregister-factory': {
        0x1fc2c: ('bl', '0x50974'),
        0x1fc34: ('ldr', 'x25,[x24,#0x58]!'),
        0x1fc80: ('tbnz', 'w21,#0x0,0x1fca8'),
        0x1fcbc: ('bl', '0x50980'),
        0x1fcc8: ('tbnz', 'w8,#0x0,0x1fcdc'),
        0x1fcd0: ('ldr', 'x8,[x8,#0x8]'),
        0x1fcd8: ('blr', 'x8'),
        0x1fcdc: ('eor', 'w0,w19,#0x1'),
        0x1fcfc: ('ldr', 'x21,[x23,#0x30]'),
        0x1fd08: ('bl', '0x228e4'),
        0x1fd10: ('b.ne', '0x1fd38'),
        0x1fd14: ('add', 'x0,x20,#0x38'),
        0x1fd1c: ('bl', '0x22d9c'),
        0x1fd24: ('b.ne', '0x1fd74'),
        0x1fd6c: ('bl', '0x50d4c'),
        0x1fda8: ('bl', '0x50d4c'),
    },
    'TDB-unregister-recursive': {
        0x1fe4c: ('bl', '0x3348c'),
        0x1fe74: ('bl', '0x50620'),
        0x1ff14: ('ldaddal', 'x9,x8,[x8]'),
        0x1ff38: ('bl', '0x302c8'),
        0x1ff48: ('bl', '0x1fbe4'),
        0x1ff4c: ('ldr', 'x8,[x19,#0x10]'),
        0x1ff8c: ('blr', 'x8'),
        0x1ffa0: ('bl', '0x1fe1c'),
        0x2001c: ('b', '0x1ffc0'),
        0x20030: ('mov', 'w2,#0x1'),
        0x20034: ('bl', '0x1fbe4'),
        0x2004c: ('bl', '0x5062c'),
    },
    'TDB-get-stream': {
        0x20164: ('bl', '0x50974'),
        0x20168: ('ldr', 'x22,[x20,#0x58]!'),
        0x201ac: ('tbz', 'w0,#0x0,0x201dc'),
        0x201b0: ('mov', 'x19,#0x0'),
        0x201c0: ('bl', '0x50980'),
        0x201dc: ('ldr', 'x19,[x21,#0x30]'),
        0x201fc: ('bl', '0x50404'),
        0x2022c: ('bl', '0x50404'),
    },
}


# Complete destructor instruction anchors also bind the observed absence of
# CFBundle release/unload calls; this is an exact-file observation, not policy.
ENTRY_ANCHORS = {
    'ASL-load': {
        0x23b68: ('bl', '0x29908'),
        0x23b8c: ('bl', '0x2953c'),
        0x23c24: ('bl', '0x29668'),
        0x23c38: ('bl', '0x2965c'),
        0x23c48: ('mov', 'w19,#0x1'),
        0x23c4c: ('movk', 'w19,#0xa00f,lsl#16'),
        0x23c50: ('bl', '0x2986c'),
        0x23cb0: ('bl', '0x29338'),
        0x23cc8: ('bl', '0x241d0'),
        0x23cd4: ('bl', '0x294a0'),
        0x23d80: ('bl', '0x24310'),
        0x23e18: ('bl', '0x2986c'),
        0x23e30: ('bl', '0x296a4'),
    },
    'ASL-create': {
        0x241fc: ('stp', 'x8,x21,[x0]'),
        0x24200: ('strb', 'wzr,[x0,#0x10]'),
        0x24210: ('bl', '0x294ac'),
        0x2422c: ('stp', 'xzr,x19,[x0,#0x10]'),
        0x24234: ('stp', 'x19,x0,[x20]'),
        0x24244: ('ldaddal', 'x9,x8,[x8]'),
        0x2426c: ('blr', 'x8'),
        0x24274: ('bl', '0x29de8'),
        0x242a0: ('blr', 'x8'),
        0x242f4: ('mov', 'w0,#0x6'),
        0x242f8: ('movk', 'w0,#0xa00f,lsl#16'),
        0x2430c: ('bl', '0x296a4'),
    },
    'ASL-ctor': {
        0x24358: ('add', 'x8,x8,#0x680'),
        0x2435c: ('stp', 'x8,x1,[x0]'),
        0x24360: ('strb', 'w2,[x0,#0x10]'),
        0x24370: ('bl', '0x294ac'),
        0x243a4: ('bl', '0x296a4'),
    },
    'ASL-ctor-base': {
        0x243c0: ('add', 'x8,x8,#0x680'),
        0x243c4: ('stp', 'x8,x1,[x0]'),
        0x243c8: ('strb', 'w2,[x0,#0x10]'),
        0x243dc: ('bl', '0x294ac'),
        0x24400: ('bl', '0x296a4'),
    },
    'ASL-dtor': {
        0x24404: ('stp', 'x20,x19,[sp,#-0x20]!'),
        0x24408: ('stp', 'x29,x30,[sp,#0x10]'),
        0x2440c: ('add', 'x29,sp,#0x10'),
        0x24410: ('mov', 'x19,x0'),
        0x24414: ('adrp', 'x8,13'),
        0x24418: ('add', 'x8,x8,#0x680'),
        0x2441c: ('str', 'x8,[x0]'),
        0x24420: ('strb', 'wzr,[x0,#0x10]'),
        0x24424: ('ldrsb', 'w8,[x0,#0x2f]'),
        0x24428: ('tbz', 'w8,#0x1f,0x2443c'),
        0x2442c: ('ldr', 'x0,[x19,#0x18]'),
        0x24430: ('ldr', 'x8,[x19,#0x28]'),
        0x24434: ('and', 'x1,x8,#0x7fffffffffffffff'),
        0x24438: ('bl', '0x29b30'),
        0x2443c: ('mov', 'x0,x19'),
        0x24440: ('ldp', 'x29,x30,[sp,#0x10]'),
        0x24444: ('ldp', 'x20,x19,[sp],#0x20'),
        0x24448: ('ret', ''),
        0x2444c: ('bl', '0x4ec8'),
    },
    'ASL-dtor-complete': {
        0x24450: ('stp', 'x20,x19,[sp,#-0x20]!'),
        0x24454: ('stp', 'x29,x30,[sp,#0x10]'),
        0x24458: ('add', 'x29,sp,#0x10'),
        0x2445c: ('mov', 'x19,x0'),
        0x24460: ('adrp', 'x8,13'),
        0x24464: ('add', 'x8,x8,#0x680'),
        0x24468: ('str', 'x8,[x0]'),
        0x2446c: ('strb', 'wzr,[x0,#0x10]'),
        0x24470: ('ldrsb', 'w8,[x0,#0x2f]'),
        0x24474: ('tbz', 'w8,#0x1f,0x24488'),
        0x24478: ('ldr', 'x0,[x19,#0x18]'),
        0x2447c: ('ldr', 'x8,[x19,#0x28]'),
        0x24480: ('and', 'x1,x8,#0x7fffffffffffffff'),
        0x24484: ('bl', '0x29b30'),
        0x24488: ('mov', 'x0,x19'),
        0x2448c: ('ldp', 'x29,x30,[sp,#0x10]'),
        0x24490: ('ldp', 'x20,x19,[sp],#0x20'),
        0x24494: ('ret', ''),
        0x24498: ('bl', '0x4ec8'),
    },
    'ASL-delete': {
        0x2449c: ('stp', 'x20,x19,[sp,#-0x20]!'),
        0x244a0: ('stp', 'x29,x30,[sp,#0x10]'),
        0x244a4: ('add', 'x29,sp,#0x10'),
        0x244a8: ('mov', 'x19,x0'),
        0x244ac: ('adrp', 'x8,13'),
        0x244b0: ('add', 'x8,x8,#0x680'),
        0x244b4: ('str', 'x8,[x0]'),
        0x244b8: ('strb', 'wzr,[x0,#0x10]'),
        0x244bc: ('ldrsb', 'w8,[x0,#0x2f]'),
        0x244c0: ('tbz', 'w8,#0x1f,0x244d4'),
        0x244c4: ('ldr', 'x0,[x19,#0x18]'),
        0x244c8: ('ldr', 'x8,[x19,#0x28]'),
        0x244cc: ('and', 'x1,x8,#0x7fffffffffffffff'),
        0x244d0: ('bl', '0x29b30'),
        0x244d4: ('mov', 'x0,x19'),
        0x244d8: ('ldp', 'x29,x30,[sp,#0x10]'),
        0x244dc: ('ldp', 'x20,x19,[sp],#0x20'),
        0x244e0: ('b', '0x29e90'),
        0x244e4: ('bl', '0x4ec8'),
    },
    'ASL-proc': {
        0x245dc: ('bl', '0x29c14'),
        0x245fc: ('bl', '0x294d0'),
        0x24634: ('bl', '0x299e0'),
        0x24660: ('bl', '0x2a07c'),
        0x24668: ('cbnz', 'w0,0x2472c'),
        0x2466c: ('ldr', 'x0,[x19,#0x8]'),
        0x24674: ('bl', '0x29344'),
        0x24678: ('mov', 'x19,x0'),
        0x2468c: ('bl', '0x299e0'),
        0x246d4: ('bl', '0x294a0'),
        0x246e4: ('bl', '0x29c20'),
        0x246e8: ('mov', 'x0,x19'),
        0x24778: ('bl', '0x29f2c'),
        0x247e0: ('bl', '0x29c20'),
        0x2487c: ('bl', '0x299f8'),
        0x2488c: ('cbnz', 'w0,0x249cc'),
        0x249c0: ('mov', 'x19,#0x0'),
        0x249c8: ('b', '0x2467c'),
        0x249f8: ('bl', '0x29a04'),
        0x249fc: ('brk', '#0x1'),
        0x24a98: ('bl', '0x25b54'),
        0x24a9c: ('b', '0x247a8'),
    },
    'ASL-unload-flag': {
        0x24b3c: ('strb', 'w1,[x0,#0x10]'),
        0x24b40: ('ret', ''),
    },
    'ASL-last-owner': {
        0x27ca8: ('ldr', 'x0,[x0,#0x18]'),
        0x27cac: ('cbz', 'x0,0x27cbc'),
        0x27cb0: ('ldr', 'x8,[x0]'),
        0x27cb4: ('ldr', 'x1,[x8,#0x8]'),
        0x27cb8: ('br', 'x1'),
        0x27cbc: ('ret', ''),
    },
    'FLT-ctor': {
        0x5cb04: ('add', 'x8,x8,#0xc80'),
        0x5cb0c: ('stp', 'x8,x9,[x0]'),
        0x5cb20: ('stp', 'q0,q0,[x0,#0xb0]'),
        0x5cb24: ('str', 'xzr,[x0,#0xd0]'),
        0x5cb60: ('bl', '0xa678c'),
        0x5cbe0: ('bl', '0x5cbec'),
        0x5cbe8: ('bl', '0xa5820'),
    },
    'FLT-desc-release': {
        0x5cbfc: ('ldr', 'x20,[x0,#0x8]'),
        0x5cc0c: ('ldaddal', 'w9,w8,[x8]'),
        0x5cc10: ('cmp', 'w8,#0x1'),
        0x5cc24: ('blr', 'x8'),
        0x5cc30: ('ldaddal', 'w9,w8,[x8]'),
        0x5cc48: ('blr', 'x8'),
    },
    'FLT-ctor-thunk': {
        0x5cc60: ('b', '0x5cae4'),
    },
    'FLT-dtor': {
        0x5cc84: ('bl', '0xa6798'),
        0x5ccd0: ('ldr', 'x20,[x19,#0xc8]'),
        0x5cce0: ('ldaddal', 'w9,w8,[x8]'),
        0x5cce4: ('cmp', 'w8,#0x1'),
        0x5ccf8: ('blr', 'x8'),
        0x5cd04: ('ldaddal', 'w9,w8,[x8]'),
        0x5cd1c: ('blr', 'x8'),
        0x5cd2c: ('ret', ''),
    },
    'FLT-get-desc': {
        0x5d0dc: ('ldp', 'x10,x9,[x0,#0xc0]'),
        0x5d0e0: ('stp', 'x10,x9,[x8]'),
        0x5d0e4: ('cbz', 'x9,0x5d0f4'),
        0x5d0e8: ('add', 'x8,x9,#0x8'),
        0x5d0ec: ('mov', 'w9,#0x1'),
        0x5d0f0: ('ldadd', 'w9,w8,[x8]'),
        0x5d0f4: ('ret', ''),
    },
    'FLT-set-proc': {
        0x5d0f8: ('add', 'x8,x0,#0xd0'),
        0x5d0fc: ('swpal', 'x1,x8,[x8]'),
        0x5d100: ('ret', ''),
    },
    'FLT-set-desc': {
        0x5e278: ('ldp', 'x9,x8,[x1]'),
        0x5e288: ('ldadd', 'w11,w10,[x10]'),
        0x5e28c: ('ldr', 'x19,[x0,#0xc8]'),
        0x5e290: ('stp', 'x9,x8,[x0,#0xc0]'),
        0x5e2a0: ('ldaddal', 'w9,w8,[x8]'),
        0x5e2a4: ('cmp', 'w8,#0x1'),
        0x5e2b8: ('blr', 'x8'),
        0x5e2c4: ('ldaddal', 'w9,w8,[x8]'),
        0x5e2dc: ('blr', 'x8'),
    },
    'FLT-get-proc': {
        0x5e2f0: ('add', 'x8,x0,#0xd0'),
        0x5e2f4: ('ldar', 'x0,[x8]'),
        0x5e2f8: ('ret', ''),
    },
    'PLUG-load-platform': {
        0x108b4: ('blr', 'x9'),
        0x108dc: ('blr', 'x8'),
        0x108e8: ('bl', '0x10b98'),
        0x108f0: ('str', 'x0,[x8,#0x8]'),
        0x108f4: ('cbz', 'x0,0x1099c'),
        0x10900: ('strh', 'w9,[x8,#0x28]'),
        0x10934: ('bl', '0x2b64'),
        0x1093c: ('str', 'xzr,[x8,#0x8]'),
        0x1095c: ('mov', 'w19,#0x0'),
        0x10964: ('mov', 'w19,#0x1'),
        0x10a48: ('bl', '0x11074'),
        0x10a58: ('str', 'w8,[x0]'),
        0x10a68: ('bl', '0x115fc'),
        0x10ac8: ('bl', '0x10f0c'),
        0x10b44: ('cmp', 'w21,#0x2'),
        0x10b48: ('b.ne', '0x10b60'),
        0x10b5c: ('b', '0x10968'),
        0x10b70: ('bl', '0x11104'),
        0x10b7c: ('b', '0x10968'),
    },
    'PLUG-entry': {
        0x10bb0: ('ldr', 'x8,[x0,#0x8]'),
        0x10bb4: ('cbnz', 'x8,0x10bdc'),
        0x10bb8: ('ldr', 'x0,[x19,#0x48]'),
        0x10bc0: ('ldr', 'x8,[x19,#0x50]'),
        0x10bcc: ('ldr', 'x8,[x8,#0x68]'),
        0x10bd0: ('blr', 'x8'),
        0x10bd4: ('str', 'x0,[x19,#0x8]'),
        0x10bdc: ('ldrb', 'w8,[x19,#0x60]'),
        0x10c2c: ('bl', '0x112f0'),
        0x10c40: ('ldaddal', 'x9,x8,[x8]'),
        0x10c94: ('bl', '0x112f0'),
        0x10c9c: ('mov', 'w1,#0x0'),
        0x10ca0: ('bl', '0x1114c'),
        0x10cb4: ('ldaddal', 'x9,x8,[x8]'),
        0x10cbc: ('ldr', 'x0,[x19,#0x8]'),
        0x10ce0: ('blr', 'x8'),
        0x10d00: ('blr', 'x8'),
        0x10d88: ('bl', '0xe6c0'),
    },
    'PLUG-unload-platform': {
        0x10dc4: ('ldr', 'x8,[x8,#0x30]'),
        0x10dc8: ('blr', 'x8'),
        0x10dcc: ('tbnz', 'w0,#0x0,0x10dd8'),
        0x10dd4: ('bl', '0x87a0'),
        0x10de0: ('str', 'xzr,[x8,#0x8]'),
        0x10de8: ('mov', 'w10,#0xffec'),
        0x10dec: ('and', 'w9,w9,w10'),
        0x10df0: ('strh', 'w9,[x8,#0x28]'),
        0x10e1c: ('mov', 'x0,x19'),
        0x10e48: ('mov', 'x0,x19'),
        0x10e64: ('bl', '0x110a4'),
    },
    'PLUG-unload-plugin': {
        0x87a0: ('ret', ''),
    },
    'PLUG-desc-dtor': {
        0xe738: ('add', 'x8,x8,#0x10'),
        0xe740: ('ldr', 'x20,[x0,#0x58]'),
        0xe750: ('ldaddal', 'x9,x8,[x8]'),
        0xe764: ('blr', 'x8'),
        0xe76c: ('bl', '0x114dc'),
        0xe770: ('ldr', 'x20,[x19,#0x40]'),
        0xe780: ('ldaddal', 'x9,x8,[x8]'),
        0xe7bc: ('blr', 'x8'),
        0xe7c4: ('bl', '0x114dc'),
        0xe7e8: ('ret', ''),
    },
}

def verify_entry_lifetime(text, label, start, end):
    require(any((row[0], row[2], row[3]) == (label, start, end)
                for row in REVIEWS['entry-lifetime']),
            'unreviewed entry lifetime window')
    count = validate_disassembly(text, start, end)
    rows = {}
    for address, op, operands in re.findall(
            r'^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:[ \t]+(\S+)[ \t]*([^\n]*)', text, re.M):
        rows[int(address, 16)] = (op, re.sub(r'\s+', '', operands.split(';')[0]))
    expected = ENTRY_ANCHORS[label]
    require(all(rows.get(address) == pair for address, pair in expected.items()),
            'entry lifetime structural anchors differ')
    return {'decoded_instructions': count, 'structural_anchors': len(expected),
            'claim': 'file-only-entry-and-owners-not-live-lifetime-or-safe-rollback'}


def verify_entry_table(words, fixups, chains, label):
    require(label in ENTRY_TABLE_TARGETS, 'unreviewed entry table')
    _, _, start, count = next(row for row in DATA_WINDOWS['entry-lifetime'] if row[0] == label)
    formats = re.findall(r'pointer_format:\s+(\d+)\s+\(([^)]+)\)', chains)
    require(formats and all(pair == ('6', 'DYLD_CHAINED_PTR_64_OFFSET') for pair in formats),
            'entry table fixup format differs')
    expected = ENTRY_TABLE_TARGETS[label]
    require(len(words) == count and words[0] == 0, 'entry table coverage/header differs')
    # 64_OFFSET rebase: low 36 bits target, high8 bits 36..43, reserved bits
    # 44..50, next bits 51..62, bind bit 63. These pins use low targets only.
    require(all(isinstance(w, int) and 0 <= w < 1 << 64 and
                not w & ((1 << 63) | (0x7fff << 36)) for w in words[1:]),
            'entry table is bound, high-address or reserved')
    targets = (0,) + tuple(w & ((1 << 36)-1) for w in words[1:])
    require(targets == expected, 'entry table targets differ')
    rows = []
    for address, kind, target in re.findall(
            r'^\s*__DATA_CONST\s+__const\s+0x([0-9a-fA-F]+)\s+(\S+)\s+([^\n]+)',
            fixups, re.M):
        address = int(address, 16)
        if start <= address < start + count*8:
            require(kind == 'rebase' and re.fullmatch(r'0x[0-9a-fA-F]+', target.strip()),
                    'entry table fixup is not a plain rebase')
            rows.append((address, int(target.strip(), 16)))
    require(rows == [(start+i*8, target) for i, target in enumerate(expected) if i],
            'entry table fixups differ or are incomplete/duplicated')
    return {'rebases': count-1, 'file_targets': [hex(target) for target in expected],
            'claim': 'file-table-correspondence-not-runtime-receiver'}


def verify_retention(text, label, start, end):
    require((label, 'PluginSupport' if label.startswith('PS-') else 'TDB', start, end)
            in REVIEWS['provider-factory'], 'unreviewed provider retention window')
    count = validate_disassembly(text, start, end)
    rows = {}
    for address, op, operands in re.findall(
            r'^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:[ \t]+(\S+)[ \t]*([^\n]*)', text, re.M):
        rows[int(address, 16)] = (op, re.sub(r'\s+', '', operands.split(';')[0]))
    expected = RETENTION_ANCHORS[label]
    require(all(rows.get(address) == pair for address, pair in expected.items()),
            'provider retention structural anchors differ')
    return {'decoded_instructions': count, 'structural_anchors': len(expected),
            'claim': 'file-only-references-and-maps-not-runtime-lifetime-or-rollback'}


def verify_dispatch(text, label, start, end):
    require((label, 'FLT', start, end) in REVIEWS['effect-dispatch'],
            'unreviewed effect dispatch window')
    count = validate_disassembly(text, start, end)
    rows = {}
    for address, op, operands in re.findall(
            r'^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:[ \t]+(\S+)[ \t]*([^\n]*)', text, re.M):
        rows[int(address, 16)] = (op, re.sub(r'\s+', '', operands.split(';')[0]))
    expected = DISPATCH_ANCHORS[label]
    require(all(rows.get(address) == pair for address, pair in expected.items()),
            'effect dispatch structural anchors differ')
    return {'decoded_instructions': count, 'structural_anchors': len(expected),
            'claim': 'file-only-dispatch-and-failure-paths-not-safe-runtime-ABI'}


def verify_readiness(text, label, start, end):
    require((label, 'PLUG' if label.startswith('PLUG-') else 'FLT', start, end)
            in REVIEWS['effect-readiness'], 'unreviewed effect readiness window')
    count = validate_disassembly(text, start, end)
    rows = {}
    for address, op, operands in re.findall(
            r'^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:[ \t]+(\S+)[ \t]*([^\n]*)', text, re.M):
        rows[int(address, 16)] = (op, re.sub(r'\s+', '', operands.split(';')[0]))
    expected = READINESS_ANCHORS[label]
    require(all(rows.get(address) == pair for address, pair in expected.items()),
            'effect readiness structural anchors differ')
    return {'decoded_instructions': count, 'structural_anchors': len(expected),
            'claim': 'file-only-state-and-ownership-not-safe-runtime-ABI'}


def verify_publication(text, label, start, end):
    require((label, 'PLUG' if label.startswith('PLUG-') else 'FLT', start, end)
            in REVIEWS['publication'], 'unreviewed publication window')
    count = validate_disassembly(text, start, end)
    rows = {}
    for address, op, operands in re.findall(
            r'^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:[ \t]+(\S+)[ \t]*([^\n]*)', text, re.M):
        rows[int(address, 16)] = (op, re.sub(r'\s+', '', operands.split(';')[0]))
    expected = PUBLICATION_ANCHORS[label]
    require(all(rows.get(address) == pair for address, pair in expected.items()),
            'publication structural anchors differ')
    return {'decoded_instructions': count, 'structural_anchors': len(expected),
            'claim': 'file-only-conditional-publication-not-safe-runtime-ABI'}


def verify_ownership(text, label, start, end):
    require((label, 'MEE', start, end) in REVIEWS['ownership'], 'unreviewed ownership window')
    count = validate_disassembly(text, start, end)
    rows = {}
    for address, op, operands in re.findall(
            r'^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:[ \t]+(\S+)[ \t]*([^\n]*)', text, re.M):
        rows[int(address, 16)] = (op, re.sub(r'\s+', '', operands.split(';')[0]))
    expected = OWNERSHIP_ANCHORS[label]
    require(all(rows.get(address) == pair for address, pair in expected.items()),
            'MEE ownership structural anchors differ')
    return {'decoded_instructions': count, 'structural_anchors': len(expected),
            'claim': 'file-only-ownership-flow-not-runtime-or-repeat-safety-proof'}


def review_windows(review):
    require(review in REVIEWS, "unknown review scope")
    windows = REVIEWS[review]
    require(len({label for label, *_ in windows}) == len(windows),
            "duplicate review window label")
    for label, name, start, end in windows:
        require(name in INPUTS and re.fullmatch(r"[A-Za-z0-9-]+", label),
                "invalid review window identity")
        lldb_script(INPUTS[name][0], start, end)
    return windows


def require(value, reason):
    if not value:
        raise ValueError(reason)


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def source_identity():
    def git(*args):
        return subprocess.check_output(
            ["git", "-c", "core.fsmonitor=false", *args],
            cwd=ROOT, text=True, stderr=subprocess.STDOUT, timeout=15,
            env=dict(os.environ, GIT_OPTIONAL_LOCKS="0")).strip()
    commit = git("rev-parse", "HEAD")
    require(re.fullmatch(r"[0-9a-f]{40}", commit), "invalid Git source identity")
    require(git("status", "--porcelain=v1", "--untracked-files=all") == "",
            "source tree must be clean")
    return commit


def profile_agrees():
    text = PROFILE.read_text(encoding="utf-8")
    for name, (path, digest) in INPUTS.items():
        if name in FILE_ONLY_INPUTS:
            require((path, digest) == FILE_ONLY_INPUTS[name],
                    "collector input differs from file-only profile: " + name)
            continue
        require(str(path) in text and digest in text,
                "collector pin differs from C1 profile: " + name)
    record = json.loads(FILE_ONLY_PROFILE.read_text(encoding="utf-8"))
    expected = {"schema": "AEHL-FILE-REVIEW-PINS-1",
                "scope": "offline-only-not-native-host-profile",
                "inputs": {key: {"path": str(path), "sha256": digest}
                           for key, (path, digest) in FILE_ONLY_INPUTS.items()}}
    require(record == expected, "collector pin differs from file-only profile")


def validate_input(path, expected):
    path = Path(path)
    require(path.is_absolute(), "input path must be absolute")
    resolved = path.resolve(strict=True)
    app = APP.resolve(strict=True)
    require(resolved == path and app in resolved.parents,
            "input path is outside reviewed app or uses a symlink")
    info = path.stat()
    require(info.st_uid in (0, os.getuid()) and info.st_nlink == 1 and
            0 < info.st_size <= 256 * 1024 * 1024,
            "input file identity is unsafe")
    actual = sha256(path)
    require(actual == expected, "input SHA-256 differs from reviewed profile")
    return actual


def lldb_target(path):
    value = str(path)
    require(not any(c in value for c in ('"', "\\", "\n", "\r", "\x00")),
            "unsafe input path")
    return [
        "settings set target.load-cwd-lldbinit false",
        "settings set target.load-script-from-symbol-file false",
        'target create --no-dependents --arch arm64 "' + value + '"',
    ]


def lldb_script(path, start, end):
    require(0 < start < end <= start + 4096 and start % 4 == 0 and end % 4 == 0,
            "invalid bounded disassembly window")
    return "\n".join(lldb_target(path) + [
        "disassemble --start-address 0x%x --end-address 0x%x" % (start, end), "quit", ""])


def lldb_data_script(path, start, count):
    require(0 < start and start % 8 == 0 and 1 <= count <= 32,
            "invalid bounded data window")
    return "\n".join(lldb_target(path) + [
        "memory read --format x --size 8 --count %d 0x%x" % (count, start), "quit", ""])


def validate_data(text, start, count):
    """Validate file-backed words only; never interpret them as runtime pointers."""
    words = []
    for address, values in re.findall(
            r"^0x([0-9a-fA-F]+):((?:\s+0x[0-9a-fA-F]{16})+)\s*$", text, re.M):
        for index, value in enumerate(values.split()):
            words.append((int(address, 16) + index * 8, int(value, 16)))
    require([address for address, _ in words] == list(range(start, start + count * 8, 8)),
            "data window is incomplete or outside reviewed bounds")
    return [value for _, value in words]


def run_tool(argv, *, input_text=None, timeout=45):
    result = subprocess.run(
        argv, input=input_text, text=True, stdin=subprocess.PIPE if input_text is not None else subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout,
        env=dict(os.environ, LC_ALL="C"), check=False)
    require(result.returncode == 0, "offline inspection tool failed")
    require(len(result.stdout.encode()) <= MAX_OUTPUT and len(result.stderr.encode()) <= MAX_OUTPUT,
            "offline inspection output exceeded limit")
    return result.stdout, result.stderr


def select_symbols(text, review="search-abi"):
    selected = [line for line in text.splitlines() if SYMBOL_WANTED[review].search(line)]
    require(selected, "expected resource-search symbols were not found")
    return "\n".join(selected) + "\n"


def validate_disassembly(text, start, end):
    """Require one decoded arm64 instruction at every address in the window."""
    instructions = re.findall(r"^.*\[0x([0-9a-fA-F]+)\]\s+<[^>]*>:\s+(\S+)", text, re.M)
    addresses = [int(address, 16) for address, _ in instructions]
    require(addresses == list(range(start, end, 4)),
            "disassembly window is incomplete or outside reviewed bounds")
    require(all(op not in (".long", ".word", ".inst", "<unknown>")
                for _, op in instructions), "disassembly contains undecoded instructions")
    return len(instructions)


def verify_lldb_disassembly(text, diagnostics, start, end):
    """Reject tool errors, but not C++ exception names in decoded comments."""
    count = validate_disassembly(text, start, end)
    # Only verified addressed instruction lines may have their symbol comment
    # removed. Commands, other output and stderr retain the fail-closed check.
    transcript = re.sub(
        r'(^.*\[0x[0-9a-fA-F]+\]\s+<[^>]*>:[ \t]+[^;\n]*);[^\n]*',
        r'\1', text, flags=re.M)
    lowered = (transcript + diagnostics).lower()
    require('error:' not in lowered and 'fatal:' not in lowered,
            'lldb reported an inspection error')
    return count


def write_exclusive(path, data):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
    except Exception:
        raise


def package(folder, record):
    record_path = folder / "record.json"
    write_exclusive(record_path, json.dumps(record, indent=2, sort_keys=True) + "\n")
    files = [p for p in sorted(folder.iterdir()) if p.is_file()]
    hashes = {p.name: sha256(p) for p in files}
    manifest = folder / "SHA256.json"
    write_exclusive(manifest, json.dumps(hashes, indent=2, sort_keys=True) + "\n")
    files.append(manifest)
    archive = folder.with_suffix(".zip")
    with zipfile.ZipFile(archive, "x", zipfile.ZIP_DEFLATED) as output:
        for path in files:
            output.write(path, path.name)
    os.chmod(archive, 0o600)
    with zipfile.ZipFile(archive) as check:
        require(check.testzip() is None, "collector ZIP integrity failed")
        require(set(check.namelist()) == {p.name for p in files},
                "collector ZIP inventory mismatch")
        archived = json.loads(check.read("SHA256.json"))
        require(archived == hashes, "collector ZIP hash manifest mismatch")
        for name, digest in hashes.items():
            require(hashlib.sha256(check.read(name)).hexdigest() == digest,
                    "collector ZIP payload hash mismatch")
    return archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review", choices=tuple(REVIEWS), default="search-abi")
    parser.add_argument("--output-parent", type=Path,
                        default=ROOT / "build-ae-hot-loader")
    args = parser.parse_args()
    if sys.platform != "darwin":
        parser.exit(2, "BLOCKED: Stage C1 resource collector requires macOS.\n")
    try:
        commit = source_identity()
        profile_agrees()
        windows = review_windows(args.review)
        names = tuple(dict.fromkeys(name for _, name, _, _ in windows))
        parent = args.output_parent.absolute()
        expected_parent = (ROOT / "build-ae-hot-loader").absolute()
        require(parent == expected_parent, "output parent must be the owned build directory")
        parent.mkdir(mode=0o700, exist_ok=True)
        require(not parent.is_symlink() and parent.is_dir() and parent.stat().st_uid == os.getuid(),
                "owned build directory is unsafe")
        parent = parent.resolve(strict=True)
        observed = {name: validate_input(*INPUTS[name]) for name in names}
        prefix = "resource-abi-" if args.review == "search-abi" else "resource-" + args.review + "-"
        folder = Path(tempfile.mkdtemp(prefix=prefix + uuid.uuid4().hex[:8] + "-",
                                       dir=parent))
        os.chmod(folder, 0o700)
        outputs = {}
        ownership = {}
        publication = {}
        readiness = {}
        dispatch = {}
        retention = {}
        entry = {}
        for name in names:
            path, _ = INPUTS[name]
            nm, nm_err = run_tool(["/usr/bin/nm", "-arch", "arm64", "-n", "-m", str(path)])
            require(not nm_err.strip(), "nm produced unexpected diagnostics")
            symbols = select_symbols(nm, args.review)
            write_exclusive(folder / (name + "-symbols.txt"), symbols)
        for label, name, start, end in windows:
            path, _ = INPUTS[name]
            script = lldb_script(path, start, end)
            write_exclusive(folder / (label + "-inspect.lldb"), script)
            disassembly, diagnostics = run_tool(
                ["/usr/bin/xcrun", "lldb", "--no-lldbinit", "--batch",
                 "--source", str(folder / (label + "-inspect.lldb"))],
                timeout=60)
            instruction_count = verify_lldb_disassembly(disassembly, diagnostics, start, end)
            if args.review == 'publication':
                publication[label] = verify_publication(disassembly, label, start, end)
            if args.review == 'effect-readiness':
                readiness[label] = verify_readiness(disassembly, label, start, end)
            if args.review == 'effect-dispatch':
                dispatch[label] = verify_dispatch(disassembly, label, start, end)
            if args.review == 'provider-factory':
                retention[label] = verify_retention(disassembly, label, start, end)
            if args.review == 'entry-lifetime':
                entry[label] = verify_entry_lifetime(disassembly, label, start, end)
            if args.review == 'ownership':
                ownership[label] = verify_ownership(disassembly, label, start, end)
            write_exclusive(folder / (label + "-disassembly.txt"), disassembly)
            if diagnostics:
                write_exclusive(folder / (label + "-stderr.txt"), diagnostics)
            outputs[label] = {
                "path": str(path), "sha256_before": observed[name],
                "window_start": hex(start), "window_end": hex(end),
                "decoded_instructions": instruction_count,
            }
        data_outputs = {}
        table_fixups = {}
        if args.review == 'entry-lifetime':
            for name in ('FLT', 'ASLFoundation'):
                chains, diagnostics = run_tool(
                    ['/usr/bin/xcrun', 'dyld_info', '-arch', 'arm64', '-fixup_chains', str(INPUTS[name][0])])
                require(not diagnostics.strip(), 'entry fixup chains produced diagnostics')
                fixups, diagnostics = run_tool(
                    ['/usr/bin/xcrun', 'dyld_info', '-arch', 'arm64', '-fixups', str(INPUTS[name][0])])
                require(not diagnostics.strip(), 'entry fixups produced diagnostics')
                table_fixups[name] = (fixups, chains)
                write_exclusive(folder / (name + '-fixup-chains.txt'), chains)
                ranges = [(a, a+n*8) for _, image, a, n in DATA_WINDOWS[args.review] if image == name]
                selected = []
                for line in fixups.splitlines():
                    match = re.match(r'^\s*__DATA_CONST\s+__const\s+0x([0-9a-fA-F]+)', line)
                    if match and any(a <= int(match[1], 16) < b for a, b in ranges):
                        selected.append(line)
                write_exclusive(folder / (name + '-table-fixups.txt'), '\n'.join(selected)+'\n')
        for label, name, start, count in DATA_WINDOWS.get(args.review, ()):
            require(name in names, "data image not included in review identity")
            script = lldb_data_script(INPUTS[name][0], start, count)
            script_path = folder / (label + "-inspect.lldb")
            write_exclusive(script_path, script)
            output, diagnostics = run_tool(
                ["/usr/bin/xcrun", "lldb", "--no-lldbinit", "--batch", "--source", str(script_path)],
                timeout=60)
            require("error:" not in (output + diagnostics).lower() and
                    "fatal:" not in (output + diagnostics).lower(), "lldb reported a data inspection error")
            values = validate_data(output, start, count)
            write_exclusive(folder / (label + "-data.txt"), output)
            if diagnostics:
                write_exclusive(folder / (label + "-stderr.txt"), diagnostics)
            data_outputs[label] = {"image": name, "start": hex(start), "word_count": len(values),
                                   "interpretation": "file-backed serialized words, not runtime pointers"}
            if args.review == 'entry-lifetime':
                data_outputs[label]['table_evidence'] = verify_entry_table(
                    values, *table_fixups[name], label)
        if args.review == "lifecycle":
            fixups, diagnostics = run_tool(
                ["/usr/bin/xcrun", "dyld_info", "-arch", "arm64", "-fixup_chains", str(INPUTS["PLUG"][0])])
            require(not diagnostics.strip() and
                    re.search(r"pointer_format:\s+6 \(DYLD_CHAINED_PTR_64_OFFSET\)", fixups),
                    "reviewed PLUG fixup format was not confirmed")
            write_exclusive(folder / "PLUG-fixup-chains.txt", fixups)
        after = {name: validate_input(*INPUTS[name]) for name in names}
        require(observed == after, "input files changed during collection")
        record = {
            "schema": "AEHL-C1-RESOURCE-ABI-1",
            "scope": "offline-bounded-resource-" + args.review + "-only",
            "review": args.review,
            "source_commit": commit,
            "live_ae_operation": "NOT RUN",
            "plugin_scan": "NOT RUN",
            "inputs": outputs,
            "data_windows": data_outputs,
        }
        if args.review == 'publication':
            record['publication_evidence'] = publication
            record['missing_effect_route'] = 'placeholder-only-not-real-plugin-loading'
            record['native_registration_ABI'] = 'UNKNOWN'
            record['isolation_from_general_plugin_state'] = 'NOT PROVEN'
            record['registration_apply_render'] = 'NOT RUN'
        if args.review == 'effect-readiness':
            record['readiness_evidence'] = readiness
            record['native_registration_ABI'] = 'UNKNOWN'
            record['receiver_thread_and_provider_lifetime'] = 'NOT PROVEN'
            record['failure_atomicity_and_safe_rollback'] = 'NOT PROVEN'
            record['registration_apply_render'] = 'NOT RUN'
        if args.review == 'effect-dispatch':
            record['dispatch_evidence'] = dispatch
            record['native_registration_ABI'] = 'UNKNOWN'
            record['actual_procedure_and_provider_identity'] = 'NOT OBSERVED'
            record['canonical_state_rollback'] = 'NOT PROVEN'
            record['receiver_thread_and_provider_lifetime'] = 'NOT PROVEN'
            record['registration_apply_render'] = 'NOT RUN'
        if args.review == 'provider-factory':
            record['provider_factory_evidence'] = retention
            record['native_registration_ABI'] = 'UNKNOWN'
            record['actual_provider_and_canonical_identity'] = 'NOT OBSERVED'
            record['reference_counts_and_map_changes'] = 'FILE ONLY'
            record['safe_unregistration_and_failure_rollback'] = 'NOT PROVEN'
            record['receiver_thread_and_provider_lifetime'] = 'NOT PROVEN'
            record['registration_apply_render'] = 'NOT RUN'
        if args.review == 'entry-lifetime':
            record['entry_lifetime_evidence'] = entry
            record['native_registration_ABI'] = 'UNKNOWN'
            record['actual_provider_descriptor_procedure_identity'] = 'NOT OBSERVED'
            record['CFBundle_lookup_may_load_code'] = True
            record['final_executable_unload_and_quiescence'] = 'NOT PROVEN'
            record['safe_unregistration_and_failure_rollback'] = 'NOT PROVEN'
            record['registration_apply_render'] = 'NOT RUN'
        if args.review == 'ownership':
            record['ownership_evidence'] = ownership
            record['actual_record_identities'] = 'NOT OBSERVED'
            record['allocation_lifetime_quiescence'] = 'NOT PROVEN'
            record['safe_repeat_invocation'] = 'NOT PROVEN'
        archive = package(folder, record)
        print("PASS: bounded offline " + args.review + " evidence only; Adobe calls=0")
        print("Report: " + str(archive))
        print("Report SHA-256: " + sha256(archive))
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile) as error:
        parser.exit(2, "BLOCKED: " + str(error) + "\n")


if __name__ == "__main__":
    main()
