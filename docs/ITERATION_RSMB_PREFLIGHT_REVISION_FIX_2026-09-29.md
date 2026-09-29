# RSMB preflight revision-metadata fix — 2026-09-29

## Baseline and reproduction

Harness source `d19edca897bf2fec051ca6bc74d931416307759e` compared each
preflight `project` object with an exact five-key dictionary. The real
collector also records a `revision` field, so an otherwise valid blank,
unsaved, clean and idle project was rejected.

Private Test Run ID `aehl-preflight-0e0287b149754565b82008f1d9826dea`
established:

- resident Agent identity: PASS;
- all three exact RSMB registry match names: PASS;
- project unchanged across preflight: PASS;
- blank/unsaved/clean/idle required fields: PASS;
- launcher validation: FAIL with `STOP: before project is not blank/clean`;
- JSX apply/render/cleanup: NOT RUN.

The private host report remains outside the repository and no project content
is recorded here.

## Change

Source `b3c30a09b6106c3c9f57e486bd621e4e2959954f` changes only the
launcher-side preflight validation and its regression tests. It checks the five
required fields individually with exact JSON types and values, while allowing
collector metadata such as `revision`.

The guard still rejects any nonzero item or queue count, saved or dirty
project, active render, missing field, or wrong field type. The JSX, Agent,
collector, plug-ins and product package are unchanged.

Corrected launcher SHA-256:
`1581aa7ba1c1ca0ceb12de2aa6fd4eda80e18fca2c3338ccd83592f726b9cbc5`.

## Verification

| Check | Status | Scope |
| --- | --- | --- |
| Reproduction test before fix | PASS | New test failed on real collector-shaped data with `revision`. |
| Focused harness tests | PASS | 6/6, including valid metadata and nonblank rejection. |
| Python discovery suite | PASS | 89/89. |
| Exact JSX mocks | PASS | 6/6. |
| zsh launcher parse | PASS | Corrected launcher parses on the target macOS host. |
| Corrected live RSMB apply/render | NOT RUN | Requires a new controlled execution of this identified runner. |

This local verification does not replace macOS CI or live AE evidence. A
successful corrected gate can prove only the scoped apply/render compatibility
smoke; cold-start causality and historical late registration remain separate.
