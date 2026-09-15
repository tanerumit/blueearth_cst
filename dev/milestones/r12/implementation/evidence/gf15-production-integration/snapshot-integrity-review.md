# GF15 Stage 1 snapshot integrity review

Reviewer: independent `python-engineer` subagent, 2026-09-14.
Reviewed source HEAD: `33c893502e399b7446d461ee851f849058505e72`.
Authority: [accepted design D8](../../../gf15-production-adapter-design.md#d8-metrics-only-migration-and-acceptance-sequence).

**Verdict: PASS WITH NOTES — snapshot integrity only.** The captured tree is
fit for the bounded old/new comparison while its original absolute collection
anchor remains available and byte-identical. This is not Stage 1 setup acceptance,
standalone portability, candidate adequacy, or permission to bypass remaining gates.
Linux and isolated environment qualification remain outstanding.

## Independent checks

Let `ROOT` be `C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3`,
`SOURCE` be `ROOT/.tmp/scratchpad/2026-09-11_0010/p3-final-direct`, and
`SNAPSHOT` be
`C:/Users/taner/workspace/blueearth_cst-artifacts/r12/gf15-production-integration/prechange/p3-final-direct`.

- Independently enumerated both complete trees using PowerShell
  `Get-ChildItem -LiteralPath <root> -Recurse -File -Force` and compared their
  relative paths with [source-inventory.json](source-inventory.json). After
  normalizing Windows separators to `/`, both have exactly 446 unique paths,
  no extras and no missing files. An initial unnormalized comparison reported
  separator-only differences; the normalized comparison resolved them all.
- Independently ran `Get-FileHash -LiteralPath <file> -Algorithm SHA256` and
  checked `Get-Item.Length` for every inventory entry in each tree: **892 file
  checks, zero hash or size failures**. Each tree totals **657,950,010 bytes**.
  No reparse points were found in either recursively enumerated tree.
- Checked `IsReadOnly` for every file: **446/446 snapshot files**, 0/446 original
  source files. Read-only is a Windows attribute, not a tamper-proof retention
  mechanism. Keep the snapshot outside all execution write targets.
- Rehashed the durably retained inventory: SHA-256
  `6483d1285b4e99c46f3587afa9c034956131d5802c77b1f02552d65f58fa7bb4`,
  matching the discovery record. Counts, sizes and attributes independently
  corroborate [snapshot-result.json](snapshot-result.json). Inspected the scratch
  `capture-snapshot.py`; the independent enumeration additionally checks coverage
  that its inventory-driven copy does not itself establish.
- Executed the existing `.pixi/envs/default/python.exe -B -` with read-only Python
  input that selected `artifacts.direct.paths` from `../p3/execution-evidence.json`,
  mapped those paths relative to SOURCE into SNAPSHOT, and called
  `read_metric_set(copied_experiment, copied_metric_manifest)` followed by
  `read_collection(copied_collection_manifest,
  describe_forcing=collection_forcing_descriptor, describe_ancillary=describe_ancillary)`.
  Both returned successfully, exit 0. No workflow or fitting was invoked.

The copied metric reader returns `ready`, metric set
`49ca015882e8396f4fd46930b9a95be3ccbd4dfcaf2d5c7840bf1b3df95aa665`,
simulation `3a8c1fc6c633687bb95736f3c5f76cf8ac323927db32af7f767f8bde03a41a10`.
The separately read copied collection returns id
`71bf34ef8db1122bb91f097ac63ff01e450cf0a16ad9a9d3cca64128fd23ba88`, revision
`5c21f75dc5cc4354ee32bd9983e1a39d55fea09944eb5bc20657dd8318010885`.
These match P3's explicit selection and the readiness record. The full-byte
checks cover its response inventory/request, native artifacts, unit index,
old environment, tables, member/coverage evidence, and all seven source configs.
The metric manifest hash remains
`74095313f3c83d1749a65a0a7ddafb59213e740bd69590b77e47ff5474ecad9e`.

## Provenance and retention boundary

The exact old argv in `../p3/operations-dedicated-reuse.json`, command label
`metrics-reuse`, is correctly reproduced by [stage-1-readiness.md](stage-1-readiness.md).
Fresh hashes match that command's retained log, `project_config_metrics.yml`,
and its actual selected `metrics-simulation.yml`: respectively `0788e4d6…91e61e7`,
`27b5463a…242c218`, and `474bc844…41f9433` (full digests in the linked records).
This proves provenance of the recorded successful complete-set reuse invocation;
it does not relabel that command as the initial generating invocation.

Compared all entries of P3's three source inventories: all have the same 193
paths; executed-to-reviewed changes only `scripts/run_workflows.py`, and
reviewed-to-commit changes only `generate_scenarios.smk`. Their before/after
hashes exactly match `comment-provenance.json` and `eof-provenance.json`.
The recorded base is `078f508d3ea3a2368d15602f68e7867daf400f3d`.
Retain those records with the historical source; the later committed inventory
must not be presented as the exact executed bytes. This review reconciles those
records, not a fresh reconstruction or rerun of the historical source tree.

The copied immutable `config/simulation.json` still selects the collection
under SOURCE. Its successful metric read therefore does not prove an independent
relocated experiment. The separate copied-collection read validates that copied
payload without changing the simulation record. Preserve the original anchor
and recheck its inventory before and after comparison; loss or mutation of it
invalidates this bounded reader arrangement. Execute new metrics in a distinct
working copy and retain the old manifest/context with the CSVs.

Verification scope: rapid / numerical unaffected, explicitly expanded to all
snapshot files and two readers because D8 requires independent integrity evidence.
No production changes, tests, lint, model runs, fitting, installs, baseline checks,
or full software/portability review were performed or needed for this verdict.
