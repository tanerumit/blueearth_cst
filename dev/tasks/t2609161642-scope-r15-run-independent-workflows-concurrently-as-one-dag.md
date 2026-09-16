---
title: Scope R15 — run independent workflows concurrently as one DAG
type: todo-item
status: backlog
effort: 2
area: workflow architecture
origin: owner question 2026-09-16
queue:
created: 2026-09-16
updated: 2026-09-16
---

> [!note] Overview
> **What** — Scope a milestone that lets independent workflow branches run concurrently, by collapsing the five entry points into one Snakemake DAG via the module system rather than by running concurrent snakemake processes.
> **Why** — On the toy rapid basin the prize is 28s of ~21min. On a REAL basin WF2 fans out over dozens of CMIP6 models and WF1's build scales with the domain, so both can run for hours — which is where the arithmetic changes. Owner raised it 2026-09-16.
> **Effort** — large

## Progress

- [ ] <first step>

## Why this is not "just run two snakemakes"

Three blockers, all verified 2026-09-16, and none is an effort question.

**1. The workflows are not independent at the FILE level, only conceptually.**
`dev/reference/workflows/rule-index.md` §0.02 states it: `delineate_region` is
"declared from the shared `region_rule` helper, so WF1, WF2 and WF3 declare the
same artifact rather than each deriving its own." WF0/WF1/WF2/WF3 all write the
same `data/spatial/geoms/region.geojson` and the same spatial units. Two
concurrent runs would write one file from two processes.

**2. Snakemake locks the working directory.** `.snakemake/locks/` exists, and all
five entry points run from the repo root against one `project_dir`. A second
invocation refuses — which is why AGENTS.md documents `snakemake --unlock` for
crash recovery. Upstream behaviour, not our choice.

**3. `journal.jsonl` is appended by WF0, WF1 and WF2.** Concurrent appends to one
ledger.

## The shape a solution takes

Not concurrent processes — that fights the tool. **One DAG**, using Snakemake's
`module` system, so the shared `region_rule` is declared ONCE and Snakemake
schedules independent branches concurrently by itself. That is what the feature
exists for.

Consequence, and why this is a milestone rather than a task: it collapses the
five-entry-point design AGENTS.md treats as the toolbox's shape, reworks
per-workflow config composition (R13/R14's `config_path` stanzas assume one
`--configfile` per workflow), and R12 has just sealed two runnable entry points
on the current structure.

## The measurement, and why it does not settle the question

Measured on `test_case/test_rapid` (benchmark tables, 2026-09):

| workflow | rapid |
|---|---|
| WF0 | 2:42 |
| WF3 | ~3:46 |
| WF1 | 5:58 |
| WF4 | ~8:05 |
| WF2 | 0:28 |

On rapid, running WF2 beside WF1 saves 28 s of ~21 min — about 2%, which argues
against doing it at all.

**That is a toy-basin number and must not be carried into the decision.** Owner's
correction, 2026-09-16: on a real basin WF2 fans out over dozens of CMIP6 models
and WF1's build scales with the domain; both can run for HOURS. The rapid config
is deliberately cheap, so it understates exactly the two legs this milestone
would parallelise. **Scoping must start by measuring a production-scale run**,
not by re-reading the table above.

## What scoping must answer

- [ ] Measure WF1 and WF2 on a production basin. Without that the payoff is unknown.
- [ ] Decide whether `module` composition can keep per-workflow `--configfile`
      entry points, or whether the CLI surface changes (a §7 contract rename).
- [ ] Establish what one shared `region_rule` declaration does to the four
      workflows' independent `enabled:` switches.
- [ ] Check the interaction with `t2609152104`'s finding: WF3's provider-code
      closure already pulls in WF4 modules through a function-level import, so
      "independent" is weaker than it looks in more than one place.

## Refs

- `dev/reference/workflows/rule-index.md` §0.02 — the shared `region_rule`.
- `AGENTS.md` — the five entry points and the convenience order.
- Roadmap "Candidate milestones" carries the direction; this item is the scoping.
