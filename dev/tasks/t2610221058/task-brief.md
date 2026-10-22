# Central configuration and portable workflow bundles

## Outcome

Keep the working project's configuration discoverable under `config/`, while allowing users to export
WF2 projection results with their configuration and provenance and import them into a compatible case
on another machine. Retain workflow-specific diagnostics beside the results they describe.

This brief records the user's agreed direction from 2026-10-22. The current assignment is to capture
future work, not to implement it or migrate existing case outputs. WF2 is the proposed first delivery;
support for all workflows is a later extension, not part of its initial acceptance.

## Scope and constraints

### Agreed setup

- Preserve `config/analyze_climate/`, `config/build_model/`, and `config/analyze_projections/` as the
  central retained configuration archives. Keep runner-prepared inputs, including `_shared/`, under
  `config/_engine/execution-configs/`. Do not distribute those folders among output directories.
- Retain WF2-specific logs and benchmarks under its output's `_engine/` directory. Keep project-wide
  invocation summaries and diagnostics for failures before output ownership is known centrally.
- Prefer one retained successful production record per result over a local history of attempts.
  A failed retry or successful no-op must not replace the evidence for the existing results.
- Export is explicit. A portable bundle includes copies of the relevant central configuration and
  provenance; it must work without source-machine paths, junctions, or access to central `_shared/`.
  The working project keeps one authoritative configuration home; exported copies are snapshots.
- Import must preserve scientific meaning, validate integrity and compatibility, and protect existing
  destination outputs and unrelated configuration. Matching bounding boxes alone is insufficient.
- Initial import supports using and interpreting transferred results. Automatic adoption as a completed
  runner execution, guaranteed no-recompute resume, and complete environment recreation are separate scope.
- Do not change scientific calculations or couple projection selection to scenario generation.

Illustrative working layout; exact new diagnostic filenames remain an implementation decision:

```text
<project>/
  config/
    analyze_projections/                 # Authoritative configuration archive
    _engine/execution-configs/
      analyze_projections/               # Prepared execution inputs
      _shared/
  data/climate/projections/cmip6/
    summary/
    analysis/
    plots/
    raw/
    scalar/
    report.md
    _engine/
      analysis_record.json
      execution/                        # Retained production diagnostics
  logs/                                 # Project invocation and failure diagnostics
```

### Starting evidence and likely surfaces

Read-only inspection on 2026-10-22 used `Get-ChildItem` and `Get-Content` on
`cst-cases/runs/gabon-ntoum-v2-rapid/config/analyze_projections/` and
`data/climate/projections/cmip6/`. The central archive contains `project_config.yml`,
`project_config_analyze_projections.yml`, `output_locations.csv`, `SOURCES.md`, `run_record.yml`, and
`catalogs/{deltares_data.yml,cmip6_data.yml,cmip6_store_index.json}`. These are existing captures to reuse.
The product's `_engine/` contains analysis, figure, and stage-B settings records, not attempt folders.

The run record captures loaded and advanced settings, configuration/file hashes, toolbox commit and
dirty state, environment lock hashes, and generated execution-input references. Scientific provenance
in `summary/provenance.json` adds the region fingerprint, resolved CMIP6 identities, windows, and series
digests. Historical absolute paths must remain distinguishable from required portable dependencies.
This case records dirty code; commit and lock hashes alone do not prove exact reproducibility.

Likely implementation entry points are `blueearth_cst/shared/execution_outputs.py`,
`blueearth_cst/shared/configuration_archive.py`, `blueearth_cst/shared/workflow_archive_launch.py`,
`scripts/run_workflows.py`, `scripts/run_workflow.py`, and `analyze_projections.smk`. Reuse their owning
archive and launch helpers; inspect current callers and tests before choosing changes. Necessary callers,
tests, and documentation are within scope. Toolbox code belongs in `blueearth_cst`; real case runs belong
in `cst-cases`. Use the Ntoum case as read-only evidence and a source for an isolated transfer trial.

The existing [execution diagnostics task](../t2610191347-execution-logs-benchmarks.md) records the landed
central logging implementation. This assignment extends that behavior with product-local retention and
portability; preserve its project invocation history and avoid implementing a second capture mechanism.

### Decisions to resolve during implementation

- Bundle representation and command names; no CLI or manifest schema has yet been approved.
- Whether the first bundle always includes raw/scalar caches or exposes explicit export profiles.
  Do not silently omit material or imply recomputation is possible when required inputs are absent.
- Import placement for provenance when a destination already has a WF2 archive; preserve source
  attribution without overwriting the destination's editable configuration or unrelated records.
- Bind retained diagnostics to the actual product generation, including partial analysis/plot reruns.
  Identify shared spatial-step ownership rather than attributing all shared work to WF2.
- Handle partial output replacement on a failed rerun: preserve a coherent previous result or mark
  incomplete results explicitly. Keeping an old successful log beside mixed outputs is unacceptable.

## Work

1. Trace current configuration capture, invocation records, scientific provenance, and diagnostic
   consumers. Define the minimal complete bundle and compatibility checks. Resolve the decisions above
   in this task's existing records. Follow applicable design-review requirements if a consequential
   cross-tool contract is introduced; this brief does not replace that review.
2. Retain WF2 diagnostics beside its outputs while preserving central configuration and project-level
   execution summaries. Stage new evidence until its relationship to published outputs is established.
   Keep failed attempts diagnosable centrally and keep no-op invocations from replacing production evidence.
3. Implement export with a versioned inventory, relative payload paths, checksums, and the exact relevant
   configuration capture. Include scientific provenance and report any missing legacy evidence honestly.
   Validate referenced dependencies; exclude machine runtime state such as locks and `.snakemake/`.
4. Implement import validation and safe publication. Check bundle integrity, supported schema, spatial
   support, variable definitions/units, windows, ensemble/member identities, and relevant method versions.
   State whether mismatches are fatal or require explicit user selection. Detect conflicts before writes;
   do not merge mixed product generations or claim runner-completion adoption.
5. Document export/import usage, diagnostic locations, compatibility limits, and legacy-result handling
   in the existing authoritative guides. Preserve existing evidence during migration; do not bulk-delete
   historical logs or snapshots to make the new layout appear tidy.

## Acceptance and verification

Follow `dev/reference/dev-validation.md` and the testing-policy skill when implementing. Use focused
archive, runner, and diagnostic tests plus new transfer tests justified by the cases below. Identify exact
test targets after inspecting current coverage. Use scoped Ruff for Python changes and an affected DAG
dry-run if rules change; use the owned runner. This documentation task does not claim those checks passed.

- Central configuration remains discoverable and existing configuration capture/launch behavior works.
- Export a completed WF2 product and import it under a different project root with the source unavailable.
  Tables, figures, analysis records, and captured configuration remain usable. Verify payload hashes;
  missing source-path dependencies or changed scientific bytes falsify portability/preservation claims.
- Detect altered payload bytes, missing required files, unsupported schemas, and unsafe bundle paths
  before publication. An incompatible basin polygon with the same bounding box must not pass as equivalent.
- Refuse conflicting destination content without modifying it. Exercise interrupted import and show
  that no incomplete bundle is presented as a valid published result.
- Exercise a successful run, failed retry, no-op, and partial plotting rerun. Attribution must remain
  truthful; an old success record describing partially replaced scientific files fails acceptance.
- Transfer does not require copying source invocation state or `.snakemake/`, enabling WF2, rerunning
  WF1/WF3/WF4, or fetching climate data merely to read the imported results. Test the transfer path with
  source access unavailable. No guarantee of future runner no-recompute behavior is implied.
- Record an isolated Ntoum export/import walkthrough with exact commands and results. Do not modify
  its production output directory for testing. Keep progress in the board note, not a second status file.

### Provisional effort

Estimate from conversational inspection, not an implementation audit: 4-7 developer days for WF2
(contract 0.5-1; diagnostics 0.5-1; export 1-1.5; import 1-1.5; verification/docs 1-2).
Runner adoption/resume adds approximately 2-4 days. All-workflow coverage was estimated at 8-15 days total,
subject to each workflow's artifact contract. A 2-4 day export/import-only slice is an optional sequencing
choice, not a replacement for the agreed diagnostic-locality objective. Re-estimate after tracing ownership.
