# Registration-pair startup control and late-load comparison

Stage C of the A–D development plan; stages A and B still have open gates.
Rules reviewed: blob `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Existing evidence and question

The historical pair run `2e8c5394d5e6` registered the dynamic fixture but
not its PiPL-only counterpart. Preserve that observation. Neither fixture
implements rendering, so neither may be applied or rendered.

Before attributing the difference to late registration, establish that the
exact same two fixture binaries register during ordinary startup. A startup
failure would leave fixture validity unresolved. RSMB apply/render PASS is
separate and does not validate these fixtures.

## Prepared inputs

Build/run ID: `50a85fce3046`.
Clean source: `f393fbd7d7a98fead93bdb6f2982250db3d7b5e3`.
Builder: `experiments/ordinary_discovery/build_registration_pair.py`.
Apple clang 21.0.0, SDK 27.0, arm64; ad-hoc signing.
Local evidence: `build-ae-hot-loader/registration-pair-50a85fce3046/`.
Manifest SHA-256:
`c7c572870f38367969470f2ac400b336b619db816b82c4988fc25d35d2299d75`.

| Fixture | Exact match name | Binary SHA-256 |
| --- | --- | --- |
| PiPL-only | AEHL.PiPL.50a85fce3046 | fbba939e3a6dc550004e1c0660268a92c94fb9969766d53d7230926db5843f0d |
| Dynamic | AEHL.Dynamic.50a85fce3046 | c22c617353bf948545b69c869276dd3b698a42f8b49d0f9a45539baeb60e4ead |

Build, codesign verification and export checks: PASS. Both expose EffectMain;
only Dynamic exposes PluginDataEntryFunction2. These are build checks only.
Installation, controlled startup and new late registration: NOT RUN.

## Predeclared procedure and acceptance

1. Obtain authorization for test-only installation and controlled AE restarts.
   Immediately before each quit, require a fresh identified Agent and an exact
   blank, unsaved, clean, idle project. Stop on any change or uncertainty.
2. Inventory active roots and require both exact fixture names absent. Resolve
   one new test-owned installation directory; refuse any existing target.
3. With AE closed, copy only these two fixtures, verify every manifest hash,
   then launch the identified AE app. Capture PID/start identity, runtime Agent
   identity and a fresh registry. Require both exact names present. Otherwise
   record startup FAIL and stop; no late-load conclusion follows.
4. Close only the verified blank test host; move the hash-verified test-owned
   installation into the run evidence directory. Restart without the pair and
   require both names absent in a fresh registry snapshot.
5. Copy back the same fixture bytes, verify hashes, issue one identity-checked
   discovery request, and capture exact registry delta in the same PID. Record
   each fixture registration separately; loaded images alone do not pass.
6. Verify unchanged blank project and Agent identity. Retire only the exact
   owned installation after hash checks; retain all reports and fixture bytes.

Do not render the registration-only fixtures. Preserve RSMB and other installed
plug-ins, user preferences and projects. No private teardown/constructor calls.
If the PiPL fixture passes startup but fails late registration while Dynamic
passes both, the experiment supports a loader-path distinction for this pair.
It does not identify a safe missing registration API or establish an RSMB fix.

Local ignored build evidence is not durable release storage. No candidate is
being handed off and no runtime authorization is implied by this build record.
