# Stage C: second live no-scan directory gate — PASS

Date: 2026-10-01. Branch: `research/ordinary-plugin-discovery`.

This record preserves the second authorized live no-scan FILE directory-lifecycle
attempt. It closes Stage C0 only. It does not prove ordinary-effect registration.

## Exact live identity

- source commit: `182d058254203236414602acdd9901b8749d89cc`;
- build ID: `noscan-8f9cb9fea71c`;
- run ID: `directory-probe-d097765fede949f5b9958b2897687df2`;
- AE: 25.6x101 arm64;
- PID: 34888;
- process-start identity: `1790858980.871652`;
- report ZIP SHA-256:
  `f767e891359a3e73dc41eefe4124fe63dc0cf4dde123c2d7efa7444cd35bc62a`.

The uploaded ZIP was independently rehashed after the run. Its outer SHA-256
matches the launcher output. Its archive inventory exactly matches
`report-hashes.json`, and every archived payload hash verifies.

## Live result

Final status: **PASS**.

Supervisor reason:

`exact no-scan directory lifecycle; same host/providers/bundle`

No plug-in scan was requested.

The durable native lifecycle evidence is exact:

- invoked = 1;
- completed = 1;
- cleanup_ok = 1;
- strings_created = 2;
- string_release_attempts = 2;
- specs_created = 1;
- spec_release_attempts = 1;
- retained_references = 3.

The durable transaction result is also exact:

- status = PASS;
- stage = complete;
- reason = `directory-roundtrip-release-only`;
- claimed = 1;
- call_started = 1;
- native_observed = 1;
- postflight_observed = 1;
- cleanup_ok = 1.

## Before / after host evidence

Before and after observation payloads are byte-identical.

Preserved values:

- project revision: 1;
- effect registry count: **785**;
- registry identities unchanged;
- runtime image count: 1402 before and 1402 after;
- no lazy system images were added in this run;
- PID, process-start, host path, helper path and project state remained unchanged.

Provider file identities remained the reviewed values:

- FILE.dylib:
  `df0db4a31955f1890b9bd6b1bff0f28c753824f63e4736721172e8697326f864`;
- U.dylib:
  `aecabb33c5ac5948ad742848c46588398bc690411b70aae7ca3f08a919362daa`;
- dvacore:
  `cb6faaf5b745903b80b44105b658ab68186d5065ae47c8a57c9b23e26aa8ecb0`.

## What this proves

For this exact AE 25.6x101 arm64 process and exact identified helper/provider
set, the reviewed private FILE directory lifecycle completed successfully:

1. one owned path was converted to the reviewed host string form;
2. one host FILE directory specification was created;
3. the path roundtripped exactly;
4. temporary host strings were each released once;
5. the specification was released once;
6. exactly three already-loaded provider references were retained;
7. the project, registry and runtime image set remained unchanged;
8. one report ZIP was produced and independently verified.

This closes the no-scan FILE ownership/binding gate **C0 = PASS**.

## What this does not prove

It does not prove:

- `PLUG_Search` safety;
- ordinary-effect registration;
- effect application;
- rendering;
- repeatability of a resource-registration pass;
- release readiness.

The historical ordinary-effect late-registration result remains FAIL:
source `45de0c9`, Build ID `scoped-0b8c8f122e80`, 785 unchanged effects.

RSMB startup apply/render PASS and RSMB late-registration FAIL remain separate.

## Next gate

Stage C1 may now proceed **offline**:

1. review end-of-pass callback and retained-state semantics for the single-root
   resource pass;
2. freeze the exact one-shot resource-registration contract;
3. build a fresh embedded ordinary-effect fixture and exact identified helper;
4. define acceptance as one new intended effect registry identity in the same
   AE process, with unchanged project state and no unrelated runtime changes.

A live C1 resource-registration attempt is a new risky private host operation.
The second no-scan authorization is consumed by this PASS and does not authorize
that later call.
