# AE Hot Loader — known static-audit candidate closeout

Date: 2026-10-01. Branch: `research/ordinary-plugin-discovery`.

This record closes only the **five previously recorded scanner candidates**. It
is not a new full repository security audit and does not promote the release
gate to PASS.

Shared DEVELOPMENT_RULES blob rechecked unchanged:
`701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`.

## Previously recorded candidates

Historical records identified five candidates:

1. unpinned `actions/checkout` in `.github/workflows/dual-pipl.yml`;
2. floating `dtolnay/rust-toolchain@stable`;
3. unpinned `actions/upload-artifact`;
4. default checkout credential persistence;
5. a scanner "rate-limit" finding at `tools/artifact_manifest.py`.

The fifth item was already reviewed as a false positive: that location is local
`argparse` CLI handling and contains no authentication endpoint or network
rate-limit path.

## Changes

Commit `54eb513dc3526f75f1446e3a80223fa3a06eea7c` changed the dual-PiPL
workflow to use the same pinned action commits/toolchain policy as the current
research/product workflows and disabled checkout credential persistence.

A follow-up at `da5d3a8e5a69b9cb719997ddba835e1a56f5d896` kept the
standalone dual-PiPL generator build valid: it has no committed standalone
Cargo.lock, so `--locked` is not claimed for that manifest. Its direct
`pipl` Git dependency remains pinned to an exact revision in Cargo.toml.
The normal core build remains `--locked`.

## Focused verification

All four workflow files currently under `.github/workflows/` were inspected.

Focused policy result:

- no workflow `uses:` reference remains on a floating tag/version;
- every `actions/checkout` occurrence has `persist-credentials: false`;
- the former `artifact_manifest.py` candidate still resolves to local
  argument parsing, not a network/authentication implementation.

This is a focused source-policy review only. The historical scanner itself was
not rerun here, so the correct overall status remains:

**known five candidates: resolved/classified; full static-security audit: NOT RUN.**

No AE process, Adobe library, plug-in installation, project, preference,
provider reference or private host function was touched by this closeout.
