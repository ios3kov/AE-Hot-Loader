# Stage C: bounded scoped discovery harness and CI checkpoint

Rules: `701a8c1ae3acb4dbfe1d7eda94acbf8095b88608`. Extends the
[research module build](SCOPED_DISCOVERY_BUILD_2026-09-29.md) and its
[predeclared plan](SCOPED_DISCOVERY_PLAN_2026-09-29.md).

## Latest identities

- Clean tested source: `1a67e7e81ff0362fa6617b7f6a453f857051e352`.
- Local research AEGP Build ID: `scoped-938e28da8c55`.
- Local directory: `build-ae-hot-loader/scoped-938e28da8c55/`.
- Research manifest SHA-256: `eda99a2dcf50f9fae4103becd0558538a4586e41e7a6aaaf56975f3fc3ae8a13`.
- Signed research binary SHA-256: `b8e2e46eccb34f2b2bafbacb023b4c636b47a2c327119c7b2c0eb9aab430fe2b`.
- Research resource file SHA-256: `6f3046ae7a5271217042ffe4e29baa9fffd946f44c6518745909196581567bbf`.
- Fixture remains `88019a1a01a7`; exact manifest hash is pinned in this build.
- Separate CI product package Build ID: `native-36565765080-1`.

The research module is not included in the ordinary product package. Its SDK
build/signature/export/identity/inert-entrypoint gates were run locally from
the clean source above. Full product CI verifies the ordinary package and the
added platform-appropriate tests; it does not run AE or the research AEGP hook.

## Supervisor and atomic publication

`run_scoped_discovery.py` verifies a supplied manifest SHA-256, research Build
ID/image, installed bundle hashes, exact test PID/executable/start time and an
unused private evidence directory. It launches and stops no process. Without
`--execute` it only checks preparation. With it, the supervisor publishes one
PID-addressed request, waits at most the selected 1–60 second polling deadline,
and independently checks claim, loader return, project revision and exact
registry delta. Each process-identity query also has a bounded 5-second `ps`
timeout; total wall time can exceed the polling deadline by that query time.

On exit, changed identity, native failure or timeout it records FAIL and keeps
the pending state. An exclusive supervisor claim prevents overlapping runners
and automatic retries. A stopped or unresponsive AE is never killed by this
tool. Existing crash correlation tooling remains available for a later failed
live run; this supervisor alone does not attribute a crash cause.

Review found two publication races before any live use: hard-link publication
temporarily gave a request two links, which the native reader rejects, and a
direct final-file write could expose a partial result. Requests and native
records now use fully flushed temporary files plus macOS `RENAME_EXCL`.
Existing records cannot be overwritten. Failed temporary files are retained
where needed to prevent an uncertain native attempt from being retried.

## Executed evidence

| Check | Status | Result |
| --- | --- | --- |
| Local identified AEGP build/signature/exports/getter | PASS | Exact research binary above, outside AE |
| Native guards and inert entry | PASS | 15 guard cases + 3 inert entry cases |
| Node tests | PASS | 51 panel + 11 exact snapshot-script cases |
| Local/macOS Python regression | PASS | 106/106, including 6 supervisor cases |
| Linux Python regression | PASS | 102 passed; four macOS-only publication tests N/A on Linux and passed on macOS |
| Research CI | PASS | [36565764998](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36565764998), exact tested source |
| Full macOS CI | PASS | [36565765080](https://github.com/ios3kov/AE-Hot-Loader/actions/runs/36565765080), all build/sign/package/roundtrip and seven existing standalone native gates |
| Static audit | FAIL | Five unchanged findings; four legacy dual-pipl workflow issues plus CLI rate-limit heuristic |
| Live preparation | BLOCKED | Read-only check returned `test host is absent`, exit 2, before request publication |
| Live registry/apply/render | NOT RUN | Research module not installed or activated in AE |

Local `offline-checks/node-tests.txt` SHA-256:
`3a7ed0995c809b287deb1c54eef6c4272bcbbbf0231f7238275fc7397bbacfce`.
`offline-checks/python-tests.txt` SHA-256:
`a60443d39395d9a692452a74ce70f3863dea1efbac34d3056133eec104be715b`.
Clean-source static audit is in the current chat's
`work/scoped-supervisor-final-audit.json`, SHA-256
`6f78ec0878e8b3cf0aa5a455edd9a8b33361f790f5ec6debd5a90cd2010eae9f`.

GitHub artifact IDs/digests returned by GitHub (archive bytes not downloaded):

- Research evidence `11032216124`, SHA-256
  `25f6c9738d5208af09b14305a47dd7c27636f24625d38bd110124a5d1d478f3c`.
- Native evidence `11031623975`, SHA-256
  `6b4be3217db7e1369189c3b46fa98d9c5a629d03f789ca5907c3704aac8dea1d`.
- Internal product artifact `11031319142`, SHA-256
  `b387621cf005554d49a4c3eb41e8e457e461fb8f466dd1c86c0ff7b697c94883`.

Earlier checkpoint `75fe324` also passed research run `36565208112` and full
macOS run `36565208105`; it is superseded by the exact source evidence above.
All development commits were pushed to `research/ordinary-plugin-discovery`.
Remote main remains `cf338bcd861504d695c3181767c18bb423575814`.

## Remaining runtime gate

Provide a dedicated AE 25.6x101 test environment with controlled preferences,
caches, plug-in roots and IPC. The pinned test-host path is currently absent;
a copied app path or token alone does not establish isolation. The research
build pins local absolute paths and should be rebuilt inside another machine
or account, not moved and silently reused. Once that host is established,
verify readiness and execute the supervisor for one scoped registration check.

Historical late-registration FAIL and crash evidence remain unchanged. Neither
offline harness tests nor CI repair legacy/RSMB registration. This is no release
or installable handoff. A documentation-only successor records these results;
it does not rebuild or replace the tested artifacts and uses the rules' limited
documentation check instead of rerunning the native CI pipeline.
