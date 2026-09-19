# ADR 0011 — Preserve exact config sources alongside one run record

- **Status:** proposed; discussion captured, implementation not started
- **Date:** 2026-09-19
- **Lifecycle:** maintained-current proposal; append-only revision log
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
or scientific artifact. This captures the proposed direction, not an implemented
or fully reviewed schema.

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
├── scenarios/collections/<id>/
│   ├── run_record.yml
│   ├── sources/
│   │   ├── project_config_rapid.yml
│   │   └── project_config_rapid_generate_scenarios.yml
│   └── ... existing collection artifacts
└── experiments/<name>/
    ├── config/
    │   ├── run_record.yml
    │   ├── sources/
    │   │   ├── project_config_rapid.yml
    │   │   └── project_config_rapid_simulate_system.yml
    │   └── ... existing simulation contract files
    └── ... existing experiment artifacts
```

Each `sources/` also archives required custom catalogs and engine configuration
files with original names and relative structure. Unmodified toolbox-tracked
dependencies may remain identified by recorded revision/blob rather than copied.

For new records, retire separate `composed_config.yml` and central output-project
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

#### Rerun contract and unresolved details

Use the normal workflow entry point with the archived project YAML, recorded
overrides and working directory, and required environment/external inputs.
Preserve relative relationships for paths resolved from source files; other
paths resolve from the run directory, so moving YAMLs does not relocate them.

Exact copies cannot silently rewrite absolute `config_path` references. Before
implementation, specify archive-root selection for parent-relative paths,
multiple drives and colliding basenames; how absolute workflow references are
restored or explicitly redirected for rerun; and how rerun adjustments are
recorded without modifying archived bytes. The sibling example does not prove
general relocatability. Portable export is outside this proposal.

Also specify the record schema, capture timing (copies must match bytes actually
loaded), and publication/recovery behavior so interrupted writes cannot pair one
execution's record with another's sources. A record alone does not certify
successful completion of calculations.

#### Unified execution history

Replace the separate `journal.jsonl` and differing wrapper/simulation invocation
formats with one versioned invocation-record format, one JSON file per invocation
under `config/runs/_engine/invocations/`. Configuration archives remain separate:
they describe configuration and rerun inputs; invocation records describe attempts
and outcomes. This is a proposed simplification, not current behavior.

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

**Coverage must be designed explicitly.** Current WF0–WF2 journal hooks cover
executions that perform work; wrapper manifests also cover dry-runs and no-op
launches. Direct Snakemake parse/startup failures can precede hooks. Unifying the
schema does not repair these gaps. Complete launch coverage would require a
launcher around direct Snakemake calls; requiring that launcher versus retaining
documented hook-only coverage remains open. Also define WF3 participation,
parent-to-child ID propagation, launch failures without a child record, and
reliable detection of up-to-date results.

References to WF0–WF2's latest archive need a matching digest: a mutable path
alone cannot recover an older invocation's configuration. Full historical config
retention remains outside scope. Preserve old journals/manifests as legacy history
until an explicit compatibility or migration policy is agreed.

### Consequences

- **Positive:** one generated configuration account; preserved annotations;
  independent archives for each workflow's custom catalog/template versions;
  no new cross-workflow configuration readers.
- **Negative:** duplicated source/parsed values and repeated project files;
  reruns still require path context, external inputs and a matching environment.
  Old syntax may need the old toolbox or explicit migration.
- **Migration:** update writers, declared targets, baseline readers, fixtures,
  tree checks and live documentation in independently runnable commits. Preserve
  readability of older outputs; do not rewrite sealed artifacts or alter their
  scientific identities to retrofit archives. Removing old files from existing
  projects requires an explicit migration policy.

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
5. Confirm comment-only changes do not alter scientific identities; existing
   sealed collections/experiments remain readable and unmodified.
6. Verify direct/orchestrated records, parent-child linkage, dry-runs, no-op
   results, launch/child failures, hard termination and concurrent invocations.
   Test the chosen pre-hook failure coverage and legacy-history policy.
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

- **2026-09-19:** Captured exact-source and rerun requirements, layout, modularity
  rationale, alternatives and unresolved implementation details. Recording the
  proposal does not authorize or claim implementation.

- **2026-09-19 (execution-history follow-up):** Added unified invocation records,
  parent/child ownership, crash semantics and recording-coverage questions; updated
  the proposed layout. Continue related file assessments here. No implementation
  was requested.
