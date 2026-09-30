# Stage C: main-image imports narrow the next offline collection

Date: 2026-09-30. Review ID: `factory-main-Z7cgNu`.
Continues `e9993ef081b1cd0e7080064ec5ddbe0c716e2e0a` on
`research/ordinary-plugin-discovery`. AGENTS and the full previously read shared
rules remain applicable. The current shared rules blob was checked again:
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`, unchanged.

## Scope and predeclared checks

Verify and inspect the supplied main-image symbol/dependency archive, distinguish
imports from definitions, identify the next evidence source, and prepare bounded
offline collection without another AE scan. Check parser/command construction,
limits, error paths, source identity and applicable CI. No native product changes,
installation, AE restart, debugger attach, private invocation, main change,
merge or release. This is file inspection, not a proposed registration fix.

## Received archive

`AEHL-factory.Z7cgNu.zip`: 3,295 bytes, SHA-256
`0111e906b0813554740fbcc5d7f2380c76cba00ffb333c88c92de8d8e45aaa4b`.
All four entries were read; no duplicate names or symbolic links were found.
Input bytes were preserved. No supplied Adobe file content is committed here.

| File | Bytes | SHA-256 |
|---|---:|---|
| symbols.txt | 12549 | `250102a3b4a2881032c4d5fc93f51849c5016101957092b265402edd8228ae03` |
| libraries.txt | 2530 | `13f59245072e9e7e43531910a18cba4fd7ef6c6dc19410abbb7513700443ad90` |
| image-before.txt | 163 | `32eefa126d2ba32cc5d9eecabb4cc552a0208bacfe5e888dc75057bf4cb98ead` |
| image-after.txt | 163 | `32eefa126d2ba32cc5d9eecabb4cc552a0208bacfe5e888dc75057bf4cb98ead` |

Both image statements contain
`464ad678ca19ba78478e2989c42f42bea3fd95e51c9180c1556c53c973457df6`
and are byte-identical. The original executable is not in this archive; its
hash was reported by the user's collection, not independently recomputed here.
These inputs do not attest the current running host, project or loaded modules.

## Finding and limit

The complete supplied symbol table has 125 rows: 81 undefined imports and 44
addressed definitions. Definitions include data and metadata; this is NOT a
count of 44 functions. The table contains six imports attributed to AfterFXLib,
including `EggMain`, `UnifiedStartupParseArgs` and startup initialization.
`_main` is defined in the small entry executable, while those entry/startup
routines are imported from another image.

The arm64 dependency list explicitly names
`@executable_path/../Frameworks/AfterFXLib.framework/Versions/A/AfterFXLib`.
This makes AfterFXLib a concrete next search target, rather than continuing to
look for all implementation in the entry executable.

No matching factory/MEE/notification definitions were found by the declared
selector in this supplied main table. This is not proof that every possible
factory is absent, nor proof that AfterFXLib owns the particular factory GUID
selected in the preceding PluginSupport analysis. Symbol names do not reveal
runtime dispatch or hidden/stripped/inlined behavior. The concrete selected
factory, its PiPL acceptance and the reason for the live failure are unresolved.

The preceding [factory-dispatch analysis](REGISTRATION_DISPATCH_STATIC_2026-09-30.md)
still applies: do not flip the final bool, force an empty notification or add a
speculative registration call. The source code of the product loader is unchanged.

## Collector implementation

Source commit `d31b8da107a903f7e31520672e7256fbb50b0175` adds
`experiments/ordinary_discovery/collect_factory_image.py`.
Code/test checkpoint: `9fdb39b751c96f6e34adcf5df9d8f94183153b37`.
The collector Git blob is `f72624c35389eedf3ccb9c6b226b5acb2c8d7b15`;
its SHA-256 is
`10097a09b97876d6bbf4fce9c5abf5a5ebc300826d5dfefac906859a8863f89c`.
The local tested file was checked against that returned Git blob. The standalone
chat copy `AEHL-collect-factory.py` has exactly the same bytes; renaming does not
change its contents. This is a file-only collector, not an installable AE artifact.

The Python 3.9+ collector:

- Requires macOS and the known app location, pins the main executable to the
  hash above, resolves AfterFXLib inside that app, and records its first-observed
  hash. AfterFXLib does not yet have an independently supplied expected hash.
- Records nm symbols with import provenance, dependencies and Mach-O headers.
- Selects at most 96 relevant defined code addresses, prioritizing MEE and the
  notification boundary. Generic template/typeinfo matches are excluded. Names
  only guide selection; only validated numeric addresses enter LLDB commands.
- Captures at most 4096 bytes per selected address, stopping earlier at the
  next known text symbol. These are heuristic windows, not verified complete
  function extents. Missing matches, omitted addresses and capped windows are
  explicit; zero matches cannot be called successful factory identification.
- Uses offline LLDB target creation with no dependents, disabled init files and
  disabled symbol-file scripts. Its commands contain no attach, launch,
  expression, process control, breakpoint or private function invocation.
- Gives inspection subprocesses a timeout and a 64 MiB per-output-file limit.
  Those limits affect only tools started by this collector, not AE. It checks
  both inspected image hashes again before completing the archive.
- Writes only a new mode-0700 Desktop directory and a mode-0600 ZIP. Failures
  preserve partial evidence rather than deleting or reusing it. It never
  installs anything, edits user projects/preferences, publishes bridge requests
  or repeats the plugin scan.

The selector is heuristic and could miss the concrete factory or truncate a
large method. This collector is not promised to settle every remaining question
in one run. Supplied source names/addresses remain private in the resulting ZIP.

LLDB's documented offline target form and script-loading settings informed the
command construction; these are references, not proof of execution on this Mac:
https://lldb.llvm.org/use/symbolication.html
https://lldb.llvm.org/use/settings.html
https://lldb.llvm.org/man/lldb.html

## Verification

20 focused synthetic tests passed locally with Python warnings treated as
errors, covering nm formats, import/data exclusions, aliases, template exclusion,
priorities, bounds, path/command injection, hashing, non-mac refusal, bounded
subprocess invocation, failed tools and no output overwrite. Five additional
mocked full-flow cases passed in a local scratch runner: normal collection,
no matches, wrong main hash, changed library and tool failure. Their committed
counterparts are `tests/test_factory_collection_flow.py`; exact committed
whole-suite verification is assigned to CI, not asserted from the scratch run.

The selector was also run on both real supplied symbol tables: 0 matching
addresses in the main-image table and 13 in the earlier PluginSupport table.
No LLDB/AE invocation occurred in that check. The local Linux LLDB executable
could not start because its libpython3.11 dependency is missing; real offline
LLDB execution here is BLOCKED, not replaced by the parser tests.

At this record's creation, research CI for the preceding code/test checkpoint
`0ca114dd` passed (run `36745344775`), while its macOS run `36745344719` was
still running. The final test-only checkpoint is `9fdb39b`; its status must be
read separately before claiming final CI PASS. No prior CI is substituted for it.
This report is documentation-only and uses [skip ci].

## Preserved results and next gate

Latest real scoped registration: FAIL, source `45de0c9`, Build ID
`scoped-0b8c8f122e80`, target absent among the unchanged 785 identities.
RSMB startup-registered apply/render PASS is separate from historical RSMB
late-registration FAIL. Neither result is changed by this archive or collector.
The previous five static-audit findings remain open; that audit was not rerun.

The next user action is only to run the exact standalone file on the Mac and
return its new ZIP (or the error output). The collector does not need AE to be
open and must not be used as a reason to launch or restart AE. No git pull,
new plugin install, authorization token or elevated permission is required.

After receipt, inspect actual factory bodies and module-publication calls. A
new host experiment still needs a specific falsifiable hypothesis, fresh host/
project/runtime identity and separately authorized risk. The earlier installation
and one-restart permission remain consumed. No unchanged scan is authorized.
