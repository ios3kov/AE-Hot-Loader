# Stage C: PiPL disk-to-memory boundary

Rules blob rechecked unchanged: `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.
Baseline: SDK disk serialization equality PASS; resource-pair live timeout FAIL;
host exit cause unknown. Aim: distinguish file bytes from parser input without
launching/attaching to AE or executing private functions. Acceptance is bounded
offline inspection with stable image identity, not a runtime fix.

## Reproducible evidence

Collector source: `0aaedb5` (clean); profiles `parser` and `asl` in
experiments/ordinary_discovery/inspect_pipl_fallback.py. Earlier incremental
collector commits: e482472 and 061f8a9. New native Build ID: N/A; no native build.
Existing Agent remains `native-36483421984-1`; failed fixture Build `79a6ce4be9f7`.

Local evidence root: build-ae-hot-loader/evidence/. Proprietary disassembly
stays local and is not committed or distributed.

| Profile | Run ID | Disassembly SHA-256 |
|---|---|---|
| parser | pipl-static-930218e0c1bd492ba72a700b17239f2f | 3d7f16bb73f3434c6dd88fdd605db96e710205fc5e3750d722a205a95e12bec1 |
| asl | pipl-static-0045f2d7ad0040dbb42ae0e5703b1805 | f1ef484f772d682504c2060afdf04d197bc23a3e9fc320e2212887217b7ef2ce |

PluginSupport image SHA-256:
`4d2c200b198124b43887bbb7e53c9e48514621a54feb36085822852978b45832`.
ASLFoundation image SHA-256:
`f1c3c7256f8a986f39519387511436577a3d65fb9d04a672bbb115c1871a3fe7`.

## Observations and limits

1. PluginSupport URL LoadFromResource at 0x41cec obtains bytes through a
   virtual module call, copies them and calls SetPiPLValues. Its embedded
   resource overload at 0x41da8 also copies reader output and calls the same
   parser. Neither visible copy path performs a byte-order conversion.
2. SetPiPLValues at 0x3fd28 reads the property count with a native ARM64
   32-bit load at 0x3fd68 and property lengths with native loads. This is
   an in-memory representation, not automatically the SDK disk format.
3. PiPLFlipper::PiPLEndianFlipProc at 0x45474 contains explicit byte reversal
   of the header and property records. PluginSupport imports CoreEndian
   flipper APIs. This establishes a conversion implementation exists, NOT
   that it was registered/invoked in the failed process.
4. ASL Module URL reader at 0x24f00 calls ASL::LoadResourceFromURL at
   0x285fc. The inspected implementation opens the data fork, allocates and
   reads bytes with FSReadFork, then closes it. No PiPL conversion is visible
   in that function. The runtime virtual receiver remains unproven.
5. Exact failed flat payload hash remains
   `69730ece7f62bbfa15a1d610642cd3bcb2e4c29702654775daf33c4d6c9677b3`.
   Bytes at offset 4 are `00 00 00 0c`: big-endian 12 but little-endian
   201326592. First property length at offset 20 similarly changes from 4
   to 67108864 if consumed without conversion.

Conditional inference: if the raw flat payload reaches this parser via the
base ASL URL reader with no override/conversion, header/length interpretation
is incompatible and unsafe. This is a specific candidate explanation for the
flat experiment, not proof of its crash cause or of RSMB's registration issue.
The SDK equality check remains valid for DISK bytes; it never certified parser
input. Earlier standalone resource reads occurred without host flipper state.

## Decision and next gate

Do not repeat the raw flat-payload experiment in AE. Do not blindly swap the
production resource generator or modify third-party bundles: property values
have different types and runtime resource conversion is not yet traced.
First test the public Resource Manager/CoreEndian conversion boundary in a
standalone owned process, with a bounded synthetic resource and no private
host code. Separately establish the actual runtime module/reader dispatch in
an isolated host before any new full registration attempt. No full-root scan,
restart, install, preferences changes or private calls were performed here.

| Check | Result |
|---|---|
| Both offline collectors, stable exact images | PASS |
| Python regression after collector commits | PASS, 92/92 |
| Diff whitespace check | PASS |
| Static audit | FAIL: existing unpinned Actions/credential-retention debt; unchanged |
| Actual flipper invocation in failed AE session | NOT RUN |
| Original process-exit cause and registration repair | BLOCKED: no correlated runtime evidence |

Static audit again found the same five candidates; the CLI rate-limit finding
is the previously reviewed false positive, not a network issue. No release
readiness claim. Existing verified Dynamic application and RSMB smoke results
are preserved unchanged.
