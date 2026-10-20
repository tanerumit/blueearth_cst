# Review directory retirement — 2026-10-20

The owner authorized triage and permanent removal of `dev/records/reviews/`. This record resolves
historical citations; [dev-record-lifecycle.md](../../reference/dev-record-lifecycle.md) owns current policy.
No replacement review archive is maintained. Measurements below describe historical candidates, not
new verification of the current toolbox.

## Retained outcomes

Paths in this list are relative to the former `dev/records/reviews/` unless stated otherwise.

- `plot-improvements/`: [verification](../validation/plot-improvements/verification.md), numerical results
  and Gabon input identities retained together. Raw logs, run records, configuration copies and the
  superseded implementation brief are recoverable from Git.
- `wf2-suite-integration/`: [qualified integration evidence](../validation/wf2-suite-integration.md).
  Design iterations, review rounds, intake and ledger are retired. This owner instruction supersedes
  the earlier requirement to keep the entire design-review bundle.
- `water-year-october-verification.md` and `wf2-wf3-performance.md`: unchanged evidence moved to
  [validation](../validation/). Their old commands and implementation descriptions are historical.
- `wf0-climate-transfer-2026-09-18/`: measurements and limits extracted to
  [climate-extraction-transfer-2026-09-18.md](../validation/climate-extraction-transfer-2026-09-18.md).
  Obsolete probe scripts retired; the previously promoted Zarr inspector remains under `dev/scripts/`.
- `wf3-scenario-generation-trace-2026-08-15/trace.md`: measured costs extracted to
  [wf3-preparation-cost-2026-08-15.md](../validation/wf3-preparation-cost-2026-08-15.md).
  The obsolete execution trace and rule inventory are retired.
- That same folder's `stress-test-design-and-surface-axes.md`: preserved byte-for-byte at
  `dev/records/milestones/r12/stress-test-design-and-surface-axes-2026-08-15.md`.
  R12 consumers still depend on its numbered sections and owner rulings.
- `wf2-plot-standardization-2026-09-27.md`: measured table parity extracted to
  [wf2-plot-table-parity-2026-09-27.md](../validation/wf2-plot-table-parity-2026-09-27.md).
  Old visual instructions are superseded by the current plot-style reference.
- `2026-10-01-v0.3.0-release-gates.md` and `2026-10-12-v0.4.1-release-gates.md`: qualified results
  retained in [release-qualification-2026-10.md](../validation/release-qualification-2026-10.md),
  including failed comparisons, skipped scope and owner waivers.
- `legacy-development-migration-2026-10-09.md`: moved to this migrations directory, with its
  `original-context.json` and `landing/gates.json`. The compressed log remains recoverable in Git.
- `dev-reference-transition-2026-10-20.md`: moved to this migrations directory.
- `geographic-robustness-2026-09-28.md`: moved unchanged to main's
  `dev/tasks/t2610091622/geographic-robustness-2026-09-28.md`. Findings remain unresolved pending triage.
- `agent-routing-diagnostics.md`: moved unchanged to main's
  `dev/tasks/t2610082103/caption-layout/agent-routing-diagnostics.md`.
  Both task transfers and their incoming pointers were committed separately on main as `65637fdc`.

The climate-workflow split and Git-workflow simplification proposals, console wording implementation
log and five HTML previews, preliminary test-suite trim assessment, and placeholder are retired.
They do not supply current policy or unique acceptance evidence. The climate-only workflow boundary
and workflow numbering are now owned by current architecture references.

The Git-workflow addendum records a useful historical failure: worktree removal could deregister a
worktree while leaving a locked directory. Cleanup decisions must inspect actual Git registration;
a nonzero command result alone does not describe the resulting state. Original details remain in Git.

## Earlier working-directory holds

The already deleted `working-folder-retirement-2026-10-20.md` recorded three final relocations.
Their source commit is `b9aa068660e6dff2047b9aa69e251f20cb2a988a`; source paths begin `dev/working/`.

- `parameter-placement.md` → `dev/records/milestones/r14/parameter-placement.md`;
  original blob `45f16fd8614325ac6692936e5bd7be12b1cbfb58`. Sealed body remains unchanged.
- `2026-08-15_wf3-scenario-generation-trace/stress-test-design-and-surface-axes.md` →
  the R12 destination above; original blob `bbbe34b39302de064b189064a20063cd66592d4a`.
- `complete-run-output-schema.md` →
  `dev/records/milestones/post-r12/output-schema/complete-run-output-schema.md`;
  original blob `14876ecc80507079aaedd7910a55faa89485be92`.

## Unimplemented infrastructure observations

The WF2 review's `design-runs/wf2-suite-integration/observations.md` proposed two changes to the
shared `design-review-loop` skill: check a pre-change artifact against the last producing-code change,
and explicitly trigger round 2 when a scoped review re-raises an accepted major finding.
These are proposals, not effective rules or completed infrastructure changes. Their only record is
preserved here so retirement does not silently mark them implemented.

## Recovery and integration boundary

All 115 tracked review paths, including eight files already deleted locally before this triage,
are recoverable at commit `53d07f52`. For example:

```powershell
git ls-tree -r --name-only 53d07f52 -- dev/records/reviews
git show 53d07f52:dev/records/reviews/wf2-suite-integration/wf2-suite-integration-design.md
```

Older citations to the already absent `2026-08-11_test-suite-bloat-assessment.md` and
`2026-07-25_post-r6-assessment.md` resolve in `c7992c6f^` under `dev/reviews/`.
Use their original section and finding IDs; these historical citations are not current compliance pointers.

Shared ledger rows and immutable records retain historical spellings. Resolve them through this map
and the source pin rather than recreating deleted paths. Session evidence becomes available in main
when this lane is integrated; the two task transfers are already present in the canonical board.
No task was advanced or closed by relocation. No simulation was rerun or landing authorized.
