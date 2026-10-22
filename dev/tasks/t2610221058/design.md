# WF2 production record and portable bundles: decisions

Resolves the [task brief](task-brief.md) decisions for the WF2 delivery (2026-10-22). Contract owners
after landing: `docs/guide/outputs.md` (user surface), `docs/site/toolbox-reference/workflow-analyze-projections.qmd` and the module docstrings named below.

## D1 Product-local production record

- Owner: new `blueearth_cst/shared/product_record.py`, called only from the WF0--WF2 launch sites
  (`workflow_archive_launch._run_workflow_started` and the WF0--WF2 branch of `scripts/run_workflows.py`).
  `execution_outputs.py` and `invocation_history.py` stay unchanged: they are in the WF3/WF4
  code-identity closure, so editing them would invalidate simulation reuse.
- Location: `<product>/_engine/execution/production.json` (`product-production/1`) plus retained copies of
  each contributing generation's `wf2.log`, `wf2-benchmarks.md` and `.tsv` under
  `<product>/_engine/execution/<invocation_id>/`. Central `logs/` and invocation records are unchanged.
- Attribution: the launcher hashes the product tree (excluding `_engine/execution/`) before the child
  starts and after `invocation_history.finish` merges diagnostics, inside the project execution lock.
  Changed or added files are attributed to the invocation; removed files leave the record; unchanged files
  keep their producer. No byte change means a no-op: neither the record nor retained diagnostics change,
  whatever the exit status. File timestamps are not used.
- State: `complete` when the latest changing invocation succeeded; `incomplete` when it failed (WF2 runs
  with `--keep-going`, and Snakemake clears `directory()` plot outputs before a job, so partial replacement
  is the normal failure shape). Files whose bytes differ from the record without a launcher observation
  (legacy products, bare Snakemake, hard kill) have `producer: null` and are counted as unattributed.
- Retention: a generation's diagnostics stay while it still owns at least one current file; copies of
  unreferenced generations are removed. Central history is never pruned by this mechanism.
- Shared steps: rules 2.01/2.02 write `data/spatial/geoms/`, not the product. The record names them as
  shared steps and stores each generation's `region.geojson` WKB fingerprint as a dependency fact.
- Configuration: each generation references the immutable snapshot named by its invocation's
  `configuration.run_record`, never the mutable latest capture under `config/analyze_projections/`.

## D2 Export bundle

- Command: `scripts/transfer_results.py export` / `import`; one ZIP (stdlib `zipfile`, no new dependency).
- Schema `cst-result-bundle/1`. Members: `manifest.json`, `product/<ensemble>/**` (the whole product,
  including `raw/`, `scalar/` and `_engine/`), `configuration/<snapshot-sha>/**` (exact retained snapshot
  bytes), `dependencies/region.geojson`. One profile; nothing is silently omitted.
- Manifest: file inventory with relative paths, sizes and SHA-256; attribution mode; compatibility facts
  (region fingerprint, variable specification, windows, ensemble/model/member identities, series digests,
  method/schema versions); source toolbox identity; source absolute paths kept as historical text only.
- Refusals before writing the bundle: incomplete product state; missing required product files; region
  fingerprint differing from `summary/provenance.json`; provenance configuration digests matching no
  bundled snapshot.
- Legacy products (no production record): allowed with attribution `legacy-unattributed`. The snapshot
  is selected by matching `summary/provenance.json` effective and input configuration digests; with no
  match export refuses. Ntoum's product matches snapshot `34d1af1e...` on both digests.
- Excluded: locks, `.snakemake/`, invocations, execution configs, `_shared/`, central `logs/`.

## D3 Import

- All validation precedes destination writes: safe member names (no absolute, drive, `..`, link entries,
  duplicates, or unlisted members), supported schema, every listed file present with matching SHA-256,
  and a bundled region whose fingerprint equals the manifest's.
- Destination region present: WKB fingerprint must match (fatal), so equal bounding boxes cannot pass.
  Absent: import proceeds, records `region: unverified`, and does not write `data/spatial/`.
- Destination configuration, when supplied: compare WF2 scientific settings (ensemble, models, scenarios,
  members, variables, windows). Differences refuse unless `--accept-differences`, which records them.
- An existing destination product refuses without modification; an identical earlier import reports a
  no-op. Publication: stage beside the target on the same volume, verify, add
  `_engine/imported/<bundle-id>/` (manifest, configuration snapshots, region, import record), then one
  rename. Destination configuration archives, `data/spatial/`, invocations and logs are never written;
  only the runtime execution lock under `config/_engine/archive-transactions/` is created.
- Import supports reading and interpreting results only; no runner adoption or no-recompute guarantee.

## D4 Process

No `design-review-loop`: the bundle is a single-tool, versioned, additive contract, and no repository rule
requires external review. Revisit if another tool consumes bundles.

## Commit plan

| # | Lands | Estimate |
|---|---|---|
| 1 | Task records: this file, the walkthrough and the board note | 15 min |
| 2 | Production record, launcher hooks, diagnostics tests (run/failed retry/no-op/partial rerun) | 3--4 h |
| 3 | Export and CLI with integrity/legacy tests | 3 h |
| 4 | Import validation and atomic publication with conflict/interruption/polygon tests | 3--4 h |
| 5 | User documentation and isolated Ntoum export/import walkthrough | 2 h |

## As shipped (2026-10-22)

Commits `7a28671e` (record), `6d5220e3` (export), `434b0ccb` (import), `0719c9be` (docs),
`207f5620` (lock wording, JSON-escaped paths, link-member test). Deviations and additions:

- Imported provenance uses 12-character directory ids (`_engine/imported/<bundle12>/configuration/<snap12>/`)
  to stay inside Windows' default MAX_PATH; manifests keep full digests.
- Bundled snapshot directories are keyed by `run_record.yml` SHA-256; export finds snapshots and the
  region in the project or carried by an earlier import, so an imported product can be re-exported.
- Re-export from a project without a captured WF2 configuration needs `--ensemble`.
- Observation and publication both fail open with a stderr note; a missed observation leaves bytes
  unattributed rather than failing the run.
- Owner-decided without review: D4 (no design-review-loop) and schema names `cst-result-bundle/1`,
  `cst-result-import/1`, `product-production/1`.
