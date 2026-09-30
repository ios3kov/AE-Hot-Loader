# Stage C: aelib connects the resource pass, predicate and setter

Date: 2026-09-30. Review ID: `aelib-resource-pass-L6qzA9`.
Continues `7791cee394222aa29d6eb9c9a4a2f8757f7dcccc` on
`research/ordinary-plugin-discovery`. AGENTS, current status and stage C of
PRODUCTION_PLAN were consulted. Shared rules were rechecked unchanged:
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Scope and acceptance

Verify the newly supplied binary, decode the initialization dispatch table,
identify the ordinary resource-search caller and concrete path predicate,
connect the MEE setter to FLT, and distinguish startup evidence from late-call
safety. Preserve inputs and prior runtime results. No Adobe binary execution,
AE connection, installation, scan, restart, unload or private function call.
No product or collector source changes and no installable artifact handoff.

## Input identity

Upload `AEHL-aelib-bin.L6qzA9.zip`: 496901 bytes, SHA-256
`2d6b23d347c94116a6d982719bef7d843a9e3561c68004bb9b08698f10c19d80`.
Exactly three expected flat files were read into a new private workspace;
archive links and unexpected paths were rejected.

| File | Bytes | Independently calculated SHA-256 |
|---|---:|---|
| aelib | 2028432 | `f6124504c8eea332ef257bf1111e6db656c2e07bb57a7b178ec775020ba5407f` |
| SHA256-before.txt and SHA256-after.txt, each | 72 | `a7f1414a5f7c92b5e0c0933a48da0335bbd792fdbebca33eec2140055ccd129f` |

The before/after statements are byte-identical and both match the received
binary. This establishes received-file identity, not its identity in the
historical failed process or today's resident AE.

The single arm64 slice begins at file offset 16384, length 2012048.
UUID: `17942DAF-6B13-30C3-9CBC-AB42AB3D0F1F`.
LLVM 17 decoded the complete __TEXT,__text address range: 139753 addressed
instructions, no missing addresses or unknown instructions, empty stderr.
Decoding coverage is not exhaustive semantic review or runtime execution.
Proprietary binary, raw disassembly and symbol inventories remain private.

## 1. The ordinary resource pass is separate and earlier

Addresses below are unslid static references into the identified aelib image,
not callable production offsets or a verified private ABI.

`aelib::InitIterator::operator++` starts at 0x61134. Its switch reads 35
unsigned 16-bit table entries at 0xaae84. The branch base is 0x6118c and each
entry is multiplied by four. The decoded table establishes these stage indices:

| Index | Target | Observed normal-path work |
|---|---|---|
| 13 | 0x616ac | Install the concrete path predicate through PLUG_Birth |
| 26 | 0x6140c | Initialize hardcoded-plugin cache, then FLT_Birth at 0x61420 |
| 31 | 0x61a80 | Required resource presearch, then Egg_PlugSearch |
| 32 | 0x613c4 | Install standard suites |
| 33 | 0x61558 | Install MEE setter, LoadAEPlugins, then module notifications |

The normal completion at 0x61bcc increments the iterator index. These are
indices in this binary, not public stage constants or an executed startup trace.
The resource pass at index 31 precedes the AELibrary pass at index 33.

At 0x61ae4 the resource stage calls PLUG_RequiredPreSearch. At 0x61b04 it
calls the local `Egg_PlugSearch` helper, 0x63914. A second initializer-callback
implementation also reaches that same helper at 0x6f22c. Which initialization
mechanism is active in a particular running host is not established here.

Unlike the earlier AfterFXLib preset caller, this is the plugin initialization
path sought in the previous iteration. There is no need to repeat the
AfterFXLib, MEE, PLUG or FLT collections to establish this static connection.

## 2. Egg_PlugSearch supplies the ordinary folders and default sack

At 0x6394c, Egg_PlugSearch obtains folder FILE_Spec pointers and a separate
owner collection through MEE_GetPluginsFolders. It passes their count and
pointer array to PLUG_Search at 0x6399c. The count is narrowed to a signed
16-bit value; the pointer array is not a raw string array.

The observed call also supplies a null first sack argument, short values zero
and ten, the SearchStatFunc callback, and references to error/cancel outputs.
The null-sack handling exists in the already supplied PLUG implementation.
These argument observations do not establish the general meaning or safety of
all flags. The helper cleans up its folder and owner storage after the call,
and a nonzero search result takes an exception path at 0x63a50.

Consequences for a proposed late-registration experiment:

- Do not call Egg_PlugSearch directly: it obtains the ordinary global folder set,
  not a single approved fixture root.
- Do not fabricate FILE_Spec objects or copy an array of pointers without their
  owners. The normal caller explicitly retains owner storage during the pass.
- Do not rerun InitIterator, Birth, RequiredPreSearch or general initialization
  as a substitute for a bounded registration test.

## 3. The concrete skip predicate is a hardcoded-cache lookup

The PLUG_Birth callback pointer assembled at 0x616ac-0x616bc is
`SkipHardcoded_PLUGScanFunc`, 0x62314.

Its body calls MEE_HardcodedPluginsCache::GetInstance at 0x62324, then
GetAEPlugin(path) at 0x6232c. The comparison and conditional result at
0x62330-0x62334 return true precisely when that lookup is non-null.

The previously inspected PLUGp_ScanFile invokes its stored predicate at
PLUG 0xf750 and skips the file on true at 0xf770. Together these files identify
the skip condition: an existing hardcoded-cache entry for the path. They do
NOT establish the cache contents, path normalization, predicate result or
receiver during the historical embedded test. No cache modification or bypass
is justified by this observation.

## 4. The dynamic setter is now connected to its implementation

At 0x61558-0x61570, index 33 installs local SetupAEPlugin, 0x63aa0, through
MEE_SetAELibPluginSetter. It then calls PluginSupport::LoadAEPlugins at
0x6158c, MEE_GetVideoFilterModules at 0x6159c, FLT notification at 0x615a4,
and MEE notification at 0x615ac.

The local setter calls FLT_SetupAEPlugin at 0x63b34. A negative return takes
the AEGP fallback at 0x63bc4; a nonnegative result takes its success return.
That success return is not an independent effect-registry insertion check.

This closes the static setter-ownership uncertainty from the MEE/FLT reviews.
It does not authorize callback replay or establish the installed callback in
an arbitrary process. Nor does the presence of both notifications justify
blindly adding MEE notification to the product loader: resource enumeration
occurs in the separate earlier pass.

## Assessment and next implementation boundary

The files now show a coherent startup chain:

`PLUG predicate and FLT callback setup -> required/ordinary resource pass ->
standard suites -> MEE setter/AELibrary pass -> module notifications`.

Combined with the MEE resource-retention branch and our loader's absence of an
explicit resource pass, this strengthens the missing-resource-pass hypothesis.
It remains a hypothesis about the failed live run, not a proven root cause or
a demonstrated safe late-registration operation. The original embedded gate
remains FAIL. RSMB startup-registered apply/render PASS and historical RSMB
late-registration FAIL remain separate.

The next development task is a bounded research-gate design using the existing
scoped harness, not more blanket collection. Existing supplied files are
sufficient to specify that gate's purpose and constraints; they do not prove
safe private ABI, ownership or post-startup lifecycle behavior.

Before any execution, the design must resolve the FILE_Spec creation/ownership
contract, restrict input to one new owned embedded fixture root, preserve the
installed skip predicate, and exclude global-folder enumeration and lifecycle
reinitialization. It must refuse used one-shot evidence and nonblank/dirty/busy
projects, pin host and module identities, and record the exact registry delta
and unchanged project revision in the same PID. Timeout/exit is failure, not
permission to repeat. Apply/render is a separate gate.

This is a proposed scope, not an implemented or approved runnable experiment.
Any new installation, restart, debugger attachment or private in-host call
still needs separate authorization. No executable diagnostic or new user
command is requested by this record. A full application archive may simplify
future dependency inspection, but is not needed for the present design step.

## Structural checks and limits

A local file-only review checked FAT/load-command/section bounds, complete
text address coverage, decoded the switch table and checked 28 targeted
structural assertions: 16 BL targets independently decoded from instruction
words and 12 additional addressed anchors. All passed. These are not unit tests
or executed Adobe branches. The supplied PLUG predicate and search prologue
were reread for cross-file consistency.

| Derived evidence | SHA-256 |
|---|---|
| aelib disassembly | `f39777d0b760fa6a8e1776dedfbe9b22bec1da9a7cde74df4b6744aa5ded0db5` |
| Local review helper | `dfbeababb0b72b0029826400a8bf797b00664651d5d862f311cf2f0a88dea415` |
| aelib-review.json | `4c8822704a57a7419ebceb0bd96c84a0c8170070a10c251b9dcfdfb24dab397b` |

The review JSON contains input/slice hashes, switch targets, exact assertion
locations and four selected-window hashes. It is private derived evidence,
not independently acquired runtime evidence.

No product/collector source changed. Full Python/Node/native regression and
static-security audit were not rerun for this documentation-only continuation.
Five prior audit findings remain unresolved. Prior CI remains tied to code
1fa62a7; documentation commits use [skip ci]. Current AE/PID/project/loaded
identity is NOT OBSERVED; new live registration/apply/render is NOT RUN.
No native build, installation, restart, main change, merge or release occurred.
