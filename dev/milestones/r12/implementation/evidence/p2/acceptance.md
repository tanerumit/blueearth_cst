# R12 P2 acceptance — durable handoffs in current WF3

**P2 complete, 2026-09-11.** The current `run_stress_test.smk` carrier now
publishes and consumes durable collections, frozen simulations/native response
inventories, and immutable metric sets. P3 extraction and runner migration have
not started. The standing baseline and P0 reference were not modified.

## Executed gates

| Gate | Evidence and result |
|---|---|
| GF-29 current-carrier generation checkpoint | Fresh source planning, exclusive initialization, real R roots/descendants and publication completed in one invocation: 32 jobs. All 14 forcing files equal P0 in arrays and bytes. |
| GF-30 current-carrier response/metric checkpoint | Fresh explicit-manifest experiment completed 25/25 jobs in one invocation; project-resolution experiment completed 30/30. Each reached completed native responses and the response-dependent metric set without a second invocation. |
| GF-31 portable preparation | Named validator accepted the bounded four-branch comparison: ERA5, CHIRPS, CHIRPS-global and E-OBS preparation preserve predecessor arrays/TOMLs; a positive perturbation is detected. Original CHIRPS fixtures were unavailable, so this is branch-preservation evidence with ERA5 values and synthetic elevation, not real-CHIRPS validation. E-OBS retains its existing production limitation. |
| GF-32 exact selection | Two complete collections coexist. Routine selection resolves only its exact plan; explicit selection validates either named manifest; an unplanned request refuses fallback. Two complete experiments select the same collection through different modes. |
| Operation/target contract | All 16 matrix cases plus a real current-WF3 retained-only dry-run pass. Unsupported targets fail before the harness launches Snakemake. |
| Actual metrics-only execution | Published a new `gwr` metric set in three jobs while the scratch project's model/data directories were unavailable, Julia was absent from PATH, and live catalog/other workflow config paths were missing. Only metric planning, publication and aggregation ran. Directories were restored. |
| Forced retention | Ready collection reuse adds no collection and preserves bytes/mtimes. Forced complete simulation/metrics reuse preserves all 121 retained files, 140,139,321 bytes. Snakemake refreshes seven output mtimes; no retained bytes change. Simulation producers are absent after completed-response validation. |
| Stale-plan refusal/recovery | An invalid mutable plan refuses ordinary execution before mutation. Explicitly forcing the source checkpoint restores the exact plan; all 154 retained collection/experiment files remain byte-identical. |
| Software | Final full suite: 3,657 passed, 9 skipped, 1 expected failure. Final CLI: 20 passed. Ruff lint and format checks pass. |

[Execution evidence](execution-evidence.json) records identities, counts, byte
accounting and source-log hashes. [Checkpoint excerpts](checkpoint-transcript.txt)
retain the decisive scheduling/completion lines and explicitly count omitted
verbose lines. [Software validation](software-validation.txt) records commands,
results and full-log hashes. [Manifest excerpts](manifest-excerpts.json) show the
persisted fields; they are labelled excerpts, not reusable ready manifests.

## Scientific handoffs

- [Portable preparation acceptance](portable-preparation.md), with its numeric
  comparison and positive perturbation probe.
- [Signed collection/response/metric acceptance](scientific-handoff.md), with
  [independent numeric evidence](scientific-comparison.json).

The final retained collection is
`2f7d2f6c97bd90af43f272b7d7ba4ed166d68e76eb895ce65a9776208a28169b`.
Both `p2_explicit` and `p2_project_final` have simulation identity
`04ab1bc6153034c0bfdad77b137466587bdec9833089c7164b047f0e70a005eb`
and the same complete response-inventory digest. Their q/gwr metric set is
`2ce17970c2b2f5406987acb356858cf1b62ad64cdbbbc255154819e61ec00ade`.
The isolated `gwr`-only reduction selects a different set while preserving
simulation identity.

All 126 native series (14 runs by nine locations) equal P0, including their
3,286 timestamps and CSV bytes. All 756 metric keys are exact: 616 Class-A/B
values reproduce P0, 140 Class-C run values match independent native-response
calculations, and 70 mean-of-run projections reproduce the predecessor tables.
All 70 GEV fits retain 18 finite annual blocks against the unchanged provisional
minimum of ten. Benchmark adequacy remains **not assessed**.

## Identity, refusal and implementation boundaries

Generation identity binds canonical settings, pure row semantics, actual source
bytes, provider code, selected execution dependencies and the complete portable
preparation closure. An invocation-specific initialization receipt authorizes
actual generator/transform workers; a later invocation cannot resume a partial
claim. Ready markers are written last. Listing/deletion is explicit and checks
retained experiment references; there is no automatic eviction.

Simulation identity binds collection identity/revision, pointer-derived model
digest, prepared-clock response request, simulator settings/code and environment.
Native CSVs and their reader TOMLs/temporal sidecars remain the response backing;
no normalized response copy was introduced. Retained model-reference entries
recompute the model digest without requiring the live model for metrics-only.

Metric identity binds completed response provenance, declarations, group and
reference membership, code and selected dependencies, including xclim. Readers
enforce exact keys, token/table inventory and the sole `metrics.json` marker.
Changed byte content, renamed markers, extra empty tables, changed response
requirements and collection assertions are tested refusals.

Two execution defects were caught before final acceptance: the first temporal
sidecar omitted a conversion already performed by HydroMT's reader; a subsequent
response request applied the timestep offset twice and inherited the WF1
calendar. Both were corrected without changing physical operations. Those
incomplete namespaces were preserved; final scientific acceptance uses a fresh
namespace. The first full suite also identified ten outdated static checks or
fixture vocabulary assumptions; their corrected 119-test group and the final
complete suite pass. No numerical tolerance was relaxed.

P2 retains the predecessor experiment-derived `seed: auto`; explicit/default
seed 123 establishes the demonstrated cross-experiment generation reuse. P3 owns
capacity-free automatic seed resolution, the two new entry points, five-stanza
config, dedicated simulation runner, public reference migration and old-WF3
retirement. It must repeat GF-29/GF-30 through those final entry points and
runners. GF-15's separate criteria/owner gate and milestone-seal comparisons
remain outside this P2 acceptance.

The user-facing current behavior is documented in
[WF3 retained handoffs](../../../../../../docs/wf3-retained-handoffs.md).
