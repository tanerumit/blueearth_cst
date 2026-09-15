---
title: export_wflow_results carries a second, unreachable return-level estimator
type: todo-item
status: backlog
effort: 1
area: wf3
queue:
created: 2026-09-15
updated: 2026-09-15
---

> [!note] Overview
> **What** — `export_wflow_results._return_level_from_blocks` still fits the
> predecessor xclim/SciPy MLE `genextreme`, while the production reducer moved to
> the L-moment estimator `gf15-lmoments-c/1` in R12. Decide whether the helper
> migrates, or the whole dead export path is removed.
> **Why** — The Stage 3 reviewer quantified the divergence: the two paths can
> differ by **3x** on the same statistic at the same location, which makes this a
> correctness risk rather than a tidy-up. It is currently unreachable — no
> Snakefile references the module, `metric_plan` imports only `_format_value`,
> and the helper is called solely from line 443 inside its own module — and
> `test_legacy_export_helper_keeps_the_predecessor_estimator` pins the
> divergence so it cannot surprise anyone. That test is what makes this a queued
> item rather than an urgent one.
> **Effort** — small

## Context

D2 scopes the estimator change to `reduce_bundle` and D8 names the export module
a preservation surface, so leaving it was correct for R12 and is recorded in
`dev/milestones/r12/implementation/evidence/gf15-production-integration/stage-2-record.md`.
Removing dead code was outside the GF15 stage briefs' allowed scope, which is why
this is boarded rather than done there.

Three options, for whoever picks it up:

1. Remove the unreachable export path. Cleanest if nothing outside the repo
   imports it — check that before assuming.
2. Migrate the helper to `gev_lmoments.fit_case`. Makes the two paths agree, but
   silently changes a surface D8 designated for preservation.
3. Leave it, pinned. The status quo; costs nothing until someone revives the path
   and gets return levels from the retired estimator without noticing.

## Progress

- [ ] Confirm no out-of-repo consumer imports `export_wflow_results`
- [ ] Choose among the three options above (owner call if it touches D8's
      preservation surface)
- [ ] Apply, keeping or replacing the divergence test accordingly
