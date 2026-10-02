# AE Development Rules 6.0.0 adoption

Adopted on 2026-10-02 after the user's explicit "выполняй" response to the
proposed project migration. Product baseline before this documentation stage:
clean `c8c56fa5bd2fa0554cb7828fbc99d7fadd0ee58d`, research branch.

- Previous standard: VERSION 5.0.0 at accepted project source
  `b27f45467e0a9152fc82c1072438dfed07f0c36e` (not a claim that it is the later
  published v5.0.0 tag's commit).
- New standard: published [v6.0.0](https://github.com/ios3kov/AE-Development-Rules/releases/tag/v6.0.0),
  annotated tag object `779aa675cbb5e9f605b4051a797b43c11732d6ec`, peeled commit
  **bb8b769404ddd5b97462812a4e6b430e8bfefe13**. VERSION, tag and source checked.
- Change scope: accepted engineering/distribution policy and documentation.
  Existing product contract covers this work; no new product discovery or
  external-reference parity task. Product runtime/artifact bytes unchanged.
- Current product work: Stage C1, Critical native/IPC research, Development.
  Eventual Release is authorized by the user's earlier publication request;
  readiness and concrete live authority retain their separate scope.
- No approved deviation is created. Canonical task state remains
  [DEVELOPMENT_STATUS](DEVELOPMENT_STATUS.md) and the current continuation handoff.

## Reviewed changes and applicability

Compared old accepted source with the released tag, including AI_ENTRYPOINT,
CHANGELOG, Engineering §34, Process, Workflow, Tools §22, Release §§26/28/30,
reading manifest, versioned errata and 6.0.0 migration notes.

| Area | Adopted behavior | Project action |
| --- | --- | --- |
| AI entry / reading map | Frozen source plus applicable component/risk/delivery and feature overlays; bugfix DEBUGGING and research API-SOURCES | Pin AGENTS/status/plan/handoff; use IPC, diagnostics and testing overlays for C1 |
| Validation / Release | Pre-handoff, intended user-validation and release-acceptance are distinct; mandatory safety gaps still block | Clarify scoped test-build handoff separately from full product release |
| macOS distribution / MAC-001 | Unsigned/ad-hoc artifacts may qualify after integrity, selected delivery, documented install and actual AE load | Remove certificate/service assumptions; keep real install/load and product gates open |
| Windows / WIN-001 | Equivalent integrity/install/load scope without certificate/timestamp prerequisite | N/A to current Mac-only native experiment; no new Windows support claim |
| IPC recovery | Unknown outcome is not rollback or success; preserve operation/session evidence and block unjustified retry | Retain consumed one-shot claims, native journals and no-retry supervision; no new transport behavior |
| Tool schemas / interfaces | Current artifact/snapshot format v2; macOS wrapper takes artifact + new evidence dir, Windows takes Target + EvidenceDirectory | No copied starter-kit tools or legacy wrapper callers exist in this product; no caller replacement required |

Old product-owned artifact/journal schemas are independently reviewed protocols,
not starter-kit artifact records. Keep their original verifier/Evidence together;
do not relabel them as v2 attestations. When adopting starter-kit artifact tooling
later, use the complete pinned scripts/lib and fresh records, not old signing
arguments or old reports. Its integrity PASS cannot become installation or AE
loading PASS. Current candidate build-profile local ad-hoc checks stay intact.

## Selected rules

The released manifest/router was exercised with explicit covered-contract
context, no product-scope change and JSX/helper/native components:

- This migration: documentation, Light, Development; adoption/mac-distribution
  overlays. CORE-SCOPE, GIT, DOCS, EVIDENCE, STATE, WORKFLOW, STANDARD-VERSION,
  ADOPTION, MAC-DIST. No Product Discovery or Reference Audit triggered.
- Continuing C1: research, Critical, Development; IPC/diagnostics/testing overlays.
  Process scope/Git/identity/baseline/regression/evidence/safety/completion/state;
  Engineering code safety/test cases/performance/compatibility/reproducibility/
  dependency/API/debugging/diagnostics; Tools §22 and Native §23.
- Eventual release: Critical with GATES/MAC-DIST/PRODUCT-VERSION and the relevant
  runtime/risk rules above. This selection does not authorize a host operation
  or certify an unverified product.

## Migration checks

At the exact clean standard commit above:

- Generated applicability map `--check`: **PASS**.
- Actual router contexts for migration/C1/release: **PASS**, all returned IDs
  validated against the manifest and canonical source headings.
- Full `self-test.mjs --dry-run --require-posix`: **PASS**, 132 files checked;
  behavioral smoke PASS; 43 executed test cases PASS, two Windows-only cases
  skipped. Node/POSIX/macOS checks ran. PowerShell/Windows execution **NOT RUN**
  locally; no product/model/AE runtime certification is inferred.
- Private self-test log SHA-256:
  `588f4b32f63ca114d7d5053890be10e7672757fb050468017a0e88f9d8f2ff41`.
- Active product caller search: no legacy standard distribution-wrapper
  invocation or copied starter-kit tooling. Historical dated descriptions remain
  tied to their original policy/source.
- Product documentation consistency, changed local links and pinned-source
  references: **PASS**. Four active baseline headers agree with the released
  version/peeled commit; both entry links are immutable; 25 local links in the
  six edited/added Markdown files resolve. `git diff --check` PASS. Diff review
  confirms documentation-only changes; README's stale C0 NOT RUN claim now points
  to the already preserved live PASS. No old native evidence is rewritten.
  No product tests rerun for
  this documentation-only migration; latest product code f4f84aa retains its
  identified local/CI evidence, which is not a new v6 runtime test.

This documentation/policy migration is complete. Migration does not consume live permission, repeat C0, create a tag/release,
alter main or erase historical evidence. Ordinary-effect late registration and
apply/render remain unverified. The pending concrete diagnostic scope remains
required after the earlier automatic-review rejection.

Rollback: restore the project's previous accepted SHA and corresponding policy/
tooling references via a reviewed Git change; preserve new Evidence and user data.
Do not move released rules tags or silently reinterpret old reports.
