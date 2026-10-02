# AE Development Rules 6.2.0 adoption

Adopted 2026-10-02 at the user's explicit request to continue under v6.2.0.
Product baseline: clean `bed0de67d7e91b56ac51d5c9efb39653f0a534ad`, research
branch. Previous accepted 6.0.0 source and dated Evidence remain historical.

- Published [v6.2.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v6.2.0),
  annotated tag object `8b701f41512330914edb4a5a22b0da644f0c54e9`, peeled source
  **d966078a9e45fee7ec9ad14f211a9da753d64b8a**. Release/tag/commit/VERSION verified.
- Previous baseline: `bb8b769404ddd5b97462812a4e6b430e8bfefe13` / 6.0.0.
- Read new AI_ENTRYPOINT first, then the baseline diff, Engineering §21/§34,
  Process scope/API/safety, Tools, Native and changed Release §26.
- Adoption is documentation/process, Light/Development. Continued C1 research
  and capture preparation are Critical/Development with diagnostics/testing/IPC;
  product contract covers them, without new product discovery/reference parity.

## Applied changes

| Area | Project action |
|---|---|
| COMPAT-001 / Engineering §21 | Record exact AE build/platform/candidate and separate Test Status from Compatibility Status. No range interpolation or future-host default support. |
| API/artifact audit | Reuse pinned research/API evidence; track wrappers, indirect/generated paths and material omissions. SDK label/build PASS is not a documented minimum AE. |
| Missing capability | Keep bounded safe refusal tests. Own adapter PASS is not another AE version's ABI/runtime proof. |
| Remote checks | An exact portable packet can enable a test on another machine; preparation does not authorize sending, installing or launching. No local installation of all AE versions required. |
| REL-DOC-001 from 6.1.0 | Verify candidate-specific install/start/compatibility/limits before release; after publication link the release and current guide. Existing release remains blocked. |
| Render know-how | Reusable guidance only; historical observations do not certify this tool's registration/apply/render. |

Current C1 compatibility scope is recorded in
[C1_COMPATIBILITY](C1_COMPATIBILITY_2026-10-02.md), retaining exact older live
candidate identity. No full product compatibility audit is claimed. The new
identity capture adapter needs its own source-bound evidence and future candidate
record. Unknown private repeat/lifetime contracts still block resource scanning.

## Migration checks

At the exact clean standard source above:

- Full `self-test.mjs --dry-run --require-posix` PASS: 136 files, 43 executed
  test cases; two Windows-only cases skipped, PowerShell NOT RUN locally.
  Node/POSIX/macOS behavioral/native checks ran. No model/product/AE runtime
  certification is inferred from these checks.
- Generated applicability map `--check` PASS.
- Actual migration and C1 research router contexts PASS; selected rules match
  manifest/canonical sections, including API-SOURCES and diagnostics/testing/IPC.
- Standard checkout remains clean. No standard code/tool schema changes copied
  into product; project-owned journals remain separate protocols.
- Active product baseline headers/entry links updated to this immutable source;
  dated native reports are not rewritten. Final link/diff checks recorded in Git.

Native helper/profile/product bytes are unchanged by adoption. Prior decoder code
`15c528f6d7dabad83e7203970fc8a09bb2b7e710` retains its separately identified local
and CI evidence. Migration neither renews consumed observe-d548b007e316 authority
nor creates permission for private calls, teardown/replay, install or another AE
launch. Earlier release authorization remains valid only after its actual gates.

Rollback uses a reviewed change to accepted source/policy links, preserving all
Evidence and user data; never move released tags or reinterpret old reports.
