# ADR 0011 — Preserve exact config sources alongside one run record

- **Status:** accepted P0 decision; implementation pending
- **Date:** 2026-09-19
- **Lifecycle:** maintained-current proposal; earlier drafts remain in Git history
- **Scope:** output-project archives, not the repository's `config/`

### Context

WF0–WF2 currently write both `composed_config.yml` and `run_record.yml` under
`config/runs/<workflow>/`. They overlap, and neither preserves original YAML
comments and formatting. WF0's snapshot includes unused settings such as
`model.outvars`; its current projection also includes the whole `model` section.
Neither is an exact inventory of parameters consumed by individual rules.

The composed snapshot supported an older downstream consistency guard. Current
entry points on the inspected branch no longer invoke it, although legacy code
and comments remain. Baseline checks still read WF1/WF2 snapshots. Repeat reader
discovery before implementation.

The user wants exact config copies with original names and comments, usable to
rerun a workflow with its recorded dependencies. A portable, self-contained
dataset/environment bundle is not required.

### Decision

Replace the separate composed snapshot with one generated `run_record.yml` and
a `sources/` archive of exact source files. Keep records owned by their workflow
or scientific artifact. The owner accepted the reviewed P0 contract on
2026-09-21; [the selected schema](../working/complete-run-output-schema.md#10-selected-p0-contract)
governs versions, digests, path resolution, publication and recovery. The
implementation has not yet been completed.

#### Proposed layout

The rapid configs have sibling project/workflow YAMLs. Scientific artifacts are
abbreviated. Nested source layouts retain their relative directory relationships.

```text
<project_dir>/
├── config/
│   ├── runs/
│   │   ├── README.md
│   │   ├── _engine/
│   │   │   └── invocations/
│   │   │       └── <invocation-id>.json
│   │   ├── analyze_climate/
│   │   │   ├── run_record.yml
│   │   │   └── sources/
│   │   │       ├── project_config_rapid.yml
│   │   │       └── project_config_rapid_analyze_climate.yml
│   │   ├── build_model/
│   │   │   ├── run_record.yml
│   │   │   └── sources/
│   │   │       ├── project_config_rapid.yml
│   │   │       └── project_config_rapid_build_model.yml
│   │   └── analyze_projections/
│   │       ├── run_record.yml
│   │       └── sources/
│   │           ├── project_config_rapid.yml
│   │           └── project_config_rapid_analyze_projections.yml
│   └── basin_data/
├── scenarios/<id>/
│   ├── config/
│   │   ├── run_record.yml
│   │   └── sources/
│   │       ├── project_config_rapid.yml
│   │       └── project_config_rapid_generate_scenarios.yml
│   └── ... collection artifacts
└── experiments/<name>/
    ├── config/
    │   ├── run_record.yml
    │   └── sources/
    │       ├── project_config_rapid.yml
    │       └── project_config_rapid_simulate_system.yml
    └── ... experiment artifacts
```

Each `sources/` also archives required custom catalogs and engine configuration
files with original names and relative structure. Unmodified toolbox-tracked
dependencies may remain identified by recorded revision/blob rather than copied.

For the proposed contract, retire separate `composed_config.yml` and central output-project
`config/catalogs/`, `config/templates/`, and `config/generated/` destinations.
Custom copies belong to their owning archive. Generated engine configs remain
beside their model. `basin_data/` retains its existing purpose.

#### Responsibilities and lifecycle

- **Run record:** store the complete composed mapping loaded for this execution
  once, including applicable overrides; advanced settings; invocation, targets
  and working directory; code/environment identity; referenced dependencies;
  and original-to-archive path mappings with checksums. Version its schema.
- **Loaded scope:** include project settings plus workflow files actually loaded.
  Do not load unrelated workflows just to archive them. Project YAMLs can still
  reference unarchived workflows; each archive supports its owning workflow.
- **Exact sources:** preserve filenames and bytes, including comments, ordering,
  whitespace, encoding and line endings. Copy without YAML re-serialization.
  Repeated project YAMLs are intentional: workflows can use different versions.
- **Identity:** distinguish source byte checksums, declared configuration
  projections, and scientific artifact identities. Comment/format edits must not
  create new scientific collection/simulation identities. Keep projections
  visible without calling them exact consumption traces. Tightening overly broad
  projections is a separate behavioral change.
- **Lifetime:** WF0–WF2 retain the latest execution's matching record and sources,
  not full configuration history. WF3/WF4 records remain immutable inside their
  collections/experiments. Existing scientific contract files remain.
- **Modularity:** share archive-writing code with workflow-specific placement and
  lifecycle handling. Downstream computation uses scientific artifact contracts,
  not archived YAMLs or the human-facing run record.

#### Rerun contract and resolved design details

Use the normal workflow entry point with the archived project YAML, recorded
overrides and working directory, and required environment/external inputs.
Preserve relative relationships for paths resolved from source files; other
paths resolve from the run directory, so moving YAMLs does not relocate them.

Exact copies cannot silently rewrite absolute `config_path` references. The
accepted schema §10.3 specifies source-path mapping, explicit rerun adjustments,
pre-parse byte capture, archive publication and interrupted-write recovery,
including duplicate basenames and multiple drives. The sibling example does
not prove general relocatability. Portable export is outside this decision.
A record alone does not certify successful completion of calculations.

#### Unified execution history

Replace the separate `journal.jsonl` and differing wrapper/simulation invocation
formats with one versioned invocation-record format, one JSON file per invocation
under `config/runs/_engine/invocations/`. Configuration archives remain separate:
they describe configuration and rerun inputs; invocation records describe attempts
and outcomes. This is accepted design, not current behavior.

Each record carries its ID, optional parent ID, entry point/workflow, command,
targets, working directory, start/end timestamps, status and exit code, plus
configuration hashes and artifact references. Record execution mode and whether
work occurred: distinguish dry-run, up-to-date/no-op, actual execution and unknown
work status rather than inferring them from exit code alone.

A direct workflow launch owns one record. An all-workflow launch owns a parent
record describing the requested sequence and referencing individual workflow
records. The parent owns the overall outcome; each child record has one writer
owning its workflow details. Parent and child must not concurrently rewrite the
same file or duplicate child histories inside the parent.

Persist startup state and atomically update completion. A hard termination leaves
an unfinished record: its outcome is unknown, not automatically failed. Derive
chronological history from timestamps; no second authoritative journal is needed.
Sorting does not establish a causal order between overlapping invocations.

**Coverage is defined by the accepted schema §10.4.** Current WF0–WF2 journal hooks cover
executions that perform work; wrapper manifests also cover dry-runs and no-op
launches. Direct Snakemake parse/startup failures can precede hooks. Unifying the
schema does not repair these gaps. Complete launch coverage would require a
launcher around direct Snakemake calls. The accepted contract requires that
launcher for new-schema archive/invocation emission, including WF3. It defines
parent-to-child ID propagation, launch failures without a child record and
up-to-date result detection; raw Snakemake cannot claim full launch history.

References to WF0–WF2's latest archive need a matching digest: a mutable path
alone cannot recover an older invocation's configuration. Full historical config
retention remains outside scope. Previous history files are outside the new reader contract.

#### Shared climate ancillary data ownership

**Agreed by the user on 2026-09-19; not implemented.** Source elevation data
belongs under the project's `data/`, not under a scenario collection. The inspected
collection `4dd34c280a88` currently retains
`ancillary/elevation/era5_orography_2018.nc`. WF4 uses it as forcing-grid elevation
for temperature/pressure corrections during HydroMT forcing preparation; its
operational use does not make it a generated scenario artifact.

The proposed destination is:

```text
<project_dir>/data/climate/
├── historical/
└── ancillary/
    └── era5/
        └── <content-sha256>/
            └── era5_orography_2018.nc
```

The WF4 experiment, not the WF3 collection, retains the source reference and
checksum in its simulation intent and verifies the bytes before forcing
preparation. Experiments using the same source version share it. Different
versions must remain distinguishable and must not silently overwrite a dependency
of an existing experiment. The complete-run schema proposes a content-hash
directory; accepted schema §10.8 fixes the catalog-relative URI and resolution anchor.

The project, including shared data dependencies, is the preservation/transfer
unit. Experiments need not independently bundle these source datasets, consistent
with historical climate already living under `data/climate/historical/`. A future
standalone experiment export must explicitly bundle its checked elevation dependency.

This replaces the assessment's earlier suggestion to retain elevation inside
the collection's `_engine/ancillary/`. Current collection validation and forcing
preparation require collection-local paths, so update the reference/reader contract
for fresh outputs. The checked HydroMT catalog binding belongs under the
experiment's `hydrology/wflow/run_settings/forcing_elevation_catalog.yml`.
Strict WF3 independence also removes elevation and WF4-only preparation code
from the new automatic-seed projection and collection identity. Retain the
canonical digest-to-integer method, with a new WF3-only seed-material version;
numeric automatic seeds may change, as accepted by the owner.

Acceptance checks must cover two experiments sharing one elevation version,
missing or changed dependency bytes, distinct source versions, project relocation
under the chosen path contract, and unchanged WF3 seed/identity when only WF4
elevation or preparation code changes.

### Consequences

- **Positive:** one generated configuration account; preserved annotations;
  independent archives for each workflow's custom catalog/template versions;
  no new cross-workflow configuration readers.
- **Negative:** duplicated source/parsed values and repeated project files;
  reruns still require path context, external inputs and a matching environment.
  Previous output schemas are outside this proposal's reader contract.
- **Migration:** update writers, declared targets, baseline readers, fixtures,
  tree checks and live documentation in independently runnable commits. Use fresh
  project outputs for the new schema; plan the baseline transition explicitly.

### Alternatives considered

| Alternative | Why not preferred here | When preferable |
|---|---|---|
| Comprehensive record only | Loses original comments and source structure | Exact source recovery is unnecessary |
| Record plus workflow YAML only | Omits original project YAML and annotations | Project source is independently versioned and available |
| Keep both generated YAMLs | Overlap remains without exact source retention | A supported reader needs the composed interface during migration |
| One project-wide record | Latest workflow overwrites another's context | Recording a coordinated invocation, as the engine manifest does |
| One append-only event journal | Requires reconstructing state and coordinating concurrent writers | Every intermediate transition must be retained |

### Validation before implementation is accepted

1. Verify original filenames and byte equality, including comments and CRLF/LF.
2. Rerun archived configs with original workflow files unavailable. Cover sibling
   and nested layouts, overrides, duplicate basenames and the chosen absolute-path
   policy; compare loaded configuration values.
3. Verify each workflow archives only loaded sources and its dependency versions;
   WF0 must not require downstream workflow files to be available.
4. Check record/source consistency after interrupted writes and repeated runs.
5. Confirm comment-only changes do not alter scientific identities.
6. Verify direct/orchestrated records, parent-child linkage, dry-runs, no-op
   results, launch/child failures, hard termination and concurrent invocations.
   Test the chosen pre-hook failure coverage.
7. Update snapshot/baseline/tree tests and apply the repository validation ladder
   to implementation. This documentation change runs no pipeline.

### Related

- [Current snapshot writer](../../blueearth_cst/model/copy_config_files.py)
- [Configuration projections and digests](../../blueearth_cst/shared/provenance.py)
- [Artifact-local snapshot writer](../../blueearth_cst/shared/workflow_config_snapshot.py)
- [ADR 0009: generation and simulation ownership](0009-split-scenario-generation-and-system-simulation.md)

- [All-workflow invocation writer](../../scripts/run_workflows.py)
- [Direct simulation invocation writer](../../scripts/simulate_system.py)

### Revisions

- **2026-09-21:** Current proposal preserves exact configuration sources and unified invocation history, assigns shared elevation and its binding to WF4, and defines a strict WF3 boundary. The new automatic-seed material excludes WF4 dependencies while retaining the digest-to-integer method; numeric seeds may change. Previous draft changes are in Git history. Implementation has not begun.
- **2026-09-21, P0 acceptance:** The owner accepted the reviewed contract in the maintained complete-run schema. Archive publication/recovery, pre-parse capture, rerun paths, launcher coverage and WF4 elevation binding are settled at design level. Runtime implementation and verification remain pending.
