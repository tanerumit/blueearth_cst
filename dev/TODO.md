# TODO

Live task board. Unfinished work only -- move closed tasks to `dev/tasks/` and
delete their working notes. Row order expresses priority.

**Next review:** _not scheduled_ -- set a date or milestone for the first
periodic project-health review.

- **ID** -- date-based, `t<YYMMDD><letter>` (e.g. `t260716a`).
- **Status** -- `backlog`, `active`, or `blocked`.
- **Area** -- free project-specific label.
- **Updated** -- ISO date of the last status change.
- **Working note** -- optional link into `dev/working/`.

| ID | Task | Status | Area | Updated | Working note |
|---|---|---|---|---|---|
| t260716a | R3 workflow-1 followups: `test_cli` xfails, exhaustive M1 warnings triage, `extract_climate_grid` truncation + Snakemake config-staleness | backlog | R3 | 2026-07-16 | [`followups.md`](followups.md) → "R3 — Workflow 1" |
| t260716b | R5 workflow-3 followups: wire `historical:` config into `extract_climate_grid`, weathergenr `spatial_ref`/wavelet fixes | backlog | R5 | 2026-07-16 | [`followups.md`](followups.md) → "R5 — Workflow 3" |
| t260716c | R3+ upgrade followups from M2b: CSDMS constant-par names, CMIP6 attr loss on merge, outlet naming convention, weathergenr/julia install story | backlog | R3+ | 2026-07-16 | [`followups.md`](followups.md) → "M2b" |

> **Detail lives in `followups.md`**, kept as the milestone-scoped backlog store
> (it carries reproducible context and is referenced by live tests). Promote an
> individual item to an `active` row here when its milestone starts.
