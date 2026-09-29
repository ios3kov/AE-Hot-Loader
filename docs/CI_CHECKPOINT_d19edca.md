# RSMB apply/render harness checkpoint — 2026-09-29

Source: d19edca897bf2fec051ca6bc74d931416307759e.
Scope: test harness and research evidence only; no live AE apply/render claim yet.

## Automated gates

- Research checks #13, run 36546959381: SUCCESS.
- panel-contract job: 51/51 panel tests PASS; Python discovery: 87/87 PASS.
- New exact-JSX mocks cover success, dirty baseline, missing RSMB, canAdd failure, add failure and render failure.
- Native-syntax job: SUCCESS, including zsh parsing of the new launcher on macOS.
- Full macOS build #247, run 36546959423: SUCCESS; existing build/sign/package and native smoke gates remain green.

Evidence artifacts:
- research evidence 11022927246, SHA-256 073db8ae407948eab6e8942a502ee5b6261a3b82eb0d85ec0c60e84b3fdf2b74
- native evidence 11022917824, SHA-256 d3b4217eeff88e1c99eef80c576327d7870ffde00a4182c567e598756e37ebeb
- internal package 11022753169, SHA-256 665f34948ded69fc7a776a07e4d77ae48a64759aa0a78602e745e3b2773cf7c7

## Runtime handoff

The user-side preflight before this harness showed resident Agent identity PASS for
native-36483421984-1 / source 04fea7060c7ef7ebc4a315b5c39364850287e294,
a blank clean project and all three RSMB registry identities. Private report
details are intentionally not committed.

The handoff gate runs a fresh preflight, applies Smart Motion Blur 3.x by exact
match name in a disposable project, renders one 64x64 frame, closes without
saving, recreates a blank project, hashes output and runs postflight.

Real AE apply/render: NOT RUN at this checkpoint. Cold-start causality and late
registration remain separate NOT RUN / historical FAIL gates as documented.
