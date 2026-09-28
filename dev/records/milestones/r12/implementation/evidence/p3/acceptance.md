# R12 P3 acceptance — workflow extraction

**P3 migration complete: execution, scientific and software checks passed.**
Updated 2026-09-12. P3 is the atomic migration from the combined WF3 carrier to
WF3 scenario generation and WF4 simulation/retained-response metrics. GF15
benchmark adequacy and milestone sealing remain separate, owner-gated work.

## Implemented contract

The five closed workflow stanzas compose through separate settings files.
Direct generation is model-independent. Simulation uses its mandatory runner,
which validates the operation and actual target before one Snakemake invocation.
The all-workflow runner applies the same contract in the accepted order:
climate → generation → model → simulation → projections. Metrics-only defines
no generation or simulation producers and reads complete retained responses.

The old entry point, current workflow template and current seed/fixture files
are retired. The config migrator preserves old resolved seeds, including old
experiment-derived automatic seeds. New automatic seeds exclude experiment
names and identifier capacity. Guides, notebook, diagram, nine WG/HM clauses,
output inventory and successor ADR 0009 migrate with the runtime. Historical
and sealed records retain their original vocabulary.

## Executed evidence

| Gate | Result |
|---|---|
| GF29, final direct and all-workflow generation | Both fresh projects generated all 14 forcing members in one invocation, 37/37 jobs each. Model directories were absent until the post-generation helper copied the frozen P0 model. |
| GF30, final dedicated and all-workflow simulation | Both completed native responses and q/gwr metric publication in one invocation, 25/25 jobs each. Fresh dry-runs preserved checkpoint-dependent target discovery. |
| Physical metrics-only isolation | A new gwr metric set published in three jobs with scratch models/data unavailable, Julia absent from PATH, and live catalog/other workflow configs missing. Original directories were restored. |
| GF30/GF32 reuse and refusal | 32 real command checks across both runners passed: normal/forced simulation and metric reuse, selected metric-file targets, unsupported target refusal, missing/stale plan refusal, exact default selection among four ready collections, explicit retained selection and mismatched-collection refusal. Retained bytes and paths were preserved; mtime-only changes are recorded. |
| GF9 | Both fresh runs preserve all 14 forcing members and 126 native series. All 546 Class-A and 70 Class-B rows are exact. All 140 Class-C run publications match independent calculations; 70 raw mean projections reproduce old pooled publications. All 686 old and 756 new rows are accounted for. |
| GF27 | Automatic seed 568532465 and all 14 forcing members are unchanged across capacities 21, 22 and 100. Collection identities differ and widths are 2/2/3. Experiment renaming selects the same exact collection. |
| GF28 | Source/prepared/native clocks match P0, including leap days, TOML time settings and interval-end responses from 2046-01-02 through 2054-12-31. Existing non-January/partial-year checks are included in the final software gate. |
| GF31 | Bounded ERA5, CHIRPS, CHIRPS-global and dormant E-OBS preparation comparisons pass. Only the precisely declared `forcing` → `run_01` selector attributes differ. This uses ERA5 values and synthetic elevation for the CHIRPS branches; it is not real-CHIRPS validation. |
| Output inventory | Direct tree: 424 mapped paths; runner tree: 228. Zero unmapped paths. |
| Notebook and diagram | All notebook code cells compile; 12 retained-data/analysis cells execute against final outputs. The updated SVG diagram was rendered and visually inspected. |
| Software | Final full suite: 3,705 passed, 15 skipped, 1 expected failure in 803.06 seconds. Lint and format checks pass. |

[Execution evidence](execution-evidence.json) records exact paths, identities,
log hashes and operation reports. [Checkpoint excerpts](checkpoint-transcript.txt)
count every omitted verbose line. The eight `operations-*.json` records retain
each checked argv, refusal, immutable-artifact inventory and mtime change.
The [direct](direct-project-tree.txt) and [runner](runner-project-tree.txt)
snapshots retain the complete mapped trees.
The [software record](software-validation.json) binds the full log, final source
inventory and affected repair checks; the complete [test log](../final/test-full.log)
is retained with this landing.

## Scientific handoffs and provenance

- [Consolidated scientific and orchestration acceptance](scientific-orchestration-handoff.md).
- [GF9/GF28 direct and runner acceptance](direct-scientific-handoff.md),
  with independent native/metric calculations and two-way row crosswalks.
- [GF27 automatic-seed acceptance](gf27-acceptance.md), including a value-only
  perturbation and experiment-rename check.
- [GF31 bounded preparation acceptance](gf31-acceptance.md).

The executed runtime inventory is
`b12a76551cf13b9bce3f96e5d8125954ae70dbfc88278e32f93a90f3e980be98`.
After execution, one stale runner comment was corrected. The
[exact reconciliation](comment-provenance.json) records both file hashes and
the diff and proves identical executable syntax. All other 192 runtime files
are byte-identical. The final reviewed inventory is
`376ae0edeed8283b4cfd0cec9667ef07f97e4966e019d300af5df5b9f7d6c04b`.
Scoped Git attributes preserve the exact evidence bytes and their recorded hashes
across checkouts; they do not change runtime source handling.

The staged whitespace check then found one extra terminal blank line in
`generate_scenarios.smk`. Its removal leaves all nontrailing-newline bytes
identical; the [exact EOF record](eof-provenance.json) preserves the before/after
hashes. The required [final CLI check](postgate-validation.json) passed all 20
tests. The committable inventory is
`7a7c6510854031a69e76ed3bf3c0a420200069d41098c3e552bf5310f0c9e1d0`;
all other 192 full-tested runtime files are unchanged. The full suite and
scientific executions were not repeated for this nonfunctional blank line.

## Repairs found during final verification

The first full suite reported eight failures. A real runner defect required
creating the invocation-record parent directory before its first atomic write;
the other failures were obsolete fixture/catalog/migration expectations. The
regression was observed failing before repair, then all 37 affected checks passed.

Actual output inspection found two missing inventory entries, reproduced by
tests before exact entries were added; 123 affected checks pass and nearby
unknown filenames remain refused. The notebook's new membership assertion
incorrectly compared IDs to Series values rather than its index; the final
reader/analysis execution passed after correction.

Two comparison/probe issues were corrected without changing runtime numbers or
tolerances. Class C must compare the raw mean before publication rounding; the
accepted grain change does not require a mean of rounded values to equal a
rounded pooled mean. The stale-plan probe initially changed JSON formatting too,
so the canonical reader refused before the digest check. Canonical serialization
with only the digest altered reached the intended refusal, with originals
restored in `finally`. Failed logs and scratch roots remain preserved.

## Remaining R12 boundary

GF15 operational screening and fit validity are preserved; benchmark adequacy
remains **not assessed**, and published status remains `provisional_operational`.
The [reviewed benchmark proposal](scientific-review-preparation.md#gf15-recommendation-for-the-owner-gate)
requires owner acceptance before execution under Master Gate 2. No estimator
change, tolerance relaxation, benchmark or milestone-seal claim is made here.

The standing baseline manifest/tree was not re-recorded and is not the GF9
reference. Standing baseline/tree seal checks remain subject to the documented
configuration and identity migration limitations. No push or CI run is claimed.
