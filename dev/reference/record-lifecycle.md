# Record lifecycle

Shared preservation rules for developers and agents promoting, shortening, or removing development
material. Task coordination lives in [development-workflow.md](development-workflow.md); scratch
placement and cleanup live in [repo-layout.md](repo-layout.md#task-temporary-material).

## Promotion

Before deleting legacy working material or closing a task, search for its filename and cited details
in code, tests, configuration, and tracked prose. A cited note supplies provenance: preserve the
needed material in its durable home and update editable citations together.

| Material | Durable home |
|---|---|
| Current rules or reusable procedures | `dev/reference/` |
| Decisions and supporting evidence | `dev/records/decisions/` |
| Milestone designs and acceptance evidence | `dev/records/milestones/<milestone>/` |
| Review snapshots with an identified future reader | `dev/records/reviews/` |
| Unfinished work | Its live board note and optional task sidecar on main |

Do not leave the only copy of needed evidence in disposable scratch.
Where citations span board files on main and branch-owned files, coordinate their separate commits
through [development-workflow.md](development-workflow.md) before removing the source.

Do not rewrite sealed evidence to repair a citation. Root `AGENTS.md` and
[sealed-records.yml](sealed-records.yml) define the sealed set; resolve immutable citations through
retained provenance or Git history.

## Retention

Among retained records, only `dev/records/reviews/` is routinely prunable. Delete a review only when
all three conditions hold:

1. Nothing cites it, including other reviews. Check tracked references with `git grep -l <filename>`.
2. Its items are dispositioned, with remaining work represented by a live board note or decision.
3. Its durable findings have another home. Approved skill or role changes must be committed in their
   canonical infrastructure repository before the source review is discarded.

Check cited detail as well as filenames. Do not replace a register with a summary when consumers cite
individual findings. A review's age or a newer summary alone does not establish that it is disposable.
For partial supersession, retain both records and identify which sections the successor replaces.
Respect sealing before editing any banner or body.

`dev/scripts/check_activation.py` rejects new reference links into transient `tasks/` and prunable
`records/reviews/`. Its two retained exceptions are the Phase A verification citations in
`plot-style.md` and `migration_plot_paths.md`. Before pruning that evidence, update both citations and
the checker's exception set together; the link check also requires the target to exist.

Decisions remain with their identity and supersession pointers. Milestone evidence is preserved.
Current references are maintained in place. Task closure and eligible legacy-source migration follow
the promotion rule; they are separate from routine review pruning.

## Closure-ledger entries

A `dev/LOG.md` closure row is at most three short sentences: what closed, why, and where durable
outcomes live. Promote measurements, findings, tolerances, and decisions first, then link to their home.
The sentence cap never authorizes dropping unique evidence.

Before shortening an existing row, check that each removed finding survives outside the ledger.
Preserve stable item IDs cited by code, tests, or records and name the Git commit from which the full
text is recoverable. Rows written before 2026-08-19 are grandfathered; shorten them only individually
after checking the evidence, never in a blanket sweep.

## Milestone records

[The milestone index](../records/milestones/README.md) owns the folder list, milestone identities,
seal dates, and tags. New milestones get a folder under `dev/records/milestones/`.

Preserve sealed milestone contents, including their existing filenames and internal structure.
Later records can use current conventions without refactoring historical ones. Promote supporting
working notes into the owning milestone when they must survive task closure.

Phase 3 uses `p31/`, `p32a/`, `p32b/`, and `p33/`, corresponding to the `P3-x` identities in
[roadmap.md](roadmap.md). There is no `p32/`: P3-2 split into two milestones.

## Historical evidence and recovery

The original incident narratives and examples behind these rules remain recoverable from the README
before this split:

```powershell
git show cda3900a:dev/README.md
```

For pre-board item IDs cited by code, tests, or Snakefiles:

```powershell
git show 45e3a564:dev/followups-archive.md
```

The retained `dev/records/reviews/legacy-development-migration-2026-10-09.md` records the Git context and
per-file destinations of the legacy cleanup. Use it to resolve historical citations, not as current
workflow guidance.
